# Tidymodels Code Review Patterns

## Overview

Anti-pattern detection and best practices for tidymodels workflows based on "Tidy Modeling with R" (TMwR) principles. This skill enables systematic code review for data leakage, resampling violations, workflow issues, evaluation problems, and reproducibility concerns.

## Data Leakage Patterns (CRITICAL)

### DL-001: Recipe Fitted on Test Data

**Severity**: CRITICAL

**Anti-Pattern**:
```r
# WRONG: Fitting recipe on test data
rec <- recipe(outcome ~ ., data = test_data) |>
 prep()

# WRONG: prep() using test data
rec <- recipe(outcome ~ ., data = train_data) |>
  prep(training = test_data)
```

**Correct Pattern**:
```r
# CORRECT: Recipe always prepped on training data only
rec <- recipe(outcome ~ ., data = train_data) |>
  prep(training = train_data)

# BEST: Use workflow (handles automatically)
wf <- workflow() |>
  add_recipe(rec) |>
  add_model(model_spec)

fit <- fit(wf, data = train_data)
```

**Detection**: Look for `prep()` calls with test data or recipes defined on test sets.

---

### DL-002: Preprocessing Before Split

**Severity**: CRITICAL

**Anti-Pattern**:
```r
# WRONG: Normalizing before splitting
df_normalized <- df |>
  mutate(across(where(is.numeric), scale))

split <- initial_split(df_normalized)

# WRONG: Feature selection before split
important_vars <- df |>
  select(where(~cor(.x, df$outcome) > 0.3))

split <- initial_split(important_vars)
```

**Correct Pattern**:
```r
# CORRECT: Split first, then preprocess in recipe
split <- initial_split(df, strata = outcome)
train_data <- training(split)

rec <- recipe(outcome ~ ., data = train_data) |>
  step_normalize(all_numeric_predictors()) |>
  step_corr(all_numeric_predictors(), threshold = 0.9)
```

**Detection**: Any transformations (scale, normalize, mutate) applied before `initial_split()`.

---

### DL-003: Target Encoding Without Cross-Validation

**Severity**: CRITICAL

**Anti-Pattern**:
```r
# WRONG: Target encoding using full dataset statistics
rec <- recipe(outcome ~ ., data = train_data) |>
  step_lencode_mixed(all_nominal_predictors(), outcome = vars(outcome))

# Then prep without proper CV
prepped <- prep(rec)
```

**Correct Pattern**:
```r
# CORRECT: Target encoding within workflow with resampling
rec <- recipe(outcome ~ ., data = train_data) |>
  step_lencode_mixed(all_nominal_predictors(), outcome = vars(outcome))

wf <- workflow() |>
  add_recipe(rec) |>
  add_model(model_spec)

# Encoding computed fresh for each fold
cv_results <- fit_resamples(wf, resamples = vfold_cv(train_data))
```

**Detection**: `step_lencode_*` or `step_embed` used outside workflow with resampling.

---

### DL-004: Feature Selection Using Test Data

**Severity**: CRITICAL

**Anti-Pattern**:
```r
# WRONG: Selecting features based on test correlations
test_cors <- cor(test_data[, -1], test_data$outcome)
selected_vars <- names(test_cors[abs(test_cors) > 0.3])

# WRONG: Using test data for variable importance
importance <- varImp(model, data = test_data)
```

**Correct Pattern**:
```r
# CORRECT: Feature selection in recipe (computed on training only)
rec <- recipe(outcome ~ ., data = train_data) |>
  step_select_vip(all_predictors(), outcome = "outcome", threshold = 0.8)

# CORRECT: Or use recursive feature elimination with CV
rfe_results <- rfe_fit(
  wf,
  resamples = vfold_cv(train_data),
  sizes = c(5, 10, 15, 20)
)
```

**Detection**: Variable selection operations referencing test data.

---

### DL-005: prep() Called Before initial_split()

**Severity**: CRITICAL

**Anti-Pattern**:
```r
# WRONG: Prepping recipe on full data before split
full_rec <- recipe(outcome ~ ., data = full_data) |>
  step_normalize(all_numeric_predictors()) |>
  prep()

# Then splitting
split <- initial_split(full_data)
```

