# Meta-Analysis Methods in R

## Overview

Comprehensive pairwise meta-analysis methods covering effect size calculation, fixed and random effects models, heterogeneity assessment, publication bias detection, subgroup analysis, meta-regression, and sensitivity analyses for synthesizing evidence across studies.

## Effect Size Calculation

### Continuous Outcomes

```r
library(metafor)

# Standardized mean difference (SMD/Cohen's d/Hedges' g)
dat <- escalc(
  measure = "SMD",      # Hedges' g (bias-corrected)
  m1i = mean_treatment, # Treatment group mean
  sd1i = sd_treatment,  # Treatment group SD
  n1i = n_treatment,    # Treatment group n
  m2i = mean_control,   # Control group mean
  sd2i = sd_control,    # Control group SD
  n2i = n_control,      # Control group n
  data = studies
)

# Mean difference (unstandardized)
dat_md <- escalc(
  measure = "MD",
  m1i = mean_treatment, m2i = mean_control,
  sd1i = sd_treatment, sd2i = sd_control,
  n1i = n_treatment, n2i = n_control,
  data = studies
)

# From pre-computed means and SEs
dat_pre <- escalc(
  measure = "SMD",
  yi = effect_size,     # Pre-computed effect
  sei = standard_error, # Standard error
  data = studies
)
```

### Binary Outcomes

```r
library(metafor)

# Odds ratio
dat_or <- escalc(
  measure = "OR",
  ai = events_treatment,    # Events in treatment
  bi = n_treatment - events_treatment,  # Non-events treatment
  ci = events_control,      # Events in control
  di = n_control - events_control,      # Non-events control
  data = studies
)

# Risk ratio (relative risk)
dat_rr <- escalc(
  measure = "RR",
  ai = events_treatment, bi = n_treatment - events_treatment,
  ci = events_control, di = n_control - events_control,
  data = studies
)

# Risk difference
dat_rd <- escalc(
  measure = "RD",
  ai = events_treatment, bi = n_treatment - events_treatment,
  ci = events_control, di = n_control - events_control,
  data = studies
)

# Arcsine square root transformed risk difference (stabilizes variance)
dat_as <- escalc(
  measure = "AS",
  ai = events_treatment, bi = n_treatment - events_treatment,
  ci = events_control, di = n_control - events_control,
  data = studies
)
```

### Correlation Coefficients

```r
library(metafor)

# Fisher's z transformation (recommended)
dat_cor <- escalc(
  measure = "ZCOR",
  ri = correlation,  # Correlation coefficient
  ni = sample_size,  # Sample size
  data = studies
)

# Raw correlation (not recommended for MA)
dat_cor_raw <- escalc(
  measure = "COR",
  ri = correlation,
  ni = sample_size,
  data = studies
)
```

### Hazard Ratios

```r
library(metafor)

# From log(HR) and SE
dat_hr <- escalc(
  measure = "GEN",
  yi = log_hr,        # Log hazard ratio
  sei = se_log_hr,    # SE of log HR
  data = studies
)

# From HR and 95% CI
studies <- studies |>
  mutate(
    log_hr = log(hr),
    se_log_hr = (log(hr_upper) - log(hr_lower)) / (2 * 1.96)
  )
```

## Fixed and Random Effects Models

### Using meta Package

```r
library(meta)

# Continuous outcomes
m_cont <- metacont(
  n.e = n_treatment,
  mean.e = mean_treatment,
  sd.e = sd_treatment,
  n.c = n_control,
  mean.c = mean_control,
  sd.c = sd_control,
  studlab = study,
  data = studies,
  sm = "SMD",           # Effect measure
  method.smd = "Hedges", # Use Hedges' g
  fixed = TRUE,         # Include fixed effect

  random = TRUE,        # Include random effects
  method.tau = "REML"   # Tau estimation method
)

# Binary outcomes
m_bin <- metabin(
  event.e = events_treatment,
  n.e = n_treatment,
  event.c = events_control,
  n.c = n_control,
  studlab = study,
  data = studies,
  sm = "OR",            # OR, RR, or RD
  method = "MH",        # Mantel-Haenszel (also: Inverse, Peto)
  fixed = TRUE,
  random = TRUE,
  method.tau = "DL"     # DerSimonian-Laird
)

# Generic meta-analysis (pre-calculated effects)
m_gen <- metagen(
  TE = yi,              # Effect estimate
  seTE = sqrt(vi),      # Standard error
  studlab = study,
  data = dat,
  sm = "SMD",
  fixed = TRUE,
  random = TRUE
)

# Print results
summary(m_cont)
```

