---
id: keep-ad-hoc-scripts-thin-and-reusable
date: 2026-03-20
kind: decision
scope: project
tags:
  - architecture
  - cli
  - scripts
  - treatment
source: retrospective
---

# Keep Ad Hoc Scripts Thin And Reusable

## Summary

Small one-off utilities should keep business logic in reusable treatment modules or connectors, not inside standalone scripts.

## Context

The project already has a canonical CLI entrypoint in `src/run.py`, connector abstractions in `src/connectors/`, and reusable treatment logic under `src/phases/phase02_treatment/core/`.

Creating standalone scripts with their own IO, argument parsing and transformation logic would fragment behavior, duplicate tests and make future maintenance harder.

## Remember

If `src/scripts/` is introduced, keep it for thin convenience wrappers only. Put reusable file-processing logic in the existing treatment or connector layers and expose it through `src/run.py` when the capability should become part of the supported toolkit.
