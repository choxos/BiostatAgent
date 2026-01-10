# Survival Analysis Patterns

## Overview

Comprehensive survival analysis methods in R covering Kaplan-Meier estimation, Cox proportional hazards models, parametric survival models, and advanced techniques for time-to-event data.

## Basic Survival Objects

### Creating Survival Data

```r
library(survival)

# Right-censored data (most common)
surv_obj <- Surv(time = df$time, event = df$status)

# Left-truncated (delayed entry)
surv_obj <- Surv(time = df$entry_time, time2 = df$event_time, event = df$status)

# Interval censoring
surv_obj <- Surv(time = df$left, time2 = df$right, type = "interval2")

# Check structure
head(surv_obj)
```

## Kaplan-Meier Estimation

### Basic KM Analysis

```r
# Fit Kaplan-Meier
km_fit <- survfit(Surv(time, status) ~ 1, data = df)

# Summary statistics
summary(km_fit)

# Median survival
km_fit

# Survival at specific times
summary(km_fit, times = c(12, 24, 36, 48, 60))
```

### KM by Groups

```r
# Stratified KM
km_fit <- survfit(Surv(time, status) ~ treatment, data = df)

# Log-rank test
survdiff(Surv(time, status) ~ treatment, data = df)

# Stratified log-rank
survdiff(Surv(time, status) ~ treatment + strata(site), data = df)

# Pairwise comparisons
pairwise_survdiff(Surv(time, status) ~ treatment, data = df)
```

### Publication-Quality KM Plots (survminer)

```r
library(survminer)

# Basic KM plot
ggsurvplot(km_fit, data = df)

# Full featured plot
ggsurvplot(
  km_fit,
  data = df,
  pval = TRUE,               # Add p-value
  conf.int = TRUE,           # Confidence intervals
  risk.table = TRUE,         # Risk table
  risk.table.col = "strata", # Color by group
  surv.median.line = "hv",   # Median line
  ggtheme = theme_bw(),
  palette = c("#E7B800", "#2E9FDF"),
  xlab = "Time (months)",
  ylab = "Survival probability",
  legend.title = "Treatment",
  legend.labs = c("Control", "Treatment")
)
```

### Risk Tables and Annotations

```r
ggsurvplot(
  km_fit,
  data = df,
  risk.table = TRUE,
  risk.table.height = 0.25,
  risk.table.y.text = FALSE,    # Show bars instead of names
  cumevents = TRUE,             # Cumulative events table
  cumcensor = TRUE,             # Cumulative censored table
  tables.height = 0.2,
  break.time.by = 12,           # Time axis breaks
  xlim = c(0, 60),
  surv.scale = "percent"        # Y-axis as percentage
)
```

## Cox Proportional Hazards

### Basic Cox Model

```r
# Fit Cox model
cox_fit <- coxph(Surv(time, status) ~ treatment + age + sex, data = df)

# Model summary
summary(cox_fit)

# Hazard ratios with CI
exp(coef(cox_fit))
exp(confint(cox_fit))

# Tidy output
library(broom)
tidy(cox_fit, exponentiate = TRUE, conf.int = TRUE)
```

### Proportional Hazards Assumption

```r
# Test PH assumption
ph_test <- cox.zph(cox_fit)
print(ph_test)

# Plot Schoenfeld residuals
ggcoxzph(ph_test)

# Test for individual variables
ph_test$table
```

### Stratified Cox Model

```r
# Stratify by variable (different baseline hazard)
cox_strat <- coxph(
  Surv(time, status) ~ treatment + age + strata(center),
  data = df
)
```

### Time-Varying Covariates

```r
# Start-stop format
cox_tv <- coxph(
  Surv(tstart, tstop, status) ~ treatment + biomarker,
  data = df_long
)

# With time-varying coefficient
cox_tv <- coxph(
  Surv(time, status) ~ treatment + tt(age),
  data = df,
  tt = function(x, t, ...) x * log(t)
)
```

### Forest Plots

```r
library(survminer)

# Forest plot from Cox model
ggforest(cox_fit, data = df)

# Custom forest plot
library(forestplot)
forest_data |>
  forestplot(
    mean = hr,
    lower = hr_lower,
    upper = hr_upper,
    labeltext = c(variable, n, hr_text),
    is.summary = is_summary
  )
```

## Parametric Survival Models

### With survreg

```r
# Weibull model
weibull_fit <- survreg(
  Surv(time, status) ~ treatment + age,
  data = df,
  dist = "weibull"
)

# Other distributions
exponential_fit <- survreg(..., dist = "exponential")
lognormal_fit <- survreg(..., dist = "lognormal")
loglogistic_fit <- survreg(..., dist = "loglogistic")

# AFT interpretation
summary(weibull_fit)
```

