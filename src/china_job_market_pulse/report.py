from __future__ import annotations

import json


def to_markdown(report: dict, source_name: str) -> str:
    overall = report["overall"]
    insights = report["insights"]
    lines = [
        "# China Job Market Pulse",
        "",
        f"> Source: `{source_name}`",
        "> Salary values are interpreted as monthly CNY units from the input CSV.",
        "",
        "## Overview",
        "",
        f"- Job postings: **{overall['total_jobs']}**",
        f"- Cities: **{overall['city_count']}**",
        f"- Median salary range: **{overall['salary_min_median']}–{overall['salary_max_median']}**",
        "",
        "## Key signals",
        "",
        f"- Most demanded skill: **{insights['most_demanded_skill'] or 'N/A'}**",
        f"- Largest job market: **{insights['largest_job_market'] or 'N/A'}**",
        f"- Highest median salary ceiling: **{insights['highest_median_salary_city'] or 'N/A'}**",
        "",
        "## Skill demand",
        "",
        "| Skill | Job postings |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {item['name']} | {item['job_count']} |" for item in report["skills"])
    lines.extend(["", "## City comparison", "", "| City | Jobs | Median min | Median max |", "| --- | ---: | ---: | ---: |"])
    for city, values in report["cities"].items():
        lines.append(
            f"| {city} | {values['job_count']} | {values['salary_min_median'] or 'N/A'} | {values['salary_max_median'] or 'N/A'} |"
        )
    lines.extend(
        [
            "",
            "## Reproducibility",
            "",
            "This report is generated from the input CSV with the `jobpulse analyze` command.",
            "Use public, permissioned, or user-exported data and follow each source's terms.",
            "",
        ]
    )
    return "\n".join(lines)


def to_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"

