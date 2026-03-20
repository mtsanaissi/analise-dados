---
id: use-src-run-as-cli-entrypoint
date: 2026-03-20
kind: fact
scope: project
tags:
  - cli
  - entrypoint
  - phases
source: documentation
---

# Use src/run.py as CLI Entrypoint

## Summary

The canonical command-line entrypoint for the project is `python src/run.py`.

## Context

The project removed the old orchestrator entrypoint and now dispatches work from `src/run.py` into the phase-specific logic under `src/phases/`.

## Remember

Use `python src/run.py` as the CLI entrypoint and do not point new instructions or workflows back to the removed `src/main/orchestrator.py`.
