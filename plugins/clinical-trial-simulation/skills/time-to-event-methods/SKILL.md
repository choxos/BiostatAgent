---
name: time-to-event-methods
description: Survival analysis methods including weighted logrank, MaxCombo, RMST, and milestone tests. Use when analyzing TTE data or choosing analysis methods for non-proportional hazards.
---

# Time-to-Event Methods

## When to Use This Skill

- Selecting appropriate analysis methods for survival endpoints
- Handling non-proportional hazards scenarios
- Implementing weighted logrank tests
- Designing MaxCombo tests
- Using RMST or milestone endpoints

## Analysis Methods Overview

### Standard Logrank Test

**When Optimal:**
- Proportional hazards assumption holds
- Treatment effect constant over time

**Formula:**
```
Z = Σ(O_trt - E_trt) / √(Var)
```

**simtrial Implementation:**
```r
data |> wlr(weight = fh(rho = 0, gamma = 0))
```

### Fleming-Harrington Weighted Logrank

**Weight Function:**
```
w(t) = S(t)^ρ × (1 - S(t))^γ
```

**Parameter Effects:**

| ρ | γ | Emphasis | Best For |
|---|---|----------|----------|
| 0 | 0 | Uniform (standard LR) | Proportional hazards |
| 0 | 0.5 | Moderate late | Moderate delayed effect |
| 0 | 1 | Strong late | Strong delayed effect |
| 1 | 0 | Early | Early divergence |
| 0.5 | 0.5 | Balanced | Crossing hazards |

**simtrial Implementation:**
```r
# Late emphasis
data |> wlr(weight = fh(rho = 0, gamma = 0.5))

# Early emphasis
data |> wlr(weight = fh(rho = 1, gamma = 0))
```

### Magirr-Burman (MB) Weights

**Design:** Zero weight before delay, then increasing weight.

**Parameters:**
- `delay`: Time before weights increase
- `w_max`: Maximum weight cap

**Formula:**
```
w(t) = min(w_max, S(min(t, τ*))^(-1))
```

**When to Use:**
- Known delay in treatment effect
- Clear scientific rationale for delay period

**simtrial Implementation:**
```r
# 4-month delay, max weight 2
data |> wlr(weight = mb(delay = 4, w_max = 2))

# Unlimited weight growth
data |> wlr(weight = mb(delay = 6, w_max = Inf))
```

### Early Zero Weights (Xu et al., 2017)

**Design:** Exactly zero weight for early period, then standard logrank.

**When to Use:**
- Want to completely ignore early period
- Regulatory acceptance of early exclusion

**simtrial Implementation:**
```r
# Zero weight for first 6 months
data |> wlr(weight = early_zero(early_period = 6))
```

### MaxCombo Test

**Concept:** Combine multiple weighted logrank tests, take maximum Z-score.

**Advantages:**
- Robust across NPH patterns
- Maintains power under uncertainty
- Single pre-specified p-value

**Common Combinations:**

| Combo | Tests | Use Case |
|-------|-------|----------|
| 2-test | FH(0,0) + FH(0,1) | Unknown late effect |
| 3-test | FH(0,0) + FH(0,0.5) + FH(0.5,0.5) | Comprehensive |
| Custom | FH(0,0) + FH(0,1) + FH(1,1) | Maximum robustness |

**simtrial Implementation:**
```r
# Two-test MaxCombo
data |> maxcombo(rho = c(0, 0), gamma = c(0, 1))

# Three-test MaxCombo
data |> maxcombo(rho = c(0, 0, 0.5), gamma = c(0, 0.5, 0.5))
```

**Correlation Handling:**
MaxCombo accounts for correlation between tests using multivariate normal distribution.

### Restricted Mean Survival Time (RMST)

**Definition:** Area under survival curve up to time τ.

**Formula:**
```
RMST(τ) = ∫₀^τ S(t) dt
```

**Advantages:**
- Interpretable (expected survival time)
- Valid under non-PH
- No proportionality assumption

**Considerations:**
- Choice of τ is critical
- τ must be within follow-up
- Less powerful than logrank under PH

**simtrial Implementation:**
```r
data |> rmst(tau = 24)  # RMST at 24 months
```

