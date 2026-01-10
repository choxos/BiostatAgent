---
name: create-model
description: Interactive workflow for creating Bayesian models in Stan, JAGS, WinBUGS, or PyMC
---

# Bayesian Model Creation Workflow

You are helping the user create a Bayesian model. Follow this structured workflow:

## Step 1: Gather Requirements

Ask the user to specify:

1. **Model Type** (select one):
   - Hierarchical/Multilevel model
   - Regression model (linear, logistic, Poisson, etc.)
   - Time series model (AR, state-space, etc.)
   - Survival analysis model
   - Meta-analysis model

2. **Target Language**:
   - Stan with cmdstanr (DEFAULT for R - recommended)
   - PyMC 5 with ArviZ (DEFAULT for Python)
   - JAGS with R2jags
   - WinBUGS with R2WinBUGS (Windows only)

3. **Experience Level**:
   - Beginner (extensive comments, educational explanations)
   - Intermediate (standard documentation)
   - Advanced (minimal comments, efficiency-focused)

4. **Data Description**:
   - Outcome variable type (continuous, binary, count, time-to-event)
   - Predictor variables
   - Grouping structure (if hierarchical)
   - Sample sizes

5. **Prior Preferences** (optional):
   - Specific prior distributions
   - Informative vs weakly informative
   - Domain-specific constraints

## Step 2: Route to Specialist

Based on the target language:

- **Stan**: Use @stan-specialist with skills:
  - `stan-fundamentals` for syntax
  - Appropriate model type skill (hierarchical-models, regression-models, etc.)

- **PyMC**: Use @pymc-specialist with skills:
  - `pymc-fundamentals` for syntax
  - Appropriate model type skill

- **JAGS/WinBUGS**: Use @bugs-specialist with skills:
  - `bugs-fundamentals` for syntax
  - Appropriate model type skill

## Step 3: Generate Model

The specialist will provide:

1. **Complete model code** with appropriate comments based on experience level

2. **Integration code** (R or Python):
   - Data preparation
   - Model compilation/fitting
   - Basic diagnostics (posterior/ArviZ)

3. **Generated quantities** for:
   - Posterior predictive checks
   - Derived quantities of interest

## Step 4: Validate Output

Before presenting to user, verify:

- [ ] Model syntax is correct for target language
- [ ] All parameters have priors
- [ ] Parameterization is correct (SD for Stan/PyMC, precision for BUGS)
- [ ] Integration code is complete and runnable (R or Python)
- [ ] Comments match experience level

## Example Interaction

**User**: I need a model for patient outcomes nested within hospitals.

**Assistant**: I'll help you create a hierarchical model. Let me gather some details:

1. **Outcome type**: Is your outcome continuous (e.g., recovery time), binary (e.g., survived/died), or count (e.g., readmissions)?

2. **Predictors**: What patient-level and hospital-level variables do you want to include?

3. **Language preference**: Would you like Stan (R), PyMC (Python), or JAGS?

4. **Experience level**: How much detail would you like in the comments?

---

**Critical Reminders**:

- Default to Stan for R users, PyMC for Python users
- Always include complete integration code (R or Python)
- Warn about parameterization when relevant (SD for Stan/PyMC, precision for BUGS)
- Suggest non-centered parameterization for hierarchical models if appropriate
- For PyMC, remind users to use `pm.math` operations inside models
