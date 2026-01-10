# Model Evaluation Patterns

## Overview

Comprehensive model evaluation using yardstick and related packages. Covers metrics for classification, regression, and survival outcomes, plus calibration and uncertainty quantification.

## Classification Metrics

### Binary Classification

```r
library(yardstick)

# Hard predictions (class)
predictions |>
  accuracy(truth = outcome, estimate = .pred_class)

predictions |>
  sens(truth = outcome, estimate = .pred_class)  # sensitivity/recall

predictions |>
  spec(truth = outcome, estimate = .pred_class)  # specificity

predictions |>
  ppv(truth = outcome, estimate = .pred_class)   # precision

predictions |>
  npv(truth = outcome, estimate = .pred_class)

predictions |>
  f_meas(truth = outcome, estimate = .pred_class)  # F1 score

predictions |>
  kap(truth = outcome, estimate = .pred_class)  # Cohen's kappa

predictions |>
  mcc(truth = outcome, estimate = .pred_class)  # Matthews correlation
```

### Probability-Based Metrics

```r
# ROC AUC
predictions |>
  roc_auc(truth = outcome, .pred_positive_class)

# PR AUC (better for imbalanced data)
predictions |>
  pr_auc(truth = outcome, .pred_positive_class)

# Brier score
predictions |>
  brier_class(truth = outcome, .pred_positive_class)

# Log loss
predictions |>
  mn_log_loss(truth = outcome, .pred_positive_class)

# Gain capture (lift)
predictions |>
  gain_capture(truth = outcome, .pred_positive_class)
```

### Multi-Class Classification

```r
# Macro-averaged (average across classes)
predictions |>
  accuracy(truth = outcome, estimate = .pred_class)

predictions |>
  f_meas(truth = outcome, estimate = .pred_class, estimator = "macro")

# Micro-averaged (pool then calculate)
predictions |>
  f_meas(truth = outcome, estimate = .pred_class, estimator = "micro")

# Weighted by class prevalence
predictions |>
  f_meas(truth = outcome, estimate = .pred_class, estimator = "macro_weighted")

# Multi-class ROC AUC (one-vs-all)
predictions |>
  roc_auc(truth = outcome, .pred_class1:.pred_classN)
```

### Metric Sets

```r
# Create metric set for consistent evaluation
class_metrics <- metric_set(
  accuracy,
  sens,
  spec,
  ppv,
  f_meas,
  roc_auc
)

# Use in tuning
tune_results <- workflow |>
  tune_grid(
    resamples = cv_folds,
    metrics = class_metrics
  )

# Use on predictions
predictions |>
  class_metrics(truth = outcome, estimate = .pred_class, .pred_positive)
```

## Regression Metrics

### Standard Metrics

```r
# RMSE (penalizes large errors)
predictions |>
  rmse(truth = outcome, estimate = .pred)

# MAE (robust to outliers)
predictions |>
  mae(truth = outcome, estimate = .pred)

# R-squared
predictions |>
  rsq(truth = outcome, estimate = .pred)

# R-squared traditional (can be negative)
predictions |>
  rsq_trad(truth = outcome, estimate = .pred)

# Mean absolute percentage error
predictions |>
  mape(truth = outcome, estimate = .pred)

# Symmetric MAPE
predictions |>
  smape(truth = outcome, estimate = .pred)
```

### Robust and Alternative Metrics

```r
# Huber loss (robust to outliers)
predictions |>
  huber_loss(truth = outcome, estimate = .pred)

# Concordance correlation coefficient
predictions |>
  ccc(truth = outcome, estimate = .pred)

# Index of ideality of correlation
predictions |>
  iic(truth = outcome, estimate = .pred)
```

### Regression Metric Set

```r
reg_metrics <- metric_set(
  rmse,
  mae,
  rsq,
  mape
)

predictions |>
  reg_metrics(truth = outcome, estimate = .pred)
```

## Visualization

### ROC Curves

```r
# Generate ROC curve data
roc_data <- predictions |>
  roc_curve(truth = outcome, .pred_positive)

# Plot
autoplot(roc_data)

# Multiple models
all_predictions |>
  group_by(model) |>
  roc_curve(truth = outcome, .pred_positive) |>
  autoplot()
```

### Precision-Recall Curves

```r
pr_data <- predictions |>
  pr_curve(truth = outcome, .pred_positive)

autoplot(pr_data)
```

### Gain and Lift Curves

```r
# Gain curve
gain_data <- predictions |>
  gain_curve(truth = outcome, .pred_positive)
autoplot(gain_data)

# Lift curve
lift_data <- predictions |>
  lift_curve(truth = outcome, .pred_positive)
autoplot(lift_data)
```

### Calibration Plots

```r
# Calibration data
cal_data <- predictions |>
  cal_plot_breaks(truth = outcome, .pred_positive, num_breaks = 10)

# Plot calibration
autoplot(cal_data)

# Windowed calibration
cal_data <- predictions |>
  cal_plot_windowed(truth = outcome, .pred_positive)
autoplot(cal_data)
```

