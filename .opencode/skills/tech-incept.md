---
name: tech-incept
description: "Produce technical design for implementation. Accepts any markdown or PDF as the requirements contract (preferably a spec file). Answers \"how do we build this?\" with concrete approaches."
---

# Tech Incept — Requirements to Design

Architecture and implementation design skill. Takes requirements from a product
owner or manager and produces an engineering design.

**Output:** `<slug>-design.md` → `$ARTIFACT_DIR/<scope>/<slug>/`


# tech-incept

Bridges the gap between a requirements source and an implementation plan. Reads
from any of: a `spec.md` produced by `incept`, an arbitrary markdown file,
a Linear ticket, or inline requirements — then runs a focused technical discovery
session (architecture, approach tradeoffs, component design) ending in a
`<slug>-design.md` that feeds into [write-plan](write-plan.md).

**Product and PM questions are closed.** Trust the spec. Do not re-litigate what
to build or why. This session is only about *how*.

**Announce at start:** "I'm using tech-incept to run technical discovery on this spec."


## Phase 0 — Locate the Source

The user invokes with `tech incept <source>`. Parse `<source>` to determine the
input type:

| Source format | How to resolve |
|---|---|
| **Linear ticket** — matches pattern like `ENG-123`, `PROJ-42`, etc. | Fetch via `linear` MCP tools. Extract the ticket title, description, acceptance criteria, and any linked docs. This becomes the requirements contract. |
| **File path** — ends in `.md` or contains `/` (e.g. `./spec.md`, `~/notes/reqs.md`, `requirements.md`) | Read the file directly. Resolve relative paths from cwd. |
| **Idea name** — plain words, no extension, no ticket pattern (e.g. `auth-refactor`, `notification system`) | Derive kebab-case slug → look for `$ARTIFACT_DIR/<scope>/<slug>/<slug>-spec.md`. If not found, check for `<slug>-inception.md` at the same path. |
| **`for <customer>` phrase** | Parse `<customer>` per the artifact-dir rule and apply when resolving paths. |
| **Omitted** | Ask: "What should I run technical discovery on? Give me a ticket ID (e.g. ENG-123), a file path, or an idea name." |

**After resolving:**

1. Read the source silently. Do not summarize it back — get to work.
2. If a named idea has no `<slug>-spec.md` or `<slug>-inception.md`, offer to run `incept`
   first, then come back.
3. For Linear tickets: if the ticket description is thin (under ~100 words with
   no acceptance criteria), flag it: "This ticket is light on detail. Want me to
   run with what's here, or should we flesh it out first?"
4. Derive the `<slug>` for the design output path:
   - From idea name: kebab-case the name
   - From file path: kebab-case the filename without extension
   - From Linear ticket: kebab-case the ticket ID (e.g. `eng-123`)


## Phase 1 — Scaffold

1. Using the `<slug>` derived in Phase 0, resolve `$ARTIFACT_DIR` and `<scope>`
   (see artifact-dir rule; parse `for <customer>` from the invocation if present).
2. Create directory: `$ARTIFACT_DIR/<scope>/<slug>/`
3. If `$ARTIFACT_DIR/<scope>/<slug>/<slug>-inception.md` does not exist, write it
   from the template below — **do not pre-fill Idea or Goal**; keep Phase 1 minimal.
