# ITC Code Review - Expert R Code Analysis and Amendment

Review ITC analysis code for: $ARGUMENTS

## Purpose

Comprehensive review of R code for indirect treatment comparison analyses (pairwise MA, NMA, MAIC, STC, ML-NMR) by an expert combining world-class ITC methodology knowledge with rigorous software engineering practices.

## Review Options

Specify your preferences:

- **review_type**: `comprehensive` (detailed) | `summary` (bullet points)
- **action**: `review_only` | `amend` (create corrected code in subfolder)
- **output_folder**: Path for amended files (default: `./amended/`)
- **focus_areas**: Specific concerns (optional)

## Review Workflow

<Task>
subagent_type: itc-code-reviewer
prompt: |
  Conduct expert review of ITC analysis code: $ARGUMENTS

  ## Review Configuration
  - Review type: {review_type} (comprehensive or summary)
  - Action: {action} (review_only or amend)
  - Output folder: {output_folder}
  - Focus areas: {focus_areas}

  ## Step 1: Understand the Analysis

  Before reviewing, understand:
  - What ITC method is being used?
  - What is the research question?
  - What data structure is present?
  - What packages are being used?

  ## Step 2: Methodological Review

  Check for issues in these areas:

  ### Pairwise Meta-Analysis (meta, metafor, bayesmeta)
  - [ ] Correct effect measure for outcome type
  - [ ] Appropriate fixed vs random effects choice
  - [ ] Heterogeneity properly assessed (Q, I², τ², prediction interval)
  - [ ] Publication bias addressed (if ≥10 studies)
  - [ ] Sensitivity analyses included
  - [ ] Forest plot generated
  - [ ] Knapp-Hartung adjustment used (if applicable)

  ### Network Meta-Analysis (netmeta, gemtc)
  - [ ] Network connectivity verified
  - [ ] Transitivity assumption assessed
  - [ ] Consistency tested (node-splitting, net heat)
  - [ ] Multi-arm correlations handled
  - [ ] Rankings reported with uncertainty
  - [ ] Convergence checked (Bayesian)
  - [ ] Priors specified and justified (Bayesian)

  ### MAIC (maicplus)
  - [ ] Covariate selection justified
  - [ ] ESS calculated and acceptable
  - [ ] Weight diagnostics checked
  - [ ] Covariate balance verified
  - [ ] Anchored vs unanchored appropriate
  - [ ] Bootstrap CI used
  - [ ] Comparison with STC (sensitivity)

  ### STC (stc)
  - [ ] Effect modifiers identified and justified
  - [ ] Covariates centered on AgD population
  - [ ] Treatment-covariate interactions included
  - [ ] Robust SE used
  - [ ] Model diagnostics checked
  - [ ] Comparison with MAIC (sensitivity)

  ### ML-NMR (multinma)
  - [ ] Integration points sufficient
  - [ ] Convergence diagnostics (R-hat, ESS)
  - [ ] Priors specified and sensitivity tested
  - [ ] Node-splitting for consistency
  - [ ] Target population specified
  - [ ] Predictions properly marginalized

  ## Step 3: Statistical Review

  - [ ] Correct variance calculations
  - [ ] Proper confidence/credible intervals
  - [ ] Appropriate hypothesis tests
  - [ ] Multiple testing addressed
  - [ ] Effect size interpretation correct
  - [ ] Uncertainty properly propagated

  ## Step 4: Code Quality Review

  ### Tidy Modelling Compliance (TMwR)
  - [ ] Consistent interfaces
  - [ ] Recipe-like data preparation
  - [ ] Results as tibbles
  - [ ] Workflow structure clear

  ### R Best Practices
  - [ ] Vectorization over loops
  - [ ] Appropriate functions used
  - [ ] Memory efficiency
  - [ ] Error handling present
  - [ ] Input validation

  ### Reproducibility
  - [ ] Seeds set for stochastic operations
  - [ ] Package versions documented
  - [ ] Complete session info available
  - [ ] Data provenance clear

  ### Documentation
  - [ ] Functions documented
  - [ ] Code comments explain "why"
  - [ ] Analysis narrative present
  - [ ] Results interpretation included

  ## Step 5: Generate Output

  ### If review_type = "comprehensive":
  Provide detailed analysis:
  - Line-by-line issues with file:line references
  - Methodology background for each issue
  - Complete corrected code examples
  - References to guidelines

  ### If review_type = "summary":
  Provide concise output:
  - Bullet-point issue list
  - Priority categorization (Critical/Major/Minor)
  - One-line recommendations

  ### If action = "amend":
  Create files in output_folder:
  ```
  {output_folder}/
  ├── {filename}_amended.R    # Corrected code
  ├── REVIEW_NOTES.md         # Change summary
  └── backup/
      └── {filename}_original.R
  ```

  ## Step 6: REVIEW_NOTES.md Structure

  ```markdown
  # ITC Code Review - {date}

  ## Summary
  - Total issues: X (Y Critical, Z Major, W Minor)
  - Files reviewed: [list]
  - Files amended: [list]

  ## Critical Issues
  [Detailed description of each critical issue]

  ## Major Issues
  [Detailed description of each major issue]

  ## Minor Issues
  [Brief description of minor issues]

  ## Recommendations
  - Additional analyses to consider
  - Best practice improvements

  ## Changes Made (if amended)
  - [List of specific changes per file]

  ## Package Versions
  [Document all package versions used]
  ```

  ## Issue Priority Definitions

  **Critical**: Could invalidate results
  - Wrong method for data structure
  - Major assumption violation
  - Incorrect statistical calculation
  - Missing essential diagnostics

  **Major**: Significantly impacts quality
  - Missing important sensitivity analysis
  - Suboptimal method choice
  - Incomplete diagnostics
  - Poor reproducibility

  **Minor**: Best practice improvements
  - Code style issues
  - Documentation gaps
  - Efficiency improvements
  - Minor formatting issues

  Proceed with the review following these guidelines.
</Task>

## Output Deliverables

Based on configuration, the review will provide:

### review_only Mode
- Comprehensive or summary review document
- Issue list with priorities
- Specific recommendations with code examples
- No files modified

### amend Mode
All of the above, plus:
- Amended code files in subfolder
- REVIEW_NOTES.md with change summary
- Backup of original files
- Original files NEVER modified

## Example Usage

```
# Comprehensive review only
Review my NMA analysis in analysis/nma_analysis.R
review_type: comprehensive
action: review_only

# Summary review with amendments
Review my MAIC code and fix issues
review_type: summary
action: amend
output_folder: ./reviewed/

# Focused review
Review the convergence diagnostics in my ML-NMR analysis
focus_areas: convergence, priors
```

## Safety Guarantees

- Original files are NEVER modified directly
- All amendments go to specified subfolder
- Backup copies created before any changes
- Clear documentation of all modifications
- Reversible changes only
