# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `scripts/validate-marketplace.py` validator that diffs `.claude-plugin/marketplace.json`
  against the actual plugin tree (agents, commands, skills, per-plugin `plugin.json`).
- GitHub Actions workflow `.github/workflows/validate.yml` that runs the validator
  on every push and pull request, preventing the registry from drifting out of sync.
- `CHANGELOG.md` and `CONTRIBUTING.md` at the repo root.
- Per-plugin documentation pages under `docs/` for the GitHub Pages site.
- Expanded `.gitignore` covering common R, Python, Stan, and Jekyll artifacts.

## [1.0.0] — 2026

### Added
- Initial public marketplace: 4 consolidated plugins, 30 agents, 17 commands, 45 skills.
- `bayesian-modeling` plugin: Stan, PyMC, JAGS, and WinBUGS support
  (6 agents / 3 commands / 9 skills).
- `itc-modeling` plugin: pairwise MA, NMA, MAIC, STC, and ML-NMR
  (7 agents / 2 commands / 6 skills).
- `r-tidy-modeling` plugin: tidyverse and tidymodels workflows for data
  science and biostatistics (10 agents / 7 commands / 23 skills).
- `clinical-trial-simulation` plugin: `simtrial` and `Mediana` frameworks
  (7 agents / 5 commands / 7 skills).
- GitHub Pages site at `docs/index.md`.
- Per-plugin `README.md` for each plugin.

### Changed
- Standardized spelling to American English (e.g. "modelling" → "modeling")
  throughout the codebase and documentation.
- Hardened plugin metadata and scientific guidance.

### Fixed
- Registered 11 r-tidy-modeling skills that were present on disk but missing
  from `marketplace.json` (`bc00536`).
