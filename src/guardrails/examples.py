"""Curated, non-executing example prompts for the analyst console."""

APPROVED_SNAPSHOT_EXAMPLES = (
    {
        "level": "Beginner",
        "title": "Count transaction types",
        "question": "Show transaction counts by transaction type.",
        "concept": "GROUP BY and a bounded ranked result.",
    },
    {
        "level": "Intermediate",
        "title": "Fraud-rate comparison",
        "question": "Show fraud rate by transaction type.",
        "concept": "Conditional aggregation over the source-provided fraud label.",
    },
    {
        "level": "Advanced",
        "title": "Ranked simulation steps",
        "question": "Rank simulation steps by total transaction amount within each transaction type.",
        "concept": "Window ranking with an explicit order and bounded preview.",
    },
)

DEMO_FIXTURE_EXAMPLES = (
    {
        "level": "Beginner",
        "title": "Count payment channels",
        "question": "Show payment counts by channel.",
        "concept": "GROUP BY over the hand-authored synthetic demo fixture.",
    },
    {
        "level": "Intermediate",
        "title": "Completed amount by channel",
        "question": "Show completed payment amount by channel.",
        "concept": "A filter plus aggregation over the bounded demo fixture.",
    },
    {
        "level": "Advanced",
        "title": "Rank payment channels",
        "question": "Rank payment channels by total payment amount.",
        "concept": "Window ranking with an explicit order and bounded preview.",
    },
)


def examples_for_schema(schema: dict[str, set[str]]) -> tuple[dict[str, str], ...]:
    """Return prompts that can run against the active, identifier-safe schema."""
    return APPROVED_SNAPSHOT_EXAMPLES if "fact_transactions" in schema else DEMO_FIXTURE_EXAMPLES
