# Health Economics Evaluation in R

## Overview

Health economic evaluation methods covering cost-effectiveness analysis (CEA), quality-adjusted life years (QALYs), incremental cost-effectiveness ratios (ICERs), budget impact analysis, Markov cohort models, partitioned survival analysis, probabilistic sensitivity analysis, and value of information analysis.

## Cost-Effectiveness Fundamentals

### Basic Calculations

```r
# Treatment comparison data
# Intervention vs Comparator
costs_int <- 15000      # Mean cost of intervention
costs_comp <- 8000      # Mean cost of comparator
effects_int <- 5.2      # Mean QALYs intervention
effects_comp <- 4.5     # Mean QALYs comparator

# Incremental calculations
delta_cost <- costs_int - costs_comp      # Incremental cost
delta_effect <- effects_int - effects_comp # Incremental effect (QALYs)

# Incremental Cost-Effectiveness Ratio (ICER)
icer <- delta_cost / delta_effect
cat("ICER:", round(icer, 0), "per QALY gained\n")

# Net Monetary Benefit (NMB) at WTP threshold
wtp <- 50000  # Willingness-to-pay threshold
nmb <- delta_effect * wtp - delta_cost
cat("NMB at WTP $", wtp, ":", round(nmb, 0), "\n")

# Net Health Benefit (NHB)
nhb <- delta_effect - delta_cost / wtp
cat("NHB:", round(nhb, 3), "QALYs\n")
```

### Cost-Effectiveness Plane

```r
library(ggplot2)

# Simulated incremental costs and effects
set.seed(123)
n_sim <- 1000
delta_c <- rnorm(n_sim, delta_cost, 2000)
delta_e <- rnorm(n_sim, delta_effect, 0.3)

ce_data <- data.frame(
  delta_cost = delta_c,
  delta_effect = delta_e
)

# CE plane
ggplot(ce_data, aes(x = delta_effect, y = delta_cost)) +
  geom_point(alpha = 0.3, color = "blue") +
  geom_hline(yintercept = 0, linetype = "dashed") +
  geom_vline(xintercept = 0, linetype = "dashed") +
  geom_abline(slope = wtp, intercept = 0, color = "red", linetype = "dashed") +
  annotate("text", x = 1.5, y = 15000, label = paste0("WTP = $", wtp),
           color = "red") +
  labs(x = "Incremental Effect (QALYs)",
       y = "Incremental Cost ($)",
       title = "Cost-Effectiveness Plane") +
  theme_bw()
```

## Cost-Effectiveness Analysis with BCEA

### Using BCEA Package

```r
library(BCEA)

# From PSA samples (effects and costs matrices)
# Each row = simulation, columns = interventions
n_sim <- 1000
n_int <- 2  # Number of interventions

# Effects matrix (QALYs)
effects <- matrix(
  c(rnorm(n_sim, 4.5, 0.5),   # Comparator
    rnorm(n_sim, 5.2, 0.6)),  # Intervention
  nrow = n_sim, ncol = n_int
)

# Costs matrix
costs <- matrix(
  c(rnorm(n_sim, 8000, 1500),   # Comparator
    rnorm(n_sim, 15000, 3000)), # Intervention
  nrow = n_sim, ncol = n_int
)

colnames(effects) <- colnames(costs) <- c("Comparator", "Intervention")

# Create BCEA object
bcea_result <- bcea(
  e = effects,
  c = costs,
  ref = 1,                            # Reference intervention
  interventions = c("Comparator", "Intervention"),
  Kmax = 100000                       # Max WTP for analysis
)

# Summary at specific WTP
summary(bcea_result, wtp = 50000)

# Key outputs
bcea_result$ICER                      # ICER
bcea_result$ceac                      # CEAC values
```

### CE Plane and CEAC Plots

