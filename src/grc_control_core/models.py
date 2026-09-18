"""Versioned public data models for control automation evidence."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Mapping

from .errors import ContractValidationError
from .severity import Severity

SCHEMA_VERSION = "1.0.0"
RISK_CATEGORIES = frozenset(
    {
        "logical_access",
        "change_management",
        "it_operations",
        "security_configuration",
        "third_party_risk",
        "system_development",
    }
)

_SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
_CONTROL_ID_RE = re.compile(r"^ITGC-[A-Z][A-Z0-9]*-\d{2,3}$")
_RULE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d{2}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _required(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{name} must be a string that is not blank")
    return value.strip()


def _version(name: str, value: str) -> str:
    value = _required(name, value)
    if not _SEMVER_RE.fullmatch(value):
        raise ContractValidationError(f"{name} must be a semantic version")
    return value


def _schema_version(value: str) -> str:
    value = _version("schema_version", value)
    if value.split(".", 1)[0] != SCHEMA_VERSION.split(".", 1)[0]:
        raise ContractValidationError(
            f"schema_version major must be {SCHEMA_VERSION.split('.', 1)[0]}"
        )
    return value


def _aware(name: str, value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ContractValidationError(f"{name} must be a datetime with timezone information")
    return value


class EvaluationStatus(str, Enum):
    COMPLETE = "complete"
    BLOCKED = "blocked"


class ExceptionStatus(str, Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    REMEDIATED_PENDING_VALIDATION = "remediated_pending_validation"
    CLOSED = "closed"


@dataclass(frozen=True)
class ResponseGuidance:
    remediation: str
    mitigation: str
    root_cause: str
    closure_evidence: str
    escalation: str

    def __post_init__(self) -> None:
        for name in (
            "remediation",
            "mitigation",
            "root_cause",
            "closure_evidence",
            "escalation",
        ):
            object.__setattr__(self, name, _required(name, getattr(self, name)))


@dataclass(frozen=True)
class ControlRule:
    rule_id: str
    assertion: str
    severity: Severity

    def __post_init__(self) -> None:
        rule_id = _required("rule_id", self.rule_id).upper()
        if not _RULE_ID_RE.fullmatch(rule_id):
            raise ContractValidationError("rule_id must use <DOMAIN>-<two digits>")
        object.__setattr__(self, "rule_id", rule_id)
        object.__setattr__(self, "assertion", _required("assertion", self.assertion))
        object.__setattr__(self, "severity", Severity.parse(self.severity))


@dataclass(frozen=True)
class ControlMetadata:
    control_id: str
    name: str
    risk_category: str
    risk: str
    control_description: str
    objective: str
    population: str
    evidence: str
    exception_response: ResponseGuidance
    rules: tuple[ControlRule, ...]
    catalog_version: str
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        control_id = _required("control_id", self.control_id).upper()
        if not _CONTROL_ID_RE.fullmatch(control_id):
            raise ContractValidationError("control_id must use ITGC-<DOMAIN>-<two or three digits>")
        object.__setattr__(self, "control_id", control_id)
        object.__setattr__(self, "schema_version", _schema_version(self.schema_version))
        object.__setattr__(self, "catalog_version", _version("catalog_version", self.catalog_version))
        for name in ("name", "objective", "population", "evidence"):
            object.__setattr__(self, name, _required(name, getattr(self, name)))
        category = _required("risk_category", self.risk_category)
        if category not in RISK_CATEGORIES:
            raise ContractValidationError(
                f"risk_category must be one of: {', '.join(sorted(RISK_CATEGORIES))}"
            )
        object.__setattr__(self, "risk_category", category)
        risk = _required("risk", self.risk)
        if not risk.startswith("Failure to "):
            raise ContractValidationError('risk must begin "Failure to "')
        object.__setattr__(self, "risk", risk)
        description = _required("control_description", self.control_description)
        if not description.startswith("Management performs "):
            raise ContractValidationError('control_description must begin "Management performs "')
        object.__setattr__(self, "control_description", description)
        rules = tuple(self.rules)
        if not rules:
            raise ContractValidationError("rules must contain at least one rule")
        duplicate_ids = sorted(
            {rule.rule_id for rule in rules if sum(item.rule_id == rule.rule_id for item in rules) > 1}
        )
        if duplicate_ids:
            raise ContractValidationError(f"duplicate rule IDs: {', '.join(duplicate_ids)}")
        object.__setattr__(self, "rules", rules)


@dataclass(frozen=True)
class SourceProvenance:
    source_id: str
    source_uri: str
    query: str
    extracted_at: datetime
    review_period_start: date
    review_period_end: date
    record_count: int
    content_sha256: str
    collected_by: str
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _schema_version(self.schema_version))
        for name in ("source_id", "source_uri", "query", "collected_by"):
            object.__setattr__(self, name, _required(name, getattr(self, name)))
        object.__setattr__(self, "extracted_at", _aware("extracted_at", self.extracted_at))
        if self.review_period_end < self.review_period_start:
            raise ContractValidationError("review_period_end must not precede review_period_start")
        if not isinstance(self.record_count, int) or isinstance(self.record_count, bool) or self.record_count < 0:
            raise ContractValidationError("record_count must be an integer that is zero or greater")
        digest = _required("content_sha256", self.content_sha256).lower()
        if not _SHA256_RE.fullmatch(digest):
            raise ContractValidationError("content_sha256 must be 64 lowercase hexadecimal characters")
        object.__setattr__(self, "content_sha256", digest)


@dataclass(frozen=True)
class EvidenceReference:
    source_id: str
    record_id: str
    locator: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _required("source_id", self.source_id))
        object.__setattr__(self, "record_id", _required("record_id", self.record_id))
        if self.locator is not None:
            object.__setattr__(self, "locator", _required("locator", self.locator))


@dataclass(frozen=True)
class Finding:
    finding_id: str
    control_id: str
    rule_id: str
    subject_key: str
    severity: Severity
    title: str
    criteria: str
    condition: str
    cause: str
    effect: str
    observed_at: datetime
    evidence: tuple[EvidenceReference, ...]
    response: ResponseGuidance
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _schema_version(self.schema_version))
        for name in (
            "finding_id",
            "subject_key",
            "title",
            "criteria",
            "condition",
            "cause",
            "effect",
        ):
            object.__setattr__(self, name, _required(name, getattr(self, name)))
        control_id = _required("control_id", self.control_id).upper()
        rule_id = _required("rule_id", self.rule_id).upper()
        if not _CONTROL_ID_RE.fullmatch(control_id):
            raise ContractValidationError("finding control_id is invalid")
        if not _RULE_ID_RE.fullmatch(rule_id):
            raise ContractValidationError("finding rule_id is invalid")
        object.__setattr__(self, "control_id", control_id)
        object.__setattr__(self, "rule_id", rule_id)
        object.__setattr__(self, "severity", Severity.parse(self.severity))
        object.__setattr__(self, "observed_at", _aware("observed_at", self.observed_at))
        evidence = tuple(self.evidence)
        if not evidence:
            raise ContractValidationError("finding evidence must contain at least one reference")
        object.__setattr__(self, "evidence", evidence)


@dataclass(frozen=True)
class PopulationReconciliation:
    authoritative_population: str
    evaluated_population: str
    authoritative_count: int
    evaluated_count: int
    missing_keys: tuple[str, ...] = ()
    unexpected_keys: tuple[str, ...] = ()
    duplicate_authoritative_keys: tuple[str, ...] = ()
    duplicate_evaluated_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("authoritative_population", "evaluated_population"):
            object.__setattr__(self, name, _required(name, getattr(self, name)))
        for name in ("authoritative_count", "evaluated_count"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ContractValidationError(f"{name} must be an integer that is zero or greater")
        for name in (
            "missing_keys",
            "unexpected_keys",
            "duplicate_authoritative_keys",
            "duplicate_evaluated_keys",
        ):
            object.__setattr__(self, name, tuple(sorted(set(getattr(self, name)))))

    @property
    def reconciled(self) -> bool:
        return (
            self.authoritative_count == self.evaluated_count
            and not self.missing_keys
            and not self.unexpected_keys
            and not self.duplicate_authoritative_keys
            and not self.duplicate_evaluated_keys
        )


@dataclass(frozen=True)
class IntegrityResult:
    source_id: str
    valid: bool
    record_count: int | None
    content_sha256: str | None
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _required("source_id", self.source_id))
        object.__setattr__(self, "errors", tuple(self.errors))
        if self.valid and self.errors:
            raise ContractValidationError("a valid integrity result cannot contain errors")
        if not self.valid and not self.errors:
            raise ContractValidationError("an invalid integrity result must explain its errors")


@dataclass(frozen=True)
class EvidencePackage:
    run_id: str
    generated_at: datetime
    control: ControlMetadata
    sources: tuple[SourceProvenance, ...]
    population: PopulationReconciliation
    findings: tuple[Finding, ...]
    evaluation_status: EvaluationStatus
    integrity_errors: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "run_id", _required("run_id", self.run_id))
        object.__setattr__(self, "generated_at", _aware("generated_at", self.generated_at))
        object.__setattr__(self, "schema_version", _schema_version(self.schema_version))
        object.__setattr__(self, "sources", tuple(self.sources))
        object.__setattr__(self, "findings", tuple(self.findings))
        object.__setattr__(self, "integrity_errors", tuple(self.integrity_errors))
        try:
            status = EvaluationStatus(self.evaluation_status)
        except ValueError as exc:
            raise ContractValidationError("evaluation_status must be complete or blocked") from exc
        object.__setattr__(self, "evaluation_status", status)
        if status is EvaluationStatus.COMPLETE:
            if self.integrity_errors:
                raise ContractValidationError("complete evidence cannot contain integrity errors")
            if not self.sources:
                raise ContractValidationError("complete evidence requires source provenance")
            if not self.population.reconciled:
                raise ContractValidationError("evaluation must be blocked when population is not reconciled")
            source_ids = [source.source_id for source in self.sources]
            if len(source_ids) != len(set(source_ids)):
                raise ContractValidationError("source provenance contains duplicate source IDs")
            rule_ids = {rule.rule_id for rule in self.control.rules}
            finding_ids = [finding.finding_id for finding in self.findings]
            if len(finding_ids) != len(set(finding_ids)):
                raise ContractValidationError("evidence package contains duplicate finding IDs")
            for finding in self.findings:
                if finding.control_id != self.control.control_id or finding.rule_id not in rule_ids:
                    raise ContractValidationError("finding is outside the evidence package control contract")
                unknown_sources = sorted(
                    {reference.source_id for reference in finding.evidence} - set(source_ids)
                )
                if unknown_sources:
                    raise ContractValidationError(
                        "finding references unknown evidence sources: " + ", ".join(unknown_sources)
                    )
        else:
            if not self.integrity_errors:
                raise ContractValidationError("blocked evidence must contain integrity_errors")
            if self.findings:
                raise ContractValidationError("blocked evidence must not report control findings")


def utc_now() -> datetime:
    """Return a UTC timestamp with timezone information."""

    return datetime.now(timezone.utc)


def mapping_value(mapping: Mapping[str, Any], key: str) -> Any:
    """Read a required mapping value with an error written for the contract."""

    try:
        return mapping[key]
    except KeyError as exc:
        raise ContractValidationError(f"missing required field: {key}") from exc
