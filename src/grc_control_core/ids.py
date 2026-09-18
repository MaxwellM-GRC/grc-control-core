"""Deterministic identifiers for findings and runs."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

_TOKEN_RE = re.compile(r"[^A-Z0-9]+")


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=lambda item: repr(item))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_canonical(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def stable_finding_id(
    control_id: str,
    rule_id: str,
    subject_key: str,
    *,
    discriminator: Mapping[str, Any] | None = None,
    digest_length: int = 16,
) -> str:
    """Create a stable ID from durable finding identity fields.

    Volatile values such as run time, observed condition, and severity should not
    be supplied as discriminators. The default 64-bit digest keeps IDs compact
    while remaining deterministic across source ordering and Python versions.
    """

    if not (12 <= digest_length <= 64):
        raise ValueError("digest_length must be between 12 and 64")
    for name, value in (
        ("control_id", control_id),
        ("rule_id", rule_id),
        ("subject_key", subject_key),
    ):
        if not str(value).strip():
            raise ValueError(f"{name} must not be blank")
    payload = {
        "control_id": control_id.strip().upper(),
        "rule_id": rule_id.strip().upper(),
        "subject_key": subject_key.strip(),
        "discriminator": discriminator or {},
    }
    encoded = json.dumps(_canonical(payload), separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:digest_length].upper()
    prefix = _TOKEN_RE.sub("-", rule_id.strip().upper()).strip("-")
    return f"{prefix}-{digest}"
