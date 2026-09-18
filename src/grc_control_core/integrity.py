"""Integrity checks for CSV and JSON file evidence that fail closed."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ContractValidationError, InputIntegrityError
from .models import IntegrityResult, SourceProvenance


@dataclass(frozen=True)
class SourceSpec:
    provenance: SourceProvenance
    required_fields: tuple[str, ...]
    primary_key_fields: tuple[str, ...]
    format: str
    json_records_key: str | None = None

    def __post_init__(self) -> None:
        fmt = self.format.strip().lower()
        if fmt not in {"csv", "json"}:
            raise ContractValidationError("source format must be csv or json")
        object.__setattr__(self, "format", fmt)
        if any(not isinstance(field, str) for field in self.required_fields):
            raise ContractValidationError("required_fields must contain only strings")
        if any(not isinstance(field, str) for field in self.primary_key_fields):
            raise ContractValidationError("primary_key_fields must contain only strings")
        required = tuple(field.strip() for field in self.required_fields)
        primary = tuple(field.strip() for field in self.primary_key_fields)
        if not required or any(not field for field in required):
            raise ContractValidationError("required_fields must contain fields that are not blank")
        if not primary or any(not field for field in primary):
            raise ContractValidationError("primary_key_fields must contain fields that are not blank")
        unknown = sorted(set(primary) - set(required))
        if unknown:
            raise ContractValidationError(
                f"primary key fields must also be required: {', '.join(unknown)}"
            )
        object.__setattr__(self, "required_fields", required)
        object.__setattr__(self, "primary_key_fields", primary)
        if self.json_records_key is not None:
            if not isinstance(self.json_records_key, str) or not self.json_records_key.strip():
                raise ContractValidationError("json_records_key must be a string that is not blank")
            object.__setattr__(self, "json_records_key", self.json_records_key.strip())


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 digest of a file's exact bytes."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_csv(path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise InputIntegrityError("CSV has no header row")
        records = [dict(row) for row in reader]
        return records, set(reader.fieldnames)


def _load_json(path: Path, records_key: str | None) -> tuple[list[dict[str, Any]], set[str]]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if records_key is not None:
        if not isinstance(value, dict) or records_key not in value:
            raise InputIntegrityError(f"JSON object is missing records key {records_key!r}")
        value = value[records_key]
    if not isinstance(value, list):
        raise InputIntegrityError("JSON evidence must be an array of records")
    if any(not isinstance(record, dict) for record in value):
        raise InputIntegrityError("every JSON evidence record must be an object")
    records = list(value)
    fields = set().union(*(record.keys() for record in records)) if records else set()
    return records, fields


def validate_source(path: str | Path, spec: SourceSpec) -> IntegrityResult:
    """Validate one source without raising, returning all detected errors."""

    source_path = Path(path)
    errors: list[str] = []
    if not source_path.is_file():
        return IntegrityResult(
            source_id=spec.provenance.source_id,
            valid=False,
            record_count=None,
            content_sha256=None,
            errors=(f"source file does not exist: {source_path}",),
        )
    try:
        digest = sha256_file(source_path)
    except OSError as exc:
        return IntegrityResult(
            source_id=spec.provenance.source_id,
            valid=False,
            record_count=None,
            content_sha256=None,
            errors=(f"source file could not be read: {exc}",),
        )
    if digest != spec.provenance.content_sha256:
        errors.append("content SHA-256 does not match retained provenance")
    try:
        if spec.format == "csv":
            records, fields = _load_csv(source_path)
        else:
            records, fields = _load_json(source_path, spec.json_records_key)
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, InputIntegrityError) as exc:
        errors.append(f"source could not be parsed: {exc}")
        return IntegrityResult(
            source_id=spec.provenance.source_id,
            valid=False,
            record_count=None,
            content_sha256=digest,
            errors=tuple(errors),
        )
    missing_fields = sorted(set(spec.required_fields) - fields)
    if missing_fields:
        errors.append(f"missing required fields: {', '.join(missing_fields)}")
    if len(records) != spec.provenance.record_count:
        errors.append(
            f"record count {len(records)} does not match retained count "
            f"{spec.provenance.record_count}"
        )
    if not missing_fields:
        seen: set[tuple[str, ...]] = set()
        duplicates: set[tuple[str, ...]] = set()
        for row_number, record in enumerate(records, start=1):
            missing_values = [
                field for field in spec.required_fields if record.get(field) is None or str(record[field]).strip() == ""
            ]
            if missing_values:
                errors.append(
                    f"record {row_number} has blank required fields: {', '.join(missing_values)}"
                )
                continue
            key = tuple(str(record[field]).strip() for field in spec.primary_key_fields)
            if key in seen:
                duplicates.add(key)
            seen.add(key)
        if duplicates:
            rendered = ", ".join("/".join(key) for key in sorted(duplicates))
            errors.append(f"duplicate primary keys: {rendered}")
    return IntegrityResult(
        source_id=spec.provenance.source_id,
        valid=not errors,
        record_count=len(records),
        content_sha256=digest,
        errors=tuple(errors),
    )


def require_integrity(results: list[IntegrityResult] | tuple[IntegrityResult, ...]) -> None:
    """Raise once with errors identified by source unless every source is valid."""

    errors = [
        f"{result.source_id}: {error}"
        for result in results
        for error in result.errors
    ]
    if errors:
        raise InputIntegrityError(errors)