### Using metafor Package

```r
library(metafor)

# Random-effects model (default: REML)
res <- rma(yi, vi, data = dat, method = "REML")

# Fixed-effect model
res_fe <- rma(yi, vi, data = dat, method = "FE")

# Different tau estimators
res_dl <- rma(yi, vi, data = dat, method = "DL")    # DerSimonian-Laird
res_pm <- rma(yi, vi, data = dat, method = "PM")    # Paule-Mandel
res_ml <- rma(yi, vi, data = dat, method = "ML")    # Maximum likelihood
res_eb <- rma(yi, vi, data = dat, method = "EB")    # Empirical Bayes
res_sj <- rma(yi, vi, data = dat, method = "SJ")    # Sidik-Jonkman

# Model summary
summary(res)

# Confidence interval for tau-squared
confint(res)
```

## Heterogeneity Assessment

### Heterogeneity Statistics

```r
library(metafor)

res <- rma(yi, vi, data = dat)

# Key statistics from model output
res$QE        # Cochran's Q statistic
res$QEp       # p-value for Q
res$I2        # I-squared (%)
res$H2        # H-squared
res$tau2      # Tau-squared (between-study variance)

# Confidence intervals for heterogeneity
ci <- confint(res)
ci$random     # CI for tau-squared, tau, I-squared, H-squared

# Prediction interval (where true effect might lie in future study)
predict(res)
```

### Interpretation Guidelines

```r
# I-squared interpretation:
# 0-25%: Low heterogeneity
# 25-50%: Moderate heterogeneity
# 50-75%: Substantial heterogeneity
# >75%: Considerable heterogeneity

# Create heterogeneity summary
het_summary <- data.frame(
  Statistic = c("Q", "df", "p-value", "I²", "τ²", "τ"),
  Value = c(
    round(res$QE, 2),
    res$k - 1,
    format.pval(res$QEp, digits = 3),
    paste0(round(res$I2, 1), "%"),
    round(res$tau2, 4),
    round(sqrt(res$tau2), 4)
  )
)
```

## Forest Plots

### Basic Forest Plot

```r
library(meta)

# Generate forest plot
forest(m_cont,
       sortvar = TE,           # Sort by effect size
       prediction = TRUE,      # Show prediction interval
       print.tau2 = TRUE,      # Show tau-squared
       print.I2 = TRUE,        # Show I-squared
       print.pval.Q = TRUE,    # Show Q p-value
       leftlabs = c("Study", "N", "Mean", "SD", "N", "Mean", "SD"),
       lab.e = "Treatment",
       lab.c = "Control"
)
```

### Customized Forest Plot

```r
library(meta)

forest(m_bin,
       sortvar = TE,
       prediction = TRUE,
       print.tau2 = TRUE,
       leftcols = c("studlab", "event.e", "n.e", "event.c", "n.c"),
       leftlabs = c("Study", "Events", "Total", "Events", "Total"),
       rightcols = c("effect", "ci", "w.random"),
       rightlabs = c("OR", "95% CI", "Weight"),
       smlab = "Odds Ratio",
       weight.study = "random",
       squaresize = 0.5,
       col.square = "navy",
       col.diamond = "maroon",
       col.predict = "black",
       fontsize = 10,
       spacing = 1.1,
       colgap.forest.left = unit(15, "mm")
)
```

### Forest Plot with metafor

```r
library(metafor)

# Basic forest plot
forest(res,
       header = TRUE,
       xlim = c(-2, 3),
       alim = c(-1, 2),
       slab = dat$study,
       ilab = cbind(dat$n_treatment, dat$n_control),
       ilab.xpos = c(-1.5, -1.2),
       cex = 0.8
)

# Add column headers
text(c(-1.5, -1.2), res$k + 2, c("Treatment N", "Control N"), cex = 0.8, font = 2)
```

