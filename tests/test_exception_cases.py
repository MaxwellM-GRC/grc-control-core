from __future__ import annotations

import unittest
from datetime import timedelta

from grc_control_core import (
    ContractValidationError,
    ExceptionStatus,
    close_exception_case,
    open_exception_case,
    render_case_markdown,
    set_case_status,
)

from tests.helpers import NOW, finding


class ExceptionCaseTests(unittest.TestCase):
    def _case(self):
        return open_exception_case(
            finding(),
            owner="control-owner@example.test",
            opened_at=NOW,
            response_due_at=NOW + timedelta(days=3),
        )

    def test_case_opens_without_a_disposition(self) -> None:
        case = self._case()
        self.assertEqual(case.status, ExceptionStatus.OPEN)
        self.assertIsNone(case.remediation)
        self.assertFalse(case.is_overdue(NOW + timedelta(days=1)))
        self.assertTrue(case.is_overdue(NOW + timedelta(days=4)))

    def test_valid_preclosure_transitions(self) -> None:
        case = set_case_status(self._case(), ExceptionStatus.UNDER_REVIEW)
        case = set_case_status(case, ExceptionStatus.REMEDIATED_PENDING_VALIDATION)
        self.assertEqual(case.status, ExceptionStatus.REMEDIATED_PENDING_VALIDATION)

    def test_closure_requires_explicit_human_approval(self) -> None:
        case = set_case_status(self._case(), ExceptionStatus.UNDER_REVIEW)
        case = set_case_status(case, ExceptionStatus.REMEDIATED_PENDING_VALIDATION)
        with self.assertRaisesRegex(ContractValidationError, "human approval"):
            close_exception_case(
                case,
                remediation="Corrected the condition.",
                mitigation="Reviewed the exposure period.",
                root_cause="Corrected a workflow gap.",
                closure_evidence=("evidence://closure/1",),
                approved_by="approver@example.test",
                approved_at=NOW + timedelta(days=2),
                human_approved=False,
            )

    def test_closed_case_retains_response_and_approval(self) -> None:
        case = set_case_status(self._case(), ExceptionStatus.UNDER_REVIEW)
        case = set_case_status(case, ExceptionStatus.REMEDIATED_PENDING_VALIDATION)
        case = close_exception_case(
            case,
            remediation="Corrected the condition.",
            mitigation="Reviewed the exposure period.",
            root_cause="Corrected a workflow gap.",
            closure_evidence=("evidence://closure/1",),
            approved_by="approver@example.test",
            approved_at=NOW + timedelta(days=2),
            human_approved=True,
        )
        self.assertEqual(case.status, ExceptionStatus.CLOSED)
        self.assertEqual(case.approved_by, "approver@example.test")

    def test_markdown_states_human_boundary(self) -> None:
        output = render_case_markdown(self._case())
        self.assertIn("authorized human", output)
        self.assertIn("XX-01", output)
        self.assertIn("Pending", output)


if __name__ == "__main__":
    unittest.main()