**Correct Pattern**:
```r
# CORRECT: Always split first
split <- initial_split(full_data, strata = outcome)
train_data <- training(split)

rec <- recipe(outcome ~ ., data = train_data) |>
  step_normalize(all_numeric_predictors())
# Don't prep manually - let workflow handle it
```

**Detection**: Sequence analysis - `prep()` appearing before `initial_split()`.

---

## Resampling Violations (MAJOR/CRITICAL)

### RS-001: Missing Stratified Sampling

**Severity**: MAJOR (CRITICAL for imbalanced data)

**Anti-Pattern**:
```r
# WRONG: No stratification for imbalanced outcome
split <- initial_split(df)  # outcome is 95%/5% imbalanced

# WRONG: Unstratified CV
folds <- vfold_cv(train_data, v = 10)
```

**Correct Pattern**:
```r
# CORRECT: Stratify by outcome
split <- initial_split(df, strata = outcome)

# CORRECT: Stratified CV
folds <- vfold_cv(train_data, v = 10, strata = outcome)

# CORRECT: For continuous outcomes, stratify by bins
split <- initial_split(df, strata = outcome, breaks = 4)
```

**Detection**: Missing `strata =` argument with classification outcomes or highly skewed continuous outcomes.

---

### RS-002: Evaluating Model on Training Data

**Severity**: CRITICAL

**Anti-Pattern**:
```r
# WRONG: Predictions on training data for evaluation
fit <- fit(wf, data = train_data)
preds <- predict(fit, train_data)
metrics <- yardstick::metrics(preds, truth = outcome, estimate = .pred)
```

**Correct Pattern**:
```r
# CORRECT: Evaluate on held-out test data
fit <- fit(wf, data = train_data)
preds <- predict(fit, test_data)
metrics <- yardstick::metrics(
  bind_cols(test_data, preds),
  truth = outcome,
  estimate = .pred
)

# BEST: Use resampling for robust estimates
cv_results <- fit_resamples(wf, resamples = folds)
collect_metrics(cv_results)
```

**Detection**: `predict()` and metrics computed on same data used for `fit()`.

---

### RS-003: Tuning Without Nested Cross-Validation

**Severity**: MAJOR

**Anti-Pattern**:
```r
# WRONG: Tune on same folds used for final evaluation
folds <- vfold_cv(train_data)

tune_results <- tune_grid(wf, resamples = folds)
best_params <- select_best(tune_results)

# Using same folds for "final" evaluation
final_wf <- finalize_workflow(wf, best_params)
fit_resamples(final_wf, resamples = folds)  # Overly optimistic!
```

**Correct Pattern**:
```r
# CORRECT: Nested CV or separate test set
# Option 1: Hold out test set for final evaluation
split <- initial_split(df, strata = outcome)
train_data <- training(split)
test_data <- testing(split)

inner_folds <- vfold_cv(train_data, strata = outcome)
tune_results <- tune_grid(wf, resamples = inner_folds)

# Final evaluation on untouched test set
final_fit <- fit(finalize_workflow(wf, select_best(tune_results)), train_data)
predict(final_fit, test_data)

# Option 2: Nested CV
outer_folds <- nested_cv(train_data, outside = vfold_cv(v = 5), inside = vfold_cv(v = 5))
```

**Detection**: Same resampling object used for both tuning and final evaluation.

---

### RS-004: Missing Random Seeds

**Severity**: MAJOR

**Anti-Pattern**:
```r
# WRONG: No seed before random operations
split <- initial_split(df)  # Non-reproducible

folds <- vfold_cv(train_data)  # Different each run

boot <- bootstraps(train_data)  # Non-reproducible
```

**Correct Pattern**:
```r
# CORRECT: Set seed before each random operation
set.seed(123)
split <- initial_split(df, strata = outcome)

set.seed(456)
folds <- vfold_cv(training(split), strata = outcome)

# Or use tidymodels control options
ctrl <- control_resamples(save_pred = TRUE)
```

**Detection**: Random operations (`initial_split`, `vfold_cv`, `bootstraps`, `mc_cv`) without preceding `set.seed()`.

---

### RS-005: Validation Set Reuse

**Severity**: CRITICAL

