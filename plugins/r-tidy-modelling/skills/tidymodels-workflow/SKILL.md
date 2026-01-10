# tidymodels Workflow Patterns

## Overview

Core workflow patterns for building machine learning models using the tidymodels ecosystem. Covers the complete pipeline from data splitting through model deployment.

## Core Workflow Components

### Data Splitting with rsample

```r
library(tidymodels)

# Basic train/test split
set.seed(123)
data_split <- initial_split(data, prop = 0.75, strata = outcome)
train_data <- training(data_split)
test_data <- testing(data_split)

# Validation set approach
data_split <- initial_validation_split(data, prop = c(0.6, 0.2))
train_data <- training(data_split)
val_data <- validation(data_split)
test_data <- testing(data_split)
```

### Recipe Creation

```r
# Create preprocessing recipe
recipe_spec <- recipe(outcome ~ ., data = train_data) |>
  step_normalize(all_numeric_predictors()) |>
  step_dummy(all_nominal_predictors()) |>
  step_zv(all_predictors())
```

### Model Specification with parsnip

```r
# Specify model with tune placeholders
model_spec <- rand_forest(
  mtry = tune(),
  trees = 1000,
  min_n = tune()
) |>
  set_engine("ranger") |>
  set_mode("classification")
```

### Workflow Assembly

```r
# Combine recipe and model
workflow_spec <- workflow() |>
  add_recipe(recipe_spec) |>
  add_model(model_spec)
```

### Resampling Setup

```r
# Cross-validation folds
cv_folds <- vfold_cv(train_data, v = 10, strata = outcome)

# Bootstrap samples
boot_samples <- bootstraps(train_data, times = 25)
```

### Hyperparameter Tuning

```r
# Define tuning grid
tune_grid <- grid_regular(
  mtry(range = c(2, 10)),
  min_n(range = c(2, 20)),
  levels = 5
)

# Tune model
tune_results <- workflow_spec |>
  tune_grid(
    resamples = cv_folds,
    grid = tune_grid,
    metrics = metric_set(roc_auc, accuracy)
  )
```

### Model Selection

```r
# Select best parameters
best_params <- select_best(tune_results, metric = "roc_auc")

# Finalize workflow
final_workflow <- workflow_spec |>
  finalize_workflow(best_params)
```

### Final Fit

```r
# Fit on full training data, evaluate on test
final_fit <- final_workflow |>
  last_fit(data_split)

# Extract metrics
collect_metrics(final_fit)

# Extract predictions
collect_predictions(final_fit)
```

### Model Extraction and Deployment

```r
# Extract fitted workflow
fitted_wf <- extract_workflow(final_fit)

# Save model
saveRDS(fitted_wf, "output/models/final_model.rds")

# Predict on new data
predictions <- predict(fitted_wf, new_data)
```

## Complete Workflow Example

```r
library(tidymodels)
tidymodels_prefer()

# 1. Load and split data
set.seed(123)
data_split <- initial_split(ames, prop = 0.75, strata = Sale_Price)

# 2. Create recipe
ames_recipe <- recipe(Sale_Price ~ ., data = training(data_split)) |>

  step_log(Sale_Price, base = 10) |>
  step_other(Neighborhood, threshold = 0.05) |>
  step_dummy(all_nominal_predictors()) |>
  step_normalize(all_numeric_predictors()) |>
  step_zv(all_predictors())

# 3. Specify model
xgb_spec <- boost_tree(
  trees = tune(),
  tree_depth = tune(),
  learn_rate = tune()
) |>
  set_engine("xgboost") |>
  set_mode("regression")

# 4. Create workflow
xgb_wf <- workflow(ames_recipe, xgb_spec)

# 5. Setup resampling
cv_folds <- vfold_cv(training(data_split), v = 5)

# 6. Tune hyperparameters
xgb_tune <- xgb_wf |>
  tune_grid(
    resamples = cv_folds,
    grid = 20,
    metrics = metric_set(rmse, rsq)
  )

# 7. Select best and finalize
best_xgb <- select_best(xgb_tune, metric = "rmse")
final_wf <- finalize_workflow(xgb_wf, best_xgb)

# 8. Final evaluation
final_fit <- last_fit(final_wf, data_split)
collect_metrics(final_fit)
```

## Workflow Sets for Model Comparison

```r
# Create multiple preprocessing recipes
basic_recipe <- recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors())

pca_recipe <- basic_recipe |>
  step_pca(all_numeric_predictors(), num_comp = 5)

# Create multiple model specifications
lm_spec <- linear_reg() |> set_engine("lm")
rf_spec <- rand_forest(trees = 500) |> set_engine("ranger") |> set_mode("regression")
xgb_spec <- boost_tree() |> set_engine("xgboost") |> set_mode("regression")

# Create workflow set
wf_set <- workflow_set(
  preproc = list(basic = basic_recipe, pca = pca_recipe),
  models = list(lm = lm_spec, rf = rf_spec, xgb = xgb_spec)
)

# Fit all workflows
wf_results <- wf_set |>
  workflow_map(
    resamples = cv_folds,
    grid = 10,
    verbose = TRUE
  )

# Compare results
autoplot(wf_results)
rank_results(wf_results, rank_metric = "rmse")
```

## Key Packages

- **rsample**: Data splitting and resampling
- **recipes**: Feature engineering
- **parsnip**: Model specification
- **workflows**: Combine preprocessing and models
- **tune**: Hyperparameter optimization
- **yardstick**: Model evaluation metrics
- **workflowsets**: Compare multiple workflows
- **broom**: Tidy model outputs

## Best Practices

1. Always set a seed before splitting data
2. Use stratified sampling for imbalanced outcomes
3. Keep test data completely separate until final evaluation
4. Use cross-validation for honest performance estimates
5. Tune hyperparameters on training data only
6. Use `last_fit()` for final evaluation on test set
7. Save the complete workflow object for deployment
