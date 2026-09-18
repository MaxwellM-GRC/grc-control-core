from __future__ import annotations

import unittest

from grc_control_core import (
    ContractValidationError,
    Severity,
    highest_severity,
    meets_threshold,
    reconcile_population,
    severity_counts,
    stable_finding_id,
)


class StableFindingIdTests(unittest.TestCase):
    def test_same_identity_is_stable(self) -> None:
        first = stable_finding_id(
            "ITGC-XX-001", "XX-01", "record-1", discriminator={"b": 2, "a": 1}
        )
        second = stable_finding_id(
            "itgc-xx-001", "xx-01", "record-1", discriminator={"a": 1, "b": 2}
        )
        self.assertEqual(first, second)
        self.assertRegex(first, r"^XX-01-[A-F0-9]{16}$")

    def test_changed_subject_changes_id(self) -> None:
        self.assertNotEqual(
            stable_finding_id("ITGC-XX-001", "XX-01", "record-1"),
            stable_finding_id("ITGC-XX-001", "XX-01", "record-2"),
        )

    def test_unordered_discriminator_set_is_stable(self) -> None:
        self.assertEqual(
            stable_finding_id(
                "ITGC-XX-001", "XX-01", "record-1", discriminator={"roles": {"b", "a"}}
            ),
            stable_finding_id(
                "ITGC-XX-001", "XX-01", "record-1", discriminator={"roles": {"a", "b"}}
            ),
        )

    def test_invalid_digest_length_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            stable_finding_id("ITGC-XX-001", "XX-01", "record-1", digest_length=8)


class PopulationTests(unittest.TestCase):
    def test_exact_population_reconciles(self) -> None:
        result = reconcile_population(
            ["a", "b"], ["b", "a"], authoritative_name="source", evaluated_name="results"
        )
        self.assertTrue(result.reconciled)

    def test_missing_unexpected_and_duplicates_are_visible(self) -> None:
        result = reconcile_population(
            ["a", "a", "b"],
            ["a", "c", "c"],
            authoritative_name="source",
            evaluated_name="results",
        )
        self.assertFalse(result.reconciled)
        self.assertEqual(result.missing_keys, ("b",))
        self.assertEqual(result.unexpected_keys, ("c",))
        self.assertEqual(result.duplicate_authoritative_keys, ("a",))
        self.assertEqual(result.duplicate_evaluated_keys, ("c",))

    def test_blank_key_is_rejected(self) -> None:
        with self.assertRaises(ContractValidationError):
            reconcile_population(
                ["a", " "], ["a"], authoritative_name="source", evaluated_name="results"
            )


class SeverityTests(unittest.TestCase):
    def test_threshold_is_inclusive(self) -> None:
        self.assertTrue(meets_threshold("high", Severity.HIGH))
        self.assertTrue(meets_threshold(Severity.CRITICAL, "high"))
        self.assertFalse(meets_threshold("medium", "high"))

    def test_highest_and_counts(self) -> None:
        values = ["high", "critical", "high", "info"]
        self.assertEqual(highest_severity(values), Severity.CRITICAL)
        self.assertEqual(severity_counts(values), {"critical": 1, "high": 2, "info": 1})

    def test_empty_highest_is_none(self) -> None:
        self.assertIsNone(highest_severity([]))


if __name__ == "__main__":
    unittest.main()
