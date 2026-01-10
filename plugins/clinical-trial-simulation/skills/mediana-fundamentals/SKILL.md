---
name: mediana-fundamentals
description: Core Mediana package functions for Clinical Scenario Evaluation (CSE). Use when designing data models, analysis models, evaluation models, and running comprehensive trial simulations.
---

# Mediana Fundamentals

## When to Use This Skill

- Building Clinical Scenario Evaluation (CSE) frameworks
- Defining data models with various endpoint distributions
- Configuring analysis models with statistical tests
- Setting up multiplicity adjustment procedures
- Defining evaluation criteria (power metrics)
- Running comprehensive trial simulations
- Generating Word-based simulation reports

## Package Overview

**Mediana** (v1.0.9) by Gautier Paux and Alex Dmitrienko provides a general framework for clinical trial simulations based on the Clinical Scenario Evaluation approach (Benda et al., 2010).

### CSE Framework Components

1. **Data Models** - Define data generation process
2. **Analysis Models** - Define statistical methods
3. **Evaluation Models** - Define success criteria

## Data Model

### Initialization

```r
data.model <- DataModel()
```

### OutcomeDist - Outcome Distribution

Specifies the distribution of patient outcomes.

```r
OutcomeDist(
  outcome.dist = "NormalDist",   # Distribution type
  outcome.type = "standard"       # "standard" or "event"
)
```

**Supported Distributions:**

| Distribution | Parameters | Use Case |
|--------------|------------|----------|
| `UniformDist` | `max` | Uniform outcomes |
| `NormalDist` | `mean`, `sd` | Continuous endpoints |
| `BinomDist` | `prop` | Binary endpoints |
| `BetaDist` | `a`, `b` | Proportions |
| `ExpoDist` | `rate` | Time-to-event |
| `WeibullDist` | `shape`, `scale` | Survival with shape |
| `TruncatedExpoDist` | `rate`, `trunc` | Truncated survival |
| `PoissonDist` | `lambda` | Count data |
| `NegBinomDist` | `dispersion`, `mean` | Overdispersed counts |
| `MultinomialDist` | `prob` | Categorical outcomes |

**Multivariate Distributions:**

| Distribution | Parameters | Use Case |
|--------------|------------|----------|
| `MVNormalDist` | `par`, `corr` | Correlated continuous |
| `MVBinomDist` | `par`, `corr` | Correlated binary |
| `MVExpoDist` | `par`, `corr` | Correlated survival |
| `MVExpoPFSOSDist` | `par`, `corr` | PFS/OS endpoints |
| `MVMixedDist` | `type`, `par`, `corr` | Mixed endpoint types |

### Sample - Treatment Arm Definition

```r
# Normal distribution parameters
outcome.placebo <- parameters(mean = 0, sd = 70)
outcome.treatment <- parameters(mean = 40, sd = 70)

# Define samples
Sample(id = "Placebo",
       outcome.par = parameters(outcome.placebo))

Sample(id = "Treatment",
       outcome.par = parameters(outcome.treatment))
```

**Multiple Scenarios:**
```r
# Define multiple effect size scenarios
outcome1.placebo <- parameters(mean = 0, sd = 70)
outcome1.treatment <- parameters(mean = 40, sd = 70)  # Conservative

outcome2.placebo <- parameters(mean = 0, sd = 70)
outcome2.treatment <- parameters(mean = 50, sd = 70)  # Optimistic

Sample(id = "Placebo",
       outcome.par = parameters(outcome1.placebo, outcome2.placebo))

Sample(id = "Treatment",
       outcome.par = parameters(outcome1.treatment, outcome2.treatment))
```

### SampleSize - Balanced Design

```r
SampleSize(c(50, 55, 60, 65, 70))  # Per arm
SampleSize(seq(50, 100, 10))
```

### Event - Event-Driven Design

```r
Event(
  n.events = c(390, 420),      # Total event counts to evaluate
  rando.ratio = c(1, 2)        # Control:Treatment ratio
)
```

### Design - Enrollment and Dropout

