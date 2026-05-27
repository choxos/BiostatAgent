---
name: stc-methodology
description: Deep methodology knowledge for STC including outcome regression, effect modifier selection, covariate centering, and comparison with MAIC. Use when conducting or reviewing STC analyses.
---

# STC Methodology

Comprehensive methodological guidance for conducting rigorous Simulated Treatment Comparisons following NICE DSU TSD 18.

## When to Use This Skill

- Deciding between STC and MAIC
- Selecting effect modifiers for an STC model
- Implementing covariate centering on an aggregate target population
- Reviewing STC code or results
- Planning Bayesian or frequentist sensitivity analyses

## Fundamental Concept

### Outcome Regression vs Propensity Weighting

**STC approach**
- Fit an outcome regression model in the IPD study.
- Include treatment and treatment-covariate interactions for relevant effect modifiers.
- Center covariates on the external aggregate population.
- Interpret the treatment coefficient as the adjusted effect in that external population.

**MAIC approach**
- Reweight IPD to match external aggregate covariate summaries.
- Estimate the weighted treatment effect in the target population.
- Use weight diagnostics and effective sample size as core feasibility checks.

### Key Equation for a Binary Anchored STC

```text
logit{P(Y = 1)} = beta_0 + beta_trt * Treatment
                + beta_X * X_centered
                + beta_trt_X * Treatment * X_centered

X_centered = X - X_external
```

With centered covariates, `beta_trt` estimates the treatment effect in the external population, because `X_centered = 0` corresponds to the aggregate target values.

## Assumptions

### Conditional Constancy of Relative Effects

- Anchored STC assumes relative effects are constant across populations after adjustment for all relevant effect modifiers.
- The assumption is not testable with the available data alone.
- Effect modifiers must be measured in the IPD and reported as compatible aggregate summaries in the external study.

### Model Specification

STC additionally assumes that the outcome model is correctly specified:
- Appropriate link function for the endpoint.
- Defensible functional forms for continuous covariates.
- Required treatment-covariate interactions included.
- No unsupported extrapolation beyond the IPD covariate support.

```text
Trade-off:
STC can be more precise than MAIC if the outcome model is correct.
STC can be biased if the model, functional form, or interactions are wrong.
MAIC avoids specifying an outcome model but can lose precision through low ESS.
```

## Effect Modifier Selection

### What Is an Effect Modifier?

A covariate is an effect modifier if the relative treatment effect differs by covariate value. Selection should be based on:
- Clinical or biological plausibility.
- Prior studies, subgroup analyses, or mechanism of action.
- Statistical interaction evidence from IPD as supportive evidence.
- Availability and compatible definition in aggregate data.
- Meaningful imbalance between the IPD and target populations.

Interaction p-values alone should not determine the final covariate set. Interaction tests are commonly underpowered, and selection after inspecting many tests can inflate false-positive findings.

### Effect Modifier Assessment

```r
candidate_covariates <- c("age", "sex_male", "biomarker_pos", "stage")

interaction_terms <- paste0("treatment:", candidate_covariates)
model_formula <- as.formula(
  paste(
    "response ~ treatment * (",
    paste(candidate_covariates, collapse = " + "),
    ")"
  )
)

fit_screen <- glm(model_formula, data = ipd_data, family = binomial())
summary(fit_screen)$coefficients[interaction_terms, , drop = FALSE]
```

Use this as a structured screen, then document why each included covariate is or is not a credible effect modifier.

## Covariate Centering

### Why Center Covariates?

Without centering, the treatment coefficient is evaluated when every covariate equals zero, which is often clinically meaningless. With centering on the external aggregate population, the treatment coefficient is evaluated at the target population.

```r
agd_targets <- c(age = 62, sex_male = 0.55, biomarker_pos = 0.40)

ipd_stc <- ipd_data |>
  dplyr::mutate(
    age_c = age - agd_targets["age"],
    sex_male_c = sex_male - agd_targets["sex_male"],
    biomarker_pos_c = biomarker_pos - agd_targets["biomarker_pos"]
  )
```

