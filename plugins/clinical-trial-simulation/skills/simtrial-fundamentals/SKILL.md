---
name: simtrial-fundamentals
description: Core simtrial package functions for time-to-event clinical trial simulation. Use when generating survival data, performing weighted logrank tests, or running TTE simulations.
---

# simtrial Fundamentals

## When to Use This Skill

- Simulating time-to-event (survival) clinical trial data
- Generating piecewise exponential failure/dropout times
- Modeling delayed treatment effects or non-proportional hazards
- Performing weighted logrank tests (Fleming-Harrington, Magirr-Burman)
- Running MaxCombo tests for non-proportional hazards
- Simulating group sequential designs
- Calculating RMST or milestone endpoints

## Package Overview

**simtrial** (v1.0.2) by Merck provides fast, extensible clinical trial simulation for time-to-event endpoints. Key features:
- Piecewise exponential distributions for flexible hazard modeling
- Built-in support for non-proportional hazards scenarios
- Integration with gsDesign2 for group sequential designs
- Parallel computation via doFuture/foreach
- Pipe-friendly API using data.table for performance

## Core Data Generation Functions

### sim_pw_surv() - Main Simulation Function

Generates stratified time-to-event outcome randomized trial data.

```r
sim_pw_surv(
  n = 100,                    # Total sample size
  stratum = data.frame(       # Stratum definitions
    stratum = "All",
    p = 1                     # Prevalence/probability
  ),
  block = c(rep("control", 2), rep("experimental", 2)),  # Randomization block
  enroll_rate = data.frame(   # Enrollment rates by period
    rate = 9,
    duration = 1
  ),
  fail_rate = data.frame(     # Failure rates by stratum/treatment/period
    stratum = rep("All", 4),
    period = rep(1:2, 2),
    treatment = c(rep("control", 2), rep("experimental", 2)),
    duration = rep(c(3, 1), 2),
    rate = log(2) / c(9, 9, 9, 18)  # Hazard rates
  ),
  dropout_rate = data.frame(  # Dropout rates
    stratum = rep("All", 2),
    period = rep(1, 2),
    treatment = c("control", "experimental"),
    duration = rep(100, 2),
    rate = rep(0.001, 2)
  )
)
```

**Returns:** Data frame with columns:
- `stratum`: Patient stratum
- `enroll_time`: Calendar time of enrollment
- `treatment`: Treatment assignment ("control" or "experimental")
- `fail_time`: Time from enrollment to event
- `dropout_time`: Time from enrollment to dropout
- `cte`: Calendar time of event (enroll_time + min(fail_time, dropout_time))
- `fail`: Event indicator (1 = event, 0 = censored)

**Attributes:**
- `ratio`: Randomization ratio (experimental:control)
- `generate_by_simpwsurv`: Marker indicating data origin

### rpwexp() - Piecewise Exponential Random Generation

Generates failure times from piecewise exponential distribution.

```r
rpwexp(
  n = 100,
  fail_rate = data.frame(
    duration = c(3, 100),
    rate = c(0.08, 0.04)  # Hazard rates for each period
  )
)
```

### rpwexp_enroll() - Enrollment Time Generation

Generates enrollment times with piecewise constant rates.

```r
rpwexp_enroll(
  n = 100,
  enroll_rate = data.frame(
    rate = c(5, 10, 20),      # Patients/month
    duration = c(2, 2, 10)    # Period durations
  )
)
```

## Data Cutting Functions

### cut_data_by_event() - Event-Based Cutoff

Cut data when target number of events is reached.

```r
trial_data <- sim_pw_surv(n = 400) |>
  cut_data_by_event(n_events = 200)
```

### cut_data_by_date() - Calendar Time Cutoff

Cut data at specified calendar time.

```r
trial_data <- sim_pw_surv(n = 400) |>
  cut_data_by_date(cut_date = 24)  # 24 months
```

### get_analysis_date() - Advanced Cutoff Logic

Derive analysis date given multiple conditions.

```r
get_analysis_date(
  data,
  planned_calendar_time = 36,        # Minimum calendar time

  target_event_overall = 300,        # Target events
  max_extension_for_target_event = 42,  # Max wait for events
  min_n_overall = 200,               # Minimum enrolled
  min_followup = 12,                 # Minimum follow-up after enrollment
  min_time_after_previous_analysis = 6  # Gap from previous analysis
)
```

