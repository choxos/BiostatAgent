# Clinical Trials Statistical Methods

## Overview

Comprehensive clinical trial design and analysis methods in R covering sample size calculation, randomization, interim analyses, multiplicity adjustment, and regulatory-compliant statistical methods.

## Sample Size Calculation

### Two-Group Comparisons

```r
library(pwr)

# Two-sample t-test
pwr.t.test(
  d = 0.5,           # Cohen's d effect size
  sig.level = 0.05,
  power = 0.80,
  type = "two.sample",
  alternative = "two.sided"
)

# Proportions (chi-square)
pwr.2p.test(
  h = ES.h(p1 = 0.6, p2 = 0.4),  # Cohen's h
  sig.level = 0.05,
  power = 0.80
)

# Two proportions (unequal groups)
pwr.2p2n.test(
  h = ES.h(p1 = 0.6, p2 = 0.4),
  n1 = 100,
  sig.level = 0.05
)
```

### Survival Endpoints

```r
library(gsDesign)

# Log-rank test sample size
nSurv(
  lambda1 = log(2)/12,  # Control median = 12 months
  lambda2 = log(2)/18,  # Treatment median = 18 months (HR = 0.67)
  Ts = 24,              # Study duration
  Tr = 12,              # Accrual duration
  alpha = 0.025,        # One-sided

  beta = 0.20,          # 80% power
  ratio = 1             # 1:1 randomization
)

# Using rpact
library(rpact)
getSampleSizeSurvival(
  hazardRatio = 0.67,
  lambda1 = log(2)/12,
  accrualTime = 12,
  followUpTime = 12,
  alpha = 0.025,
  beta = 0.20,
  allocationRatioPlanned = 1
)
```

### Non-Inferiority Trials

```r
library(TrialSize)

# Non-inferiority for proportions
TwoSampleProportion.NIS(
  p = 0.80,           # Expected proportion in both groups
  delta = 0.10,       # Non-inferiority margin
  alpha = 0.025,      # One-sided
  power = 0.80
)

# Non-inferiority for means
TwoSampleMean.NIS(
  sigma = 10,         # SD
  delta = 5,          # Non-inferiority margin
  alpha = 0.025,
  power = 0.80
)
```

## Randomization

### Simple Randomization

```r
# Base R simple randomization
set.seed(123)
n <- 100
treatment <- sample(c("A", "B"), n, replace = TRUE)

# blockrand package
library(blockrand)
randomization <- blockrand(
  n = 100,
  num.levels = 2,
  levels = c("Treatment", "Control"),
  id.prefix = "PAT",
  block.prefix = "BLK"
)
```

### Stratified Block Randomization

```r
library(blockrand)

# Generate lists for each stratum
strata <- expand.grid(
  sex = c("Male", "Female"),
  age_group = c("<65", ">=65")
)

rand_lists <- lapply(1:nrow(strata), function(i) {
  blockrand(
    n = 50,
    num.levels = 2,
    levels = c("Treatment", "Control"),
    block.sizes = c(2, 4, 6),  # Variable block sizes
    stratum = paste(strata[i, ], collapse = "_")
  )
})

full_list <- do.call(rbind, rand_lists)
```

### Minimization

```r
library(Minirand)

# Minimization randomization
minirand(
  covariates = data.frame(
    sex = c("M", "F", "M"),
    age = c("young", "old", "young"),
    center = c("A", "A", "B")
  ),
  treatment = c("A", "B"),
  ratio = c(1, 1),
  p = 0.85  # Probability of assigning to minimizing treatment
)
```

## Group Sequential Designs

### gsDesign Package

```r
library(gsDesign)

# O'Brien-Fleming boundaries
gs_design <- gsDesign(
  k = 3,               # Number of analyses
  test.type = 2,       # Two-sided symmetric
  alpha = 0.025,       # One-sided alpha
  beta = 0.20,         # Type II error
  sfu = "OF",          # O'Brien-Fleming spending function
  timing = c(0.5, 0.75, 1)  # Information fractions
)

# Summary
gs_design

# Boundaries
gs_design$upper$bound  # Upper efficacy boundary
gs_design$lower$bound  # Lower futility boundary

# Plot
plot(gs_design)
```

### Alpha Spending Functions

```r
# Pocock
gs_pocock <- gsDesign(k = 3, sfu = "Pocock")

# Hwang-Shih-DeCani
gs_hsd <- gsDesign(k = 3, sfu = sfHSD, sfupar = -4)

# Power family (Kim-DeMets)
gs_power <- gsDesign(k = 3, sfu = sfPower, sfupar = 2)

# Custom spending
gs_custom <- gsDesign(
  k = 3,
  sfu = sfPoints,
  sfupar = c(0.01, 0.03, 0.025),  # Cumulative alpha at each look
  timing = c(0.5, 0.75, 1)
)
```

### rpact Package

```r
library(rpact)

# Design
design <- getDesignGroupSequential(
  kMax = 3,
  alpha = 0.025,
  beta = 0.20,
  sided = 1,
  typeOfDesign = "OF",  # O'Brien-Fleming
  informationRates = c(0.5, 0.75, 1)
)

# Sample size
sampleSize <- getSampleSizeMeans(
  design = design,
  alternative = 0.5,
  stDev = 1
)

# Interim analysis
getAnalysisResults(
  design,
  dataInput = getDataset(
    n = c(50, 75),
    means = c(0.3, 0.4),
    stDevs = c(1, 1)
  )
)
```

## Multiplicity Adjustment

