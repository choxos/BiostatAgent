# Pharmacokinetics and Pharmacodynamics in R

## Overview

Comprehensive pharmacokinetic (PK) and pharmacodynamic (PD) modeling in R covering non-compartmental analysis (NCA), compartmental PK modeling, population PK with nonlinear mixed effects, bioequivalence assessment, PK/PD modeling, and drug-drug interaction evaluation.

## Non-Compartmental Analysis (NCA)

### Using PKNCA Package

```r
library(PKNCA)

# Prepare concentration data
conc_data <- data.frame(
  subject = rep(1:3, each = 8),
  time = rep(c(0, 0.5, 1, 2, 4, 8, 12, 24), 3),
  concentration = c(
    0, 450, 380, 290, 180, 85, 40, 12,
    0, 520, 410, 320, 200, 95, 45, 15,
    0, 480, 395, 305, 190, 90, 42, 13
  )
)

# Prepare dose data
dose_data <- data.frame(
  subject = 1:3,
  time = 0,
  dose = 100  # mg
)

# Create PKNCA objects
conc_obj <- PKNCAconc(concentration ~ time | subject, data = conc_data)
dose_obj <- PKNCAdose(dose ~ time | subject, data = dose_data)

# Combine into analysis object
data_obj <- PKNCAdata(conc_obj, dose_obj)

# Run NCA
results <- pk.nca(data_obj)

# View results
summary(results)
as.data.frame(results)
```

### Custom NCA Parameters

```r
library(PKNCA)

# Specify intervals and parameters
intervals <- data.frame(
  start = 0,
  end = 24,
  cmax = TRUE,
  tmax = TRUE,
  auclast = TRUE,
  aucinf.obs = TRUE,
  half.life = TRUE,
  cl.obs = TRUE,
  vss.obs = TRUE,
  mrt.last = TRUE
)

# Create analysis with custom intervals
data_obj <- PKNCAdata(
  conc_obj,
  dose_obj,
  intervals = intervals
)

results <- pk.nca(data_obj)

# Extract specific parameters
pk_summary <- summary(results)

# Individual subject parameters
individual_params <- as.data.frame(results) |>
  tidyr::pivot_wider(
    id_cols = subject,
    names_from = PPTESTCD,
    values_from = PPORRES
  )
```

### Manual NCA Calculations

```r
# Basic NCA calculations for a single subject
calculate_nca <- function(time, conc, dose) {

  # Cmax and Tmax
  cmax <- max(conc)
  tmax <- time[which.max(conc)]

  # AUC by linear trapezoidal rule
  auc_last <- sum(diff(time) * (head(conc, -1) + tail(conc, -1)) / 2)

  # Terminal phase (last 3 points for lambda_z)
  n_terminal <- 3
  terminal_idx <- (length(time) - n_terminal + 1):length(time)
  terminal_time <- time[terminal_idx]
  terminal_conc <- conc[terminal_idx]

  # Lambda_z from log-linear regression
  fit <- lm(log(terminal_conc) ~ terminal_time)
  lambda_z <- -coef(fit)[2]

  # Half-life
  half_life <- log(2) / lambda_z

  # AUC extrapolated to infinity
  auc_extrap <- tail(conc, 1) / lambda_z
  auc_inf <- auc_last + auc_extrap

  # Clearance (CL/F for oral)
  cl_f <- dose / auc_inf

  # Volume of distribution (Vd/F)
  vd_f <- cl_f / lambda_z

  # Mean residence time
  # AUMC (first moment)
  aumc <- sum(diff(time) * (head(time * conc, -1) + tail(time * conc, -1)) / 2)
  aumc_extrap <- tail(conc, 1) / lambda_z^2 + tail(time * conc, 1) / lambda_z
  aumc_inf <- aumc + aumc_extrap
  mrt <- aumc_inf / auc_inf

  return(data.frame(
    Cmax = cmax,
    Tmax = tmax,
    AUClast = auc_last,
    AUCinf = auc_inf,
    Lambda_z = lambda_z,
    Half_life = half_life,
    CL_F = cl_f,
    Vd_F = vd_f,
    MRT = mrt
  ))
}
```

## Concentration-Time Visualization

### Spaghetti Plots