```r
# Non-uniform enrollment with beta distribution
# 50% enrolled at 75% of enrollment period
enroll.par <- parameters(
  a = log(0.5)/log(0.75),
  b = 1
)

Design(
  enroll.period = 12,              # Enrollment duration (months)
  study.duration = 36,             # Total study duration
  enroll.dist = "BetaDist",        # Or "UniformDist"
  enroll.dist.par = enroll.par,
  dropout.dist = "ExpoDist",
  dropout.dist.par = parameters(rate = 0.0115)
)
```

### Complete Data Model Example

```r
# Time-to-event trial with PFS and OS
median.pfs.placebo <- 6
median.pfs.treatment <- 9
median.os.placebo <- 15
median.os.treatment <- 19

placebo.par <- parameters(
  parameters(rate = log(2)/median.pfs.placebo),
  parameters(rate = log(2)/median.os.placebo)
)

treatment.par <- parameters(
  parameters(rate = log(2)/median.pfs.treatment),
  parameters(rate = log(2)/median.os.treatment)
)

corr.matrix <- matrix(c(1.0, 0.3, 0.3, 1.0), 2, 2)

data.model <- DataModel() +
  OutcomeDist(outcome.dist = "MVExpoPFSOSDist",
              outcome.type = c("event", "event")) +
  Event(n.events = c(390, 420), rando.ratio = c(1, 2)) +
  Design(enroll.period = 12, study.duration = 30,
         enroll.dist = "BetaDist",
         enroll.dist.par = parameters(a = log(0.5)/log(0.75), b = 1),
         dropout.dist = "ExpoDist",
         dropout.dist.par = parameters(rate = 0.0115)) +
  Sample(id = list("Placebo PFS", "Placebo OS"),
         outcome.par = parameters(parameters(par = placebo.par,
                                             corr = corr.matrix))) +
  Sample(id = list("Treatment PFS", "Treatment OS"),
         outcome.par = parameters(parameters(par = treatment.par,
                                             corr = corr.matrix)))
```

## Analysis Model

### Initialization

```r
analysis.model <- AnalysisModel()
```

### Test - Statistical Tests

```r
Test(
  id = "Primary",                           # Unique test ID
  samples = samples("Placebo", "Treatment"), # Samples to compare
  method = "TTest",                          # Test method
  par = parameters(...)                      # Optional parameters
)
```

**Built-in Tests:**

| Method | Description | Parameters |
|--------|-------------|------------|
| `TTest` | Two-sample t-test | `larger` (optional) |
| `TTestNI` | Non-inferiority t-test | `margin`, `larger` |
| `WilcoxTest` | Wilcoxon-Mann-Whitney | `larger` |
| `PropTest` | Two-sample proportion | `yates`, `larger` |
| `PropTestNI` | NI proportion test | `margin`, `yates`, `larger` |
| `FisherTest` | Fisher exact test | `larger` |
| `GLMPoissonTest` | Poisson regression | `larger` |
| `GLMNegBinomTest` | Negative binomial | `larger` |
| `LogrankTest` | Log-rank test | `larger` |
| `OrdinalLogisticRegTest` | Ordinal logistic | `larger` |

**Note:** Tests are one-sided. By default, larger values expected in Sample 2. Set `larger = FALSE` if larger values expected in Sample 1.

### Statistic - Descriptive Statistics

```r
Statistic(
  id = "Mean Treatment",
  method = "MeanStat",
  samples = samples("Treatment")
)
```

**Built-in Statistics:**

| Method | Description | Samples Required |
|--------|-------------|------------------|
| `MeanStat` | Mean | 1 |
| `MedianStat` | Median | 1 |
| `SdStat` | Standard deviation | 1 |
| `MinStat` | Minimum | 1 |
| `MaxStat` | Maximum | 1 |
| `PropStat` | Proportion | 1 |
| `DiffMeanStat` | Difference in means | 2 |
| `DiffPropStat` | Difference in proportions | 2 |
| `EffectSizeContStat` | Effect size (continuous) | 2 |
| `EffectSizePropStat` | Effect size (binary) | 2 |
| `EffectSizeEventStat` | Effect size (survival) | 2 |
| `HazardRatioStat` | Hazard ratio | 2 |
| `EventCountStat` | Number of events | 1+ |
| `PatientCountStat` | Number of patients | 1+ |

### MultAdjProc - Multiplicity Adjustment

```r
MultAdjProc(
  proc = "HolmAdj",
  par = parameters(weight = c(0.5, 0.5)),
  tests = tests("Test1", "Test2")  # Optional: applies to all if omitted
)
```

