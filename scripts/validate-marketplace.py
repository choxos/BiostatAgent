#!/usr/bin/env python3
"""Validate that .claude-plugin/marketplace.json matches the actual plugin tree.

Exits non-zero on any of:
  - a plugin's source directory is missing
  - a plugin's plugin.json is missing or missing required keys
  - a registered agent/command file is missing on disk
  - a registered skill directory is missing on disk
  - an agent/command file exists on disk but is not registered
  - a skill directory exists on disk but is not registered

Run from the repo root:

    python3 scripts/validate-marketplace.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"

REQUIRED_PLUGIN_JSON_KEYS = {"name", "version", "description"}


def relset(entries: list[str]) -> set[str]:
    return {e.lstrip("./").rstrip("/") for e in entries}


def discover(dirpath: Path, kind: str) -> set[str]:
    if not dirpath.is_dir():
        return set()
    if kind == "skills":
        return {f"skills/{p.name}" for p in dirpath.iterdir() if p.is_dir()}
    return {f"{kind}/{p.name}" for p in dirpath.iterdir() if p.is_file() and p.suffix == ".md"}


def diff(label: str, registered: set[str], present: set[str], errors: list[str]) -> None:
    missing = sorted(registered - present)
    unregistered = sorted(present - registered)
    for m in missing:
        errors.append(f"  [{label}] registered but missing on disk: {m}")
    for u in unregistered:
        errors.append(f"  [{label}] present on disk but not registered: {u}")


def main() -> int:
    if not MARKETPLACE.exists():
        print(f"ERROR: {MARKETPLACE} not found", file=sys.stderr)
        return 2

    marketplace = json.loads(MARKETPLACE.read_text())
    errors: list[str] = []

    for plugin in marketplace.get("plugins", []):
        name = plugin.get("name", "<unnamed>")
        source = plugin.get("source", "").lstrip("./").rstrip("/")
        plugin_dir = REPO_ROOT / source
        print(f"Checking {name} ({source})")

        if not plugin_dir.is_dir():
            errors.append(f"[{name}] source directory missing: {source}")
            continue

        plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            errors.append(f"[{name}] plugin.json missing at {plugin_json.relative_to(REPO_ROOT)}")
        else:
            try:
                data = json.loads(plugin_json.read_text())
                missing_keys = REQUIRED_PLUGIN_JSON_KEYS - data.keys()
                if missing_keys:
                    errors.append(f"[{name}] plugin.json missing keys: {sorted(missing_keys)}")
            except json.JSONDecodeError as e:
                errors.append(f"[{name}] plugin.json is not valid JSON: {e}")

        registered_agents = relset(plugin.get("agents", []))
        registered_commands = relset(plugin.get("commands", []))
        registered_skills = relset(plugin.get("skills", []))

        present_agents = discover(plugin_dir / "agents", "agents")
        present_commands = discover(plugin_dir / "commands", "commands")
        present_skills = discover(plugin_dir / "skills", "skills")

        plugin_errors: list[str] = []
        diff(f"{name}:agents", registered_agents, present_agents, plugin_errors)
        diff(f"{name}:commands", registered_commands, present_commands, plugin_errors)
        diff(f"{name}:skills", registered_skills, present_skills, plugin_errors)
        errors.extend(plugin_errors)

    if errors:
        print("\nValidation failed:\n", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print("\nAll plugins valid: marketplace.json matches the filesystem.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
