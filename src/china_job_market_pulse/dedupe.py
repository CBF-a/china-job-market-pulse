from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from .models import DataIssue, JobPosting


def _key_text(value: object) -> str:
    return "" if value is None else str(value).strip().casefold()


def fingerprint_job(job: JobPosting) -> str:
    """Create a stable identifier from fields that describe one posting."""

    payload = {
        "title": _key_text(job.title),
        "company": _key_text(job.company),
        "city": _key_text(job.city),
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "posted_date": job.posted_date or "",
        "source_url": _key_text(job.source_url),
        "source_name": _key_text(job.source_name),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def deduplicate_jobs(jobs: list[JobPosting]) -> tuple[list[JobPosting], int, tuple[DataIssue, ...]]:
    """Keep the first occurrence of each fingerprint and report later rows."""

    seen: set[str] = set()
    unique: list[JobPosting] = []
    issues: list[DataIssue] = []
    duplicate_count = 0
    for job in jobs:
        fingerprint = fingerprint_job(job)
        if fingerprint in seen:
            duplicate_count += 1
            issues.append(
                DataIssue(
                    severity="warning",
                    row_number=job.row_number or 0,
                    field="record",
                    code="DUPLICATE_RECORD",
                    message="duplicate posting removed; first occurrence was retained",
                    value=fingerprint,
                )
            )
            continue
        seen.add(fingerprint)
        unique.append(replace(job, record_id=fingerprint))
    return unique, duplicate_count, tuple(issues)