**Anti-Pattern**:
```r
# WRONG: Using validation set multiple times for decisions
val_split <- validation_split(train_data)

# First use: model selection
results1 <- fit_resamples(wf1, val_split)
results2 <- fit_resamples(wf2, val_split)
# Choose wf1 based on validation

# Second use: hyperparameter tuning
tune_results <- tune_grid(wf1, val_split)
# Choose best params based on same validation set

# Third use: final "evaluation" on same validation
final_results <- fit_resamples(final_wf, val_split)  # Overfit to validation!
```

**Correct Pattern**:
```r
# CORRECT: Use CV for development, hold out final test
split <- initial_split(df, strata = outcome)
train_data <- training(split)
test_data <- testing(split)  # Touch only ONCE at the end

# Use CV for all development decisions
folds <- vfold_cv(train_data, strata = outcome)

# Model selection via CV
results1 <- fit_resamples(wf1, folds)
results2 <- fit_resamples(wf2, folds)

# Tuning via CV
tune_results <- tune_grid(wf1, folds)

# Final evaluation on test_data (only once!)
final_fit <- last_fit(final_wf, split)
```

**Detection**: Same validation/test split used in multiple `fit_resamples()` or `tune_grid()` calls.

---

## Workflow Issues (MINOR/MAJOR)

### WF-001: Not Using Workflows

**Severity**: MINOR to MAJOR

**Anti-Pattern**:
```r
# WRONG: Manual prep/bake/fit
rec <- recipe(outcome ~ ., data = train_data) |>
  step_normalize(all_numeric_predictors()) |>
  prep()

train_baked <- bake(rec, new_data = NULL)
test_baked <- bake(rec, new_data = test_data)

model <- linear_reg() |> set_engine("lm")
fit <- fit(model, outcome ~ ., data = train_baked)
preds <- predict(fit, test_baked)
```

**Correct Pattern**:
```r
# CORRECT: Use workflow
wf <- workflow() |>
  add_recipe(recipe(outcome ~ ., data = train_data) |>
    step_normalize(all_numeric_predictors())) |>
  add_model(linear_reg() |> set_engine("lm"))

fit <- fit(wf, data = train_data)
preds <- predict(fit, new_data = test_data)
```

**Benefits of workflows**:
- Automatic handling of preprocessing on new data
- Proper integration with tuning and resampling
- Cleaner code organization
- Reduced risk of data leakage

---

### WF-002: Inconsistent Preprocessing Train/Test

**Severity**: MAJOR

**Anti-Pattern**:
```r
# WRONG: Different preprocessing for train vs test
train_processed <- train_data |>
  mutate(across(where(is.numeric), ~(.x - mean(.x)) / sd(.x)))

test_processed <- test_data |>
  mutate(across(where(is.numeric), ~(.x - mean(.x)) / sd(.x)))  # Uses TEST means!
```

**Correct Pattern**:
```r
# CORRECT: Recipe applies training statistics to test data
rec <- recipe(outcome ~ ., data = train_data) |>
  step_normalize(all_numeric_predictors())

wf <- workflow() |>
  add_recipe(rec) |>
  add_model(model_spec)

fit <- fit(wf, train_data)
# predict() automatically applies training normalization to test data
predict(fit, test_data)
```

**Detection**: Manual transformations applied separately to train and test data.

---

### WF-003: Not Finalizing Workflow After Tuning

**Severity**: MAJOR

**Anti-Pattern**:
```r
# WRONG: Fitting workflow without finalizing tuned parameters
tune_results <- tune_grid(wf, resamples = folds, grid = 20)
best <- select_best(tune_results, metric = "rmse")

# Forgot to finalize!
final_fit <- fit(wf, data = train_data)  # Uses default params, not tuned!
```

**Correct Pattern**:
```r
# CORRECT: Finalize workflow before final fit
tune_results <- tune_grid(wf, resamples = folds, grid = 20)
best <- select_best(tune_results, metric = "rmse")

final_wf <- finalize_workflow(wf, best)
final_fit <- fit(final_wf, data = train_data)

# OR use last_fit() for automatic handling
final_results <- last_fit(final_wf, split)
```

