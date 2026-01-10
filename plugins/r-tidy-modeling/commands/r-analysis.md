# R Data Analysis Workflow

Comprehensive data analysis workflow using tidy principles. This command orchestrates multiple agents to perform end-to-end data analysis.

## Workflow Steps

### 1. Data Assessment
First, the **data-wrangler** agent will:
- Load and inspect the data structure
- Identify variable types and distributions
- Check for missing values and data quality issues
- Document data cleaning requirements

### 2. Data Preparation
The **feature-engineer** agent will:
- Create preprocessing recipe based on data characteristics
- Handle missing data appropriately
- Encode categorical variables
- Create derived features if needed
- Document all transformations

### 3. Exploratory Analysis
The **viz-specialist** agent will:
- Create distribution plots for key variables
- Generate correlation analyses
- Produce visualizations for relationships of interest
- Create publication-ready figures

### 4. Statistical Analysis
Based on the analysis type, the appropriate agent will be engaged:
- **biostatistician** for inferential statistics, survival analysis, clinical endpoints
- **tidymodels-engineer** for predictive modeling and machine learning

### 5. Results Documentation
The **reporting-engineer** agent will:
- Compile analysis results into a reproducible report
- Include all code, outputs, and interpretations
- Generate appropriate output format (HTML, PDF, Word)

## Usage

```
/r-analysis [data_path] [analysis_type] [output_format]
```

### Parameters
- `data_path`: Path to the dataset (CSV, RDS, Excel, etc.)
- `analysis_type`: One of `descriptive`, `inferential`, `predictive`, `survival`, `clinical`
- `output_format`: One of `html`, `pdf`, `word` (default: html)

## Output Location

All outputs will be written to:
```
output/
├── code/           # R scripts for reproducibility
├── reports/        # Analysis report
├── figures/        # Generated visualizations
└── models/         # Saved model objects (if applicable)
```

## Example

```
/r-analysis data/patient_outcomes.csv survival html
```

This will perform survival analysis on the patient outcomes data and generate an HTML report.

## Notes

- All code is generated in the output folder - your original data files are never modified
- The workflow adapts based on data characteristics discovered during assessment
- Interactive mode will ask clarifying questions about analysis goals