4. Open in editor/vault if integration is configured (skip if file already existed).
5. Confirm: `Inception file created: $ARTIFACT_DIR/<scope>/<slug>/<slug>-inception.md`
   (or `Inception file exists: …` if already present — no update)

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
```

**Properties (YAML frontmatter):** Document metadata for search and
organization. Always include:

| Field | When | Content |
|-------|------|---------|
| `title` | Phase 1 | Idea name (human-readable) |
| `tags` | Phase 1 → refine at distill | Always include `inception` and `<slug>`; add 2–5 domain tags (lowercase, kebab-case or single words) inferred from the idea name and opening brief |
| `keywords` | Phase 1 → refine at distill | 3–8 search terms: products, users, capabilities, systems mentioned |
| `incepted` | Phase 1 | `YYYY-MM-DD` |

At Phase 1, populate `tags` and `keywords` from whatever is known (idea name,
slug, repos/products in the opening brief). Refine both at distill from the
full interview — do not leave `keywords: []` after distill.


## Phase 2 — Codebase Orientation (if applicable)

If the user is working in an existing codebase, do a quick orientation pass
*before* asking any questions:

- Check the repo root for structure clues (package.json, go.mod, pyproject.toml, etc.)
- Note the primary language, framework, and any patterns already established
- Flag anything in the existing code that's directly relevant to the spec (similar
  features, shared models, existing APIs to extend)

This context informs every question and approach you propose. Follow existing
patterns rather than proposing from scratch. If there's no codebase (greenfield),
note that and proceed.


## Phase 3 — Scope Check

Before going deep, assess whether the spec is the right size for a single design
session. A good scope produces working, independently testable software.

If the spec describes multiple independent subsystems, flag it immediately:

> "This spec spans several independent subsystems. I'd recommend one design
> session per subsystem — they can be built and tested independently. Want to
> start with [most logical first piece]?"

Don't refine details on a project that needs decomposing first.


## Phase 4 — Technical Interrogation

Ask one question at a time. Prefer multiple choice when possible — it's faster
and surfaces tradeoffs naturally.

**Focus areas** (read the spec and ask only what's actually unclear):

- **Data model** — core entities, relationships, where state lives
- **Integration points** — APIs, queues, databases, third-party services
- **Scale & constraints** — expected load, latency requirements
- **Auth & security** — who can do what, compliance requirements
- **Testing strategy** — what does "this works" look like?
- **Deployment & ops** — where does this run, release process

Only ask about constraints that will actually change the design. Three to five
questions is typical for a well-scoped spec.


## Phase 5 — Propose Approaches

Present **2–3 distinct technical approaches** with tradeoffs. Lead with your
recommendation and explain why.

For each approach:
- Name it concisely (e.g., "Event-driven with Redis pub/sub")
- Describe the core idea in 2–3 sentences
- State the key tradeoff (simpler to build vs. more scalable, etc.)

Get the user to pick one before moving to design.

<HARD-GATE>
Do not write any code, scaffold any files, or invoke any implementation skill
until you have presented a design and the user has approved it. This applies
regardless of how simple the spec seems.
</HARD-GATE>


## Phase 6 — Design Document

Once an approach is chosen, write the design. Scale each section to complexity —
a few sentences for simple projects, a full breakdown for complex ones. Get
approval after each section before moving on.

**Cover:**
- **Architecture overview** — the high-level shape of the system
- **Components** — what each unit does and its interfaces
- **Data flow** — how data moves through the system end to end
- **Key decisions** — choices that would be hard to reverse (schema, API
  contracts, storage, external dependencies)
- **Error handling** — what fails, how it fails, what recovers
- **Testing approach** — unit vs. integration vs. e2e boundaries

Design for isolation: each component has one clear purpose, communicates through
well-defined interfaces, and can be understood without reading its neighbors'
internals.


## Phase 7 — Write and Self-Review

**Save the design doc:**

```
$ARTIFACT_DIR/<scope>/<slug>/<slug>-design.md
```

Open in your editor/vault if integration is configured.

**Self-review silently — fix inline, don't ask the user:**

1. **Placeholder scan** — any "TBD", "TODO", vague hand-waves? Fix them.
2. **Consistency check** — do component names, types, and interfaces agree across all sections?
3. **Spec coverage** — can you point to a design decision for every requirement in the spec?
4. **Ambiguity check** — can any requirement be read two ways? Pick one and make it explicit.


## Phase 8 — User Review Gate

> "Design written to `$ARTIFACT_DIR/<scope>/<slug>/<slug>-design.md`.
> Read it over and let me know if anything needs to change before we move to planning."

Wait for approval. Make any changes requested. Only proceed once the user signs off.


## Phase 9 — Handoff to write-plan

> "Design is locked. Moving to implementation planning."

Hand off to [write-plan](write-plan.md) to produce `<slug>-plan.md` under `$ARTIFACT_DIR/<scope>/<slug>/`.


## Key Principles

- **Trust the spec** — product questions are closed; don't re-ask them
- **One question at a time** — never more than one per message
- **Multiple choice preferred** — faster and surfaces tradeoffs
- **Propose approaches before designing** — never skip straight to the design
- **Incremental approval** — get sign-off on each design section
- **No placeholders** — every section complete before handoff
- **Decompose first** — if scoped too large, break it apart before designing
