# Diagnostic Accuracy Analysis in R

## Overview

Comprehensive diagnostic test accuracy analysis covering ROC curve analysis, optimal cutpoint determination, sensitivity and specificity estimation, likelihood ratios, decision curve analysis, inter-rater reliability measures, and diagnostic meta-analysis.

## Basic Diagnostic Measures

### 2x2 Table Analysis

```r
library(epiR)

# Create 2x2 table
# Format: [TP, FN; FP, TN]
diag_table <- matrix(c(85, 15,   # Disease+ (TP, FN)
                       20, 180), # Disease- (FP, TN)
                     nrow = 2, byrow = TRUE,
                     dimnames = list(
                       Test = c("Positive", "Negative"),
                       Disease = c("Present", "Absent")
                     ))

# Calculate diagnostic measures
results <- epi.tests(as.table(diag_table), method = "exact")
print(results)

# Extract specific measures
results$detail  # All measures with CIs
# Includes: Se, Sp, PPV, NPV, LR+, LR-, DOR, accuracy, prevalence
```

### Manual Calculations

```r
# From confusion matrix elements
TP <- 85; FN <- 15; FP <- 20; TN <- 180

# Sensitivity (True Positive Rate)
sensitivity <- TP / (TP + FN)

# Specificity (True Negative Rate)
specificity <- TN / (TN + FP)

# Positive Predictive Value
ppv <- TP / (TP + FP)

# Negative Predictive Value
npv <- TN / (TN + FN)

# Positive Likelihood Ratio
lr_pos <- sensitivity / (1 - specificity)

# Negative Likelihood Ratio
lr_neg <- (1 - sensitivity) / specificity

# Diagnostic Odds Ratio
dor <- (TP * TN) / (FP * FN)

# Youden's Index (J)
youden <- sensitivity + specificity - 1

# Accuracy
accuracy <- (TP + TN) / (TP + TN + FP + FN)

# Wilson confidence intervals
library(binom)
se_ci <- binom.confint(TP, TP + FN, method = "wilson")
sp_ci <- binom.confint(TN, TN + FP, method = "wilson")
```

## ROC Curve Analysis

### Basic ROC Curve

```r
library(pROC)

# Create ROC object
roc_obj <- roc(
  response = df$disease,     # Binary outcome (0/1 or factor)
  predictor = df$biomarker,  # Continuous test value
  levels = c(0, 1),          # Control, case
  direction = "<"            # Lower values = control
)

# Summary
print(roc_obj)

# AUC with confidence interval
auc(roc_obj)
ci.auc(roc_obj, method = "delong")       # DeLong method
ci.auc(roc_obj, method = "bootstrap", boot.n = 2000)  # Bootstrap
```

### ROC Curve Plotting

```r
library(pROC)

# Basic plot
plot(roc_obj, print.auc = TRUE, print.thres = TRUE)

# ggplot2-based ROC curve
ggroc(roc_obj) +
  geom_abline(intercept = 1, slope = 1, linetype = "dashed", color = "gray") +
  annotate("text", x = 0.25, y = 0.25,
           label = paste0("AUC = ", round(auc(roc_obj), 3))) +
  theme_bw() +
  labs(x = "Specificity", y = "Sensitivity",
       title = "ROC Curve for Biomarker X")

# Multiple ROC curves
roc1 <- roc(df$disease, df$biomarker1)
roc2 <- roc(df$disease, df$biomarker2)
roc3 <- roc(df$disease, df$biomarker3)

ggroc(list(Biomarker1 = roc1, Biomarker2 = roc2, Biomarker3 = roc3)) +
  geom_abline(intercept = 1, slope = 1, linetype = "dashed") +
  theme_bw() +
  scale_color_brewer(palette = "Set1")
```

### Comparing ROC Curves

