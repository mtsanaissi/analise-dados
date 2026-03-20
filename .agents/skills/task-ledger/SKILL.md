---
name: task-ledger
description: Lightweight local task planning, tracking, and work logging with a TSV task ledger and append-only history. Use this skill whenever the user asks to handle local tasks, issues, todos, backlog items, work logs, blockers, dependencies, follow-ups, resumable session state, or audit-friendly task tracking in the workspace, especially when no stronger project-specific task system already exists.
---

# Task Ledger

Use this skill to keep work visible across sessions with a compact current-state ledger and an append-only history log.

If the repo already has a different task system, follow that system instead of replacing it.

Read [references/format-examples.md](references/format-examples.md) when you need canonical TSV examples or dependency encoding details.

Read [references/python-helper-snippet.md](references/python-helper-snippet.md) when manual TSV editing feels error-prone or repetitive.

## Canonical Files

- `tasks/tasks.tsv`: current task state
- `tasks/task_log.tsv`: append-only audit history
- `tasks/tasks_config.yaml`: task ledger configuration and defaults

## Minimal Config

- `format`
- `fields`
- `logFields`
- `idPattern`
- `statuses`
- `logActions`
- `defaultOwner`

Other config keys are optional and refine validation, sorting, or checklist behavior.

## Conventions

### Default conventions

Use these defaults only when no task ledger exists yet and no custom conventions have been confirmed:

- `format: tsv`
- `fields: ["id", "status", "title", "description", "depends_on", "owner", "created_at", "updated_at", "completed_at", "refs", "acceptance_criteria"]`
- `logFields: ["ts", "id", "action", "actor", "note"]`
- `idPattern: "^T-\\d{3}$"`
- `statuses: ["pending", "in_progress", "blocked", "done", "cancelled"]`
- `logActions: ["create", "update", "start", "block", "unblock", "complete", "cancel", "note"]`
- `defaultOwner: "username"`

### Existing-project conventions

- If `tasks/tasks.tsv` already exists, follow its existing column layout.
- If `tasks/tasks_config.yaml` also exists, treat it as strictly canonical and let it override conflicting TSV conventions.
- If `tasks/tasks.tsv` exists and `tasks/tasks_config.yaml` does not, infer the current ledger shape from the existing TSV files, write a matching `tasks/tasks_config.yaml`, and avoid silent migration.

### User-confirmed custom conventions

- If the defaults are not appropriate, confirm the desired fields, ID pattern, statuses, or checklist behavior with the user.
- Persist confirmed conventions in `tasks/tasks_config.yaml`.

## Common Operations

### Create a task

- Read `tasks/tasks_config.yaml` first if it exists.
- If `tasks/tasks.tsv` exists, reuse the existing header order.
- If no ledger exists yet, create `tasks/tasks_config.yaml`, `tasks/tasks.tsv`, and `tasks/task_log.tsv` together using the current project convention or the defaults.
- Allocate the next task ID by incrementing the largest existing numeric suffix.
- Set `status` to `pending` unless the user clearly asked for a different starting state.
- Set `owner` from the explicit assignee if the project has one. Otherwise use `defaultOwner` from config, or a stable agent label such as `claude`, `codex`, `gemini`.
- Set `created_at` and `updated_at` to the current timestamp.
- Set `completed_at` to empty unless the task is already done.
- Append a matching `create` entry to `tasks/task_log.tsv`.

### List or summarize work

- Read `tasks/tasks.tsv`.
- Group work by status.
- Call out blocked tasks, tasks with unmet dependencies, and recently updated tasks.
- If `depends_on` exists, compute which tasks are ready versus blocked by unfinished prerequisites.

### Update task state

- Read the target row first.
- Preserve all columns you are not changing.
- Update `updated_at` every time.
- Set `completed_at` only when entering `done`; clear it when reopening a completed task unless the project convention says otherwise.
- Append a matching factual log entry for each meaningful change.

### Change task config

- Read `tasks/tasks_config.yaml`, `tasks/tasks.tsv`, and `tasks/task_log.tsv` before changing conventions.
- Update config first when the user asks to change columns, statuses, log actions, delimiters, ID patterns, or owner defaults.
- If the config change requires data migration, describe the migration clearly and then apply it deliberately.
- When changing `fields`, update the `tasks/tasks.tsv` header and ensure every existing row still has the same number of columns.
- When changing `logFields`, do not change `tasks/task_log.tsv` unless the user explicitly asks for a log migration.
- When changing `statuses` or `logActions`, preserve existing historical values unless the user asked for a full migration.
- Never silently drop columns or rewrite historical meaning.

## Partial Ledger Recovery

When only part of the ledger exists, recover it before normal operations:

- If `tasks/tasks.tsv` exists and `tasks/tasks_config.yaml` does not, infer the current task schema from the TSV header, write a matching config, and then treat config as canonical from that point forward.
- If `tasks/tasks.tsv` exists and `tasks/task_log.tsv` does not, create `tasks/task_log.tsv` using the configured `logFields` and append a factual bootstrap note as the first entry only if the project wants that initialization recorded.
- If `tasks/tasks_config.yaml` exists and `tasks/tasks.tsv` header diverges from config `fields`, treat config as authoritative and either migrate the TSV header and rows to match or stop and report the mismatch if migration would be risky.
- If `tasks/tasks_config.yaml` exists and `tasks/task_log.tsv` header diverges from config `logFields`, stop and report the mismatch unless the user explicitly asked for a log migration.
- If only `tasks/task_log.tsv` exists, inspect it for useful history but do not infer the full task schema from it alone; ask the user or use defaults to recreate `tasks/tasks_config.yaml` and `tasks/tasks.tsv`.

### Mark blocked or unblock

- When blocking a task, record the reason in the task description or log note according to the project convention.
- When unblocking, verify that the blocker is actually resolved before changing status.
- If `depends_on` exists, prefer deriving blocked state from unfinished dependencies plus the user-stated blocker reason.

### Resume work from the ledger

- Read `tasks/tasks.tsv` and `tasks/task_log.tsv` if both exist.
- Summarize `in_progress`, `blocked`, and recently changed tasks first.
- Use `depends_on` to identify tasks that are newly ready.
- Recommend the next task based on explicit priority from the project system if available; otherwise prefer ready, unblocked, nearly-finished work.

## Normalization Rules

- Keep TSV headers stable once the ledger exists.
- Use UTF-8 text and literal tab separators.
- Store timestamps in ISO 8601 format, preferably UTC like `2026-03-11T14:22:00Z`.
- Keep one task per row and one log event per row.
- Preserve column order from config and from the existing file once initialized.
- Generate the next ID by incrementing the highest existing ID that matches the project pattern. Do not reuse IDs.
- Use empty strings for unknown optional values rather than inventing placeholders unless the project already uses them.
- Prefer the configured `logActions`. If config is missing during migration, fall back to these actions: `create`, `update`, `start`, `block`, `unblock`, `complete`, `cancel`, `note`.
- Prefer the configured `defaultOwner`. If it is missing, use a stable agent label such as `claude`, `codex`, `gemini` until the project adopts a stronger convention.
- If config exists, treat `fields`, `logFields`, delimiters, statuses, and owner defaults from config as the source of truth over TSV habit or historical drift.

## Dependency Convention

If the ledger includes a `depends_on` column:

- store zero or more task IDs in one cell
- separate IDs with `, ` unless config defines another delimiter
- reference task IDs exactly as written in the ledger
- do not invent dependencies that are not supported by the task description or user intent
- treat a task as not ready while any dependency is not in a terminal satisfied state
- treat `done` as satisfied by default
- treat `cancelled` as satisfied only if the project convention or user intent makes that appropriate
- append a log entry when dependencies materially change

## Rules

- Update `tasks/tasks.tsv` for task creation or state changes.
- Do not delete tasks unless explicitly asked to. Change the status accordingly instead.
- Append a matching factual entry to `tasks/task_log.tsv` for each meaningful change.
- Keep task semantics in `tasks/tasks_config.yaml`.

## First Run

- Expect that `tasks/tasks.tsv` and `tasks/tasks_config.yaml` may not exist yet.
- Only initialize task files when the user asks to handle tasks, issues, todos, backlog, or similar work tracking, or when project instructions explicitly require this skill.
- On first use, create `tasks/tasks_config.yaml`, `tasks/tasks.tsv`, and `tasks/task_log.tsv`.
- Write the active defaults into `tasks/tasks_config.yaml` so the project can inspect and edit them directly.
- If `tasks/tasks.tsv` exists without `tasks/tasks_config.yaml`, infer the current ledger shape and write a matching config before making further schema-dependent changes.

## Optional Checklist Convention

If the config defines an acceptance-criteria field, or if the default field `acceptance_criteria` is present:

- store all checklist items in one TSV cell
- separate items with ` | ` unless config defines another delimiter
- use `- [ ]` and `- [x]` prefixes
- keep items atomic and testable
- prefer outcome language over implementation steps

## Output Contract

When reading or updating the ledger, report a compact summary with these buckets:

- `Open`: pending and in-progress tasks worth attention now
- `Blocked`: tasks blocked by dependencies or explicit blocker notes
- `Changed`: tasks created or updated in the current operation
- `Next`: the recommended next ready task, or the clearest blocker if nothing is ready