```r
library(ggplot2)

# Individual profiles (spaghetti plot)
ggplot(conc_data, aes(x = time, y = concentration, group = subject)) +
  geom_line(alpha = 0.5) +
  geom_point(alpha = 0.5) +
  stat_summary(aes(group = 1), fun = mean, geom = "line",
               color = "red", size = 1.5) +
  stat_summary(aes(group = 1), fun = mean, geom = "point",
               color = "red", size = 2) +
  labs(x = "Time (hours)", y = "Concentration (ng/mL)",
       title = "Concentration-Time Profile") +
  theme_bw()

# Semi-log plot
ggplot(conc_data, aes(x = time, y = concentration, group = subject)) +
  geom_line(alpha = 0.5) +
  geom_point(alpha = 0.5) +
  scale_y_log10() +
  labs(x = "Time (hours)", y = "Concentration (ng/mL) - Log Scale",
       title = "Semi-Logarithmic Concentration-Time Profile") +
  theme_bw()
```
### Summary Plots with Error Bars

```r
library(ggplot2)
library(dplyr)

# Calculate summary statistics
conc_summary <- conc_data |>
  group_by(time) |>
  summarise(
    mean_conc = mean(concentration),
    sd_conc = sd(concentration),
    geom_mean = exp(mean(log(concentration + 0.001))),
    n = n(),
    se_conc = sd_conc / sqrt(n)
  )

# Mean + SD plot
ggplot(conc_summary, aes(x = time, y = mean_conc)) +
  geom_line(size = 1) +
  geom_point(size = 2) +
  geom_errorbar(aes(ymin = mean_conc - sd_conc,
                    ymax = mean_conc + sd_conc),
                width = 0.5) +
  labs(x = "Time (hours)",
       y = "Concentration (ng/mL)",
       title = "Mean (± SD) Concentration-Time Profile") +
  theme_bw()

# Geometric mean plot
ggplot(conc_summary, aes(x = time, y = geom_mean)) +
  geom_line(size = 1) +
  geom_point(size = 2) +
  scale_y_log10() +
  labs(x = "Time (hours)",
       y = "Geometric Mean Concentration (ng/mL)",
       title = "Geometric Mean Concentration Profile") +
  theme_bw()
```

## Compartmental PK with mrgsolve

### One-Compartment Model

```r
library(mrgsolve)

# Define one-compartment model with first-order absorption
code_1cmt <- '
$PARAM CL = 10, V = 100, KA = 1.5

$CMT GUT CENT

$ODE
dxdt_GUT = -KA * GUT;
dxdt_CENT = KA * GUT - (CL/V) * CENT;

$TABLE
double CP = CENT / V;

$CAPTURE CP
'

# Compile model
mod_1cmt <- mcode("pk1cmt", code_1cmt)

# Single dose simulation
out <- mod_1cmt |>
  ev(amt = 100, cmt = 1) |>  # 100 mg oral dose
  mrgsim(end = 24, delta = 0.1)

# Plot
plot(out, CP ~ time)
```

### Two-Compartment Model

```r
library(mrgsolve)

# Two-compartment model with central and peripheral
code_2cmt <- '
$PARAM CL = 10, V1 = 50, V2 = 100, Q = 15, KA = 1.2

$CMT GUT CENT PERIPH

$ODE
double K10 = CL / V1;
double K12 = Q / V1;
double K21 = Q / V2;

dxdt_GUT = -KA * GUT;
dxdt_CENT = KA * GUT - K10 * CENT - K12 * CENT + K21 * PERIPH;
dxdt_PERIPH = K12 * CENT - K21 * PERIPH;

$TABLE
double CP = CENT / V1;

$CAPTURE CP
'

mod_2cmt <- mcode("pk2cmt", code_2cmt)

# Simulate IV bolus
out_iv <- mod_2cmt |>
  ev(amt = 100, cmt = 2) |>  # IV bolus to central
  mrgsim(end = 48, delta = 0.1)

plot(out_iv, CP ~ time, log = TRUE)
```

### Multiple Dosing

```r
library(mrgsolve)

# Multiple dose regimen
dosing_regimen <- ev(
  amt = 100,
  ii = 12,      # Dosing interval (hours)
  addl = 6,     # Additional doses
  cmt = 1       # Oral
)

out_multi <- mod_1cmt |>
  ev(dosing_regimen) |>
  mrgsim(end = 96, delta = 0.1)

plot(out_multi, CP ~ time)

# Steady-state check
out_ss <- mod_1cmt |>
  ev(amt = 100, ii = 12, addl = 100, cmt = 1, ss = 1) |>
  mrgsim(end = 24, delta = 0.1)
```

## Population PK with nlmixr2

