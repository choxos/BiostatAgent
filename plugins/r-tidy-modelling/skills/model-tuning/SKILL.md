# Model Tuning Patterns

## Overview

Comprehensive hyperparameter optimization using the tune package. Covers grid search, iterative search, racing methods, and Bayesian optimization.

## Tunable Parameters

### Marking Parameters for Tuning

```r
library(tidymodels)

# Use tune() placeholder in model specification
rf_spec <- rand_forest(
  mtry = tune(),
  trees = 1000,
  min_n = tune()
) |>
  set_engine("ranger") |>
  set_mode("classification")

# Tune recipe steps
rec <- recipe(outcome ~ ., data = train) |>
  step_pca(all_numeric_predictors(), num_comp = tune()) |>
  step_normalize(all_numeric_predictors())
```

### Parameter Objects (dials)

```r
library(dials)

# View parameter information
mtry()
min_n()
trees()
learn_rate()
penalty()

# Customize parameter ranges
mtry(range = c(2, 20))
min_n(range = c(5, 50))
learn_rate(range = c(-3, -1), trans = log10_trans())

# Update based on data
mtry_final <- finalize(mtry(), train_data)
```

## Grid Search

### Regular Grid

```r
# Evenly spaced grid
regular_grid <- grid_regular(
  mtry(range = c(2, 10)),
  min_n(range = c(2, 20)),
  levels = 5  # 5 levels per parameter = 25 combinations
)

# Different levels per parameter
regular_grid <- grid_regular(
  mtry(range = c(2, 10)),
  min_n(range = c(2, 20)),
  levels = c(mtry = 5, min_n = 3)
)
```

### Random Grid

```r
# Random sampling of parameter space
random_grid <- grid_random(
  mtry(range = c(2, 10)),
  min_n(range = c(2, 20)),
  size = 50
)
```

### Space-Filling Designs

```r
# Latin hypercube (better coverage than random)
lhs_grid <- grid_latin_hypercube(
  mtry(range = c(2, 10)),
  min_n(range = c(2, 20)),
  size = 30
)

# Maximum entropy grid
maxent_grid <- grid_max_entropy(
  mtry(range = c(2, 10)),
  min_n(range = c(2, 20)),
  size = 30
)
```

### Running Grid Search

```r
# Basic grid search
tune_results <- workflow |>
  tune_grid(
    resamples = cv_folds,
    grid = 20,  # auto-generates grid
    metrics = metric_set(roc_auc, accuracy),
    control = control_grid(verbose = TRUE)
  )

# With explicit grid
tune_results <- workflow |>
  tune_grid(
    resamples = cv_folds,
    grid = my_grid,
    metrics = metric_set(roc_auc, accuracy)
  )
```

## Bayesian Optimization

### Basic Bayesian Tuning

```r
# Iterative Bayesian search
tune_results <- workflow |>
  tune_bayes(
    resamples = cv_folds,
    iter = 50,           # maximum iterations
    initial = 10,        # initial grid points
    metrics = metric_set(roc_auc),
    control = control_bayes(
      verbose = TRUE,
      no_improve = 20    # stop if no improvement for 20 iters
    )
  )
```

### Bayesian with Custom Initial Points

```r
# Start with grid results
initial_grid <- workflow |>
  tune_grid(
    resamples = cv_folds,
    grid = 10,
    metrics = metric_set(roc_auc)
  )

# Continue with Bayesian
bayes_results <- workflow |>
  tune_bayes(
    resamples = cv_folds,
    iter = 40,
    initial = initial_grid,  # use grid results as initial points
    metrics = metric_set(roc_auc)
  )
```

### Acquisition Functions

```r
control_bayes(
  # Expected improvement (default)
  objective = exp_improve(),

  # Probability of improvement
  objective = prob_improve(),

  # Confidence bound
  objective = conf_bound(kappa = 2)
)
```

## Racing Methods (finetune)

### ANOVA Racing

```r
library(finetune)

# Eliminate poor configurations early
race_results <- workflow |>
  tune_race_anova(
    resamples = cv_folds,
    grid = 50,
    metrics = metric_set(roc_auc),
    control = control_race(
      verbose = TRUE,
      burn_in = 3  # evaluate all for first 3 resamples
    )
  )

# Plot racing results
plot_race(race_results)
```
### Win/Loss Racing

