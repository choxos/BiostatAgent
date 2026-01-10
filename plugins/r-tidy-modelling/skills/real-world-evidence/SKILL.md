# Real-World Evidence Analysis in R

## Overview

Methods for analyzing real-world data (RWD) to generate real-world evidence (RWE). Covers target trial emulation, comparative effectiveness research, propensity score methods for observational data, external control arms, bias quantification, and sensitivity analysis for unmeasured confounding.

## Target Trial Emulation

### Conceptual Framework

```r
# Target trial emulation framework
# Specify the target trial protocol, then emulate using observational data

# Key elements to specify:
# 1. Eligibility criteria
# 2. Treatment strategies
# 3. Assignment procedures
# 4. Follow-up period
# 5. Outcome
# 6. Causal contrast (ITT, per-protocol, etc.)
# 7. Analysis plan
```

### Using TrialEmulation Package

```r
library(TrialEmulation)

# Prepare data for target trial emulation
# Data should be in long format with time-varying covariates

# Example: Clone-censor-weight approach
trial_data <- initiators(
  data = rwd,
  id = "patient_id",
  period = "period",
  treatment = "treatment",
  outcome = "outcome",
  eligible = "eligible",
  outcome_cov = ~ age + sex + comorbidity,
  model_var = "assigned_treatment",
  switch_d_cov = ~ time_since_start + lag_outcome,
  first_period = 1,
  last_period = 52,
  use_censor_weights = TRUE
)

# Fit the model
fit <- trial_msm(
  trial_data,
  outcome_cov = ~ assigned_treatment * poly(follow_up, 2),
  model_var = "assigned_treatment",
  include_followup_time = TRUE,
  include_trial_period = TRUE,
  use_sample_weights = TRUE,
  analysis_weights = "asis"
)

summary(fit)
```

### Sequential Trial Emulation

```r
# Emulate multiple trials starting at different time points
# Pool results across trials

# Step 1: Identify eligible patients at each time point
rwd_expanded <- rwd |>
  group_by(patient_id) |>
  mutate(
    # Check eligibility at each visit
    eligible = check_eligibility(age, lab_values, prior_treatment),
    # Time zero for each potential trial
    trial_start = if_else(eligible & treatment_initiated, visit_date, NA)
  ) |>
  ungroup()

# Step 2: Clone patients for each trial they're eligible for
# Step 3: Apply artificial censoring per assigned strategy
# Step 4: Weight for selection and artificial censoring
# Step 5: Pool and analyze
```

## Propensity Score Methods for RWE

### Propensity Score Estimation

```r
library(MatchIt)
library(WeightIt)
library(cobalt)

# Estimate propensity scores
ps_model <- glm(
  treatment ~ age + sex + bmi + smoking + diabetes +
    prior_hosp + baseline_egfr + acei_use,
  family = binomial,
  data = rwd
)

rwd$ps <- predict(ps_model, type = "response")

# Check positivity (overlap)
ggplot(rwd, aes(x = ps, fill = factor(treatment))) +
  geom_density(alpha = 0.5) +
  labs(x = "Propensity Score", fill = "Treatment") +
  theme_bw()
```

### Inverse Probability Weighting (IPW)

```r
library(WeightIt)

# ATT weights (Average Treatment Effect on the Treated)
weights_att <- weightit(
  treatment ~ age + sex + bmi + smoking + diabetes +
    prior_hosp + baseline_egfr,
  data = rwd,
  method = "ps",
  estimand = "ATT"
)

# ATE weights (Average Treatment Effect)
weights_ate <- weightit(
  treatment ~ age + sex + bmi + smoking + diabetes,
  data = rwd,
  method = "ps",
  estimand = "ATE"
)

# Check balance
library(cobalt)
bal.tab(weights_att, stats = c("m", "v", "ks"))
love.plot(weights_att, threshold = 0.1)

# Weighted analysis
library(survey)
design <- svydesign(ids = ~1, weights = ~weights_att$weights, data = rwd)
fit_weighted <- svyglm(outcome ~ treatment, design = design, family = binomial)
summary(fit_weighted)
```

### Overlap Weighting

```r
library(PSweight)

# Overlap weights (target population with equipoise)
ow_result <- PSweight(
  ps.formula = treatment ~ age + sex + bmi + smoking + diabetes,
  data = rwd,
  yname = "outcome",
  weight = "overlap"
)

summary(ow_result)
```

### Propensity Score Matching

```r
library(MatchIt)

# 1:1 nearest neighbor matching
match_nn <- matchit(
  treatment ~ age + sex + bmi + smoking + diabetes + baseline_egfr,
  data = rwd,
  method = "nearest",
  distance = "glm",
  caliper = 0.2,
  ratio = 1,
  replace = FALSE
)

summary(match_nn)
plot(match_nn, type = "jitter")

# Get matched data
matched_data <- match.data(match_nn)

# Analyze matched data
fit_matched <- glm(outcome ~ treatment,
                   family = binomial,
                   data = matched_data,
                   weights = weights)
```

