from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, median
from typing import Iterable

from .models import JobPosting


def _rounded(value: float | None) -> float | None:
    return round(value, 2) if value is not None else None


def _salary_values(jobs: Iterable[JobPosting], field: str) -> list[float]:
    return [value for job in jobs if (value := getattr(job, field)) is not None]


def _salary_summary(jobs: list[JobPosting]) -> dict[str, float | None]:
    minimums = _salary_values(jobs, "salary_min")
    maximums = _salary_values(jobs, "salary_max")
    return {
        "salary_min_median": _rounded(median(minimums)) if minimums else None,
        "salary_max_median": _rounded(median(maximums)) if maximums else None,
        "salary_min_average": _rounded(mean(minimums)) if minimums else None,
        "salary_max_average": _rounded(mean(maximums)) if maximums else None,
    }


def analyze_jobs(jobs: Iterable[JobPosting]) -> dict:
    """Return JSON-serializable market indicators for normalized postings."""

    normalized = list(jobs)
    if not normalized:
        raise ValueError("At least one job posting is required")

    skills = Counter(skill for job in normalized for skill in job.skills)
    titles = Counter(job.title for job in normalized)
    cities: dict[str, list[JobPosting]] = defaultdict(list)
    for job in normalized:
        cities[job.city].append(job)

    city_summary = {}
    for city, city_jobs in sorted(cities.items()):
        city_summary[city] = {"job_count": len(city_jobs), **_salary_summary(city_jobs)}

    top_skill = skills.most_common(1)[0][0] if skills else None
    top_city = max(city_summary, key=lambda city: city_summary[city]["job_count"])
    best_paid_city = max(
        (city for city in city_summary if city_summary[city]["salary_max_median"] is not None),
        key=lambda city: city_summary[city]["salary_max_median"],
        default=None,
    )

    return {
        "overall": {
            "total_jobs": len(normalized),
            "city_count": len(city_summary),
            **_salary_summary(normalized),
        },
        "skills": [{"name": name, "job_count": count} for name, count in skills.most_common()],
        "titles": [{"name": name, "job_count": count} for name, count in titles.most_common()],
        "cities": city_summary,
        "insights": {
            "most_demanded_skill": top_skill,
            "largest_job_market": top_city,
            "highest_median_salary_city": best_paid_city,
        },
    }

