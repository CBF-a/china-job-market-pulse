from __future__ import annotations

import csv
import json
from collections.abc import Mapping
from pathlib import Path

from .dedupe import deduplicate_jobs
from .models import DataQualityReport, JobDataset, JobPosting
from .normalize import (
    clean_text,
    normalize_city,
    normalize_company,
    normalize_date,
    normalize_education,
    normalize_title,
    parse_optional_number,
    split_skills,
)
from .quality import REQUIRED_COLUMNS, has_errors, validate_row


def _read_rows(path: Path) -> tuple[list[dict[str, object]], set[str], int]:
    if path.suffix.casefold() == ".json":
        with path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            payload = payload.get("jobs")
        if not isinstance(payload, list) or not all(isinstance(item, Mapping) for item in payload):
            raise ValueError("JSON input must be a list of objects or an object with a jobs list")
        rows = [dict(item) for item in payload]
        columns = {str(key) for row in rows for key in row}
        return rows, columns, 1

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or ())
        rows = [dict(row) for row in reader]
    return rows, columns, 2


def _job_from_row(row: Mapping[str, object], row_number: int, source_name: str | None = None) -> JobPosting:
    title_raw = clean_text(row.get("title"))
    company_raw = normalize_company(row.get("company"))
    city_raw = clean_text(row.get("city"))
    skills_raw = clean_text(row.get("skills"))
    education_raw = clean_text(row.get("education"))
    posted_date = normalize_date(row.get("posted_date"))
    return JobPosting(
        title=normalize_title(title_raw),
        company=company_raw,
        city=normalize_city(city_raw),
        salary_min=parse_optional_number(row.get("salary_min")),
        salary_max=parse_optional_number(row.get("salary_max")),
        experience_years_min=parse_optional_number(row.get("experience_years_min")),
        education=education_raw,
        skills=split_skills(skills_raw),
        posted_date=posted_date,
        source_url=clean_text(row.get("source_url")) or None,
        employment_type=clean_text(row.get("employment_type")) or None,
        title_raw=title_raw,
        company_raw=company_raw or None,
        city_raw=city_raw,
        skills_raw=skills_raw,
        education_normalized=normalize_education(education_raw),
        salary_period="monthly"
        if row.get("salary_min") not in (None, "") or row.get("salary_max") not in (None, "")
        else None,
        row_number=row_number,
        source_name=clean_text(row.get("source_name")) or source_name,
        collected_at=clean_text(row.get("collected_at")) or None,
    )


def load_job_dataset(
    path: str | Path,
    *,
    deduplicate: bool = True,
    source_name: str | None = None,
    source_license: str | None = None,
    access_mode: str | None = None,
) -> JobDataset:
    """Load, validate, normalize, and optionally deduplicate CSV or JSON input."""

    source_path = Path(path)
    rows, columns, first_row_number = _read_rows(source_path)
    missing = REQUIRED_COLUMNS - columns
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Input is missing required columns: {missing_text}")

    issues = []
    valid_jobs: list[JobPosting] = []
    for offset, row in enumerate(rows):
        row_number = first_row_number + offset
        row_issues = validate_row(row, row_number)
        issues.extend(row_issues)
        if not has_errors(row_issues):
            valid_jobs.append(_job_from_row(row, row_number, source_name))

    duplicate_count = 0
    if deduplicate:
        valid_jobs, duplicate_count, duplicate_issues = deduplicate_jobs(valid_jobs)
        issues.extend(duplicate_issues)

    quality = DataQualityReport(
        total_rows=len(rows),
        accepted_rows=len(valid_jobs),
        rejected_rows=len(rows) - len(valid_jobs) - duplicate_count,
        duplicate_rows=duplicate_count,
        issues=tuple(issues),
    )
    return JobDataset(
        tuple(valid_jobs),
        quality,
        str(source_path),
        source_name=source_name,
        source_license=source_license,
        access_mode=access_mode,
    )


def load_jobs(path: str | Path) -> list[JobPosting]:
    """Load jobs in strict compatibility mode.

    Invalid rows are reported as a ValueError, while non-fatal warnings do not
    prevent the caller from using the normalized jobs.
    """

    dataset = load_job_dataset(path)
    if dataset.quality.error_count:
        first_error = next(issue for issue in dataset.quality.issues if issue.severity == "error")
        raise ValueError(f"Input row {first_error.row_number}, {first_error.field}: {first_error.message}")
    return list(dataset.jobs)


# Backwards-compatible import location used by the prototype and its users.
split_skills = split_skills