```r
library(BCEA)

# Cost-effectiveness plane
ceplane.plot(bcea_result,
             wtp = 50000,
             graph = "ggplot2",
             title = "Cost-Effectiveness Plane")

# Cost-Effectiveness Acceptability Curve (CEAC)
ceac.plot(bcea_result,
          graph = "ggplot2",
          title = "Cost-Effectiveness Acceptability Curve")

# Cost-Effectiveness Acceptability Frontier (CEAF)
ceaf.plot(bcea_result, graph = "ggplot2")

# Expected Incremental Benefit (EIB) plot
eib.plot(bcea_result, graph = "ggplot2")
```

### Multiple Interventions

```r
library(BCEA)

# Three interventions
effects_3 <- matrix(
  c(rnorm(n_sim, 4.0, 0.4),   # Standard care
    rnorm(n_sim, 4.8, 0.5),   # Treatment A
    rnorm(n_sim, 5.5, 0.6)),  # Treatment B
  nrow = n_sim
)

costs_3 <- matrix(
  c(rnorm(n_sim, 5000, 1000),
    rnorm(n_sim, 12000, 2500),
    rnorm(n_sim, 20000, 4000)),
  nrow = n_sim
)

colnames(effects_3) <- colnames(costs_3) <- c("Standard", "Treatment_A", "Treatment_B")

bcea_multi <- bcea(
  e = effects_3,
  c = costs_3,
  ref = 1,
  interventions = colnames(effects_3)
)

# Multi-comparison CEAC
mce <- multi.ce(bcea_multi)
ceac.plot(mce, graph = "ggplot2")

# Contour plot
contour2(bcea_multi, wtp = 50000)
```

## Markov Cohort Models

### Using heemod Package

```r
library(heemod)

# Define transition probabilities
mat_trans <- define_transition(
  state_names = c("Healthy", "Sick", "Dead"),
  # From Healthy
  C, 0.15, 0.01,
  # From Sick
  0.10, C, 0.05,
  # From Dead (absorbing)
  0, 0, 1
)

# Define states with costs and utilities
state_healthy <- define_state(
  cost = 0,
  utility = 1
)

state_sick <- define_state(
  cost = 5000,
  utility = 0.7
)

state_dead <- define_state(
  cost = 0,
  utility = 0
)

# Define strategy (no treatment)
strat_base <- define_strategy(
  transition = mat_trans,
  Healthy = state_healthy,
  Sick = state_sick,
  Dead = state_dead
)

# Run the model
result_base <- run_model(
  strat_base,
  cycles = 50,
  cost = cost,
  effect = utility,
  init = c(1000, 0, 0),     # Initial cohort distribution
  method = "beginning"       # Cycle correction
)

# Summary
summary(result_base)
plot(result_base)
```

### Comparing Strategies

```r
library(heemod)

# Define treatment strategy (reduced transition to sick)
mat_trans_trt <- define_transition(
  state_names = c("Healthy", "Sick", "Dead"),
  C, 0.10, 0.01,     # Lower transition to sick
  0.15, C, 0.04,     # Higher recovery
  0, 0, 1
)

state_healthy_trt <- define_state(
  cost = 500,        # Treatment cost
  utility = 1
)

strat_trt <- define_strategy(
  transition = mat_trans_trt,
  Healthy = state_healthy_trt,
  Sick = state_sick,
  Dead = state_dead
)

# Run both strategies
result_comp <- run_model(
  base = strat_base,
  treatment = strat_trt,
  cycles = 50,
  cost = cost,
  effect = utility,
  init = c(1000, 0, 0)
)

# Summary comparison
summary(result_comp)

# ICER
icer_result <- summary(result_comp)$res_comp
print(icer_result)
```

### Time-Dependent Parameters

```r
library(heemod)

# Parameters that change over time
param <- define_parameters(
  age_init = 50,
  age = age_init + model_time,
  mortality = 1 - exp(-0.0001 * age^2),  # Age-dependent mortality
  p_sick = 0.1 + 0.005 * model_time       # Increasing disease risk
)

# Transition matrix with parameters
mat_time <- define_transition(
  state_names = c("Healthy", "Sick", "Dead"),
  C, p_sick, mortality,
  0.05, C, mortality * 1.5,
  0, 0, 1
)

# Run with parameters
result_time <- run_model(
  define_strategy(
    transition = mat_time,
    Healthy = state_healthy,
    Sick = state_sick,
    Dead = state_dead
  ),
  cycles = 30,
  cost = cost,
  effect = utility,
  init = c(1000, 0, 0),
  parameters = param
)
```

