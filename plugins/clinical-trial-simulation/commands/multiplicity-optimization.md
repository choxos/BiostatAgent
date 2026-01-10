---
name: multiplicity-optimization
description: Optimize multiplicity adjustment selection including procedure choice and parameter tuning.
---

# Multiplicity Optimization Workflow

## Overview

Select and optimize multiplicity adjustment procedures for multi-arm or multi-endpoint trials while controlling FWER and maximizing power.

## Workflow Phases

### Phase 1: Hypothesis Structure

<Task>
subagent_type: multiplicity-expert
prompt: |
  Define hypothesis structure:
  1. List all hypotheses to be tested
  2. Identify clinical hierarchy (primary vs secondary)
  3. Define families (groups of related hypotheses)
  4. Specify testing order preferences
  5. Document dependencies between hypotheses
  6. Determine success criteria (any, all, weighted)
</Task>

### Phase 2: Procedure Selection

<Task>
subagent_type: multiplicity-expert
prompt: |
  Identify candidate procedures:
  1. Based on hypothesis structure, select candidates:
     - Independent: Holm, Hochberg
     - Hierarchical: Fixed-sequence, Chain
     - Families: Gatekeeping (parallel, multiple-sequence)
  2. Consider dependence assumptions
  3. Evaluate regulatory acceptability
  4. Recommend 2-3 procedures for comparison
</Task>

### Phase 3: Optimization

<Task>
subagent_type: power-optimizer
prompt: |
  Optimize procedure parameters:
  1. For each candidate procedure:
     - Grid search over parameters (weights, gamma)
     - Evaluate power for each configuration
     - Check FWER constraint under global null
  2. Find optimal parameters maximizing:
     - Primary endpoint power (subject to FWER ≤ alpha)
     - Overall weighted power
     - Minimum power across endpoints
  3. Compare optimized procedures
</Task>

### Phase 4: Sensitivity Analysis

<Task>
subagent_type: power-optimizer
prompt: |
  Assess robustness of selected procedure:
  1. Evaluate across treatment effect scenarios
  2. Test sensitivity to correlation assumptions
  3. Check performance if hierarchy changes
  4. Validate FWER under null (100,000+ simulations)
  5. Document trade-offs and recommendations
</Task>

## Success Criteria

- FWER controlled at alpha under all null configurations
- Power optimized for primary objective
- Procedure robust across scenarios
- Clear rationale for recommendation

## Final Deliverables

1. Recommended procedure with parameters
2. FWER validation results
3. Power comparison across procedures
4. Sensitivity analysis summary
5. R code for implementation

## Configuration Options

- `alpha`: FWER level (default: 0.025)
- `candidates`: List of procedures to compare
- `optimize_for`: "primary" or "weighted" or "minimum"
- `gamma_grid`: Truncation parameters to search
- `weight_options`: Weight allocations to consider
- `n_sims_power`: Sims for power (default: 10000)
- `n_sims_fwer`: Sims for FWER (default: 100000)
