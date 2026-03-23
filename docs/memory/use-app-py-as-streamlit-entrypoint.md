---
id: use-app-py-as-streamlit-entrypoint
date: 2026-03-23
kind: fact
scope: project
tags:
  - streamlit
  - ui
  - entrypoint
source: refactor
---

# Use `app.py` as Streamlit Entrypoint

## Summary

The canonical Streamlit entrypoint for the project is `streamlit run app.py`.

## Context

The project keeps the UI logic in `src.app_main_interface`, but starts Streamlit through a thin wrapper at the repository root to avoid `sys.path` hacks when executing the app.

## Remember

Use `streamlit run app.py` in documentation, tests, and local workflows. Keep `src.app_main_interface` importable as a normal package module and avoid reintroducing path-mutation workarounds there.
