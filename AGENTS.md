# Text-to-SQL Guardrails agent contract

## Authority

- Current implementation state: `docs/STATE.md`.
- Continuation instructions: `docs/HANDOFF.md`.
- Public facts, evidence, deployment classification, and résumé candidates: `portfolio/project.json`.
- Structured deployment observation: `evidence/deployment/anonymous-live-demo.json`.
- Dataset source, license, checksums, and classification: `data/PROVENANCE.md` and `data/source_manifest.json`.
- Generated evaluation: `evaluation/report.json`; source is `scripts/run_evaluation.py`.

## Working rules

- Query fresh Graphify output first when it covers the relevant files. The current graph is AST-only and omits documentation; inspect source directly for uncovered work.
- Preserve the untracked `data/.DS_Store` and any unrelated dirty changes unless the owner separately authorizes removal.
- Use only permitted synthetic data. Never log or publish raw questions, result rows, tokens, environment values, raw source rows, or source identifiers.
- Do not invent metrics, URLs, checks, deployment state, or production claims. Every résumé bullet and public metric must resolve to a versioned evidence ID.
- Use purpose branches and conventional commits with the configured human identity. Never add an AI/model author or co-author.
- Merging a completed release to `main` authorizes automatic redeployment to the declared existing Azure target, live-SHA verification, and portfolio synchronization. New or expanded cloud spending and teardown remain separately owner-gated.
- Delegation is optional and bounded; do not use subagents when coordination costs more than direct work.
- Use host-reported context/quota signals. Update `docs/STATE.md` and `docs/HANDOFF.md` before a handoff; do not claim automatic percentage detection.

## Required checks

Run formatting, lint, tests, evaluation generation, manifest validation, Docker Compose validation, the container data-boundary check, and `git diff --check`. Publication stays blocked while `githubUrl` is null or the anonymous-demo limitations are unresolved.
