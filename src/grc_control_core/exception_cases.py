"""Helpers for the exception case lifecycle owned by people."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from .errors import ContractValidationError
from .models import ExceptionStatus, Finding, _aware, _required


@dataclass(frozen=True)
class ExceptionCase:
    case_id: str
    finding: Finding
    status: ExceptionStatus
    owner: str
    response_due_at: datetime
    opened_at: datetime
    remediation: str | None = None
    mitigation: str | None = None
    root_cause: str | None = None
    closure_evidence: tuple[str, ...] = ()
    approved_by: str | None = None
    closed_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _required("case_id", self.case_id))
        object.__setattr__(self, "owner", _required("owner", self.owner))
        object.__setattr__(self, "response_due_at", _aware("response_due_at", self.response_due_at))
        object.__setattr__(self, "opened_at", _aware("opened_at", self.opened_at))
        object.__setattr__(self, "closure_evidence", tuple(self.closure_evidence))
        try:
            status = ExceptionStatus(self.status)
        except ValueError as exc:
            raise ContractValidationError("invalid exception case status") from exc
        object.__setattr__(self, "status", status)
        if status is ExceptionStatus.CLOSED:
            for name in ("remediation", "mitigation", "root_cause", "approved_by"):
                _required(name, getattr(self, name) or "")
            if not self.closure_evidence or any(not item.strip() for item in self.closure_evidence):
                raise ContractValidationError("closed cases require closure evidence that is not blank")
            if self.closed_at is None:
                raise ContractValidationError("closed cases require closed_at")
            _aware("closed_at", self.closed_at)
        elif self.closed_at is not None or self.approved_by is not None:
            raise ContractValidationError("only closed cases may have closure approval metadata")

    def is_overdue(self, as_of: datetime) -> bool:
        """Return whether the response target has elapsed for an open case."""

        as_of = _aware("as_of", as_of)
        return self.status is not ExceptionStatus.CLOSED and as_of > self.response_due_at


def open_exception_case(
    finding: Finding,
    *,
    owner: str,
    opened_at: datetime,
    response_due_at: datetime,
) -> ExceptionCase:
    """Open one case for one finding without making a disposition."""

    return ExceptionCase(
        case_id=finding.finding_id,
        finding=finding,
        status=ExceptionStatus.OPEN,
        owner=owner,
        response_due_at=response_due_at,
        opened_at=opened_at,
    )


def set_case_status(case: ExceptionCase, status: ExceptionStatus) -> ExceptionCase:
    """Advance a case through workflow states before closure."""

    target = ExceptionStatus(status)
    if target is ExceptionStatus.CLOSED:
        raise ContractValidationError("use close_exception_case for closure with human approval")
    allowed = {
        ExceptionStatus.OPEN: {ExceptionStatus.UNDER_REVIEW},
        ExceptionStatus.UNDER_REVIEW: {
            ExceptionStatus.OPEN,
            ExceptionStatus.REMEDIATED_PENDING_VALIDATION,
        },
        ExceptionStatus.REMEDIATED_PENDING_VALIDATION: {ExceptionStatus.UNDER_REVIEW},
        ExceptionStatus.CLOSED: set(),
    }
    if target not in allowed[case.status]:
        raise ContractValidationError(f"invalid case transition: {case.status.value} -> {target.value}")
    return replace(case, status=target)


def close_exception_case(
    case: ExceptionCase,
    *,
    remediation: str,
    mitigation: str,
    root_cause: str,
    closure_evidence: tuple[str, ...],
    approved_by: str,
    approved_at: datetime,
    human_approved: bool,
) -> ExceptionCase:
    """Close a validated case only with an explicit human approval assertion."""

    if case.status is not ExceptionStatus.REMEDIATED_PENDING_VALIDATION:
        raise ContractValidationError("case must be remediated_pending_validation before closure")
    if human_approved is not True:
        raise ContractValidationError("case closure requires explicit human approval")
    return replace(
        case,
        status=ExceptionStatus.CLOSED,
        remediation=remediation,
        mitigation=mitigation,
        root_cause=root_cause,
        closure_evidence=closure_evidence,
        approved_by=approved_by,
        closed_at=approved_at,
    )
