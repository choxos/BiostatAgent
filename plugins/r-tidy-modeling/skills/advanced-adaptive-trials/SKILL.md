# Advanced Adaptive Trial Designs in R

## Overview

Advanced adaptive clinical trial designs including platform trials, basket and umbrella trials, response-adaptive randomization, multi-arm multi-stage designs, Bayesian adaptive methods, and sample size re-estimation techniques.

## Platform Trials

### Using adaptr Package

```r
library(adaptr)

# Define a platform trial with multiple arms
setup <- setup_trial(
  arms = c("Control", "Arm_A", "Arm_B", "Arm_C"),
  control = "Control",
  true_ys = c(0.30, 0.35, 0.45, 0.32),  # True response rates
  data_looks = seq(100, 500, by = 100),  # Interim analyses
  randomised_at_looks = NULL,            # Equal allocation initially
  min_n = 25                              # Minimum per arm before dropping
)

# Specify stopping rules
setup <- setup |>
  setup_trial_binom(
    highest_is_best = TRUE,
    soften_power = 0.5                    # Softening for allocation
  )

# Add arm dropping rules
setup <- setup_trial_binom(
  arms = c("Control", "Arm_A", "Arm_B", "Arm_C"),
  control = "Control",
  true_ys = c(0.30, 0.35, 0.45, 0.32),
  data_looks = seq(100, 500, 100),
  superiority = 0.99,                     # Probability for superiority
  inferiority = 0.01,                     # Probability for futility
  equivalence_prob = 0.90,
  equivalence_diff = 0.05
)

# Simulate trial
set.seed(123)
sims <- run_trials(setup, n_rep = 1000, cores = 4)

# Summarize results
summary(sims)
plot(sims)
```

### Adding Arms Mid-Trial

```r
library(adaptr)

# Platform trial with arm addition
setup_platform <- setup_trial_binom(
  arms = c("Control", "Arm_A", "Arm_B"),
  control = "Control",
  true_ys = c(0.30, 0.40, 0.35),
  data_looks = seq(100, 1000, 100),
  superiority = 0.99,
  inferiority = 0.01
)

# Add Arm_C at look 3 (n=300)
setup_platform <- setup_platform |>
  add_arm(
    arm = "Arm_C",
    true_y = 0.50,
    start_look = 3              # Add at third interim
  )

# Simulate
sims_platform <- run_trials(setup_platform, n_rep = 500)
summary(sims_platform)
```

## Response-Adaptive Randomization

### Thompson Sampling

```r
# Thompson sampling for binary outcomes
thompson_sampling <- function(successes, failures, n_arms) {
  # Sample from posterior Beta distributions
  samples <- sapply(1:n_arms, function(i) {
    rbeta(10000, successes[i] + 1, failures[i] + 1)
  })

  # Probability each arm is best
  prob_best <- colMeans(samples == apply(samples, 1, max))

  # Allocation probabilities (can apply min allocation constraint)
  alloc_prob <- prob_best
  alloc_prob <- pmax(alloc_prob, 0.1 / n_arms)  # Minimum 10% of equal
  alloc_prob <- alloc_prob / sum(alloc_prob)    # Normalize

  return(alloc_prob)
}

# Example: After 100 patients
successes <- c(20, 25, 30)  # Successes in Control, A, B
failures <- c(30, 25, 20)   # Failures

alloc <- thompson_sampling(successes, failures, 3)
cat("Allocation probabilities:", round(alloc, 3), "\n")
```

### RAR with Minimum Allocation

```r
# Response-adaptive randomization with constraints
rar_allocation <- function(posterior_probs, min_alloc = 0.1, control_fixed = TRUE) {

  n_arms <- length(posterior_probs)
  alloc <- posterior_probs

  if (control_fixed) {
    # Fix control allocation
    control_alloc <- 1 / n_arms
    remaining <- 1 - control_alloc
    alloc[-1] <- alloc[-1] / sum(alloc[-1]) * remaining
    alloc[1] <- control_alloc
  }

  # Apply minimum allocation
  alloc <- pmax(alloc, min_alloc)
  alloc <- alloc / sum(alloc)

  return(alloc)
}
```

## Basket Trials

### Using basket Package

```r
library(basket)

# Basket trial: One treatment, multiple tumor types/biomarker groups
# Data: responses (r) and sample sizes (n) per basket

basket_data <- data.frame(
  basket = c("Breast", "Lung", "Colon", "Melanoma", "Ovarian"),
  r = c(8, 12, 5, 15, 7),     # Responders
  n = c(20, 25, 18, 30, 22)   # Total patients
)

# Bayesian hierarchical model (MEM - Multisource Exchangeability Model)
fit_mem <- mem_exact(
  r = basket_data$r,
  n = basket_data$n,
  p0 = 0.15,                  # Null response rate
  shape1 = 0.5,               # Beta prior shape1
  shape2 = 0.5                # Beta prior shape2
)

summary(fit_mem)
plot(fit_mem)

# Posterior probabilities of response > p0
fit_mem$post_prob

# Cluster map (which baskets share information)
plot(fit_mem, type = "cluster")
```

