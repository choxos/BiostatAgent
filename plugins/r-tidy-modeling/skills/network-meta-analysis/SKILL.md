# Network Meta-Analysis in R

## Overview

Network meta-analysis (NMA) methods for comparing multiple treatments simultaneously using direct and indirect evidence. Covers network structure assessment, frequentist and Bayesian NMA approaches, consistency evaluation, treatment rankings, and visualization techniques.

## Network Structure and Data Preparation

### Pairwise Data Format

```r
library(netmeta)

# Standard pairwise format for contrast-based NMA
pairwise_data <- data.frame(
  study = c("Study1", "Study1", "Study2", "Study2", "Study3", "Study3",
            "Study4", "Study4", "Study5", "Study5", "Study5"),
  treat1 = c("A", "A", "A", "B", "B", "B", "A", "C", "A", "B", "C"),
  treat2 = c("B", "C", "B", "C", "C", "D", "C", "D", "B", "C", "D"),
  TE = c(0.5, 0.3, 0.4, -0.2, 0.1, 0.3, 0.35, 0.25, 0.45, -0.15, 0.2),
  seTE = c(0.1, 0.12, 0.11, 0.13, 0.15, 0.14, 0.09, 0.11, 0.10, 0.12, 0.13)
)

# Create network meta-analysis object
net <- netmeta(
  TE = TE,
  seTE = seTE,
  treat1 = treat1,
  treat2 = treat2,
  studlab = study,
  data = pairwise_data,
  sm = "MD",                    # Effect measure
  reference.group = "A",        # Reference treatment
  all.treatments = NULL         # Auto-detect
)

summary(net)
```

### Arm-Level Data Format

```r
library(netmeta)

# Convert arm-level to pairwise format
arm_data <- data.frame(
  study = rep(c("S1", "S2", "S3"), c(2, 3, 2)),
  treatment = c("A", "B", "A", "B", "C", "B", "C"),
  n = c(50, 52, 48, 51, 49, 55, 53),
  events = c(15, 22, 12, 25, 18, 28, 20)
)

# Use pairwise() to convert
library(meta)
pw <- pairwise(
  treat = treatment,
  event = events,
  n = n,
  studlab = study,
  data = arm_data,
  sm = "OR"
)

# Create network
net_from_arm <- netmeta(pw)
```

### Network Visualization

```r
library(netmeta)

# Network graph
netgraph(net,
         plastic = FALSE,
         thickness = "number.of.studies",
         multiarm = TRUE,
         points = TRUE,
         cex.points = 3,
         col = "darkblue")

# Improved network graph
netgraph(net,
         seq = "optimal",           # Optimal node arrangement
         plastic = FALSE,
         thickness = "se.fixed",    # Edge thickness by precision
         number.of.studies = TRUE,  # Show number of studies
         col = "#4477AA",
         col.points = "#CC6677",
         cex.points = 4,
         labels = paste0(trts(net), "\n(n=", n.arms(net), ")"))
```

## Frequentist NMA with netmeta

### Basic Network Meta-Analysis

```r
library(netmeta)

# Fit NMA (fixed and random effects)
net <- netmeta(
  TE = TE,
  seTE = seTE,
  treat1 = treat1,
  treat2 = treat2,
  studlab = study,
  data = pairwise_data,
  sm = "MD",
  fixed = TRUE,
  random = TRUE,
  reference.group = "A"
)

# Summary
summary(net)

# Results for specific comparison
net$TE.fixed["B", "A"]      # Fixed effect B vs A
net$TE.random["B", "A"]     # Random effects B vs A
net$seTE.random["B", "A"]   # SE for random effects
```

### Forest Plot for NMA

```r
library(netmeta)

# Forest plot: all treatments vs reference
forest(net,
       reference.group = "A",
       sortvar = TE,
       smlab = "Mean Difference vs A",
       drop.reference.group = TRUE,
       label.left = "Favors A",
       label.right = "Favors Treatment")

# Forest plot with subgroup (by comparison type)
forest(net,
       reference.group = "A",
       direct = TRUE)  # Show direct evidence only
```

### League Table

```r
library(netmeta)

# League table (all pairwise comparisons)
league <- netleague(
  net,
  digits = 2,
  bracket = "(",
  separator = " to ",
  fixed = FALSE    # Use random effects
)

# Print league table
print(league, common = FALSE)

# As matrix
league$random
```

### Treatment Rankings

```r
library(netmeta)

# P-scores (frequentist ranking)
netrank(net, small.values = "good")

# Rankogram
set.seed(123)
rank <- rankogram(net, nsim = 1000)
plot(rank)

# SUCRA-like plot
plot(rank, cumulative = TRUE)
```

