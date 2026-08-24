from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analysis import analyze_jobs
from .io import load_job_dataset
from .report import build_report, to_csv, to_json, to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze China job-market CSV or JSON data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="generate market reports")
    analyze.add_argument("input_path", type=Path, help="input job-posting CSV or JSON")
    analyze.add_argument("--output", "-o", type=Path, help="Markdown output path")
    analyze.add_argument("--json-output", type=Path, help="optional JSON output path")
    analyze.add_argument("--csv-output", type=Path, help="optional long-form CSV output path")
    analyze.add_argument(
        "--allow-errors",
        action="store_true",
        help="analyze valid rows while retaining validation errors in the quality report",
    )
    analyze.add_argument(
        "--no-dedupe",
        action="store_true",
        help="keep duplicate rows instead of applying the default deterministic dedupe",
    )
    return parser


def _write_text(path: Path | None, content: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "analyze":
        return 2

    try:
        dataset = load_job_dataset(args.input_path, deduplicate=not args.no_dedupe)
    except (OSError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    if dataset.quality.error_count and not args.allow_errors:
        first_error = next(issue for issue in dataset.quality.issues if issue.severity == "error")
        print(
            f"Data quality check failed: {dataset.quality.error_count} error(s); "
            f"first issue is row {first_error.row_number}, field {first_error.field}: {first_error.message}. "
            "Use --allow-errors to analyze valid rows.",
            file=sys.stderr,
        )
        return 2
    if not dataset.jobs:
        print("Data quality check produced no analyzable rows.", file=sys.stderr)
        return 2

    analysis = analyze_jobs(dataset.jobs)
    report = build_report(analysis, dataset.quality, args.input_path.name)
    markdown = to_markdown(report)
    _write_text(args.output, markdown)
    _write_text(args.json_output, to_json(report))
    _write_text(args.csv_output, to_csv(report))
    if args.output is None:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
