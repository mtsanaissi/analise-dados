# Validation Matrix

Use the smallest validation set that still exercises the risk introduced by the change.

## Always

- Run the repo's existing automated checks for the touched surface.
- If the repo has no formal checks for that surface, run the smallest direct execution path that still exercises the change.

## Package Structure, Imports, Or Type Shape Changes

- Run the repo's static analysis or import-validation step if one exists after changing public interfaces, imports, or typed contracts.
- Verify the changed modules still import cleanly in the intended runtime context.

## Trust Boundary, Serialization, Subprocess, Or Config Changes

- Add or run negative tests for malformed input, unauthorized use, subprocess failure, or unsafe payload handling as applicable.
- Exercise the boundary directly instead of only through a higher-level happy path.
- Re-check logging and error surfaces for secret or environment leakage.

## Packaging Or Tooling Changes

- Verify local commands, CI expectations, and documented commands still agree.
- Check that entry points, dependency groups, and Python version assumptions match the repo's checked-in packaging or environment config.

## Test-Only Changes

- Run the smallest relevant automated test target plus any repo-defined static or style checks required by the touched files.
