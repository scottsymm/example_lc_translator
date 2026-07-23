---
name: incept
description: "Optional. Clarify a raw idea into a structured spec. Use when starting from scratch with no existing ticket, user story, or requirements — \"I have an idea, help me think it through.\" Skip when requirements already exist."
---

# Incept — Idea to Spec

Product-definition and requirements-clarification skill. This is a Product
Owner/Manager tool for turning a rough idea into a concrete spec through a
structured PM interview loop.

**This skill learns over time.** Before each session it loads accumulated
learnings; after each distill it captures a retrospective. Use `improve incept`
to fold memory into the skill itself.

## When to Use

- You have an idea but no written requirements.
- You want to pressure-test scope, audience, and MVP boundaries before building.
- Personal projects where you are both the PM and the engineer.

## When to Skip

- A ticket, user story, spec, or other requirements artifact already exists.
  Go directly to [tech-incept](tech-incept.md) with that material.

## Outputs

| Artifact | Path |
|----------|------|
| `<slug>-inception.md` | `$ARTIFACT_DIR/<scope>/<slug>/` |
| `<slug>-spec.md` | `$ARTIFACT_DIR/<scope>/<slug>/` (written at distill only) |

Hand off to [tech-incept](tech-incept.md) when the spec is ready.


## Artifact directory (`ARTIFACT_DIR`)

Resolve `$ARTIFACT_DIR` and `<scope>` per the artifact-dir rule. Every output
path is `$ARTIFACT_DIR/<scope>/<slug>/<slug>-*.md`. Never hardcode vault paths.

If the invocation contains `for <customer>` (e.g. "incept an idea for Acme"),
capture `<customer>` per the artifact-dir scope rules before scaffolding.

### Editor integration (optional)

If `$ARTIFACT_DIR` lives inside a note-taking app vault (e.g. Obsidian), open
artifacts after write using the appropriate URI scheme:

```bash
open "obsidian://open?vault=<vault>&file=<vault-relative-path-without-.md>"
```

If `$ARTIFACT_DIR` is outside a vault, skip the URI and confirm the absolute
path only.


## Phase 0 — Load Memory

Before doing anything else:

1. Check for `$ARTIFACT_DIR/META/incept-memory.md`
2. If it exists, read it silently — apply learnings (preferred question styles,
   recurring gaps, patterns that worked)
3. Do NOT surface the memory file contents to the user unless they ask


## Phase 1 — Scaffold

1. Derive **slug**: kebab-case the idea name (e.g. "loyalty rewards" →
   `loyalty-rewards`, "notification system" → `notification-system`). Slug
   names the subdirectory and prefixes both output files.
2. Resolve `$ARTIFACT_DIR` and `<scope>` (see artifact-dir rule; parse
   `for <customer>` from the invocation if present).
3. Create directory: `$ARTIFACT_DIR/<scope>/<slug>/`
4. Write `$ARTIFACT_DIR/<scope>/<slug>/<slug>-inception.md` from the template
   below — **do not pre-fill Idea or Goal**; keep Phase 1 minimal.
5. Open in editor/vault if integration is configured (see above).
6. Confirm: `Inception file created: $ARTIFACT_DIR/<scope>/<slug>/<slug>-inception.md`

**`<slug>-inception.md` template:**

```markdown
title: <Idea Name>
tags:
  - inception
  - <slug>
keywords: []
incepted: YYYY-MM-DD

# <Idea Name>

## Idea

> (executive summary — written at distill; leave placeholder during interview)

## Goal

> (success criteria and feature list — written at distill; leave placeholder during interview)

## Interview Results

## Timeline
(Consider the time taken to complete the task. Include any timelines or deadlines that are expected, but leave placeholders during the interview.)
```

**Properties (YAML frontmatter):** Document metadata for search and
organization. Always include:

| Field      | When                        | Content                                                                                                                                            |
| ---------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`    | Phase 1                     | Idea name (human-readable)                                                                                                                         |
| `tags`     | Phase 1 → refine at distill | Always include `inception` and `<slug>`; add 1–3 domain tags (lowercase, kebab-case or single words) inferred from the idea name and opening brief |
| `keywords` | Phase 1 → refine at distill | 3–8 search terms: products, users, capabilities, systems mentioned                                                                                 |
| `incepted` | Phase 1                     | `YYYY-MM-DD`                                                                                                                                       |

At Phase 1, populate `tags` and `keywords` from whatever is known (idea name,
slug, repos/products in the opening brief). Refine both at distill from the
full interview — do not leave `keywords: []` after distill.


## Phase 2 — Opening Brief

After confirming the file, prompt:

> "Go ahead — tell me everything about this idea. Stream of consciousness is fine."

- Append under `## Interview Results` using the Q&A format (see Phase 3)
- Use **What's the idea?** as the first question unless the user already
  stated the idea in the incept command — then use that exact framing
- Preserve the user's voice verbatim in the answer
- **Tight spacing:** one blank line between Q&A pairs only; no blank line between
  question and answer; no `Round #` headings


## Phase 3 — Interrogation Loop

