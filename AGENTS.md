# AGENTS.md

Read `docs/STATE.md`, `docs/HANDOFF.md`, and local Graphify output before broad exploration. Query Graphify for the relevant path first.

Use only permitted data. Do not invent evidence, metrics, URLs, or deployment status. Do not commit secrets or generated dependency directories. Use conventional commits with the configured human identity only; never add AI/model co-author trailers.

At 90% context usage begin a checkpoint. At 95%, stop feature work, update state and handoff, commit/push green work, and preserve any non-green diff precisely in the handoff. Never create a knowingly broken commit.

## Lean delivery policy

Define the smallest verified vertical slice before writing code. Do not add features, abstractions, dependencies, files, or documentation that do not directly serve the charter, acceptance criteria, deployment, or portfolio evidence.

The lead may delegate only a bounded, independent research, implementation, testing, or review task with a named deliverable and file scope. Run one worker at a time by default; two are allowed only when their file scopes cannot overlap. Stop and reassess after four worker runs in a milestone. Each worker returns a concise evidence handoff and must not broadly reread the repository.
