---
id: use-docs-memory-as-canonical-store
date: 2026-03-20
kind: decision
scope: project
tags:
  - memory
  - workflow
  - docs
source: user-request
---

# Use docs/memory as Canonical Store

## Summary

Store reusable project memory in `docs/memory/` instead of maintaining separate ad hoc memory logs per assistant.

## Context

The project previously kept lessons in `JULES_MEMORY.md` and `GEMINI_MEMORY.md`, which split durable knowledge across assistant-specific files.

## Remember

Use `docs/memory/_index.md` plus atomic cards in `docs/memory/` as the canonical memory system for reusable project knowledge, and update cards there instead of reviving assistant-specific memory logs.