For centered binary covariates, subtract the external proportion. For categorical covariates with more than two levels, center compatible dummy variables or use another clearly documented parameterization.

### Hierarchy

When a treatment-covariate interaction is included, include the corresponding main effects unless there is a strong modeling reason not to. This keeps the model hierarchically well formed and the interaction interpretable.

## Anchored vs Unanchored STC

### Anchored STC

```text
Setup:
IPD trial: A vs Common
External aggregate trial: B vs Common
Target: A vs B

Steps:
1. Center effect modifiers on the external aggregate population.
2. Fit the IPD outcome model with interactions.
3. Extract A vs Common at the external population.
4. Obtain B vs Common and its uncertainty from aggregate data.
5. Calculate A vs B using Bucher logic on the correct effect scale.
```

### Unanchored STC

```text
Setup:
No common comparator.
Target: direct comparison of absolute outcomes for A vs B.

Additional requirements:
1. Adjust for all prognostic factors, not only effect modifiers.
2. Assume absolute outcomes are transportable after adjustment.
3. Align outcome definitions, follow-up, and analysis populations.
```

Unanchored STC is high risk and should be avoided when anchored evidence, NMA, or ML-NMR can answer the question.

## Frequentist Implementation Pattern

```r
library(dplyr)

ipd_stc <- ipd_data |>
  mutate(
    age_c = age - agd_targets["age"],
    sex_male_c = sex_male - agd_targets["sex_male"],
    treatment = relevel(factor(treatment), ref = "Placebo")
  )

fit <- glm(
  response ~ treatment * (age_c + sex_male_c),
  data = ipd_stc,
  family = binomial()
)

coef_name <- "treatmentDrug A"
log_or_ac <- unname(coef(fit)[coef_name])
se_log_or_ac <- sqrt(vcov(fit)[coef_name, coef_name])

log_or_bc <- log(external_or_bc)
se_log_or_bc <- (log(external_ci_upper) - log(external_ci_lower)) / (2 * qnorm(0.975))

log_or_ab <- log_or_ac - log_or_bc
se_log_or_ab <- sqrt(se_log_or_ac^2 + se_log_or_bc^2)
ci_log_or_ab <- log_or_ab + c(-1, 1) * qnorm(0.975) * se_log_or_ab

data.frame(
  comparison = "Drug A vs Drug B",
  effect_measure = "OR",
  estimate = exp(log_or_ab),
  ci_lower = exp(ci_log_or_ab[1]),
  ci_upper = exp(ci_log_or_ab[2])
)
```

Use the effect scale that matches the external estimate. Do not mix odds ratios, risk ratios, hazard ratios, mean differences, or risk differences without transforming to a common scale.

## Bayesian STC

### Advantages

- Natural propagation of uncertainty.
- Prior sensitivity analysis.
- Partial regularization for sparse interaction terms.
- Posterior predictive checks.

### Implementation Pattern

```r
bayes_fit <- brms::brm(
  response ~ treatment * (age_c + sex_male_c),
  data = ipd_stc,
  family = brms::bernoulli(),
  prior = c(
    brms::prior(normal(0, 2), class = "b"),
    brms::prior(normal(0, 5), class = "Intercept")
  ),
  chains = 4,
  iter = 4000,
  seed = 12345
)

brms::summary(bayes_fit)
brms::pp_check(bayes_fit)
```

Priors must be justified on the model scale. Report convergence diagnostics and sensitivity to alternative prior scales.

## STC vs MAIC Comparison

| Aspect | STC | MAIC |
|--------|-----|------|
| Method | Outcome regression | Propensity weighting |
| Efficiency | Higher if model correct | Lower when weights reduce ESS |
| Model dependence | Higher | Lower |
| Continuous covariates | Natural | May be limited by reported summaries |
| Extrapolation | Possible, but risky | Limited by overlap |
| Main diagnostics | Model fit, residuals, interactions | ESS, weight distribution, balance |

