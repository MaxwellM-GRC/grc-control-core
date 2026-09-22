from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema.validators import validator_for

from grc_control_core import (
    ContractValidationError,
    SCHEMAS,
    config_from_mapping,
    load_json_config,
    load_schema,
    render_findings_csv,
    render_json,
)

from tests.helpers import control, finding, provenance


def raw_config() -> dict[str, object]:
    item = control()
    source = provenance()
    return {
        "control": {
            "schema_version": item.schema_version,
            "catalog_version": item.catalog_version,
            "control_id": item.control_id,
            "name": item.name,
            "risk_category": item.risk_category,
            "risk": item.risk,
            "control_description": item.control_description,
            "objective": item.objective,
            "population": item.population,
            "evidence": item.evidence,
            "exception_response": item.exception_response.__dict__,
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "assertion": rule.assertion,
                    "severity": rule.severity.value,
                }
                for rule in item.rules
            ],
        },
        "sources": [
            {
                "path": "data/records.csv",
                "format": "csv",
                "required_fields": ["id"],
                "primary_key_fields": ["id"],
                "provenance": {
                    "schema_version": source.schema_version,
                    "source_id": source.source_id,
                    "source_uri": source.source_uri,
                    "query": source.query,
                    "extracted_at": "2026-09-17T12:00:00Z",
                    "review_period_start": source.review_period_start.isoformat(),
                    "review_period_end": source.review_period_end.isoformat(),
                    "record_count": source.record_count,
                    "content_sha256": source.content_sha256,
                    "collected_by": source.collected_by,
                },
            }
        ],
    }


class ConfigurationTests(unittest.TestCase):
    def test_mapping_is_parsed_to_typed_config(self) -> None:
        config = config_from_mapping(raw_config(), base_path="/tmp/example")
        self.assertEqual(config.control.control_id, "ITGC-XX-001")
        self.assertEqual(config.sources[0].path, Path("/tmp/example/data/records.csv"))

    def test_duplicate_source_ids_are_rejected(self) -> None:
        raw = raw_config()
        raw["sources"] = list(raw["sources"]) * 2
        with self.assertRaisesRegex(ContractValidationError, "duplicate source"):
            config_from_mapping(raw)

    def test_primary_key_must_be_required(self) -> None:
        raw = raw_config()
        raw["sources"][0]["primary_key_fields"] = ["other"]
        with self.assertRaisesRegex(ContractValidationError, "also be required"):
            config_from_mapping(raw)

    def test_json_config_loads_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(raw_config()), encoding="utf-8")
            config = load_json_config(path)
            self.assertEqual(config.sources[0].path, Path(directory) / "data/records.csv")


class RenderingTests(unittest.TestCase):
    def test_json_is_sorted_and_utc_normalized(self) -> None:
        output = render_json(finding())
        parsed = json.loads(output)
        self.assertTrue(output.endswith("\n"))
        self.assertEqual(parsed["observed_at"], "2026-09-17T12:00:00Z")
        self.assertEqual(parsed["severity"], "high")

    def test_csv_has_stable_header_and_one_row(self) -> None:
        output = render_findings_csv([finding()])
        rows = list(csv.DictReader(io.StringIO(output)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["rule_id"], "XX-01")
        self.assertEqual(json.loads(rows[0]["evidence"])[0]["record_id"], "record-1")


class SchemaTests(unittest.TestCase):
    def test_all_published_schemas_are_valid_json_with_ids(self) -> None:
        self.assertEqual(len(SCHEMAS), 5)
        for name in SCHEMAS:
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertIn(name, schema["$id"])
            validator_for(schema).check_schema(schema)

    def test_unknown_schema_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            load_schema("missing.schema.json")


if __name__ == "__main__":
    unittest.main()
