# Bayesian Modeling in R

## Overview

Comprehensive Bayesian statistical modeling using Stan-based packages (brms, rstanarm), covering prior specification, posterior analysis, model comparison, and Bayesian workflow best practices.

## brms: Bayesian Regression Models

### Basic Models

```r
library(brms)

# Linear regression
fit <- brm(
  formula = y ~ x1 + x2,
  data = df,
  family = gaussian(),
  seed = 123
)

# Logistic regression
fit_logit <- brm(
  y ~ x1 + x2,
  data = df,
  family = bernoulli(link = "logit")
)

# Poisson regression
fit_pois <- brm(
  count ~ x1 + x2 + offset(log(exposure)),
  data = df,
  family = poisson()
)
```

### Prior Specification

```r
# View default priors
get_prior(y ~ x1 + x2, data = df, family = gaussian())

# Set custom priors
custom_priors <- c(
  prior(normal(0, 10), class = "Intercept"),
  prior(normal(0, 2), class = "b"),  # All regression coefficients
  prior(normal(0, 1), class = "b", coef = "x1"),  # Specific coefficient
  prior(exponential(1), class = "sigma")  # Error SD
)

fit <- brm(
  y ~ x1 + x2,
  data = df,
  family = gaussian(),
  prior = custom_priors,
  seed = 123
)
```

### Prior Predictive Checks

```r
# Sample from prior only
fit_prior <- brm(
  y ~ x1 + x2,
  data = df,
  family = gaussian(),
  prior = custom_priors,
  sample_prior = "only",  # Prior predictive
  seed = 123
)

# Visualize prior predictions
pp_check(fit_prior, type = "dens_overlay", ndraws = 100)
```

### Mixed Effects Models

```r
# Random intercepts
fit_mixed <- brm(
  y ~ x1 + x2 + (1 | group),
  data = df,
  family = gaussian()
)

# Random slopes
fit_mixed <- brm(
  y ~ x1 + x2 + (1 + x1 | group),
  data = df,
  family = gaussian()
)

# Crossed random effects
fit_mixed <- brm(
  y ~ x1 + (1 | subject) + (1 | item),
  data = df,
  family = gaussian()
)
```

### Control Parameters

```r
fit <- brm(
  y ~ x1 + x2,
  data = df,
  family = gaussian(),
  chains = 4,
  iter = 4000,
  warmup = 2000,
  cores = 4,
  seed = 123,
  control = list(
    adapt_delta = 0.95,  # Higher for problematic posteriors
    max_treedepth = 15
  )
)
```

## rstanarm: Applied Regression

```r
library(rstanarm)

# Linear regression
fit <- stan_glm(
  y ~ x1 + x2,
  data = df,
  family = gaussian(),
  prior = normal(0, 2.5),
  prior_intercept = normal(0, 10),
  seed = 123
)

# Mixed effects
fit_mixed <- stan_lmer(
  y ~ x1 + x2 + (1 | group),
  data = df,
  seed = 123
)

# Generalized linear mixed
fit_glmer <- stan_glmer(
  y ~ x1 + x2 + (1 | group),
  data = df,
  family = binomial(),
  seed = 123
)
```

## Posterior Analysis

### Summary and Inference

```r
# Model summary
summary(fit)

# Posterior draws
posterior <- as_draws_df(fit)

# Posterior summary
posterior_summary(fit)

# Fixed effects
fixef(fit)

# Random effects
ranef(fit)

# Credible intervals
posterior_interval(fit, prob = 0.95)
```

### Hypothesis Testing

```r
# Probability statements
hypothesis(fit, "x1 > 0")
hypothesis(fit, "x1 > x2")
hypothesis(fit, "x1 + x2 > 0")

# Multiple hypotheses
hypothesis(fit, c("x1 > 0", "x2 > 0", "x1 > x2"))
```

### Posterior Predictive Checks

```r
library(bayesplot)

# Density overlay
pp_check(fit, type = "dens_overlay", ndraws = 50)

# Histogram
pp_check(fit, type = "hist", ndraws = 8)

# Error scatter
pp_check(fit, type = "error_scatter_avg")

# Intervals
pp_check(fit, type = "intervals")

# Stat comparison
pp_check(fit, type = "stat", stat = "mean")
pp_check(fit, type = "stat_2d", stat = c("mean", "sd"))
```

### MCMC Diagnostics

```r
library(bayesplot)

# Trace plots
mcmc_trace(fit)

# Rhat
rhat(fit)
mcmc_rhat(rhat(fit))

# Effective sample size
neff_ratio(fit)
mcmc_neff(neff_ratio(fit))

# Pairs plot (divergences)
mcmc_pairs(fit, pars = c("b_x1", "b_x2", "sigma"))

# Energy
mcmc_nuts_energy(nuts_params(fit))
```

