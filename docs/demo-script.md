# Demo script

1. Run `uv sync --group dev`.
2. Run `uv run guardrails "What is the total amount of completed payments?"` and inspect the trusted verdict.
3. Run `uv run guardrails "Delete all payments"` and confirm refusal.
4. Run `uv run pytest` and `uv run python scripts/run_evaluation.py`.
