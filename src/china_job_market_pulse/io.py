from __future__ import annotations

import csv
from pathlib import Path

from .models import JobPosting


REQUIRED_COLUMNS = {"title", "city", "skills"}


def _optional_float(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    return float(value.strip())


def _optional_int(value: str | None) -> int | None:
    if value is None or not value.strip():
        return None
    return int(float(value.strip()))


def split_skills(value: str | None) -> tuple[str, ...]:
    """Normalize comma-, slash-, semicolon-, and Chinese-list separators."""

    if not value:
        return ()
    parts = value.replace("，", ",").replace("；", ";").replace("、", ",")
    for separator in ("/", "|", ";"):
        parts = parts.replace(separator, ",")
    return tuple(dict.fromkeys(part.strip() for part in parts.split(",") if part.strip()))


def load_jobs(path: str | Path) -> list[JobPosting]:
    """Load the project's portable CSV format."""

    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or ())
        missing = REQUIRED_COLUMNS - columns
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"CSV is missing required columns: {missing_text}")

        jobs: list[JobPosting] = []
        for row_number, row in enumerate(reader, start=2):
            title = (row.get("title") or "").strip()
            city = (row.get("city") or "").strip()
            if not title or not city:
                raise ValueError(f"CSV row {row_number} needs both title and city")
            try:
                jobs.append(
                    JobPosting(
                        title=title,
                        company=(row.get("company") or "").strip(),
                        city=city,
                        salary_min=_optional_float(row.get("salary_min")),
                        salary_max=_optional_float(row.get("salary_max")),
                        experience_years_min=_optional_int(row.get("experience_years_min")),
                        education=(row.get("education") or "").strip(),
                        skills=split_skills(row.get("skills")),
                        posted_date=(row.get("posted_date") or "").strip() or None,
                        source_url=(row.get("source_url") or "").strip() or None,
                        employment_type=(row.get("employment_type") or "").strip() or None,
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value on CSV row {row_number}: {exc}") from exc
    return jobs

