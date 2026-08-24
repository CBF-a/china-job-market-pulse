from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, median
from typing import Iterable

from .models import JobPosting, SCHEMA_VERSION


ROLE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "data_analytics",
        ("数据", "分析", "算法", "bi", "machine learning", "机器学习", "人工智能", "ai"),
    ),
    ("software_engineering", ("开发", "工程师", "程序员", "后端", "前端", "全栈", "软件", "java", "python")),
    ("finance", ("财务", "金融", "风险", "会计", "审计", "投资", "资金")),
    ("hr_recruiting", ("人力", "招聘", "hr", "人才", "组织发展")),
    ("product_operations", ("产品", "运营", "项目", "增长", "战略", "商业")),
)

EXPERIENCE_BUCKET_ORDER = ("unknown", "<1", "1-2", "3-4", "5+")


def _rounded(value: float | None, digits: int = 2) -> float | None:
    return round(value, digits) if value is not None else None


def _salary_values(jobs: Iterable[JobPosting], field: str) -> list[float]:
    return [value for job in jobs if (value := getattr(job, field)) is not None]


def _salary_summary(jobs: list[JobPosting]) -> dict[str, float | int | None]:
    minimums = _salary_values(jobs, "salary_min")
    maximums = _salary_values(jobs, "salary_max")
    salary_job_count = sum(job.salary_min is not None or job.salary_max is not None for job in jobs)
    complete_salary_count = sum(job.salary_min is not None and job.salary_max is not None for job in jobs)
    return {
        "salary_min_median": _rounded(median(minimums)) if minimums else None,
        "salary_max_median": _rounded(median(maximums)) if maximums else None,
        "salary_min_average": _rounded(mean(minimums)) if minimums else None,
        "salary_max_average": _rounded(mean(maximums)) if maximums else None,
        "salary_job_count": salary_job_count,
        "complete_salary_count": complete_salary_count,
        "salary_missing_rate": _rounded(1 - salary_job_count / len(jobs), 4) if jobs else None,
    }


def _ranked_counts(counter: Counter[str], labels: dict[str, str], total: int) -> list[dict[str, str | int | float]]:
    ranked = sorted(counter.items(), key=lambda item: (-item[1], labels.get(item[0], item[0]).casefold()))
    return [
        {
            "name": labels.get(name, name),
            "job_count": count,
            "job_share": _rounded(count / total, 4) if total else 0,
        }
        for name, count in ranked
    ]


def _normalized_counter(values: Iterable[str]) -> tuple[Counter[str], dict[str, str]]:
    counter: Counter[str] = Counter()
    labels: dict[str, str] = {}
    for value in values:
        key = value.casefold()
        counter[key] += 1
        labels.setdefault(key, value)
    return counter, labels


def _grouped_counts(values: Iterable[str], total: int, order: tuple[str, ...] | None = None) -> list[dict[str, str | int | float]]:
    counter, labels = _normalized_counter(values)
    result = _ranked_counts(counter, labels, total)
    if order is None:
        return result
    rank = {name.casefold(): index for index, name in enumerate(order)}
    return sorted(result, key=lambda item: (rank.get(str(item["name"]).casefold(), len(order)), str(item["name"])))


def experience_bucket(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value < 1:
        return "<1"
    if value < 3:
        return "1-2"
    if value < 5:
        return "3-4"
    return "5+"


def classify_role(title: str) -> str:
    lowered = title.casefold()
    for category, keywords in ROLE_KEYWORDS:
        if any(keyword.casefold() in lowered for keyword in keywords):
            return category
    return "other"


def _salary_group_summary(jobs: list[JobPosting]) -> dict:
    return {"job_count": len(jobs), **_salary_summary(jobs)}


def _city_summary(jobs: list[JobPosting]) -> dict[str, dict]:
    cities: dict[str, list[JobPosting]] = defaultdict(list)
    for job in jobs:
        cities[job.city].append(job)
    total = len(jobs)
    return {
        city: {
            **_salary_group_summary(city_jobs),
            "job_share": _rounded(len(city_jobs) / total, 4) if total else 0,
        }
        for city, city_jobs in sorted(cities.items(), key=lambda item: item[0].casefold())
    }


def _trend_summary(jobs: list[JobPosting]) -> list[dict]:
    grouped: dict[str, list[JobPosting]] = defaultdict(list)
    for job in jobs:
        if job.posted_date and len(job.posted_date) >= 7:
            grouped[job.posted_date[:7]].append(job)
    return [
        {"period": period, **_salary_group_summary(grouped[period])}
        for period in sorted(grouped)
    ]


def _top_city(city_summary: dict[str, dict]) -> str | None:
    if not city_summary:
        return None
    return sorted(city_summary, key=lambda city: (-city_summary[city]["job_count"], city.casefold()))[0]


def _best_paid_city(city_summary: dict[str, dict]) -> str | None:
    candidates = [
        city for city, values in city_summary.items() if values["salary_max_median"] is not None
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda city: (-float(city_summary[city]["salary_max_median"]), city.casefold()),
    )[0]


def analyze_jobs(jobs: Iterable[JobPosting]) -> dict:
    """Return deterministic, JSON-serializable market indicators."""

    normalized = list(jobs)
    if not normalized:
        raise ValueError("At least one job posting is required")

    skill_values = (skill for job in normalized for skill in job.skills)
    skill_counts, skill_labels = _normalized_counter(skill_values)
    title_counts, title_labels = _normalized_counter(job.title for job in normalized)
    city_summary = _city_summary(normalized)

    experience_values = [experience_bucket(job.experience_years_min) for job in normalized]
    education_values = [job.education_normalized or job.education or "unknown" for job in normalized]
    role_values = [classify_role(job.title) for job in normalized]

    experience_distribution = _grouped_counts(experience_values, len(normalized), EXPERIENCE_BUCKET_ORDER)
    education_distribution = _grouped_counts(education_values, len(normalized))
    role_distribution = _grouped_counts(role_values, len(normalized))

    top_skill = _ranked_counts(skill_counts, skill_labels, len(normalized))
    top_city = _top_city(city_summary)
    best_paid_city = _best_paid_city(city_summary)

    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_version": "0.3",
        "overall": {
            "total_jobs": len(normalized),
            "city_count": len(city_summary),
            **_salary_summary(normalized),
        },
        "skills": top_skill,
        "titles": _ranked_counts(title_counts, title_labels, len(normalized)),
        "cities": city_summary,
        "experience": experience_distribution,
        "education": education_distribution,
        "roles": role_distribution,
        "trends": _trend_summary(normalized),
        "insights": {
            "most_demanded_skill": top_skill[0]["name"] if top_skill else None,
            "largest_job_market": top_city,
            "highest_median_salary_city": best_paid_city,
        },
    }