## Bayesian NMA with gemtc

### Basic Bayesian NMA

```r
library(gemtc)

# Prepare data for gemtc (arm-level)
network_data <- list(
  data.ab = data.frame(
    study = c("S1", "S1", "S2", "S2", "S3", "S3", "S3"),
    treatment = c("A", "B", "A", "C", "A", "B", "C"),
    responders = c(15, 22, 12, 18, 20, 28, 24),
    sampleSize = c(50, 52, 48, 49, 55, 58, 54)
  )
)

# Create network object
network <- mtc.network(data.ab = network_data$data.ab)

# Plot network
plot(network)

# Consistency model
model <- mtc.model(
  network,
  type = "consistency",
  likelihood = "binom",
  link = "logit",
  linearModel = "random"
)

# Run MCMC
set.seed(123)
result <- mtc.run(
  model,
  n.adapt = 5000,
  n.iter = 20000,
  thin = 1
)

summary(result)
```

### Model Diagnostics

```r
library(gemtc)
library(coda)

# Trace plots
plot(result)

# Gelman-Rubin diagnostic
gelman.diag(result$samples)
gelman.plot(result$samples)

# Effective sample size
effectiveSize(result$samples)

# Autocorrelation
autocorr.plot(result$samples)

# Density plots
densplot(result$samples)
```

### Treatment Rankings (Bayesian)

```r
library(gemtc)

# Rank probabilities
ranks <- rank.probability(result)
print(ranks)

# Plot rank probabilities
plot(ranks)

# SUCRA
sucra <- sucra(ranks)
print(sucra)

# Cumulative ranking plot
plot(ranks, beside = TRUE)
```

## Bayesian NMA with multinma

### Using multinma Package

```r
library(multinma)

# Prepare data
nma_data <- set_agd_arm(
  data = arm_data,
  study = study,
  trt = treatment,
  r = events,
  n = n
)

# Network plot
plot(nma_data)

# Fit Bayesian NMA
nma_fit <- nma(
  nma_data,
  trt_effects = "random",
  prior_intercept = normal(scale = 10),
  prior_trt = normal(scale = 10),
  prior_het = half_normal(scale = 1)
)

# Summary
summary(nma_fit)
print(nma_fit, pars = "d")

# Treatment effects
relative_effects(nma_fit, all_contrasts = TRUE)
```

### Population-Adjusted NMA

```r
library(multinma)

# With individual patient data (IPD) and aggregate data (AgD)
# IPD data
ipd_data <- set_ipd(
  data = ipd_df,
  study = study,
  trt = treatment,
  y = outcome
)

# AgD data
agd_data <- set_agd_arm(
  data = agd_df,
  study = study,
  trt = treatment,
  r = events,
  n = n
)

# Combine networks
combined_network <- combine_network(ipd_data, agd_data)

# Fit with covariate adjustment
nma_cov <- nma(
  combined_network,
  trt_effects = "random",
  regression = ~age + sex
)
```

## Consistency Assessment

### Global Inconsistency Tests

```r
library(netmeta)

# Design-by-treatment interaction model
decomp <- decomp.design(net)
print(decomp)

# Q statistics
decomp$Q.decomp           # Overall Q decomposition
decomp$Q.het.design       # Within-design heterogeneity
decomp$Q.inc.detach       # Between-design inconsistency

# Net heat plot (visual inconsistency)
netheat(net)
```

### Local Inconsistency (Node-Splitting)

```r
library(netmeta)

# Node-splitting for all comparisons with direct evidence
netsplit_result <- netsplit(net)
print(netsplit_result)

# Forest plot of node-splitting
forest(netsplit_result)

# Using gemtc for Bayesian node-splitting
library(gemtc)

# Node-split model
nodesplit <- mtc.nodesplit(network, comparisons = NULL)  # All comparisons

# Run each comparison
ns_results <- lapply(nodesplit, function(model) {
  mtc.run(model, n.adapt = 5000, n.iter = 20000)
})

# Summary
mtc.nodesplit.comparisons(nodesplit)
```

### Inconsistency Model

```r
library(gemtc)

# Unrelated mean effects (inconsistency) model
model_ume <- mtc.model(
  network,
  type = "ume",
  likelihood = "binom",
  link = "logit"
)

result_ume <- mtc.run(model_ume, n.adapt = 5000, n.iter = 20000)

# Compare DIC
summary(result)$DIC      # Consistency model
summary(result_ume)$DIC  # Inconsistency model

# Model comparison
mtc.deviance(result)
```

## Heterogeneity Assessment

