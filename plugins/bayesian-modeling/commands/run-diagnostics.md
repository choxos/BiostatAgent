---
name: run-diagnostics
description: Execute Bayesian models with test data and report convergence diagnostics
---

# Model Execution and Diagnostics Workflow

You are helping the user run and diagnose their Bayesian model.

## Step 1: Identify Model and Data

Determine:
1. **Model language**: Stan / JAGS / WinBUGS / PyMC
2. **Data source**:
   - User-provided data
   - Generate synthetic test data

## Step 2: Generate Test Data (if needed)

Use @test-runner to create appropriate synthetic data:

### For Regression Models
```r
set.seed(42)
N <- 100
K <- 3
X <- matrix(rnorm(N * K), N, K)
true_beta <- c(0.5, -0.3, 0.8)
true_sigma <- 1
y <- X %*% true_beta + rnorm(N, 0, true_sigma)

stan_data <- list(N = N, K = K, X = X, y = as.vector(y))
```

### For Hierarchical Models
```r
set.seed(42)
J <- 8
N_per_group <- 20
true_mu <- 5
true_tau <- 3
true_theta <- rnorm(J, true_mu, true_tau)

y <- unlist(lapply(1:J, function(j) rnorm(N_per_group, true_theta[j], 2)))
group <- rep(1:J, each = N_per_group)

stan_data <- list(N = J * N_per_group, J = J, group = group, y = y)
```

## Step 3: Execute Model

### Stan (cmdstanr)
```r
library(cmdstanr)

# Compile
mod <- cmdstan_model("model.stan")

# Short test run
fit <- mod$sample(
  data = stan_data,
  seed = 12345,
  chains = 2,
  parallel_chains = 2,
  iter_warmup = 500,
  iter_sampling = 500,
  refresh = 100
)
```

### JAGS (R2jags)
```r
library(R2jags)

fit <- jags(
  data = jags_data,
  parameters.to.save = c("mu", "sigma", "theta"),
  model.file = "model.txt",
  n.chains = 2,
  n.iter = 2000,
  n.burnin = 1000,
  progress.bar = "text"
)
```

### PyMC (Python)
```python
import pymc as pm
import arviz as az
import numpy as np

# Define model
with pm.Model() as model:
    # Priors
    mu = pm.Normal("mu", mu=0, sigma=10)
    sigma = pm.HalfNormal("sigma", sigma=1)

    # Likelihood
    y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=y_data)

    # Sample
    trace = pm.sample(
        draws=1000,
        tune=1000,
        chains=2,
        cores=2,
        random_seed=12345,
        return_inferencedata=True
    )

# Diagnostics
print(az.summary(trace))
az.plot_trace(trace)
```

## Step 4: Report Diagnostics

Generate a diagnostic report:

```markdown
## Execution Report

### Model Information
- **Language**: [Stan/JAGS/PyMC]
- **File**: model.stan
- **Test Data**: Synthetic (N=100)

### Sampling Summary
- **Chains**: 2
- **Warmup**: 500
- **Sampling**: 500
- **Total time**: X.X seconds

### Convergence Diagnostics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Max Rhat | X.XX | < 1.01 | ✓/✗ |
| Min ESS (bulk) | XXX | > 400 | ✓/✗ |
| Min ESS (tail) | XXX | > 400 | ✓/✗ |
| Divergences | X | = 0 | ✓/✗ |
| Max treedepth | X | = 0 | ✓/✗ |

### Parameter Summary

| Parameter | Mean | SD | 5% | 95% | Rhat | ESS |
|-----------|------|----|----|-----|------|-----|
| mu | X.XX | X.XX | X.XX | X.XX | X.XX | XXX |
| sigma | X.XX | X.XX | X.XX | X.XX | X.XX | XXX |

### Parameter Recovery (Synthetic Data)

| Parameter | True | Estimate | In 90% CI |
|-----------|------|----------|-----------|
| mu | 5.00 | 5.12 | ✓ |
| sigma | 1.00 | 0.98 | ✓ |

### Warnings
[List any warnings from sampling]

### Recommendations
[Suggestions based on diagnostics]
```

## Step 5: Troubleshooting

If issues detected, provide specific guidance:

### Divergences
```
ISSUE: X divergent transitions detected

SOLUTIONS:
1. Increase adapt_delta:
   fit <- mod$sample(..., adapt_delta = 0.95)

2. Use non-centered parameterization for hierarchical parameters

3. Check for multimodality in posterior
```

### Low ESS
```
ISSUE: ESS for parameter X is only YY

SOLUTIONS:
1. Run longer chains (increase iter_sampling)
2. Check for high autocorrelation
3. Consider reparameterization
```

### High Rhat
```
ISSUE: Rhat for parameter X is Y.YY

SOLUTIONS:
1. Run longer warmup period
2. Check for label switching (mixture models)
3. Verify model is identified
```

## Quick Test Commands

### Test Stan Model
```r
# One-liner syntax check
cmdstanr::cmdstan_model("model.stan", compile = FALSE)$check_syntax()

# Quick test run
source("test_model.R")  # Generated test script
```

### Test JAGS Model
```r
# Quick test
library(R2jags)
test_data <- list(N = 10, y = rnorm(10))
jags(data = test_data, model.file = "model.txt",
     parameters.to.save = "mu", n.chains = 1, n.iter = 100)
```

### Test PyMC Model
```python
import pymc as pm
import numpy as np
import arviz as az

# Quick test
y_test = np.random.randn(20)
with pm.Model() as test_model:
    mu = pm.Normal("mu", 0, 10)
    y = pm.Normal("y", mu=mu, sigma=1, observed=y_test)
    trace = pm.sample(200, tune=200, chains=1, progressbar=False)

print(az.summary(trace))
```

## Convergence Checklist

Before reporting success:
- [ ] All Rhat values < 1.01 (Stan) or < 1.1 (JAGS)
- [ ] All ESS values > 100 (minimum) or > 400 (ideal)
- [ ] Zero divergent transitions (Stan)
- [ ] Not hitting max treedepth (Stan)
- [ ] Parameters recovered (if synthetic data)
- [ ] No obvious pathologies in trace plots
