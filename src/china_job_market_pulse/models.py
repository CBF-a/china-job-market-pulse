from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SCHEMA_VERSION = "0.2"


@dataclass(frozen=True, slots=True)
class JobPosting:
    """A normalized job posting used by the analysis pipeline.

    The first eight fields preserve the original public constructor used by
    the prototype. Metadata fields are appended so existing callers remain
    compatible while the data layer can retain provenance and row context.
    """

    title: str
    company: str
    city: str
    salary_min: float | None
    salary_max: float | None
    experience_years_min: float | None
    education: str
    skills: tuple[str, ...]
    posted_date: str | None = None
    source_url: str | None = None
    employment_type: str | None = None
    title_raw: str | None = None
    company_raw: str | None = None
    city_raw: str | None = None
    skills_raw: str | None = None
    education_normalized: str | None = None
    salary_period: str | None = None
    record_id: str | None = None
    row_number: int | None = None
    source_name: str | None = None
    collected_at: str | None = None


@dataclass(frozen=True, slots=True)
class DataIssue:
    """A row-level validation or normalization issue."""

    severity: Literal["error", "warning"]
    row_number: int
    field: str
    code: str
    message: str
    value: str | None = None

    def to_dict(self) -> dict[str, str | int | None]:
        return {
            "severity": self.severity,
            "row_number": self.row_number,
            "field": self.field,
            "code": self.code,
            "message": self.message,
            "value": self.value,
        }


@dataclass(frozen=True, slots=True)
class DataQualityReport:
    """Summary of accepted, rejected, duplicate, and problematic rows."""

    total_rows: int
    accepted_rows: int
    rejected_rows: int
    duplicate_rows: int
    issues: tuple[DataIssue, ...] = ()

    @property
    def error_count(self) -> int:
        return sum(issue.severity == "error" for issue in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "total_rows": self.total_rows,
            "accepted_rows": self.accepted_rows,
            "rejected_rows": self.rejected_rows,
            "duplicate_rows": self.duplicate_rows,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True, slots=True)
class JobDataset:
    """Normalized jobs plus the quality and provenance of one import run."""

    jobs: tuple[JobPosting, ...]
    quality: DataQualityReport
    source_path: str
    schema_version: str = SCHEMA_VERSION
    source_name: str | None = None
    source_license: str | None = None
    access_mode: str | None = None