```r
library(pROC)

# DeLong test for comparing AUCs
roc_test <- roc.test(roc1, roc2, method = "delong")
print(roc_test)

# Bootstrap comparison
roc_test_boot <- roc.test(roc1, roc2, method = "bootstrap", boot.n = 2000)

# Venkatraman test (for entire curves, not just AUC)
roc_test_venk <- roc.test(roc1, roc2, method = "venkatraman")

# Compare multiple markers
comparison <- data.frame(
  Marker = c("Biomarker1", "Biomarker2", "Biomarker3"),
  AUC = c(auc(roc1), auc(roc2), auc(roc3)),
  CI_Lower = c(ci.auc(roc1)[1], ci.auc(roc2)[1], ci.auc(roc3)[1]),
  CI_Upper = c(ci.auc(roc1)[3], ci.auc(roc2)[3], ci.auc(roc3)[3])
)
```

### Partial AUC

```r
library(pROC)

# Partial AUC for high specificity region (Sp > 0.9)
pauc_spec <- auc(roc_obj, partial.auc = c(1, 0.9),
                 partial.auc.focus = "specificity")

# Partial AUC for high sensitivity region (Se > 0.9)
pauc_sens <- auc(roc_obj, partial.auc = c(0.9, 1),
                 partial.auc.focus = "sensitivity")

# Standardized partial AUC (McClish correction)
pauc_std <- auc(roc_obj, partial.auc = c(1, 0.9),
                partial.auc.focus = "specificity",
                partial.auc.correct = TRUE)

# CI for partial AUC
ci.auc(roc_obj, partial.auc = c(1, 0.9),
       partial.auc.focus = "specificity")
```

## Optimal Cutpoint Selection

### Using cutpointr Package

```r
library(cutpointr)

# Youden's Index (maximize Se + Sp - 1)
cp_youden <- cutpointr(
  data = df,
  x = biomarker,
  class = disease,
  method = maximize_metric,
  metric = youden
)
summary(cp_youden)
plot(cp_youden)

# Maximize sensitivity with specificity >= 0.9
cp_constrained <- cutpointr(
  df, biomarker, disease,
  method = maximize_metric,
  metric = sensitivity,
  tol_metric = specificity,
  tol_threshold = 0.9
)

# Cost-based optimization
cp_cost <- cutpointr(
  df, biomarker, disease,
  method = minimize_metric,
  metric = misclassification_cost,
  cost_fp = 1,    # Cost of false positive
  cost_fn = 5     # Cost of false negative (5x higher)
)

# Multiple optimal cutpoints
cp_multi <- multi_cutpointr(
  df, biomarker, disease,
  method = maximize_metric,
  metric = youden,
  boot_cut = 1000
)
```

### Using OptimalCutpoints Package

```r
library(OptimalCutpoints)

# Multiple methods simultaneously
opt_cut <- optimal.cutpoints(
  X = "biomarker",
  status = "disease",
  methods = c("Youden", "MaxSpSe", "MaxProdSpSe", "ROC01",
              "MinValueSp", "MinValueSe", "MaxEfficiency"),
  data = df,
  tag.healthy = 0
)

summary(opt_cut)

# Cost-benefit method
opt_cost <- optimal.cutpoints(
  X = "biomarker",
  status = "disease",
  methods = "CB",
  data = df,
  tag.healthy = 0,
  costs.ratio = 5,        # FN cost / FP cost
  prevalence = 0.10       # Disease prevalence
)
```

### Manual Cutpoint Selection

```r
library(pROC)

# Youden's optimal threshold
coords_youden <- coords(roc_obj, "best", best.method = "youden")
print(coords_youden)

# Closest to (0,1) corner
coords_closest <- coords(roc_obj, "best", best.method = "closest.topleft")

# At specific sensitivity/specificity
coords_se90 <- coords(roc_obj, x = 0.90, input = "sensitivity",
                      ret = c("threshold", "sensitivity", "specificity"))

# All coordinates
all_coords <- coords(roc_obj, x = "all",
                     ret = c("threshold", "sensitivity", "specificity",
                             "ppv", "npv", "accuracy"))
```

## Decision Curve Analysis

### Using dcurves Package

