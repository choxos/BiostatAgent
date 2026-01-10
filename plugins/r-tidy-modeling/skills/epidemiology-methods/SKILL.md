# Epidemiology Methods in R

## Overview

Comprehensive epidemiological analysis methods covering study designs, measures of association, confounding control, propensity scores, and causal inference using R.

## Measures of Association

### Risk and Rate Measures

```r
library(epiR)

# 2x2 table data
# Outcome: +/-
# Exposure: +/-
table_data <- matrix(c(a, b, c, d), nrow = 2, byrow = TRUE)
colnames(table_data) <- c("Disease+", "Disease-")
rownames(table_data) <- c("Exposed", "Unexposed")

# Risk ratio, risk difference, odds ratio
epi.2by2(as.table(table_data), method = "cohort.count")

# For case-control
epi.2by2(as.table(table_data), method = "case.control")

# For cross-sectional
epi.2by2(as.table(table_data), method = "cross.sectional")
```

### Incidence Rates

```r
library(Epi)

# Person-time calculations
# Create Lexis object
lex <- Lexis(
  entry = list(age = entry_age, cal = entry_date),
  exit = list(cal = exit_date),
  exit.status = event,
  data = cohort_data
)

# Split person-time by age bands
lex_split <- splitLexis(lex, breaks = seq(30, 80, by = 10), time.scale = "age")

# Calculate rates
rates <- tapply(status(lex_split, "exit"),
                timeBand(lex_split, "age", type = "factor"),
                function(x) sum(x == 1))
pyrs <- tapply(dur(lex_split),
               timeBand(lex_split, "age", type = "factor"),
               sum)

# Incidence rates
rates / pyrs * 1000
```

### Standardized Rates

```r
library(epitools)

# Direct standardization
ageadjust.direct(
  count = cases,
  pop = population,
  stdpop = standard_population
)

# Indirect standardization (SMR)
ageadjust.indirect(
  count = observed_cases,
  pop = study_population,
  stdcount = expected_rates * std_population,
  stdpop = standard_population
)
```

## Regression Models

### Logistic Regression (Case-Control, Cross-Sectional)

```r
# Simple logistic
fit <- glm(outcome ~ exposure + covariate1 + covariate2,
           family = binomial(link = "logit"),
           data = df)

# Odds ratios with CI
exp(cbind(OR = coef(fit), confint(fit)))

# Using broom
library(broom)
tidy(fit, exponentiate = TRUE, conf.int = TRUE)
```

### Conditional Logistic Regression (Matched Case-Control)

```r
library(survival)

# Matched case-control analysis
fit <- clogit(
  case ~ exposure + covariate + strata(matched_set),
  data = matched_data
)

summary(fit)
exp(coef(fit))  # ORs
```

### Poisson Regression (Rates)

```r
# Poisson for rates
fit <- glm(
  events ~ exposure + age_group + offset(log(person_years)),
  family = poisson(link = "log"),
  data = df
)

# Rate ratios
exp(cbind(RR = coef(fit), confint(fit)))

# Check overdispersion
library(AER)
dispersiontest(fit)

# Negative binomial if overdispersed
library(MASS)
fit_nb <- glm.nb(
  events ~ exposure + age_group + offset(log(person_years)),
  data = df
)
```

### Log-Binomial Regression (Risk Ratios)

```r
# Log-binomial for risk ratios (prevalence ratios)
fit <- glm(
  outcome ~ exposure + covariates,
  family = binomial(link = "log"),
  data = df
)

# If convergence fails, use Poisson with robust SE
library(sandwich)
library(lmtest)

fit_pois <- glm(
  outcome ~ exposure + covariates,
  family = poisson(link = "log"),
  data = df
)

# Robust standard errors
coeftest(fit_pois, vcov = sandwich)
```

## Confounding Control

### Stratified Analysis

```r
library(epiR)

# Mantel-Haenszel adjusted estimates
# Stratified 2x2 tables
mh_result <- epi.2by2(
  stratified_table,  # 3D array: 2x2xK strata
  method = "cohort.count"
)

# MH adjusted RR and homogeneity test
mh_result$massoc$RR.mh  # Adjusted RR
mh_result$massoc$chisq.mh  # Homogeneity test
```

### Regression Adjustment

```r
# Multivariable model
fit_adjusted <- glm(
  outcome ~ exposure + confounder1 + confounder2 + confounder3,
  family = binomial(),
  data = df
)

# Compare crude vs adjusted
fit_crude <- glm(outcome ~ exposure, family = binomial(), data = df)

# Change in estimate
(exp(coef(fit_crude)["exposure"]) - exp(coef(fit_adjusted)["exposure"])) /
  exp(coef(fit_crude)["exposure"]) * 100
```

## Propensity Score Methods

### Propensity Score Estimation

```r
library(MatchIt)

# Estimate propensity scores
ps_model <- glm(
  treatment ~ age + sex + bmi + smoking + comorbidities,
  family = binomial(),
  data = df
)

df$ps <- predict(ps_model, type = "response")

# Check overlap
library(ggplot2)
ggplot(df, aes(x = ps, fill = factor(treatment))) +
  geom_density(alpha = 0.5) +
  labs(title = "Propensity Score Distribution by Treatment")
```

