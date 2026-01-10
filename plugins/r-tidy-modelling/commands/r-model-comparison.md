# R Model Comparison Workflow

Systematic model comparison using tidymodels workflow sets. This command orchestrates the **tidymodels-engineer** and **feature-engineer** agents to build and compare multiple models.

## Workflow Steps

### 1. Data Preparation
The **feature-engineer** agent will:
- Analyze data characteristics
- Design appropriate preprocessing recipes
- Create multiple recipe variants if beneficial

### 2. Model Specification
The **tidymodels-engineer** agent will:
- Define candidate model specifications
- Configure appropriate hyperparameters for tuning
- Set up model-specific preprocessing requirements

### 3. Workflow Set Creation
Create systematic combinations of:
- Preprocessing approaches
- Model algorithms
- Hyperparameter configurations

### 4. Cross-Validation
Execute parallel model fitting with:
- Appropriate resampling strategy
- Racing methods for efficiency (if many configurations)
- Comprehensive metric collection

### 5. Comparison Analysis
Generate comparison outputs:
- Performance metric rankings
- Statistical comparisons between models
- Visualization of results

### 6. Final Model Selection
Based on results:
- Select best performing model
- Fit final model on full training data
- Evaluate on held-out test set

## Usage

```
/r-model-comparison [data_path] [target] [task_type] [models]
```

### Parameters
- `data_path`: Path to the dataset
- `target`: Name of the outcome variable
- `task_type`: One of `classification`, `regression`
- `models`: Comma-separated list or `all` (default: sensible defaults based on task)

### Available Models

**Classification:**
- `logistic` - Logistic regression
- `glmnet` - Regularized logistic regression
- `rf` - Random forest
- `xgb` - XGBoost
- `lightgbm` - LightGBM
- `svm` - Support vector machine
- `mlp` - Neural network

**Regression:**
- `lm` - Linear regression
- `glmnet` - Regularized regression
- `rf` - Random forest
- `xgb` - XGBoost
- `lightgbm` - LightGBM
- `svm` - Support vector regression
- `mars` - MARS

## Output Location

```
output/
├── code/
│   └── model_comparison.R      # Reproducible script
├── reports/
│   └── model_comparison.html   # Comparison report
├── models/
│   ├── tuning_results.rds      # All tuning results
│   └── final_model.rds         # Best model fitted
└── figures/
    ├── model_comparison.png    # Performance comparison
    └── calibration.png         # Calibration plots
```

## Example

```
/r-model-comparison data/credit.csv default classification rf,xgb,glmnet
```

This compares random forest, XGBoost, and regularized logistic regression for predicting credit default.

## Comparison Report Contents

1. **Data Summary**
   - Dataset dimensions
   - Target distribution
   - Feature overview

2. **Preprocessing Summary**
   - Recipe steps applied
   - Transformations and encodings

3. **Model Performance**
   - Cross-validation metrics
   - Confidence intervals
   - Statistical comparisons

4. **Visualizations**
   - ROC curves (classification)
   - Calibration plots
   - Variable importance (for interpretable models)

5. **Recommendations**
   - Best model selection rationale
   - Trade-off considerations
   - Deployment notes

## Advanced Options

For advanced configurations, you can specify:
- Custom resampling schemes
- Specific tuning grids
- Racing parameters
- Parallel processing settings

## Notes

- Original data is never modified
- All models are saved for later use
- Reproducible script is generated for re-running