### One-Compartment PopPK Model

```r
library(nlmixr2)

# Define population PK model
one_cmt_pop <- function() {
  ini({
    # Fixed effects (thetas)
    tka <- log(1)       # Log Ka
    tcl <- log(10)      # Log CL
    tv <- log(100)      # Log V

    # Random effects (omegas)
    eta.ka ~ 0.6        # IIV on Ka
    eta.cl ~ 0.3        # IIV on CL
    eta.v ~ 0.1         # IIV on V

    # Residual error
    add.err <- 0.1      # Additive
    prop.err <- 0.1     # Proportional
  })
  model({
    # Individual parameters
    ka <- exp(tka + eta.ka)
    cl <- exp(tcl + eta.cl)
    v <- exp(tv + eta.v)

    # Differential equations
    d/dt(depot) <- -ka * depot
    d/dt(central) <- ka * depot - cl/v * central

    # Concentration
    cp <- central / v

    # Combined error model
    cp ~ add(add.err) + prop(prop.err)
  })
}

# Prepare data (nlmixr2 format)
pk_data <- data.frame(
  ID = rep(1:10, each = 8),
  TIME = rep(c(0, 0.5, 1, 2, 4, 8, 12, 24), 10),
  DV = rnorm(80, 100, 20),  # Observed concentrations
  AMT = c(rep(c(100, rep(0, 7)), 10)),
  EVID = c(rep(c(1, rep(0, 7)), 10)),
  CMT = 1
)

# Fit model using SAEM
fit <- nlmixr2(one_cmt_pop, pk_data, est = "saem",
               control = saemControl(print = 50))

# Summary
summary(fit)

# Parameter estimates
fit$parFixed      # Fixed effects
fit$omega         # Random effects variance
fit$sigma         # Residual error

# Individual predictions
fit$ipred
```

### Covariate Model

```r
library(nlmixr2)

# Model with covariates (weight, age)
cov_model <- function() {
  ini({
    tka <- log(1)
    tcl <- log(10)
    tv <- log(100)

    # Covariate effects
    cl_wt <- 0.75       # Allometric on CL
    v_wt <- 1           # Allometric on V

    eta.ka ~ 0.6
    eta.cl ~ 0.3
    eta.v ~ 0.1

    add.err <- 0.1
    prop.err <- 0.1
  })
  model({
    # Covariate-adjusted parameters
    ka <- exp(tka + eta.ka)
    cl <- exp(tcl + eta.cl) * (WT/70)^cl_wt
    v <- exp(tv + eta.v) * (WT/70)^v_wt

    d/dt(depot) <- -ka * depot
    d/dt(central) <- ka * depot - cl/v * central

    cp <- central / v
    cp ~ add(add.err) + prop(prop.err)
  })
}

# Fit with covariates
fit_cov <- nlmixr2(cov_model, pk_data_with_cov, est = "saem")
```

### Model Diagnostics

```r
library(nlmixr2)
library(xpose.nlmixr2)

# Create xpose database
xpdb <- xpose_data_nlmixr2(fit)

# Goodness-of-fit plots
dv_vs_pred(xpdb)           # DV vs PRED
dv_vs_ipred(xpdb)          # DV vs IPRED
res_vs_pred(xpdb)          # CWRES vs PRED
res_vs_idv(xpdb)           # CWRES vs TIME

# Individual plots
ind_plots(xpdb, nrow = 3, ncol = 3)

# VPC (Visual Predictive Check)
vpc_result <- vpc(fit, n = 500)
plot(vpc_result)
```

## Bioequivalence Analysis

### Using BE Package

```r
library(BE)

# 2x2 crossover BE study data
be_data <- data.frame(
  subj = rep(1:24, each = 2),
  seq = rep(rep(c("TR", "RT"), each = 12), each = 2),
  prd = rep(c(1, 2), 24),
  trt = c(rep(c("T", "R"), 12), rep(c("R", "T"), 12)),
  AUClast = rlnorm(48, log(100), 0.3),
  Cmax = rlnorm(48, log(50), 0.3)
)

# BE analysis
be_result <- test2x2(be_data, "AUClast")
print(be_result)

# 90% CI for geometric mean ratio
be_result$ci       # Should be within 80-125%

# Multiple endpoints
be_auc <- test2x2(be_data, "AUClast")
be_cmax <- test2x2(be_data, "Cmax")
```

### Manual BE Calculations

