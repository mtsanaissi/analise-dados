# Memory Card Template

Use this template for each file in `docs/memory/`.

```markdown
---
id: run-pnpm-through-corepack
date: 2026-03-12
kind: workflow
scope: project
tags:
  - pnpm
  - tooling
  - commands
source: bug-fix
---

# Run pnpm through Corepack

## Summary

Use Corepack to activate and run the repo's expected pnpm version instead of assuming a globally installed `pnpm` binary will work.

## Context

Direct `pnpm` commands failed in this environment because the expected package manager version was not active.

## Remember

Enable Corepack first, then run `pnpm` through the activated toolchain when the repo depends on a managed pnpm version.
```

Guidelines:

- Keep one atomic memory per file.
- Prefer concrete names that describe the reusable rule.
- If the entry is a stable fact rather than a lesson, keep `Remember` factual and brief.