## Statistical Analysis Functions

### wlr() - Weighted Logrank Test

Supports multiple weighting schemes.

```r
# Standard logrank (FH(0,0))
data |> wlr(weight = fh(rho = 0, gamma = 0))

# Fleming-Harrington weights
data |> wlr(weight = fh(rho = 0, gamma = 0.5))   # Late effects emphasis
data |> wlr(weight = fh(rho = 1, gamma = 0))     # Early effects emphasis

# Magirr-Burman weights (for delayed effects)
data |> wlr(weight = mb(delay = 4, w_max = 2))

# Early zero weights (Xu 2017)
data |> wlr(weight = early_zero(early_period = 6))
```

**Returns:** List with:
- `method`: "WLR"
- `parameter`: Weight specification (e.g., "FH(rho=0, gamma=0.5)")
- `estimate`: Treatment effect estimate
- `se`: Standard error
- `z`: Z-score (negative favors experimental)
- `info`: Statistical information
- `info0`: Information under null

### Weight Functions

#### fh() - Fleming-Harrington Weights
Weight = S(t)^rho * (1-S(t))^gamma

| rho | gamma | Effect |
|-----|-------|--------|
| 0 | 0 | Standard logrank |
| 0 | 0.5 | Moderate late emphasis |
| 0 | 1 | Strong late emphasis |
| 1 | 0 | Early effects |
| 0.5 | 0.5 | Balanced |

#### mb() - Magirr-Burman Weights
Designed for delayed treatment effects.

```r
mb(delay = 4, w_max = 2)  # Zero weight before delay, capped at w_max
```

#### early_zero() - Early Zero Weights
Sets weights to zero during early period.

```r
early_zero(early_period = 6)  # Zero weight first 6 months
```

### maxcombo() - MaxCombo Test

Combines multiple weighted logrank tests for non-proportional hazards.

```r
data |> maxcombo(
  rho = c(0, 0, 1),
  gamma = c(0, 1, 1),
  return_corr = TRUE
)
```

**Returns:** List with:
- `method`: "MaxCombo"
- `parameter`: Combined test description
- `z`: Z-scores for each component test
- `p_value`: Combined p-value
- `corr`: Correlation matrix (if return_corr = TRUE)

### rmst() - Restricted Mean Survival Time

Alternative endpoint for non-proportional hazards.

```r
data |> rmst(tau = 24)  # RMST at 24 months
```

### milestone() - Milestone Analysis

Test survival difference at fixed time point.

```r
data |> milestone(ms_time = 12, test_type = "naive")
```

## Simulation Functions

### sim_fixed_n() - Fixed Design Simulation

Simulate multiple trials with fixed sample size.

```r
sim_fixed_n(
  n_sim = 1000,
  sample_size = 400,
  target_event = 200,
  enroll_rate = data.frame(rate = 20, duration = 12),
  fail_rate = data.frame(
    stratum = "All",
    duration = c(4, 100),
    fail_rate = log(2)/12,
    hr = c(1, 0.7),
    dropout_rate = 0.001
  ),
  timing_type = 2,  # Time at target events
  rho_gamma = data.frame(rho = c(0, 0), gamma = c(0, 0.5))
)
```

**timing_type options:**
1. Planned study duration
2. Time at target events
3. Planned minimum follow-up
4. Max of (1) and (2)
5. Max of (2) and (3)

### sim_gs_n() - Group Sequential Simulation

Simulate group sequential designs with interim analyses.

