# Causal Mediation Analysis in R

## Overview

Causal mediation analysis methods for decomposing total effects into direct and indirect effects. Covers traditional approaches, natural effect models, sensitivity analysis for unmeasured confounding, mediation with survival outcomes, and comprehensive causal mediation frameworks.

## Traditional Mediation (Baron-Kenny)

### Basic Approach

```r
# Baron-Kenny steps for mediation
# Total effect: Y = c*X + e
# Mediator: M = a*X + e
# Outcome with mediator: Y = c'*X + b*M + e
# Indirect effect: a*b
# Direct effect: c'

# Step 1: Total effect (X -> Y)
fit_total <- lm(outcome ~ treatment + covariates, data = df)
c_total <- coef(fit_total)["treatment"]

# Step 2: Effect on mediator (X -> M)
fit_med <- lm(mediator ~ treatment + covariates, data = df)
a <- coef(fit_med)["treatment"]

# Step 3: Direct effect (X -> Y | M)
fit_direct <- lm(outcome ~ treatment + mediator + covariates, data = df)
c_prime <- coef(fit_direct)["treatment"]
b <- coef(fit_direct)["mediator"]

# Effects
indirect_effect <- a * b
direct_effect <- c_prime
total_effect <- c_total
proportion_mediated <- indirect_effect / total_effect

cat("Total effect:", round(total_effect, 4), "\n")
cat("Direct effect:", round(direct_effect, 4), "\n")
cat("Indirect effect:", round(indirect_effect, 4), "\n")
cat("Proportion mediated:", round(proportion_mediated * 100, 1), "%\n")
```

### Sobel Test (Not Recommended for Small Samples)

```r
# Sobel test for indirect effect
sobel_test <- function(a, b, se_a, se_b) {
  se_ab <- sqrt(b^2 * se_a^2 + a^2 * se_b^2)
  z <- (a * b) / se_ab
  p <- 2 * pnorm(-abs(z))
  return(list(indirect = a * b, se = se_ab, z = z, p = p))
}

se_a <- summary(fit_med)$coefficients["treatment", "Std. Error"]
se_b <- summary(fit_direct)$coefficients["mediator", "Std. Error"]

sobel <- sobel_test(a, b, se_a, se_b)
print(sobel)

# Note: Bootstrap methods are preferred over Sobel test
```

## Causal Mediation with mediation Package

### Basic Mediation Analysis

```r
library(mediation)

# Fit mediator model
med_model <- lm(mediator ~ treatment + age + sex, data = df)

# Fit outcome model
out_model <- lm(outcome ~ treatment + mediator + age + sex, data = df)

# Mediation analysis
med_result <- mediate(
  med_model,
  out_model,
  treat = "treatment",
  mediator = "mediator",
  boot = TRUE,
  boot.ci.type = "bca",
  sims = 1000
)

summary(med_result)

# Key outputs:
# ACME: Average Causal Mediation Effect (indirect)
# ADE: Average Direct Effect
# Total Effect
# Prop. Mediated

# Plot effects
plot(med_result)
```

### Binary Outcomes

```r
library(mediation)

# Mediator model (continuous mediator)
med_model <- lm(mediator ~ treatment + covariates, data = df)

# Outcome model (binary)
out_model <- glm(outcome ~ treatment + mediator + covariates,
                 family = binomial(link = "logit"), data = df)

# Mediation with simulation
med_result <- mediate(
  med_model,
  out_model,
  treat = "treatment",
  mediator = "mediator",
  boot = TRUE,
  sims = 1000
)

summary(med_result)
```

### Binary Mediator

```r
library(mediation)

# Binary mediator model
med_model <- glm(mediator ~ treatment + covariates,
                 family = binomial, data = df)

# Outcome model
out_model <- lm(outcome ~ treatment + mediator + covariates, data = df)

# Mediation
med_result <- mediate(
  med_model,
  out_model,
  treat = "treatment",
  mediator = "mediator",
  boot = TRUE,
  sims = 1000
)

summary(med_result)
```

### Treatment-Mediator Interaction

```r
library(mediation)

# Outcome model with interaction
out_model <- lm(outcome ~ treatment * mediator + covariates, data = df)

# Mediation with interaction
med_result <- mediate(
  med_model,
  out_model,
  treat = "treatment",
  mediator = "mediator",
  boot = TRUE,
  sims = 1000
)

summary(med_result)

# Note: When interaction exists, effects may differ by treatment level
# ACME(0), ACME(1): Indirect effect at control and treatment
# ADE(0), ADE(1): Direct effect at control and treatment
```

