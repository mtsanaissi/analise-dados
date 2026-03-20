---
id: use-project-relative-paths-in-code-and-tests
date: 2026-03-20
kind: lesson
scope: project
tags:
  - paths
  - tests
  - portability
source: retrospective
---

# Use Project-Relative Paths in Code and Tests

## Summary

Avoid fixed machine-specific absolute paths in code, tests and documentation.

## Context

The project needs to run in copied workspaces and on Windows 11, so hardcoded paths from one environment do not transfer safely.

## Remember

Build paths from the project root or use project-relative paths in tests, scripts and docs instead of hardcoding local absolute paths from a specific machine.