### Hierarchical Model for Baskets

```r
library(basket)

# Full Bayesian hierarchical model
fit_hier <- basket(
  r = basket_data$r,
  n = basket_data$n,
  p0 = 0.15,
  method = "hpd",
  alpha = 0.05
)

# Alternative: EXNEX model (exchangeability-nonexchangeability)
# Allows some baskets to be exchangeable, others not
```

## Umbrella Trials

### Design Considerations

```r
# Umbrella trial: One disease, multiple biomarker-treatment pairs
# Each stratum has its own comparison

# Example setup
umbrella_design <- data.frame(
  stratum = c("EGFR+", "ALK+", "KRAS+", "Other"),
  treatment = c("Erlotinib", "Crizotinib", "Trametinib", "Chemotherapy"),
  target_n = c(100, 80, 120, 150),
  alpha = 0.025 / 4  # Bonferroni correction
)

# Each stratum can be analyzed separately
# But may share control arm or use master protocol

library(rpact)

# Design for each stratum
designs <- lapply(1:4, function(i) {
  getDesignGroupSequential(
    kMax = 2,
    alpha = umbrella_design$alpha[i],
    beta = 0.20,
    sided = 1,
    typeOfDesign = "OF"
  )
})
```

## Multi-Arm Multi-Stage (MAMS)

### Using MAMS Package

```r
library(MAMS)

# Design MAMS trial
mams_design <- mams(
  K = 3,                      # Number of experimental arms
  J = 2,                      # Number of stages
  alpha = 0.025,              # One-sided type I error
  power = 0.90,               # Power
  r = c(1, 1.5),             # Allocation ratio at each stage (exp:control)
  r0 = c(1, 1.5),            # Control allocation ratio
  p = 0.5,                    # Control response rate (continuous: effect size)
  p0 = 0.5,                   # Null response rate
  p1 = 0.65,                  # Alternative response rate
  ushape = "triangular",      # Upper boundary shape
  lshape = "triangular"       # Lower boundary shape
)

summary(mams_design)
plot(mams_design)

# Sample size
mams_design$n          # Per arm per stage
mams_design$N          # Total sample size
```

### MAMS with Continuous Outcome

```r
library(MAMS)

# MAMS for continuous outcomes
mams_cont <- mams(
  K = 4,
  J = 3,
  alpha = 0.025,
  power = 0.90,
  r = c(1, 1, 1),
  r0 = c(1, 1, 1),
  p = 0,                      # Null effect size (standardized)
  p0 = 0,
  p1 = 0.3,                   # Target effect size (standardized)
  ushape = "obf",             # O'Brien-Fleming
  lshape = "fixed"            # Fixed lower boundary
)

summary(mams_cont)
```

## Bayesian Adaptive Designs with RBesT

### Historical Data Integration

```r
library(RBesT)

# Meta-analytic predictive (MAP) prior from historical data
hist_data <- data.frame(
  study = paste0("Hist", 1:4),
  r = c(15, 20, 18, 22),      # Responders
  n = c(50, 55, 48, 60)       # Total
)

# Fit MAP prior
map_prior <- gMAP(
  cbind(r, n - r) ~ 1 | study,
  data = hist_data,
  family = binomial,
  tau.dist = "HalfNormal",
  tau.prior = 1,
  beta.prior = 2
)

summary(map_prior)
plot(map_prior)

# Get mixture prior approximation
prior_mix <- automixfit(map_prior)
plot(prior_mix)
```

### Robust Prior (Protect Against Conflict)

```r
library(RBesT)

# Robustify prior (mixture with vague component)
robust_prior <- robustify(
  prior_mix,
  weight = 0.2,           # 20% weight on vague component
  mean = 0.5              # Mean of vague component
)

plot(robust_prior)

# Compare priors
plot_mix <- function(...) {
  priors <- list(...)
  x <- seq(0, 1, 0.01)
  plot_data <- map_dfr(names(priors), function(nm) {
    tibble(x = x, y = dmix(priors[[nm]], x), prior = nm)
  })
  ggplot(plot_data, aes(x, y, color = prior)) + geom_line() + theme_bw()
}
```

### Operating Characteristics

```r
library(RBesT)

# Define decision rules
decision <- decision2S(
  pc = 0.975,             # Success: P(rate > p0) > 0.975
  qc = 0.10,              # Futility: P(rate > p0) < 0.10
  lower.tail = FALSE
)

# Operating characteristics
oc <- oc2S(
  prior_treatment = robust_prior,
  prior_control = robust_prior,
  n1_treatment = 30,      # Stage 1 treatment
  n1_control = 30,        # Stage 1 control
  n2_treatment = 30,      # Stage 2 treatment
  n2_control = 30,        # Stage 2 control
  decision = decision
)

# Plot OC curves
plot(oc)

# Type I error and power
summary(oc)
```