## Partitioned Survival Analysis

### Using hesim Package

```r
library(hesim)
library(flexsurv)

# Fit parametric survival models for each health state
# Overall Survival (OS)
fit_os <- flexsurvreg(
  Surv(time, status) ~ treatment,
  data = surv_data,
  dist = "weibull"
)

# Progression-Free Survival (PFS)
fit_pfs <- flexsurvreg(
  Surv(time_pfs, status_pfs) ~ treatment,
  data = surv_data,
  dist = "weibull"
)

# State probabilities from survival curves
# Pre-progression: S_PFS(t)
# Post-progression: S_OS(t) - S_PFS(t)
# Death: 1 - S_OS(t)
```

### Building PSM with hesim

```r
library(hesim)

# Treatment strategies
strategies <- data.table(
  strategy_id = 1:2,
  strategy_name = c("Standard", "New Treatment")
)

# Patients (can include heterogeneity)
patients <- data.table(
  patient_id = 1:100,
  age = rnorm(100, 60, 10)
)

# Health states
states <- data.table(
  state_id = 1:3,
  state_name = c("Stable", "Progressed", "Dead")
)

# Create hesim data object
hesim_data <- hesim_data(
  strategies = strategies,
  patients = patients,
  states = states
)

# Define input data for survival models
input_data <- expand(hesim_data, by = c("strategies", "patients"))

# Create survival curves (from fitted models)
survmods <- create_PsmCurves(
  input_data = input_data,
  params = params_surv_list  # From fitted flexsurv models
)

# State probabilities
stprobs <- survmods$sim_stateprobs(t = seq(0, 10, 0.1))
```

### Costs and QALYs from PSM

```r
library(hesim)

# State utilities
utility_tbl <- stateval_tbl(
  data.table(
    state_id = 1:3,
    est = c(0.8, 0.6, 0)  # Utilities by state
  ),
  dist = "fixed"
)

# State costs
cost_tbl <- stateval_tbl(
  data.table(
    state_id = 1:3,
    est = c(1000, 5000, 0)  # Annual costs
  ),
  dist = "fixed"
)

# Create PSM object
psm <- Psm$new(
  survival_models = survmods,
  utility_model = utility_tbl,
  cost_models = list(drug = cost_tbl)
)

# Simulate QALYs and costs
psm$sim_stateprobs(t = seq(0, 10, by = 0.1))
psm$sim_qalys(dr = 0.03)  # 3% discount rate
psm$sim_costs(dr = 0.03)

# Summarize
ce_results <- psm$summarize()
```

## Probabilistic Sensitivity Analysis

### Parameter Distributions

```r
library(heemod)

# Define parameter distributions
param_psa <- define_parameters(
  # Beta distribution for probabilities
  p_sick = rbeta(1, shape1 = 20, shape2 = 80),
  p_death_healthy = rbeta(1, shape1 = 2, shape2 = 198),
  p_death_sick = rbeta(1, shape1 = 10, shape2 = 90),

  # Gamma distribution for costs
  cost_sick = rgamma(1, shape = 100, rate = 0.02),
  cost_treatment = rgamma(1, shape = 50, rate = 0.1),

  # Beta distribution for utilities
  utility_sick = rbeta(1, shape1 = 70, shape2 = 30)
)

# Run PSA
psa_result <- run_psa(
  model = result_comp,
  psa = param_psa,
  N = 1000  # Number of simulations
)

# Summary
summary(psa_result)

# CE plane from PSA
plot(psa_result, type = "ce")

# CEAC from PSA
plot(psa_result, type = "ac")
```

### Custom PSA Implementation

