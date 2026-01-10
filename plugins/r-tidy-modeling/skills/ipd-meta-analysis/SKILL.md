# Individual Participant Data Meta-Analysis in R

## Overview

Individual participant data (IPD) meta-analysis methods for synthesizing patient-level data across studies. Covers one-stage and two-stage approaches, mixed-effects models, combining IPD with aggregate data, treatment-covariate interactions, and handling missing data in multi-study settings.

## Two-Stage IPD Meta-Analysis

### Stage 1: Study-Level Analysis

```r
library(dplyr)
library(purrr)
library(broom)

# IPD from multiple studies
ipd_data <- data.frame(
  study = rep(paste0("Study", 1:5), each = 100),
  patient_id = 1:500,
  treatment = rbinom(500, 1, 0.5),
  age = rnorm(500, 60, 10),
  outcome = rnorm(500, 50, 15)
)

# Stage 1: Analyze each study separately
study_results <- ipd_data |>
  group_by(study) |>
  nest() |>
  mutate(
    model = map(data, ~lm(outcome ~ treatment + age, data = .x)),
    tidy_model = map(model, tidy, conf.int = TRUE)
  ) |>
  unnest(tidy_model) |>
  filter(term == "treatment") |>
  select(study, estimate, std.error, conf.low, conf.high)

print(study_results)
```

### Stage 2: Meta-Analysis of Study Effects

```r
library(metafor)

# Stage 2: Meta-analyze study-level estimates
ma_result <- rma(
  yi = study_results$estimate,
  sei = study_results$std.error,
  method = "REML",
  slab = study_results$study
)

summary(ma_result)

# Forest plot
forest(ma_result, header = TRUE)

# Heterogeneity
cat("I-squared:", round(ma_result$I2, 1), "%\n")
cat("Tau-squared:", round(ma_result$tau2, 4), "\n")
```

## One-Stage IPD Meta-Analysis

### Linear Mixed-Effects Model

```r
library(lme4)

# Random intercepts by study
fit_ri <- lmer(
  outcome ~ treatment + age + (1 | study),
  data = ipd_data
)

summary(fit_ri)
confint(fit_ri)

# Random treatment effects by study
fit_rt <- lmer(
  outcome ~ treatment + age + (1 + treatment | study),
  data = ipd_data
)

summary(fit_rt)

# Compare models
anova(fit_ri, fit_rt)

# Extract treatment effect
library(broom.mixed)
tidy(fit_rt, effects = "fixed", conf.int = TRUE) |>
  filter(term == "treatment")
```

### Binary Outcomes

```r
library(lme4)

# Logistic mixed-effects model
fit_logistic <- glmer(
  outcome_binary ~ treatment + age + (1 + treatment | study),
  family = binomial(link = "logit"),
  data = ipd_data,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 100000))
)

summary(fit_logistic)

# Odds ratio
exp(fixef(fit_logistic)["treatment"])
exp(confint(fit_logistic, parm = "treatment", method = "Wald"))
```

### Survival Outcomes

```r
library(survival)
library(coxme)

# Stratified Cox model (fixed study effects)
fit_strat <- coxph(
  Surv(time, event) ~ treatment + age + strata(study),
  data = ipd_data
)

summary(fit_strat)

# Frailty model (random study effects)
fit_frailty <- coxph(
  Surv(time, event) ~ treatment + age + frailty(study, distribution = "gamma"),
  data = ipd_data
)

summary(fit_frailty)

# Using coxme (random effects Cox)
library(coxme)
fit_coxme <- coxme(
  Surv(time, event) ~ treatment + age + (1 | study),
  data = ipd_data
)

summary(fit_coxme)
```

## Combining IPD with Aggregate Data

### Two-Stage with Combined Data

