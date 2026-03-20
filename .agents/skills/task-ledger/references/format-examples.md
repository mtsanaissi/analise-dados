# Task Ledger Format Examples

Use these examples only as defaults. If the repository already has a ledger, follow its existing shape instead of migrating it silently.

## Default `tasks/tasks_config.yaml`

```yaml
format: tsv
fields:
  - id
  - status
  - title
  - description
  - depends_on
  - owner
  - created_at
  - updated_at
  - completed_at
  - refs
  - acceptance_criteria
logFields:
  - ts
  - id
  - action
  - actor
  - note
idPattern: "^T-\\d{3}$"
statuses:
  - pending
  - in_progress
  - blocked
  - done
  - cancelled
logActions:
  - create
  - update
  - start
  - block
  - unblock
  - complete
  - cancel
  - note
defaultOwner: username
dependencyDelimiter: ", "
checklistDelimiter: " | "
```

## Default `tasks/tasks.tsv`

Header:

```tsv
id	status	title	description	depends_on	owner	created_at	updated_at	completed_at	refs	acceptance_criteria
```

Example rows:

```tsv
T-001	done	Inventory current task system	Inspect repo for existing task tracking files and conventions.		username	2026-03-11T13:50:00Z	2026-03-11T14:05:00Z	2026-03-11T14:05:00Z	AGENTS.md|skills/task-ledger/SKILL.md	- [x] Existing task system identified
T-002	in_progress	Draft task-ledger revisions	Update SKILL.md with operational workflow and normalization guidance.	T-001	username	2026-03-11T14:06:00Z	2026-03-11T14:20:00Z		skills/task-ledger/SKILL.md	- [ ] Frontmatter reduced to required keys | - [ ] Common operations documented
T-003	pending	Add reference examples	Create reference docs for TSV examples and helper snippet.	T-002	username	2026-03-11T14:10:00Z	2026-03-11T14:10:00Z		skills/task-ledger/references/format-examples.md|skills/task-ledger/references/python-helper-snippet.md	- [ ] Canonical examples added | - [ ] Helper guidance added
T-004	blocked	Validate revised skill	Run project validator or manual checks and capture the result.	T-002, T-003	username	2026-03-11T14:12:00Z	2026-03-11T14:18:00Z		manual-review	- [ ] Validation completed
```

## Owner Guidance

Treat `owner` as the responsible actor label, not necessarily a human username.

- If the repository already has an owner convention, follow it.
- If the task is clearly assigned to a specific human or team, use that value.
- If an agent creates the task without a stronger convention, use `defaultOwner` from config.
- If no config exists yet during bootstrapping, use a stable agent label such as `username`.
- Avoid mixing labels like `assistant`, `ai`, `agent`, and personal usernames unless the project deliberately wants that variety.

## Default `tasks/task_log.tsv`

Header:

```tsv
ts	id	action	actor	note
```

Example rows:

```tsv
2026-03-11T13:50:00Z	T-001	create	username	Created task from user request to review local task ledger skill.
2026-03-11T14:05:00Z	T-001	complete	username	Confirmed repository has no stronger built-in task system for this scope.
2026-03-11T14:06:00Z	T-002	start	username	Started revising SKILL.md based on review findings.
2026-03-11T14:18:00Z	T-004	block	username	Validator script not present in repository; using manual review instead.
```

## Dependency Encoding

If `depends_on` exists:

- Store task IDs in one cell.
- Use `, ` as the default delimiter.
- Keep IDs stable and exact: `T-002, T-003`
- Leave the cell empty when there are no dependencies.

Interpretation defaults:

- A task is ready only when every dependency is satisfied.
- `done` is satisfied.
- `cancelled` is satisfied only if the project convention allows it.
- `pending`, `in_progress`, and `blocked` are not satisfied.

## Acceptance Criteria Encoding

If `acceptance_criteria` exists, keep checklist items in one cell separated by ` | ` unless the project already uses another delimiter:

```text
- [ ] Frontmatter reduced to required keys | - [ ] Output contract documented
```

## Config Change Notes

When the user asks to change config:

- Update `tasks/tasks_config.yaml` first.
- If `fields` changes, migrate the `tasks/tasks.tsv` header and rows explicitly.
- If `statuses` changes, do not rewrite historical values unless the user asks for migration.
- If `logActions` changes, prefer the new vocabulary for future entries and preserve history unless instructed otherwise.
- If `logFields` changes, do not modify `tasks/task_log.tsv` unless the user explicitly requests a log migration.

## Reopen Example

When reopening a completed task:

```tsv
T-002	in_progress	Draft task-ledger revisions	Update SKILL.md with clarified workflow after user feedback.	T-001	username	2026-03-11T14:06:00Z	2026-03-11T15:02:00Z		skills/task-ledger/SKILL.md	- [ ] Follow-up edits applied
```

Matching log row:

```tsv
2026-03-11T15:02:00Z	T-002	update	username	Reopened task after follow-up review requested additional edits.
```
