---
name: memory
description: LanceDB-backed categorized memory with automatic recall, consolidation, and explicit memory tools.
always: true
---

# Memory

## Structure

- Long-term memory is split into four categories: **preference**, **personal**, **project**, **general**.
- Each category is stored independently in LanceDB; consolidation outputs `memory_updates` dict with per-category content.
- Experience entries use a columnar schema (quality, uses, successes, category, outcome as dedicated columns).
- Experience ranking uses quality-based retention (quality 5 = 365 days, 1 = 14 days) with Laplace-smoothed confidence.
- High-quality, frequently reused experiences (quality ≥ 5, uses ≥ 3) are immune from cleanup unless deprecated.
- Old text-based schemas are auto-migrated on first load.

## Explicit Memory Tools

- **remember** — Save a fact to a specific memory category (default: general).
- **forget** — Remove memory content matching a keyword from a category.
- **update_memory** — Overwrite a specific category's memory with new content.

Use these tools when the user explicitly asks to remember, forget, or update something.

## How To Use It

- Save durable user facts (preferences, project constraints, relationships) to the appropriate category.
- Reuse recalled memory in responses, but avoid repeating irrelevant history.
- Let the system manage consolidation and cleanup; no manual file maintenance is required.

## Notes

- Prefer concise, high-signal memory updates over verbose logs.
- Keep behavior unchanged: this skill improves recall quality, not tool behavior.
