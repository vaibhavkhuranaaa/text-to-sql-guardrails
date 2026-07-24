import argparse
import json
import sys
from pathlib import Path

from .catalog import SUPPORTED_QUESTIONS
from .pipeline import DataQualityError, build_snapshot, fetch_source, write_profile
from .service import query


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "data":
        _data_main(sys.argv[2:])
        return
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


def _data_main(arguments: list[str]) -> None:
    parser = argparse.ArgumentParser(description="Run owner-approved data release steps.")
    commands = parser.add_subparsers(dest="command", required=True)
    fetch = commands.add_parser("fetch", help="Fetch checksum-pinned source files.")
    fetch.add_argument("--manifest", type=Path, default=Path("data/source_manifest.json"))
    fetch.add_argument("--destination", type=Path, default=Path("data/raw"))
    build = commands.add_parser("build", help="Normalize a reviewed CSV into an approved snapshot.")
    build.add_argument("--source", type=Path, required=True)
    build.add_argument("--snapshot", type=Path, default=Path("data/approved/payments.duckdb"))
    build.add_argument("--manifest", type=Path, default=Path("data/source_manifest.json"))
    profile = commands.add_parser("profile", help="Create a row-free schema and quality profile.")
    profile.add_argument("--source", type=Path, required=True, action="append")
    profile.add_argument("--out", type=Path, default=Path("data/approved/profile.json"))
    args = parser.parse_args(arguments)
    try:
        if args.command == "fetch":
            print(json.dumps([str(path) for path in fetch_source(args.manifest, args.destination)]))
        elif args.command == "profile":
            print(json.dumps(write_profile(args.source, args.out), indent=2))
        else:
            print(json.dumps(build_snapshot(args.source, args.snapshot, args.manifest), indent=2))
    except DataQualityError as exc:
        parser.error(str(exc))
