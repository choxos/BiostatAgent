# BiostatAgent

> **Comprehensive Biostatistics Agent Ecosystem** — 30 specialized agents, 17 workflow commands, and 34 methodology skills for R-based statistical analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A unified [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) plugin marketplace consolidating four specialized biostatistics plugins:

| Plugin | Focus | Agents | Commands | Skills |
|--------|-------|--------|----------|--------|
| **bayesian-modeling** | Bayesian inference (Stan, PyMC, JAGS) | 6 | 3 | 9 |
| **itc-modelling** | Indirect treatment comparisons | 7 | 2 | 6 |
| **r-tidy-modelling** | Tidy R workflows & biostatistics | 10 | 7 | 12 |
| **clinical-trial-simulation** | Clinical trial simulation | 7 | 5 | 7 |
| **Total** | | **30** | **17** | **34** |

## Quick Start

### 1. Add the Marketplace

```bash
/plugin marketplace add choxos/BiostatAgent
```

### 2. Install Plugins

Install all plugins or select specific ones:

```bash
# Install all
/plugin install bayesian-modeling itc-modelling r-tidy-modelling clinical-trial-simulation

# Or install individually
/plugin install bayesian-modeling
/plugin install itc-modelling
/plugin install r-tidy-modelling
/plugin install clinical-trial-simulation
```

### 3. Install R Dependencies

```r
# Core dependencies (install as needed)
install.packages(c(
  # Bayesian modeling
  "cmdstanr", "rstan", "R2jags", "R2WinBUGS", "bayesplot", "loo",
  # ITC/NMA
  "meta", "netmeta", "gemtc", "multinma", "maicplus",
  # Tidy modeling
  "tidyverse", "tidymodels", "recipes", "parsnip", "workflows",
  # Clinical trials
  "simtrial", "Mediana", "gsDesign2", "survival"
))
```

---

## Plugins Overview

### 1. Bayesian Modeling (`bayesian-modeling`)

Create, review, and validate Bayesian models across four languages:

- **Stan 2.37** — Modern HMC/NUTS sampling with cmdstanr
- **PyMC 5** — Python-native Bayesian modeling with ArviZ
- **JAGS** — Cross-platform Gibbs sampling with R2jags
- **WinBUGS** — Classic BUGS implementation with R2WinBUGS

**Commands:**
| Command | Description |
|---------|-------------|
| `/create-model` | Interactive model creation workflow |
| `/review-model` | Review existing models for correctness |
| `/run-diagnostics` | Test model execution with synthetic data |

**Agents:** model-architect, stan-specialist, pymc-specialist, bugs-specialist, model-reviewer, test-runner

---

### 2. ITC Modelling (`itc-modelling`)

Expert agents for indirect treatment comparison following NICE DSU guidance:

- **Pairwise Meta-Analysis** — Fixed/random effects with meta, metafor, bayesmeta
- **Network Meta-Analysis** — Frequentist (netmeta) and Bayesian (gemtc)
- **MAIC** — Matching-adjusted indirect comparison with maicplus
- **STC** — Simulated treatment comparison
- **ML-NMR** — Multilevel network meta-regression with multinma

**Commands:**
| Command | Description |
|---------|-------------|
| `/itc-analysis` | Full ITC workflow from method selection to results |
| `/itc-review` | Review existing ITC code for methodological issues |

**Agents:** itc-architect, pairwise-meta-analyst, nma-specialist, maic-specialist, stc-specialist, ml-nmr-specialist, itc-code-reviewer

---

### 3. R Tidy Modelling (`r-tidy-modelling`)

Comprehensive R data science following tidyverse and tidymodels best practices:

- **Data Wrangling** — dplyr, tidyr, data transformation
- **Feature Engineering** — recipes, preprocessing, transformations
- **Model Building** — parsnip, workflows, tidymodels
- **Visualization** — ggplot2, publication-ready figures
- **Reporting** — Quarto, R Markdown, reproducible reports
- **Biostatistics** — Clinical trials, survival analysis, epidemiology

**Commands:**
| Command | Description |
|---------|-------------|
| `/r-analysis` | End-to-end analysis workflow |
| `/r-code-review` | Review R code for best practices |
| `/r-model-comparison` | Compare multiple models |
| `/r-clinical-analysis` | Clinical trial analysis workflow |
| `/r-project-setup` | Set up reproducible R project |
| `/r-doc-generate` | Generate documentation |
| `/r-tutorial-create` | Create tutorials from code |

**Agents:** r-data-architect, tidymodels-engineer, feature-engineer, biostatistician, data-wrangler, viz-specialist, reporting-engineer, r-code-reviewer, r-docs-architect, r-tutorial-engineer

---

### 4. Clinical Trial Simulation (`clinical-trial-simulation`)

Design and simulate clinical trials using simtrial and Mediana:

