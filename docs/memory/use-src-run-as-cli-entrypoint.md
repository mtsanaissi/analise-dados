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

# Use `python -m src.run` as CLI Entrypoint

## Summary

The canonical command-line entrypoint for the project is `python -m src.run`.

## Context

The project removed the old orchestrator entrypoint and now dispatches work from the `src.run` module into the phase-specific logic under `src/phases/`.

## Remember

Use `python -m src.run` as the CLI entrypoint and do not point new instructions or workflows back to the removed `src/main/orchestrator.py`.