### P-value Adjustments

```r
# Bonferroni
p.adjust(p_values, method = "bonferroni")

# Holm (step-down)
p.adjust(p_values, method = "holm")

# Hochberg (step-up)
p.adjust(p_values, method = "hochberg")

# Benjamini-Hochberg (FDR)
p.adjust(p_values, method = "BH")

# Hommel
p.adjust(p_values, method = "hommel")
```

### Graphical Approaches

```r
library(gMCP)

# Define hypothesis graph
graph <- matrix2graph(
  # Transition matrix
  m = matrix(c(
    0, 0.5, 0.5, 0,
    0.5, 0, 0, 0.5,
    0.5, 0, 0, 0.5,
    0, 0.5, 0.5, 0
  ), nrow = 4, byrow = TRUE),
  # Initial weights
  w = c(0.5, 0.5, 0, 0)
)

# Set hypothesis names
nodeNames(graph) <- c("H1_OS", "H2_OS", "H1_PFS", "H2_PFS")

# Plot graph
plot(graph)

# Perform test
gMCP(
  graph = graph,
  pvalues = c(0.01, 0.03, 0.02, 0.04),
  alpha = 0.025
)
```

### Gatekeeping Procedures

```r
library(multcomp)

# Serial gatekeeping
# Primary must be significant before testing secondary
serial_gate <- function(p_primary, p_secondary, alpha = 0.05) {
  if (p_primary < alpha) {
    # Primary significant, test secondary at full alpha
    return(c(primary = p_primary < alpha, secondary = p_secondary < alpha))
  } else {
    return(c(primary = FALSE, secondary = FALSE))
  }
}
```

## Missing Data

### Mixed Models for Repeated Measures (MMRM)

```r
library(mmrm)

# MMRM model
mmrm_fit <- mmrm(
  formula = change ~ treatment * visit + baseline + us(visit | subject),
  data = long_data,
  weights = NULL,
  reml = TRUE
)

# Least squares means
library(emmeans)
emmeans(mmrm_fit, ~ treatment | visit)

# Treatment comparison at each visit
emmeans(mmrm_fit, pairwise ~ treatment | visit)
```

### Multiple Imputation

```r
library(mice)

# Create imputations
imp <- mice(
  data = df,
  m = 20,           # Number of imputations
  method = "pmm",   # Predictive mean matching
  maxit = 10
)

# Analyze each imputed dataset
analyses <- with(imp, lm(outcome ~ treatment + covariates))

# Pool results (Rubin's rules)
pooled <- pool(analyses)
summary(pooled)
```

### Tipping Point Analysis

```r
# Sensitivity analysis for MNAR
library(rbmi)

# Define imputation method with delta adjustment
draws <- draws(
  data = data,
  data_ice = ice_data,
  method = method_bayes(),
  vars = vars
)

# Impute with different delta values
impute(draws, references = c("Control" = "Control", "Treatment" = "Control"))
```

## Subgroup Analysis

### Forest Plots for Subgroups

```r
library(forestplot)

# Calculate treatment effects by subgroup
subgroup_effects <- df |>
  group_by(subgroup) |>
  summarise(
    n = n(),
    effect = mean(outcome[trt == 1]) - mean(outcome[trt == 0]),
    se = sqrt(var(outcome[trt == 1])/sum(trt == 1) +
              var(outcome[trt == 0])/sum(trt == 0)),
    lower = effect - 1.96 * se,
    upper = effect + 1.96 * se
  )

# Create forest plot
forestplot(
  labeltext = subgroup_effects$subgroup,
  mean = subgroup_effects$effect,
  lower = subgroup_effects$lower,
  upper = subgroup_effects$upper,
  zero = 0,
  xlab = "Treatment Effect (95% CI)"
)
```

### Interaction Tests

```r
# Test for treatment-by-subgroup interaction
interaction_model <- lm(outcome ~ treatment * subgroup, data = df)
anova(interaction_model)

# Quantitative interaction test
library(QI)
qi_test(outcome ~ treatment | subgroup, data = df)
```

## Regulatory Considerations

### ICH E9 Estimands Framework

```r
# Define estimand components:
# 1. Population
# 2. Variable (endpoint)
# 3. Intercurrent events and strategies
# 4. Population-level summary

# Example: Treatment policy estimand with MMRM
mmrm_fit <- mmrm(
  change ~ treatment * visit + baseline + us(visit | subject),
  data = data_all_randomized  # Include all randomized (ITT)
)
```

### CONSORT Diagram

```r
library(consort)

# Create CONSORT diagram
consort_plot(
  data = trial_data,
  orders = c(
    Assessed = "Assessed for eligibility",
    Randomized = "Randomized",
    Arm_A = "Allocated to Arm A",
    Arm_B = "Allocated to Arm B",
    Lost_A = "Lost to follow-up (Arm A)",
    Lost_B = "Lost to follow-up (Arm B)",
    Analyzed_A = "Analyzed (Arm A)",
    Analyzed_B = "Analyzed (Arm B)"
  ),
  side_box = c("Excluded", "Discontinued_A", "Discontinued_B"),
  cex = 0.8
)
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| pwr | Power analysis |
| gsDesign | Group sequential designs |
| rpact | Adaptive designs |
| blockrand | Randomization |
| gMCP | Graphical multiplicity |
| mmrm | MMRM analysis |
| mice | Multiple imputation |
| rbmi | Reference-based imputation |
| emmeans | Least squares means |
| consort | CONSORT diagrams |
