# Resampling Strategies

## Overview

Comprehensive guide to resampling methods for model validation using the rsample package. Covers cross-validation, bootstrapping, and specialized resampling for time series and grouped data.

## Data Splitting

### Basic Train/Test Split

```r
library(rsample)

set.seed(123)

# Simple split (75% training)
split <- initial_split(data, prop = 0.75)

# Stratified split (maintain outcome proportions)
split <- initial_split(data, prop = 0.75, strata = outcome)

# Stratified with breaking for continuous outcomes
split <- initial_split(data, prop = 0.75, strata = outcome, breaks = 4)

# Extract sets
train <- training(split)
test <- testing(split)
```

### Three-Way Split (Train/Validation/Test)

```r
# Single validation set
split <- initial_validation_split(data, prop = c(0.6, 0.2))

train <- training(split)
val <- validation(split)
test <- testing(split)

# Create validation set from resampling
val_set <- validation_set(split)
```

## Cross-Validation

### V-Fold Cross-Validation

```r
# Basic 10-fold CV
folds <- vfold_cv(train_data, v = 10)

# Stratified CV
folds <- vfold_cv(train_data, v = 10, strata = outcome)

# Repeated CV
folds <- vfold_cv(train_data, v = 10, repeats = 5, strata = outcome)

# Access individual folds
folds$splits[[1]]
analysis(folds$splits[[1]])  # training fold
assessment(folds$splits[[1]])  # validation fold
```

### Leave-One-Out CV

```r
# LOO CV (useful for small datasets)
loo_folds <- loo_cv(train_data)
```

### Monte Carlo Cross-Validation

```r
# Random repeated holdout
mc_folds <- mc_cv(train_data, prop = 0.75, times = 25)
```

## Bootstrapping

### Basic Bootstrap

```r
# Standard bootstrap (with replacement)
boot <- bootstraps(train_data, times = 100)

# Stratified bootstrap
boot <- bootstraps(train_data, times = 100, strata = outcome)

# Apparent resampling (training = assessment for baseline)
apparent <- apparent(train_data)
```

### Bootstrap for Confidence Intervals

```r
# Bootstrap model coefficients
boot_models <- boot |>
  mutate(
    model = map(splits, ~ lm(y ~ x, data = analysis(.x))),
    coefs = map(model, tidy)
  ) |>
  unnest(coefs)

# Calculate confidence intervals
boot_ci <- int_pctl(boot_models, statistic = estimate)
```

## Grouped Resampling

### Group V-Fold CV

```r
# Keep groups together (e.g., patients, clusters)
group_folds <- group_vfold_cv(
  data,
  group = patient_id,
  v = 10
)
```

### Nested Resampling

```r
# Outer resamples for model assessment
outer_folds <- vfold_cv(train_data, v = 5)

# Inner resamples for tuning (created during tune_grid)
tune_results <- workflow |>
  tune_grid(
    resamples = outer_folds,  # outer loop
    grid = 20
  )
```

## Time Series Resampling

### Rolling Origin

```r
# Time series cross-validation
ts_folds <- rolling_origin(
  ts_data,
  initial = 365,      # initial training window
  assess = 30,        # assessment window size
  skip = 29,          # skip between resamples
  cumulative = TRUE   # growing training window
)

# Fixed-size training window
ts_folds <- rolling_origin(
  ts_data,
  initial = 365,
  assess = 30,
  cumulative = FALSE  # sliding window
)
```

### Sliding Window

```r
# Alternative sliding window approach
ts_folds <- sliding_window(
  ts_data,
  lookback = 365,   # training window size
  assess_start = 1,
  assess_stop = 30
)

# Sliding period (for date/time index)
ts_folds <- sliding_period(
  ts_data,
  index = date,
  period = "month",
  lookback = 12,
  assess_stop = 1
)
```

## Spatial Resampling (spatialsample)

```r
library(spatialsample)

# Spatial block CV
spatial_folds <- spatial_block_cv(
  sf_data,
  v = 10,
  buffer = 1000  # buffer distance in map units
)

# Spatial clustering CV
spatial_folds <- spatial_clustering_cv(
  sf_data,
  v = 10,
  cluster_function = "kmeans"
)

# Leave-location-out CV
spatial_folds <- spatial_leave_location_out_cv(
  sf_data,
  group = location_id
)
```

## Working with Resamples

### Fitting Models to Resamples

```r
# Using workflows
results <- workflow |>
  fit_resamples(
    resamples = folds,
    metrics = metric_set(rmse, rsq, mae),
    control = control_resamples(save_pred = TRUE)
  )

# Collect metrics
collect_metrics(results)

# Collect predictions
collect_predictions(results)
```

### Custom Resampling

```r
# Create custom resample object
custom_splits <- list(
  make_splits(
    list(analysis = 1:100, assessment = 101:130),
    data = my_data
  ),
  make_splits(
    list(analysis = 1:120, assessment = 121:150),
    data = my_data
  )
)

custom_rset <- manual_rset(
  splits = custom_splits,
  ids = c("Split1", "Split2")
)
```

## Resampling Comparison

| Method | Use Case | Variance | Bias |
|--------|----------|----------|------|
| V-fold CV | General purpose | Medium | Low |
| Repeated CV | More stable estimates | Low | Low |
| LOOCV | Small datasets | High | Very Low |
| Bootstrap | Confidence intervals | Low | Medium |
| Monte Carlo CV | Large datasets | Medium | Low |
| Rolling Origin | Time series | - | Low |
| Group CV | Clustered data | Medium | Low |

## Best Practices

### Choosing Resampling Method

```r
# Classification with imbalanced classes
folds <- vfold_cv(data, v = 10, strata = outcome)

# Small dataset (n < 100)
folds <- vfold_cv(data, v = 5, repeats = 10, strata = outcome)
# or
folds <- loo_cv(data)

# Large dataset (n > 10000)
folds <- vfold_cv(data, v = 10)  # single fold sufficient

# Time series
folds <- rolling_origin(data, initial = n_train, assess = n_test)

# Grouped/clustered data
folds <- group_vfold_cv(data, group = cluster_id, v = 10)
```

### Stratification Guidelines

```r
# Always stratify for:
# - Imbalanced classification (rare events)
# - Small datasets
# - Multi-class with varying frequencies

# Stratify continuous outcomes with breaks
folds <- vfold_cv(data, strata = continuous_outcome, breaks = 4)
```

### Number of Folds/Resamples

- **V-fold CV**: v = 10 is standard; v = 5 for large datasets; v = n (LOOCV) for small
- **Bootstrap**: 100-1000 resamples for stable estimates
- **Monte Carlo CV**: 25-100 iterations depending on dataset size
- **Time series**: Enough folds to cover seasonal patterns

## Integration with tune

```r
# Tune with cross-validation
tune_results <- workflow |>
  tune_grid(
    resamples = vfold_cv(train, v = 10, strata = outcome),
    grid = 20,
    metrics = metric_set(roc_auc, accuracy)
  )

# Tune with bootstrap
tune_results <- workflow |>
  tune_bayes(
    resamples = bootstraps(train, times = 25),
    iter = 50
  )
```
