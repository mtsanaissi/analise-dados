# Python Helper Snippet

Use this snippet when manual TSV editing is error-prone and a tiny deterministic helper is enough. This is a reference pattern, not a required bundled script.

## Safe Update Pattern

```python
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

TASKS_PATH = Path("tasks/tasks.tsv")
LOG_PATH = Path("tasks/task_log.tsv")
DEFAULT_LOG_FIELDS = ["ts", "id", "action", "actor", "note"]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return reader.fieldnames or [], list(reader)


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def append_log(task_id: str, action: str, actor: str, note: str) -> None:
    header, rows = read_tsv(LOG_PATH)
    if not header:
        header = DEFAULT_LOG_FIELDS
    rows.append(
        {
            "ts": now_iso(),
            "id": task_id,
            "action": action,
            "actor": actor,
            "note": note,
        }
    )
    write_tsv(LOG_PATH, header, rows)


def update_task(task_id: str, **changes: str) -> None:
    fieldnames, rows = read_tsv(TASKS_PATH)
    for row in rows:
        if row.get("id") != task_id:
            continue
        row.update(changes)
        row["updated_at"] = now_iso()
        if row.get("status") == "done" and "completed_at" in fieldnames and not row.get("completed_at"):
            row["completed_at"] = row["updated_at"]
        write_tsv(TASKS_PATH, fieldnames, rows)
        append_log(task_id, "update", "username", f"Updated fields: {', '.join(sorted(changes))}")
        return
    raise ValueError(f"Task not found: {task_id}")
```

## Notes

- Preserve existing field order.
- Read the current header before writing.
- Bootstrap `tasks/task_log.tsv` if it does not exist yet.
- Update `updated_at` on every meaningful change.
- If `depends_on` exists, treat it as a plain string column unless you are also implementing dependency validation.
- Keep the helper local to the workspace unless the skill proves it needs a real bundled script later.
