# Recipes Feature Engineering Patterns

## Overview

Comprehensive patterns for feature engineering using the recipes package. Covers preprocessing steps for numeric, categorical, and text data while preventing information leakage.

## Recipe Fundamentals

### Basic Recipe Structure

```r
library(recipes)

# Initialize recipe with formula
rec <- recipe(outcome ~ ., data = training_data)

# Or with explicit roles
rec <- recipe(training_data) |>
  update_role(outcome, new_role = "outcome") |>
  update_role(id_column, new_role = "ID") |>
  update_role(-outcome, -id_column, new_role = "predictor")
```

### Selector Functions

```r
# Type-based selectors
all_predictors()
all_outcomes()
all_numeric_predictors()
all_nominal_predictors()
all_numeric()
all_nominal()

# Name-based selectors
starts_with("prefix_")
ends_with("_suffix")
contains("pattern")
matches("regex")
one_of(c("var1", "var2"))
```

## Numeric Preprocessing

### Normalization and Scaling

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Center and scale (z-score)
  step_normalize(all_numeric_predictors()) |>

  # Scale to [0, 1]
  step_range(all_numeric_predictors(), min = 0, max = 1) |>

  # Center only
  step_center(all_numeric_predictors()) |>

  # Scale only
  step_scale(all_numeric_predictors())
```

### Transformations for Normality

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Yeo-Johnson (handles zero and negative values)
  step_YeoJohnson(all_numeric_predictors()) |>

  # Box-Cox (positive values only)
  step_BoxCox(positive_vars) |>

  # Log transformation
  step_log(skewed_vars, base = 10) |>

  # Square root
  step_sqrt(count_vars)
```

### Spline and Polynomial Features

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Natural splines
  step_ns(continuous_var, deg_free = 5) |>

  # B-splines
  step_bs(continuous_var, deg_free = 5, degree = 3) |>

  # Polynomial features
  step_poly(continuous_var, degree = 3)
```

## Categorical Encoding

### Dummy Variables

```r
rec <- recipe(outcome ~ ., data = train) |>
  # One-hot encoding (drop first level)
  step_dummy(all_nominal_predictors()) |>

  # Keep all levels
  step_dummy(all_nominal_predictors(), one_hot = TRUE)
```

### Handling Rare Categories

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Pool infrequent levels
  step_other(categorical_var, threshold = 0.05, other = "other") |>

  # Handle novel levels in new data
  step_novel(all_nominal_predictors()) |>

  # Convert NA to explicit level
  step_unknown(all_nominal_predictors())
```

### Target Encoding (embed package)

```r
library(embed)

rec <- recipe(outcome ~ ., data = train) |>
  # Likelihood encoding
  step_lencode_glm(high_cardinality_var, outcome = vars(outcome)) |>

  # Mixed model encoding (for hierarchical data)
  step_lencode_mixed(category, outcome = vars(outcome)) |>

  # Weight of evidence
  step_woe(categorical_var, outcome = vars(binary_outcome))
```

## Missing Data Handling

### Imputation Methods

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Simple imputation
  step_impute_mean(all_numeric_predictors()) |>
  step_impute_median(all_numeric_predictors()) |>
  step_impute_mode(all_nominal_predictors()) |>

  # KNN imputation
  step_impute_knn(all_predictors(), neighbors = 5) |>

  # Bagged tree imputation
  step_impute_bag(all_predictors()) |>

  # Linear model imputation
  step_impute_linear(numeric_var, impute_with = imp_vars(predictor1, predictor2))
```

### Missing Indicators

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Create indicator for missingness
  step_indicate_na(all_predictors()) |>

  # Then impute

  step_impute_median(all_numeric_predictors()) |>
  step_impute_mode(all_nominal_predictors())
```

## Dimensionality Reduction

### PCA and Related Methods

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors()) |>

  # Principal Component Analysis
  step_pca(all_numeric_predictors(), num_comp = 5) |>

  # Or keep components explaining variance threshold
  step_pca(all_numeric_predictors(), threshold = 0.95)