```r
library(metafor)

# Studies with IPD
ipd_studies <- ipd_data |>
  group_by(study) |>
  nest() |>
  mutate(
    model = map(data, ~lm(outcome ~ treatment, data = .x)),
    results = map(model, ~tibble(
      yi = coef(.x)["treatment"],
      vi = vcov(.x)["treatment", "treatment"],
      source = "IPD"
    ))
  ) |>
  unnest(results) |>
  select(study, yi, vi, source)

# Studies with only aggregate data
agd_studies <- tibble(
  study = c("Study6", "Study7", "Study8"),
  yi = c(2.5, 3.1, 1.8),        # Treatment effects from publications
  vi = c(0.5, 0.6, 0.4)^2,      # Squared SEs
  source = "AgD"
)

# Combine
all_studies <- bind_rows(ipd_studies, agd_studies)

# Meta-analyze
ma_combined <- rma(yi, vi, data = all_studies, method = "REML")
summary(ma_combined)

# Subgroup by data source
ma_combined_sub <- rma(yi, vi, mods = ~ source, data = all_studies)
summary(ma_combined_sub)
```

### One-Stage with Pseudo-IPD

```r
# When only aggregate data available for some studies,
# can't directly use one-stage approach

# Alternative: Use aggregate-level likelihood in mixed model
# This requires specialized methods (see multinma package)

library(multinma)

# Combine IPD and AgD in network
network <- combine_network(
  set_ipd(ipd_studies_data, study, trt, y = outcome),
  set_agd_arm(agd_studies_data, study, trt, y = mean_outcome, se = se_outcome)
)

# Fit model
fit_combined <- nma(
  network,
  trt_effects = "random",
  regression = ~age  # Individual-level covariate
)
```

## Treatment-Covariate Interactions

### Within-Study vs Between-Study Effects

```r
library(lme4)

# Separate within and between-study covariate effects
ipd_data <- ipd_data |>
  group_by(study) |>
  mutate(
    age_mean = mean(age),              # Study-level mean
    age_centered = age - age_mean       # Individual deviation
  ) |>
  ungroup()

# Model with separated effects
fit_interaction <- lmer(
  outcome ~ treatment + age_centered + age_mean +
    treatment:age_centered + treatment:age_mean +
    (1 + treatment | study),
  data = ipd_data
)

summary(fit_interaction)

# treatment:age_centered = within-study interaction (individual-level)
# treatment:age_mean = between-study interaction (ecological)
```

### Testing Treatment-Effect Modification

```r
library(lme4)
library(lmerTest)

# Is treatment effect modified by age?
fit_mod <- lmer(
  outcome ~ treatment * age + (1 + treatment | study),
  data = ipd_data
)

# Test interaction
summary(fit_mod)  # Check treatment:age coefficient

# Alternative: Stratified analysis
ipd_data$age_group <- cut(ipd_data$age, breaks = c(0, 50, 65, 100),
                           labels = c("Young", "Middle", "Old"))

results_by_age <- ipd_data |>
  group_by(age_group) |>
  nest() |>
  mutate(
    model = map(data, ~lmer(outcome ~ treatment + (1 | study), data = .x)),
    effect = map(model, ~fixef(.x)["treatment"])
  ) |>
  unnest(effect)
```

## Handling Missing Data

### Multiple Imputation for IPD-MA

```r
library(mice)
library(mitml)

# Multiple imputation accounting for clustering
# Use multilevel imputation methods

# Set up imputation
imp <- mice(
  ipd_data,
  method = c(
    study = "",            # Don't impute study
    treatment = "",        # Don't impute treatment
    age = "2l.norm",       # Multilevel normal for continuous
    outcome = "2l.norm"    # Multilevel normal for outcome
  ),
  m = 20,
  maxit = 10
)

# Analyze each imputed dataset
fit_list <- with(imp, lmer(outcome ~ treatment + age + (1 | study)))

# Pool results using Rubin's rules
library(mitml)
pool_fit <- testEstimates(fit_list)
print(pool_fit)
```

### Pattern-Mixture Models

```r
# Sensitivity analysis for missing not at random (MNAR)

# Assume different means for missing vs observed
delta <- c(0, 1, 2, 5)  # Sensitivity parameter

results_sensitivity <- map_dfr(delta, function(d) {
  # Adjust imputed values by delta
  imp_adjusted <- complete(imp, "long") |>
    mutate(outcome = if_else(.imp > 0 & is_missing, outcome + d, outcome))

  # Analyze
  fit <- lmer(outcome ~ treatment + age + (1 | study),
              data = imp_adjusted)

  tibble(
    delta = d,
    estimate = fixef(fit)["treatment"],
    se = sqrt(vcov(fit)["treatment", "treatment"])
  )
})
```