## Funnel Plots and Publication Bias

### Funnel Plots

```r
library(meta)

# Standard funnel plot
funnel(m_cont,
       xlab = "Effect Size (SMD)",
       studlab = TRUE)

# Contour-enhanced funnel plot
funnel(m_cont,
       xlim = c(-2, 2),
       contour = c(0.9, 0.95, 0.99),
       col.contour = c("darkgray", "gray", "lightgray"),
       studlab = TRUE)

# Using metafor
library(metafor)
funnel(res, main = "Funnel Plot")

# Trim-and-fill funnel plot
tf <- trimfill(res)
funnel(tf)
```

### Statistical Tests for Bias

```r
library(metafor)

# Egger's regression test (continuous outcomes)
regtest(res, model = "lm")

# Begg's rank correlation test
ranktest(res)

# Peters' test (binary outcomes, recommended over Egger's)
regtest(res, model = "lm", predictor = "ni")

# Using meta package
library(meta)
metabias(m_cont, method.bias = "Egger")
metabias(m_bin, method.bias = "Peters")
```

### Trim-and-Fill Method

```r
library(metafor)

# Trim-and-fill analysis
tf <- trimfill(res)
summary(tf)

# Number of studies imputed
tf$k0

# Funnel plot with imputed studies
funnel(tf, legend = TRUE)
```

### Fail-Safe N

```r
library(metafor)

# Rosenthal's fail-safe N
fsn(yi, vi, data = dat, type = "Rosenthal")

# Orwin's fail-safe N
fsn(yi, vi, data = dat, type = "Orwin", target = 0.1)

# Rosenberg's fail-safe N
fsn(yi, vi, data = dat, type = "Rosenberg")
```

### Selection Models

```r
library(metafor)

# Vevea-Hedges weight-function model
sel <- selmodel(res, type = "stepfun", steps = c(0.025, 0.5))
summary(sel)

# Three-parameter selection model
sel3 <- selmodel(res, type = "beta")
summary(sel3)
```

## Subgroup Analysis

### Categorical Moderators

```r
library(meta)

# Subgroup analysis by categorical variable
m_sub <- update(m_cont, subgroup = risk_of_bias, tau.common = FALSE)
forest(m_sub)

# Using metafor
library(metafor)
res_sub <- rma(yi, vi, mods = ~ factor(risk_of_bias), data = dat)
summary(res_sub)

# Test for subgroup differences
res_sub$QM      # Test statistic
res_sub$QMp     # p-value
```

### Forest Plot by Subgroup

```r
library(meta)

forest(m_sub,
       sortvar = TE,
       prediction = TRUE,
       print.subgroup.labels = TRUE,
       subgroup.hetstat = TRUE,
       test.subgroup = TRUE
)
```

## Meta-Regression

### Continuous Moderators

```r
library(metafor)

# Single moderator
res_reg <- rma(yi, vi, mods = ~ year, data = dat)
summary(res_reg)

# Multiple moderators
res_reg2 <- rma(yi, vi, mods = ~ year + sample_size + mean_age, data = dat)
summary(res_reg2)

# Bubble plot
regplot(res_reg,
        xlab = "Publication Year",
        label = TRUE,
        labsize = 0.8)
```

### Mixed Moderators

```r
library(metafor)

# Categorical and continuous moderators
res_mixed <- rma(yi, vi,
                 mods = ~ factor(study_design) + mean_age + follow_up,
                 data = dat)
summary(res_mixed)

# Model comparison
anova(res, res_mixed)  # Compare with no moderators
```

### Multimodel Inference

```r
library(metafor)
library(MuMIn)

# Fit full model
res_full <- rma(yi, vi, mods = ~ year + sample_size + risk_of_bias, data = dat)

# All subsets
dredge(res_full)
```

## Sensitivity Analysis

### Leave-One-Out Analysis

```r
library(metafor)

# Leave-one-out analysis
loo <- leave1out(res)
print(loo)

# Forest plot of leave-one-out
forest(loo$estimate, sei = loo$se,
       slab = paste0("Omitting ", dat$study),
       header = "Leave-One-Out Analysis",
       refline = coef(res))

# Using meta package
library(meta)
metainf(m_cont, pooled = "random")
```

