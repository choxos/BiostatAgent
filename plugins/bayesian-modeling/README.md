# Bayesian Modeling Plugin

> **Bayesian Model Creation & Validation** — Create, review, and test Bayesian models in Stan, PyMC, JAGS, and WinBUGS

Part of the [BiostatAgent](https://github.com/choxos/BiostatAgent) ecosystem.

## Overview

This plugin provides AI-assisted workflows for Bayesian statistical modeling across four major probabilistic programming languages:

| Language | Interface | Parameterization | Sampling |
|----------|-----------|------------------|----------|
| **Stan 2.37** | cmdstanr | SD (σ) | HMC/NUTS |
| **PyMC 5** | Python native | SD (σ) | NUTS/Metropolis |
| **JAGS** | R2jags | Precision (τ = 1/σ²) | Gibbs |
| **WinBUGS** | R2WinBUGS | Precision (τ = 1/σ²) | Gibbs |

## Quick Start

```bash
# Install plugin
/plugin install bayesian-modeling

# Create a model
/create-model
```

## Commands

### `/create-model`
Interactive workflow for creating Bayesian models from natural language descriptions.

**Example:**
```
Create a hierarchical model for student test scores nested within schools.
Include student-level predictors (study_hours, prior_gpa) and school-level
predictor (school_size). Use Stan with cmdstanr.
```

**Workflow:**
1. Clarify model structure and data
2. Select appropriate priors
3. Generate complete model code
4. Provide R/Python integration code
5. Include posterior predictive checks

### `/review-model`
Review existing Bayesian models for correctness, efficiency, and best practices.

**Checks:**
- Syntax correctness
- Prior completeness and appropriateness
- Parameterization efficiency (centered vs non-centered)
- Common errors (SD vs precision confusion)
- Sampling efficiency recommendations

### `/run-diagnostics`
Execute models with synthetic data to validate convergence.

**Reports:**
- Rhat convergence statistics
- Effective sample size (ESS)
- Divergence detection
- Parameter recovery validation

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `model-architect` | Haiku | Routes requests to language specialists |
| `stan-specialist` | Sonnet | Stan 2.37 expert with cmdstanr integration |
| `pymc-specialist` | Sonnet | PyMC 5 expert with ArviZ diagnostics |
| `bugs-specialist` | Sonnet | JAGS/WinBUGS expert with precision parameterization |
| `model-reviewer` | Sonnet | Reviews models for correctness and efficiency |
| `test-runner` | Haiku | Executes models with synthetic data |

## Skills

### Language Fundamentals
- **stan-fundamentals** — Stan 2.37 syntax, blocks, distributions, cmdstanr integration
- **pymc-fundamentals** — PyMC 5 syntax, distributions, ArviZ diagnostics
- **bugs-fundamentals** — JAGS/WinBUGS syntax, precision parameterization, R integration

### Model Types
- **hierarchical-models** — Multilevel models, random effects, partial pooling
- **regression-models** — Linear, logistic, Poisson, negative binomial, robust regression
- **time-series-models** — AR, MA, ARMA, state-space, dynamic linear models
- **survival-models** — Exponential, Weibull, log-normal, piecewise hazard
- **meta-analysis** — Fixed effects, random effects, network meta-analysis

### Diagnostics
- **model-diagnostics** — Rhat, ESS, divergences, posterior predictive checks

## Critical: Parameterization Differences

**The most common source of errors when working across languages:**

| Distribution | Stan | PyMC | JAGS/WinBUGS |
|-------------|------|------|--------------|
| Normal | `normal(mu, sigma)` — SD | `Normal(mu, sigma)` — SD | `dnorm(mu, tau)` — precision |
| Multivariate Normal | `multi_normal(mu, Sigma)` — cov | `MvNormal(mu, cov)` — cov | `dmnorm(mu, Omega)` — precision matrix |
| Gamma | `gamma(alpha, beta)` — rate | `Gamma(alpha, beta)` — rate | `dgamma(shape, rate)` — rate |

**Conversion:** τ = 1/σ² (precision = 1/variance)

The agents automatically handle these differences when creating or converting models.

## Usage Examples

### Hierarchical Linear Model (Stan)

```
I need a hierarchical model for patient blood pressure measurements.
Patients are nested within clinics. Include patient age as a predictor
and allow the age effect to vary by clinic. Use Stan.
```

**Generated Stan code:**
```stan
data {
  int<lower=0> N;           // observations
  int<lower=0> J;           // clinics
  int<lower=1,upper=J> clinic[N];
  vector[N] age;
  vector[N] bp;
}
parameters {
  real alpha;               // global intercept
  real beta;                // global age effect
  vector[J] alpha_j;        // clinic intercepts
  vector[J] beta_j;         // clinic age effects
  real<lower=0> sigma;      // residual SD
  real<lower=0> sigma_alpha;
  real<lower=0> sigma_beta;
}
model {
  // Priors
  alpha ~ normal(120, 20);
  beta ~ normal(0, 5);
  sigma ~ exponential(0.1);
  sigma_alpha ~ exponential(1);
  sigma_beta ~ exponential(1);

  // Hierarchical priors
  alpha_j ~ normal(0, sigma_alpha);
  beta_j ~ normal(0, sigma_beta);

  // Likelihood
  bp ~ normal(alpha + alpha_j[clinic] + (beta + beta_j[clinic]) .* age, sigma);
}
```

### Logistic Regression (PyMC)

```
Create a Bayesian logistic regression in Python for binary classification
with 3 predictors. Use weakly informative priors.
```

**Generated PyMC code:**
```python
import pymc as pm
import arviz as az

with pm.Model() as logistic_model:
    # Priors
    alpha = pm.Normal("alpha", mu=0, sigma=2.5)
    beta = pm.Normal("beta", mu=0, sigma=2.5, shape=3)

    # Linear predictor
    eta = alpha + pm.math.dot(X, beta)

    # Likelihood
    p = pm.math.invlogit(eta)
    y_obs = pm.Bernoulli("y_obs", p=p, observed=y)

    # Sample
    trace = pm.sample(2000, tune=1000, return_inferencedata=True)

# Diagnostics
az.summary(trace)
az.plot_trace(trace)
```

### Random Effects Meta-Analysis (JAGS)

```
Create a random effects meta-analysis model in JAGS for combining
treatment effects from multiple studies.
```

**Generated JAGS code:**
```r
model {
  for (i in 1:n_studies) {
    # Likelihood
    y[i] ~ dnorm(theta[i], prec[i])
    prec[i] <- 1 / (se[i]^2)

    # Random effects
    theta[i] ~ dnorm(mu, tau_theta)
  }

  # Priors
  mu ~ dnorm(0, 0.001)           # Overall effect
  tau_theta <- 1 / (sigma_theta^2)
  sigma_theta ~ dunif(0, 10)     # Between-study SD

  # Derived quantities
  I2 <- sigma_theta^2 / (sigma_theta^2 + mean(se^2))
}
```

## R Dependencies

```r
# Stan
install.packages("cmdstanr", repos = c("https://mc-stan.org/r-packages/", getOption("repos")))
cmdstanr::install_cmdstan()

# JAGS
install.packages("R2jags")
# Also install JAGS: https://mcmc-jags.sourceforge.io/

# WinBUGS (Windows only)
install.packages("R2WinBUGS")

# Diagnostics
install.packages(c("bayesplot", "loo", "posterior"))
```

## Python Dependencies

```bash
pip install pymc arviz numpy pandas
```

## Supported Model Types

| Model Type | Stan | PyMC | JAGS | WinBUGS |
|------------|:----:|:----:|:----:|:-------:|
| Linear regression | ✓ | ✓ | ✓ | ✓ |
| Logistic regression | ✓ | ✓ | ✓ | ✓ |
| Poisson/NegBin regression | ✓ | ✓ | ✓ | ✓ |
| Hierarchical/Multilevel | ✓ | ✓ | ✓ | ✓ |
| Time series (AR, ARMA) | ✓ | ✓ | ✓ | ✓ |
| State-space models | ✓ | ✓ | ✓ | ✓ |
| Survival analysis | ✓ | ✓ | ✓ | ✓ |
| Meta-analysis | ✓ | ✓ | ✓ | ✓ |
| Gaussian processes | ✓ | ✓ | - | - |
| Mixture models | ✓ | ✓ | ✓ | ✓ |

## References

- Stan Development Team (2024). Stan Modeling Language Users Guide and Reference Manual, 2.37
- Salvatier J, Wiecki TV, Fonnesbeck C (2016). Probabilistic programming in Python using PyMC3
- Plummer M (2003). JAGS: A program for analysis of Bayesian graphical models using Gibbs sampling
- Gelman A, et al. (2013). Bayesian Data Analysis, Third Edition

## License

MIT License — see [LICENSE](../../LICENSE) for details.
