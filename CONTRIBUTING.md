# Contributing to BiostatAgent

Thank you for considering a contribution! BiostatAgent is a Claude Code plugin
marketplace that ships agents, commands, and skills for biostatistics workflows
in R. This guide explains how to add new content and how to keep the marketplace
registry in sync with the filesystem.

## Repository layout

```
.
├── .claude-plugin/marketplace.json   # Source of truth for all 4 plugins
├── plugins/
│   ├── bayesian-modeling/
│   ├── clinical-trial-simulation/
│   ├── itc-modeling/
│   └── r-tidy-modeling/
│       ├── .claude-plugin/plugin.json
│       ├── agents/<agent>.md
│       ├── commands/<command>.md
│       ├── skills/<skill>/SKILL.md (and any supporting files)
│       └── README.md
├── docs/                             # GitHub Pages site
├── scripts/validate-marketplace.py   # Registry-vs-filesystem validator
└── .github/workflows/validate.yml    # CI runs the validator
```

## Adding a new agent, command, or skill

1. **Create the file(s) in the right plugin.**
   - Agent: `plugins/<plugin>/agents/<name>.md` (single Markdown file with
     YAML front matter declaring the agent's `name`, `description`, etc.).
   - Command: `plugins/<plugin>/commands/<name>.md` (single Markdown file).
   - Skill: `plugins/<plugin>/skills/<name>/` (a directory; conventionally
     contains a `SKILL.md` plus any supporting assets).

2. **Register it in `.claude-plugin/marketplace.json`.** Add the relative path
   to the appropriate `agents`, `commands`, or `skills` array of the plugin's
   entry. Paths are relative to the plugin source and start with `./`. Example:

   ```json
   "skills": [
     "./skills/existing-skill",
     "./skills/my-new-skill"
   ]
   ```

3. **Update the plugin's `README.md`** if it lists agents/commands/skills, and
   update the top-level `README.md` totals if they would change.

4. **Update `CHANGELOG.md`** under the `Unreleased` section.

5. **Run the validator locally** before committing:

   ```bash
   python3 scripts/validate-marketplace.py
   ```

   The same script runs in CI on every push and pull request; if you forget to
   register a new file (or remove one without updating the registry), the
   workflow will fail with a clear diff.

## Style notes

- **American English** throughout the codebase and documentation
  (e.g. "modeling", not "modelling"). This was standardized in commit
  `c278748` and is the project default.
- Keep agent/command/skill **names in kebab-case** matching their filename.
- Prefer **concise, focused agents and skills** over large monoliths.

## Versioning

This repository follows [Semantic Versioning](https://semver.org/). Bump the
plugin's own `version` in its `.claude-plugin/plugin.json` when its agents,
commands, or skills change in a user-visible way, and reflect the change in
`CHANGELOG.md`.

## Reporting issues

Please open a GitHub issue describing:
- Which plugin / agent / skill / command is affected.
- The behavior you expected and what happened.
- A minimal reproduction (R code, data, prompt) when possible.
