# Task Routing

Read this file first, then load only the references needed for the current task.

## Trust Boundaries, Input Handling, And Risky Runtime Surfaces

Use [boundaries-and-inputs.md](boundaries-and-inputs.md) when the task involves:

- request parsing, CLI args, environment input, queue payloads, or file ingestion
- serialization, deserialization, XML, pickle-adjacent behavior, or unsafe object loading
- subprocess calls, shell execution, filesystem side effects, or temp files
- auth, secrets, config loading, logging, or sensitive error handling

## Package Structure, Imports, And Type Shape

Use [module-and-type-shape.md](module-and-type-shape.md) when the task involves:

- package layout, module ownership, or import refactors
- type hints, protocols, dataclasses, or schema/model boundaries
- domain code leaking framework assumptions
- deciding whether helpers belong in shared, runtime-specific, or boundary modules

## Packaging, Dependencies, And Toolchain Choices

Use [packaging-and-tooling.md](packaging-and-tooling.md) when the task involves:

- packaging metadata or environment bootstrap files
- dependency additions or version constraints
- CLI entry points, packaging metadata, or build backend choices
- repo-specific automation, validation, or tooling changes

## Test Shape And Regression Coverage

Use [testing-strategy.md](testing-strategy.md) when the task involves:

- test coverage expectations
- the existing test framework, fixtures, or test organization
- integration boundaries, contract tests, or failure-path checks
- deciding what to validate before closing work

## Closing Work

Always read [validation-matrix.md](validation-matrix.md) before finishing implementation or review work.