## Group Sequential Designs with rpact

### O'Brien-Fleming Design

```r
library(rpact)

# O'Brien-Fleming group sequential design
design_of <- getDesignGroupSequential(
  kMax = 3,                   # Number of stages
  alpha = 0.025,              # One-sided alpha
  beta = 0.20,                # Type II error
  sided = 1,
  typeOfDesign = "OF",
  informationRates = c(0.33, 0.67, 1.0)
)

summary(design_of)
plot(design_of)

# Boundaries
design_of$criticalValues    # Z-score boundaries
design_of$alphaSpent        # Cumulative alpha spent
```

### Sample Size Calculation

```r
library(rpact)

# Sample size for survival endpoint
sample_size <- getSampleSizeSurvival(
  design = design_of,
  lambda1 = log(2) / 24,      # Control median = 24 months
  lambda2 = log(2) / 36,      # Treatment median = 36 months (HR = 0.67)
  accrualTime = 24,           # Accrual period
  followUpTime = 12,          # Additional follow-up
  dropoutRate1 = 0.05,        # Control dropout
  dropoutRate2 = 0.05,        # Treatment dropout
  allocationRatioPlanned = 1
)

summary(sample_size)

# Events and sample size at each look
sample_size$eventsPerStage
sample_size$numberOfSubjects
```

### Interim Analysis

```r
library(rpact)

# Perform interim analysis
interim <- getAnalysisResults(
  design_of,
  dataInput = getDataset(
    n = c(100, 100),          # Cumulative n by stage
    events = c(40, 80),       # Cumulative events by stage
    logRanks = c(2.1, 2.8)    # Log-rank Z statistics
  )
)

summary(interim)

# Can the trial stop?
interim$finalStage           # Final stage reached?
interim$futilityStop         # Stopped for futility?
interim$rejectAtFinalStage   # Rejected at final analysis?
```

## Sample Size Re-Estimation

### Blinded SSR

```r
library(rpact)

# Sample size re-estimation based on interim data
ssr <- getSampleSizeReestimation(
  design_of,
  stageResults = interim,
  conditionalPower = 0.80     # Target conditional power
)

summary(ssr)
ssr$sampleSizeNew             # New sample size recommendation
```

### Unblinded SSR

```r
library(rpact)

# Conditional power at interim
cp <- getConditionalPower(
  design = design_of,
  stage = 2,
  stageResults = interim,
  nPlanned = c(50, 50),       # Planned future n per arm
  assumedEffect = 0.67        # Assumed treatment effect (HR)
)

summary(cp)

# If CP too low, calculate required sample size
if (cp$conditionalPower < 0.50) {
  # Increase sample size
  new_n <- getSampleSizeReestimation(design_of, interim, conditionalPower = 0.80)
}
```

## Graphical Multiplicity with gMCP

```r
library(gMCPLite)

# Define hypothesis graph
# H1, H2: Primary endpoints; H3, H4: Secondary endpoints
m <- matrix(
  c(0, 0.5, 0.5, 0,
    0.5, 0, 0, 0.5,
    0.5, 0, 0, 0.5,
    0, 0.5, 0.5, 0),
  nrow = 4, byrow = TRUE
)

weights <- c(0.5, 0.5, 0, 0)  # Initial alpha allocation

# Create graph
graph <- gMCP::matrix2graph(m, weights)
nodeNames(graph) <- c("H1_Primary", "H2_Primary", "H3_Secondary", "H4_Secondary")

# Plot
plot(graph)

# Test with p-values
pvalues <- c(0.01, 0.03, 0.02, 0.04)
result <- gMCP::gMCP(graph, pvalues, alpha = 0.025)
print(result)

# Which hypotheses rejected?
result@rejected
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| adaptr | Platform trial simulation |
| basket | Basket trial analysis |
| MAMS | Multi-arm multi-stage designs |
| rpact | Group sequential and adaptive designs |
| RBesT | Bayesian evidence synthesis |
| gMCPLite | Graphical multiplicity procedures |
| gsDesign | Group sequential designs |
| gsDesign2 | Enhanced group sequential |
| Mediana | Clinical trial simulations |

## Best Practices

1. **Pre-specification**: Define adaptation rules before trial starts
2. **Type I error**: Ensure strong control under all adaptations
3. **Operating characteristics**: Simulate extensively under various scenarios
4. **Blinding**: Maintain blinding where possible during adaptations
5. **Documentation**: Document all decision rules in protocol
6. **Regulatory**: Engage regulators early for complex adaptive designs
7. **Implementation**: Plan for operational complexity of adaptations
8. **Analysis**: Plan for potential biases from adaptations
