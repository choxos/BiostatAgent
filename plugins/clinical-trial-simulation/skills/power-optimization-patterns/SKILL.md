---
name: power-optimization-patterns
description: Direct and tradeoff-based optimization strategies for clinical trial design. Use when optimizing sample size, selecting design parameters, or performing sensitivity analysis.
---

# Power Optimization Patterns

## When to Use This Skill

- Optimizing sample size for target power
- Selecting design parameters (randomization ratio, event count)
- Trading off between competing objectives
- Performing sensitivity analysis
- Finding optimal regions across scenarios

## Clinical Trial Optimization Framework

### Problem Formulation

**Components:**
- Data Model D(θ): Parameterized by θ (treatment effects, rates, etc.)
- Analysis Model A(λ): Parameterized by λ (sample size, events, etc.)
- Criterion ψ(λ | θ): Power or other metric

**Objective:**
Find λ* that optimizes ψ(λ | θ) subject to constraints.

## Direct Optimization

### Sample Size Determination

**Objective:** Find minimum n such that Power(n) ≥ target

**Binary Search Algorithm:**
```r
find_sample_size <- function(target_power, effect_size, alpha = 0.025,
                            n_low = 50, n_high = 500, n_sims = 10000) {

  while (n_high - n_low > 5) {
    n_mid <- round((n_low + n_high) / 2)

    # Run CSE with n_mid
    data.model <- DataModel() +
      OutcomeDist(outcome.dist = "NormalDist") +
      SampleSize(n_mid) +
      Sample(id = "Control", outcome.par = parameters(mean = 0, sd = 1)) +
      Sample(id = "Treatment", outcome.par = parameters(mean = effect_size, sd = 1))

    analysis.model <- AnalysisModel() +
      Test(id = "Primary", samples = samples("Control", "Treatment"), method = "TTest")

    evaluation.model <- EvaluationModel() +
      Criterion(id = "Power", method = "MarginalPower",
                tests = tests("Primary"), labels = "Power",
                par = parameters(alpha = alpha))

    results <- CSE(data.model, analysis.model, evaluation.model,
                   SimParameters(n.sims = n_sims, proc.load = "full", seed = 12345))

    power <- results$simulation.results$Power

    if (power >= target_power) {
      n_high <- n_mid
    } else {
      n_low <- n_mid
    }
  }

  return(n_high)
}
```

### Event Count Optimization (TTE)

```r
# Grid search over event counts
event_grid <- seq(200, 400, by = 25)
power_results <- numeric(length(event_grid))

for (i in seq_along(event_grid)) {
  results <- sim_fixed_n(
    n_sim = 10000,
    sample_size = 500,
    target_event = event_grid[i],
    enroll_rate = enroll_rate,
    fail_rate = fail_rate,
    timing_type = 2
  )
  power_results[i] <- mean(results$z < qnorm(0.025))
}

# Find minimum events for 90% power
min_events <- event_grid[min(which(power_results >= 0.90))]
```

## Tradeoff-Based Optimization

### Additive Criterion

**Formula:**
```
ψ_combined(λ) = w₁ × ψ₁(λ) + w₂ × ψ₂(λ)
```

**Example: Power vs Sample Size**
```r
# Weights: 70% power importance, 30% sample size (negative for minimization)
w1 <- 0.7
w2 <- -0.3  # Negative because we want to minimize sample size

sample_sizes <- seq(60, 120, by = 10)
combined_scores <- numeric(length(sample_sizes))

for (i in seq_along(sample_sizes)) {
  n <- sample_sizes[i]

  # Simulate power
  # ... CSE simulation ...
  power <- results$simulation.results$Power

  # Normalize sample size to [0,1] scale
  n_normalized <- (n - min(sample_sizes)) / (max(sample_sizes) - min(sample_sizes))

  combined_scores[i] <- w1 * power + w2 * n_normalized
}

optimal_n <- sample_sizes[which.max(combined_scores)]
```

### Constrained Optimization

**Problem:** Maximize ψ₁(λ) subject to ψ₂(λ) ≥ c

**Example: Maximize secondary power subject to primary power ≥ 90%**
```r
# Grid search with constraint
secondary_power <- numeric(length(weight_grid))
primary_power <- numeric(length(weight_grid))

for (i in seq_along(weight_grid)) {
  w <- weight_grid[i]

  # Configure multiplicity with weight w for primary
  # ... run CSE ...

  primary_power[i] <- results$simulation.results$Primary_Power
  secondary_power[i] <- results$simulation.results$Secondary_Power
}

# Find optimal weight satisfying constraint
valid_idx <- which(primary_power >= 0.90)
optimal_w <- weight_grid[valid_idx[which.max(secondary_power[valid_idx])]]
```

## Sensitivity Analysis

### Qualitative Sensitivity (Pivoting)

Evaluate optimal λ across multiple θ scenarios.