**Detection**: `select_best()` or `select_by_*()` not followed by `finalize_workflow()`.

---

## Evaluation Issues (MAJOR)

### ME-001: Only Accuracy for Imbalanced Data

**Severity**: MAJOR

**Anti-Pattern**:
```r
# WRONG: Only accuracy for 95%/5% imbalanced data
metrics <- metric_set(accuracy)
results <- fit_resamples(wf, folds, metrics = metrics)
```

**Correct Pattern**:
```r
# CORRECT: Use appropriate metrics for imbalanced data
metrics <- metric_set(
  accuracy,
  bal_accuracy,    # Balanced accuracy
  kap,             # Cohen's kappa
  sens,            # Sensitivity (recall)
  spec,            # Specificity
  ppv,             # Positive predictive value (precision)
  npv,             # Negative predictive value
  f_meas,          # F1 score
  roc_auc,         # AUC-ROC
  pr_auc           # AUC-PR (better for imbalanced)
)

results <- fit_resamples(wf, folds, metrics = metrics)

# Also consider: detection_prevalence, j_index, mcc
```

**Detection**: `metric_set(accuracy)` alone with classification tasks.

---

### ME-002: Wrong Metrics for Model Mode

**Severity**: MAJOR

**Anti-Pattern**:
```r
# WRONG: Using regression metrics for classification
model <- logistic_reg() |> set_mode("classification")
metrics <- metric_set(rmse, mae, rsq)  # These are for regression!

# WRONG: Using classification metrics for regression
model <- linear_reg() |> set_mode("regression")
metrics <- metric_set(accuracy, roc_auc)  # These are for classification!
```

**Correct Pattern**:
```r
# CORRECT: Classification metrics for classification
model <- logistic_reg() |> set_mode("classification")
metrics <- metric_set(accuracy, roc_auc, f_meas, kap)

# CORRECT: Regression metrics for regression
model <- linear_reg() |> set_mode("regression")
metrics <- metric_set(rmse, mae, rsq, mape, huber_loss)
```

**Detection**: Mismatch between model mode and metric types.

---

### ME-003: Missing Calibration Assessment

**Severity**: MINOR to MAJOR

**Anti-Pattern**:
```r
# WRONG: Only evaluating discrimination, not calibration
results <- fit_resamples(wf, folds, metrics = metric_set(roc_auc))
# No calibration check!
```

**Correct Pattern**:
```r
# CORRECT: Check calibration for probabilistic predictions
final_fit <- last_fit(wf, split)
preds <- collect_predictions(final_fit)

# Calibration plot
library(probably)
cal_plot_windowed(preds, truth = outcome, .pred_class)

# Brier score
brier_class(preds, truth = outcome, .pred_positive_class)

# Consider recalibration if needed
cal_estimate <- cal_estimate_logistic(preds, truth = outcome)
```

**Detection**: Classification models without calibration assessment (no `cal_plot_*` or `brier_*`).

---

### ME-004: Missing Confidence Intervals

**Severity**: MINOR

**Anti-Pattern**:
```r
# WRONG: Reporting only point estimates
results <- fit_resamples(wf, folds)
collect_metrics(results)  # Only means, no uncertainty
```

**Correct Pattern**:
```r
# CORRECT: Report confidence intervals
results <- fit_resamples(wf, folds)
collect_metrics(results) |>
  select(.metric, mean, std_err, n) |>
  mutate(
    ci_lower = mean - 1.96 * std_err,
    ci_upper = mean + 1.96 * std_err
  )

# For bootstrap CIs
boot_results <- fit_resamples(wf, bootstraps(train_data, times = 1000))
int_pctl(boot_results, metrics)
```

**Detection**: Metric summaries without `std_err` or CI calculations.

---

### ME-005: Different Resamples for Model Comparison

**Severity**: MAJOR

**Anti-Pattern**:
```r
# WRONG: Different random folds for each model
set.seed(123)
folds1 <- vfold_cv(train_data)
results1 <- fit_resamples(wf1, folds1)

set.seed(456)  # Different seed!
folds2 <- vfold_cv(train_data)
results2 <- fit_resamples(wf2, folds2)

# Comparison is invalid - different folds!
```