- **simtrial** — Time-to-event simulations, weighted logrank, MaxCombo
- **Mediana** — Clinical Scenario Evaluation, multiplicity, Word reports
- **gsDesign2** — Group sequential designs, alpha spending

**Commands:**
| Command | Description |
|---------|-------------|
| `/power-analysis` | Calculate power across scenarios |
| `/sample-size` | Find minimum sample size for target power |
| `/gs-design` | Design group sequential trials |
| `/multiplicity-optimization` | Optimize multiple testing procedures |
| `/cse-analysis` | Full Clinical Scenario Evaluation |

**Agents:** simulation-architect, tte-specialist, cse-specialist, multiplicity-expert, gs-design-specialist, power-optimizer, code-reviewer

---

## Repository Structure

```
BiostatAgent/
├── .claude-plugin/
│   └── marketplace.json              # Unified plugin manifest
├── plugins/
│   ├── bayesian-modeling/
│   │   ├── agents/                   # 6 agents
│   │   ├── commands/                 # 3 commands
│   │   └── skills/                   # 9 skills
│   ├── itc-modelling/
│   │   ├── agents/                   # 7 agents
│   │   ├── commands/                 # 2 commands
│   │   └── skills/                   # 6 skills
│   ├── r-tidy-modelling/
│   │   ├── agents/                   # 10 agents
│   │   ├── commands/                 # 7 commands
│   │   └── skills/                   # 12 skills
│   └── clinical-trial-simulation/
│       ├── agents/                   # 7 agents
│       ├── commands/                 # 5 commands
│       └── skills/                   # 7 skills
├── README.md
└── LICENSE
```

---

## Usage Examples

### Bayesian Modeling

```
Create a hierarchical model for patient outcomes nested within hospitals.
Use Stan with cmdstanr.
```

### ITC Analysis

```
I have IPD for trial A and AgD for trial B.
Help me run a MAIC to compare treatments.
```

### Tidy R Analysis

```
Build a predictive model for patient readmission using tidymodels.
Include cross-validation and hyperparameter tuning.
```

### Clinical Trial Simulation

```
Calculate power for a survival trial with HR=0.7, 300 events, alpha=0.025.
Use weighted logrank for non-proportional hazards.
```

---

## All Components

### Agents (30 total)

| Plugin | Agents |
|--------|--------|
| bayesian-modeling | model-architect, stan-specialist, pymc-specialist, bugs-specialist, model-reviewer, test-runner |
| itc-modelling | itc-architect, pairwise-meta-analyst, nma-specialist, maic-specialist, stc-specialist, ml-nmr-specialist, itc-code-reviewer |
| r-tidy-modelling | r-data-architect, tidymodels-engineer, feature-engineer, biostatistician, data-wrangler, viz-specialist, reporting-engineer, r-code-reviewer, r-docs-architect, r-tutorial-engineer |
| clinical-trial-simulation | simulation-architect, tte-specialist, cse-specialist, multiplicity-expert, gs-design-specialist, power-optimizer, code-reviewer |

### Commands (17 total)

| Plugin | Commands |
|--------|----------|
| bayesian-modeling | `/create-model`, `/review-model`, `/run-diagnostics` |
| itc-modelling | `/itc-analysis`, `/itc-review` |
| r-tidy-modelling | `/r-analysis`, `/r-code-review`, `/r-model-comparison`, `/r-clinical-analysis`, `/r-project-setup`, `/r-doc-generate`, `/r-tutorial-create` |
| clinical-trial-simulation | `/power-analysis`, `/sample-size`, `/gs-design`, `/multiplicity-optimization`, `/cse-analysis` |

### Skills (34 total)

| Plugin | Skills |
|--------|--------|
| bayesian-modeling | stan-fundamentals, pymc-fundamentals, bugs-fundamentals, hierarchical-models, regression-models, time-series-models, survival-models, meta-analysis, model-diagnostics |
| itc-modelling | tidy-itc-workflow, pairwise-ma-methodology, nma-methodology, maic-methodology, stc-methodology, ml-nmr-methodology |
| r-tidy-modelling | tidymodels-workflow, recipes-patterns, resampling-strategies, model-tuning, model-evaluation, survival-analysis, clinical-trials, bayesian-modeling, epidemiology-methods, genomics-analysis, r-documentation-patterns, roxygen2-pkgdown |
| clinical-trial-simulation | simtrial-fundamentals, mediana-fundamentals, multiplicity-methods, time-to-event-methods, group-sequential-methods, power-optimization-patterns, clinical-trial-design-patterns |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Stan Development Team](https://mc-stan.org/) for Stan
- [PyMC Developers](https://www.pymc.io/) for PyMC
- [Merck & Co.](https://github.com/Merck/simtrial) for simtrial
- [Mediana Inc.](https://github.com/medianasoft/Mediana) for Mediana
- [tidymodels team](https://www.tidymodels.org/) for tidymodels
- [Anthropic](https://www.anthropic.com/) for Claude Code
