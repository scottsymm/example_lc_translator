---
name: drawio
description: "Create and embed diagrams in plans, designs, specs, and other artifacts using Draw.io or Excalidraw. Use when a visual diagram would clarify architecture, flow, scope, or relationships."
---

# Draw.io — Diagrams in Artifacts

Diagram creation and management skill for embedded visuals in plans, designs, specs, and discovery artifacts.

## When to Use

- You want to add architecture, flow, or relationship diagrams to a plan, design, or spec
- You need to iterate on a diagram alongside narrative documentation
- You're working in an artifact that benefits from visual communication (system architecture, data flows, decision trees, timelines)

## When to Skip

- The artifact is text-only and diagrams aren't helpful
- A quick sketch or placeholder is sufficient — wait until the artifact is more solid


## Quick Start

### Option 1: Use Excalidraw (Built-in)

The Excalidraw MCP is available in Claude Code. Create diagrams programmatically:

```
/excalidraw create
```

This creates an editable diagram you can save to your artifact.

### Option 2: Use draw.io Online Editor

1. Go to **[draw.io](https://app.diagrams.net)**
2. Start a new diagram
3. Design your diagram (no account needed; auto-saves to browser)
4. Export as PNG/SVG and embed in your artifact file, or copy the XML and save it

### Option 3: Embed Draw.io Diagrams Directly

Save your diagram as XML in a `.drawio` file alongside your artifact:

```
$ARTIFACT_DIR/<scope>/<slug>/<slug>-diagram.drawio
```

Add a reference in the artifact markdown:

```markdown
![Diagram](./slug-diagram.drawio)

<!-- To edit: open slug-diagram.drawio in draw.io -->
```


## Workflow Integration

### In Plans

Use diagrams to show:
- Task dependencies and timeline
- System components being modified
- Before/after state
- Risk areas or critical paths

**File pattern:**
```
$ARTIFACT_DIR/<scope>/<slug>/<slug>-plan.md
$ARTIFACT_DIR/<scope>/<slug>/<slug>-plan-diagram.drawio  (optional)
```

### In Designs

Use diagrams for:
- System architecture
- Data flow / request flow
- Component hierarchy
- Decision trees for complex logic

**File pattern:**
```
$ARTIFACT_DIR/<scope>/<slug>/<slug>-design.md
$ARTIFACT_DIR/<scope>/<slug>/<slug>-design-diagram.drawio  (optional)
```

### In Specs

Use diagrams to clarify:
- Feature scope and boundaries
- User journeys
- State transitions
- Integration points

**File pattern:**
```
$ARTIFACT_DIR/<scope>/<slug>/<slug>-spec.md
$ARTIFACT_DIR/<scope>/<slug>/<slug>-spec-diagram.drawio  (optional)
```

### In Discovery

Use diagrams to map:
- Technology landscape / ecosystem
- Component relationships
- Trade-off matrices
- Risk/impact graphs

**File pattern:**
```
$ARTIFACT_DIR/<scope>/<slug>/<slug>-discovery.md
$ARTIFACT_DIR/<scope>/<slug>/<slug>-discovery-diagram.drawio  (optional)
```


## Embedding Diagrams in Markdown

### As Image (PNG/SVG)

Export from draw.io and commit to the artifact directory:

```markdown
![Architecture Overview](./architecture-diagram.png)
```

**Pros:** Works in Obsidian, GitHub, and all markdown viewers
**Cons:** Must re-export after edits

### As Embedded SVG

Copy the SVG export directly into the markdown:

```markdown
<svg width="800" height="600" ...><!-- diagram XML --></svg>
```

**Pros:** Inline, version-controlled, no extra files
**Cons:** Can be verbose; harder to edit (needs draw.io reimport)

### As Link (Shareable)

Use draw.io's share feature to generate a public URL:

1. Save your diagram to draw.io cloud
2. Share → Link → Copy
3. Add to artifact:

```markdown
[View diagram on draw.io](https://app.diagrams.net/#G...)
```

**Pros:** Always up-to-date, collaborative
**Cons:** External dependency, requires internet

### As XML File

Save `.drawio` file alongside the artifact for later editing:

```markdown
[Edit diagram](./slug-diagram.drawio)

Or import the XML into [draw.io](https://app.diagrams.net) → File → Open → [upload file]
```

**Pros:** Version-controlled, no external tools needed to view
**Cons:** Requires draw.io to edit; not visible in markdown preview


## Hard Rules

- **Always** use `$ARTIFACT_DIR` — never hardcode vault paths.
- **File naming:** Use `<slug>-<artifact-type>-diagram.*` (e.g. `my-feature-plan-diagram.drawio`)
- **Single diagram per artifact type** unless the artifact explicitly calls for multiple (e.g. "before and after" diagrams)
- Commit diagrams to version control (`.drawio` files, PNG/SVG exports) — don't rely on external links alone
- If a diagram becomes stale during artifact iteration, update it alongside the text
- Use consistent styling across diagrams in the same scope (colors, fonts, shapes) for a cohesive visual language