### Doubly Robust Estimation

```r
library(AIPW)

# Doubly robust estimator
aipw_result <- AIPW$new(
  Y = rwd$outcome,
  A = rwd$treatment,
  W = rwd |> select(age, sex, bmi, smoking, diabetes, baseline_egfr),
  Q.SL.library = c("SL.glm", "SL.ranger", "SL.xgboost"),
  g.SL.library = c("SL.glm", "SL.ranger"),
  k_split = 5,
  verbose = FALSE
)

aipw_result$fit()$summary()

# Risk difference and risk ratio
aipw_result$summary()
```

## External Control Arms

### Historical Controls Integration

```r
# Combine trial data with external controls

# Step 1: Identify comparable external controls
external_controls <- rwd |>
  filter(
    # Match eligibility criteria
    age >= 18 & age <= 75,
    egfr >= 30,
    no_prior_treatment == TRUE
  )

# Step 2: Propensity score matching/weighting
library(MatchIt)

combined <- bind_rows(
  trial_data |> mutate(source = "trial", treatment = treatment),
  external_controls |> mutate(source = "external", treatment = 0)
)

# Match external controls to trial control arm characteristics
match_ext <- matchit(
  (source == "trial" & treatment == 0) ~ age + sex + stage + biomarker,
  data = combined |> filter(treatment == 0 | source == "external"),
  method = "nearest",
  caliper = 0.2
)

# Step 3: Analysis with matched external controls
matched_combined <- match.data(match_ext)
```

### Propensity Score Integration

```r
library(WeightIt)

# Weight external controls to match trial population
weights_ext <- weightit(
  source == "trial" ~ age + sex + stage + biomarker + region,
  data = combined,
  method = "ebal",          # Entropy balancing
  estimand = "ATT"
)

# Check balance
bal.tab(weights_ext)

# Weighted analysis
library(survival)
fit_ext <- coxph(
  Surv(time, event) ~ treatment + source,
  data = combined,
  weights = weights_ext$weights
)
```

## Inverse Probability of Censoring Weighting

```r
# Handle informative censoring in RWD

library(ipw)

# Model censoring probability
cens_model <- glm(
  censored ~ time_period + treatment + age + prior_event,
  family = binomial,
  data = rwd_long
)

# Calculate IPCW
rwd_long <- rwd_long |>
  group_by(patient_id) |>
  mutate(
    p_uncensored = 1 - predict(cens_model, type = "response"),
    ipcw = cumprod(p_uncensored)
  ) |>
  ungroup()

# Stabilized weights
rwd_long <- rwd_long |>
  mutate(
    sw = ps_weight * ipcw / mean(ps_weight * ipcw, na.rm = TRUE)
  )

# Weighted analysis with stabilized weights
library(survey)
design_ipcw <- svydesign(ids = ~patient_id, weights = ~sw, data = rwd_long)
```

## Time-Varying Confounding and MSMs

```r
library(ipw)

# Marginal Structural Model for time-varying treatment

# Step 1: Estimate time-varying treatment weights
temp_weights <- ipwtm(
  exposure = treatment,
  family = "binomial",
  link = "logit",
  numerator = ~ 1,
  denominator = ~ age + cd4 + viral_load + prior_oi,
  id = patient_id,
  timevar = visit,
  type = "first",
  data = rwd_long
)

# Step 2: Estimate censoring weights
temp_cens <- ipwtm(
  exposure = censored,
  family = "binomial",
  link = "logit",
  numerator = ~ 1,
  denominator = ~ age + cd4 + viral_load + treatment,
  id = patient_id,
  timevar = visit,
  type = "first",
  data = rwd_long
)

# Step 3: Combine weights
rwd_long$msm_weight <- temp_weights$ipw.weights * temp_cens$ipw.weights

# Step 4: Truncate extreme weights
rwd_long$msm_weight_trunc <- pmin(rwd_long$msm_weight,
                                   quantile(rwd_long$msm_weight, 0.99))

# Step 5: Fit MSM
library(geepack)
msm_fit <- geeglm(
  outcome ~ treatment + time,
  id = patient_id,
  weights = msm_weight_trunc,
  corstr = "independence",
  family = binomial,
  data = rwd_long
)
```

## Adjusted Survival Curves

```r
library(adjustedCurves)

# G-computation adjusted survival curves
adj_surv <- adjustedsurv(
  data = rwd,
  variable = "treatment",
  ev_time = "time",
  event = "event",
  method = "direct",
  outcome_model = coxph(Surv(time, event) ~ treatment + age + sex + stage,
                        data = rwd, x = TRUE),
  conf_int = TRUE,
  bootstrap = TRUE,
  n_boot = 500
)

# Plot
plot(adj_surv) +
  labs(x = "Time (months)", y = "Survival Probability",
       title = "Adjusted Survival Curves")

# IPTW-adjusted survival
adj_surv_iptw <- adjustedsurv(
  data = rwd,
  variable = "treatment",
  ev_time = "time",
  event = "event",
  method = "iptw_km",
  treatment_model = glm(treatment ~ age + sex + stage, family = binomial,
                        data = rwd),
  conf_int = TRUE
)
```

