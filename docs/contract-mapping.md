# Governing contract mapping

The canonical contract remains in the Automated GRC portfolio:

- `docs/control_catalog.yaml`, catalog version `1.0.0`;
- `docs/control_language_standard.md`;
- `docs/writing_style.md` for human facing prose.

This package implements their shared mechanics without copying assertions that
are specific to a control into a shared policy engine.

| Governing requirement | Package enforcement |
|---|---|
| Control ID and rule ID conventions | `ControlMetadata` and `ControlRule` validation |
| Risk begins “Failure to” | `ControlMetadata.risk` validation and JSON Schema pattern |
| Description begins “Management performs” | `ControlMetadata.control_description` validation and JSON Schema pattern |
| Taxonomy with six categories | `RISK_CATEGORIES`, model validation, and JSON Schema enum |
| Versioned catalog and contracts | `catalog_version`, `schema_version`, Semantic Versioning policy |
| Source/query provenance and counts | `SourceProvenance` and `source-provenance-v1.schema.json` |
| Fail closed on integrity/completeness | `validate_source`, `require_integrity`, and `EvidencePackage` status invariants |
| Population reconciliation | `reconcile_population` with missing, unexpected, and duplicate keys |
| Findings and closure evidence | `Finding`, `EvidenceReference`, response guidance, and exception cases |
| Remediation and closure with human approval | explicit exception case state machine and closure requirements |
| Framework claims across product, control, and evidence documents | `framework-mapping-v1.schema.json` and `docs/framework_mapping_governance.md` |

## Intentional boundary

The catalog's named controls, rules, severities, regulatory context, and response
text that is specific to a control stay in each POC. This library validates those
values structurally but does not decide whether a source record passes a control.

Contract conformance tests in `tests/test_contract_conformance.py` exercise the
language standard, taxonomy, identifier forms, provenance requirement, and
population behavior that fails closed.
