from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from grc_control_core import (
    InputIntegrityError,
    SourceSpec,
    require_integrity,
    validate_source,
)

from tests.helpers import provenance


class InputIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def _digest(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def test_valid_csv_matches_schema_count_hash_and_key(self) -> None:
        content = b"id,status\n1,active\n2,disabled\n"
        path = self.root / "records.csv"
        path.write_bytes(content)
        spec = SourceSpec(
            provenance=provenance(digest=self._digest(content), count=2),
            required_fields=("id", "status"),
            primary_key_fields=("id",),
            format="csv",
        )
        result = validate_source(path, spec)
        self.assertTrue(result.valid)
        self.assertEqual(result.record_count, 2)

    def test_changed_content_fails_closed(self) -> None:
        content = b"id,status\n1,active\n"
        path = self.root / "records.csv"
        path.write_bytes(content)
        spec = SourceSpec(
            provenance=provenance(digest="f" * 64, count=1),
            required_fields=("id", "status"),
            primary_key_fields=("id",),
            format="csv",
        )
        result = validate_source(path, spec)
        self.assertFalse(result.valid)
        self.assertIn("SHA-256", " ".join(result.errors))

    def test_missing_fields_count_and_duplicate_keys_are_reported(self) -> None:
        content = b"id,status\n1,active\n1,\n"
        path = self.root / "records.csv"
        path.write_bytes(content)
        spec = SourceSpec(
            provenance=provenance(digest=self._digest(content), count=3),
            required_fields=("id", "status", "owner"),
            primary_key_fields=("id",),
            format="csv",
        )
        result = validate_source(path, spec)
        joined = " ".join(result.errors)
        self.assertIn("missing required fields: owner", joined)
        self.assertIn("record count", joined)

    def test_duplicate_json_primary_key_is_reported(self) -> None:
        content = json.dumps([{"id": "1"}, {"id": "1"}]).encode()
        path = self.root / "records.json"
        path.write_bytes(content)
        spec = SourceSpec(
            provenance=provenance(digest=self._digest(content), count=2),
            required_fields=("id",),
            primary_key_fields=("id",),
            format="json",
        )
        result = validate_source(path, spec)
        self.assertFalse(result.valid)
        self.assertIn("duplicate primary keys: 1", result.errors)

    def test_json_records_key_is_supported(self) -> None:
        content = json.dumps({"records": [{"id": "1"}, {"id": "2"}]}).encode()
        path = self.root / "records.json"
        path.write_bytes(content)
        spec = SourceSpec(
            provenance=provenance(digest=self._digest(content), count=2),
            required_fields=("id",),
            primary_key_fields=("id",),
            format="json",
            json_records_key="records",
        )
        self.assertTrue(validate_source(path, spec).valid)

    def test_missing_file_returns_invalid_result(self) -> None:
        spec = SourceSpec(
            provenance=provenance(),
            required_fields=("id",),
            primary_key_fields=("id",),
            format="csv",
        )
        result = validate_source(self.root / "missing.csv", spec)
        self.assertFalse(result.valid)
        with self.assertRaises(InputIntegrityError):
            require_integrity([result])


if __name__ == "__main__":
    unittest.main()
