# Testing Strategy

## Rules

- Run the repo's existing automated checks for the changed surface. If the repo has no formal lint, typecheck, or test step, use the smallest direct runtime validation that still exercises the risk.
- Add focused tests for trust boundaries, serialization paths, subprocess behavior, and config handling when those areas change.
- Cover both success and failure paths for auth-sensitive, IO-heavy, or user-controlled inputs.
- Keep fixtures small and readable; prefer explicit setup over hidden global state.
- Use integration tests where boundary behavior matters more than isolated unit behavior.

## Review Hotspots

- New tests that mock away the exact boundary the change is supposed to validate.
- Fixtures that leak secrets, machine-specific paths, or mutable shared state between tests.
- Runtime entry points that have only unit tests even though import-time behavior or CLI parsing changed.
- Error handling changes that do not include negative tests.

## Common Mistakes

- Declaring a change safe because the happy-path unit tests passed.
- Overusing monkeypatching until the test no longer reflects the actual runtime shape.
- Leaving subprocess, XML, or serialization edges covered only indirectly through unrelated tests.
- Skipping interface or import validation after changing public contracts or typed surfaces.
