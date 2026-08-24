from __future__ import annotations

import csv
import json
from io import StringIO

from .models import SCHEMA_VERSION, DataQualityReport


def build_report(
    analysis: dict,
    quality: DataQualityReport,
    source_name: str,
    *,
    source_license: str | None = None,
    access_mode: str | None = None,
) -> dict:
    """Wrap analysis with stable schema, provenance, and quality metadata."""

    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_version": analysis.get("analysis_version", "unknown"),
        "metadata": {
            "source_name": source_name,
            "job_count": analysis.get("overall", {}).get("total_jobs", 0),
            "source_license": source_license,
            "access_mode": access_mode,
        },
        "quality": quality.to_dict(),
        "analysis": analysis,
    }


def _analysis(report: dict) -> dict:
    """Accept both the current wrapped report and the prototype shape."""

    return report.get("analysis", report)


def to_markdown(report: dict, source_name: str | None = None) -> str:
    analysis = _analysis(report)
    overall = analysis["overall"]
    insights = analysis["insights"]
    quality = report.get("quality", {})
    metadata = report.get("metadata", {})
    display_source = source_name or metadata.get("source_name") or "unknown"
    lines = [
        "# China Job Market Pulse",
        "",
        f"> Source: `{display_source}`",
        "> Salary values are interpreted as monthly CNY units from the input data.",
        "",
        "## Overview",
        "",
        f"- Job postings: **{overall['total_jobs']}**",
        f"- Cities: **{overall['city_count']}**",
        f"- Median salary range: **{overall['salary_min_median']}–{overall['salary_max_median']}**",
        f"- Salary missing rate: **{overall.get('salary_missing_rate', 'N/A')}**",
    ]
    if quality:
        lines.extend(
            [
                f"- Input rows: **{quality.get('total_rows', 'N/A')}**",
                f"- Rejected rows: **{quality.get('rejected_rows', 'N/A')}**",
                f"- Duplicate rows: **{quality.get('duplicate_rows', 'N/A')}**",
                f"- Quality warnings: **{quality.get('warning_count', 'N/A')}**",
            ]
        )
    lines.extend(
        [
            "",
            "## Key signals",
            "",
            f"- Most demanded skill: **{insights['most_demanded_skill'] or 'N/A'}**",
            f"- Largest job market: **{insights['largest_job_market'] or 'N/A'}**",
            f"- Highest median salary ceiling: **{insights['highest_median_salary_city'] or 'N/A'}**",
            "",
            "## Skill demand",
            "",
            "| Skill | Job postings | Share |",
            "| --- | ---: | ---: |",
        ]
    )
    lines.extend(f"| {item['name']} | {item['job_count']} | {item.get('job_share', 'N/A')} |" for item in analysis["skills"])
    lines.extend(["", "## City comparison", "", "| City | Jobs | Share | Median min | Median max |", "| --- | ---: | ---: | ---: | ---: |"])
    for city, values in analysis["cities"].items():
        lines.append(
            f"| {city} | {values['job_count']} | {values.get('job_share', 'N/A')} | {values['salary_min_median'] if values['salary_min_median'] is not None else 'N/A'} | {values['salary_max_median'] if values['salary_max_median'] is not None else 'N/A'} |"
        )
    for title, key in (("Experience distribution", "experience"), ("Education distribution", "education"), ("Role distribution", "roles")):
        lines.extend(["", f"## {title}", "", "| Group | Jobs | Share |", "| --- | ---: | ---: |"])
        lines.extend(f"| {item['name']} | {item['job_count']} | {item.get('job_share', 'N/A')} |" for item in analysis.get(key, []))
    lines.extend(["", "## Monthly trend", "", "| Month | Jobs | Median min | Median max |", "| --- | ---: | ---: | ---: |"])
    for item in analysis.get("trends", []):
        lines.append(
            f"| {item['period']} | {item['job_count']} | {item['salary_min_median'] if item['salary_min_median'] is not None else 'N/A'} | {item['salary_max_median'] if item['salary_max_median'] is not None else 'N/A'} |"
        )
    lines.extend(
        [
            "",
            "## Reproducibility",
            "",
            "This report is generated from the input file with the `jobpulse analyze` command.",
            "Use public, permissioned, or user-exported data and follow each source's terms.",
            "",
        ]
    )
    return "\n".join(lines)


def to_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


CSV_FIELDS = (
    "section",
    "name",
    "period",
    "job_count",
    "job_share",
    "salary_min_median",
    "salary_max_median",
    "salary_min_average",
    "salary_max_average",
    "salary_missing_rate",
)


def _csv_row(section: str, item: dict, *, name: str = "", period: str = "") -> dict[str, object]:
    return {
        "section": section,
        "name": name or item.get("name", ""),
        "period": period or item.get("period", ""),
        **{field: item.get(field, "") for field in CSV_FIELDS[3:]},
    }


def to_csv(report: dict) -> str:
    """Export core report sections as one stable long-form CSV."""

    analysis = _analysis(report)
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerow(_csv_row("overall", analysis["overall"], name="all"))
    for section in ("skills", "cities", "experience", "education", "roles"):
        values = analysis.get(section, {})
        if isinstance(values, dict):
            values = [{"name": name, **item} for name, item in values.items()]
        for item in values:
            writer.writerow(_csv_row(section, item))
    for item in analysis.get("trends", []):
        writer.writerow(_csv_row("trends", item, period=item["period"]))
    return output.getvalue()