```r
library(dcurves)

# Fit prediction models
model1 <- glm(cancer ~ age + psa, data = df, family = binomial)
model2 <- glm(cancer ~ age + psa + dre, data = df, family = binomial)

df$pred1 <- predict(model1, type = "response")
df$pred2 <- predict(model2, type = "response")

# Decision curve analysis
dca_result <- dca(
  cancer ~ pred1 + pred2,
  data = df,
  thresholds = seq(0, 0.5, by = 0.01),
  label = list(pred1 = "PSA Model", pred2 = "PSA + DRE Model")
)

# Plot decision curves
plot(dca_result)

# Customized plot
plot(dca_result, smooth = TRUE) +
  ggplot2::coord_cartesian(ylim = c(-0.05, 0.2)) +
  ggplot2::labs(x = "Threshold Probability",
                y = "Net Benefit",
                title = "Decision Curve Analysis")
```

### Net Benefit Calculation

```r
library(dcurves)

# Extract net benefit at specific threshold
nb_data <- as_tibble(dca_result)

# Net interventions avoided
net_intervention_avoided(dca_result)

# Standardized net benefit
standardized_net_benefit <- function(nb, prevalence, threshold) {
  max_nb <- prevalence - (1 - prevalence) * threshold / (1 - threshold)
  nb / max_nb
}
```

### Clinical Utility Visualization

```r
library(dcurves)

# Clinical impact plot
dca_result |>
  plot(type = "clinical_impact")

# Net benefit with confidence intervals (bootstrap)
dca_boot <- dca(
  cancer ~ pred1,
  data = df,
  thresholds = seq(0, 0.5, by = 0.05)
)
```

## Inter-Rater Reliability

### Cohen's Kappa (Two Raters)

```r
library(irr)

# Two raters, categorical data
ratings <- data.frame(
  rater1 = c(1, 2, 3, 1, 2, 3, 1, 2, 3, 1),
  rater2 = c(1, 2, 3, 1, 2, 2, 1, 3, 3, 2)
)

# Unweighted kappa (nominal categories)
kappa_unweighted <- kappa2(ratings, weight = "unweighted")
print(kappa_unweighted)

# Linear weighted kappa (ordinal categories)
kappa_linear <- kappa2(ratings, weight = "equal")

# Quadratic weighted kappa
kappa_quadratic <- kappa2(ratings, weight = "squared")

# Interpretation:
# < 0.20: Poor
# 0.21-0.40: Fair
# 0.41-0.60: Moderate
# 0.61-0.80: Substantial
# 0.81-1.00: Almost perfect
```

### Fleiss' Kappa (Multiple Raters)

```r
library(irr)

# Multiple raters (each row = subject, each column = rater)
ratings_multi <- matrix(c(
  1, 1, 1, 2,
  2, 2, 2, 2,
  3, 3, 2, 3,
  1, 1, 1, 1,
  2, 3, 2, 2
), nrow = 5, byrow = TRUE)

# Fleiss' kappa
fleiss_k <- kappam.fleiss(ratings_multi)
print(fleiss_k)

# Light's kappa (average of all pairwise kappas)
light_k <- kappam.light(ratings_multi)
```

### Intraclass Correlation Coefficient (ICC)

```r
library(irr)

# Continuous measurements
measurements <- data.frame(
  rater1 = c(2.5, 3.1, 4.2, 2.8, 3.5),
  rater2 = c(2.4, 3.3, 4.0, 2.9, 3.4),
  rater3 = c(2.6, 3.0, 4.1, 2.7, 3.6)
)

# ICC types:
# ICC(1,1): Single rater, absolute agreement
# ICC(2,1): Single rater, consistency
# ICC(3,1): Single rater, consistency (fixed raters)
# ICC(1,k): Average of k raters, absolute agreement
# ICC(2,k): Average of k raters, consistency
# ICC(3,k): Average of k raters, consistency (fixed raters)

# Two-way random effects, single measures, absolute agreement
icc_result <- icc(measurements, model = "twoway", type = "agreement", unit = "single")
print(icc_result)

# Two-way mixed effects, average measures, consistency
icc_avg <- icc(measurements, model = "twoway", type = "consistency", unit = "average")
```

### Agreement for Continuous Data

