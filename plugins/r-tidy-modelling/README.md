# R Tidy Modelling Plugin

> **Comprehensive R Data Science & Biostatistics** — tidyverse, tidymodels, clinical trials, epidemiology, and reproducible research

Part of the [BiostatAgent](https://github.com/choxos/BiostatAgent) ecosystem.

## Overview

This plugin provides expert agents for R-based data science and biostatistics following tidyverse and tidymodels best practices. It covers the complete data analysis lifecycle from data wrangling to publication-ready reports.

### Core Frameworks

| Framework | Purpose | Key Packages |
|-----------|---------|--------------|
| **tidyverse** | Data manipulation & visualization | dplyr, tidyr, ggplot2, purrr |
| **tidymodels** | Machine learning workflows | parsnip, recipes, workflows, tune |
| **renv** | Reproducible environments | renv |
| **targets** | Pipeline orchestration | targets, tarchetypes |
| **Quarto** | Scientific publishing | quarto, knitr |

## Quick Start

```bash
# Install plugin
/plugin install r-tidy-modelling

# Start analysis
/r-analysis
```

## Commands

### `/r-analysis`
End-to-end analysis workflow from data import to results.

### `/r-code-review`
Review R code for tidyverse best practices and efficiency.

### `/r-model-comparison`
Compare multiple models with cross-validation and metrics.

### `/r-clinical-analysis`
Clinical trial analysis following ICH E9 and CONSORT guidelines.

### `/r-project-setup`
Set up reproducible R project with renv, targets, and folder structure.

### `/r-doc-generate`
Generate documentation for R packages and projects.

### `/r-tutorial-create`
Create tutorials and educational content from code.

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `r-data-architect` | Haiku | Routes requests and designs data pipelines |
| `tidymodels-engineer` | Sonnet | ML workflows with tidymodels |
| `feature-engineer` | Sonnet | Feature engineering with recipes |
| `biostatistician` | Sonnet | Statistical analysis for clinical/medical research |
| `data-wrangler` | Sonnet | Data manipulation with tidyverse |
| `viz-specialist` | Sonnet | Publication-ready visualizations with ggplot2 |
| `reporting-engineer` | Sonnet | Quarto/R Markdown reports |
| `r-code-reviewer` | Sonnet | Code review for best practices |
| `r-docs-architect` | Sonnet | Documentation with roxygen2/pkgdown |
| `r-tutorial-engineer` | Sonnet | Educational content creation |

## Skills

### Tidymodels Workflow
- **tidymodels-workflow** — Complete ML pipeline: parsnip, workflows, tune
- **recipes-patterns** — Feature engineering: step_*, preprocessing pipelines
- **resampling-strategies** — Cross-validation, bootstrap, nested resampling
- **model-tuning** — Hyperparameter optimization with tune_grid, tune_bayes
- **model-evaluation** — Metrics, calibration, performance assessment
- **tidymodels-review-patterns** — Code review patterns for tidymodels

### Clinical & Biostatistics
- **clinical-trials** — ICH E9, CONSORT, ITT/PP analysis, safety reporting
- **survival-analysis** — Cox models, Kaplan-Meier, competing risks, survminer
- **epidemiology-methods** — Cohort studies, case-control, incidence/prevalence
- **meta-analysis** — Fixed/random effects, forest plots, publication bias
- **diagnostic-accuracy** — Sensitivity, specificity, ROC curves, Youden index

### Advanced Methods
- **bayesian-modeling** — brms, rstanarm, Bayesian workflow in R
- **causal-mediation** — Mediation analysis, causal inference
- **mendelian-randomization** — MR methods, instrument validation
- **pharmacokinetics** — PK/PD modeling, compartmental models
- **health-economics** — Cost-effectiveness, QALY, decision models

### Specialized Domains
- **genomics-analysis** — Bioconductor, DESeq2, pathway analysis
- **network-meta-analysis** — Network MA, consistency, rankings
- **ipd-meta-analysis** — Individual patient data meta-analysis
- **real-world-evidence** — RWE studies, target trial emulation
- **advanced-adaptive-trials** — Adaptive designs, interim analyses

### Documentation & Reporting
- **r-documentation-patterns** — roxygen2, pkgdown, vignettes
- **roxygen2-pkgdown** — Package documentation best practices

## Usage Examples

### Tidymodels Machine Learning Pipeline

```
Build a classification model to predict patient readmission using
tidymodels. Include feature engineering, cross-validation, and
hyperparameter tuning. Compare random forest and XGBoost.
```

**Generated R code:**
```r
library(tidymodels)
library(xgboost)

# Data split
set.seed(123)
data_split <- initial_split(patient_data, prop = 0.8, strata = readmission)
train_data <- training(data_split)
test_data <- testing(data_split)

# Recipe
readmission_recipe <- recipe(readmission ~ ., data = train_data) |>
  step_impute_median(all_numeric_predictors()) |>
  step_impute_mode(all_nominal_predictors()) |>
  step_dummy(all_nominal_predictors()) |>
  step_normalize(all_numeric_predictors()) |>
  step_zv(all_predictors())

# Model specifications
rf_spec <- rand_forest(
  mtry = tune(),
  trees = 500,
  min_n = tune()
) |>
  set_engine("ranger") |>
  set_mode("classification")

xgb_spec <- boost_tree(
  trees = tune(),
  tree_depth = tune(),
  learn_rate = tune()
) |>
  set_engine("xgboost") |>
  set_mode("classification")

# Workflows
rf_wf <- workflow() |>
  add_recipe(readmission_recipe) |>
  add_model(rf_spec)

xgb_wf <- workflow() |>
  add_recipe(readmission_recipe) |>
  add_model(xgb_spec)

# Cross-validation
cv_folds <- vfold_cv(train_data, v = 10, strata = readmission)

# Tune models
rf_results <- tune_grid(
  rf_wf,
  resamples = cv_folds,
  grid = 20,
  metrics = metric_set(roc_auc, accuracy, sensitivity, specificity)
)

xgb_results <- tune_grid(
  xgb_wf,
  resamples = cv_folds,
  grid = 20,
  metrics = metric_set(roc_auc, accuracy, sensitivity, specificity)
)

# Compare models
collect_metrics(rf_results) |> filter(.metric == "roc_auc")
collect_metrics(xgb_results) |> filter(.metric == "roc_auc")

# Finalize best model
best_rf <- select_best(rf_results, metric = "roc_auc")
final_rf <- finalize_workflow(rf_wf, best_rf)
final_fit <- fit(final_rf, train_data)

# Test set evaluation
test_results <- augment(final_fit, test_data)
roc_auc(test_results, readmission, .pred_Yes)
```

### Survival Analysis

```
Analyze time-to-event data for a clinical trial. Include Kaplan-Meier
curves, log-rank test, and Cox proportional hazards model with
treatment, age, and stage as covariates.
```

**Generated R code:**
```r
library(survival)
library(survminer)

# Kaplan-Meier estimate
km_fit <- survfit(Surv(time, event) ~ treatment, data = trial_data)

# Kaplan-Meier plot
ggsurvplot(
  km_fit,
  data = trial_data,
  risk.table = TRUE,
  pval = TRUE,
  conf.int = TRUE,
  palette = c("#E7B800", "#2E9FDF"),
  xlab = "Time (months)",
  ylab = "Survival Probability",
  title = "Overall Survival by Treatment",
  legend.title = "Treatment",
  legend.labs = c("Control", "Active"),
  risk.table.col = "strata",
  ggtheme = theme_bw()
)

# Log-rank test
survdiff(Surv(time, event) ~ treatment, data = trial_data)

# Cox proportional hazards
cox_model <- coxph(
  Surv(time, event) ~ treatment + age + stage,
  data = trial_data
)

summary(cox_model)

# Forest plot of hazard ratios
ggforest(cox_model, data = trial_data)

# Check proportional hazards assumption
cox.zph(cox_model)
```

### Clinical Trial Analysis (CONSORT)

```
Generate a CONSORT-compliant analysis for a randomized controlled trial
including flow diagram numbers, baseline characteristics table,
primary efficacy analysis, and safety summary.
```

**Generated R code:**
```r
library(tidyverse)
library(gtsummary)
library(table1)

# CONSORT flow numbers
flow_data <- trial_data |>
  summarize(
    screened = n(),
    randomized = sum(!is.na(randomization_group)),
    excluded_not_eligible = sum(exclusion_reason == "not_eligible"),
    excluded_declined = sum(exclusion_reason == "declined"),
    allocated_treatment = sum(randomization_group == "Treatment"),
    allocated_control = sum(randomization_group == "Control"),
    completed_treatment = sum(randomization_group == "Treatment" & completed),
    completed_control = sum(randomization_group == "Control" & completed),
    analyzed_treatment = sum(randomization_group == "Treatment" & in_analysis),
    analyzed_control = sum(randomization_group == "Control" & in_analysis)
  )

# Baseline characteristics (Table 1)
baseline_table <- trial_data |>
  filter(!is.na(randomization_group)) |>
  select(randomization_group, age, sex, bmi, disease_stage,
         baseline_score, comorbidities) |>
  tbl_summary(
    by = randomization_group,
    statistic = list(
      all_continuous() ~ "{mean} ({sd})",
      all_categorical() ~ "{n} ({p}%)"
    ),
    digits = all_continuous() ~ 1,
    label = list(
      age ~ "Age (years)",
      sex ~ "Sex",
      bmi ~ "BMI (kg/m²)",
      disease_stage ~ "Disease Stage",
      baseline_score ~ "Baseline Score",
      comorbidities ~ "Comorbidities"
    )
  ) |>
  add_p() |>
  modify_header(label = "**Characteristic**")

# Primary efficacy analysis (ITT)
primary_model <- lm(
  endpoint_change ~ treatment + baseline_score + stratification_factor,
  data = trial_data |> filter(itt_population)
)

tbl_regression(primary_model, intercept = TRUE)

# Safety summary
ae_summary <- trial_data |>
  group_by(randomization_group) |>
  summarize(
    n_patients = n(),
    any_ae = sum(any_ae),
    any_ae_pct = mean(any_ae) * 100,
    serious_ae = sum(serious_ae),
    serious_ae_pct = mean(serious_ae) * 100,
    discontinued_ae = sum(discontinued_due_to_ae),
    discontinued_pct = mean(discontinued_due_to_ae) * 100
  )
```

### Reproducible Project Setup

```
Set up a new R project for a clinical analysis with renv for
dependency management, targets for pipeline, and standard folder structure.
```

**Generated structure:**
```
project/
├── _targets.R              # targets pipeline definition
├── renv.lock               # locked dependencies
├── R/
│   ├── functions.R         # analysis functions
│   ├── data_prep.R         # data preparation
│   └── visualization.R     # plotting functions
├── data/
│   ├── raw/                # original data (never modify)
│   └── processed/          # cleaned data
├── reports/
│   └── analysis.qmd        # Quarto report
├── output/
│   ├── figures/
│   └── tables/
└── README.md
```

**_targets.R:**
```r
library(targets)
library(tarchetypes)

tar_option_set(packages = c("tidyverse", "survival", "gtsummary"))

list(
  tar_target(raw_data, read_csv("data/raw/trial_data.csv")),
  tar_target(clean_data, clean_trial_data(raw_data)),
  tar_target(baseline_table, create_baseline_table(clean_data)),
  tar_target(km_analysis, run_survival_analysis(clean_data)),
  tar_target(report, tar_quarto(path = "reports/analysis.qmd"))
)
```

## R Dependencies

```r
# Core tidyverse
install.packages("tidyverse")

# Tidymodels
install.packages("tidymodels")

# Clinical/biostatistics
install.packages(c("survival", "survminer", "gtsummary", "table1"))

# Reproducibility
install.packages(c("renv", "targets", "tarchetypes"))

# Reporting
install.packages("quarto")

# Visualization
install.packages(c("ggplot2", "patchwork", "scales", "ggrepel"))

# Bayesian
install.packages(c("brms", "rstanarm", "bayesplot"))

# Genomics (Bioconductor)
if (!require("BiocManager")) install.packages("BiocManager")
BiocManager::install(c("DESeq2", "edgeR", "limma"))
```

## Best Practices

### Tidyverse Style
```r
# Good
patient_data |>
  filter(age >= 18) |>
  group_by(treatment) |>
  summarize(
    n = n(),
    mean_outcome = mean(outcome, na.rm = TRUE)
  )

# Avoid
summarize(group_by(filter(patient_data, age >= 18), treatment),
          n = n(), mean_outcome = mean(outcome, na.rm = TRUE))
```

### Tidymodels Patterns
```r
# Good: Modular workflow
recipe_spec <- recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors())

model_spec <- linear_reg() |>
  set_engine("lm")

workflow() |>
  add_recipe(recipe_spec) |>
  add_model(model_spec) |>
  fit(train)
```

### Reproducibility
- Always use `set.seed()` before random operations
- Use `renv` for dependency management
- Use `targets` for complex pipelines
- Document data provenance

## References

- Wickham H, Grolemund G (2023). R for Data Science, 2nd Edition
- Kuhn M, Silge J (2022). Tidy Modeling with R
- ICH E9: Statistical Principles for Clinical Trials
- CONSORT Statement: https://www.consort-statement.org/

## License

MIT License — see [LICENSE](../../LICENSE) for details.
