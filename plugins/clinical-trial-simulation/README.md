# Clinical Trial Simulation Plugin

> **Clinical Trial Design & Simulation Ecosystem** — Power analysis, sample size determination, group sequential designs, and multiplicity optimization with AI assistance

A comprehensive [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) plugin providing **7 specialized agents**, **7 knowledge skills**, and **5 workflow commands** for clinical trial simulations using R.

## Overview

This plugin supports two major R frameworks for clinical trial simulation:

- **simtrial** — Time-to-event/survival simulations with piecewise exponential distributions, weighted logrank tests, and MaxCombo
- **Mediana** — Clinical Scenario Evaluation (CSE) for multi-scenario power analysis with automated Word reports

### Key Features

- **Power Analysis** — Calculate statistical power across treatment effect scenarios
- **Sample Size Determination** — Find minimum sample sizes meeting target power via binary/grid search
- **Group Sequential Designs** — Interim analyses with alpha spending and futility stopping
- **Multiplicity Optimization** — Select and tune procedures (Holm, Hochberg, Chain, Gatekeeping)
- **CSE Workflows** — Complete Clinical Scenario Evaluation with DataModel, AnalysisModel, EvaluationModel

## Quick Start

### Step 1: Add the Marketplace

Add this plugin marketplace to Claude Code:

```bash
/plugin marketplace add choxos/ClinicalTrialAgent
```

### Step 2: Install the Plugin

```bash
/plugin install clinical-trial-simulation
```

### Step 3: Install R Dependencies

```r
# Core packages
install.packages(c("simtrial", "Mediana", "gsDesign2"))

# Supporting packages
install.packages(c("survival", "dplyr", "data.table", "mvtnorm"))
```

## Usage

### Power Analysis for Time-to-Event Endpoint

Use the `/power-analysis` command or describe your needs:

```
Calculate power for a two-arm survival trial:
- Hazard ratio: 0.7
- Target events: 300
- Alpha: 0.025 (one-sided)
- Enrollment: 24 months uniform
- Median survival control: 12 months
```

The agent generates complete simtrial code:

```r
library(simtrial)

# Define failure rates (piecewise exponential)
fail_rate <- tibble(
  stratum = "All",
  duration = c(Inf),
  fail_rate = log(2) / 12,  # Control median = 12 months
  hr = c(0.7),
  dropout_rate = 0.001
)

# Define enrollment
enroll_rate <- tibble(
  stratum = "All",
  duration = 24,
  rate = 300 / 24  # ~12.5 per month
)

# Run simulations
results <- sim_fixed_n(
  n_sim = 10000,
  sample_size = 450,
  target_event = 300,
  enroll_rate = enroll_rate,
  fail_rate = fail_rate,
  total_duration = 36,
  analysis_method = wlr(weight = fh(rho = 0, gamma = 0))
)

# Power estimate
mean(results$z <= -qnorm(0.975))
```

### Sample Size Determination

Use the `/sample-size` command:

```
What sample size do I need for:
- 90% power
- Treatment difference: 5 units (continuous endpoint)
- Standard deviation: 15
- Alpha: 0.025 (one-sided)
- Two-arm parallel design (1:1 randomization)
```

The agent performs binary search using CSE:

```r
library(Mediana)

# Binary search for minimum N
target_power <- 0.90
n_range <- seq(100, 500, by = 20)

data.model <- DataModel() +
  OutcomeDist(outcome.dist = "NormalDist") +
  SampleSize(n_range) +
  Sample(id = "Control",
         outcome.par = parameters(mean = 0, sd = 15)) +
  Sample(id = "Treatment",
         outcome.par = parameters(mean = 5, sd = 15))

analysis.model <- AnalysisModel() +
  Test(id = "Primary",
       samples = samples("Control", "Treatment"),
       method = "TTest")

evaluation.model <- EvaluationModel() +
  Criterion(id = "Power", method = "MarginalPower",
            tests = tests("Primary"),
            par = parameters(alpha = 0.025))

results <- CSE(data.model, analysis.model, evaluation.model,
               SimParameters(n.sims = 10000, proc.load = "full", seed = 42))
```

### Group Sequential Design

Use the `/gs-design` command:

