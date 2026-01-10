---
name: review-model
description: Review and improve existing Bayesian models for correctness, efficiency, and best practices
---

# Bayesian Model Review Workflow

You are reviewing a user's existing Bayesian model. Follow this structured approach:

## Step 1: Receive Model Code

Ask the user to paste their model code. Automatically detect:
- Language (Stan / JAGS / WinBUGS)
- Model type
- Complexity level

## Step 2: Syntax Check

### For Stan:
- Valid block order (functions → data → transformed data → parameters → transformed parameters → model → generated quantities)
- Correct array syntax (`array[N] real`, not `real[N]`)
- Proper constraint syntax (`<lower=0>`, `simplex`, etc.)
- Semicolons on all statements

### For JAGS/WinBUGS:
- Single `model { }` block
- Proper distribution prefix (`d` for distributions)
- Correct indexing syntax
- Valid truncation syntax (`T(lower, upper)`)

## Step 3: Statistical Review

Check the following using @model-reviewer:

### Priors
- [ ] All parameters have explicit priors
- [ ] Priors are appropriate for the scale of data
- [ ] No improper priors that could cause issues
- [ ] Informative priors are justified

### Parameterization
- [ ] **Stan**: Using SD (sigma), not precision
- [ ] **BUGS/JAGS**: Using precision (tau = 1/sigma²) correctly
- [ ] Covariance vs precision matrices are correct
- [ ] Hierarchical models: centered vs non-centered appropriateness

### Efficiency
- [ ] Vectorization used where possible (Stan)
- [ ] No unnecessary loops
- [ ] Appropriate transformed parameter placement
- [ ] Cholesky factors for covariance matrices

### Common Errors
- [ ] Integer division issues
- [ ] Missing constraints on parameters
- [ ] Potential numerical overflow/underflow
- [ ] Invalid parameter combinations

## Step 4: Generate Report

Provide a structured review:

```markdown
## Model Review Report

### Language Detected
[Stan / JAGS / WinBUGS]

### Model Type
[Hierarchical / Regression / Time Series / etc.]

### Syntax Issues
- [List any syntax errors or warnings]

### Statistical Concerns
- [List concerns about priors, parameterization, etc.]

### Efficiency Improvements
- [Suggestions for better performance]

### Recommended Changes
1. [Specific change with code example]
2. [Another change...]

### Corrected Model (if needed)
[Full corrected model code]
```

## Step 5: Offer Improvements

Based on review, offer to:
1. Fix identified issues
2. Add missing components (generated quantities, diagnostics)
3. Convert to different language (Stan ↔ JAGS)
4. Add posterior predictive checks

## Example Review Output

```
## Model Review Report

### Language Detected
JAGS

### Syntax Issues
✓ No syntax errors detected

### Statistical Concerns
⚠️ **Prior on tau is very vague**: `tau ~ dgamma(0.001, 0.001)` can
   cause sampling issues. Consider `sigma ~ dunif(0, 100)` with
   `tau <- pow(sigma, -2)` instead.

⚠️ **Missing prior on alpha**: The intercept `alpha` has no prior,
   defaulting to improper uniform.

### Efficiency Improvements
- Consider combining the two loops on lines 5-8 and 10-13

### Recommended Changes

1. Add prior for alpha:
   ```
   alpha ~ dnorm(0, 0.0001)
   ```

2. Use half-uniform prior on SD:
   ```
   sigma ~ dunif(0, 100)
   tau <- pow(sigma, -2)
   ```
```

## Critical Checklist

When reviewing any model:

1. **Language Detection**: Look for `~` (both), `target +=` (Stan only), `dnorm`/`dgamma` (BUGS)
2. **Parameterization Warning**: If converting or comparing, ALWAYS note SD vs precision
3. **Prior Completeness**: Every stochastic node in parameters needs a prior
4. **Computational Issues**: Divergences, low ESS, and Rhat problems often trace to parameterization
