from __future__ import annotations

import unittest
from datetime import datetime

from grc_control_core import (
    ContractValidationError,
    ControlMetadata,
    ControlRule,
    EvaluationStatus,
    EvidencePackage,
    RISK_CATEGORIES,
    Severity,
    reconcile_population,
)

from tests.helpers import NOW, control, finding, provenance, response


class ControlLanguageContractTests(unittest.TestCase):
    def test_supported_taxonomy_matches_portfolio_contract(self) -> None:
        self.assertEqual(
            RISK_CATEGORIES,
            {
                "logical_access",
                "change_management",
                "it_operations",
                "security_configuration",
                "third_party_risk",
                "system_development",
            },
        )

    def test_valid_metadata_carries_catalog_and_schema_versions(self) -> None:
        item = control()
        self.assertEqual(item.catalog_version, "1.0.0")
        self.assertEqual(item.schema_version, "1.0.0")

    def test_unsupported_schema_major_is_rejected(self) -> None:
        values = control().__dict__ | {"schema_version": "2.0.0"}
        with self.assertRaisesRegex(ContractValidationError, "major must be 1"):
            ControlMetadata(**values)

    def test_risk_must_begin_failure_to(self) -> None:
        values = control().__dict__ | {"risk": "A weak process creates risk."}
        with self.assertRaisesRegex(ContractValidationError, "Failure to"):
            ControlMetadata(**values)

    def test_control_description_must_begin_management_performs(self) -> None:
        values = control().__dict__ | {"control_description": "The system performs a review."}
        with self.assertRaisesRegex(ContractValidationError, "Management performs"):
            ControlMetadata(**values)

    def test_control_and_rule_id_formats_accept_portfolio_variants(self) -> None:
        values = control().__dict__ | {
            "control_id": "ITGC-CM-01",
            "rules": (ControlRule("CM-01", "Every change is authorized.", Severity.CRITICAL),),
        }
        self.assertEqual(ControlMetadata(**values).control_id, "ITGC-CM-01")

    def test_unknown_risk_category_is_rejected(self) -> None:
        values = control().__dict__ | {"risk_category": "privacy"}
        with self.assertRaises(ContractValidationError):
            ControlMetadata(**values)

    def test_duplicate_rule_ids_are_rejected(self) -> None:
        duplicate = ControlRule("XX-01", "A second assertion.", Severity.HIGH)
        values = control().__dict__ | {"rules": control().rules + (duplicate,)}
        with self.assertRaisesRegex(ContractValidationError, "duplicate rule"):
            ControlMetadata(**values)

    def test_naive_observation_time_is_rejected(self) -> None:
        values = finding().__dict__ | {"observed_at": datetime(2026, 9, 17, 12, 0)}
        with self.assertRaisesRegex(ContractValidationError, "timezone information"):
            type(finding())(**values)


class FailClosedEvidenceTests(unittest.TestCase):
    def test_complete_evidence_requires_reconciled_population(self) -> None:
        population = reconcile_population(
            ["a", "b"], ["a"], authoritative_name="source", evaluated_name="results"
        )
        with self.assertRaisesRegex(ContractValidationError, "blocked"):
            EvidencePackage(
                run_id="run-1",
                generated_at=NOW,
                control=control(),
                sources=(provenance(),),
                population=population,
                findings=(),
                evaluation_status=EvaluationStatus.COMPLETE,
            )

    def test_blocked_evidence_cannot_report_control_findings(self) -> None:
        population = reconcile_population(
            ["a", "b"], ["a"], authoritative_name="source", evaluated_name="results"
        )
        with self.assertRaisesRegex(ContractValidationError, "must not report"):
            EvidencePackage(
                run_id="run-1",
                generated_at=NOW,
                control=control(),
                sources=(provenance(),),
                population=population,
                findings=(finding(),),
                evaluation_status=EvaluationStatus.BLOCKED,
                integrity_errors=("missing population member",),
            )

    def test_complete_evidence_requires_provenance(self) -> None:
        population = reconcile_population(
            ["a"], ["a"], authoritative_name="source", evaluated_name="results"
        )
        with self.assertRaisesRegex(ContractValidationError, "provenance"):
            EvidencePackage(
                run_id="run-1",
                generated_at=NOW,
                control=control(),
                sources=(),
                population=population,
                findings=(),
                evaluation_status=EvaluationStatus.COMPLETE,
            )

    def test_complete_package_accepts_contract_conforming_finding(self) -> None:
        package = EvidencePackage(
            run_id="run-1",
            generated_at=NOW,
            control=control(),
            sources=(provenance(),),
            population=reconcile_population(
                ["a"], ["a"], authoritative_name="source", evaluated_name="results"
            ),
            findings=(finding(),),
            evaluation_status=EvaluationStatus.COMPLETE,
        )
        self.assertEqual(package.findings[0].rule_id, "XX-01")

    def test_finding_evidence_must_reference_declared_source(self) -> None:
        item = finding()
        bad_reference = type(item.evidence[0])("unlisted-source", "record-1")
        item = type(item)(**(item.__dict__ | {"evidence": (bad_reference,)}))
        with self.assertRaisesRegex(ContractValidationError, "unknown evidence sources"):
            EvidencePackage(
                run_id="run-1",
                generated_at=NOW,
                control=control(),
                sources=(provenance(),),
                population=reconcile_population(
                    ["a"], ["a"], authoritative_name="source", evaluated_name="results"
                ),
                findings=(item,),
                evaluation_status=EvaluationStatus.COMPLETE,
            )

    def test_finding_ids_must_be_unique_within_a_package(self) -> None:
        with self.assertRaisesRegex(ContractValidationError, "duplicate finding IDs"):
            EvidencePackage(
                run_id="run-1",
                generated_at=NOW,
                control=control(),
                sources=(provenance(),),
                population=reconcile_population(
                    ["a"], ["a"], authoritative_name="source", evaluated_name="results"
                ),
                findings=(finding(), finding()),
                evaluation_status=EvaluationStatus.COMPLETE,
            )


if __name__ == "__main__":
    unittest.main()
