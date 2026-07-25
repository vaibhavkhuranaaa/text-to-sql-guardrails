# Evaluation

Run `uv run python scripts/run_evaluation.py`. The committed JSON and Markdown report are generated from the local fixture and cover supported, unsupported, unsafe, malformed SQL, unknown table/column, empty-result, explicit NULL-bucket, and ordered/unordered-ranking paths. The report records execution accuracy, safety-rejection rate, hallucination-detection rate, local latency percentiles, and local cost. It does not measure Foundry behavior; the separately verified Entra workflow is integration evidence only.

`uv run python scripts/run_benchmark.py --snapshot data/approved/payments.duckdb` produces transaction row counts, transaction-type group count, query elapsed time, and runtime disclosure only from a real local snapshot run. It is not a production benchmark, model evaluation, or production SLO.

`uv run python scripts/run_private_ibm_evaluation.py` produces an ignored, aggregate-only M4 report from the separately approved local IBM AML derivative. It records the pinned curated-content digest, case/pass/fail counts, threshold, and limitations only. It contains no rows, prompts, SQL, identifiers, labels, tokens, or environment values; it is not served, deployed, or a model, load, or production evaluation.
