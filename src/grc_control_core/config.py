"""Strict configuration parsing and contract validation."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .errors import ContractValidationError
from .integrity import SourceSpec
from .models import (
    ControlMetadata,
    ControlRule,
    ResponseGuidance,
    SourceProvenance,
    mapping_value,
)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractValidationError(f"{name} must be an object")
    return value


def _sequence(value: Any, name: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ContractValidationError(f"{name} must be an array")
    return value


def _datetime(value: Any, name: str) -> datetime:
    if not isinstance(value, str):
        raise ContractValidationError(f"{name} must be an ISO 8601 string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractValidationError(f"{name} must be a valid ISO 8601 datetime") from exc


def _date(value: Any, name: str) -> date:
    if not isinstance(value, str):
        raise ContractValidationError(f"{name} must be an ISO 8601 date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ContractValidationError(f"{name} must be a valid ISO 8601 date") from exc


def response_from_mapping(value: Mapping[str, Any]) -> ResponseGuidance:
    value = _mapping(value, "exception_response")
    return ResponseGuidance(
        remediation=mapping_value(value, "remediation"),
        mitigation=mapping_value(value, "mitigation"),
        root_cause=mapping_value(value, "root_cause"),
        closure_evidence=mapping_value(value, "closure_evidence"),
        escalation=mapping_value(value, "escalation"),
    )


def control_from_mapping(value: Mapping[str, Any]) -> ControlMetadata:
    """Parse and validate raw control metadata."""

    value = _mapping(value, "control")
    rules = tuple(
        ControlRule(
            rule_id=mapping_value(_mapping(rule, "rule"), "rule_id"),
            assertion=mapping_value(_mapping(rule, "rule"), "assertion"),
            severity=mapping_value(_mapping(rule, "rule"), "severity"),
        )
        for rule in _sequence(mapping_value(value, "rules"), "rules")
    )
    return ControlMetadata(
        schema_version=value.get("schema_version", "1.0.0"),
        catalog_version=mapping_value(value, "catalog_version"),
        control_id=mapping_value(value, "control_id"),
        name=mapping_value(value, "name"),
        risk_category=mapping_value(value, "risk_category"),
        risk=mapping_value(value, "risk"),
        control_description=mapping_value(value, "control_description"),
        objective=mapping_value(value, "objective"),
        population=mapping_value(value, "population"),
        evidence=mapping_value(value, "evidence"),
        exception_response=response_from_mapping(mapping_value(value, "exception_response")),
        rules=rules,
    )


def provenance_from_mapping(value: Mapping[str, Any]) -> SourceProvenance:
    """Parse and validate raw source provenance metadata."""

    value = _mapping(value, "provenance")
    return SourceProvenance(
        schema_version=value.get("schema_version", "1.0.0"),
        source_id=mapping_value(value, "source_id"),
        source_uri=mapping_value(value, "source_uri"),
        query=mapping_value(value, "query"),
        extracted_at=_datetime(mapping_value(value, "extracted_at"), "extracted_at"),
        review_period_start=_date(
            mapping_value(value, "review_period_start"), "review_period_start"
        ),
        review_period_end=_date(mapping_value(value, "review_period_end"), "review_period_end"),
        record_count=mapping_value(value, "record_count"),
        content_sha256=mapping_value(value, "content_sha256"),
        collected_by=mapping_value(value, "collected_by"),
    )


@dataclass(frozen=True)
class ConfiguredSource:
    path: Path
    spec: SourceSpec

    def __post_init__(self) -> None:
        if not str(self.path).strip():
            raise ContractValidationError("source path must not be blank")


@dataclass(frozen=True)
class PackageConfig:
    control: ControlMetadata
    sources: tuple[ConfiguredSource, ...]

    def __post_init__(self) -> None:
        if not self.sources:
            raise ContractValidationError("configuration must declare at least one source")
        source_ids = [item.spec.provenance.source_id for item in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ContractValidationError("configuration contains duplicate source IDs")


def config_from_mapping(value: Mapping[str, Any], *, base_path: str | Path = ".") -> PackageConfig:
    """Validate a decoded JSON/YAML mapping into a typed configuration."""

    value = _mapping(value, "configuration")
    root = Path(base_path)
    sources: list[ConfiguredSource] = []
    for raw_source in _sequence(mapping_value(value, "sources"), "sources"):
        source = _mapping(raw_source, "source")
        spec = SourceSpec(
            provenance=provenance_from_mapping(mapping_value(source, "provenance")),
            required_fields=tuple(
                _sequence(mapping_value(source, "required_fields"), "required_fields")
            ),
            primary_key_fields=tuple(
                _sequence(mapping_value(source, "primary_key_fields"), "primary_key_fields")
            ),
            format=mapping_value(source, "format"),
            json_records_key=source.get("json_records_key"),
        )
        sources.append(
            ConfiguredSource(path=root / str(mapping_value(source, "path")), spec=spec)
        )
    return PackageConfig(
        control=control_from_mapping(mapping_value(value, "control")),
        sources=tuple(sources),
    )


def load_json_config(path: str | Path) -> PackageConfig:
    """Load a JSON config; YAML users can decode then call ``config_from_mapping``."""

    config_path = Path(path)
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractValidationError(f"configuration could not be loaded: {exc}") from exc
    return config_from_mapping(raw, base_path=config_path.parent)