```
Design a 3-look group sequential trial:
- O'Brien-Fleming alpha spending
- Non-binding futility
- Information fractions: 0.5, 0.75, 1.0
- Overall alpha: 0.025
```

```r
library(simtrial)
library(gsDesign2)

# Create cutting functions for each analysis
cut_ia1 <- create_cut(planned_calendar_time = 18)  # IA1
cut_ia2 <- create_cut(planned_calendar_time = 24)  # IA2
cut_fa <- create_cut(planned_calendar_time = 36)   # Final

# Run group sequential simulation
results <- sim_gs_n(

  n_sim = 10000,
  sample_size = 450,
  enroll_rate = enroll_rate,
  fail_rate = fail_rate,
  test = wlr(weight = fh(rho = 0, gamma = 0)),
  cut = list(cut_ia1, cut_ia2, cut_fa),
  seed = 12345
)
```

### Multiplicity Optimization

Use the `/multiplicity-optimization` command:

```
I have a trial with:
- 2 doses (low, high) vs placebo
- Primary endpoint: PFS
- Secondary endpoint: OS
Help me select a gatekeeping procedure
```

```r
library(Mediana)

# Parallel gatekeeping for dose-endpoint hierarchy
analysis.model <- AnalysisModel() +
  Test(id = "PFS-Low", ...) +
  Test(id = "PFS-High", ...) +
  Test(id = "OS-Low", ...) +
  Test(id = "OS-High", ...) +
  MultAdjProc(proc = "ParallelGatekeepingAdj",
              par = parameters(family = families(
                family("PFS-Low", "PFS-High"),   # Primary family
                family("OS-Low", "OS-High")      # Secondary family
              ), proc = "HolmAdj", gamma = 1))
```

### Full CSE Analysis

Use the `/cse-analysis` command:

```
Run a complete CSE for:
- Sample sizes: 80, 100, 120 per arm
- Scenarios: Conservative (delta=3), Expected (delta=5), Optimistic (delta=7)
- SD = 15, alpha = 0.025
- Generate Word report
```

```r
library(Mediana)

# Data Model with multiple scenarios
data.model <- DataModel() +
  OutcomeDist(outcome.dist = "NormalDist") +
  SampleSize(c(80, 100, 120)) +
  Sample(id = "Control", outcome.par = parameters(mean = 0, sd = 15)) +
  Sample(id = "Treatment-Conservative", outcome.par = parameters(mean = 3, sd = 15)) +
  Sample(id = "Treatment-Expected", outcome.par = parameters(mean = 5, sd = 15)) +
  Sample(id = "Treatment-Optimistic", outcome.par = parameters(mean = 7, sd = 15))

# Analysis Model
analysis.model <- AnalysisModel() +
  Test(id = "Conservative", samples = samples("Control", "Treatment-Conservative"), method = "TTest") +
  Test(id = "Expected", samples = samples("Control", "Treatment-Expected"), method = "TTest") +
  Test(id = "Optimistic", samples = samples("Control", "Treatment-Optimistic"), method = "TTest")

# Evaluation Model
evaluation.model <- EvaluationModel() +
  Criterion(id = "Power-Conservative", method = "MarginalPower",
            tests = tests("Conservative"), par = parameters(alpha = 0.025)) +
  Criterion(id = "Power-Expected", method = "MarginalPower",
            tests = tests("Expected"), par = parameters(alpha = 0.025)) +
  Criterion(id = "Power-Optimistic", method = "MarginalPower",
            tests = tests("Optimistic"), par = parameters(alpha = 0.025))

# Run CSE
results <- CSE(data.model, analysis.model, evaluation.model,
               SimParameters(n.sims = 10000, proc.load = "full", seed = 42))

# Generate Word report
GenerateReport(results, "cse_report.docx")
```

## Components

### Agents (7)

| Agent | Model | Purpose |
|-------|-------|---------|
| `simulation-architect` | Haiku | Routes requests to appropriate specialists |
| `tte-specialist` | Sonnet | Time-to-event simulations with simtrial |
| `cse-specialist` | Sonnet | Clinical Scenario Evaluation with Mediana |
| `multiplicity-expert` | Sonnet | Multiple testing procedures and optimization |
| `gs-design-specialist` | Sonnet | Group sequential trial designs |
| `power-optimizer` | Opus | Sample size/power optimization algorithms |
| `code-reviewer` | Sonnet | R code validation and best practices |

