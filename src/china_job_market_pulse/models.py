from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JobPosting:
    """A normalized job posting used by the analysis pipeline."""

    title: str
    company: str
    city: str
    salary_min: float | None
    salary_max: float | None
    experience_years_min: int | None
    education: str
    skills: tuple[str, ...]
    posted_date: str | None = None
    source_url: str | None = None
    employment_type: str | None = None

