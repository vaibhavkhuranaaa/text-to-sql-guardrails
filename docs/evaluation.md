# Evaluation

Run `uv run python scripts/run_evaluation.py`. The committed JSON and Markdown report are generated from the local fixture and cover supported, unsupported, unsafe, malformed SQL, unknown table/column, and empty-result paths. The report records execution accuracy, safety-rejection rate, hallucination-detection rate, local latency percentiles, and local cost.

It is not a production benchmark, model evaluation, or production SLO.
