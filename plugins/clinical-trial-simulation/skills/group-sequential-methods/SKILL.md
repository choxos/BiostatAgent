---
name: group-sequential-methods
description: Group sequential design methods for interim analyses, alpha spending, and futility stopping. Use when designing trials with interim looks or implementing spending functions.
---

# Group Sequential Methods

## When to Use This Skill

- Designing group sequential trials with interim analyses
- Implementing alpha spending functions
- Setting futility stopping rules
- Calculating information fractions
- Using sim_gs_n() for GS simulations
- Integrating with gsDesign2 package

## Fundamental Concepts

### Group Sequential Design

A group sequential design allows for:
- **Early stopping for efficacy**: If treatment effect is larger than expected
- **Early stopping for futility**: If treatment effect is unlikely to reach significance
- **Reduced expected sample size**: When treatment effect is present

### Information Fraction

Information fraction at analysis k:
```
I_k / I_K = (events at analysis k) / (total planned events)
```

For time-to-event trials, information ≈ number of events.

### Type I Error Spending

The key constraint: Σ α_k ≤ α (overall Type I error)

Spending functions distribute alpha across analyses.

## Alpha Spending Functions

### O'Brien-Fleming (OBF)

**Properties:**
- Conservative at early analyses
- Nearly full alpha at final analysis
- Difficult to stop early
- Maintains nominal Type I error

**Formula:**
```
α*(t) = 2 - 2Φ(z_{α/2} / √t)
```

**When to Use:**
- Want maximum power at final analysis
- Early efficacy stopping unlikely
- Regulatory preference for conservative early bounds

### Pocock

**Properties:**
- Equal spending at each analysis
- Easier to stop early
- Inflated final alpha
- Lower power at final analysis

**Formula:**
```
α*(t) = α × log(1 + (e-1)t)
```

**When to Use:**
- Early stopping is a priority
- Treatment effect expected to be large
- Willing to sacrifice final analysis power

### Hwang-Shih-DeCani (HSD)

**Properties:**
- Flexible family indexed by γ
- γ = -4: Similar to OBF
- γ = 1: Similar to Pocock
- γ = 0: Linear (Pocock-like)

**Formula:**
```
α*(t) = α × (1 - e^{-γt}) / (1 - e^{-γ})
```

**When to Use:**
- Want flexibility between OBF and Pocock
- Customized spending pattern needed

### Spending Function Comparison

| Function | Early Spending | Final Power | Early Stopping |
|----------|---------------|-------------|----------------|
| OBF | Low | High | Difficult |
| Pocock | High | Lower | Easier |
| HSD(γ=-4) | Low | High | Difficult |
| HSD(γ=1) | High | Lower | Easier |

## Futility Boundaries

### Binding Futility

- If futility boundary crossed, trial MUST stop
- Affects Type I error calculation
- More powerful than non-binding

### Non-Binding Futility

- Crossing futility boundary is advisory
- Trial can continue at investigator discretion
- Conservative: assumes no early stopping for futility in Type I error

### Beta-Spending for Futility

Similar to alpha-spending, but for Type II error:
```
β*(t) = spending function × β
```

## simtrial GS Implementation

### create_cut() - Define Analysis Timing

```r
# Interim Analysis 1
ia1_cut <- create_cut(
  planned_calendar_time = 20,        # Minimum 20 months
  target_event_overall = 100,        # Target 100 events
  max_extension_for_target_event = 24,  # Wait up to 24 months for events
  min_n_overall = 200,               # At least 200 enrolled
  min_followup = 12                  # 12 months minimum follow-up
)

# Interim Analysis 2
ia2_cut <- create_cut(
  planned_calendar_time = 32,
  target_event_overall = 200,
  max_extension_for_target_event = 34,
  min_time_after_previous_analysis = 10  # At least 10 months after IA1
)

# Final Analysis
fa_cut <- create_cut(
  planned_calendar_time = 45,
  target_event_overall = 350
)
```

### sim_gs_n() - Run GS Simulations

```r
library(simtrial)
library(gsDesign2)

# Define enrollment
enroll_rate <- define_enroll_rate(
  duration = c(4, 12),
  rate = c(10, 30)
)

# Define failure rates
fail_rate <- define_fail_rate(
  duration = c(3, 100),
  fail_rate = log(2)/9,
  hr = c(1, 0.6),
  dropout_rate = 0.001
)

# Run simulation
results <- sim_gs_n(
  n_sim = 1000,
  sample_size = 400,
  enroll_rate = enroll_rate,
  fail_rate = fail_rate,
  test = wlr,
  cut = list(ia1 = ia1_cut, ia2 = ia2_cut, fa = fa_cut),
  weight = fh(rho = 0, gamma = 0)
)
```

### Integration with gsDesign2

