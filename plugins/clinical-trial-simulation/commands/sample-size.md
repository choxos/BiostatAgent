---
name: sample-size
description: Determine sample sizes given power requirements using simulation-based optimization.
---

# Sample Size Determination Workflow

## Overview

Find the minimum sample size (or event count) required to achieve target power across specified treatment effect scenarios.

## Workflow Phases

### Phase 1: Requirements

<Task>
subagent_type: simulation-architect
prompt: |
  Gather sample size requirements:
  1. Target power level (e.g., 90%)
  2. Type I error rate (alpha)
  3. Primary endpoint type
  4. Treatment effect assumptions (range of plausible effects)
  5. Any constraints (max N, budget, timeline)
  6. Robustness requirements (power across scenarios)
</Task>

### Phase 2: Search Strategy

<Task>
subagent_type: power-optimizer
prompt: |
  Implement sample size search:
  1. Define sample size grid or binary search range
  2. For each candidate N:
     - Run power simulations
     - Record power at each scenario
  3. Find minimum N achieving target power
  4. Calculate optimal interval (range of acceptable N)
  5. Determine joint optimal region across scenarios

  Methods:
  - Binary search: Efficient for single scenario
  - Grid search: Better for multiple scenarios
  - Compound criteria: Min power across scenarios ≥ target
</Task>

### Phase 3: Validation

<Task>
subagent_type: tte-specialist
condition: endpoint_type == "time-to-event"
prompt: |
  Validate sample size for TTE endpoint:
  1. Confirm power at recommended N using sim_fixed_n()
  2. Run validation simulations (larger n_sims)
  3. Compare to analytical approximation
  4. Check event count assumptions
</Task>

<Task>
subagent_type: cse-specialist
condition: endpoint_type != "time-to-event"
prompt: |
  Validate sample size using CSE:
  1. Confirm power at recommended N
  2. Generate detailed results across scenarios
  3. Prepare presentation-ready output
</Task>

## Success Criteria

- Sample size found meeting target power
- Results validated with high-precision simulation
- Sensitivity across scenarios documented
- Clear recommendation with rationale

## Final Deliverables

1. Recommended sample size with justification
2. Power at recommended N for all scenarios
3. Sample size sensitivity table
4. Optimal interval analysis
5. R code for replication

## Configuration Options

- `target_power`: Target power (default: 0.90)
- `alpha`: Type I error rate (default: 0.025)
- `search_method`: "binary" or "grid"
- `n_range`: Sample size search range (e.g., c(50, 500))
- `scenarios`: Treatment effect scenarios
- `robustness`: "expected" (optimize for expected) or "conservative" (ensure power under conservative)
