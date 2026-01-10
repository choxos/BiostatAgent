---
name: power-analysis
description: Calculate power for various clinical trial designs using simtrial or Mediana frameworks.
---

# Power Analysis Workflow

## Overview

Calculate statistical power for clinical trial designs across multiple scenarios, analysis methods, and design parameters.

## Workflow Phases

### Phase 1: Requirements Gathering

<Task>
subagent_type: simulation-architect
prompt: |
  Gather requirements for power analysis:
  1. What is the primary endpoint type? (continuous, binary, time-to-event, count)
  2. What is the trial design? (two-arm, multi-arm, multi-endpoint)
  3. What are the treatment effect assumptions? (conservative, expected, optimistic)
  4. What is the target power level?
  5. What is the Type I error rate (alpha)?
  6. Are there any special considerations? (non-proportional hazards, multiplicity, stratification)

  Based on responses, determine whether to use simtrial (TTE) or Mediana (CSE) framework.
</Task>

### Phase 2: Model Selection

<Task>
subagent_type: tte-specialist
condition: endpoint_type == "time-to-event"
prompt: |
  Set up simtrial-based power analysis:
  1. Configure fail_rate for piecewise exponential model
  2. Set up enrollment rates
  3. Define data cutting strategy (events or calendar)
  4. Select analysis method (logrank, weighted, MaxCombo)
  5. Prepare sim_fixed_n() or sim_gs_n() parameters
</Task>

<Task>
subagent_type: cse-specialist
condition: endpoint_type != "time-to-event" OR multi_scenario == TRUE
prompt: |
  Set up Mediana CSE-based power analysis:
  1. Build DataModel with appropriate distribution
  2. Define multiple sample size or event count scenarios
  3. Configure treatment effect scenarios
  4. Build AnalysisModel with tests
  5. Build EvaluationModel with power criteria
</Task>

### Phase 3: Power Calculation

<Task>
subagent_type: power-optimizer
prompt: |
  Execute power simulations:
  1. Run simulations across all scenarios
  2. Calculate power at each scenario combination
  3. Generate power curves
  4. Identify scenarios meeting target power
  5. Summarize operating characteristics
</Task>

### Phase 4: Review

<Task>
subagent_type: code-reviewer
prompt: |
  Review power analysis code and results:
  1. Validate simulation parameters
  2. Check statistical assumptions
  3. Verify reproducibility (seeds)
  4. Confirm power calculations are correct
  5. Flag any potential issues
</Task>

## Success Criteria

- Power calculated for all specified scenarios
- Results validated by code reviewer
- Clear power curves or tables generated
- Assumptions documented
- Reproducible code provided

## Final Deliverables

1. R code for power analysis
2. Power summary table by scenario
3. Power curves (if applicable)
4. Documentation of assumptions
5. Sensitivity analysis results

## Configuration Options

- `framework`: "simtrial" or "mediana" or "auto"
- `n_sims`: Number of simulations (default: 10000)
- `alpha`: Type I error rate (default: 0.025)
- `target_power`: Target power level (default: 0.90)
- `scenarios`: List of treatment effect scenarios
- `parallel`: Enable parallel computation (default: TRUE)
