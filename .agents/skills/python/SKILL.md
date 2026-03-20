---
name: python
description: Use this skill when the task is materially about Python package structure, imports, typing, serialization, trust boundaries, subprocess usage, packaging or environment configuration, dependency management, runtime entry points, or test strategy in a Python project.
---

# Python

Use this skill for implementation, debugging, refactoring, and review work where Python runtime behavior materially affects the answer.

Do not use this skill for generic product planning or infrastructure tasks unless Python package, runtime, or toolchain choices are part of the work.

## Before You Change Code

1. Inspect the repo's Python packaging or environment config if present, the Python version, and the installed frameworks or libraries before using version-specific APIs.
2. Check the project shape: library, service, CLI, worker, notebook-heavy repo, or a hybrid.
3. Read [references/task-routing.md](references/task-routing.md) first, then load only the referenced files that match the task.

## Reference Routing

- Read [references/boundaries-and-inputs.md](references/boundaries-and-inputs.md) for trust boundaries, input validation, subprocess usage, config loading, logging, secrets, and serialization risk.
- Read [references/module-and-type-shape.md](references/module-and-type-shape.md) for package layout, imports, type usage, data-model boundaries, and framework leakage into domain code.
- Review [references/packaging-and-tooling.md](references/packaging-and-tooling.md) for packaging metadata, dependency choices, entry points, environment tooling, and repo-shape assumptions.
- Consult [references/testing-strategy.md](references/testing-strategy.md) for the existing test layout, failure-path coverage, fixtures, integration boundaries, and regression checks.
- Before closing work, check [references/validation-matrix.md](references/validation-matrix.md) so the validation matches the change.

## Workflow

1. Inspect local versions, repo config, and the affected runtime boundary.
2. Load only the references that match the task shape.
3. Preserve explicit boundaries for imports, side effects, validation, and configuration.
4. Make the smallest change that fits the existing project shape.
5. Run the relevant validation from the validation matrix.
6. Report any remaining runtime, packaging, or security risk explicitly.

## Common Failure Modes

- Hallucinating framework helpers, stdlib behavior, or package APIs from a different Python or library version.
- Making imports work by mutating `sys.path`, relying on current-directory precedence, or shadowing stdlib module names.
- Treating type hints, dataclasses, or pydantic-style models as sufficient validation at trust boundaries.
- Hiding runtime assumptions in import-time side effects, global config reads, or broad exception handling.
- Adding packaging or dependency complexity that the repo does not need.
- Closing work with only happy-path tests when the changed code sits on an auth, subprocess, IO, or serialization boundary.

## Output Expectations

- Name the Python boundary being changed: package layout, runtime entry point, trust boundary, serialization path, toolchain surface, or test surface.
- Call out any version-sensitive assumptions.
- If subprocesses, secrets, config loading, packaging metadata, or untrusted input changed, say what was verified and what still needs manual confirmation.