```r
library(gsDesign2)

# Define enrollment
enroll_rate <- define_enroll_rate(
  duration = c(4, 12),
  rate = c(10, 30)
)

# Define failure rates with delayed effect
fail_rate <- define_fail_rate(
  duration = c(3, 100),
  fail_rate = log(2)/9,
  hr = c(1, 0.6),
  dropout_rate = 0.001
)

# Define cutting functions
ia1_cut <- create_cut(
  planned_calendar_time = 20,
  target_event_overall = 100,
  max_extension_for_target_event = 24
)

ia2_cut <- create_cut(
  planned_calendar_time = 32,
  target_event_overall = 200,
  min_time_after_previous_analysis = 10
)

fa_cut <- create_cut(
  planned_calendar_time = 45,
  target_event_overall = 350
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

### create_cut() - Create Cutting Function

```r
cutting <- create_cut(
  planned_calendar_time = 36,
  target_event_overall = 300,
  max_extension_for_target_event = 42,
  min_n_overall = 200,
  min_followup = 12,
  min_time_after_previous_analysis = 6
)
```

### create_test() - Create Test Function

```r
# Create reusable test function
my_test <- create_test(wlr, weight = fh(rho = 0, gamma = 0.5))
my_test(trial_data_cut)  # Apply to cut data
```

## Common Patterns

### Delayed Treatment Effect

```r
# 3-month delay before treatment effect kicks in
fail_rate <- data.frame(
  stratum = rep("All", 4),
  period = rep(1:2, 2),
  treatment = c(rep("control", 2), rep("experimental", 2)),
  duration = c(3, 100, 3, 100),
  rate = log(2) / c(12, 12, 12, 18)  # HR=1 then HR=0.67
)
```

### Stratified Analysis

```r
sim_pw_surv(
  n = 400,
  stratum = data.frame(stratum = c("Low", "High"), p = c(0.3, 0.7)),
  fail_rate = data.frame(
    stratum = rep(c("Low", "High"), each = 2),
    period = rep(1, 4),
    treatment = rep(c("control", "experimental"), 2),
    duration = rep(100, 4),
    rate = c(0.05, 0.03, 0.08, 0.05)
  )
)
```

### Unequal Randomization (2:1)

```r
sim_pw_surv(
  n = 300,
  block = c(rep("experimental", 2), "control")  # 2:1 ratio
)
```

### Parallel Computation

```r
library(future)
plan("multisession", workers = 4)

results <- sim_gs_n(
  n_sim = 10000,
  sample_size = 400,
  # ... other parameters
)

plan("sequential")  # Reset to single-threaded
```

## Integration with gsDesign2

```r
library(gsDesign2)

# Design a group sequential trial
design <- gs_design_ahr(
  analysis_time = c(12, 24, 36),
  alpha = 0.025,
  beta = 0.1
) |> to_integer()

# Simulate with updated bounds
sim_gs_n(
  n_sim = 1000,
  sample_size = max(design$analysis$n),
  enroll_rate = design$enroll_rate,
  fail_rate = design$fail_rate,
  test = wlr,
  cut = NULL,  # Automatically created from design
  original_design = design,
  weight = fh(rho = 0, gamma = 0)
)
```

## Utility Functions

### counting_process() - Convert to Counting Process Format

```r
cp_data <- trial_data |>
  cut_data_by_event(200) |>
  counting_process(arm = "experimental")
```

### fit_pwexp() - Fit Piecewise Exponential

Estimate piecewise rates from observed data.

```r
fit_pwexp(
  data,
  intervals = c(0, 6, 12, Inf)  # Breakpoints
)
```

### to_sim_pw_surv() - Format Conversion

Convert gsDesign2 fail_rate format to sim_pw_surv format.

```r
fail_rate_gs2 <- define_fail_rate(...)
converted <- to_sim_pw_surv(fail_rate_gs2)
# Returns list with $fail_rate and $dropout_rate
```

## Example Datasets

Built-in datasets for various scenarios:
- `ex1_delayed_effect`: Delayed treatment benefit
- `ex2_delayed_effect`: Alternative delayed scenario
- `ex3_cure_with_ph`: Cure models with proportional hazards
- `ex4_belly`: Complex non-proportional hazards
- `ex5_widening`: Diverging survival curves
- `ex6_crossing`: Crossing survival curves
- `mb_delayed_effect`: Magirr-Burman delayed effect

## Best Practices

1. **Reproducibility**: Always set seed via SimParameters or set.seed()
2. **Validation**: Compare sim results to analytical solutions where possible
3. **Efficiency**: Use counting_process() once then multiple wlr() calls
4. **Parallelization**: Use plan("multisession") for large simulations
5. **Non-PH**: Consider MaxCombo or weighted tests for delayed effects
6. **Documentation**: Record all simulation parameters for regulatory submissions
