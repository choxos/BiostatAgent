# Mendelian Randomization in R

## Overview

Mendelian randomization (MR) methods for causal inference using genetic variants as instrumental variables. Covers instrument selection, two-sample MR, sensitivity analyses, pleiotropy assessment, multivariable MR, and advanced methods for robust causal inference.

## Instrument Selection

### Using TwoSampleMR

```r
library(TwoSampleMR)

# Extract instruments from GWAS database
# IEU Open GWAS Project
exposure_dat <- extract_instruments(
  outcomes = "ieu-a-2",      # GWAS ID for exposure
  p1 = 5e-8,                 # Genome-wide significance
  clump = TRUE,              # LD clumping
  r2 = 0.001,                # LD threshold
  kb = 10000                 # Clumping window (kb)
)

# View extracted SNPs
head(exposure_dat)

# Manual instrument selection from summary statistics
exposure_dat <- read_exposure_data(
  filename = "exposure_gwas.txt",
  sep = "\t",
  snp_col = "SNP",
  beta_col = "BETA",
  se_col = "SE",
  effect_allele_col = "A1",
  other_allele_col = "A2",
  pval_col = "P",
  eaf_col = "EAF"
) |>
  filter(pval.exposure < 5e-8)

# Clump instruments
exposure_dat <- clump_data(exposure_dat, clump_r2 = 0.001)
```

### F-statistic Calculation

```r
# F-statistic for instrument strength
# Rule of thumb: F > 10 indicates strong instruments

calculate_f_stat <- function(beta, se, n) {
  r2 <- (beta^2) / (beta^2 + se^2 * n)  # Approximate R²
  k <- 1  # Number of instruments (per SNP)
  f_stat <- (r2 * (n - k - 1)) / ((1 - r2) * k)
  return(f_stat)
}

exposure_dat$f_stat <- with(exposure_dat,
  calculate_f_stat(beta.exposure, se.exposure, samplesize.exposure)
)

# Summary
cat("Mean F-statistic:", mean(exposure_dat$f_stat), "\n")
cat("SNPs with F < 10:", sum(exposure_dat$f_stat < 10), "\n")
```

## Two-Sample MR

### Extract Outcome Data

```r
library(TwoSampleMR)

# Get outcome data for selected SNPs
outcome_dat <- extract_outcome_data(
  snps = exposure_dat$SNP,
  outcomes = "ieu-a-7"       # GWAS ID for outcome
)

# Harmonize exposure and outcome
dat <- harmonise_data(
  exposure_dat = exposure_dat,
  outcome_dat = outcome_dat,
  action = 2                  # Try to infer forward strand
)

# Check harmonization
table(dat$mr_keep)           # SNPs kept after harmonization
```

### Primary MR Methods

```r
library(TwoSampleMR)

# Run multiple MR methods
results <- mr(
  dat,
  method_list = c(
    "mr_ivw",                 # Inverse variance weighted
    "mr_egger_regression",    # MR-Egger
    "mr_weighted_median",     # Weighted median
    "mr_weighted_mode"        # Weighted mode
  )
)

# View results
print(results)

# Generate odds ratios (for binary outcomes)
or_results <- generate_odds_ratios(results)
print(or_results)
```

### Using MendelianRandomization Package

```r
library(MendelianRandomization)

# Create MR input object
mr_input <- mr_input(
  bx = dat$beta.exposure,
  bxse = dat$se.exposure,
  by = dat$beta.outcome,
  byse = dat$se.outcome,
  exposure = "LDL Cholesterol",
  outcome = "Coronary Heart Disease"
)

# IVW method
ivw_result <- mr_ivw(mr_input)
print(ivw_result)

# MR-Egger
egger_result <- mr_egger(mr_input)
print(egger_result)

# Weighted median
median_result <- mr_median(mr_input, weighting = "weighted")
print(median_result)

# All methods
mr_allmethods(mr_input, method = "main")
```

## Sensitivity Analyses

### MR-Egger Intercept Test

```r
library(TwoSampleMR)

# Egger intercept test for directional pleiotropy
pleiotropy <- mr_pleiotropy_test(dat)
print(pleiotropy)

# Interpretation:
# p < 0.05 suggests directional pleiotropy
# Non-zero intercept indicates bias in IVW estimate

library(MendelianRandomization)
egger <- mr_egger(mr_input)
cat("Egger intercept:", egger@Intercept, "\n")
cat("Intercept p-value:", egger@Pvalue.Int, "\n")
```