### With flexsurv (more distributions)

```r
library(flexsurv)

# Generalized gamma (very flexible)
ggamma_fit <- flexsurvreg(
  Surv(time, status) ~ treatment + age,
  data = df,
  dist = "gengamma"
)

# Compare distributions
compare_distributions <- list(
  exponential = flexsurvreg(Surv(time, status) ~ treatment, data = df, dist = "exp"),
  weibull = flexsurvreg(Surv(time, status) ~ treatment, data = df, dist = "weibull"),
  lognormal = flexsurvreg(Surv(time, status) ~ treatment, data = df, dist = "lognormal"),
  gamma = flexsurvreg(Surv(time, status) ~ treatment, data = df, dist = "gamma"),
  gengamma = flexsurvreg(Surv(time, status) ~ treatment, data = df, dist = "gengamma")
)

# AIC comparison
sapply(compare_distributions, AIC)
```

### Flexible Parametric Models (rstpm2)

```r
library(rstpm2)

# Royston-Parmar spline model
stpm_fit <- stpm2(
  Surv(time, status) ~ treatment + age,
  data = df,
  df = 4  # degrees of freedom for baseline
)

# Time-varying effects
stpm_tv <- stpm2(
  Surv(time, status) ~ treatment + age,
  data = df,
  df = 4,
  tvc = list(treatment = 2)  # time-varying treatment effect
)
```

## Competing Risks

### Cause-Specific Hazards

```r
# Fit separate Cox models for each cause
cs_cause1 <- coxph(
  Surv(time, status == 1) ~ treatment + age,
  data = df
)

cs_cause2 <- coxph(
  Surv(time, status == 2) ~ treatment + age,
  data = df
)
```

### Fine-Gray Subdistribution Hazards

```r
library(cmprsk)

# Cumulative incidence function
cif <- cuminc(
  ftime = df$time,
  fstatus = df$status,
  group = df$treatment
)

# Plot CIF
ggcompetingrisks(cif)

# Fine-Gray regression
fg_fit <- crr(
  ftime = df$time,
  fstatus = df$status,
  cov1 = model.matrix(~ treatment + age, df)[, -1],
  failcode = 1  # event of interest
)

summary(fg_fit)
```

### With tidycmprsk

```r
library(tidycmprsk)

# Cumulative incidence
cuminc(Surv(time, status) ~ treatment, data = df) |>
  ggcuminc()

# Fine-Gray model (tidy interface)
crr(Surv(time, status) ~ treatment + age, data = df, failcode = 1)
```

## Restricted Mean Survival Time

```r
library(survRM2)

# RMST comparison
rmst_result <- rmst2(
  time = df$time,
  status = df$status,
  arm = df$treatment,
  tau = 60  # restriction time
)

print(rmst_result)

# RMST regression
library(survRM2)
rmst_reg <- rmst2(
  time = df$time,
  status = df$status,
  arm = df$treatment,
  covariates = df[, c("age", "sex")],
  tau = 60
)
```

## Multi-State Models

```r
library(mstate)

# Define transition matrix
tmat <- transMat(
  x = list(
    c(2, 3),  # from state 1
    c(3),     # from state 2
    c()       # state 3 absorbing
  ),
  names = c("Healthy", "Illness", "Death")
)

# Prepare data
msdata <- msprep(
  time = c(NA, "illness_time", "death_time"),
  status = c(NA, "illness_status", "death_status"),
  data = df,
  trans = tmat
)

# Fit Cox model
ms_cox <- coxph(
  Surv(Tstart, Tstop, status) ~ treatment + strata(trans),
  data = msdata
)

# Transition probabilities
pt <- probtrans(msfit(ms_cox, newdata = new_patient), predt = 0)
```

## Survival with tidymodels (censored)

```r
library(censored)

# Model specification
cox_spec <- proportional_hazards() |>
  set_engine("survival") |>
  set_mode("censored regression")

# Workflow
surv_wf <- workflow() |>
  add_formula(Surv(time, status) ~ treatment + age + sex) |>
  add_model(cox_spec)

# Fit
surv_fit <- fit(surv_wf, data = train_data)

# Predict survival probability
predict(surv_fit, new_data, type = "survival", eval_time = c(12, 24, 36))

# Predict hazard
predict(surv_fit, new_data, type = "hazard", eval_time = c(12, 24, 36))
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| survival | Core survival functions |
| survminer | KM plots and Cox visualization |
| flexsurv | Parametric models |
| rstpm2 | Flexible parametric (Royston-Parmar) |
| cmprsk | Competing risks |
| tidycmprsk | Tidy competing risks |
| survRM2 | RMST analysis |
| mstate | Multi-state models |
| censored | tidymodels integration |
