# Module And Type Shape

## Rules

- Keep domain logic free of framework-specific request, ORM, or transport objects where practical.
- Prefer explicit package structure over import hacks, plugin magic, or current-working-directory assumptions.
- Keep server-only, CLI-only, or environment-specific code isolated so tests and imports stay predictable.
- Use type hints to clarify contracts, but keep them aligned with actual runtime behavior and supported Python versions.
- Favor small data-shaping boundaries between transport models and domain objects instead of passing large framework models everywhere.

## Review Hotspots

- New shared modules that import both runtime-specific and generic helpers.
- `__init__.py` files that re-export too much or trigger import-time side effects.
- Widening helper modules until they mix config loading, transport parsing, and business logic.
- Type aliases or protocols copied from examples without matching the installed framework version.

## Common Mistakes

- Fixing imports by appending to `sys.path`.
- Naming local modules `typing.py`, `email.py`, `logging.py`, or other stdlib-colliding names.
- Treating pydantic-style model methods or ORM conveniences as if every project uses the same version and API surface.
- Letting domain code depend directly on framework exceptions, request objects, or active global state.
