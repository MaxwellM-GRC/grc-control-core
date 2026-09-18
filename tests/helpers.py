from __future__ import annotations

from datetime import date, datetime, timezone

from grc_control_core import (
    ControlMetadata,
    ControlRule,
    EvidenceReference,
    Finding,
    ResponseGuidance,
    Severity,
    SourceProvenance,
    stable_finding_id,
)

NOW = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)


def response() -> ResponseGuidance:
    return ResponseGuidance(
        remediation="Correct the confirmed condition after authorized review.",
        mitigation="Review the exposure period and affected activity.",
        root_cause="Determine why the preventive or detective path failed.",
        closure_evidence="Retain before/after evidence and accountable approval.",
        escalation="Escalate critical exposure immediately.",
    )


def control() -> ControlMetadata:
    return ControlMetadata(
        control_id="ITGC-XX-001",
        name="Example Population Review",
        risk_category="logical_access",
        risk="Failure to review the complete population could permit an error that affects financial reporting.",
        control_description="Management performs a daily reconciliation of the authoritative population to evaluated records and investigates exceptions.",
        objective="The complete population is evaluated against approved criteria.",
        population="All records in scope during the review period.",
        evidence="Source provenance, reconciliation, results, and closure evidence.",
        exception_response=response(),
        rules=(ControlRule("XX-01", "Every record meets the approved criterion.", Severity.HIGH),),
        catalog_version="1.0.0",
    )


def provenance(*, digest: str = "0" * 64, count: int = 2) -> SourceProvenance:
    return SourceProvenance(
        source_id="authoritative-records",
        source_uri="evidence://example/records",
        query="Export all records in scope during the review period.",
        extracted_at=NOW,
        review_period_start=date(2026, 9, 1),
        review_period_end=date(2026, 9, 17),
        record_count=count,
        content_sha256=digest,
        collected_by="collector@example.test",
    )


def finding() -> Finding:
    finding_id = stable_finding_id("ITGC-XX-001", "XX-01", "subject-1")
    return Finding(
        finding_id=finding_id,
        control_id="ITGC-XX-001",
        rule_id="XX-01",
        subject_key="subject-1",
        severity=Severity.HIGH,
        title="Approved criterion not met",
        criteria="Every record meets the approved criterion.",
        condition="The observed record does not meet the approved criterion.",
        cause="The source process did not enforce the criterion.",
        effect="The exception could affect financial reporting reliability.",
        observed_at=NOW,
        evidence=(EvidenceReference("authoritative-records", "record-1", "row:1"),),
        response=response(),
    )