### Heterogeneity Assessment

```r
library(TwoSampleMR)

# Cochran's Q test for heterogeneity
het <- mr_heterogeneity(dat)
print(het)

# I-squared
het$I2 <- (het$Q - het$Q_df) / het$Q * 100
het$I2[het$I2 < 0] <- 0

# Interpretation:
# Significant Q suggests heterogeneous SNP effects
# May indicate pleiotropy or population stratification
```

### Leave-One-Out Analysis

```r
library(TwoSampleMR)

# Leave-one-out analysis
loo <- mr_leaveoneout(dat)
head(loo)

# Plot
mr_leaveoneout_plot(loo)

# Identify influential SNPs
influential <- loo |>
  filter(abs(b - results$b[results$method == "Inverse variance weighted"]) >
         2 * results$se[results$method == "Inverse variance weighted"])
```

### MR-PRESSO

```r
library(MRPRESSO)

# MR-PRESSO for outlier detection
presso <- mr_presso(
  BetaOutcome = "beta.outcome",
  BetaExposure = "beta.exposure",
  SdOutcome = "se.outcome",
  SdExposure = "se.exposure",
  data = dat,
  OUTLIERtest = TRUE,
  DISTORTIONtest = TRUE,
  NbDistribution = 1000,
  SignifThreshold = 0.05
)

# Results
presso$`Main MR results`      # Raw and outlier-corrected
presso$`MR-PRESSO results`$`Global Test`$Pvalue  # Global pleiotropy test
presso$`MR-PRESSO results`$`Distortion Test`     # Distortion test
```

### Steiger Filtering

```r
library(TwoSampleMR)

# Test correct causal direction
dat <- steiger_filtering(dat)
table(dat$steiger_dir)       # TRUE = correct direction

# Keep only correctly oriented SNPs
dat_filtered <- dat[dat$steiger_dir == TRUE | is.na(dat$steiger_dir), ]

# Re-run MR
results_filtered <- mr(dat_filtered)
```

## Visualization

### Scatter Plot

```r
library(TwoSampleMR)

# Scatter plot with regression lines
p_scatter <- mr_scatter_plot(results, dat)
print(p_scatter[[1]])

# Customize
p_scatter[[1]] +
  ggplot2::theme_bw() +
  ggplot2::labs(
    title = "MR Scatter Plot",
    x = "SNP effect on exposure",
    y = "SNP effect on outcome"
  )
```

### Forest Plot

```r
library(TwoSampleMR)

# Single SNP forest plot
res_single <- mr_singlesnp(dat)
p_forest <- mr_forest_plot(res_single)
print(p_forest[[1]])
```

### Funnel Plot

```r
library(TwoSampleMR)

# Funnel plot for asymmetry
res_single <- mr_singlesnp(dat)
p_funnel <- mr_funnel_plot(res_single)
print(p_funnel[[1]])

# Asymmetry suggests directional pleiotropy
```

### Radial MR Plot

```r
library(RadialMR)

# Format data for RadialMR
radial_dat <- format_radial(
  BXG = dat$beta.exposure,
  BYG = dat$beta.outcome,
  seBXG = dat$se.exposure,
  seBYG = dat$se.outcome,
  RSID = dat$SNP
)

# IVW radial
ivw_radial <- ivw_radial(radial_dat, alpha = 0.05)
plot_radial(ivw_radial)

# Egger radial
egger_radial <- egger_radial(radial_dat)
plot_radial(egger_radial)
```

## Multivariable MR

```r
library(TwoSampleMR)

# Multiple exposures
exposure_ids <- c("ieu-a-299", "ieu-a-300", "ieu-a-302")  # LDL, HDL, TG

# Extract instruments for each exposure
exposures <- mv_extract_exposures(exposure_ids)

# Get outcome data
outcome_dat <- extract_outcome_data(
  snps = exposures$SNP,
  outcomes = "ieu-a-7"
)

# Harmonize
mvdat <- mv_harmonise_data(exposures, outcome_dat)

# Multivariable MR
mv_results <- mv_multiple(mvdat)
print(mv_results$result)

# Using MendelianRandomization package
library(MendelianRandomization)

# Create multivariable input
mv_input <- mr_mvinput(
  bx = cbind(dat1$beta.exposure, dat2$beta.exposure),
  bxse = cbind(dat1$se.exposure, dat2$se.exposure),
  by = dat1$beta.outcome,
  byse = dat1$se.outcome,
  exposure = c("Exposure 1", "Exposure 2"),
  outcome = "Outcome"
)

# Multivariable IVW
mv_ivw <- mr_mvivw(mv_input)
print(mv_ivw)

# Multivariable MR-Egger
mv_egger <- mr_mvegger(mv_input)
print(mv_egger)
```