```r
library(nlme)

# ANOVA for 2x2 crossover
be_data$log_auc <- log(be_data$AUClast)

# Linear mixed effects model
fit_be <- lme(
  log_auc ~ seq + prd + trt,
  random = ~1 | subj,
  data = be_data
)

# Treatment effect
trt_effect <- fixef(fit_be)["trtT"]

# 90% CI
se <- sqrt(vcov(fit_be)["trtT", "trtT"])
ci_lower <- exp(trt_effect - qt(0.95, df = 22) * se) * 100
ci_upper <- exp(trt_effect + qt(0.95, df = 22) * se) * 100
gmr <- exp(trt_effect) * 100

cat("GMR (T/R):", round(gmr, 2), "%\n")
cat("90% CI:", round(ci_lower, 2), "-", round(ci_upper, 2), "%\n")

# Bioequivalence conclusion
if (ci_lower >= 80 & ci_upper <= 125) {
  cat("Conclusion: Bioequivalent\n")
} else {
  cat("Conclusion: Not bioequivalent\n")
}
```

### Power and Sample Size for BE

```r
# Sample size calculation for BE study
be_sample_size <- function(cv, gmr = 1, alpha = 0.05, power = 0.80,
                           lower = 0.80, upper = 1.25) {

  # Approximate formula for 2x2 crossover
  se <- sqrt(2) * cv  # Within-subject CV
  delta <- log(gmr)
  theta <- log(upper)

  # Effect size
  z_alpha <- qnorm(1 - alpha)
  z_beta <- qnorm(power)

  # Sample size per sequence
  n <- 2 * ((z_alpha + z_beta) * se / (theta - abs(delta)))^2

  return(ceiling(n) * 2)  # Total subjects
}

# Example: CV = 30%, GMR = 1.0
n_total <- be_sample_size(cv = 0.30, gmr = 1.0)
cat("Required sample size:", n_total, "subjects\n")

# Using PowerTOST package
library(PowerTOST)

# Sample size for 2x2 crossover
sampleN.TOST(
  CV = 0.30,
  theta0 = 0.95,    # Expected GMR
  theta1 = 0.80,    # Lower BE limit
  theta2 = 1.25,    # Upper BE limit
  targetpower = 0.80,
  design = "2x2"
)
```

## PK/PD Modeling

### Emax Model

```r
library(mrgsolve)

# PK/PD with Emax effect
code_pkpd <- '
$PARAM CL = 10, V = 100, KA = 1.5
$PARAM EMAX = 100, EC50 = 50, GAMMA = 1, E0 = 10

$CMT GUT CENT

$ODE
dxdt_GUT = -KA * GUT;
dxdt_CENT = KA * GUT - (CL/V) * CENT;

$TABLE
double CP = CENT / V;
double EFFECT = E0 + EMAX * pow(CP, GAMMA) / (pow(EC50, GAMMA) + pow(CP, GAMMA));

$CAPTURE CP EFFECT
'

mod_pkpd <- mcode("pkpd_emax", code_pkpd)

out_pkpd <- mod_pkpd |>
  ev(amt = 100, cmt = 1) |>
  mrgsim(end = 24, delta = 0.1)

# Plot PK and PD
library(ggplot2)
out_df <- as.data.frame(out_pkpd)

p1 <- ggplot(out_df, aes(time, CP)) +
  geom_line() +
  labs(y = "Concentration", title = "PK")

p2 <- ggplot(out_df, aes(time, EFFECT)) +
  geom_line() +
  labs(y = "Effect", title = "PD")

library(patchwork)
p1 / p2
```

### Indirect Response Models

```r
library(mrgsolve)

# Indirect response model (inhibition of production)
code_indirect <- '
$PARAM CL = 10, V = 100, KA = 1.5
$PARAM KIN = 10, KOUT = 0.1, IC50 = 50, IMAX = 1

$CMT GUT CENT RESP

$MAIN
RESP_0 = KIN / KOUT;  // Baseline response

$ODE
double CP = CENT / V;
double INH = 1 - IMAX * CP / (IC50 + CP);  // Inhibition function

dxdt_GUT = -KA * GUT;
dxdt_CENT = KA * GUT - (CL/V) * CENT;
dxdt_RESP = KIN * INH - KOUT * RESP;

$CAPTURE CP RESP
'

mod_indirect <- mcode("indirect", code_indirect)

out_indirect <- mod_indirect |>
  ev(amt = 100, cmt = 1) |>
  mrgsim(end = 72, delta = 0.1)

plot(out_indirect, RESP ~ time)
```