**Built-in Procedures:**

| Procedure | Type | Parameters |
|-----------|------|------------|
| `BonferroniAdj` | Single-step | `weight` |
| `HolmAdj` | Step-down | `weight` |
| `HochbergAdj` | Step-up | `weight` |
| `HommelAdj` | Step-up | `weight` |
| `FixedSeqAdj` | Sequential | (order from tests) |
| `ChainAdj` | Graphical | `weight`, `transition` |
| `FallbackAdj` | Fallback | `weight` |
| `NormalParamAdj` | Parametric | `corr`, `weight` |
| `ParallelGatekeepingAdj` | Gatekeeping | `family`, `proc`, `gamma` |
| `MultipleSequenceGatekeepingAdj` | Gatekeeping | `family`, `proc`, `gamma` |
| `MixtureGatekeepingAdj` | Gatekeeping | `family`, `proc`, `gamma`, `serial`, `parallel` |

### Multiplicity Examples

**Chain Procedure:**
```r
MultAdjProc(
  proc = "ChainAdj",
  par = parameters(
    weight = c(0.5, 0.5),
    transition = matrix(c(0, 1,
                          1, 0), 2, 2, byrow = TRUE)
  )
)
```

**Parallel Gatekeeping:**
```r
MultAdjProc(
  proc = "ParallelGatekeepingAdj",
  par = parameters(
    family = families(
      family1 = c(1, 2),    # Primary endpoints
      family2 = c(3, 4)     # Secondary endpoints
    ),
    proc = families(
      family1 = "HolmAdj",
      family2 = "HolmAdj"
    ),
    gamma = families(
      family1 = 0.8,        # Truncation parameter
      family2 = 1
    )
  ),
  tests = tests("Primary1", "Primary2", "Secondary1", "Secondary2")
)
```

**Multiple-Sequence Gatekeeping:**
```r
MultAdjProc(
  proc = "MultipleSequenceGatekeepingAdj",
  par = parameters(
    family = families(family1 = c(1, 2), family2 = c(3, 4)),
    proc = families(family1 = "HolmAdj", family2 = "HochbergAdj"),
    gamma = families(family1 = 0.8, family2 = 1)
  )
)
```

### Complete Analysis Model Example

```r
analysis.model <- AnalysisModel() +
  # Primary tests
  Test(id = "PFS test",
       samples = samples("Placebo PFS", "Treatment PFS"),
       method = "LogrankTest") +
  Test(id = "OS test",
       samples = samples("Placebo OS", "Treatment OS"),
       method = "LogrankTest") +

  # Fixed-sequence multiplicity adjustment
  MultAdjProc(proc = "FixedSeqAdj") +

  # Descriptive statistics
  Statistic(id = "Patients Placebo",
            samples = samples("Placebo PFS"),
            method = "PatientCountStat") +
  Statistic(id = "Patients Treatment",
            samples = samples("Treatment PFS"),
            method = "PatientCountStat")
```

## Evaluation Model

### Initialization

```r
evaluation.model <- EvaluationModel()
```

### Criterion - Success Metrics

```r
Criterion(
  id = "Marginal power",
  method = "MarginalPower",
  tests = tests("Primary"),
  labels = c("Primary Power"),
  par = parameters(alpha = 0.025)
)
```

**Built-in Criteria:**

| Method | Description | Parameters |
|--------|-------------|------------|
| `MarginalPower` | Power for each test | `alpha` |
| `WeightedPower` | Weighted combination | `alpha`, `weight` |
| `DisjunctivePower` | P(reject at least one) | `alpha` |
| `ConjunctivePower` | P(reject all) | `alpha` |
| `ExpectedRejPower` | Expected # rejected | `alpha` |
| `MeanSumm` | Mean of statistics | - |
| `MedianSumm` | Median of statistics | - |

### Complete Evaluation Model Example

```r
evaluation.model <- EvaluationModel() +
  Criterion(id = "Marginal power",
            method = "MarginalPower",
            tests = tests("PFS test", "OS test"),
            labels = c("PFS Power", "OS Power"),
            par = parameters(alpha = 0.025)) +

  Criterion(id = "Disjunctive power",
            method = "DisjunctivePower",
            tests = tests("PFS test", "OS test"),
            labels = c("At least one significant"),
            par = parameters(alpha = 0.025)) +

  Criterion(id = "Average patients",
            method = "MeanSumm",
            statistics = statistics("Patients Placebo", "Patients Treatment"),
            labels = c("Mean Placebo N", "Mean Treatment N"))
```

