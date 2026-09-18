"""Deterministic JSON, CSV, and Markdown rendering."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterable

from .exception_cases import ExceptionCase
from .models import Finding
from .serialization import to_primitive

CSV_FIELDS = (
    "finding_id",
    "control_id",
    "rule_id",
    "subject_key",
    "severity",
    "title",
    "criteria",
    "condition",
    "cause",
    "effect",
    "observed_at",
    "evidence",
    "remediation",
    "mitigation",
    "root_cause_guidance",
    "closure_evidence_guidance",
    "escalation",
)


def render_json(value: object, *, indent: int | None = 2) -> str:
    """Render stable UTF-8 JSON with sorted keys and a trailing newline."""

    separators = (",", ":") if indent is None else None
    return (
        json.dumps(
            to_primitive(value),
            indent=indent,
            sort_keys=True,
            ensure_ascii=False,
            separators=separators,
        )
        + "\n"
    )


def render_findings_csv(findings: Iterable[Finding]) -> str:
    """Render one stable RFC 4180 compatible row per finding."""

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for finding in sorted(findings, key=lambda item: item.finding_id):
        writer.writerow(
            {
                "finding_id": finding.finding_id,
                "control_id": finding.control_id,
                "rule_id": finding.rule_id,
                "subject_key": finding.subject_key,
                "severity": finding.severity.value,
                "title": finding.title,
                "criteria": finding.criteria,
                "condition": finding.condition,
                "cause": finding.cause,
                "effect": finding.effect,
                "observed_at": to_primitive(finding.observed_at),
                "evidence": json.dumps(
                    to_primitive(finding.evidence), sort_keys=True, separators=(",", ":")
                ),
                "remediation": finding.response.remediation,
                "mitigation": finding.response.mitigation,
                "root_cause_guidance": finding.response.root_cause,
                "closure_evidence_guidance": finding.response.closure_evidence,
                "escalation": finding.response.escalation,
            }
        )
    return output.getvalue()


def _md(value: object) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def render_case_markdown(case: ExceptionCase) -> str:
    """Render a response case owned by a person without implying a disposition."""

    finding = case.finding
    evidence = "\n".join(
        f"- `{_md(item.source_id)}` / `{_md(item.record_id)}`"
        + (f" — {_md(item.locator)}" if item.locator else "")
        for item in finding.evidence
    )
    closure = "\n".join(f"- {_md(item)}" for item in case.closure_evidence) or "- Pending"
    return f"""# Exception case {case.case_id}

| Field | Value |
|---|---|
| Control | `{_md(finding.control_id)}` |
| Rule | `{_md(finding.rule_id)}` |
| Severity | {_md(finding.severity.value)} |
| Subject | `{_md(finding.subject_key)}` |
| Owner | {_md(case.owner)} |
| Status | `{_md(case.status.value)}` |
| Response due | {_md(to_primitive(case.response_due_at))} |

## Condition

{finding.condition}

## Criteria, cause, and effect

- **Criteria:** {finding.criteria}
- **Cause:** {finding.cause}
- **Effect:** {finding.effect}

## Evidence references

{evidence}

## Human response requirements

- **Remediation:** {finding.response.remediation}
- **Mitigation/lookback:** {finding.response.mitigation}
- **Root cause:** {finding.response.root_cause}
- **Closure evidence:** {finding.response.closure_evidence}
- **Escalation:** {finding.response.escalation}

## Recorded closure evidence

{closure}

> Automation may detect and route this exception. An authorized human must
> approve its disposition and closure.
"""