### Milestone Analysis

**Definition:** Compare survival probability at fixed time point.

**Test Statistic:**
```
Z = (S_trt(t*) - S_ctrl(t*)) / SE
```

**Advantages:**
- Easy to interpret
- Clinically meaningful time point
- Valid under non-PH

**simtrial Implementation:**
```r
data |> milestone(ms_time = 12, test_type = "naive")
```

## Non-Proportional Hazards Patterns

### Delayed Treatment Effect

**Pattern:** HR = 1 initially, then HR < 1

**Analysis Recommendations:**
1. Primary: FH(0, γ) with γ > 0 or MaxCombo
2. Sensitivity: Standard logrank
3. Alternative: RMST with appropriate τ

**Simulation Setup:**
```r
fail_rate <- data.frame(
  stratum = rep("All", 4),
  period = rep(1:2, 2),
  treatment = c(rep("control", 2), rep("experimental", 2)),
  duration = c(4, 100, 4, 100),  # 4-month delay
  rate = log(2) / c(12, 12, 12, 18)  # HR=1 then HR=0.67
)
```

### Crossing Hazards

**Pattern:** Early benefit reverses over time

**Analysis Recommendations:**
1. Consider if crossing is clinically meaningful
2. FH(0.5, 0.5) may be appropriate
3. MaxCombo provides robustness
4. RMST with carefully chosen τ

### Diminishing Effect

**Pattern:** Strong early effect that wanes

**Analysis Recommendations:**
1. FH(ρ, 0) with ρ > 0
2. Early milestone analysis
3. Consider if effect is clinically durable

### Cure Model

**Pattern:** Proportion of patients cured (never event)

**Analysis Recommendations:**
1. Standard logrank often adequate
2. Long-term milestone helpful
3. Consider cure fraction estimation

## Method Selection Algorithm

```
START
  │
  ├─ Is proportional hazards expected?
  │   ├─ Yes → Standard logrank FH(0,0)
  │   └─ No → Continue
  │
  ├─ Is delayed effect expected?
  │   ├─ Yes, delay known → MB weights
  │   ├─ Yes, delay uncertain → FH(0, 0.5) or MaxCombo
  │   └─ No → Continue
  │
  ├─ Is crossing possible?
  │   ├─ Yes → RMST or FH(0.5, 0.5)
  │   └─ No → Continue
  │
  ├─ Maximum robustness needed?
  │   ├─ Yes → MaxCombo
  │   └─ No → FH(0, γ) based on expected pattern
  │
END
```

## Power Comparison Under Different Scenarios

### Proportional Hazards (HR = 0.7)

| Method | Relative Power |
|--------|---------------|
| Logrank FH(0,0) | 100% (optimal) |
| FH(0, 0.5) | ~95% |
| MaxCombo | ~98% |
| RMST | ~90% |

### Delayed Effect (3-month delay, HR = 0.6 after)

| Method | Relative Power |
|--------|---------------|
| Logrank FH(0,0) | 70% |
| FH(0, 0.5) | 90% |
| MB(delay=3) | 95% |
| MaxCombo | 92% |

### Crossing Hazards

| Method | Relative Power |
|--------|---------------|
| Logrank FH(0,0) | Variable |
| FH(0.5, 0.5) | Better |
| RMST | Depends on τ |
| MaxCombo | Robust |

## Practical Considerations

### Regulatory Acceptance

- FDA generally accepts weighted logrank with justification
- Pre-specification is critical
- MaxCombo gaining acceptance
- RMST as sensitivity analysis

### Pre-specification Requirements

1. Analysis method must be specified before unblinding
2. Weight parameters (ρ, γ) must be fixed
3. MaxCombo test components must be defined
4. τ for RMST must be justified

### Sample Size Implications

- Weighted tests may require larger sample under PH
- MaxCombo has slight efficiency loss
- Consider this in planning

## Best Practices

1. **Primary Analysis**: Choose method aligned with expected NPH pattern
2. **Sensitivity Analyses**: Include standard logrank and alternatives
3. **Justification**: Document scientific rationale for method choice
4. **Simulation**: Validate power across plausible scenarios
5. **Pre-specification**: Lock method before any data review