```r
# Statistical comparison of configurations
race_results <- workflow |>
  tune_race_win_loss(
    resamples = cv_folds,
    grid = 50,
    metrics = metric_set(roc_auc),
    control = control_race()
  )
```

## Simulated Annealing

```r
library(finetune)

# Simulated annealing search
sa_results <- workflow |>
  tune_sim_anneal(
    resamples = cv_folds,
    iter = 50,
    initial = 5,
    metrics = metric_set(roc_auc),
    control = control_sim_anneal(
      verbose = TRUE,
      cooling_coef = 0.1
    )
  )
```

## Analyzing Tuning Results

### Best Parameters

```r
# Best by primary metric
best_params <- select_best(tune_results, metric = "roc_auc")

# Best within one SE of optimal (more parsimonious)
best_params <- select_by_one_std_err(
  tune_results,
  metric = "roc_auc",
  mtry, min_n  # parameters to minimize
)

# Best by percent loss from optimal
best_params <- select_by_pct_loss(
  tune_results,
  metric = "roc_auc",
  limit = 2  # within 2% of best
)
```

### Visualizing Results

```r
# Performance across parameters
autoplot(tune_results)

# Specific parameter effects
autoplot(tune_results, type = "marginals")

# Performance vs parameters
autoplot(tune_results, type = "parameters")

# Collect all metrics
metrics_df <- collect_metrics(tune_results)
```

### Finalizing Model

```r
# Finalize workflow with best parameters
final_wf <- workflow |>
  finalize_workflow(best_params)

# Final fit on all training data
final_fit <- final_wf |>
  last_fit(data_split)

# Extract metrics on test set
collect_metrics(final_fit)
```

## Parallel Processing

```r
library(doParallel)

# Register parallel backend
cl <- makePSOCKcluster(parallel::detectCores() - 1)
registerDoParallel(cl)

# Tuning will automatically use parallel
tune_results <- workflow |>
  tune_grid(
    resamples = cv_folds,
    grid = 100
  )

# Stop cluster
stopCluster(cl)
```

### Using future

```r
library(future)

# Set up parallel plan
plan(multisession, workers = 4)

# With finetune racing
race_results <- workflow |>
  tune_race_anova(
    resamples = cv_folds,
    grid = 100,
    control = control_race(parallel_over = "everything")
  )
```

## Tuning XGBoost Example

```r
# XGBoost with many tunable parameters
xgb_spec <- boost_tree(
  trees = tune(),
  tree_depth = tune(),
  min_n = tune(),
  loss_reduction = tune(),
  sample_size = tune(),
  mtry = tune(),
  learn_rate = tune()
) |>
  set_engine("xgboost") |>
  set_mode("classification")

# Define parameter grid
xgb_grid <- grid_latin_hypercube(
  trees(range = c(100, 1500)),
  tree_depth(range = c(3, 15)),
  min_n(range = c(2, 30)),
  loss_reduction(),
  sample_prop(range = c(0.5, 1)),
  finalize(mtry(), train_data),
  learn_rate(range = c(-3, -1)),
  size = 50
)

# Use racing for efficiency
xgb_results <- workflow(rec, xgb_spec) |>
  tune_race_anova(
    resamples = cv_folds,
    grid = xgb_grid,
    metrics = metric_set(roc_auc)
  )
```

## Control Options Summary

| Function | Key Control Options |
|----------|-------------------|
| `tune_grid` | `save_pred`, `verbose`, `allow_par` |
| `tune_bayes` | `no_improve`, `uncertain`, `objective` |
| `tune_race_*` | `burn_in`, `num_ties`, `alpha` |
| `tune_sim_anneal` | `cooling_coef`, `restart` |

## Best Practices

1. Start with grid search to understand parameter space
2. Use racing methods for large grids (>50 combinations)
3. Use Bayesian optimization for expensive models
4. Always set a seed for reproducibility
5. Use stratified resampling for imbalanced outcomes
6. Consider `select_by_one_std_err` for simpler models
7. Monitor for overfitting during iterative search
