---
name: memory
description: Capture, organize, and recall reusable project memory across sessions in `docs/memory/`. Use when the user asks to remember something, save a lesson learned, preserve how a complex problem was solved, keep information for future use, make knowledge reusable, memorize findings from a task, record a workaround, save an operational constraint, or remind future sessions about stable context that should not be rediscovered.
---

# Memory

Use this skill to maintain durable, reusable project memory.

Treat memory capture and recall as a distinct workflow. It is not replaced by task trackers, changelogs, or progress notes.

Read [references/card-template.md](references/card-template.md) before creating or updating a memory card.

## Goal

Store non-obvious knowledge that should help future sessions work faster or avoid repeating mistakes.

## Trigger Contract

Invoke this skill when the user asks to:

- remember this
- save this for later
- add this to memory
- keep this across sessions
- remember what you learned
- save how this was solved
- record the workaround
- save this finding for future use
- make this reusable knowledge
- memorize this lesson
- keep a note so future sessions know this
- store a stable project fact that will likely matter again

Also invoke it when:

- a non-trivial fix exposed a reusable rule or hidden constraint
- the user corrected your approach in a way that should prevent recurrence
- resuming work would benefit from recalling prior lessons before implementation

Do not invoke it for:

- one-off answers with no reusable rule
- obvious framework or language behavior
- temporary local state, transient logs, or environment noise
- raw meeting notes or status updates without a durable takeaway
- speculative conclusions not yet confirmed enough to reuse

## Storage Model

Store memory under `docs/memory/` at the project root.

Use this layout:

```text
docs/memory/
├── _index.md
├── run-pnpm-through-corepack.md
├── keep-agents-canonical.md
└── migrate-settings-before-seeding.md
```

Default to one Markdown file per atomic memory plus one generated index. Why this default:

- one file per memory keeps entries atomic, diff-friendly, and easy to update
- `_index.md` makes recall fast without forcing large file reads
- a flat folder keeps the operational model simple
- centralized files become noisy, harder to deduplicate, and harder to recall selectively

## Recall Phase

Run recall before non-trivial implementation work when prior memory may matter.

1. Extract keywords from the current task.
2. Check whether `docs/memory/` exists.
3. If it exists and `_index.md` is missing, rebuild `_index.md` from existing cards before recall.
4. Read `docs/memory/_index.md`.
5. Select the most relevant 1-3 cards using:
   `tag match -> kind match -> scope match -> date desc`
6. Read only those cards unless another card is clearly needed.
7. Apply the recalled memories as constraints for the current task.
8. Mention recalled card IDs briefly when they materially affected the work.

If no memory exists yet, continue without recall.

## Capture Phase

Run capture when:

- the user explicitly asks to remember something
- the user corrects you with a reusable lesson
- a complex bug fix reveals a stable solution rule
- finishing the task reveals a non-obvious pattern worth preserving

This is a non-replaceable step. Do not substitute task logs, commit messages, or ad hoc notes for memory capture.

### Step 1: Decide whether to capture

Ask: `Will this save meaningful time or prevent a repeat mistake in a future session?`

Capture when at least one of these is true:

- a hidden dependency or ordering rule mattered
- the successful workflow differed from the obvious workflow
- a command, flag, env var, or prerequisite was easy to miss
- several files had to change together
- the user clarified a stable project convention
- the final solution took multiple failed attempts and the winning condition is now clear

Skip capture when:

- the information is already obvious from local code or docs
- the conclusion is too situational to generalize
- the note is really a temporary task reminder
- the content is just raw evidence without a reusable rule

### Step 2: Choose create vs update

Before writing a new card, check for a semantically similar existing card.

- `decision=create` when no similar card exists
- `decision=update` when an existing card already captures the same rule

Prefer updating an existing card over creating near-duplicates.

### Step 3: Write the card

Write one atomic memory card to `docs/memory/<id>.md` using the reference template. Use a semantic kebab-case `id` that describes the rule or remembered fact. Use these fields:

- `id`: semantic slug and filename
- `date`: ISO date `YYYY-MM-DD`
- `kind`: `lesson`, `workflow`, `decision`, `fact`, or `constraint`
- `scope`: `project`, `module`, or `feature`
- `tags`: 2-6 lowercase tags for recall
- `source`: `user-request`, `user-correction`, `bug-fix`, `retrospective`, or `documentation`
- `Title`: H1 heading naming the memory
- `Summary`: one-line statement of the memory
- `Context`: where or when this mattered
- `Remember`: the durable rule, fact, or workaround

Prefer imperative wording in `Remember`. Keep each card short and actionable.

### Step 4: Update the index

Upsert one row per card in `docs/memory/_index.md`. Use this structure:

```markdown
# Memory Index

> Auto-generated summary of reusable project memory. Update entries through memory cards, not by hand.

| Card | Kind | Scope | Tags | Date |
|---|---|---|---|---|
```

Keep rows sorted by `Date` descending, newest first.

### Step 5: Confirm briefly

Report the outcome in a minimalist form: `Memory {created or updated}: {id}`.
Do not dump the full card body unless the user asks to inspect it.

## Promotion And Freshness

The canonical memory stays in `docs/memory/`.

If the project already uses a small always-loaded agent file such as `AGENTS.md`, or a copied or renamed tool-specific equivalent, optionally promote only the most frequently reused constraints there, asking user for permission. Do not create or expand such a hot-cache file unless project conventions already support it.

When a memory becomes stale:

- update the card if the rule still exists but changed
- leave the old date only if preserving original capture time matters
- otherwise refresh the date to the current update date
- do not silently delete memory unless the user asks

## Validation

These checks are required for each card:

- filename matches `id`
- `date` uses `YYYY-MM-DD`
- `kind` is valid
- `scope` is valid
- `tags` count is 2-6
- index row exists and matches the card metadata

## Anti-patterns

- Writing long narratives without a reusable takeaway
- Capturing obvious behavior with no hidden constraint
- Mixing unrelated lessons into one card
- Using memory cards as todo items
- Replacing memory capture with commit history or task ledgers

## First Run

On first use:

- create `docs/memory/`
- create `docs/memory/_index.md`
- create the first card only when there is something worth remembering

Do not create placeholder memory cards.
