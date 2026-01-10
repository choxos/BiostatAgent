# ITC Analysis - Multi-Agent Evidence Synthesis Orchestration

Design and execute a complete indirect treatment comparison analysis for: $ARGUMENTS

## Thinking

This workflow orchestrates multiple specialized agents to conduct rigorous ITC analysis following NICE DSU guidance and tidy modelling principles. The approach emphasizes:

- **Phase-based coordination**: Each phase builds upon previous outputs with clear handoffs
- **Method-appropriate specialists**: Matching the right expert to the analytical task
- **Assumption transparency**: Explicit checking and documentation of all assumptions
- **Reproducibility**: Complete documentation for replication
- **Sensitivity analysis**: Multiple approaches to validate findings

The multi-agent approach ensures each aspect is handled by domain experts:
- ITC Architect selects methodology
- Appropriate specialists execute analysis
- Code Reviewer validates implementation

## Phase 1: Evidence Assessment & Method Selection

<Task>
subagent_type: itc-architect
prompt: |
  Assess the evidence structure and recommend ITC methodology for: $ARGUMENTS

  Deliverables:
  1. Evidence mapping:
     - Available studies and their characteristics
     - IPD vs AgD availability
     - Network structure and connectivity
     - Treatment comparisons of interest

  2. Population assessment:
     - Key population characteristics across studies
     - Potential effect modifiers
     - Population differences requiring adjustment

  3. Assumption evaluation:
     - Transitivity assessment (for NMA)
     - Effect modifier identification (for MAIC/STC)
     - Data requirements for each method

  4. Method recommendation:
     - Primary recommended method with justification
     - Alternative methods for sensitivity
     - Package recommendations (meta, netmeta, maicplus, stc, multinma)

  5. Analysis plan outline:
     - Key analyses to perform
     - Sensitivity analyses needed
     - Reporting requirements

  Provide clear rationale for method selection referencing NICE DSU TSD guidance.
</Task>

## Phase 2: Data Preparation

<Task>
subagent_type: itc-code-reviewer
prompt: |
  Review and prepare data for ITC analysis based on methodology: {phase1.itc-architect.output}

  Data preparation tasks:
  1. Data validation:
     - Check IPD structure and completeness
     - Validate AgD format and required fields
     - Identify missing values and handling strategy

  2. Effect size calculation (if needed):
     - Calculate study-level effect sizes
     - Variance estimation
     - Transformation to common scale

  3. Covariate preparation:
     - Identify effect modifiers to include
     - Calculate centering values from AgD
     - Prepare covariate summaries

  4. Data quality checks:
     - Outlier detection
     - Consistency checks
     - Documentation of data decisions

  Provide tidy R code following TMwR patterns with validation functions.
  Action: review_only (document issues and recommendations)
</Task>

## Phase 3: Primary Analysis

Execute primary analysis based on recommended method from Phase 1.

### If Pairwise Meta-Analysis:

<Task>
subagent_type: pairwise-meta-analyst
prompt: |
  Conduct pairwise meta-analysis based on: {phase1.itc-architect.output}
  Using prepared data from: {phase2.itc-code-reviewer.output}

  Analysis requirements:
  1. Primary analysis:
     - Fit both fixed and random effects models
     - Report effect estimate with 95% CI
     - Include prediction interval

  2. Heterogeneity assessment:
     - Q statistic and p-value
     - I², τ², H² with confidence intervals
     - Interpretation of heterogeneity level

  3. Publication bias (if ≥10 studies):
     - Funnel plot
     - Egger's/Peters' test
     - Trim-and-fill if indicated

  4. Visualizations:
     - Forest plot with study-level results
     - Funnel plot

  5. Sensitivity analyses:
     - Leave-one-out analysis
     - Fixed vs random effects comparison
     - Risk of bias subgroup (if available)

  Use meta or metafor package. Provide complete, reproducible R code.
</Task>

### If Network Meta-Analysis:

<Task>
subagent_type: nma-specialist
prompt: |
  Conduct network meta-analysis based on: {phase1.itc-architect.output}
  Using prepared data from: {phase2.itc-code-reviewer.output}

  Analysis requirements:
  1. Network assessment:
     - Network diagram
     - Evidence distribution
     - Multi-arm trial identification

  2. Primary NMA:
     - Fit consistency model (random effects)
     - All pairwise comparisons
     - League table

  3. Consistency assessment:
     - Global consistency test
     - Node-splitting for closed loops
     - Net heat plot

  4. Treatment rankings:
     - P-scores or SUCRA
     - Ranking probabilities
     - Cumulative ranking plots

  5. Sensitivity analyses:
     - Fixed vs random effects
     - Excluding specific studies
     - Frequentist vs Bayesian comparison

  Use netmeta (frequentist) and/or gemtc (Bayesian). Provide complete R code.
</Task>

### If MAIC:

<Task>
subagent_type: maic-specialist
prompt: |
  Conduct MAIC analysis based on: {phase1.itc-architect.output}
  Using prepared data from: {phase2.itc-code-reviewer.output}

  Analysis requirements:
  1. Weight estimation:
     - Define matching covariates
     - Center IPD on AgD targets
     - Estimate propensity weights
     - Bootstrap for variance

  2. Weight diagnostics:
     - ESS calculation and interpretation
     - Covariate balance assessment
     - Weight distribution summary
     - Extreme weight identification

  3. Anchored/Unanchored analysis:
     - Weighted outcome analysis
     - Effect estimates with bootstrap CI
     - Bucher indirect comparison (if anchored)

  4. Multiple endpoints (if applicable):
     - Binary, continuous, time-to-event
     - Consistent methodology across endpoints

  5. Sensitivity analyses:
     - Different covariate sets
     - Normalized vs unnormalized weights
     - Comparison with STC

  Use maicplus package. Provide complete R code with diagnostics.
</Task>

### If STC:

<Task>
subagent_type: stc-specialist
prompt: |
  Conduct STC analysis based on: {phase1.itc-architect.output}
  Using prepared data from: {phase2.itc-code-reviewer.output}

  Analysis requirements:
  1. Model specification:
     - Define effect modifiers
     - Center covariates on AgD population
     - Specify regression model with interactions

  2. Frequentist STC:
     - Fit outcome regression
     - Extract treatment effect at AgD population
     - Robust standard errors
     - Bucher indirect comparison (if anchored)

  3. Bayesian STC (sensitivity):
     - Prior specification
     - Posterior summaries
     - Credible intervals

  4. Model diagnostics:
     - Residual assessment
     - Interaction significance
     - Model fit statistics

  5. Sensitivity analyses:
     - Different covariate sets
     - With/without interactions
     - Comparison with MAIC

  Use stc package. Provide complete R code.
</Task>

### If ML-NMR:

<Task>
subagent_type: ml-nmr-specialist
prompt: |
  Conduct ML-NMR analysis based on: {phase1.itc-architect.output}
  Using prepared data from: {phase2.itc-code-reviewer.output}

  Analysis requirements:
  1. Network setup:
     - Set up IPD studies
     - Set up AgD studies
     - Combine network
     - Add integration points

  2. Model fitting:
     - Specify regression formula
     - Define priors
     - Fit ML-NMR model
     - Check convergence (R-hat, ESS, traces)

  3. Results extraction:
     - Relative effects for all comparisons
     - Treatment rankings
     - Predictions to target population

  4. Consistency assessment:
     - Node-splitting
     - Direct vs indirect comparison

  5. Sensitivity analyses:
     - Prior sensitivity
     - Integration point sensitivity
     - Covariate inclusion

  Use multinma package. Provide complete R code with convergence diagnostics.
</Task>

## Phase 4: Code Review & Validation

<Task>
subagent_type: itc-code-reviewer
prompt: |
  Review all analysis code from Phase 3 for methodological and code quality issues.

  Review checklist:
  1. Methodological correctness:
     - Appropriate method for data structure
     - Assumptions properly checked
     - Correct effect measures used
     - Proper uncertainty quantification

  2. Statistical issues:
     - Correct model specification
     - Appropriate inference methods
     - Multiple testing considerations
     - Sensitivity analyses adequate

  3. Code quality:
     - Tidy modelling compliance
     - Reproducibility (seeds, versions)
     - Error handling
     - Documentation

  4. Completeness:
     - All planned analyses performed
     - Diagnostics included
     - Visualizations appropriate

  Action: review_only
  Review type: comprehensive

  Provide detailed feedback with specific line references and recommendations.
</Task>

## Phase 5: Final Reporting

<Task>
subagent_type: itc-architect
prompt: |
  Synthesize all analysis results and prepare final report structure.

  Report components:
  1. Executive summary:
     - Key findings
     - Primary effect estimates
     - Strength of evidence

  2. Methods summary:
     - Data sources
     - Analytical approach
     - Key assumptions

  3. Results synthesis:
     - Primary analysis results
     - Sensitivity analysis results
     - Consistency of findings

  4. Limitations:
     - Data limitations
     - Methodological limitations
     - Assumption violations (if any)

  5. Conclusions:
     - Summary of evidence
     - Confidence in findings
     - Implications

  Provide structured report outline following NICE/PRISMA guidelines.
</Task>

## Configuration Options

- **primary_method**: pairwise_ma | nma | maic | stc | ml_nmr | auto (recommended by architect)
- **bayesian_analysis**: true | false (include Bayesian as sensitivity)
- **report_format**: comprehensive | summary
- **sensitivity_depth**: minimal | standard | extensive

## Success Criteria

1. **Method Selection**:
   - Appropriate for data structure
   - Justified with references to guidance

2. **Analysis Quality**:
   - All assumptions checked
   - Proper diagnostics performed
   - Sensitivity analyses completed

3. **Code Quality**:
   - Reproducible
   - Well-documented
   - Follows tidy principles

4. **Reporting**:
   - Complete and transparent
   - Follows PRISMA/NICE guidelines
   - Appropriate interpretation

## Final Deliverables

Upon completion, the orchestrated analysis will provide:
- Complete R code for all analyses
- Diagnostic output and visualizations
- Results tables (effect estimates, rankings)
- Sensitivity analysis comparison
- Final report structure
- Reproducibility documentation (session info, seeds)