### Influence Diagnostics

```r
library(metafor)

# Influence diagnostics
inf <- influence(res)
plot(inf)

# Key diagnostics
inf$inf          # Influence measures
inf$dfbs         # DFBETAS
inf$cook.d       # Cook's distance

# Identify influential studies
which(inf$is.infl)

# Baujat plot (influence vs heterogeneity contribution)
baujat(res)
```

### Cumulative Meta-Analysis

```r
library(metafor)

# Cumulative meta-analysis by year
cum <- cumul(res, order = dat$year)
forest(cum, header = "Cumulative Meta-Analysis")

# Using meta
library(meta)
metacum(m_cont, sortvar = year)
```

## Bayesian Meta-Analysis

```r
library(brms)

# Bayesian random-effects meta-analysis
fit_bayes <- brm(
  yi | se(sqrt(vi)) ~ 1 + (1 | study),
  data = dat,
  prior = c(
    prior(normal(0, 1), class = Intercept),
    prior(cauchy(0, 0.5), class = sd)
  ),
  iter = 4000,
  chains = 4,
  cores = 4
)

summary(fit_bayes)

# Posterior predictive check
pp_check(fit_bayes)

# Forest plot from posterior
library(tidybayes)
fit_bayes |>
  spread_draws(b_Intercept, r_study[study,]) |>
  mutate(study_effect = b_Intercept + r_study) |>
  ggplot(aes(y = study, x = study_effect)) +
  stat_halfeye()
```

## Diagnostic Meta-Analysis

```r
library(mada)

# Bivariate random-effects model for diagnostic accuracy
fit_diag <- reitsma(
  data = diag_data,
  formula = cbind(TP, FN, FP, TN) ~ 1
)

summary(fit_diag)

# SROC curve
plot(fit_diag, sroclwd = 2)

# Summary sensitivity and specificity
summary_sens <- fit_diag$coefficients["tsens..Intercept."]
summary_spec <- fit_diag$coefficients["tfpr..Intercept."]
```

## Reporting Meta-Analysis Results

### Summary Table

```r
library(meta)

# Create summary table
summary_table <- data.frame(
  Model = c("Fixed Effect", "Random Effects"),
  Estimate = c(m_cont$TE.fixed, m_cont$TE.random),
  CI_Lower = c(m_cont$lower.fixed, m_cont$lower.random),
  CI_Upper = c(m_cont$upper.fixed, m_cont$upper.random),
  p_value = c(m_cont$pval.fixed, m_cont$pval.random)
)

# Heterogeneity
het_table <- data.frame(
  Q = m_cont$Q,
  df = m_cont$df.Q,
  p_value = m_cont$pval.Q,
  I2 = m_cont$I2,
  tau2 = m_cont$tau2
)
```

### PRISMA Flow Diagram

```r
library(PRISMAstatement)

prisma_flow <- prisma(
  found = 1000,
  found_other = 50,
  no_dupes = 800,
  screened = 800,
  screen_exclusions = 600,
  full_text = 200,
  full_text_exclusions = 150,
  qualitative = 50,
  quantitative = 45
)

prisma_flow
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| meta | User-friendly meta-analysis with forest plots |
| metafor | Comprehensive meta-analysis and meta-regression |
| dmetar | Meta-analysis helpers and additional functions |
| metasens | Sensitivity analysis and bias assessment |
| robumeta | Robust variance estimation for dependent effects |
| clubSandwich | Cluster-robust standard errors |
| mada | Diagnostic test accuracy meta-analysis |
| brms | Bayesian meta-analysis |
| PRISMAstatement | PRISMA flow diagrams |

## Best Practices

1. **Pre-register protocol**: Define inclusion criteria and analysis plan a priori
2. **Use appropriate effect measure**: Match to outcome type and clinical meaning
3. **Assess heterogeneity**: Report Q, I², tau² and interpret in context
4. **Investigate sources**: Use subgroup analysis and meta-regression
5. **Evaluate bias**: Use multiple methods (funnel, Egger, trim-fill)
6. **Sensitivity analysis**: Leave-one-out, influence diagnostics, different estimators
7. **Report transparently**: Follow PRISMA guidelines
8. **Consider prediction intervals**: More relevant for clinical application than CI
