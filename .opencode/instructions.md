# OpenCode instructions

This project uses the agent-workbench standard dev-workflow.

## Skills

Skills are installed into `.opencode/skills/` from the agent-workbench `skills/`
directory. Each skill is a plain markdown file with sections for role, inputs,
outputs, and workflow.

The pipeline:

`incept` → `tech-incept` → `tech-discovery` (optional) → `write-plan` →
`plan-review` (optional) → `execute-plan` → `git-pr` / `github-pr-description`

## Artifact directory (`ARTIFACT_DIR` + `<scope>`)

Every artifact path is `$ARTIFACT_DIR/<scope>/<slug>/<slug>-*.md`.

### `ARTIFACT_DIR`

Read from environment. Fallback: `./artifacts/` relative to cwd.

### `<scope>` resolution

Build `<scope>` from two inputs:

1. **Explicit `for <customer>`** in the invocation
   (`"incept an idea for Gloo"`, `"plan for Thickideas"`).
2. **Workspace path** from cwd — strip `$HOME` and any leading segments named
   in `ARTIFACT_DIR_STRIP_SEGMENTS` (comma-separated env var, default `dev`).
   Take the next two segments as `<customer>/<workspace>`.

| Inputs | `<scope>` |
|--------|-----------|
| Explicit `for <customer>` + matching workspace | `<customer>/<project>` |
| Explicit `for <customer>` only | `<customer>` |
| Workspace only | `<customer>/<project>` |
| Neither | (empty — `$ARTIFACT_DIR/<slug>/`) |

### Case rule

Reuse existing directory casing under `$ARTIFACT_DIR` when present. Otherwise
prefer the casing the user typed.

## Hard rules

- Always resolve `$ARTIFACT_DIR` from environment — never hardcode vault paths.
- Use slug-prefixed filenames: `<slug>-inception.md`, `<slug>-spec.md`,
  `<slug>-design.md`, `<slug>-discovery.md`, `<slug>-plan.md`.
- Confirm the final path before writing the first artifact in a new scope.
- Skills are deterministic and bounded.