```r
# Define scenarios
scenarios <- list(
  conservative = parameters(mean = 0.3, sd = 1),
  expected = parameters(mean = 0.5, sd = 1),
  optimistic = parameters(mean = 0.7, sd = 1)
)

optimal_n <- list()

for (scenario_name in names(scenarios)) {
  effect <- scenarios[[scenario_name]]

  # Find optimal n for this scenario
  optimal_n[[scenario_name]] <- find_sample_size(
    target_power = 0.90,
    effect_size = effect$mean
  )
}

# Report range
cat("Sample size range:", min(unlist(optimal_n)), "-", max(unlist(optimal_n)))
```

### Quantitative Sensitivity (Bootstrap)

Perturb θ and evaluate robustness of optimal λ.

```r
# Bootstrap perturbation of effect size
n_bootstrap <- 1000
bootstrap_power <- numeric(n_bootstrap)

optimal_n <- 100  # Fixed design choice

for (b in 1:n_bootstrap) {
  # Perturb effect size (e.g., from prior distribution)
  effect_b <- rnorm(1, mean = 0.5, sd = 0.1)

  # Simulate power at optimal_n
  # ... CSE with effect_b ...
  bootstrap_power[b] <- results$simulation.results$Power
}

# Robustness metrics
cat("Mean power:", mean(bootstrap_power), "\n")
cat("Power 95% CI:", quantile(bootstrap_power, c(0.025, 0.975)), "\n")
cat("P(power >= 80%):", mean(bootstrap_power >= 0.80), "\n")
```

## Optimal Intervals and Regions

### Optimal Interval

The η-optimal interval contains all λ values within η% of optimal power.

```r
# Define optimal interval
eta <- 0.95  # 95% of maximum power

sample_sizes <- seq(50, 150, by = 5)
power_curve <- numeric(length(sample_sizes))

for (i in seq_along(sample_sizes)) {
  # ... simulate power ...
  power_curve[i] <- power_at_n
}

max_power <- max(power_curve)
threshold <- eta * max_power

# Find interval boundaries
optimal_interval <- sample_sizes[power_curve >= threshold]
cat("95%-optimal interval: [", min(optimal_interval), ",", max(optimal_interval), "]")
```

### Joint Optimal Region

Intersection of optimal intervals across scenarios.

```r
# Find joint optimal region
intervals <- list()

for (scenario in scenarios) {
  # Get optimal interval for this scenario
  intervals[[scenario]] <- find_optimal_interval(scenario, eta = 0.95)
}

# Joint region = intersection
joint_region <- Reduce(intersect, intervals)
cat("Joint optimal sample sizes:", joint_region)
```

## Compound Criteria

### Minimum Power

**Use:** Ensure robustness across scenarios

```r
# Evaluate minimum power across scenarios
evaluate_min_power <- function(n, scenarios) {
  powers <- numeric(length(scenarios))

  for (i in seq_along(scenarios)) {
    # ... simulate power for scenario i ...
    powers[i] <- power_i
  }

  return(min(powers))
}

# Optimize for minimum power
min_powers <- sapply(sample_sizes, evaluate_min_power, scenarios = scenarios)
optimal_n <- sample_sizes[which.max(min_powers)]
```

### Average Power

**Use:** Balance across scenarios

```r
evaluate_avg_power <- function(n, scenarios, weights = NULL) {
  if (is.null(weights)) weights <- rep(1/length(scenarios), length(scenarios))

  powers <- numeric(length(scenarios))
  for (i in seq_along(scenarios)) {
    powers[i] <- simulate_power(n, scenarios[[i]])
  }

  return(sum(weights * powers))
}
```

## Multiplicity Optimization

### Gamma Parameter Optimization

```r
gamma_grid <- seq(0.5, 1.0, by = 0.05)
results_list <- list()

for (i in seq_along(gamma_grid)) {
  g <- gamma_grid[i]

  analysis.model <- AnalysisModel() +
    # Tests ...
    MultAdjProc(
      proc = "ParallelGatekeepingAdj",
      par = parameters(
        family = families(family1 = c(1, 2), family2 = c(3, 4)),
        proc = families(family1 = "HolmAdj", family2 = "HolmAdj"),
        gamma = families(family1 = g, family2 = 1)
      )
    )

  results_list[[i]] <- CSE(data.model, analysis.model, evaluation.model,
                           SimParameters(n.sims = 10000, proc.load = "full", seed = i))
}

# Extract powers and find optimal gamma
# ... (subject to FWER constraint)
```

### Weight Allocation Optimization

```r
# Optimize weights in chain procedure
weight_grid <- expand.grid(
  w1 = seq(0.3, 0.7, by = 0.1),
  w2 = seq(0.3, 0.7, by = 0.1)
) |> subset(w1 + w2 == 1)

# Evaluate each weight combination
# ... and select optimal weights
```

## Best Practices

1. **Define Clear Objective**: Power, sample size, cost, or combination
2. **Consider All Scenarios**: Use qualitative sensitivity for range
3. **Validate Constraints**: Check FWER, minimum power thresholds
4. **Document Trade-offs**: Explain rationale for chosen parameters
5. **Report Robustness**: Show performance across scenarios
6. **Pre-specify Optimization**: Define optimization strategy in SAP
