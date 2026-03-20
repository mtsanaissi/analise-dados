# Boundaries And Inputs

Treat every Python entry point as a trust boundary until proven otherwise.

## Rules

- Validate and normalize untrusted input at the boundary instead of relying on downstream type hints.
- Keep config loading centralized, typed, and explicit. Avoid scattered `os.getenv()` fallbacks for security-relevant behavior.
- Prefer `subprocess` argument lists over shell strings. Avoid `shell=True`; if it is unavoidable, keep untrusted input out of command construction.
- Do not use `pickle`, `shelve`, or similar object-graph formats across trust boundaries.
- Keep secrets, tokens, PII, and internal hostnames out of logs, reprs, fixtures, notebooks, and sample payloads.
- Catch expected exceptions at the boundary and preserve security-relevant failures instead of flattening everything into `except Exception`.

## Review Hotspots

- HTTP handlers, CLI wrappers, queue consumers, workers, cron jobs, and migration scripts.
- XML parsing, archive extraction, file uploads, and user-controlled file paths.
- Code that constructs shell commands, database DSNs, or outbound URLs from external input.
- Logging or tracing changes that may expose request bodies, auth tokens, or environment-derived secrets.

## Common Mistakes

- Assuming a dataclass or annotated function signature enforces runtime validation.
- Reading environment variables from many modules and silently changing behavior when one value is missing.
- Trusting hidden CLI defaults or sample payloads in tests that do not reflect production inputs.
- Swallowing subprocess stderr or exit status on a privileged automation path.