**Correct Pattern**:
```r
# CORRECT: Same folds for all models being compared
set.seed(123)
folds <- vfold_cv(train_data, strata = outcome)

results1 <- fit_resamples(wf1, folds)
results2 <- fit_resamples(wf2, folds)
results3 <- fit_resamples(wf3, folds)

# Valid paired comparison
library(workflowsets)
all_wfs <- workflow_set(
  preproc = list(rec1 = rec),
  models = list(lm = lm_spec, rf = rf_spec, xgb = xgb_spec)
)

results <- workflow_map(all_wfs, resamples = folds)
autoplot(results)
```

**Detection**: Multiple `vfold_cv()` or `mc_cv()` calls with different seeds before model comparisons.

---

## Reproducibility Issues (MINOR/MAJOR)

### RP-001: Missing set.seed()

**Severity**: MAJOR

**Anti-Pattern**:
```r
# WRONG: No seeds anywhere
split <- initial_split(df)
folds <- vfold_cv(train_data)
tune_results <- tune_grid(wf, folds)  # All non-reproducible
```

**Correct Pattern**:
```r
# CORRECT: Seeds before random operations
set.seed(123)
split <- initial_split(df, strata = outcome)
train_data <- training(split)

set.seed(234)
folds <- vfold_cv(train_data, strata = outcome)

# Tuning uses internal parallelism - control seeds there too
doParallel::registerDoParallel(cores = 4)
tune_results <- tune_grid(
  wf,
  folds,
  control = control_grid(parallel_over = "resamples")
)
```

---

### RP-002: Missing tidymodels_prefer()

**Severity**: MINOR

**Anti-Pattern**:
```r
# WRONG: Potential function conflicts
library(tidymodels)
library(MASS)  # select() conflict
library(plyr)  # summarize() conflict

# Which select() is being used?
df |> select(a, b)  # Ambiguous!
```

**Correct Pattern**:
```r
# CORRECT: Set tidymodels as preferred
library(tidymodels)
tidymodels_prefer()  # Ensures tidymodels/tidyverse functions take precedence

library(MASS)
library(plyr)

# Now unambiguous
df |> select(a, b)  # Uses dplyr::select()
```

---

### RP-003: Hard-Coded File Paths

**Severity**: MINOR

**Anti-Pattern**:
```r
# WRONG: Absolute paths
df <- read_csv("/Users/john/Documents/project/data/raw_data.csv")
write_rds(model, "/Users/john/Documents/project/models/final_model.rds")
```

**Correct Pattern**:
```r
# CORRECT: Use here() for relative paths
library(here)

df <- read_csv(here("data", "raw_data.csv"))
write_rds(model, here("models", "final_model.rds"))

# Or use project-relative paths
df <- read_csv("data/raw_data.csv")
```

---

### RP-004: Missing renv for Package Management

**Severity**: MINOR to MAJOR

**Anti-Pattern**:
```r
# WRONG: No package version control
library(tidymodels)  # Which version? Unknown!
```

**Correct Pattern**:
```r
# CORRECT: Use renv for reproducibility
# Initialize: renv::init()
# Snapshot: renv::snapshot()
# Restore: renv::restore()

# Check renv.lock exists in project root
# Should have entries like:
# "tidymodels": { "Version": "1.1.1", ... }
```

---

### RP-005: Missing Session Info

**Severity**: MINOR

**Anti-Pattern**:
```r
# WRONG: No session information recorded
# Analysis runs, but versions unknown
```

**Correct Pattern**:
```r
# CORRECT: Always record session info
sessionInfo()

# Or more detailed
devtools::session_info()

# Or specifically for tidymodels
tidymodels::tidymodels_conflicts()
tidymodels::tidymodels_packages()

# Include in reports
cat("Analysis completed:", Sys.time(), "\n")
sessionInfo()
```

---

## Code Review Checklist

### Pre-Review Questions

| # | Question | Check |
|---|----------|-------|
| 1 | Is `initial_split()` called before any preprocessing? | ☐ |
| 2 | Is stratification used for splits and CV? | ☐ |
| 3 | Are seeds set before random operations? | ☐ |
| 4 | Is a workflow used (not manual prep/bake)? | ☐ |
| 5 | Is the workflow finalized after tuning? | ☐ |
| 6 | Are metrics appropriate for the task? | ☐ |
| 7 | Are confidence intervals reported? | ☐ |
| 8 | Is test data used only once at the end? | ☐ |
| 9 | Are model comparisons done on same resamples? | ☐ |
| 10 | Is session info recorded? | ☐ |

