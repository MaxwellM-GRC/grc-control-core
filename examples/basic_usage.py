"""Construct a complete evidence package that is not specific to a control."""

from datetime import date, datetime, timezone

from grc_control_core import (
    ControlMetadata,
    ControlRule,
    EvaluationStatus,
    EvidencePackage,
    ResponseGuidance,
    Severity,
    SourceProvenance,
    reconcile_population,
    render_json,
)

now = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)
response = ResponseGuidance(
    remediation="Correct the confirmed condition after authorized review.",
    mitigation="Review the exposure period and affected activity.",
    root_cause="Determine why the control path failed.",
    closure_evidence="Retain correction and approval evidence.",
    escalation="Escalate critical exposure immediately.",
)
control = ControlMetadata(
    control_id="ITGC-XX-001",
    name="Example Population Review",
    risk_category="logical_access",
    risk="Failure to evaluate the complete population could allow an error to affect financial reporting.",
    control_description="Management performs a daily reconciliation of authoritative records to evaluated records and investigates exceptions.",
    objective="The complete population is evaluated against approved criteria.",
    population="All records in scope during the review period.",
    evidence="Provenance, population reconciliation, results, and closure evidence.",
    exception_response=response,
    rules=(ControlRule("XX-01", "Every record meets the approved criterion.", Severity.HIGH),),
    catalog_version="1.0.0",
)
source = SourceProvenance(
    source_id="authoritative-records",
    source_uri="evidence://example/records",
    query="Export all records in scope.",
    extracted_at=now,
    review_period_start=date(2026, 9, 1),
    review_period_end=date(2026, 9, 17),
    record_count=2,
    content_sha256="0" * 64,
    collected_by="collector@example.test",
)
population = reconcile_population(
    ["record-1", "record-2"],
    ["record-2", "record-1"],
    authoritative_name="authoritative records",
    evaluated_name="rule results",
)
package = EvidencePackage(
    run_id="example-run-001",
    generated_at=now,
    control=control,
    sources=(source,),
    population=population,
    findings=(),
    evaluation_status=EvaluationStatus.COMPLETE,
)

print(render_json(package), end="")
