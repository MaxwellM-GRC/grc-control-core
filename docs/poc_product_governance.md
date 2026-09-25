# Lean POC Product Governance

## Locked design

Each POC maintains exactly four product-governance artifacts:

| Artifact | Purpose |
|---|---|
| `docs/product_brief.md` | One-page value, scope, framework-fit, operating-model, and proof decision. |
| `framework_mapping.json` | Canonical structured framework applicability and evidence mapping. |
| `docs/requirements_risk_profile.md` | Applicable requirements, risks, evidence, actions, owners, and decisions. |
| `docs/decision_log.md` | Material decisions using independent evidence and decision statuses. |

The product brief contains the company operating model and proof plan. Do not
create separate operating-model or pilot-plan documents unless the POC becomes
too complex to review efficiently in one page.

Existing RCM narratives and evidence contracts remain technical control
documentation; they do not count as additional product-governance artifacts.

## Six structural adoption changes

Each POC:

1. pins `grc-control-core` to the approved `v0.2.1` release;
2. completes `docs/product_brief.md` from the shared template;
3. completes the canonical `framework_mapping.json`;
4. references its mapping IDs in the product brief, RCM narrative, and evidence
   contract without independently authoring framework claims;
5. completes the Requirements & Risk Profile and decision log; and
6. adds a framework-mapping release test that validates schema conformance,
   configured assertion IDs, evidence outputs, and cross-document mapping-ID
   coverage.

These changes do not require control-detection logic to change. Any proposed
rule change is a separate decision and must be supported by control or framework
evidence.
