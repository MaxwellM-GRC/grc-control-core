"""Stable conversion of package models to values that are safe for interchange."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


def to_primitive(value: Any) -> Any:
    """Convert dataclasses and supported standard types into JSON compatible values."""

    if is_dataclass(value) and not isinstance(value, type):
        result: dict[str, Any] = {}
        for item in fields(value):
            field_value = getattr(value, item.name)
            if item.name == "reconciled" or callable(field_value):
                continue
            result[item.name] = to_primitive(field_value)
        if value.__class__.__name__ == "PopulationReconciliation":
            result["reconciled"] = bool(value.reconciled)
        return result
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("cannot serialize a naive datetime")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): to_primitive(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted((to_primitive(item) for item in value), key=repr)
    if isinstance(value, (tuple, list)):
        return [to_primitive(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported value for serialization: {type(value).__name__}")