## Drug-Drug Interaction

### Competitive Inhibition

```r
library(mrgsolve)

# DDI model with competitive inhibition
code_ddi <- '
$PARAM
// Victim drug parameters
CLv = 10, Vv = 100, KAv = 1
// Perpetrator parameters
CLp = 5, Vp = 50, KAp = 0.5
// Interaction parameters
KI = 20, FM = 0.8  // Ki and fraction metabolized by affected pathway

$CMT GUT_V CENT_V GUT_P CENT_P

$ODE
double CPv = CENT_V / Vv;
double CPp = CENT_P / Vp;

// Inhibition factor
double INH = 1 / (1 + CPp / KI);

// Effective clearance
double CL_eff = CLv * (1 - FM + FM * INH);

dxdt_GUT_V = -KAv * GUT_V;
dxdt_CENT_V = KAv * GUT_V - (CL_eff/Vv) * CENT_V;
dxdt_GUT_P = -KAp * GUT_P;
dxdt_CENT_P = KAp * GUT_P - (CLp/Vp) * CENT_P;

$TABLE
double CPvictim = CENT_V / Vv;
double CPperp = CENT_P / Vp;

$CAPTURE CPvictim CPperp
'

mod_ddi <- mcode("ddi", code_ddi)

# Victim alone
out_alone <- mod_ddi |>
  ev(amt = 100, cmt = 1) |>
  mrgsim(end = 24, delta = 0.1)

# Victim + perpetrator
out_ddi <- mod_ddi |>
  ev(amt = 100, cmt = 1, time = 0) |>
  ev(amt = 200, cmt = 3, time = 0) |>
  mrgsim(end = 24, delta = 0.1)

# Calculate AUC ratio (DDI magnitude)
auc_alone <- sum(out_alone$CPvictim) * 0.1
auc_ddi <- sum(out_ddi$CPvictim) * 0.1
auc_ratio <- auc_ddi / auc_alone

cat("AUC ratio (DDI/alone):", round(auc_ratio, 2), "\n")
```

## PK Summary Statistics

```r
# Standard PK parameter summary table
create_pk_summary <- function(pk_params) {
  pk_params |>
    group_by(parameter) |>
    summarise(
      N = n(),
      Mean = mean(value),
      SD = sd(value),
      CV_percent = SD / Mean * 100,
      Median = median(value),
      Min = min(value),
      Max = max(value),
      Geom_Mean = exp(mean(log(value))),
      Geom_CV = sqrt(exp(var(log(value))) - 1) * 100
    ) |>
    mutate(across(where(is.numeric), ~round(., 3)))
}

# Format for regulatory submission
format_pk_table <- function(summary_df) {
  summary_df |>
    mutate(
      `Mean (SD)` = paste0(round(Mean, 2), " (", round(SD, 2), ")"),
      `Median [Min, Max]` = paste0(round(Median, 2), " [",
                                   round(Min, 2), ", ", round(Max, 2), "]"),
      `Geom Mean (Geom CV%)` = paste0(round(Geom_Mean, 2), " (",
                                      round(Geom_CV, 1), "%)")
    ) |>
    select(parameter, N, `Mean (SD)`, `Median [Min, Max]`,
           `Geom Mean (Geom CV%)`)
}
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| PKNCA | Non-compartmental analysis |
| mrgsolve | ODE-based PK/PD simulation |
| nlmixr2 | Population PK modeling (NLME) |
| rxode2 | ODE solver, nlmixr2 backend |
| BE | Bioequivalence analysis |
| PowerTOST | BE sample size and power |
| pk | Classical PK calculations |
| NonCompart | NCA calculations |
| xpose.nlmixr2 | Diagnostic plots for nlmixr2 |
| vpc | Visual predictive checks |

## Best Practices

1. **NCA conventions**: Use linear trapezoidal up/log down for oral dosing
2. **Terminal phase**: Require at least 3 points and R² > 0.9 for lambda_z
3. **Population PK**: Start simple (1-cmt), add complexity as needed
4. **Model qualification**: GOF plots, VPC, bootstrap for parameter uncertainty
5. **BE studies**: Log-transform PK parameters, use ANOVA for crossover
6. **Regulatory**: Follow FDA/EMA guidance for NCA intervals and BE limits
7. **Documentation**: Report software versions, methods, and all assumptions
8. **Covariate selection**: Use stepwise approach with clinical plausibility
