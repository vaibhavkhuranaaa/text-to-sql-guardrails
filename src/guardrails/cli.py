import argparse
import json

from .catalog import SUPPORTED_QUESTIONS
from .service import query


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the local Text-to-SQL Guardrails walkthrough."
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Exact supported question, or an unsupported question to demonstrate refusal.",
    )
    parser.add_argument("--list", action="store_true", help="List exact supported questions.")
    args = parser.parse_args()
    if args.list:
        print("\n".join(item.question for item in SUPPORTED_QUESTIONS))
        return
    print(
        json.dumps(query(args.question or SUPPORTED_QUESTIONS[0].question), indent=2, default=str)
    )
