---
name: clinical-trial-design-patterns
description: Common clinical trial design patterns including multi-arm, multi-endpoint, adaptive, and stratified designs. Use when selecting or implementing trial designs.
---

# Clinical Trial Design Patterns

## When to Use This Skill

- Selecting appropriate trial design for clinical objectives
- Implementing multi-arm or multi-endpoint trials
- Designing stratified trials
- Planning adaptive designs
- Understanding design trade-offs

## Two-Arm Parallel Design

### Standard Design

The most common design: randomize patients to treatment or control.

```r
# simtrial implementation
sim_pw_surv(
  n = 400,
  block = c(rep("control", 1), rep("experimental", 1)),  # 1:1
  enroll_rate = data.frame(rate = 20, duration = 12),
  fail_rate = fail_rate
)
```

```r
# Mediana implementation
DataModel() +
  OutcomeDist(outcome.dist = "NormalDist") +
  SampleSize(200) +  # Per arm
  Sample(id = "Control", outcome.par = parameters(mean = 0, sd = 1)) +
  Sample(id = "Treatment", outcome.par = parameters(mean = 0.5, sd = 1))
```

### Unequal Randomization

**When to Use:**
- Increase exposure to experimental treatment
- Ethical considerations
- Resource optimization

```r
# 2:1 randomization (experimental:control)
sim_pw_surv(
  n = 300,
  block = c("control", rep("experimental", 2))
)

# Mediana with unequal allocation
DataModel() +
  Sample(id = "Control", sample.size = 100, ...) +
  Sample(id = "Treatment", sample.size = 200, ...)
```

**Trade-off:** Unequal allocation reduces power for same total N.

## Multi-Arm Designs

### Dose-Finding (Multiple Doses vs Placebo)

```r
# Three doses + placebo
DataModel() +
  OutcomeDist(outcome.dist = "NormalDist") +
  SampleSize(75) +  # Per arm
  Sample(id = "Placebo", outcome.par = parameters(mean = 0, sd = 1)) +
  Sample(id = "Low Dose", outcome.par = parameters(mean = 0.3, sd = 1)) +
  Sample(id = "Mid Dose", outcome.par = parameters(mean = 0.5, sd = 1)) +
  Sample(id = "High Dose", outcome.par = parameters(mean = 0.7, sd = 1))

# Analysis with Dunnett-type comparison
AnalysisModel() +
  Test(id = "Low vs Placebo", samples = samples("Placebo", "Low Dose"), method = "TTest") +
  Test(id = "Mid vs Placebo", samples = samples("Placebo", "Mid Dose"), method = "TTest") +
  Test(id = "High vs Placebo", samples = samples("Placebo", "High Dose"), method = "TTest") +
  MultAdjProc(proc = "HolmAdj")
```

### Active Comparator Design

```r
# Treatment vs Active Control
DataModel() +
  Sample(id = "Active Control", outcome.par = parameters(mean = 0.4, sd = 1)) +
  Sample(id = "New Treatment", outcome.par = parameters(mean = 0.6, sd = 1))
```

## Multi-Endpoint Designs

### Co-Primary Endpoints

Both endpoints must be significant for trial success.

```r
# Correlated endpoints
corr.matrix <- matrix(c(1.0, 0.5, 0.5, 1.0), 2, 2)

DataModel() +
  OutcomeDist(outcome.dist = "MVNormalDist") +
  SampleSize(100) +
  Sample(id = list("Control E1", "Control E2"),
         outcome.par = parameters(
           parameters(par = parameters(
             parameters(mean = 0, sd = 1),
             parameters(mean = 0, sd = 1)
           ), corr = corr.matrix))) +
  Sample(id = list("Treatment E1", "Treatment E2"),
         outcome.par = parameters(
           parameters(par = parameters(
             parameters(mean = 0.4, sd = 1),
             parameters(mean = 0.3, sd = 1)
           ), corr = corr.matrix)))

# Evaluation: Conjunctive power (both must be significant)
EvaluationModel() +
  Criterion(id = "Co-primary",
            method = "ConjunctivePower",
            tests = tests("E1 Test", "E2 Test"),
            par = parameters(alpha = 0.025))
```

### Hierarchical Endpoints

Primary must succeed before secondary is tested.

```r
# Primary → Key Secondary → Other Secondary
AnalysisModel() +
  Test(id = "Primary", ...) +
  Test(id = "Key Secondary", ...) +
  Test(id = "Other Secondary", ...) +
  MultAdjProc(proc = "FixedSeqAdj")
```

### Multiple Primary with Gatekeeping

```r
# Two primary, two secondary
MultAdjProc(
  proc = "ParallelGatekeepingAdj",
  par = parameters(
    family = families(family1 = c(1, 2), family2 = c(3, 4)),
    proc = families(family1 = "HolmAdj", family2 = "HolmAdj"),
    gamma = families(family1 = 0.8, family2 = 1)
  )
)
```

## Stratified Designs

### Single Stratification Factor

```r
# simtrial stratification
sim_pw_surv(
  n = 400,
  stratum = data.frame(
    stratum = c("Low Risk", "High Risk"),
    p = c(0.4, 0.6)  # Prevalence
  ),
  fail_rate = data.frame(
    stratum = rep(c("Low Risk", "High Risk"), each = 2),
    period = rep(1, 4),
    treatment = rep(c("control", "experimental"), 2),
    duration = rep(100, 4),
    rate = c(0.03, 0.02, 0.06, 0.04)  # Different by stratum
  )
)
```

