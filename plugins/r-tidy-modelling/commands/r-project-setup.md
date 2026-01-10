# R Project Setup

Initialize a new R data science project with best practices. This command uses the **r-data-architect** agent to create a well-structured, reproducible project foundation.

## Project Structure Created

```
project_name/
├── R/                      # R functions
│   └── utils.R
├── data/
│   ├── raw/                # Original, immutable data
│   └── processed/          # Cleaned data
├── output/
│   ├── figures/            # Plots and visualizations
│   ├── tables/             # Summary tables
│   └── models/             # Saved model objects
├── reports/                # Quarto/RMarkdown reports
│   └── analysis.qmd
├── tests/                  # testthat tests
│   └── testthat/
├── _targets.R              # targets pipeline (optional)
├── .gitignore              # Git ignore patterns
├── .Rprofile               # Project-specific settings
├── renv.lock               # Dependency lock file
├── project_name.Rproj      # RStudio project
├── README.md               # Project documentation
└── DESCRIPTION             # Project metadata
```

## Usage

```
/r-project-setup [project_name] [template] [options]
```

### Parameters
- `project_name`: Name for the new project
- `template`: One of `analysis`, `package`, `shiny`, `clinical` (default: analysis)
- `options`: Comma-separated options (see below)

### Templates

**analysis**: Standard data analysis project
- Focus on EDA and statistical analysis
- Includes Quarto report template
- Sets up targets pipeline

**package**: R package development
- Standard R package structure
- Includes testthat setup
- pkgdown configuration
- GitHub Actions workflows

**shiny**: Shiny application
- golem or rhino structure (configurable)
- Modular app organization
- Testing infrastructure

**clinical**: Clinical trial analysis
- Pharmaverse-ready structure
- Validation documentation templates
- TLF folder organization

### Options

- `renv`: Initialize renv for dependency management (default: yes)
- `targets`: Set up targets pipeline (default: yes for analysis)
- `git`: Initialize git repository (default: yes)
- `github`: Create GitHub repo structure (default: yes)
- `docker`: Include Dockerfile (default: no)
- `ci`: Include CI/CD workflows (default: yes)

## Example

```
/r-project-setup customer_churn analysis renv,targets,git
```

This creates an analysis project called "customer_churn" with renv, targets, and git.

## Files Created

### Core Files

**README.md**
```markdown
# Project Name

## Overview
Brief description of the project.

## Setup
Instructions for setting up the environment.

## Usage
How to run the analysis.

## Structure
Description of project organization.
```

**DESCRIPTION**
```
Type: project
Package: project_name
Title: Project Title
Version: 0.1.0
Authors@R: person("Name", "email@example.com", role = c("aut", "cre"))
Description: Project description.
License: MIT
```

### R Files

**R/utils.R**
- Common utility functions
- Data loading helpers
- Project-specific functions

### Configuration

**_targets.R** (if targets enabled)
```r
library(targets)

tar_option_set(
  packages = c("tidyverse", "tidymodels"),
  format = "qs"
)

list(
  tar_target(raw_data, read_data("data/raw/data.csv")),
  tar_target(clean_data, clean_data(raw_data)),
  tar_target(model, fit_model(clean_data)),
  tar_target(report, render_report(model))
)
```

**.Rprofile**
```r
source("renv/activate.R")

options(
  tidyverse.quiet = TRUE,
  scipen = 999
)
```

### GitHub Actions

**.github/workflows/check.yml**
- R CMD check
- Test coverage
- lint checking

**.github/workflows/targets.yml**
- Pipeline execution
- Caching

## Dependencies Installed

Standard analysis project includes:
- tidyverse
- tidymodels
- targets
- quarto
- gt, gtsummary
- here
- janitor

## Post-Setup Steps

After creation, the following manual steps are recommended:

1. Review and edit README.md with project-specific details
2. Add your data to data/raw/
3. Update _targets.R with your pipeline
4. Configure renv with additional packages: `renv::install("package")`
5. Push to GitHub if using version control

## Notes

- Project is created in a new subfolder
- All paths use the here package for portability
- Template files include helpful comments
- Configuration follows tidyverse best practices