## Natural Effect Models with medflex

### Imputation-Based Approach

```r
library(medflex)

# Expand data for natural effect estimation
expData <- neWeight(
  outcome ~ treatment + mediator + age + sex,
  data = df
)

# Fit natural effect model
neMod <- neModel(
  outcome ~ treatment0 + treatment1 + age + sex,
  expData = expData,
  se = "robust"
)

# Effect decomposition
neEffdecomp(neMod)

# Natural Direct Effect (NDE): treatment1 = 0, treatment0 varies
# Natural Indirect Effect (NIE): treatment0 = 0, treatment1 varies
```

### Weighting-Based Approach

```r
library(medflex)

# Using inverse probability weighting
expData <- neWeight(
  outcome ~ treatment + mediator + age + sex,
  data = df,
  weights = "estimated"
)

neMod <- neModel(
  outcome ~ treatment0 + treatment1 + age + sex,
  expData = expData,
  se = "bootstrap",
  nBoot = 1000
)

summary(neMod)
neEffdecomp(neMod)
```

## Comprehensive Mediation with CMAverse

### Basic CMAverse Analysis

```r
library(CMAverse)

# Comprehensive mediation analysis
cma_result <- cmest(
  data = df,
  outcome = "outcome",
  exposure = "treatment",
  mediator = "mediator",
  basec = c("age", "sex", "baseline"),
  EMint = TRUE,                    # Exposure-mediator interaction
  model = "rb",                    # Regression-based
  estimation = "imputation",
  inference = "bootstrap",
  nboot = 1000
)

summary(cma_result)

# Decomposition:
# CDE: Controlled Direct Effect
# PNDE: Pure Natural Direct Effect
# TNDE: Total Natural Direct Effect
# PNIE: Pure Natural Indirect Effect
# TNIE: Total Natural Indirect Effect
# TE: Total Effect
# PM: Proportion Mediated
```

### Multiple Mediators

```r
library(CMAverse)

# Multiple mediators (parallel)
cma_multi <- cmest(
  data = df,
  outcome = "outcome",
  exposure = "treatment",
  mediator = c("mediator1", "mediator2"),
  basec = c("age", "sex"),
  EMint = TRUE,
  model = "rb",
  estimation = "imputation",
  inference = "bootstrap",
  nboot = 500
)

summary(cma_multi)
```

### Sequential Mediators

```r
library(CMAverse)

# Sequential/serial mediation
# X -> M1 -> M2 -> Y

cma_seq <- cmest(
  data = df,
  outcome = "outcome",
  exposure = "treatment",
  mediator = c("mediator1", "mediator2"),
  basec = c("age", "sex"),
  EMint = TRUE,
  model = "rb",
  mreg = list("linear", "linear"),  # Mediator regressions
  yreg = "linear",                   # Outcome regression
  estimation = "imputation",
  inference = "bootstrap",
  nboot = 500
)

summary(cma_seq)
```

## Mediation with Survival Outcomes

### Using mediation Package

```r
library(mediation)
library(survival)

# Mediator model
med_model <- lm(mediator ~ treatment + age + sex, data = df)

# Survival outcome model
surv_model <- coxph(Surv(time, event) ~ treatment + mediator + age + sex,
                    data = df)

# Mediation analysis (simulation-based)
med_surv <- mediate(
  med_model,
  surv_model,
  treat = "treatment",
  mediator = "mediator",
  sims = 1000
)

summary(med_surv)
```

### Survival Mediation with CMAverse

```r
library(CMAverse)

# Survival outcome
cma_surv <- cmest(
  data = df,
  outcome = "event",
  event = "event",
  eventtime = "time",
  exposure = "treatment",
  mediator = "mediator",
  basec = c("age", "sex"),
  EMint = TRUE,
  model = "rb",
  yreg = "coxph",
  estimation = "paramfunc",
  inference = "bootstrap",
  nboot = 500
)

summary(cma_surv)
```

## Sensitivity Analysis

### Sensitivity to Unmeasured Confounding

```r
library(mediation)

# Sensitivity analysis for sequential ignorability
sens_result <- medsens(
  med_result,
  rho.by = 0.05,
  effect.type = "indirect",
  sims = 1000
)

summary(sens_result)
plot(sens_result)

# Key output: At what correlation (rho) between residuals
# does the indirect effect become non-significant?
```