## IPD Network Meta-Analysis

```r
library(multinma)

# IPD-NMA with individual patient data
ipd_network <- set_ipd(
  data = ipd_nma_data,
  study = study,
  trt = treatment,
  y = outcome  # Continuous outcome
)

# For binary outcome
ipd_network_bin <- set_ipd(
  data = ipd_nma_data,
  study = study,
  trt = treatment,
  r = events  # Binary outcome
)

# Fit NMA
nma_ipd <- nma(
  ipd_network,
  trt_effects = "random",
  prior_intercept = normal(scale = 10),
  prior_trt = normal(scale = 10),
  prior_het = half_normal(scale = 1)
)

summary(nma_ipd)
relative_effects(nma_ipd)
```

### IPD-NMA with Covariate Adjustment

```r
library(multinma)

# Population-adjusted NMA
nma_adj <- nma(
  ipd_network,
  trt_effects = "random",
  regression = ~age + sex,  # Covariate adjustment
  class_interactions = "common"
)

# Predict effects for specific population
predict(nma_adj, newdata = data.frame(age = 65, sex = 1))
```

## Diagnostics and Model Checking

### Residual Analysis

```r
library(lme4)
library(DHARMa)

# Fit model
fit <- lmer(outcome ~ treatment + age + (1 + treatment | study), data = ipd_data)

# Residual diagnostics
# Level 1 residuals (within-study)
resid_l1 <- residuals(fit, type = "pearson")

# Random effects
ranef_fit <- ranef(fit)$study

# DHARMa residual diagnostics
sim_res <- simulateResiduals(fit)
plot(sim_res)

# Check for heteroscedasticity
plot(fitted(fit), resid_l1)
abline(h = 0, col = "red")
```

### Influence Diagnostics

```r
library(influence.ME)

# Study-level influence
infl <- influence(fit, group = "study")

# Cook's distance by study
cooks.distance(infl)

# DFBETAs
dfbetas(infl)

# Plot influence
plot(infl, which = "cook")
```

## Reporting IPD-MA Results

```r
# Create comprehensive summary table
create_ipd_ma_summary <- function(fit_one_stage, fit_two_stage) {

  summary_table <- tibble(
    Method = c("One-stage (mixed effects)", "Two-stage (meta-analysis)"),
    Estimate = c(
      fixef(fit_one_stage)["treatment"],
      fit_two_stage$beta
    ),
    SE = c(
      sqrt(vcov(fit_one_stage)["treatment", "treatment"]),
      fit_two_stage$se
    ),
    CI_Lower = Estimate - 1.96 * SE,
    CI_Upper = Estimate + 1.96 * SE,
    Heterogeneity = c(
      VarCorr(fit_one_stage)$study["treatment", "treatment"],
      fit_two_stage$tau2
    )
  )

  return(summary_table)
}
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| lme4 | Linear/generalized mixed-effects models |
| metafor | Two-stage meta-analysis |
| coxme | Mixed-effects Cox models |
| survival | Stratified/frailty survival models |
| mice | Multiple imputation |
| mitml | MI pooling for multilevel |
| multinma | IPD network meta-analysis |
| ipdmeta | IPD-MA utilities |
| joineR | Joint models for IPD |
| DHARMa | Residual diagnostics |

## Best Practices

1. **Data sharing**: Establish data governance before IPD collection
2. **Harmonization**: Standardize variable definitions across studies
3. **One vs two-stage**: One-stage preferred for treatment-covariate interactions
4. **Random effects**: Include random treatment effects to allow for heterogeneity
5. **Missing data**: Use multilevel MI methods; conduct sensitivity analyses
6. **Confounding**: Separate within vs between-study covariate effects
7. **Reporting**: Follow PRISMA-IPD guidelines
8. **Sensitivity**: Compare one-stage and two-stage results
