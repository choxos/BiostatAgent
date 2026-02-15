---
layout: default
title: BiostatAgent
---

# BiostatAgent

**Comprehensive Biostatistics Agent Ecosystem** -- 30 specialized agents, 17 workflow commands, and 45 methodology skills for R-based statistical analysis.

A unified [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) plugin marketplace consolidating four specialized biostatistics plugins.

[View on GitHub](https://github.com/choxos/BiostatAgent){: .btn }

---

## At a Glance

| Plugin | Focus | Agents | Commands | Skills |
|:-------|:------|:------:|:--------:|:------:|
| **bayesian-modeling** | Bayesian inference (Stan, PyMC, JAGS) | 6 | 3 | 9 |
| **itc-modeling** | Indirect treatment comparisons | 7 | 2 | 6 |
| **r-tidy-modeling** | Tidy R workflows & biostatistics | 10 | 7 | 23 |
| **clinical-trial-simulation** | Clinical trial simulation | 7 | 5 | 7 |
| **Total** | | **30** | **17** | **45** |

---

## Quick Start

### 1. Add the Marketplace

```bash
/plugin marketplace add choxos/BiostatAgent
```

### 2. Install Plugins

```bash
# Install all
/plugin install bayesian-modeling itc-modeling r-tidy-modeling clinical-trial-simulation

# Or install individually
/plugin install bayesian-modeling
```

### 3. Install R Dependencies

```r
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

## Bayesian Modeling

Create, review, and validate Bayesian models across four languages:

- **Stan 2.37** -- Modern HMC/NUTS sampling with cmdstanr
- **PyMC 5** -- Python-native Bayesian modeling with ArviZ
- **JAGS** -- Cross-platform Gibbs sampling with R2jags
- **WinBUGS** -- Classic BUGS implementation with R2WinBUGS

### Commands

| Command | Description |
|:--------|:------------|
| `/create-model` | Interactive model creation workflow |
| `/review-model` | Review existing models for correctness |
| `/run-diagnostics` | Test model execution with synthetic data |

### Agents

model-architect, stan-specialist, pymc-specialist, bugs-specialist, model-reviewer, test-runner

### Skills

stan-fundamentals, pymc-fundamentals, bugs-fundamentals, hierarchical-models, regression-models, time-series-models, survival-models, meta-analysis, model-diagnostics

---

## ITC Modeling

Expert agents for indirect treatment comparison following NICE DSU guidance:

- **Pairwise Meta-Analysis** -- Fixed/random effects with meta, metafor, bayesmeta
- **Network Meta-Analysis** -- Frequentist (netmeta) and Bayesian (gemtc)
- **MAIC** -- Matching-adjusted indirect comparison with maicplus
- **STC** -- Simulated treatment comparison
- **ML-NMR** -- Multilevel network meta-regression with multinma

### Commands

| Command | Description |
|:--------|:------------|
| `/itc-analysis` | Full ITC workflow from method selection to results |
| `/itc-review` | Review existing ITC code for methodological issues |

### Agents

itc-architect, pairwise-meta-analyst, nma-specialist, maic-specialist, stc-specialist, ml-nmr-specialist, itc-code-reviewer

### Skills

tidy-itc-workflow, pairwise-ma-methodology, nma-methodology, maic-methodology, stc-methodology, ml-nmr-methodology

---

## R Tidy Modeling

Comprehensive R data science and biostatistics following tidyverse and tidymodels best practices:

- **Data Wrangling** -- dplyr, tidyr, data transformation
- **Feature Engineering** -- recipes, preprocessing, transformations
- **Model Building** -- parsnip, workflows, tidymodels
- **Visualization** -- ggplot2, publication-ready figures
- **Reporting** -- Quarto, R Markdown, reproducible reports
- **Biostatistics** -- Clinical trials, survival analysis, epidemiology, meta-analysis, genomics, pharmacokinetics, health economics

### Commands

| Command | Description |
|:--------|:------------|
| `/r-analysis` | End-to-end analysis workflow |
| `/r-code-review` | Review R code for best practices |
| `/r-model-comparison` | Compare multiple models |
| `/r-clinical-analysis` | Clinical trial analysis workflow |
| `/r-project-setup` | Set up reproducible R project |
| `/r-doc-generate` | Generate documentation |
| `/r-tutorial-create` | Create tutorials from code |

### Agents

r-data-architect, tidymodels-engineer, feature-engineer, biostatistician, data-wrangler, viz-specialist, reporting-engineer, r-code-reviewer, r-docs-architect, r-tutorial-engineer

### Skills (23)

| Category | Skills |
|:---------|:-------|
| Tidymodels | tidymodels-workflow, tidymodels-review-patterns, recipes-patterns, resampling-strategies, model-tuning, model-evaluation |
| Clinical & Epidemiology | clinical-trials, epidemiology-methods, advanced-adaptive-trials, real-world-evidence |
| Evidence Synthesis | meta-analysis, network-meta-analysis, ipd-meta-analysis |
| Specialized Methods | survival-analysis, bayesian-modeling, diagnostic-accuracy, causal-mediation, mendelian-randomization, pharmacokinetics, health-economics, genomics-analysis |
| Documentation | r-documentation-patterns, roxygen2-pkgdown |

---

## Clinical Trial Simulation

Design and simulate clinical trials using simtrial and Mediana:

- **simtrial** -- Time-to-event simulations, weighted logrank, MaxCombo
- **Mediana** -- Clinical Scenario Evaluation, multiplicity, Word reports
- **gsDesign2** -- Group sequential designs, alpha spending

### Commands

| Command | Description |
|:--------|:------------|
| `/power-analysis` | Calculate power across scenarios |
| `/sample-size` | Find minimum sample size for target power |
| `/gs-design` | Design group sequential trials |
| `/multiplicity-optimization` | Optimize multiple testing procedures |
| `/cse-analysis` | Full Clinical Scenario Evaluation |

### Agents

simulation-architect, tte-specialist, cse-specialist, multiplicity-expert, gs-design-specialist, power-optimizer, code-reviewer

### Skills

simtrial-fundamentals, mediana-fundamentals, multiplicity-methods, time-to-event-methods, group-sequential-methods, power-optimization-patterns, clinical-trial-design-patterns

---

## Usage Examples

**Bayesian Modeling:**
```
Create a hierarchical model for patient outcomes nested
within hospitals. Use Stan with cmdstanr.
```

**ITC Analysis:**
```
I have IPD for trial A and AgD for trial B.
Help me run a MAIC to compare treatments.
```

**Tidy R Analysis:**
```
Build a predictive model for patient readmission using
tidymodels. Include cross-validation and hyperparameter tuning.
```

**Clinical Trial Simulation:**
```
Calculate power for a survival trial with HR=0.7, 300 events,
alpha=0.025. Use weighted logrank for non-proportional hazards.
```

---

## All Components Summary

### Agents (30)

| Plugin | Agents |
|:-------|:-------|
| bayesian-modeling | model-architect, stan-specialist, pymc-specialist, bugs-specialist, model-reviewer, test-runner |
| itc-modeling | itc-architect, pairwise-meta-analyst, nma-specialist, maic-specialist, stc-specialist, ml-nmr-specialist, itc-code-reviewer |
| r-tidy-modeling | r-data-architect, tidymodels-engineer, feature-engineer, biostatistician, data-wrangler, viz-specialist, reporting-engineer, r-code-reviewer, r-docs-architect, r-tutorial-engineer |
| clinical-trial-simulation | simulation-architect, tte-specialist, cse-specialist, multiplicity-expert, gs-design-specialist, power-optimizer, code-reviewer |

### Commands (17)

| Plugin | Commands |
|:-------|:---------|
| bayesian-modeling | `/create-model`, `/review-model`, `/run-diagnostics` |
| itc-modeling | `/itc-analysis`, `/itc-review` |
| r-tidy-modeling | `/r-analysis`, `/r-code-review`, `/r-model-comparison`, `/r-clinical-analysis`, `/r-project-setup`, `/r-doc-generate`, `/r-tutorial-create` |
| clinical-trial-simulation | `/power-analysis`, `/sample-size`, `/gs-design`, `/multiplicity-optimization`, `/cse-analysis` |

### Skills (45)

| Plugin | Skills |
|:-------|:-------|
| bayesian-modeling | stan-fundamentals, pymc-fundamentals, bugs-fundamentals, hierarchical-models, regression-models, time-series-models, survival-models, meta-analysis, model-diagnostics |
| itc-modeling | tidy-itc-workflow, pairwise-ma-methodology, nma-methodology, maic-methodology, stc-methodology, ml-nmr-methodology |
| r-tidy-modeling | tidymodels-workflow, tidymodels-review-patterns, recipes-patterns, resampling-strategies, model-tuning, model-evaluation, survival-analysis, clinical-trials, bayesian-modeling, epidemiology-methods, genomics-analysis, r-documentation-patterns, roxygen2-pkgdown, meta-analysis, network-meta-analysis, ipd-meta-analysis, diagnostic-accuracy, causal-mediation, mendelian-randomization, pharmacokinetics, health-economics, real-world-evidence, advanced-adaptive-trials |
| clinical-trial-simulation | simtrial-fundamentals, mediana-fundamentals, multiplicity-methods, time-to-event-methods, group-sequential-methods, power-optimization-patterns, clinical-trial-design-patterns |

---

## Acknowledgments

- [Stan Development Team](https://mc-stan.org/)
- [PyMC Developers](https://www.pymc.io/)
- [Merck & Co.](https://github.com/Merck/simtrial) for simtrial
- [Mediana Inc.](https://github.com/medianasoft/Mediana) for Mediana
- [tidymodels team](https://www.tidymodels.org/)
- [Anthropic](https://www.anthropic.com/) for Claude Code

---

**License:** MIT -- see [LICENSE](https://github.com/choxos/BiostatAgent/blob/main/LICENSE) for details.