```r
library(netmeta)

# Heterogeneity statistics
net$tau           # Tau (between-study SD)
net$tau2          # Tau-squared
net$I2            # I-squared
net$Q             # Q statistic
net$df.Q          # Degrees of freedom
net$pval.Q        # P-value for Q

# Prediction intervals
net$lower.predict  # Lower prediction interval
net$upper.predict  # Upper prediction interval
```

## Network Meta-Regression

```r
library(netmeta)

# With study-level covariate
net_reg <- netmeta(
  TE = TE,
  seTE = seTE,
  treat1 = treat1,
  treat2 = treat2,
  studlab = study,
  data = pairwise_data,
  sm = "MD"
)

# Meta-regression using netmetareg (requires netmeta >= 2.0)
# net_reg <- netmetareg(net, ~year)

# Alternative: Use gemtc with covariates
library(gemtc)

# Add study-level covariate
network_cov <- mtc.network(
  data.ab = network_data$data.ab,
  studies = data.frame(
    study = c("S1", "S2", "S3"),
    year = c(2010, 2015, 2020)
  )
)

model_reg <- mtc.model(
  network_cov,
  type = "regression",
  regressor = list(coefficient = "shared", variable = "year")
)

result_reg <- mtc.run(model_reg, n.adapt = 5000, n.iter = 20000)
summary(result_reg)
```

## Subgroup and Sensitivity Analysis

```r
library(netmeta)

# Subgroup NMA by risk of bias
net_low_rob <- netmeta(
  TE = TE[rob == "low"],
  seTE = seTE[rob == "low"],
  treat1 = treat1[rob == "low"],
  treat2 = treat2[rob == "low"],
  studlab = study[rob == "low"],
  sm = "MD"
)

# Compare results
comparison_table <- data.frame(
  Model = c("All studies", "Low RoB only"),
  Tau = c(net$tau, net_low_rob$tau),
  Effect_B_vs_A = c(net$TE.random["B", "A"], net_low_rob$TE.random["B", "A"])
)
```

## Reporting and Visualization

### PRISMA-NMA Flow Diagram

```r
# Recommended reporting items for NMA
# 1. Network geometry
# 2. Assessment of transitivity
# 3. Presentation of results (forest, league table)
# 4. Ranking with uncertainty
# 5. Assessment of inconsistency
# 6. Assessment of heterogeneity
```

### Comparison-Adjusted Funnel Plot

```r
library(netmeta)

# Funnel plot for NMA
funnel(net,
       order = c("A", "B", "C", "D"),
       pooled = "random",
       pch = 1:4,
       legend = TRUE)
```

### Summary of Evidence Table

```r
# Create summary table for publication
create_nma_summary <- function(net, ref = "A") {
  treatments <- net$trts[net$trts != ref]

  summary_df <- data.frame(
    Comparison = paste(treatments, "vs", ref),
    Effect_Fixed = sapply(treatments, function(t) net$TE.fixed[t, ref]),
    CI_Lower_Fixed = sapply(treatments, function(t) net$lower.fixed[t, ref]),
    CI_Upper_Fixed = sapply(treatments, function(t) net$upper.fixed[t, ref]),
    Effect_Random = sapply(treatments, function(t) net$TE.random[t, ref]),
    CI_Lower_Random = sapply(treatments, function(t) net$lower.random[t, ref]),
    CI_Upper_Random = sapply(treatments, function(t) net$upper.random[t, ref])
  )

  # Format
  summary_df <- summary_df |>
    mutate(
      Fixed = paste0(round(Effect_Fixed, 2), " (",
                    round(CI_Lower_Fixed, 2), ", ",
                    round(CI_Upper_Fixed, 2), ")"),
      Random = paste0(round(Effect_Random, 2), " (",
                     round(CI_Lower_Random, 2), ", ",
                     round(CI_Upper_Random, 2), ")")
    ) |>
    select(Comparison, Fixed, Random)

  return(summary_df)
}
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| netmeta | Frequentist NMA (contrast-based) |
| gemtc | Bayesian NMA with JAGS |
| multinma | Bayesian NMA with Stan |
| bnma | Bayesian NMA |
| pcnetmeta | Patient-centered NMA |
| NMAoutlier | Outlier detection in NMA |
| nmathresh | Decision thresholds for NMA |

## Best Practices

1. **Network geometry**: Check connectivity before analysis
2. **Transitivity**: Assess similarity of study populations across comparisons
3. **Consistency**: Always assess local and global inconsistency
4. **Heterogeneity**: Report tau, I², and consider prediction intervals
5. **Ranking**: Present uncertainty (CrI for ranks, rankograms)
6. **Sensitivity**: Conduct analyses excluding high RoB studies
7. **Reporting**: Follow PRISMA-NMA extension guidelines
8. **Model selection**: Compare fixed vs random effects, check model fit
