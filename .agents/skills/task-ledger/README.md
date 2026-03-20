# Task Ledger Skill

`task-ledger` is a reusable agent skill for lightweight local task planning, progress tracking, and append-only work logging.

It is designed for moments like:

- "Track these follow-up tasks"
- "Create a local backlog for this repo"
- "What should we work on next?"
- "Resume from the current task state"
- "Record this blocker or completion in a durable way"

The skill stores current task state and task history in simple repo-local files so work remains inspectable, resumable, and easy to audit across sessions.

## What It Covers

- Initialize a lightweight local task system when no stronger project-specific tracker exists
- Create, update, block, unblock, and complete tasks
- Preserve a compact current-state ledger plus append-only history
- Recover partial ledger state when only some task files exist
- Recommend the next ready task based on current status and dependencies

## Storage Shape

The default layout is:

```text
tasks/
├── task_log.tsv
├── tasks.tsv
└── tasks_config.yaml
```

This skill intentionally uses simple, inspectable files instead of a hidden state store or a tool-specific database.

## Canonical Files

- `SKILL.md`: trigger contract, task lifecycle rules, normalization guidance, and output contract
- `references/format-examples.md`: canonical TSV examples and dependency encoding details
- `references/python-helper-snippet.md`: optional helper guidance for repetitive TSV editing

## Default Model

When no repo-specific task system already exists, the skill defaults to:

- a TSV current-state ledger in `tasks/tasks.tsv`
- an append-only audit log in `tasks/task_log.tsv`
- a YAML config in `tasks/tasks_config.yaml`
- stable task IDs such as `T-001`
- explicit task statuses such as `pending`, `in_progress`, `blocked`, `done`, and `cancelled`

## When To Use It

This skill is a good fit when you need:

- lightweight repo-local task tracking
- resumable agent work across sessions
- visible dependencies and blockers
- an audit-friendly history of task changes

It is not meant to replace a stronger project-specific task system that already exists.

## Support

If you hit a bug or a documentation problem while using this skill in `ai-stacks`:

- [Open an issue](https://github.com/mtsanaissi/ai-stacks/issues)
- [Read the support guide](../../SUPPORT.md)

If you want to support maintenance of this repo and its reusable skills:

- [GitHub Sponsors](https://github.com/sponsors/mtsanaissi)
- [Buy Me a Coffee](https://buymeacoffee.com/mtsanaissi)