```

### Other Reduction Methods

```r
library(embed)

rec <- recipe(outcome ~ ., data = train) |>
  # UMAP
  step_umap(all_numeric_predictors(), num_comp = 2) |>

  # Kernel PCA
  step_kpca(all_numeric_predictors(), num_comp = 5)
```

## Interactions and Combinations

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Create interaction terms
  step_interact(terms = ~ var1:var2) |>

  # Multiple interactions
  step_interact(terms = ~ starts_with("x"):starts_with("z")) |>

  # Ratios
  step_ratio(numerator = denom_vars(var1), denom = denom_vars(var2))
```

## Feature Selection

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Remove zero variance
  step_zv(all_predictors()) |>

  # Remove near-zero variance
  step_nzv(all_predictors(), freq_cut = 95/5, unique_cut = 10) |>

  # Remove highly correlated
  step_corr(all_numeric_predictors(), threshold = 0.9) |>

  # Remove linear combinations
  step_lincomb(all_numeric_predictors())
```

## Class Imbalance (themis)

```r
library(themis)

rec <- recipe(outcome ~ ., data = train) |>
  # Downsample majority class
  step_downsample(outcome) |>

  # Upsample minority class
  step_upsample(outcome) |>

  # SMOTE
  step_smote(outcome) |>

  # ADASYN
  step_adasyn(outcome)
```

## Date/Time Features

```r
rec <- recipe(outcome ~ ., data = train) |>
  # Extract date components
  step_date(date_var, features = c("year", "month", "dow", "doy")) |>

  # Holiday indicators
  step_holiday(date_var, holidays = c("USChristmasDay", "USNewYearsDay")) |>

  # Time components
  step_time(datetime_var, features = c("hour", "minute"))
```

## Text Features (textrecipes)

```r
library(textrecipes)

rec <- recipe(outcome ~ ., data = train) |>
  step_tokenize(text_var) |>
  step_stopwords(text_var) |>
  step_stem(text_var) |>
  step_ngram(text_var, num_tokens = 2) |>
  step_tfidf(text_var, max_tokens = 100)
```

## Recipe Execution

```r
# Prepare recipe (estimate parameters from training data)
prepped_rec <- prep(rec, training = train_data)

# Apply to training data
train_processed <- bake(prepped_rec, new_data = NULL)  # or juice(prepped_rec)

# Apply to new data
test_processed <- bake(prepped_rec, new_data = test_data)

# Inspect recipe
tidy(prepped_rec)
tidy(prepped_rec, number = 1)  # specific step
```

## Step Ordering Best Practices

```r
recipe(outcome ~ ., data = train) |>
  # 1. Handle roles and IDs
  update_role(id, new_role = "ID") |>


  # 2. Impute missing values first
  step_impute_median(all_numeric_predictors()) |>
  step_impute_mode(all_nominal_predictors()) |>

  # 3. Handle individual variable issues
  step_other(all_nominal_predictors(), threshold = 0.05) |>
  step_novel(all_nominal_predictors()) |>

  # 4. Transform numeric variables
  step_YeoJohnson(all_numeric_predictors()) |>

  # 5. Create interactions before encoding
  step_interact(terms = ~ var1:var2) |>

  # 6. Encode categorical variables
  step_dummy(all_nominal_predictors()) |>

  # 7. Normalize (after dummy coding)
  step_normalize(all_numeric_predictors()) |>

  # 8. Feature selection last
  step_zv(all_predictors()) |>
  step_corr(all_numeric_predictors())
```

## Key Principles

1. **Prevent leakage**: All statistics computed from training data only
2. **Order matters**: Impute → Transform → Encode → Normalize → Select
3. **Use selectors**: More maintainable than listing variable names
4. **Document decisions**: Comment why each step is included
5. **Test on holdout**: Verify recipe generalizes to new data
