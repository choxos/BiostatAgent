---
name: cse-analysis
description: Full Clinical Scenario Evaluation workflow using Mediana framework.
---

# Clinical Scenario Evaluation Workflow

## Overview

Comprehensive Clinical Scenario Evaluation (CSE) using the Mediana package to evaluate trial designs across multiple scenarios, analysis strategies, and success criteria.

## Workflow Phases

### Phase 1: Data Model Construction

<Task>
subagent_type: cse-specialist
prompt: |
  Build the Data Model:
  1. Select appropriate outcome distribution:
     - Continuous: NormalDist
     - Binary: BinomDist
     - Survival: ExpoDist, WeibullDist
     - Count: PoissonDist, NegBinomDist
     - Multivariate: MVNormalDist, MVExpoDist, etc.
  2. Define sample sizes or event counts to evaluate
  3. Specify treatment effect scenarios:
     - Conservative (pessimistic)
     - Expected (primary assumption)
     - Optimistic
  4. Configure design parameters (if event-driven):
     - Enrollment period and distribution
     - Study duration
     - Dropout rates
  5. Build complete DataModel object
</Task>

### Phase 2: Analysis Model Construction

<Task>
subagent_type: cse-specialist
prompt: |
  Build the Analysis Model:
  1. Define all statistical tests:
     - Match test method to endpoint type
     - Specify sample order correctly
  2. Add descriptive statistics for monitoring
  3. Configure multiplicity adjustments (if needed)
</Task>

<Task>
subagent_type: multiplicity-expert
condition: multiple_hypotheses == TRUE
prompt: |
  Add multiplicity adjustment to Analysis Model:
  1. Select appropriate procedure based on structure
  2. Configure procedure parameters
  3. Specify test ordering/families
  4. Validate FWER control
</Task>

### Phase 3: Evaluation Model

<Task>
subagent_type: cse-specialist
prompt: |
  Build the Evaluation Model:
  1. Define power criteria:
     - MarginalPower for individual tests
     - DisjunctivePower for "at least one"
     - ConjunctivePower for "all"
     - WeightedPower for prioritized
  2. Add summary statistics (means, counts)
  3. Ensure labels are clear for reporting
</Task>

### Phase 4: Simulation Execution

<Task>
subagent_type: cse-specialist
prompt: |
  Execute CSE and generate results:
  1. Configure SimParameters:
     - n.sims (10000+ for stable estimates)
     - proc.load (parallel computation)
     - seed (reproducibility)
  2. Run CSE()
  3. Extract and summarize results
  4. Generate Word report (optional)
</Task>

## Success Criteria

- All three models (Data, Analysis, Evaluation) complete
- Simulations run successfully
- Results interpretable and documented
- Report generated (if requested)

## Final Deliverables

1. Complete R code for CSE
2. Results summary table
3. Word report (optional)
4. Scenario comparison visualization
5. Recommendations based on results

## Configuration Options

- `n_sims`: Number of simulations (default: 10000)
- `proc_load`: "full", "high", "med", "low", or integer
- `generate_report`: TRUE/FALSE
- `report_sections`: Section organization for report
- `scenarios`: Named list of treatment effect scenarios
- `sample_sizes`: Vector of sample sizes to evaluate

## Example Structure

```r
# Data Model
data.model <- DataModel() +
  OutcomeDist(outcome.dist = "NormalDist") +
  SampleSize(seq(80, 120, 10)) +
  Sample(id = "Control", outcome.par = parameters(...)) +
  Sample(id = "Treatment", outcome.par = parameters(...))

# Analysis Model
analysis.model <- AnalysisModel() +
  Test(id = "Primary", samples = samples("Control", "Treatment"), method = "TTest") +
  MultAdjProc(proc = "HolmAdj")

# Evaluation Model
evaluation.model <- EvaluationModel() +
  Criterion(id = "Power", method = "MarginalPower",
            tests = tests("Primary"), par = parameters(alpha = 0.025))

# Run CSE
results <- CSE(data.model, analysis.model, evaluation.model,
               SimParameters(n.sims = 10000, proc.load = "full", seed = 12345))
```