```r
# Manual PSA loop
n_sim <- 1000
psa_results <- data.frame(
  sim = 1:n_sim,
  cost_base = NA,
  cost_trt = NA,
  qaly_base = NA,
  qaly_trt = NA
)

for (i in 1:n_sim) {
  # Sample parameters
  p_sick <- rbeta(1, 20, 80)
  cost_sick <- rgamma(1, 100, 0.02)
  utility_sick <- rbeta(1, 70, 30)

  # Run model with sampled parameters
  # ... model calculations ...

  # Store results
  psa_results$cost_base[i] <- sum_cost_base
  psa_results$cost_trt[i] <- sum_cost_trt
  psa_results$qaly_base[i] <- sum_qaly_base
  psa_results$qaly_trt[i] <- sum_qaly_trt
}

# Incremental results
psa_results <- psa_results |>
  mutate(
    delta_cost = cost_trt - cost_base,
    delta_qaly = qaly_trt - qaly_base,
    icer = delta_cost / delta_qaly
  )

# CEAC calculation
wtp_range <- seq(0, 100000, 1000)
ceac <- sapply(wtp_range, function(k) {
  mean(psa_results$delta_qaly * k - psa_results$delta_cost > 0)
})

# Plot CEAC
plot(wtp_range, ceac, type = "l",
     xlab = "Willingness-to-Pay ($/QALY)",
     ylab = "Probability Cost-Effective",
     main = "Cost-Effectiveness Acceptability Curve")
```

## Value of Information Analysis

### Expected Value of Perfect Information (EVPI)

```r
library(BCEA)

# EVPI from BCEA object
evpi_result <- evpi(bcea_result)

# Plot EVPI
evi.plot(bcea_result, graph = "ggplot2")

# EVPI at specific WTP
evpi_50k <- evpi_result[evpi_result$k == 50000, "evpi"]
cat("EVPI at $50,000/QALY:", round(evpi_50k, 0), "\n")

# Population EVPI
pop_size <- 100000           # Affected population
time_horizon <- 10           # Years of technology relevance
discount_rate <- 0.03        # Annual discount rate

# Annuity factor
annuity <- (1 - (1 + discount_rate)^(-time_horizon)) / discount_rate

pop_evpi <- evpi_50k * pop_size * annuity
cat("Population EVPI:", round(pop_evpi / 1e6, 2), "million\n")
```

### Expected Value of Partial Perfect Information (EVPPI)

```r
library(BCEA)

# EVPPI for specific parameters
# Requires PSA parameter matrix
psa_params <- data.frame(
  p_sick = rbeta(n_sim, 20, 80),
  cost_sick = rgamma(n_sim, 100, 0.02),
  utility_sick = rbeta(n_sim, 70, 30)
)

# EVPPI for p_sick
evppi_result <- evppi(
  bcea_result,
  param_idx = "p_sick",
  input = psa_params,
  method = "gam"
)

# Plot
plot(evppi_result, graph = "ggplot2")

# EVPPI for multiple parameters
evppi_multi <- evppi(
  bcea_result,
  param_idx = c("p_sick", "cost_sick"),
  input = psa_params
)
```

## Budget Impact Analysis

### Basic Budget Impact Model

```r
# Population and market share assumptions
pop_eligible <- 50000        # Eligible patient population
uptake_year1 <- 0.10
uptake_year2 <- 0.25
uptake_year3 <- 0.40
uptake_year4 <- 0.50
uptake_year5 <- 0.55

uptake <- c(uptake_year1, uptake_year2, uptake_year3, uptake_year4, uptake_year5)

# Annual treatment costs
cost_current <- 8000
cost_new <- 15000

# Budget impact calculation
budget_impact <- data.frame(
  Year = 1:5,
  Uptake = uptake,
  Patients_New = pop_eligible * uptake,
  Patients_Current = pop_eligible * (1 - uptake),
  Cost_New = pop_eligible * uptake * cost_new,
  Cost_Current = pop_eligible * (1 - uptake) * cost_current,
  Cost_Reference = pop_eligible * cost_current
)

budget_impact <- budget_impact |>
  mutate(
    Total_Cost = Cost_New + Cost_Current,
    Budget_Impact = Total_Cost - Cost_Reference
  )

# Summary
print(budget_impact)

# Total 5-year budget impact
total_impact <- sum(budget_impact$Budget_Impact)
cat("Total 5-year budget impact:", round(total_impact / 1e6, 2), "million\n")
```

