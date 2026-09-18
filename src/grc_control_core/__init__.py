"""Reusable GRC control automation primitives that retain supporting evidence."""

from .config import (
    ConfiguredSource,
    PackageConfig,
    config_from_mapping,
    control_from_mapping,
    load_json_config,
    provenance_from_mapping,
)
from .errors import ContractValidationError, InputIntegrityError
from .exception_cases import (
    ExceptionCase,
    close_exception_case,
    open_exception_case,
    set_case_status,
)
from .ids import stable_finding_id
from .integrity import SourceSpec, require_integrity, sha256_file, validate_source
from .models import (
    SCHEMA_VERSION,
    RISK_CATEGORIES,
    ControlMetadata,
    ControlRule,
    EvaluationStatus,
    EvidencePackage,
    EvidenceReference,
    ExceptionStatus,
    Finding,
    IntegrityResult,
    PopulationReconciliation,
    ResponseGuidance,
    SourceProvenance,
    utc_now,
)
from .population import reconcile_population
from .render import render_case_markdown, render_findings_csv, render_json
from .schema import SCHEMAS, load_schema
from .severity import Severity, highest_severity, meets_threshold, severity_counts

__version__ = "0.1.0"

__all__ = [
    "SCHEMA_VERSION",
    "SCHEMAS",
    "RISK_CATEGORIES",
    "ConfiguredSource",
    "ContractValidationError",
    "ControlMetadata",
    "ControlRule",
    "EvaluationStatus",
    "EvidencePackage",
    "EvidenceReference",
    "ExceptionCase",
    "ExceptionStatus",
    "Finding",
    "InputIntegrityError",
    "IntegrityResult",
    "PackageConfig",
    "PopulationReconciliation",
    "ResponseGuidance",
    "Severity",
    "SourceProvenance",
    "SourceSpec",
    "close_exception_case",
    "config_from_mapping",
    "control_from_mapping",
    "highest_severity",
    "load_json_config",
    "load_schema",
    "meets_threshold",
    "open_exception_case",
    "provenance_from_mapping",
    "reconcile_population",
    "render_case_markdown",
    "render_findings_csv",
    "render_json",
    "require_integrity",
    "set_case_status",
    "severity_counts",
    "sha256_file",
    "stable_finding_id",
    "utc_now",
    "validate_source",
]
