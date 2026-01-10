# ITC Modelling Plugin

> **Indirect Treatment Comparison Experts** — Pairwise MA, NMA, MAIC, STC, and ML-NMR following NICE DSU guidance

Part of the [BiostatAgent](https://github.com/choxos/BiostatAgent) ecosystem.

## Overview

This plugin provides expert agents for indirect treatment comparison (ITC) methodologies used in health technology assessment (HTA). All methods follow NICE Decision Support Unit (DSU) Technical Support Documents.

| Method | Data Requirements | Key Assumption | R Package |
|--------|-------------------|----------------|-----------|
| **Pairwise MA** | AgD from multiple trials | Common comparator | meta, metafor, bayesmeta |
| **NMA** | AgD network | Transitivity, consistency | netmeta, gemtc |
| **MAIC** | IPD vs AgD | No unmeasured effect modifiers | maicplus |
| **STC** | IPD vs AgD | Correct outcome model | Custom/stc |
| **ML-NMR** | Mixed IPD + AgD | Exchangeability | multinma |

## Quick Start

```bash
# Install plugin
/plugin install itc-modelling

# Start ITC analysis
/itc-analysis
```

## Commands

### `/itc-analysis`
Complete ITC workflow from method selection to results interpretation.

**Workflow:**
1. Assess available data (IPD vs AgD)
2. Evaluate network structure
3. Select appropriate ITC method
4. Implement analysis
5. Validate assumptions
6. Generate results and diagnostics

**Example:**
```
I have IPD from my trial comparing Drug A vs Placebo, and published
aggregate data from a trial comparing Drug B vs Placebo. I need to
estimate the relative efficacy of Drug A vs Drug B for a binary endpoint.
```

### `/itc-review`
Review existing ITC code for methodological correctness and best practices.

**Checks:**
- Appropriate method selection
- Assumption validation
- Weight diagnostics (MAIC)
- Consistency assessment (NMA)
- Sensitivity analyses

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `itc-architect` | Haiku | Routes to appropriate ITC specialist |
| `pairwise-meta-analyst` | Sonnet | Frequentist and Bayesian pairwise meta-analysis |
| `nma-specialist` | Sonnet | Network meta-analysis with netmeta and gemtc |
| `maic-specialist` | Sonnet | Matching-adjusted indirect comparison with maicplus |
| `stc-specialist` | Sonnet | Simulated treatment comparison |
| `ml-nmr-specialist` | Sonnet | Multilevel network meta-regression with multinma |
| `itc-code-reviewer` | Sonnet | Reviews ITC code for methodological issues |

## Skills

### Core Methodologies
- **pairwise-ma-methodology** — Fixed/random effects, heterogeneity (I², τ²), publication bias
- **nma-methodology** — Network geometry, transitivity, consistency, treatment rankings
- **maic-methodology** — Weight estimation, ESS, anchored vs unanchored MAIC
- **stc-methodology** — Outcome regression, effect modifier selection, covariate centering
- **ml-nmr-methodology** — IPD/AgD integration, population adjustment, multinma package

### Workflow
- **tidy-itc-workflow** — Reproducible ITC pipelines following tidy principles

## Method Selection Guide

```
                    ┌─────────────────────────────┐
                    │  Do you have IPD for at     │
                    │  least one trial?           │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                   YES                           NO
                    │                             │
        ┌───────────┴───────────┐     ┌──────────┴──────────┐
        │  Is there a common    │     │  Is there a         │
        │  comparator (anchor)? │     │  connected network? │
        └───────────┬───────────┘     └──────────┬──────────┘
                    │                             │
         ┌──────────┴──────────┐       ┌─────────┴─────────┐
         │                     │       │                   │
        YES                   NO      YES                 NO
         │                     │       │                   │
    ┌────┴────┐          ┌────┴────┐  │            ┌──────┴──────┐
    │ MAIC or │          │Unanchored│  │            │  Cannot     │
    │   STC   │          │  MAIC   │  │            │  compare    │
    └─────────┘          └─────────┘  │            └─────────────┘
                                      │
                              ┌───────┴───────┐
                              │               │
                          Pairwise          Network
                             MA               MA
```

## Usage Examples

### Pairwise Meta-Analysis

```
Conduct a random-effects meta-analysis of 8 RCTs comparing
treatment vs control for a continuous outcome. Include
heterogeneity assessment and forest plot.
```

**Generated R code:**
```r
library(meta)

# Meta-analysis
ma_result <- metacont(
  n.e = n_treatment, mean.e = mean_treatment, sd.e = sd_treatment,
  n.c = n_control, mean.c = mean_control, sd.c = sd_control,
  studlab = study,
  data = trials,
  sm = "MD",
  method.tau = "REML",
  hakn = TRUE
)

# Results
summary(ma_result)

# Forest plot
forest(ma_result,
       sortvar = TE,
       prediction = TRUE,
       print.tau2 = TRUE,
       leftcols = c("studlab", "n.e", "n.c"),
       leftlabs = c("Study", "N (Tx)", "N (Ctrl)"))

# Heterogeneity
cat("I² =", round(ma_result$I2 * 100, 1), "%\n")
cat("τ² =", round(ma_result$tau2, 4), "\n")
```

### Network Meta-Analysis (Frequentist)

```
Perform a network meta-analysis comparing 4 treatments (A, B, C, Placebo)
using aggregate data from 12 trials. Assess consistency and generate
league table.
```

**Generated R code:**
```r
library(netmeta)

# Prepare pairwise data
pw_data <- pairwise(
  treat = treatment,
  event = events,
  n = n,
  studlab = study,
  data = trials,
  sm = "OR"
)

# Network meta-analysis
nma <- netmeta(
  TE, seTE, treat1, treat2, studlab,
  data = pw_data,
  sm = "OR",
  reference.group = "Placebo",
  common = FALSE,
  random = TRUE
)

# Network plot
netgraph(nma, plastic = FALSE, thickness = "number.of.studies",
         multiarm = TRUE, points = TRUE)

# League table
netleague(nma, digits = 2, bracket = "(", separator = " to ")

# Consistency assessment
netsplit(nma)
```

### MAIC (Anchored)

```
Perform an anchored MAIC to compare Drug A (IPD) vs Drug B (AgD).
Both trials have placebo arms. Match on age, sex, and baseline severity.
Binary endpoint (response rate).
```

**Generated R code:**
```r
library(maicplus)

# Specify effect modifiers to match
match_vars <- c("age", "sex_male", "baseline_severity")

# Estimate weights
weighted_data <- estimate_weights(
  data = ipd_data,
  centered_colnames = match_vars,
  agd_means = agd_summary[match_vars]
)

# Check effective sample size
ess <- weighted_data$ess
cat("Original N:", nrow(ipd_data), "\n")
cat("Effective sample size:", round(ess, 1), "\n")
cat("ESS reduction:", round((1 - ess/nrow(ipd_data)) * 100, 1), "%\n")

# Weight diagnostics
summarize_wts(weighted_data)

# Anchored comparison (binary endpoint)
result <- maic_anchored(
  weights_object = weighted_data,
  ipd_data = ipd_data,
  agd_data = agd_data,
  ipd_event = "response",
  agd_n_trt = n_B,
  agd_event_trt = events_B,
  agd_n_ctrl = n_placebo_B,
  agd_event_ctrl = events_placebo_B,
  binary_method = "bucher"
)

# Results
print(result)
```

### ML-NMR with multinma

```
Conduct a multilevel network meta-regression combining IPD from 2 trials
and AgD from 5 trials. Adjust for age as a treatment effect modifier.
```

**Generated R code:**
```r
library(multinma)

# Combine IPD and AgD
combined_network <- combine_network(
  set_ipd(ipd_trials, studyid, trtid,
          y = outcome, trt_ref = "Placebo"),
  set_agd_arm(agd_trials, studyid, trtid,
              y = mean, se = se, n = n,
              trt_ref = "Placebo")
)

# Fit ML-NMR with covariate adjustment
mlnmr_fit <- nma(
  combined_network,
  trt_effects = "random",
  regression = ~ age_centered * .trt,
  prior_intercept = normal(0, 10),
  prior_trt = normal(0, 2),
  prior_reg = normal(0, 1),
  prior_het = half_normal(1),
  adapt_delta = 0.95,
  iter = 4000
)

# Results
print(mlnmr_fit)

# Relative effects
relative_effects(mlnmr_fit, newdata = target_population)

# Predictions for target population
predict(mlnmr_fit, newdata = target_population, type = "response")
```

## Key Assumptions by Method

### Pairwise Meta-Analysis
- Studies measure same treatment comparison
- Outcomes are comparable (same definition, timing)
- Random effects: true effects vary between studies

### Network Meta-Analysis
- **Transitivity**: Effect modifiers are balanced across comparisons
- **Consistency**: Direct and indirect evidence agree
- No closed loops with conflicting evidence

### MAIC
- All effect modifiers are observed and matched
- No unmeasured confounding after weighting
- Target population represented by AgD trial

### STC
- Outcome model correctly specified
- Effect modifiers correctly identified
- Linear (or specified) relationship with outcome

### ML-NMR
- IPD and AgD are exchangeable after adjustment
- Covariate-outcome relationships are correctly specified
- Effect modification is consistent across network

## R Dependencies

```r
# Core packages
install.packages(c("meta", "metafor", "netmeta", "gemtc"))

# MAIC
# Install maicplus from GitHub
remotes::install_github("hta-pharma/maicplus")

# ML-NMR
install.packages("multinma")

# Bayesian meta-analysis
install.packages("bayesmeta")

# Supporting
install.packages(c("dplyr", "ggplot2", "tidyr"))
```

## NICE DSU Technical Support Documents

This plugin follows guidance from:
- **TSD 2**: Network meta-analysis
- **TSD 17**: Population-adjusted indirect comparisons (MAIC/STC)
- **TSD 18**: Methods for population-adjusted indirect comparisons

## References

- Dias S, et al. (2018). Network Meta-Analysis for Decision Making. Wiley.
- Phillippo DM, et al. (2018). Methods for Population-Adjusted Indirect Comparisons. Medical Decision Making.
- Signorovitch JE, et al. (2010). Comparative Effectiveness Without Head-to-Head Trials. PharmacoEconomics.
- NICE DSU Technical Support Documents: https://www.sheffield.ac.uk/nice-dsu

## License

MIT License — see [LICENSE](../../LICENSE) for details.
