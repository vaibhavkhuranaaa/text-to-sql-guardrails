"""Curated, non-executing example prompts for the analyst console."""

EXAMPLES = (
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