### E-value for Mediation

```r
library(EValue)

# E-value for natural indirect effect
# Convert to risk ratio scale if needed

# For continuous outcome:
nie_estimate <- med_result$d0      # NIE point estimate
nie_se <- med_result$d0.se         # NIE standard error
nie_ci_lower <- med_result$d0.ci[1]

# Standardized effect to approximate RR
# (Simplified - actual conversion depends on outcome distribution)
```

### Sensitivity in CMAverse

```r
library(CMAverse)

# Sensitivity analysis for unmeasured confounding
cma_sens <- cmsens(
  object = cma_result,
  sens = "uc",                     # Unmeasured confounding
  eval_uc = list(
    ume_effect = seq(-0.5, 0.5, 0.1),  # Effect on mediator
    uye_effect = seq(-0.5, 0.5, 0.1)   # Effect on outcome
  )
)

summary(cma_sens)
plot(cma_sens)
```

## Moderated Mediation

### Conditional Process Analysis

```r
library(mediation)

# Outcome model with moderator interaction
out_model_mod <- lm(outcome ~ treatment * moderator + mediator + covariates,
                    data = df)

# Mediation at different moderator levels
med_low <- mediate(
  med_model,
  out_model_mod,
  treat = "treatment",
  mediator = "mediator",
  covariates = list(moderator = quantile(df$moderator, 0.25)),
  boot = TRUE,
  sims = 500
)

med_high <- mediate(
  med_model,
  out_model_mod,
  treat = "treatment",
  mediator = "mediator",
  covariates = list(moderator = quantile(df$moderator, 0.75)),
  boot = TRUE,
  sims = 500
)

# Compare
summary(med_low)
summary(med_high)

# Test moderated mediation
test.modmed(med_result, list(moderator = "low"), list(moderator = "high"))
```

## Causal Diagrams for Mediation

```r
library(dagitty)
library(ggdag)

# Simple mediation DAG
dag_mediation <- dagitty('
  dag {
    X -> M
    M -> Y
    X -> Y
    C -> X
    C -> M
    C -> Y
  }
')

# Identify adjustment sets
adjustmentSets(dag_mediation, exposure = "X", outcome = "Y")

# Plot DAG
ggdag(dag_mediation) +
  theme_dag() +
  labs(title = "Mediation DAG")

# Check if mediation is identified
# Need: No unmeasured confounding of X-Y, X-M, M-Y relationships
```

## Reporting Mediation Results

```r
# Create mediation summary table
create_mediation_table <- function(med_result) {

  effects <- data.frame(
    Effect = c("ACME (Indirect)", "ADE (Direct)", "Total Effect",
               "Proportion Mediated"),
    Estimate = c(med_result$d0, med_result$z0, med_result$tau.coef,
                 med_result$n0),
    CI_Lower = c(med_result$d0.ci[1], med_result$z0.ci[1],
                 med_result$tau.ci[1], med_result$n0.ci[1]),
    CI_Upper = c(med_result$d0.ci[2], med_result$z0.ci[2],
                 med_result$tau.ci[2], med_result$n0.ci[2]),
    P_value = c(med_result$d0.p, med_result$z0.p,
                med_result$tau.p, med_result$n0.p)
  )

  effects <- effects |>
    mutate(across(c(Estimate, CI_Lower, CI_Upper), ~round(., 4))) |>
    mutate(P_value = format.pval(P_value, digits = 3))

  return(effects)
}

# Generate table
med_table <- create_mediation_table(med_result)
print(med_table)
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| mediation | Causal mediation analysis |
| medflex | Natural effect models |
| CMAverse | Comprehensive causal mediation |
| intmed | Interventional effects |
| sensmediation | Sensitivity analysis |
| mediator | SEM-based mediation |
| lavaan | Structural equation modeling |
| dagitty | Causal DAG analysis |

## Best Practices

1. **Causal assumptions**: Clearly state and justify no unmeasured confounding
2. **DAGs**: Draw and analyze causal diagram before analysis
3. **Bootstrap**: Use bootstrap CIs instead of Sobel test
4. **Sensitivity**: Always conduct sensitivity analysis for unmeasured confounding
5. **Interactions**: Test for exposure-mediator interaction
6. **Multiple mediators**: Use appropriate methods for parallel vs sequential
7. **Reporting**: Report all effects (direct, indirect, total) with CIs
8. **Interpretation**: Consider biological/theoretical plausibility of mechanism
