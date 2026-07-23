# Agents

This project uses the agent-workbench standard dev-workflow. Detailed
instructions live in `.opencode/instructions.md`.

## Pipeline

`incept` → `tech-incept` → `tech-discovery` (optional) → `write-plan` →
`plan-review` (optional) → `execute-plan` → `git-pr` / `github-pr-description`

Each skill produces a single artifact under
`$ARTIFACT_DIR/<scope>/<slug>/<slug>-*.md`. See `.opencode/instructions.md`
section "Artifact directory" for `<scope>` resolution.