```r
library(BlandAltmanLeh)

# Bland-Altman analysis
ba <- bland.altman.stats(
  method1 = df$measurement1,
  method2 = df$measurement2
)

# Bland-Altman plot
bland.altman.plot(
  method1 = df$measurement1,
  method2 = df$measurement2,
  main = "Bland-Altman Plot",
  xlab = "Mean of Methods",
  ylab = "Difference (Method 1 - Method 2)"
)

# Limits of agreement
ba$mean.diffs        # Mean difference (bias)
ba$lower.limit       # Lower limit of agreement
ba$upper.limit       # Upper limit of agreement

# Using ggplot2
library(ggplot2)
df_ba <- data.frame(
  mean = (df$method1 + df$method2) / 2,
  diff = df$method1 - df$method2
)

ggplot(df_ba, aes(x = mean, y = diff)) +
  geom_point() +
  geom_hline(yintercept = mean(df_ba$diff), color = "blue") +
  geom_hline(yintercept = mean(df_ba$diff) + 1.96 * sd(df_ba$diff),
             linetype = "dashed", color = "red") +
  geom_hline(yintercept = mean(df_ba$diff) - 1.96 * sd(df_ba$diff),
             linetype = "dashed", color = "red") +
  labs(title = "Bland-Altman Plot",
       x = "Mean of Two Methods",
       y = "Difference Between Methods") +
  theme_bw()
```

## Diagnostic Meta-Analysis

### Bivariate Model

```r
library(mada)

# Data format: TP, FN, FP, TN for each study
diag_ma_data <- data.frame(
  study = paste("Study", 1:10),
  TP = c(45, 38, 52, 41, 55, 48, 39, 44, 50, 47),
  FN = c(5, 7, 8, 9, 5, 7, 11, 6, 5, 8),
  FP = c(8, 12, 10, 15, 7, 11, 14, 9, 12, 10),
  TN = c(142, 143, 130, 135, 133, 134, 136, 141, 133, 135)
)

# Bivariate random effects model (Reitsma)
fit <- reitsma(diag_ma_data)
summary(fit)

# Summary sensitivity and specificity
sens_summary <- plogis(coef(fit)["tsens.(Intercept)"])
spec_summary <- plogis(-coef(fit)["tfpr.(Intercept)"])

# SROC curve
plot(fit, sroclwd = 2, main = "SROC Curve")
points(fit)  # Add study points
```

### HSROC Model

```r
library(mada)

# Hierarchical Summary ROC model
fit_hsroc <- reitsma(diag_ma_data, method = "ml")

# Crosshairs plot
crosshair(fit_hsroc)
```

### Forest Plots for Diagnostic MA

```r
library(mada)

# Forest plot of sensitivity
forest(madad(diag_ma_data), type = "sens",
       main = "Sensitivity by Study")

# Forest plot of specificity
forest(madad(diag_ma_data), type = "spec",
       main = "Specificity by Study")

# Calculate study-level estimates
study_est <- madad(diag_ma_data)
print(study_est)
```

### Publication Bias in Diagnostic MA

```r
library(mada)

# Deeks' funnel plot asymmetry test
deeks_test <- mada:::.deeks(diag_ma_data)

# ROC-based funnel plot
# (visual assessment of publication bias)
```

## Three-Group ROC Analysis

```r
library(DiagTest3Grp)

# Three diagnostic groups (e.g., Normal, Mild, Severe)
# Marker increases with severity

# VUS (Volume Under Surface) - 3D extension of AUC
vus_result <- VUS(
  marker = df$biomarker,
  group = df$severity  # Factor with 3 levels
)
print(vus_result)

# Optimal cutpoints for 3 groups
cut3 <- DiagTest3Grp.optimalCutoff(
  x = df$biomarker,
  group = df$severity
)
```

## Pre-test and Post-test Probability

```r
# Calculate post-test probability using Bayes' theorem

calculate_post_test_prob <- function(pre_test_prob, lr) {
  pre_test_odds <- pre_test_prob / (1 - pre_test_prob)
  post_test_odds <- pre_test_odds * lr
  post_test_prob <- post_test_odds / (1 + post_test_odds)
  return(post_test_prob)
}

# Example: prevalence = 10%, LR+ = 5, LR- = 0.1
pre_test <- 0.10
lr_positive <- 5
lr_negative <- 0.1

# Post-test probability given positive test
post_test_pos <- calculate_post_test_prob(pre_test, lr_positive)
# Post-test probability given negative test
post_test_neg <- calculate_post_test_prob(pre_test, lr_negative)

cat("Pre-test probability:", pre_test, "\n")
cat("Post-test probability (positive test):", round(post_test_pos, 3), "\n")
cat("Post-test probability (negative test):", round(post_test_neg, 3), "\n")
```

