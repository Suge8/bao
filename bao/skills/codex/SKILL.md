---
name: codex
description: "Delegate coding tasks to Codex CLI. Use for implementing features, fixing bugs, refactoring code, and running iterative coding conversations."
metadata: {"bao":{"emoji":"🧠","requires":{"bins":["codex"]}}}
---

# Codex Skill

Use Codex CLI as a production coding backend from bao.

## When to use

- User asks to write or modify code
- User asks to debug, refactor, or add a feature
- User wants iterative coding follow-ups in the same thread

## Tools

- `codex`: Run coding tasks with session continuity, retries, and timeout protection
- `codex_details`: Fetch full stdout/stderr by `request_id` when details are omitted

## Recommended flow

1. Start with `codex` using a clear, scoped prompt.
2. Read `Summary` and `CODEX_META` from response.
3. If user asks for logs/details, call `codex_details` with `request_id`.
4. For follow-ups, call `codex` again with `continue_session=true`.

## Good defaults

- `continue_session=true`
- `response_format="hybrid"`
- `include_details=false`
- `full_auto=false` (enable explicitly when you want unattended execution)

## Example

Request:
"Add request validation to `src/api/users.py` and run related tests."

Follow-up:
"Keep the same session. Show full stderr only if tests fail."