### Budget Impact Visualization

```r
library(ggplot2)
library(tidyr)

# Reshape for plotting
bi_long <- budget_impact |>
  select(Year, Cost_New, Cost_Current, Cost_Reference) |>
  pivot_longer(
    cols = -Year,
    names_to = "Category",
    values_to = "Cost"
  )

# Stacked bar chart
ggplot(bi_long |> filter(Category != "Cost_Reference"),
       aes(x = factor(Year), y = Cost / 1e6, fill = Category)) +
  geom_bar(stat = "identity") +
  geom_line(data = bi_long |> filter(Category == "Cost_Reference"),
            aes(y = Cost / 1e6, group = 1), linetype = "dashed", size = 1) +
  labs(x = "Year", y = "Cost ($ millions)",
       title = "Budget Impact Analysis",
       fill = "Treatment") +
  scale_fill_brewer(palette = "Set2") +
  theme_bw()
```

## Decision Trees

### Using dampack Package

```r
library(dampack)

# Define decision tree parameters
params <- list(
  p_disease = 0.10,          # Probability of disease
  p_cure_trt = 0.80,         # Cure probability with treatment
  p_cure_notrt = 0.50,       # Cure probability without treatment
  c_test = 100,              # Cost of diagnostic test
  c_treatment = 5000,        # Cost of treatment
  c_disease = 20000,         # Cost of disease (if not cured)
  u_healthy = 1.0,           # Utility healthy
  u_disease = 0.60           # Utility with disease
)

# Strategy 1: Treat all
cost_treat_all <- params$c_treatment +
  params$p_disease * (1 - params$p_cure_trt) * params$c_disease
qaly_treat_all <- params$p_disease * (
  params$p_cure_trt * params$u_healthy +
  (1 - params$p_cure_trt) * params$u_disease
) + (1 - params$p_disease) * params$u_healthy

# Strategy 2: Test then treat
cost_test_treat <- params$c_test +
  params$p_disease * (params$c_treatment +
  (1 - params$p_cure_trt) * params$c_disease)

# Calculate all strategies and compare
```

## Discounting

```r
# Discount costs and effects
discount <- function(values, rate, time_points) {
  values / (1 + rate)^time_points
}

# Example: 30-year costs
years <- 0:29
annual_costs <- rep(5000, 30)
discount_rate <- 0.03

# Present value
pv_costs <- sum(discount(annual_costs, discount_rate, years))
cat("Undiscounted total:", sum(annual_costs), "\n")
cat("Present value (3% discount):", round(pv_costs, 0), "\n")

# Differential discounting (costs vs QALYs)
# Some guidelines recommend different rates
discount_costs <- 0.03
discount_qalys <- 0.015

pv_costs <- sum(discount(annual_costs, discount_costs, years))
pv_qalys <- sum(discount(annual_qalys, discount_qalys, years))
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| BCEA | Bayesian cost-effectiveness analysis |
| heemod | Markov cohort models for HE |
| hesim | Health economic simulation modeling |
| dampack | Decision-analytic modeling tools |
| survHE | Survival analysis for HE |
| flexsurv | Parametric survival for extrapolation |
| CEAutil | CEA utility functions |
| valueEQ5D | EQ-5D utility mapping |

## Best Practices

1. **Model structure**: Match model type to disease natural history
2. **Time horizon**: Sufficient to capture all relevant costs and effects
3. **Discounting**: Apply recommended rates (often 3% for both costs and effects)
4. **Uncertainty**: Always conduct PSA and report CIs/CrIs
5. **Transparency**: Document all assumptions and data sources
6. **Validation**: Internal consistency checks and external validation
7. **Reporting**: Follow CHEERS checklist for publications
8. **Perspective**: Clearly state healthcare payer vs societal perspective
