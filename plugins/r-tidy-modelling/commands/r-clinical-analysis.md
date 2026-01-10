# R Clinical Analysis Workflow

Regulatory-compliant clinical trial analysis workflow. This command orchestrates the **biostatistician** agent with support from **viz-specialist** and **reporting-engineer** for comprehensive clinical data analysis.

## Workflow Steps

### 1. Data Validation
- Verify CDISC-compliant data structure (ADaM/SDTM)
- Check required variables for analysis type
- Validate data integrity and completeness

### 2. Population Definition
- Define analysis populations (ITT, mITT, PP, Safety)
- Generate disposition summary
- Create CONSORT diagram

### 3. Statistical Analysis
Perform analysis based on endpoint type:
- **Continuous endpoints**: MMRM, ANCOVA, change from baseline
- **Binary endpoints**: CMH, logistic regression, responder analysis
- **Time-to-event**: Kaplan-Meier, Cox regression, RMST
- **Count data**: Poisson/negative binomial models

### 4. Tables, Listings, and Figures (TLF)
Generate standard clinical outputs:
- Demographic tables (Table 14.1)
- Efficacy tables
- Safety tables (adverse events, labs)
- Forest plots for subgroups
- Kaplan-Meier curves

### 5. Report Generation
Compile analysis into regulatory-ready format:
- Statistical Analysis Report (SAR)
- Define file outputs
- Include validation documentation

## Usage

```
/r-clinical-analysis [data_path] [analysis_type] [output_format]
```

### Parameters
- `data_path`: Path to ADaM dataset(s) or directory
- `analysis_type`: One of `efficacy`, `safety`, `survival`, `pk`, `full`
- `output_format`: One of `html`, `pdf`, `rtf`, `docx` (default: html)

### Analysis Types

**efficacy**: Primary and secondary efficacy endpoints
- MMRM for repeated measures
- ANCOVA for single timepoints
- Responder analysis

**safety**: Safety analysis
- Adverse event summary
- Laboratory parameters
- Vital signs
- Exposure summary

**survival**: Time-to-event analysis
- Kaplan-Meier estimation
- Log-rank test
- Cox proportional hazards
- Landmark analysis

**pk**: Pharmacokinetic analysis
- Summary statistics
- Concentration-time profiles
- Non-compartmental analysis

**full**: Complete clinical study report analysis

## Output Location

```
output/
├── code/
│   └── clinical_analysis.R
├── reports/
│   └── statistical_analysis_report.html
├── tables/
│   ├── t_dm.rtf                # Demographics
│   ├── t_efficacy.rtf          # Efficacy
│   └── t_ae.rtf                # Adverse events
├── figures/
│   ├── f_km.png                # Kaplan-Meier
│   └── f_forest.png            # Forest plot
└── listings/
    └── l_ae.rtf                # AE listing
```

## Example

```
/r-clinical-analysis data/adsl.sas7bdat,data/adae.sas7bdat,data/adtte.sas7bdat full rtf
```

This performs complete clinical analysis and generates RTF outputs for regulatory submission.

## Regulatory Compliance

### ICH E9 Compliance
- Estimand specification
- Intercurrent event handling strategies
- Sensitivity analyses

### 21 CFR Part 11
- Audit trail documentation
- Version control
- Validation documentation

### CDISC Standards
- ADaM variable naming
- Standard analysis flags
- Define.xml compatibility

## Report Contents

1. **Executive Summary**
   - Key efficacy results
   - Safety summary
   - Conclusions

2. **Methods**
   - Analysis populations
   - Statistical methods
   - Handling of missing data

3. **Results**
   - Efficacy analyses
   - Safety analyses
   - Subgroup analyses

4. **Appendices**
   - Detailed tables
   - Statistical code
   - Validation documentation

## Packages Used

- **survival, survminer**: Survival analysis
- **mmrm**: Mixed models for repeated measures
- **emmeans**: Estimated marginal means
- **gtsummary, gt**: Clinical tables
- **rtables, tern**: Pharmaverse tables
- **haven**: SAS data import

## Notes

- All analyses follow pre-specified SAP
- Original data is never modified
- Validation documentation is generated
- Code is audit-ready with comments
