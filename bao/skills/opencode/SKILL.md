---
name: opencode
description: "Delegate coding tasks to OpenCode, an AI coding agent. Use when the user asks to write code, refactor, debug, add features, fix bugs, run tests, or perform any programming task on a project. Supports multi-turn conversations for iterative development."
metadata: {"bao":{"emoji":"⌨️","requires":{"bins":["opencode"]},"install":[{"id":"npm","kind":"shell","command":"npm i -g opencode-ai@latest","bins":["opencode"],"label":"Install OpenCode (npm)"},{"id":"brew","kind":"brew","formula":"anomalyco/tap/opencode","bins":["opencode"],"label":"Install OpenCode (brew)"}]}}
---

# OpenCode Skill

Delegate programming tasks to [OpenCode](https://opencode.ai), an open-source AI coding agent with full file editing, bash execution, and LSP support.

## When to use

Use this skill when the user asks any of:
- "帮我写/改/重构/修复代码"
- "Add a feature to …"
- "Debug this error …"
- "Refactor the function in …"
- "Run the tests and fix failures"
- "Create a new module/component/file"
- Any task that requires reading, writing, or modifying source code in a project

Do NOT use for:
- Simple questions about code concepts (answer directly)
- Reading a single file (use read_file tool)
- Running a single shell command (use exec tool)

## Prerequisites

1. `opencode` CLI installed and on PATH
2. At least one LLM provider configured in OpenCode (`opencode auth login`)
3. Target project directory exists

## Quick start — one-shot coding task

```bash
opencode run --format default "Refactor the parse_config function in src/utils.py to use dataclasses"
```

The command blocks until OpenCode finishes, then prints the final result to stdout. The process exit code is 0 on success.

## Multi-turn workflow (iterative development)

For tasks that need back-and-forth with the user:

**Round 1 — initial task:**
```bash
opencode run "Implement JWT authentication for the REST API in src/api/"
```

**Round 2+ — continue the conversation:**
```bash
opencode run --continue "Good, but use httpOnly cookies instead of localStorage for token storage"
```

`--continue` automatically resumes the most recent session. Use this for follow-up instructions, corrections, or "keep going" messages.

**Important:** Always relay OpenCode's full response to the user. If OpenCode asks a clarifying question or proposes a plan, forward it — the user decides whether to proceed.

## Project setup

Before first use on a project, set up `opencode.json` in the project root to auto-approve file edits and bash commands (avoids mid-execution permission prompts that block non-interactive mode):

```bash
{baseDir}/scripts/setup-project.sh /path/to/project
```

Or create it manually:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "allow",
    "bash": "allow"
  }
}
```

**Security note:** This grants OpenCode full edit and bash access within the project. Only use on trusted projects. For sensitive repos, set `"bash": "deny"` to restrict shell access.

## Session management

List recent sessions:
```bash
opencode session list --format json -n 5
```

Continue a specific session by ID:
```bash
opencode run --session <session-id> "Continue with the refactoring"
```

Fork a session (branch off without affecting the original):
```bash
opencode run --session <session-id> --fork "Try a different approach: use composition instead of inheritance"
```

## Model selection

Override the model for a specific task:
```bash
opencode run --model anthropic/claude-sonnet-4-20250514 "Optimize the database queries in src/db/"
```

## Working directory

OpenCode operates on the current working directory. Always `cd` to the target project first, or specify the project path:
```bash
cd /path/to/project && opencode run "Fix the failing tests"
```

If the user mentions a specific project or directory, use that path. If unclear, ask the user which project to work on.

## Agent selection

OpenCode has built-in agents. Choose the right one for the task:

```bash
# Default: build agent (full access, can edit files and run commands)
opencode run "Add error handling to the API endpoints"

# Plan agent: read-only analysis, no file changes
opencode run --agent plan "Review the authentication flow and suggest improvements"
```

Use `--agent plan` when the user wants analysis or a plan before making changes.

## Best practices for prompts

Write clear, specific prompts for better results:

- **Be specific:** "Add input validation to the `create_user` endpoint in `src/api/users.py`" > "Fix the API"
- **Provide context:** "The tests in `tests/test_auth.py` are failing because the JWT secret changed. Update the test fixtures."
- **Reference files:** Mention specific file paths so OpenCode knows where to look
- **State the goal:** "Refactor to reduce duplication" > "Clean up the code"
- **One task at a time:** Break large tasks into focused steps for better results
## Error handling

If `opencode run` fails (non-zero exit code), check:

1. **Not installed:** `command not found` → guide user to install: `npm i -g opencode-ai@latest`
2. **No provider configured:** `no providers` → run `opencode auth login`
3. **Project not initialized:** first run in a project may need `opencode` (TUI) then `/init` to create `AGENTS.md`
4. **Timeout:** long tasks may take minutes — this is normal, do not interrupt prematurely
5. **Permission denied:** if `opencode.json` is missing or has `"ask"` permissions, run the setup script first

## Interaction pattern

When acting as a coding delegate for the user:

1. **Translate the user's request** into a clear, specific prompt for OpenCode
2. **Run** `opencode run` with the prompt (use `--continue` for follow-ups)
3. **Relay** OpenCode's full response back to the user verbatim
4. **If OpenCode asks a question** or proposes a plan, forward it to the user and wait for their decision
5. **If the user says "continue"** or gives feedback, pass it through with `--continue`
6. **Never silently discard** OpenCode's output — the user needs to see what happened

## Limitations

- `opencode run` is **blocking** — the exec tool will wait until OpenCode finishes (may take several minutes for complex tasks)
- `--continue` resumes the **most recent** session in the project directory — if multiple users share a machine, sessions may collide
- OpenCode requires its own LLM API keys, separate from bao's provider configuration
- File changes are made directly on disk — recommend using git so changes can be reviewed and reverted
