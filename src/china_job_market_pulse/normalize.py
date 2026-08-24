from __future__ import annotations

import re
from datetime import date, datetime
from math import isfinite
from typing import Any


_WHITESPACE_RE = re.compile(r"\s+")

CITY_ALIASES = {
    "北京市": "北京",
    "北京": "北京",
    "上海市": "上海",
    "上海": "上海",
    "广州市": "广州",
    "广州": "广州",
    "深圳市": "深圳",
    "深圳": "深圳",
    "杭州市": "杭州",
    "杭州": "杭州",
    "成都市": "成都",
    "成都": "成都",
    "重庆市": "重庆",
    "重庆": "重庆",
    "武汉市": "武汉",
    "武汉": "武汉",
    "南京市": "南京",
    "南京": "南京",
    "西安市": "西安",
    "西安": "西安",
    "苏州市": "苏州",
    "苏州": "苏州",
}

EDUCATION_ALIASES = (
    ("博士", ("博士", "ph.d", "phd")),
    ("硕士", ("硕士", "研究生", "master")),
    ("本科", ("本科", "学士", "bachelor")),
    ("大专", ("大专", "专科", "高职", "associate")),
    ("高中及以下", ("高中", "中专", "中技", "职高", "初中")),
    ("不限", ("不限", "无学历要求")),
)


def clean_text(value: Any) -> str:
    """Convert a scalar to trimmed text and collapse repeated whitespace."""

    if value is None:
        return ""
    return _WHITESPACE_RE.sub(" ", str(value).replace("\u3000", " ")).strip()


def normalize_title(value: Any) -> str:
    return clean_text(value)


def normalize_company(value: Any) -> str:
    return clean_text(value)


def normalize_city(value: Any) -> str:
    city = clean_text(value)
    if city in CITY_ALIASES:
        return CITY_ALIASES[city]
    if city.endswith("市") and len(city) > 2:
        return city[:-1]
    return city


def normalize_skill(value: Any) -> str:
    return clean_text(value)


def split_skills(value: Any) -> tuple[str, ...]:
    """Split common Chinese and ASCII list separators deterministically."""

    if value is None:
        return ()
    text = str(value).replace("\u3000", " ")
    if not text.strip():
        return ()
    parts = text.replace("，", ",").replace("；", ";").replace("、", ",")
    parts = parts.replace("\n", ",").replace("\r", ",")
    for separator in ("/", "|", ";"):
        parts = parts.replace(separator, ",")
    return tuple(dict.fromkeys(normalize_skill(part) for part in parts.split(",") if normalize_skill(part)))


def normalize_education(value: Any) -> str | None:
    education = clean_text(value)
    if not education:
        return None
    lowered = education.casefold()
    for canonical, aliases in EDUCATION_ALIASES:
        if any(alias.casefold() in lowered for alias in aliases):
            return canonical
    return education


def normalize_date(value: Any) -> str | None:
    """Return an ISO date, accepting an ISO datetime as input."""

    text = clean_text(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return None


def parse_optional_number(value: Any) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, bool):
        raise ValueError("boolean is not a numeric value")
    text = clean_text(value).replace(",", "").replace("，", "")
    number = float(text)
    if not isfinite(number):
        raise ValueError("number must be finite")
    return number