## Sensitivity Analysis for Unmeasured Confounding

### E-values

```r
library(EValue)

# E-value for point estimate and confidence interval
evalue_result <- evalues.RR(
  est = 1.8,           # Observed risk ratio
  lo = 1.3,            # Lower CI bound
  hi = 2.5             # Upper CI bound
)

print(evalue_result)

# Interpretation: An unmeasured confounder would need to be
# associated with both treatment and outcome by RR of [E-value]
# to explain away the observed association

# Visualize
bias_plot(evalue_result)
```

### Tip Analysis

```r
library(tipr)

# Tipping point analysis
tip_result <- tip_coef(
  effect_observed = log(1.8),     # Observed log(RR)
  exposure_confounder_effect = seq(1, 3, 0.1),
  confounder_outcome_effect = seq(1, 3, 0.1),
  verbose = TRUE
)

# Visualize tipping points
plot(tip_result)

# Identify combinations that would tip result
tip_result |>
  filter(adjusted_effect < 0)  # Where effect becomes null/protective
```

### Quantitative Bias Analysis

```r
library(episensr)

# Probabilistic bias analysis for unmeasured confounding
set.seed(123)

# Observed data
obs_table <- matrix(c(100, 50, 80, 120), nrow = 2)

# Bias parameters (distributions)
pba_result <- probsens.conf(
  obs_table,
  reps = 10000,
  seca.parms = list("trapezoidal", c(0.7, 0.8, 0.9, 0.95)),  # Sensitivity
  spca.parms = list("trapezoidal", c(0.8, 0.85, 0.95, 1.0))  # Specificity
)

summary(pba_result)
```

## Data Quality Assessment

```r
# RWD quality checks

# 1. Completeness
completeness <- rwd |>
  summarise(across(everything(), ~mean(!is.na(.)) * 100)) |>
  pivot_longer(everything(), names_to = "variable", values_to = "pct_complete")

# 2. Plausibility
plausibility_checks <- rwd |>
  summarise(
    age_range_ok = all(age >= 0 & age <= 120),
    dates_consistent = all(discharge_date >= admission_date, na.rm = TRUE),
    lab_in_range = all(egfr >= 0 & egfr <= 200, na.rm = TRUE)
  )

# 3. Temporal patterns
rwd |>
  count(year = year(index_date)) |>
  ggplot(aes(year, n)) +
  geom_col() +
  labs(title = "Patient Enrollment Over Time")

# 4. Treatment patterns
rwd |>
  group_by(treatment) |>
  summarise(
    n = n(),
    mean_age = mean(age),
    pct_male = mean(sex == "male") * 100,
    mean_followup = mean(followup_time)
  )
```

## Reporting RWE Studies

```r
# Create Table 1 for RWE study
library(tableone)

# Unweighted baseline characteristics
vars <- c("age", "sex", "bmi", "smoking", "diabetes", "egfr", "stage")
cat_vars <- c("sex", "smoking", "diabetes", "stage")

tab1_unweighted <- CreateTableOne(
  vars = vars,
  strata = "treatment",
  data = rwd,
  factorVars = cat_vars,
  test = FALSE
)

# Weighted baseline characteristics (after PS weighting)
tab1_weighted <- svyCreateTableOne(
  vars = vars,
  strata = "treatment",
  data = design_weighted,
  factorVars = cat_vars,
  test = FALSE
)

# Print with SMD
print(tab1_unweighted, smd = TRUE)
print(tab1_weighted, smd = TRUE)
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| TrialEmulation | Target trial emulation |
| WeightIt | Propensity score weighting |
| MatchIt | Propensity score matching |
| cobalt | Balance diagnostics |
| AIPW | Doubly robust estimation |
| adjustedCurves | Adjusted survival curves |
| tipr | Tipping point analysis |
| EValue | E-values for unmeasured confounding |
| ipw | Inverse probability weighting |
| episensr | Quantitative bias analysis |

## Best Practices

1. **Protocol first**: Define target trial before touching data
2. **Eligibility**: Apply strict, transparent eligibility criteria
3. **Time zero**: Align treatment initiation with follow-up start
4. **Immortal time**: Avoid immortal time bias in study design
5. **Balance**: Check and report covariate balance (SMD < 0.1)
6. **Positivity**: Assess overlap and address violations
7. **Sensitivity**: Quantify impact of unmeasured confounding
8. **Reporting**: Follow RECORD/STROBE-RWE guidelines