## Fagan Nomogram

```r
library(ggplot2)

# Fagan nomogram visualization
fagan_nomogram <- function(pre_test_prob, lr_pos, lr_neg) {
  # Calculate post-test probabilities
  pre_odds <- pre_test_prob / (1 - pre_test_prob)
  post_odds_pos <- pre_odds * lr_pos
  post_odds_neg <- pre_odds * lr_neg
  post_prob_pos <- post_odds_pos / (1 + post_odds_pos)
  post_prob_neg <- post_odds_neg / (1 + post_odds_neg)

  cat("Pre-test probability:", round(pre_test_prob * 100, 1), "%\n")
  cat("LR+:", lr_pos, "-> Post-test probability:", round(post_prob_pos * 100, 1), "%\n")
  cat("LR-:", lr_neg, "-> Post-test probability:", round(post_prob_neg * 100, 1), "%\n")

  return(list(
    pre_test = pre_test_prob,
    post_test_positive = post_prob_pos,
    post_test_negative = post_prob_neg
  ))
}

# Example usage
fagan_nomogram(pre_test_prob = 0.20, lr_pos = 8, lr_neg = 0.15)
```

## Reporting Diagnostic Study Results

```r
# Create comprehensive diagnostic report
create_diagnostic_report <- function(roc_obj, cutpoint, df) {
  # Calculate all measures at optimal cutpoint
  pred_class <- ifelse(df$biomarker >= cutpoint, 1, 0)

  # Confusion matrix
  cm <- table(Predicted = pred_class, Actual = df$disease)
  TP <- cm[2, 2]; FN <- cm[1, 2]
  FP <- cm[2, 1]; TN <- cm[1, 1]

  # Calculate metrics
  metrics <- data.frame(
    Metric = c("AUC", "Cutpoint", "Sensitivity", "Specificity",
               "PPV", "NPV", "LR+", "LR-", "Accuracy", "Youden Index"),
    Value = c(
      round(auc(roc_obj), 3),
      round(cutpoint, 2),
      round(TP / (TP + FN), 3),
      round(TN / (TN + FP), 3),
      round(TP / (TP + FP), 3),
      round(TN / (TN + FN), 3),
      round((TP / (TP + FN)) / (FP / (FP + TN)), 2),
      round((FN / (TP + FN)) / (TN / (FP + TN)), 2),
      round((TP + TN) / (TP + TN + FP + FN), 3),
      round(TP / (TP + FN) + TN / (TN + FP) - 1, 3)
    )
  )

  return(metrics)
}
```

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| pROC | ROC curve analysis and AUC |
| cutpointr | Optimal cutpoint selection |
| OptimalCutpoints | Multiple cutpoint methods |
| dcurves | Decision curve analysis |
| irr | Inter-rater reliability (kappa, ICC) |
| mada | Diagnostic meta-analysis |
| BlandAltmanLeh | Method agreement plots |
| epiR | Diagnostic test evaluation |
| DiagTest3Grp | Three-group ROC analysis |
| caret | Confusion matrix utilities |

## Best Practices

1. **Report multiple metrics**: Sensitivity, specificity, PPV, NPV, and likelihood ratios
2. **Account for prevalence**: PPV/NPV depend heavily on disease prevalence
3. **Use appropriate cutpoint method**: Consider clinical consequences (cost of FN vs FP)
4. **Provide confidence intervals**: Especially for AUC and diagnostic measures
5. **Check calibration**: Predicted probabilities should match observed frequencies
6. **Decision curve analysis**: Evaluates clinical utility across threshold range
7. **Consider spectrum bias**: Ensure representative disease severity range
8. **Report according to STARD**: Standards for Reporting of Diagnostic Accuracy Studies