### Propensity Score Matching

```r
library(MatchIt)

# 1:1 nearest neighbor matching
match_out <- matchit(
  treatment ~ age + sex + bmi + smoking + comorbidities,
  data = df,
  method = "nearest",
  distance = "glm",
  caliper = 0.2,
  ratio = 1
)

# Summary and balance
summary(match_out)
plot(match_out, type = "jitter")
plot(summary(match_out))

# Get matched data
matched_data <- match.data(match_out)

# Analyze matched data
fit_matched <- glm(
  outcome ~ treatment,
  family = binomial(),
  data = matched_data,
  weights = weights
)
```

### Propensity Score Weighting (IPTW)

```r
library(WeightIt)

# Estimate weights
weights <- weightit(
  treatment ~ age + sex + bmi + smoking + comorbidities,
  data = df,
  method = "ps",  # Propensity score
  estimand = "ATE"  # Average treatment effect
)

# Check balance
library(cobalt)
bal.tab(weights, stats = c("m", "v"))
love.plot(weights)

# Weighted analysis
library(survey)
design <- svydesign(ids = ~1, weights = ~weights$weights, data = df)
fit_iptw <- svyglm(outcome ~ treatment, design = design, family = binomial())
```

### Doubly Robust Estimation

```r
library(AIPW)

# Doubly robust estimator
aipw_out <- AIPW$new(
  Y = df$outcome,
  A = df$treatment,
  W = df[, c("age", "sex", "bmi", "smoking")],
  Q.SL.library = c("SL.glm", "SL.ranger"),
  g.SL.library = c("SL.glm", "SL.ranger"),
  k_split = 5,
  verbose = FALSE
)$fit()$summary()
```

## Causal Inference

### Directed Acyclic Graphs (DAGs)

```r
library(dagitty)
library(ggdag)

# Define DAG
dag <- dagitty('
  dag {
    Exposure -> Outcome
    Confounder -> Exposure
    Confounder -> Outcome
    Mediator -> Outcome
    Exposure -> Mediator
  }
')

# Plot
ggdag(dag) + theme_dag()

# Find adjustment set
adjustmentSets(dag, exposure = "Exposure", outcome = "Outcome")

# Check if path is blocked
isAdjustmentSet(dag, exposure = "Exposure", outcome = "Outcome",
                Z = c("Confounder"))
```

### E-values for Sensitivity Analysis

```r
library(EValue)

# E-value for point estimate
evalues.RR(est = 2.5, lo = 1.8, hi = 3.5)

# For odds ratio (convert to approximate RR)
evalues.OR(est = 2.5, lo = 1.8, hi = 3.5, rare = TRUE)

# Bias factor plot
bias_plot(RR = 2.5, xmax = 5)
```

### Instrumental Variables

```r
library(ivreg)

# Two-stage least squares
iv_fit <- ivreg(
  outcome ~ treatment + covariates | instrument + covariates,
  data = df
)

summary(iv_fit, diagnostics = TRUE)
```

## Study Design Calculations

### Sample Size for Cohort Studies

```r
library(epiR)

# Cohort study sample size
epi.sscohortt(
  irexp1 = 0.05,   # Incidence in exposed
  irexp0 = 0.02,   # Incidence in unexposed
  FT = 5,          # Follow-up time
  n = NA,          # Sample size (to calculate)
  power = 0.80,
  r = 1,           # Ratio unexposed:exposed
  design = 1,      # Design effect
  sided.test = 2,
  nfractional = FALSE,
  conf.level = 0.95
)
```

### Sample Size for Case-Control Studies

```r
library(epiR)

# Unmatched case-control
epi.sscc(
  OR = 2.0,
  p1 = NA,
  p0 = 0.30,       # Exposure prevalence in controls
  n = NA,
  power = 0.80,
  r = 1,           # Controls per case
  phi.coef = 0,
  design = 1,
  sided.test = 2,
  nfractional = FALSE,
  conf.level = 0.95,
  method = "unmatched",
  fleiss = FALSE
)
```

## Outbreak Investigation

### Epidemic Curves

```r
library(incidence2)

# Create incidence object
inc <- incidence(
  dates = case_data$onset_date,
  interval = "week"
)

# Plot epidemic curve
plot(inc)

# By group
inc_group <- incidence(
  dates = case_data$onset_date,
  interval = "week",
  groups = case_data$region
)
plot(inc_group)
```

### Attack Rates

```r
# Calculate attack rates
attack_rates <- df |>
  group_by(exposure_variable) |>
  summarise(
    cases = sum(ill),
    total = n(),
    attack_rate = cases / total * 100
  )

# Risk ratio
library(fmsb)
riskratio(
  exposed_cases, exposed_total,
  unexposed_cases, unexposed_total
)
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| epiR | Epidemiological measures |
| Epi | Person-time, Lexis diagrams |
| epitools | Rate calculations |
| MatchIt | Propensity score matching |
| WeightIt | Propensity score weighting |
| cobalt | Balance diagnostics |
| dagitty, ggdag | Causal diagrams |
| EValue | Sensitivity analysis |
| ivreg | Instrumental variables |
| incidence2 | Epidemic curves |
