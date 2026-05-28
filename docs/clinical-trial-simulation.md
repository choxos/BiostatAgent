---
layout: default
title: clinical-trial-simulation
---

# clinical-trial-simulation

Clinical trial simulation supporting `simtrial` (time-to-event) and `Mediana`
(Clinical Scenario Evaluation) frameworks — for power analysis, sample-size
determination, group sequential designs, and multiplicity optimization.

**7 agents · 5 commands · 7 skills**

## Agents

- `simulation-architect` — entry point; selects the right simulation framework.
- `tte-specialist` — time-to-event simulation with `simtrial`.
- `cse-specialist` — Clinical Scenario Evaluation with `Mediana`.
- `multiplicity-expert` — gatekeeping, graphical procedures, alpha allocation.
- `gs-design-specialist` — group sequential boundaries (O'Brien-Fleming, Pocock, etc.).
- `power-optimizer` — sample size and design tuning under constraints.
- `code-reviewer` — review of trial-simulation R code.

## Commands

`/power-analysis`, `/sample-size`, `/gs-design`, `/multiplicity-optimization`,
`/cse-analysis`.

## Skills

`simtrial-fundamentals`, `mediana-fundamentals`, `multiplicity-methods`,
`time-to-event-methods`, `group-sequential-methods`,
`power-optimization-patterns`, `clinical-trial-design-patterns`.

## Source

Full README and source: [plugins/clinical-trial-simulation](https://github.com/choxos/BiostatAgent/tree/main/plugins/clinical-trial-simulation).

[← Back to overview](./)
