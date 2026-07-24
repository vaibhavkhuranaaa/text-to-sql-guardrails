from dataclasses import dataclass


@dataclass(frozen=True)
class SupportedQuestion:
    key: str
    question: str
    sql: str


CATALOG_VERSION = "2026-07-22"
SUPPORTED_QUESTIONS = (
    SupportedQuestion(
        "total_completed_amount",
        "What is the total amount of completed payments?",
        "SELECT ROUND(SUM(amount_usd), 2) AS total_completed_amount_usd FROM fact_payments WHERE status = 'completed'",
    ),
    SupportedQuestion(
        "completed_payments_by_country",
        "Show completed payments by country.",
        "SELECT c.country, COUNT(*) AS payment_count, ROUND(SUM(p.amount_usd), 2) AS total_amount_usd FROM fact_payments AS p JOIN dim_customer AS c ON p.customer_id = c.customer_id WHERE p.status = 'completed' GROUP BY c.country ORDER BY total_amount_usd DESC",
    ),
    SupportedQuestion(
        "daily_completed_amount",
        "Show daily completed payment totals.",
        "SELECT payment_date, ROUND(SUM(amount_usd), 2) AS total_amount_usd FROM fact_payments WHERE status = 'completed' GROUP BY payment_date ORDER BY payment_date",
    ),
    SupportedQuestion(
        "completed_payments_by_segment",
        "Show completed payments by customer segment.",
        "SELECT c.segment, COUNT(*) AS payment_count, ROUND(SUM(p.amount_usd), 2) AS total_amount_usd FROM fact_payments AS p JOIN dim_customer AS c ON p.customer_id = c.customer_id WHERE p.status = 'completed' GROUP BY c.segment ORDER BY total_amount_usd DESC",
    ),
    SupportedQuestion(
        "payments_by_channel",
        "Show payment counts by channel.",
        "SELECT channel, COUNT(*) AS payment_count, ROUND(SUM(amount_usd), 2) AS total_amount_usd FROM fact_payments GROUP BY channel ORDER BY total_amount_usd DESC",
    ),
)


def generate(question: str) -> tuple[str | None, str | None]:
    normalized = " ".join(question.strip().lower().split())
    for item in SUPPORTED_QUESTIONS:
        if normalized == " ".join(item.question.lower().split()):
            return item.sql, None
    return None, (
        "Unsupported question. This deterministic baseline only accepts an exact question "
        "from the documented supported-question catalog."
    )
