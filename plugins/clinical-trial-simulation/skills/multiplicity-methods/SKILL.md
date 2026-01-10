---
name: multiplicity-methods
description: Multiple testing procedures reference for clinical trials. Use when selecting or implementing multiplicity adjustments, gatekeeping procedures, or graphical approaches.
---

# Multiplicity Methods

## When to Use This Skill

- Selecting appropriate multiplicity adjustment procedures
- Implementing gatekeeping for primary/secondary endpoints
- Designing graphical testing procedures
- Optimizing truncation parameters (gamma)
- Ensuring FWER control in multi-arm/multi-endpoint trials

## Fundamental Concepts

### Family-Wise Error Rate (FWER)

FWER = P(reject at least one true null hypothesis)

Multiplicity adjustments control FWER at level α (typically 0.025 one-sided or 0.05 two-sided).

### Closed Testing Principle

A hypothesis H_i can be rejected at level α if and only if all intersection hypotheses containing H_i are rejected at level α.

This principle underlies most powerful multiplicity procedures.

## Single-Step Procedures

### Bonferroni

**Method:** Reject H_i if p_i ≤ α × w_i (where Σw_i = 1)

**Properties:**
- Most conservative
- Valid under any dependence
- Simple implementation

```r
MultAdjProc(proc = "BonferroniAdj",
            par = parameters(weight = c(0.5, 0.5)))
```

## Step-Down Procedures

### Holm Procedure

**Method:**
1. Order p-values: p_(1) ≤ p_(2) ≤ ... ≤ p_(m)
2. Reject H_(j) if p_(j) ≤ α/(m - j + 1) for all j ≤ i

**Properties:**
- More powerful than Bonferroni
- Valid under any dependence
- Consonant and coherent

```r
MultAdjProc(proc = "HolmAdj",
            par = parameters(weight = c(0.6, 0.4)))
```

### Fixed-Sequence Procedure

**Method:** Test hypotheses in predetermined order; stop at first non-rejection.

**Properties:**
- Maximum power for first hypothesis
- Zero power for later hypotheses if early ones fail
- Useful for clear hierarchy

```r
MultAdjProc(proc = "FixedSeqAdj")
# Tests in order defined in AnalysisModel
```

## Step-Up Procedures

### Hochberg Procedure

**Method:**
1. Order p-values: p_(1) ≤ p_(2) ≤ ... ≤ p_(m)
2. Find largest j where p_(j) ≤ α × j/m
3. Reject all H_(i) with p_(i) ≤ α × j/m

**Properties:**
- More powerful than Holm
- Requires positive dependence (PRDS) or independence
- Step-up → starts from largest p-value

```r
MultAdjProc(proc = "HochbergAdj",
            par = parameters(weight = c(0.5, 0.5)))
```

### Hommel Procedure

**Method:** More complex step-up based on Simes' inequality

**Properties:**
- Most powerful step-up procedure
- Requires PRDS or independence
- Computationally more intensive

```r
MultAdjProc(proc = "HommelAdj")
```

## Graphical Procedures

### Chain Procedure

Generalizes fixed-sequence with flexible weight transfer.

**Components:**
- Initial weights: w = (w_1, ..., w_m), Σw_i = 1
- Transition matrix: G where G_ij = weight transferred from H_i to H_j upon rejection

**Algorithm:**
1. Test each H_i at level α × w_i
2. Upon rejecting H_j, update: w_i ← w_i + w_j × G_ji, w_j ← 0

```r
# Equal split with full transfer
MultAdjProc(
  proc = "ChainAdj",
  par = parameters(
    weight = c(0.5, 0.5),
    transition = matrix(c(0, 1,
                          1, 0), 2, 2, byrow = TRUE)
  )
)
```

### Fallback Procedure

Special case of chain where rejected hypothesis passes weight to next in sequence.

```r
MultAdjProc(
  proc = "FallbackAdj",
  par = parameters(weight = c(0.5, 0.3, 0.2))
)
```

## Gatekeeping Procedures

### Parallel Gatekeeping

For trials with primary and secondary endpoint families where secondary can only be tested if at least one primary is rejected.

**Structure:**
- Family F_1 (primary): Must reject at least one to "open the gate"
- Family F_2 (secondary): Tested only after gate opens

**Components:**
- `family`: List of hypothesis indices per family
- `proc`: Procedure for each family
- `gamma`: Truncation parameter (0 = Bonferroni, 1 = Holm within family)

```r
MultAdjProc(
  proc = "ParallelGatekeepingAdj",
  par = parameters(
    family = families(
      family1 = c(1, 2),     # Primary (H1, H2)
      family2 = c(3, 4)      # Secondary (H3, H4)
    ),
    proc = families(
      family1 = "HolmAdj",
      family2 = "HolmAdj"
    ),
    gamma = families(
      family1 = 0.8,         # Truncation for primary
      family2 = 1            # Full Holm for secondary
    )
  ),
  tests = tests("Primary1", "Primary2", "Secondary1", "Secondary2")
)
```

### Multiple-Sequence Gatekeeping

For complex hierarchies with multiple sequences of hypotheses.

**Example:** Two doses (High, Low) each with primary and secondary endpoints.

```r
MultAdjProc(
  proc = "MultipleSequenceGatekeepingAdj",
  par = parameters(
    family = families(
      family1 = c(1, 2),     # Primary: DoseH, DoseL
      family2 = c(3, 4)      # Secondary: DoseH, DoseL
    ),
    proc = families(
      family1 = "HolmAdj",
      family2 = "HolmAdj"
    ),
    gamma = families(
      family1 = 0.8,
      family2 = 1
    )
  )
)
```