### Confusion Matrix

```r
# Generate confusion matrix
conf_mat <- predictions |>
  conf_mat(truth = outcome, estimate = .pred_class)

# Visualize
autoplot(conf_mat, type = "heatmap")
autoplot(conf_mat, type = "mosaic")

# Extract metrics from confusion matrix
summary(conf_mat)
```

## Probability Calibration

### Calibration Methods (probably package)

```r
library(probably)

# Logistic calibration (Platt scaling)
cal_obj <- predictions |>
  cal_estimate_logistic(truth = outcome, .pred_positive)

calibrated <- predictions |>
  cal_apply(cal_obj)

# Isotonic regression
cal_obj <- predictions |>
  cal_estimate_isotonic(truth = outcome, .pred_positive)

# Beta calibration
cal_obj <- predictions |>
  cal_estimate_beta(truth = outcome, .pred_positive)
```

### Calibration in Workflow

```r
# Add calibration to workflow
calibrated_wf <- workflow |>
  add_model(model_spec) |>
  add_recipe(recipe) |>
  add_calibration()  # not yet in tidymodels but conceptually
```

## Threshold Optimization

### Finding Optimal Threshold

```r
library(probably)

# Optimize for J-index (sens + spec - 1)
threshold_perf <- predictions |>
  threshold_perf(
    truth = outcome,
    .pred_positive,
    thresholds = seq(0.1, 0.9, by = 0.05),
    metrics = metric_set(j_index, sens, spec)
  )

# Find optimal
best_threshold <- threshold_perf |>
  filter(.metric == "j_index") |>
  slice_max(.estimate)

# Apply threshold
predictions |>
  mutate(.pred_class = make_two_class_pred(.pred_positive, levels(outcome), threshold = 0.4))
```

### Cost-Sensitive Thresholds

```r
# With different misclassification costs
cost_matrix <- matrix(c(0, 1, 5, 0), nrow = 2)  # FN costs 5x FP

predictions |>
  classification_cost(
    truth = outcome,
    .pred_positive,
    costs = cost_matrix
  )
```

## Confidence and Prediction Intervals

### Bootstrap Confidence Intervals

```r
# Bootstrap metric estimates
boot_metrics <- bootstraps(predictions, times = 1000) |>
  mutate(
    metrics = map(splits, ~ {
      analysis(.x) |>
        accuracy(truth = outcome, estimate = .pred_class)
    })
  ) |>
  unnest(metrics)

# Calculate CI
quantile(boot_metrics$.estimate, c(0.025, 0.975))
```

### Prediction Intervals (Conformal)

```r
library(probably)

# Conformal prediction intervals
conf_obj <- predictions |>
  conformal_cv(outcome ~ ., data = train_data, cv_folds)

# Predict with intervals
predict(conf_obj, new_data, level = 0.95)
```

## Model Comparison

### Comparing Resampled Models

```r
# Collect metrics from multiple workflows
wf_results <- workflow_set |>
  workflow_map(resamples = cv_folds)

# Compare
autoplot(wf_results)
rank_results(wf_results, rank_metric = "roc_auc")

# Statistical comparison
# (informally via confidence intervals)
collect_metrics(wf_results) |>
  filter(.metric == "roc_auc") |>
  ggplot(aes(x = wflow_id, y = mean, ymin = mean - std_err, ymax = mean + std_err)) +
  geom_pointrange()
```

### Paired Comparisons

```r
# Resample-level comparison
library(tidyposterior)

# ANOVA-like comparison
perf_mod <- perf_mod(wf_results, metric = "roc_auc")

# Contrasts
contrast_models(perf_mod, list_1 = "model_A", list_2 = "model_B")
```

## Evaluation Best Practices

### Training vs Test Performance

```r
# Collect training CV metrics
train_metrics <- collect_metrics(tune_results)

# Get test metrics
test_metrics <- final_fit |>
  collect_metrics()

# Compare for overfitting
bind_rows(
  train_metrics |> mutate(set = "CV"),
  test_metrics |> mutate(set = "Test")
)
```

### Stratified Evaluation

```r
# Performance by subgroup
predictions |>
  group_by(subgroup) |>
  metrics(truth = outcome, estimate = .pred_class, .pred_positive)
```

### Key Metrics by Problem Type

| Problem | Primary Metric | Secondary Metrics |
|---------|---------------|-------------------|
| Binary balanced | ROC AUC | Accuracy, F1 |
| Binary imbalanced | PR AUC, F1 | Sens, PPV |
| Multi-class | Macro F1 | Accuracy, Kappa |
| Regression | RMSE | MAE, R² |
| Regression with outliers | MAE, Huber | RMSE |
| Rare events | PR AUC | Sens, PPV |
| Medical diagnosis | Sens, Spec | NPV, PPV |
