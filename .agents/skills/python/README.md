# Python Skill

This skill holds the repo-owned agent guidance for Python-specific work.

## Purpose

Use this skill for tasks where Python behavior materially affects the answer, such as:

- package layout and import boundaries
- typing, validation, and serialization decisions
- CLI, worker, web, or automation entry points
- packaging, dependency, and toolchain choices
- test strategy for runtime and trust-boundary changes

## Layout

- `SKILL.md`: trigger rules, workflow, and reference-routing guidance
- `references/`: deep Python operating references for agents

## Repository Status

This skill is intentionally repo-owned but not selected for mirroring into `.agents/skills/` in this repository.

The stack template under `specs/python/` can still reference the skill as an optional repo-local capability for repositories that choose to install it.