### Mixture Gatekeeping

Combines serial and parallel gatekeeping components.

**Components:**
- `serial`: Matrix indicating serial relationships
- `parallel`: Matrix indicating parallel relationships

```r
MultAdjProc(
  proc = "MixtureGatekeepingAdj",
  par = parameters(
    family = families(family1 = c(1), family2 = c(2, 3)),
    proc = families(family1 = "BonferroniAdj", family2 = "HolmAdj"),
    gamma = families(family1 = 1, family2 = 0.8),
    serial = matrix(c(0, 0, 0,
                      1, 0, 0,
                      1, 0, 0), 3, 3, byrow = TRUE),
    parallel = matrix(c(0, 0, 0,
                        0, 0, 0,
                        0, 1, 0), 3, 3, byrow = TRUE)
  )
)
```

## Parametric Procedures

### Normal Parametric

Uses correlation structure for more powerful testing when test statistics are multivariate normal.

```r
# Correlation from study design
corr.matrix <- matrix(c(1.0, 0.5, 0.5, 1.0), 2, 2)

MultAdjProc(
  proc = "NormalParamAdj",
  par = parameters(
    corr = corr.matrix,
    weight = c(0.5, 0.5)
  )
)
```

## Truncation Parameter (γ) Optimization

### Role of γ

- γ = 0: Bonferroni within family (most conservative)
- γ = 1: Holm within family (most powerful)
- 0 < γ < 1: Trade-off between error spending and power

### Optimization Strategy

1. Start with γ = 1 for all families
2. If simulated Type I error exceeds α, reduce γ for gatekeeper families
3. Binary search for optimal γ that maximizes power while controlling FWER

```r
# Compare multiple gamma values
gamma.values <- c(0.5, 0.6, 0.7, 0.8, 0.9, 1.0)

for (g in gamma.values) {
  mult.adj <- MultAdjProc(
    proc = "ParallelGatekeepingAdj",
    par = parameters(
      family = families(family1 = c(1, 2), family2 = c(3, 4)),
      proc = families(family1 = "HolmAdj", family2 = "HolmAdj"),
      gamma = families(family1 = g, family2 = 1)
    )
  )
  # Run CSE and record power
}
```

## Procedure Selection Guide

### By Hypothesis Structure

| Structure | Recommended Procedure |
|-----------|----------------------|
| Independent hypotheses | Holm or Hochberg |
| Strict hierarchy | Fixed-Sequence |
| Primary/Secondary | Parallel Gatekeeping |
| Multiple doses × endpoints | Multiple-Sequence |
| Complex dependencies | Graphical (Chain) |

### By Dependence Structure

| Dependence | Valid Procedures |
|------------|------------------|
| Any | Bonferroni, Holm |
| PRDS/Independent | Hochberg, Hommel |
| Known correlation | NormalParamAdj |

### By Power Priority

| Priority | Procedure |
|----------|-----------|
| First hypothesis | Fixed-Sequence |
| Equal priority | Holm with equal weights |
| Weighted priority | Graphical with weights |

## Common Patterns

### Two Primary + Two Secondary

```r
# H1, H2 = primary; H3, H4 = secondary
MultAdjProc(
  proc = "ParallelGatekeepingAdj",
  par = parameters(
    family = families(family1 = c(1, 2), family2 = c(3, 4)),
    proc = families(family1 = "HolmAdj", family2 = "HolmAdj"),
    gamma = families(family1 = 0.8, family2 = 1)
  )
)
```

### Three Doses vs Placebo

```r
# All pairwise comparisons with equal weight
MultAdjProc(
  proc = "HolmAdj",
  par = parameters(weight = c(1/3, 1/3, 1/3))
)
```

### Hierarchical Endpoints

```r
# Primary → Key Secondary → Other Secondary
MultAdjProc(proc = "FixedSeqAdj")
```

### Graphical with Recycling

```r
# Two primary with full recycling
MultAdjProc(
  proc = "ChainAdj",
  par = parameters(
    weight = c(0.5, 0.5),
    transition = matrix(c(0, 1,
                          1, 0), 2, 2, byrow = TRUE)
  )
)
```

## FWER Validation

Always validate FWER control under the global null:

```r
# Set all treatment effects to null
null.data.model <- DataModel() +
  OutcomeDist(outcome.dist = "NormalDist") +
  SampleSize(100) +
  Sample(id = "Control", outcome.par = parameters(mean = 0, sd = 1)) +
  Sample(id = "Treatment", outcome.par = parameters(mean = 0, sd = 1))

# Check rejection rate ≤ alpha
null.results <- CSE(null.data.model, analysis.model, evaluation.model,
                    SimParameters(n.sims = 100000, proc.load = "full", seed = 123))

# DisjunctivePower under null = simulated FWER
# Should be ≤ 0.025 (one-sided)
```

## Best Practices

1. **Start Conservative**: Begin with Holm/Bonferroni, add complexity as needed
2. **Validate FWER**: Always check Type I error under global null
3. **Document Hierarchy**: Clearly specify hypothesis ordering rationale
4. **Optimize γ**: Use simulation to find optimal truncation parameters
5. **Consider Correlation**: Use parametric methods when correlation is known
6. **Plan Pre-Specification**: Multiplicity strategy must be pre-specified in SAP