**Persona:** Product manager + CEO. Direct, probing, treats vague answers as gaps.

**Audience:** The inception artifact is for **non-engineers** — product owners,
executives, and domain experts. Keep questions at the **problem, user, outcome,
and scope** level. Do **not** ask implementation questions (architecture,
deployment, data migration, component boundaries) — those belong in
[tech-incept](tech-incept.md) after the spec exists.

**Question style:**

- Plain language; no jargon unless the user introduced it
- 2–3 questions per round, not four dense multiple-choice menus
- Prefer open prompts over numbered technical forks
- When you do offer options, keep them outcome-focused (who, why, what changes
  for the user, how we know it worked)

**Interview Results format** — append each exchange under `## Interview Results`:

```markdown
**Who is this for?**
Internal users managing time entries via Slack. Admins use the web dashboard.

**What must v1 deliver?**
Full answer here — preserve the user's voice.
```

Rules:

- Question on its own line, **bold**, ends with **`?`**
- Answer immediately on the next line (no blank line between question and answer)
- One blank line between Q&A pairs — no extra spacing, no `Round #` headings
- **Multiple-choice shorthand:** when the user replies with a number or letter
  that maps to options you offered (e.g. `"1"`, `"B"`), write the **full option
  text** in the answer — not the number alone. Preserve their intent; expand
  abbreviations so the artifact stands alone without the chat transcript.

Each round:

1. Read the full `<slug>-inception.md`
2. Surface **2–3 pointed questions** — biggest gaps first:
   - Who is this for, and what changes for them day to day?
   - What problem does this solve that isn't solved today?
   - What must be true in v1 vs what can wait?
   - What would make stakeholders say this failed?
   - How do we measure success (behavior or outcome, not uptime)?
3. After the user answers, append each Q&A to `## Interview Results` using the
   format above
4. Loop until user says "distill", "done", "wrap it up", or equivalent


## Phase 4 — Distill to Spec

**Trigger:** "distill", "done", "spec", or equivalent.

1. Replace placeholders in `<slug>-inception.md`:
   - **Frontmatter** — refresh `tags` and `keywords` from the distilled Idea/Goal
     (keep `inception`, `<slug>`, and `incepted`; add domain tags and search terms)
   - **`## Idea`** — 2–4 sentence executive summary (problem, who, why now)
   - **`## Goal`** — success criteria (bullets) and v1 feature list (bullets);
     include any unresolved product questions under success criteria or as a
     final bullet prefixed `Open:`
   - Leave **`## Interview Results`** unchanged

2. Write standalone `$ARTIFACT_DIR/<scope>/<slug>/<slug>-spec.md`:

```markdown
title: <Idea Name> — Spec
tags:
  - spec
  - <slug>
keywords: []
distilled: YYYY-MM-DD

# <Idea Name> — Spec

## Problem Statement

## Target Audience

## Core Value Proposition

## MVP Scope

## Success Metrics

## Key Risks & Open Questions
```

Copy `tags` and `keywords` from the inception doc; replace `inception` with `spec`
in tags. Set `distilled` to today's date.

1. Open in editor/vault if integration is configured.
2. Confirm: `Done. Spec written to $ARTIFACT_DIR/<scope>/<slug>/<slug>-spec.md`
3. Confirm readiness to hand off to [tech-incept](tech-incept.md).


## Phase 5 — Learning Capture

Immediately after Phase 4, append a retrospective entry to
`$ARTIFACT_DIR/META/incept-memory.md` (create if missing):

```markdown
## <Idea Name> — <YYYY-MM-DD>

- **Idea type:** (e.g. product feature / internal tool / content / business model)
- **Domain:** (e.g. fintech / consumer app / dev tooling)
- **Questions that surfaced real gaps:** (1–2 questions from Phase 3 that cracked it open)
- **Questions that missed:** (any that felt off or got deflected)
- **Rounds to distill:** (how many interrogation rounds before user said done)
- **Observations:** (user style, recurring blindspot, good reframe)
```

Do NOT ask the user to fill this in — infer from the session. Keep each entry
concise (5–8 lines max).


## `improve incept` — Self-Update Trigger

**Trigger:** user says "improve incept", "update the incept skill", or
"fold in learnings"

1. Read `$ARTIFACT_DIR/META/incept-memory.md`
2. Synthesize patterns across entries
3. Propose edits to this skill file
4. Ask: "Apply these updates?" — if yes, write changes
5. Confirm: `incept skill updated — learnings folded in`


## Hard Rules

- **Always** resolve and use `$ARTIFACT_DIR` — never hardcode vault paths.
- **Always** use slug-prefixed filenames: `<slug>-inception.md`, `<slug>-spec.md`.
- **Never** pre-fill Idea/Goal in Phase 1 — interview first; write both at distill.
- **Interview Results** use bold `**Question?**` + answer on the next line; tight
  spacing; no round headings.
- **Properties** — YAML frontmatter with `title`, `tags`, `keywords`, `incepted`;
  refine tags/keywords at distill.
- **Never** write `<slug>-spec.md` until Phase 4 (distill).
