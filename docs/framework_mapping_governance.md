# Framework Mapping Governance

## Optional production extension

The lean portfolio standard keeps mappings in `docs/poc_product_profile.md`.
When a real implementation needs machine-readable exchange with a GRC platform
or other system, add one canonical `framework_mapping.json`, created from
`templates/framework_mapping.json` and validated against the bundled
`framework-mapping-v1.schema.json`.

The mapping is an alignment claim, not a certification of compliance. It must
state the framework reference, why the reference applies, the POC assertions
and evidence that support the claim, and the company-specific validation still
required before reliance.

## Aligned surfaces when JSON is adopted

| Surface | Purpose | Source of truth rule |
|---|---|---|
| `docs/poc_product_profile.md` | Fast value and pilot decision | Include the mapping ID and concise summary from the canonical record. |
| `framework_mapping.json` | Canonical, structured mapping | Owns framework references, applicability, assertion IDs, evidence outputs, status, and remaining validation. |
| `docs/rcm_and_control_narrative.md` and `docs/evidence_contract.md` | Detailed control and evidence review | Reference mapping IDs and expand only the implementation details supported by the canonical record. |

Do not independently author framework claims across these surfaces. Update the
canonical record first, then refresh the profile and detailed documents.

## Release check when JSON is adopted

Each POC adds a framework-mapping test that:

1. validates `framework_mapping.json` against the bundled schema;
2. confirms every mapping ID appears in the product profile, RCM narrative, and
   evidence contract;
3. confirms every mapped assertion ID exists in the POC's rule configuration;
4. confirms every named evidence output is produced or explicitly documented as
   a production-only output; and
5. fails when a mapping is `Approved` but retains unresolved mandatory
   validation for the claimed use.

The product owner approves product-fit decisions. The company control owner
approves company-specific control scope and reliance. Neither approval may be
inferred from a framework label alone.