## Model Comparison

### LOO Cross-Validation

```r
# LOO-CV
loo_fit1 <- loo(fit1)
loo_fit2 <- loo(fit2)

# Compare models
loo_compare(loo_fit1, loo_fit2)

# Pareto k diagnostics
plot(loo_fit1)
```

### WAIC

```r
# WAIC
waic_fit1 <- waic(fit1)
waic_fit2 <- waic(fit2)

# Compare
loo_compare(waic_fit1, waic_fit2)
```

### Bayes Factors

```r
library(bridgesampling)

# Compute marginal likelihood
bridge_fit1 <- bridge_sampler(fit1)
bridge_fit2 <- bridge_sampler(fit2)

# Bayes factor
bayes_factor(bridge_fit1, bridge_fit2)
```

### Model Stacking

```r
library(loo)

# Model weights based on LOO
model_weights <- loo_model_weights(
  list(fit1, fit2, fit3),
  method = "stacking"
)
```

## Predictions

### Posterior Predictions

```r
# Expected values (fitted)
fitted(fit, newdata = new_data)

# Predictions with uncertainty
predict(fit, newdata = new_data)

# Full posterior predictive draws
pp_draws <- posterior_predict(fit, newdata = new_data)
```

### Marginal Effects

```r
# Conditional effects
conditional_effects(fit)

# Specific effects
conditional_effects(fit, effects = "x1")

# Interaction effects
conditional_effects(fit, effects = "x1:x2")

# Plot with data
plot(conditional_effects(fit, effects = "x1"), points = TRUE)
```

### Marginal Means

```r
library(emmeans)

# Estimated marginal means
emmeans(fit, ~ treatment)

# Contrasts
emmeans(fit, pairwise ~ treatment)
```

## Advanced Topics

### Non-Linear Models

```r
# Non-linear formula
fit_nl <- brm(
  bf(y ~ a * exp(-b * x), a ~ 1, b ~ 1, nl = TRUE),
  data = df,
  prior = c(
    prior(normal(10, 5), nlpar = "a"),
    prior(normal(0.5, 0.2), nlpar = "b")
  ),
  family = gaussian()
)
```

### Distributional Models

```r
# Model mean and variance
fit_dist <- brm(
  bf(y ~ x1 + x2, sigma ~ x1),  # Heteroscedasticity
  data = df,
  family = gaussian()
)
```

### Ordinal Regression

```r
fit_ordinal <- brm(
  rating ~ x1 + x2,
  data = df,
  family = cumulative("logit")
)
```

### Zero-Inflated Models

```r
fit_zi <- brm(
  count ~ x1 + x2,
  data = df,
  family = zero_inflated_poisson()
)

# With predictors for zero-inflation
fit_zi <- brm(
  bf(count ~ x1 + x2, zi ~ x3),
  data = df,
  family = zero_inflated_poisson()
)
```

### Survival Models

```r
# Cox model (brms)
fit_surv <- brm(
  time | cens(censored) ~ x1 + x2,
  data = df,
  family = cox()
)

# Parametric survival
fit_weibull <- brm(
  time | cens(censored) ~ x1 + x2,
  data = df,
  family = weibull()
)
```

## Bayesian Workflow

### Complete Workflow Example

```r
library(brms)
library(bayesplot)

# 1. Prior predictive check
fit_prior <- brm(
  y ~ x1 + x2,
  data = df,
  family = gaussian(),
  prior = c(
    prior(normal(0, 10), class = "Intercept"),
    prior(normal(0, 2), class = "b"),
    prior(exponential(1), class = "sigma")
  ),
  sample_prior = "only",
  seed = 123
)
pp_check(fit_prior, ndraws = 50)

# 2. Fit model
fit <- update(fit_prior, sample_prior = "no")

# 3. Check convergence
summary(fit)
mcmc_trace(fit)

# 4. Posterior predictive check
pp_check(fit, ndraws = 50)

# 5. Model comparison
fit_alt <- brm(y ~ x1, data = df, family = gaussian())
loo_compare(loo(fit), loo(fit_alt))

# 6. Inference
fixef(fit)
hypothesis(fit, "x1 > 0")

# 7. Predictions
conditional_effects(fit)
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| brms | General Bayesian regression |
| rstanarm | Applied regression models |
| bayesplot | MCMC visualization |
| loo | Model comparison |
| bridgesampling | Bayes factors |
| tidybayes | Tidy Bayesian analysis |
| posterior | Posterior manipulation |
