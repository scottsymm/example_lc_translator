---
name: plan-review
description: "Second-opinion review of an implementation plan. Checks whether a junior engineer could execute it without asking questions. On-demand only — not automatic in the workflow. Trigger on: 'review this plan', 'is this plan ready', 'plan review', 'check my plan', 'is this detailed enough'."
---

# plan-review

Review an implementation plan (typically `<slug>-plan.md`) and determine whether
it is detailed enough for a junior engineer to execute without asking questions.

This is an on-demand quality gate — invoke it when you want a second opinion
before running `execute-plan`.

## Inputs accepted

- **Slug** — resolves to `$ARTIFACT_DIR/<scope>/<slug>/<slug>-plan.md` (see artifact-dir rule)
- **File path** — direct path to any plan file
- **Pasted content** — paste the plan directly into chat

## Behavior

1. **Read the plan** and the associated spec/design if available.
2. **Score on 6 dimensions** (see below).
3. **Produce a gap report** — short, specific, actionable.
4. **Cross-check against spec** — if `<slug>-spec.md` exists, verify every spec
   requirement has a corresponding plan task. Flag spec items with no coverage.
5. **Verdict** — ready to execute, or needs revision.

## Scoring dimensions

Score each 1–3 (1 = weak, 2 = adequate, 3 = strong):

| Dimension | What to check |
|---|---|
| **File specificity** | Does every task name exact file paths and symbols (functions, types, routes) to create or modify? |
| **Code completeness** | Does each task include enough detail that the implementer won't need to make design decisions? No "similar to X" or "as appropriate". |
| **Ordering** | Are tasks ordered so each builds on the last? Are dependencies between tasks explicit? |
| **Verification** | Does every task have a concrete verification command (test, lint, curl, etc.) — not just "confirm it works"? |
| **Commit hygiene** | Does each task specify what to commit and a commit message template? |
| **Spec coverage** | If a spec exists, does the plan cover every requirement? Are there spec items with no plan task? |

## Output format

```
## Plan Review: [Plan Name]

### Scores
- File specificity: X/3
- Code completeness: X/3
- Ordering: X/3
- Verification: X/3
- Commit hygiene: X/3
- Spec coverage: X/3
**Overall: X/18**

### Gaps
1. Task N — [what's missing or ambiguous] → [specific suggested fix]

### Spec Coverage
- [Spec requirement] → Task N ✓
- [Spec requirement] → NOT COVERED ✗

### Verdict
[Ready to execute / Needs revision — a junior engineer would get stuck on: ...]
```

## The junior engineer test

For each task, ask: "If I handed this to someone with 1 year of experience in
this stack and no context beyond this plan, could they complete it without
messaging me?" If the answer is no, the task needs more detail.

Common failures:
- "Update the auth middleware" — which file? what change exactly?
- "Add tests" — which test file? what cases? what assertions?
- "Wire up the endpoint" — what route, method, handler signature, request/response shape?
- "Similar to the existing pattern" — copy the pattern into the task explicitly.

## Do not

- Rewrite the plan without asking first
- Change scope or add tasks — only review what's there
- Give a passing verdict if any dimension scores 1
- Give a passing verdict if spec coverage has uncovered items