### Biomarker-Defined Subgroups

```r
# Marker-positive and marker-negative populations
DataModel() +
  OutcomeDist(outcome.dist = "NormalDist") +
  SampleSize(100) +
  Sample(id = "Control M+", outcome.par = parameters(mean = 0, sd = 1)) +
  Sample(id = "Control M-", outcome.par = parameters(mean = 0, sd = 1)) +
  Sample(id = "Treatment M+", outcome.par = parameters(mean = 0.6, sd = 1)) +
  Sample(id = "Treatment M-", outcome.par = parameters(mean = 0.2, sd = 1))

# Pooled analysis (Overall Population)
AnalysisModel() +
  Test(id = "Overall",
       samples = samples(c("Control M+", "Control M-"),
                        c("Treatment M+", "Treatment M-")),
       method = "TTest")

# Subgroup analysis
AnalysisModel() +
  Test(id = "M+ Subgroup",
       samples = samples("Control M+", "Treatment M+"),
       method = "TTest") +
  Test(id = "M- Subgroup",
       samples = samples("Control M-", "Treatment M-"),
       method = "TTest")
```

## Event-Driven Designs

### Time-to-Event with Fixed Events

```r
# Mediana event-driven
DataModel() +
  OutcomeDist(outcome.dist = "ExpoDist", outcome.type = "event") +
  Event(n.events = c(300, 350, 400), rando.ratio = c(1, 1)) +
  Design(
    enroll.period = 24,
    study.duration = 48,
    enroll.dist = "UniformDist",
    dropout.dist = "ExpoDist",
    dropout.dist.par = parameters(rate = 0.01)
  ) +
  Sample(id = "Control", outcome.par = parameters(rate = log(2)/12)) +
  Sample(id = "Treatment", outcome.par = parameters(rate = log(2)/18))
```

### PFS/OS Correlated Endpoints

```r
# Correlated survival endpoints
DataModel() +
  OutcomeDist(outcome.dist = "MVExpoPFSOSDist",
              outcome.type = c("event", "event")) +
  Event(n.events = 350, rando.ratio = c(1, 1)) +
  Sample(id = list("Control PFS", "Control OS"),
         outcome.par = parameters(
           parameters(
             par = parameters(
               parameters(rate = log(2)/6),   # PFS
               parameters(rate = log(2)/15)   # OS
             ),
             corr = matrix(c(1, 0.3, 0.3, 1), 2, 2)
           ))) +
  Sample(id = list("Treatment PFS", "Treatment OS"),
         outcome.par = parameters(
           parameters(
             par = parameters(
               parameters(rate = log(2)/9),
               parameters(rate = log(2)/20)
             ),
             corr = matrix(c(1, 0.3, 0.3, 1), 2, 2)
           )))
```

## Adaptive Designs

### Sample Size Re-Estimation

Concept: Adjust sample size at interim based on observed effect size.

```r
# Simulation framework for adaptive design
# 1. Generate interim data
# 2. Estimate effect size
# 3. Re-calculate sample size
# 4. Complete enrollment
# 5. Perform final analysis

simulate_adaptive <- function(initial_n, interim_frac, target_power) {
  # Stage 1: Interim
  n_interim <- round(initial_n * interim_frac)
  interim_data <- generate_data(n_interim)
  effect_estimate <- estimate_effect(interim_data)

  # Re-estimate sample size
  new_n <- calculate_sample_size(effect_estimate, target_power)
  new_n <- max(new_n, initial_n)  # Cannot decrease

  # Stage 2: Continue to new_n
  final_data <- generate_data(new_n)

  return(final_data)
}
```

### Response-Adaptive Randomization

Concept: Adjust randomization ratio based on interim results.

**Note:** More common in Bayesian settings; simtrial/Mediana focus on fixed designs.

## Design Selection Flowchart

```
START
  │
  ├─ How many treatment arms?
  │   ├─ 2 → Two-arm parallel
  │   └─ 3+ → Multi-arm design
  │
  ├─ How many primary endpoints?
  │   ├─ 1 → Single primary
  │   ├─ 2 (both required) → Co-primary
  │   └─ 2+ (any success) → Multiple primary with multiplicity
  │
  ├─ Are there secondary endpoints?
  │   ├─ Yes, hierarchical → Fixed-sequence or gatekeeping
  │   └─ Yes, equal priority → Holm/Hochberg
  │
  ├─ Is stratification needed?
  │   ├─ Yes → Stratified randomization
  │   └─ No → Simple randomization
  │
  ├─ Endpoint type?
  │   ├─ Continuous → Normal-based tests
  │   ├─ Binary → Proportion tests
  │   ├─ Time-to-event → Logrank/survival methods
  │   └─ Count → Poisson/NegBinom tests
  │
  └─ Interim analyses needed?
      ├─ Yes → Group sequential design
      └─ No → Fixed design
END
```

## Best Practices

1. **Match Design to Objectives**: Choose design that directly addresses primary question
2. **Consider Multiplicity Early**: Plan adjustment strategy during design phase
3. **Stratify When Important**: Use stratification for known prognostic factors
4. **Pre-specify Everything**: Document design choices before data collection
5. **Simulate Extensively**: Validate operating characteristics via simulation
6. **Consider Regulatory Path**: Align design with agency expectations
