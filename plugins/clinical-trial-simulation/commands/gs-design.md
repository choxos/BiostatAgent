---
name: gs-design
description: Design group sequential trials with interim analyses, alpha spending, and futility stopping.
---

# Group Sequential Design Workflow

## Overview

Design and simulate group sequential trials with interim analyses for early stopping due to efficacy or futility.

## Workflow Phases

### Phase 1: Design Specification

<Task>
subagent_type: gs-design-specialist
prompt: |
  Specify group sequential design:
  1. Number of analyses (interim + final)
  2. Information fractions (timing of analyses)
  3. Alpha spending function (OBF, Pocock, HSD)
  4. Futility stopping rules (binding vs non-binding)
  5. Integration with gsDesign2 (if applicable)
  6. Stopping boundaries derivation
</Task>

### Phase 2: Simulation Setup

<Task>
subagent_type: tte-specialist
prompt: |
  Configure GS simulation with simtrial:
  1. Define enrollment rates
  2. Define failure rates (under H0 and H1)
  3. Create cutting functions with create_cut()
  4. Configure sim_gs_n() parameters
  5. Set up test functions (create_test())
  6. Link to original_design for bound updates
</Task>

### Phase 3: Boundary Calculation

<Task>
subagent_type: gs-design-specialist
prompt: |
  Calculate and validate boundaries:
  1. Compute efficacy boundaries using spending function
  2. Compute futility boundaries (if applicable)
  3. Verify cumulative alpha spending ≤ alpha
  4. Check information fraction assumptions
  5. Document boundary derivation
</Task>

### Phase 4: Operating Characteristics

<Task>
subagent_type: power-optimizer
prompt: |
  Evaluate GS design performance:
  1. Simulate under H1 (treatment effect present):
     - Overall power
     - Stopping probabilities at each analysis
     - Expected sample size/events
  2. Simulate under H0 (no effect):
     - Type I error at each analysis
     - Overall FWER
     - Expected sample size under null
  3. Compare to fixed design:
     - Expected sample size savings
     - Power trade-off
</Task>

## Success Criteria

- Boundaries derived and documented
- Type I error controlled at alpha
- Power meets target under alternative
- Operating characteristics fully characterized
- Design integrates with gsDesign2

## Final Deliverables

1. Design specification with boundaries
2. Boundary table (analysis, efficacy Z, futility Z)
3. Operating characteristics summary
4. sim_gs_n() code for replication
5. Comparison to fixed design

## Configuration Options

- `n_analyses`: Number of analyses (default: 3)
- `info_frac`: Information fractions (default: evenly spaced)
- `alpha_spending`: "OBF", "Pocock", or list(sf=, param=)
- `futility`: TRUE/FALSE (default: TRUE)
- `futility_binding`: TRUE/FALSE (default: FALSE)
- `n_sim_h1`: Simulations under H1 (default: 10000)
- `n_sim_h0`: Simulations under H0 (default: 100000)