### TMwR Compliance Score

Calculate compliance score:
- **Critical Issues** (DL-*, RS-002, RS-003, RS-005): -25 points each
- **Major Issues** (RS-001, RS-004, WF-002, WF-003, ME-*): -10 points each
- **Minor Issues** (WF-001, RP-*): -5 points each

**Score Interpretation**:
- 100: Perfect TMwR compliance
- 80-99: Good compliance, minor issues
- 60-79: Acceptable, some major issues
- Below 60: Significant problems, needs revision

---

## Remediation Examples

### Before: Multiple Issues

```r
# Multiple problems:
library(tidymodels)

# DL-002: Preprocessing before split
df <- read_csv("data.csv") |>
  mutate(across(where(is.numeric), scale))

# RS-004: No seed
split <- initial_split(df)

# RS-001: No stratification
folds <- vfold_cv(training(split))

# WF-001: Not using workflow
rec <- recipe(outcome ~ ., data = training(split)) |>
  prep()

train_baked <- bake(rec, new_data = NULL)
model <- rand_forest() |> fit(outcome ~ ., data = train_baked)

# RS-002: Evaluating on training data
predict(model, train_baked) |>
  bind_cols(train_baked) |>
  metrics(truth = outcome, estimate = .pred)
```

### After: TMwR Compliant

```r
library(tidymodels)
tidymodels_prefer()
set.seed(123)

# Load raw data (no preprocessing yet)
df <- read_csv(here::here("data", "data.csv"))

# Split first with stratification
split <- initial_split(df, prop = 0.8, strata = outcome)
train_data <- training(split)
test_data <- testing(split)

# Recipe for preprocessing
rec <- recipe(outcome ~ ., data = train_data) |>
  step_normalize(all_numeric_predictors())

# Model specification
model_spec <- rand_forest(trees = 500) |>
  set_mode("regression") |>
  set_engine("ranger")

# Workflow
wf <- workflow() |>
  add_recipe(rec) |>
  add_model(model_spec)

# Cross-validation with stratification
set.seed(234)
folds <- vfold_cv(train_data, v = 10, strata = outcome)

# Evaluate
cv_results <- fit_resamples(
  wf,
  folds,
  metrics = metric_set(rmse, mae, rsq),
  control = control_resamples(save_pred = TRUE)
)

# Report with confidence intervals
collect_metrics(cv_results) |>
  mutate(
    ci_lower = mean - 1.96 * std_err,
    ci_upper = mean + 1.96 * std_err
  )

# Final fit on train, evaluate on test (once!)
final_fit <- last_fit(wf, split)
collect_metrics(final_fit)

sessionInfo()
```

---

## Key Packages Summary

| Package | Purpose |
|---------|---------|
| tidymodels | Meta-package for modeling framework |
| workflows | Workflow management |
| recipes | Preprocessing pipelines |
| parsnip | Model specifications |
| tune | Hyperparameter tuning |
| rsample | Resampling infrastructure |
| yardstick | Model metrics |
| probably | Calibration and thresholds |
| workflowsets | Comparing multiple workflows |
| stacks | Ensemble methods |
| broom | Tidy model outputs |
| here | Reproducible file paths |
| renv | Package management |

## Best Practices Summary

1. **Always split first**: `initial_split()` before any data exploration or transformation
2. **Use workflows**: Encapsulate preprocessing and models together
3. **Stratify everything**: Stratify splits and CV folds by outcome
4. **Set seeds**: Before every random operation
5. **Same folds for comparison**: Use identical resamples when comparing models
6. **Appropriate metrics**: Match metrics to problem type and class balance
7. **Report uncertainty**: Include confidence intervals for all metrics
8. **Touch test once**: Only evaluate on test data at the very end
9. **Finalize workflows**: Always `finalize_workflow()` after tuning
10. **Document environment**: Record session info for reproducibility