### When to Prefer STC

- The outcome model is clinically and statistically defensible.
- Key continuous covariates need direct modeling.
- MAIC has poor ESS but the IPD support still covers the target population.
- A Bayesian regression framework is useful for sensitivity analysis.

### When to Prefer MAIC

- Outcome model specification is uncertain.
- A design-based balancing approach is preferred.
- Covariate overlap is adequate and ESS is acceptable.
- The target aggregate summaries can be matched directly.

Run both as sensitivity analyses when feasible. Similar results increase confidence; divergent results require investigation, not automatic averaging.

## Reporting Requirements

### Methods
- [ ] Justification for STC and anchored or unanchored design.
- [ ] Effect modifier selection rationale.
- [ ] Aggregate covariate target values and definitions.
- [ ] Model formula, link function, covariate functional forms, and interactions.
- [ ] Centering approach.
- [ ] External treatment effect source and effect scale.
- [ ] Frequentist or Bayesian uncertainty method.
- [ ] Prior specification if Bayesian.

### Results
- [ ] Model coefficients with uncertainty.
- [ ] Adjusted treatment effect in the external population.
- [ ] Indirect comparison with 95% confidence or credible interval.
- [ ] Comparison with unadjusted ITC and, when feasible, MAIC.
- [ ] Model diagnostics and sensitivity analyses.
- [ ] Limitations from residual unmeasured effect modification or extrapolation.

## Common Pitfalls

### 1. Forgetting to Center Covariates
- The treatment coefficient then targets the wrong covariate values.

### 2. Omitting Interactions for Effect Modifiers
- This does not adjust the relative treatment effect for population differences.

### 3. Selecting Covariates by P-Value Alone
- Interaction tests are underpowered and can be unstable.
- Use clinical rationale and external evidence.

### 4. Including Too Many Covariates
- Interaction models can overfit quickly.
- Preserve events-per-parameter and report instability.

### 5. Ignoring Functional Form
- Nonlinear covariate effects may require splines, transformations, or categories.

### 6. Treating Unanchored STC Like Anchored STC
- Unanchored analyses require all prognostic factors and transportable absolute effects.

### 7. Mixing Effect Scales
- Bucher comparisons must be made on a common additive scale, such as log-OR or log-HR.

## Quick Reference Code

```r
# 1. Choose effect modifiers from clinical rationale and supporting evidence.
effect_modifiers <- c("age", "sex_male")
agd_targets <- c(age = 62, sex_male = 0.55)

# 2. Center IPD on the target population.
ipd_stc <- ipd |>
  dplyr::mutate(
    age_c = age - agd_targets["age"],
    sex_male_c = sex_male - agd_targets["sex_male"],
    treatment = stats::relevel(factor(treatment), ref = "Placebo")
  )

# 3. Fit outcome regression with interactions.
fit <- stats::glm(
  response ~ treatment * (age_c + sex_male_c),
  data = ipd_stc,
  family = stats::binomial()
)

# 4. Extract adjusted A vs common-comparator effect.
coef_name <- "treatmentDrug A"
log_or_ac <- unname(stats::coef(fit)[coef_name])
se_log_or_ac <- sqrt(stats::vcov(fit)[coef_name, coef_name])

# 5. Combine with external B vs common-comparator estimate.
log_or_ab <- log_or_ac - log_or_bc
se_log_or_ab <- sqrt(se_log_or_ac^2 + se_log_or_bc^2)
```

## Resources

- NICE DSU TSD 18: Population-adjusted indirect comparisons
- Phillippo et al. (2016): Methods for population-adjusted indirect comparisons
- Ishak et al. (2015): STC simulation studies
- Current documentation for the modeling packages actually used in the analysis
