from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

from .models import DataIssue
from .normalize import clean_text, normalize_date, parse_optional_number, split_skills


REQUIRED_COLUMNS = frozenset({"title", "city", "skills"})


def _value(row: Mapping[str, object], field: str) -> str:
    return clean_text(row.get(field))


def _issue(
    severity: Literal["error", "warning"],
    row_number: int,
    field: str,
    code: str,
    message: str,
    value: str | None = None,
) -> DataIssue:
    return DataIssue(severity=severity, row_number=row_number, field=field, code=code, message=message, value=value)


def validate_row(row: Mapping[str, object], row_number: int) -> tuple[DataIssue, ...]:
    """Validate one raw row without mutating it."""

    issues: list[DataIssue] = []
    for field in sorted(REQUIRED_COLUMNS):
        value = _value(row, field)
        if not value:
            issues.append(_issue("error", row_number, field, "REQUIRED", f"{field} is required", value or None))

    numeric_values: dict[str, float | None] = {}
    for field in ("salary_min", "salary_max", "experience_years_min"):
        raw = _value(row, field)
        if not raw:
            numeric_values[field] = None
            continue
        try:
            numeric_values[field] = parse_optional_number(raw)
        except ValueError as exc:
            issues.append(_issue("error", row_number, field, "INVALID_NUMBER", str(exc), raw))
            numeric_values[field] = None

    salary_min = numeric_values["salary_min"]
    salary_max = numeric_values["salary_max"]
    for field in ("salary_min", "salary_max", "experience_years_min"):
        value = numeric_values[field]
        if value is not None and value < 0:
            issues.append(_issue("error", row_number, field, "NEGATIVE_NUMBER", f"{field} cannot be negative", str(value)))

    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        issues.append(
            _issue(
                "error",
                row_number,
                "salary_min",
                "SALARY_ORDER",
                "salary_min cannot be greater than salary_max",
                f"{salary_min}>{salary_max}",
            )
        )
    if (salary_min is None) != (salary_max is None):
        issues.append(
            _issue(
                "warning",
                row_number,
                "salary",
                "PARTIAL_SALARY",
                "only one salary bound is present; range statistics may be incomplete",
            )
        )

    posted_date = _value(row, "posted_date")
    if posted_date and normalize_date(posted_date) is None:
        issues.append(_issue("error", row_number, "posted_date", "INVALID_DATE", "posted_date must be ISO 8601", posted_date))
    elif not posted_date:
        issues.append(_issue("warning", row_number, "posted_date", "MISSING_DATE", "posted_date is missing"))

    source_url = _value(row, "source_url")
    if source_url:
        parsed = urlparse(source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            issues.append(_issue("error", row_number, "source_url", "INVALID_URL", "source_url must be an http(s) URL", source_url))

    skills = split_skills(row.get("skills"))
    if _value(row, "skills") and not skills:
        issues.append(_issue("warning", row_number, "skills", "EMPTY_SKILLS", "skills contains no usable values"))

    return tuple(issues)


def has_errors(issues: tuple[DataIssue, ...] | list[DataIssue]) -> bool:
    return any(issue.severity == "error" for issue in issues)


@dataclass(frozen=True, slots=True)
class QualityThresholds:
    """Policy thresholds for deciding whether an import needs attention."""

    max_rejected_rate: float = 0.0
    max_duplicate_rate: float = 0.2
    max_warning_rate: float = 0.5


@dataclass(frozen=True, slots=True)
class QualityAlert:
    severity: Literal["error", "warning"]
    metric: str
    observed: float
    threshold: float
    message: str

    def to_dict(self) -> dict[str, str | float]:
        return {
            "severity": self.severity,
            "metric": self.metric,
            "observed": self.observed,
            "threshold": self.threshold,
            "message": self.message,
        }


def monitor_quality(report, thresholds: QualityThresholds | None = None) -> tuple[QualityAlert, ...]:
    """Return deterministic alerts for a completed import quality report."""

    policy = thresholds or QualityThresholds()
    denominator = max(report.total_rows, 1)
    rejected_rate = report.rejected_rows / denominator
    duplicate_rate = report.duplicate_rows / denominator
    warning_rate = report.warning_count / denominator
    alerts: list[QualityAlert] = []
    if rejected_rate > policy.max_rejected_rate:
        alerts.append(
            QualityAlert(
                "error",
                "rejected_rate",
                round(rejected_rate, 6),
                policy.max_rejected_rate,
                "rejected row rate exceeds the configured threshold",
            )
        )
    if duplicate_rate > policy.max_duplicate_rate:
        alerts.append(
            QualityAlert(
                "warning",
                "duplicate_rate",
                round(duplicate_rate, 6),
                policy.max_duplicate_rate,
                "duplicate row rate exceeds the configured threshold",
            )
        )
    if warning_rate > policy.max_warning_rate:
        alerts.append(
            QualityAlert(
                "warning",
                "warning_rate",
                round(warning_rate, 6),
                policy.max_warning_rate,
                "quality warning rate exceeds the configured threshold",
            )
        )
    return tuple(alerts)
