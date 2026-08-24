from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyze_jobs
from .io import load_jobs
from .report import to_json, to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze China job-market CSV data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="generate a Markdown market report")
    analyze.add_argument("csv_path", type=Path, help="input job-posting CSV")
    analyze.add_argument("--output", "-o", type=Path, help="Markdown output path")
    analyze.add_argument("--json-output", type=Path, help="optional JSON output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        report = analyze_jobs(load_jobs(args.csv_path))
        markdown = to_markdown(report, args.csv_path.name)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(markdown, encoding="utf-8")
        else:
            print(markdown)
        if args.json_output:
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(to_json(report), encoding="utf-8")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