```r
library(gsDesign2)

# Design with gsDesign2
design <- gs_design_ahr(
  enroll_rate = define_enroll_rate(duration = c(4, 12), rate = c(10, 30)),
  fail_rate = define_fail_rate(
    duration = c(3, 100),
    fail_rate = log(2)/9,
    hr = c(1, 0.6),
    dropout_rate = 0.001
  ),
  alpha = 0.025,
  beta = 0.1,
  analysis_time = c(24, 36, 48),
  upper = gs_spending_bound,
  upar = list(sf = gsDesign::sfLDOF, total_spend = 0.025),
  lower = gs_spending_bound,
  lpar = list(sf = gsDesign::sfHSD, param = -4, total_spend = 0.1)
) |> to_integer()

# Simulate with design object
sim_results <- sim_gs_n(
  n_sim = 1000,
  sample_size = max(design$analysis$n),
  enroll_rate = design$enroll_rate,
  fail_rate = design$fail_rate,
  test = wlr,
  cut = NULL,  # Auto-generated from design
  original_design = design,
  weight = fh(rho = 0, gamma = 0)
)
```

### Bound Updates with sim_gs_n()

When using `original_design`, sim_gs_n() can compute updated bounds:

```r
# Results include planned and updated bounds
results <- sim_gs_n(
  # ... parameters ...
  original_design = design,
  ia_alpha_spending = "min_planned_actual",  # Conservative
  fa_alpha_spending = "full_alpha"           # Spend full alpha at FA
)

# Output includes:
# - planned_upper_bound, planned_lower_bound
# - updated_upper_bound, updated_lower_bound
```

**Alpha Spending Options:**

| ia_alpha_spending | Description |
|-------------------|-------------|
| "min_planned_actual" | Conservative: min of planned and actual |
| "actual" | Spend based on actual information |

| fa_alpha_spending | Description |
|-------------------|-------------|
| "full_alpha" | Spend remaining alpha at final |
| "info_frac" | Spend based on information fraction |

## Different Tests Across Analyses

```r
# Different tests at each analysis
ia1_test <- create_test(wlr, weight = fh(rho = 0, gamma = 0))
ia2_test <- create_test(wlr, weight = fh(rho = 0, gamma = 0.5))
fa_test <- create_test(wlr, weight = mb(delay = 6, w_max = Inf))

results <- sim_gs_n(
  n_sim = 1000,
  sample_size = 400,
  enroll_rate = enroll_rate,
  fail_rate = fail_rate,
  test = list(ia1 = ia1_test, ia2 = ia2_test, fa = fa_test),
  cut = list(ia1 = ia1_cut, ia2 = ia2_cut, fa = fa_cut)
)
```

## Common GS Patterns

### Two-Look Design (1 IA + FA)

```r
# IA at 50% information, FA at 100%
ia_cut <- create_cut(target_event_overall = 150)  # 50%
fa_cut <- create_cut(target_event_overall = 300)  # 100%

sim_gs_n(
  n_sim = 1000,
  sample_size = 400,
  test = wlr,
  cut = list(ia = ia_cut, fa = fa_cut),
  weight = fh(0, 0)
)
```

### Three-Look Design (2 IA + FA)

```r
# Standard 33%, 67%, 100% information
ia1_cut <- create_cut(target_event_overall = 100)
ia2_cut <- create_cut(target_event_overall = 200)
fa_cut <- create_cut(target_event_overall = 300)
```

### Event-Driven with Calendar Constraints

```r
# Events-based but with minimum calendar time
ia_cut <- create_cut(
  target_event_overall = 150,
  planned_calendar_time = 18,  # At least 18 months
  max_extension_for_target_event = 24  # Max 24 months
)
```

## Operating Characteristics

### Key Metrics to Evaluate

1. **Power**: P(reject H0 | H1 true)
2. **Type I Error**: P(reject H0 | H0 true)
3. **Expected Sample Size**: E[N] under H0 and H1
4. **Expected Events**: E[events] at each analysis
5. **Stopping Probabilities**: P(stop at analysis k)

### Simulation Summary

```r
# Summarize simulation results
results_summary <- results |>
  group_by(analysis) |>
  summarise(
    mean_events = mean(event),
    mean_z = mean(z),
    power = mean(z < qnorm(0.025)),  # One-sided
    .groups = "drop"
  )
```

## Best Practices

1. **Information Fraction**: Target evenly spaced (e.g., 50%, 100% or 33%, 67%, 100%)
2. **Alpha Spending**: OBF is default for most regulatory submissions
3. **Futility**: Use non-binding to preserve flexibility
4. **Validation**: Compare simulated power to gsDesign analytical results
5. **Documentation**: Record all boundary calculations for regulatory submission
6. **Parallelization**: Use `plan("multisession")` for large simulations

## Regulatory Considerations

- Pre-specify number and timing of interim analyses
- Pre-specify spending function and parameters
- Document stopping rules clearly in protocol
- Consider DSMB recommendations for unblinded reviews
- Maintain blinding for operational team
