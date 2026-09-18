"""Severity values and comparison helpers."""

from __future__ import annotations

from enum import Enum
from typing import Iterable


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        return _RANK[self]

    @classmethod
    def parse(cls, value: "Severity | str") -> "Severity":
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(item.value for item in cls)
            raise ValueError(f"unknown severity {value!r}; expected one of: {allowed}") from exc


_RANK = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


def meets_threshold(value: Severity | str, threshold: Severity | str) -> bool:
    """Return whether *value* is at least as severe as *threshold*."""

    return Severity.parse(value).rank >= Severity.parse(threshold).rank


def highest_severity(values: Iterable[Severity | str]) -> Severity | None:
    """Return the highest severity, or ``None`` for an empty iterable."""

    parsed = [Severity.parse(value) for value in values]
    return max(parsed, key=lambda value: value.rank, default=None)


def severity_counts(values: Iterable[Severity | str]) -> dict[str, int]:
    """Count severities in deterministic descending order."""

    counts = {severity.value: 0 for severity in reversed(list(Severity))}
    for value in values:
        counts[Severity.parse(value).value] += 1
    return {key: count for key, count in counts.items() if count}