## Advanced Methods

### MR-RAPS

```r
library(mr.raps)

# Robust Adjusted Profile Score
raps_result <- mr.raps(
  b_exp = dat$beta.exposure,
  b_out = dat$beta.outcome,
  se_exp = dat$se.exposure,
  se_out = dat$se.outcome,
  over.dispersion = TRUE,
  loss.function = "huber"
)

summary(raps_result)
```

### MR-Lasso

```r
library(MendelianRandomization)

# MR-Lasso for invalid instrument selection
lasso_result <- mr_lasso(mr_input)
print(lasso_result)

# Selected valid instruments
lasso_result@Valid
```

### CAUSE Method

```r
library(cause)

# Format data for CAUSE
X <- gwas_merge(
  exposure_gwas,
  outcome_gwas,
  snp_name_cols = c("SNP", "SNP"),
  beta_hat_cols = c("BETA", "BETA"),
  se_cols = c("SE", "SE"),
  A1_cols = c("A1", "A1"),
  A2_cols = c("A2", "A2")
)

# LD pruning
set.seed(123)
variants <- X |>
  filter(pval_exp < 1e-3) |>
  pull(snp)

# Fit CAUSE
cause_result <- cause(
  X = X,
  variants = variants,
  param_ests = params
)

# Summary
summary(cause_result)
plot(cause_result)
```

### Contamination Mixture Model

```r
library(MendelianRandomization)

# Contamination mixture
conmix <- mr_conmix(mr_input)
print(conmix)

# Plot
mr_plot(conmix)
```

## Bidirectional MR

```r
library(TwoSampleMR)

# Forward direction: X -> Y
forward_results <- mr(dat_forward)

# Reverse direction: Y -> X
# Extract instruments for outcome
outcome_instruments <- extract_instruments("ieu-a-7")

# Get exposure data for outcome SNPs
reverse_exposure <- extract_outcome_data(
  snps = outcome_instruments$SNP,
  outcomes = "ieu-a-2"
)

# Harmonize reverse
dat_reverse <- harmonise_data(outcome_instruments, reverse_exposure)

# Run reverse MR
reverse_results <- mr(dat_reverse)

# Compare directions
comparison <- data.frame(
  Direction = c("X -> Y", "Y -> X"),
  Beta = c(forward_results$b[1], reverse_results$b[1]),
  SE = c(forward_results$se[1], reverse_results$se[1]),
  P = c(forward_results$pval[1], reverse_results$pval[1])
)
print(comparison)
```

## Reporting Results

```r
# Create comprehensive MR report
create_mr_report <- function(dat, results, het, pleiotropy) {

  report <- list(
    n_snps = nrow(dat),
    methods = results |>
      select(method, nsnp, b, se, pval) |>
      mutate(
        or = exp(b),
        ci_lower = exp(b - 1.96 * se),
        ci_upper = exp(b + 1.96 * se)
      ),
    heterogeneity = het,
    pleiotropy = pleiotropy,
    f_statistic = mean(dat$f_stat, na.rm = TRUE)
  )

  return(report)
}

# Generate report
mr_report <- create_mr_report(dat, results, het, pleiotropy)
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| TwoSampleMR | Two-sample MR with GWAS databases |
| MendelianRandomization | Classical MR methods |
| MRPRESSO | Outlier detection and correction |
| mr.raps | Robust adjusted profile score |
| RadialMR | Radial MR plots and analysis |
| cause | Causal Analysis Using Summary Effect |
| MVMR | Multivariable MR |
| MRMix | Mixture model MR |

## Best Practices

1. **Instrument strength**: Ensure F-statistic > 10 for all instruments
2. **Multiple methods**: Report IVW, MR-Egger, weighted median, and MR-PRESSO
3. **Sensitivity analyses**: Always check heterogeneity, pleiotropy, and leave-one-out
4. **Steiger filtering**: Verify causal direction is correct
5. **Visualization**: Include scatter, forest, and funnel plots
6. **Bidirectional**: Consider reverse causation when biologically plausible
7. **Biological plausibility**: Interpret results in biological context
8. **Reporting**: Follow STROBE-MR guidelines
