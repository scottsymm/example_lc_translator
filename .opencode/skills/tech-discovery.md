---
name: tech-discovery
description: "Deep-dive technical discovery on a topic, feature, technology, or codebase. Trigger on \"tech discovery\", \"discover <topic>\", \"technical discovery on\", \"deep dive into\", \"research <topic> for me\". Output is `<slug>-discovery.md` under $ARTIFACT_DIR."
---

# Tech Discovery — Research

Technology research and synthesis skill. Produces a reference artifact that
builds understanding of a topic — what it is, how it works, key concepts,
trade-offs, and gotchas. Theory and understanding — not specs, requirements,
or design.

**Output:** `<slug>-discovery.md` → `$ARTIFACT_DIR/<scope>/<slug>/`


# Role

Research a technology, architecture pattern, or codebase and synthesize it into
one reference artifact. Write with the judgment of someone who has built and
operated production systems — but keep the document tight and readable, not
exhaustive.

# When to use

- "I've heard of X but don't really understand it."
- "How does this codebase / library / framework actually work?"
- "What are the architectural options for Y?"
- Before `tech-incept` when the technology is unfamiliar.

# What this is NOT

- Not a spec or requirements document (use `incept` for that).
- Not an implementation design (use `tech-incept` for that).
- Not a plan with tasks and code changes (use `write-plan` for that).

# Primary Output

A single discovery artifact:

- **Filename:** `<slug>-discovery.md`
- **Path:** `$ARTIFACT_DIR/<scope>/<slug>/<slug>-discovery.md`

Resolve `$ARTIFACT_DIR` and `<scope>` per the artifact-dir rule:

- `<slug>` is the kebab-case subject.
- `<scope>` comes from the cwd or a `for <customer>` phrase in the invocation.
- If the slug directory already exists (from a prior incept/design/discovery),
  save alongside those files — it's the same project.
- Use a `-v2` suffix only if a discovery file from a *previous* session already
  exists. Never hardcode a vault path; never write to `.cursor/plans/`.

The document opens with YAML frontmatter:

```yaml
title: <Human-readable subject>
tags:
  - discovery
  - <slug>
  - <2–4 domain tags>
keywords:
  - <3–8 search terms>
created: YYYY-MM-DD
updated: YYYY-MM-DD
```

Set `created` and `updated` to today on first save; bump `updated` on later edits.

# Document Structure

After the frontmatter, cover these sections in order. Keep the whole document
tight — quality over length, no placeholders, real component names.

1. **Summary** — how it works, written for a mid-level engineer *and* an
   executive. Plain language; lead with what problem it solves and why it matters.
2. **In-depth review** — the technical deep dive using all available sources,
   written for a staff engineer. **No more than two pages.**
3. **Architecture diagrams** — use draw.io if the `drawio` skill/tooling is
   available, otherwise mermaid. Show component boundaries and data flow. Add a
   sequence diagram when it clarifies an interaction an architect would care about.
4. **Use cases** — 2–5 concrete scenarios. For each, say where this tech fits
   and where it does not.
5. **Alternatives** — competing technologies or approaches, and how they compare.
6. **Limitations, risks & gotchas** — honest constraints, failure modes, and
   traps surfaced during research.
7. **References** — the sources the discovery drew from. Prefer official docs,
   RFCs, and authoritative posts over random tutorials. Clickable links.

# Workflow

1. **Resolve the subject.** Parse the invocation — a topic/technology, a codebase
   path or feature, a Linear ticket (`ENG-123`), or a URL. State the subject in
   one sentence, derive `<slug>`, and resolve `<scope>`. If nothing is given,
   ask what to dig into.
2. **Research.** Go deep with every tool available: read the actual codebase,
   current docs, and web sources — not training-data recall. Understand failure
   modes, not just the happy path. Ask few, focused questions (multiple choice
   when possible); otherwise state an assumption and proceed.
3. **Write.** Fill the Document Structure above. Every section substantive.
4. **Save.** Write to `$ARTIFACT_DIR/<scope>/<slug>/<slug>-discovery.md` with the
   frontmatter populated. Confirm: `Saved: <path>`.
5. **Keep it living.** On follow-ups, update the saved file in place and bump
   `updated`. Don't append changelogs or leave stale content behind.