### Skills (7)

- **Framework Skills**: `simtrial-fundamentals`, `mediana-fundamentals`
- **Method Skills**: `multiplicity-methods`, `time-to-event-methods`, `group-sequential-methods`
- **Design Skills**: `power-optimization-patterns`, `clinical-trial-design-patterns`

### Commands (5)

| Command | Description |
|---------|-------------|
| `/power-analysis` | Calculate power across scenarios |
| `/sample-size` | Find minimum sample size for target power |
| `/gs-design` | Design group sequential trials |
| `/multiplicity-optimization` | Select and optimize testing procedures |
| `/cse-analysis` | Full Clinical Scenario Evaluation workflow |

## Supported Analysis Types

| Analysis Type | simtrial | Mediana |
|--------------|:--------:|:-------:|
| Fixed design power | ✓ | ✓ |
| Sample size search | ✓ | ✓ |
| Group sequential | ✓ | - |
| Weighted logrank (FH) | ✓ | - |
| MaxCombo test | ✓ | - |
| RMST analysis | ✓ | - |
| Multi-scenario CSE | - | ✓ |
| Multiplicity adjustment | - | ✓ |
| Word report generation | - | ✓ |

## Repository Structure

```
ClinicalTrialAgent/
├── .claude-plugin/
│   └── marketplace.json              # Plugin configuration
├── plugins/clinical-trial-simulation/
│   ├── agents/                       # 7 specialized agents
│   │   ├── simulation-architect.md   # Entry point router
│   │   ├── tte-specialist.md         # Time-to-event expert
│   │   ├── cse-specialist.md         # CSE framework expert
│   │   ├── multiplicity-expert.md    # Multiple testing expert
│   │   ├── gs-design-specialist.md   # Group sequential expert
│   │   ├── power-optimizer.md        # Optimization specialist
│   │   └── code-reviewer.md          # Code validation
│   ├── commands/                     # 5 workflow commands
│   │   ├── power-analysis.md
│   │   ├── sample-size.md
│   │   ├── gs-design.md
│   │   ├── multiplicity-optimization.md
│   │   └── cse-analysis.md
│   └── skills/                       # 7 knowledge skills
│       ├── simtrial-fundamentals/
│       ├── mediana-fundamentals/
│       ├── multiplicity-methods/
│       ├── time-to-event-methods/
│       ├── group-sequential-methods/
│       ├── power-optimization-patterns/
│       └── clinical-trial-design-patterns/
├── refs/                             # Reference materials
├── README.md
└── LICENSE
```

## Critical: Framework Selection

**Choose the right framework for your analysis:**

| Use Case | Recommended Framework |
|----------|----------------------|
| Time-to-event endpoint | simtrial |
| Non-proportional hazards | simtrial (MaxCombo, weighted LR) |
| Group sequential design | simtrial + gsDesign2 |
| Multi-scenario evaluation | Mediana (CSE) |
| Multiple endpoints/doses | Mediana (multiplicity) |
| Automated reporting | Mediana (Word reports) |
| Continuous/binary endpoints | Mediana (CSE) |

The `simulation-architect` agent automatically routes to the appropriate specialist based on your request.

## References

- Benda N, Branson M, Maurer W, Friede T (2010). "Aspects of modernizing drug development using clinical scenario planning and evaluation." *Drug Information Journal*, 44(3), 299-315.
- Anderson KM, et al. (2022). "simtrial: Clinical Trial Simulation." R package.
- Dmitrienko A, D'Agostino RB Sr (2013). "Tutorial in Biostatistics: Traditional multiplicity adjustment methods in clinical trials." *Statistics in Medicine*.
- Dmitrienko A, D'Agostino RB (2018). *Clinical Trial Optimization Using R*. Chapman & Hall/CRC.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Merck & Co.](https://github.com/Merck/simtrial) for the simtrial package
- [Mediana Inc.](https://github.com/medianasoft/Mediana) for the Mediana package
- [Anthropic](https://www.anthropic.com/) for Claude Code