## Running Simulations

### SimParameters

```r
sim.parameters <- SimParameters(
  n.sims = 10000,        # Number of simulations
  proc.load = "full",    # Parallelization: "low", "med", "high", "full", or integer
  seed = 42938001        # For reproducibility
)
```

### CSE Function

```r
results <- CSE(
  data.model,
  analysis.model,
  evaluation.model,
  sim.parameters
)

# View summary
summary(results)
```

### Results Structure

The CSE function returns a list with:
- `simulation.results`: Data frame of results per scenario
- `analysis.scenario.grid`: Grid of data/analysis combinations
- `data.structure`: Data model structure
- `analysis.structure`: Analysis model structure
- `evaluation.structure`: Evaluation model structure
- `sim.parameters`: Simulation parameters
- `timestamp`: Start/end time and duration

## Report Generation

### PresentationModel

```r
presentation.model <- PresentationModel() +
  Project(username = "Analyst Name",
          title = "Phase III Trial Simulation",
          description = "Power analysis for multi-endpoint trial") +
  Section(by = "outcome.parameter") +
  Subsection(by = "sample.size") +
  Table(by = "multiplicity.adjustment") +
  CustomLabel(param = "sample.size",
              label = paste0("N = ", c(50, 60, 70))) +
  CustomLabel(param = "outcome.parameter",
              label = c("Conservative", "Expected", "Optimistic"))
```

### GenerateReport

```r
GenerateReport(
  presentation.model = presentation.model,
  cse.results = results,
  report.filename = "Simulation_Report.docx"
)
```

## Complete Example: Multi-Endpoint Trial

```r
library(Mediana)

# Data Model
outcome.placebo <- parameters(mean = 0, sd = 1)
outcome.trt.conservative <- parameters(mean = 0.3, sd = 1)
outcome.trt.expected <- parameters(mean = 0.5, sd = 1)

data.model <- DataModel() +
  OutcomeDist(outcome.dist = "NormalDist") +
  SampleSize(seq(80, 120, 10)) +
  Sample(id = "Placebo",
         outcome.par = parameters(outcome.placebo, outcome.placebo)) +
  Sample(id = "Treatment",
         outcome.par = parameters(outcome.trt.conservative, outcome.trt.expected))

# Analysis Model
analysis.model <- AnalysisModel() +
  Test(id = "Primary",
       samples = samples("Placebo", "Treatment"),
       method = "TTest") +
  Statistic(id = "Effect Size",
            samples = samples("Placebo", "Treatment"),
            method = "EffectSizeContStat")

# Evaluation Model
evaluation.model <- EvaluationModel() +
  Criterion(id = "Power",
            method = "MarginalPower",
            tests = tests("Primary"),
            labels = "Primary Power",
            par = parameters(alpha = 0.025)) +
  Criterion(id = "Mean Effect",
            method = "MeanSumm",
            statistics = statistics("Effect Size"),
            labels = "Mean Effect Size")

# Run Simulations
results <- CSE(
  data.model,
  analysis.model,
  evaluation.model,
  SimParameters(n.sims = 10000, proc.load = "full", seed = 12345)
)

# View Results
summary(results)

# Generate Report
presentation.model <- PresentationModel() +
  Project(title = "Sample Size Analysis") +
  Section(by = "outcome.parameter") +
  Table(by = "sample.size") +
  CustomLabel(param = "outcome.parameter",
              label = c("Conservative", "Expected"))

GenerateReport(presentation.model, results, "Analysis_Report.docx")
```

## Best Practices

1. **Multiple Scenarios**: Always evaluate multiple treatment effect assumptions
2. **Sample Size Range**: Test a range of sample sizes to build power curves
3. **Reproducibility**: Always set seed in SimParameters
4. **Parallelization**: Use `proc.load = "full"` for large simulations
5. **Report Labels**: Use CustomLabel for interpretable scenario names
6. **Validation**: Compare CSE results to analytical formulas where available
7. **Multiplicity**: Select appropriate procedures based on hypothesis structure
