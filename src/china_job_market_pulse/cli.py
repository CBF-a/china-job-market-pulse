from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analysis import analyze_jobs
from .dashboard import to_dashboard_html
from .io import load_job_dataset
from .report import build_report, to_csv, to_json, to_markdown


def _add_quality_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--allow-errors",
        action="store_true",
        help="analyze valid rows while retaining validation errors in the quality report",
    )
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="keep duplicate rows instead of applying the default deterministic dedupe",
    )
    parser.add_argument("--source-name", help="human-readable source name for provenance")
    parser.add_argument("--source-license", help="data license or permission note")
    parser.add_argument(
        "--access-mode",
        choices=("synthetic", "user_export", "public_dataset", "authorized_api"),
        help="declared access mode for the input source",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze China job-market CSV or JSON data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="generate market reports")
    analyze.add_argument("input_path", type=Path, help="input job-posting CSV or JSON")
    analyze.add_argument("--output", "-o", type=Path, help="Markdown output path")
    analyze.add_argument("--json-output", type=Path, help="optional JSON output path")
    analyze.add_argument("--csv-output", type=Path, help="optional long-form CSV output path")
    _add_quality_options(analyze)

    dashboard = subparsers.add_parser("dashboard", help="generate a self-contained local HTML dashboard")
    dashboard.add_argument("input_path", type=Path, help="input job-posting CSV or JSON")
    dashboard.add_argument("--output", "-o", type=Path, help="HTML output path")
    _add_quality_options(dashboard)
    return parser


def _write_text(path: Path | None, content: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _load_report(
    input_path: Path,
    allow_errors: bool,
    deduplicate: bool,
    source_name: str | None,
    source_license: str | None,
    access_mode: str | None,
) -> dict | None:
    try:
        dataset = load_job_dataset(
            input_path,
            deduplicate=deduplicate,
            source_name=source_name,
            source_license=source_license,
            access_mode=access_mode,
        )
    except (OSError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return None

    if dataset.quality.error_count and not allow_errors:
        first_error = next(issue for issue in dataset.quality.issues if issue.severity == "error")
        print(
            f"Data quality check failed: {dataset.quality.error_count} error(s); "
            f"first issue is row {first_error.row_number}, field {first_error.field}: {first_error.message}. "
            "Use --allow-errors to analyze valid rows.",
            file=sys.stderr,
        )
        return None
    if not dataset.jobs:
        print("Data quality check produced no analyzable rows.", file=sys.stderr)
        return None

    analysis = analyze_jobs(dataset.jobs)
    return build_report(
        analysis,
        dataset.quality,
        source_name or input_path.name,
        source_license=source_license,
        access_mode=access_mode,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        report = _load_report(
            args.input_path,
            args.allow_errors,
            not args.no_dedupe,
            args.source_name,
            args.source_license,
            args.access_mode,
        )
        if report is None:
            return 2
        markdown = to_markdown(report)
        _write_text(args.output, markdown)
        _write_text(args.json_output, to_json(report))
        _write_text(args.csv_output, to_csv(report))
        if args.output is None:
            print(markdown)
        return 0

    if args.command == "dashboard":
        report = _load_report(
            args.input_path,
            args.allow_errors,
            not args.no_dedupe,
            args.source_name,
            args.source_license,
            args.access_mode,
        )
        if report is None:
            return 2
        dashboard = to_dashboard_html(report)
        _write_text(args.output, dashboard)
        if args.output is None:
            print(dashboard)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
