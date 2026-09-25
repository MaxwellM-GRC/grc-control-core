# Lean POC Product Profile

## Locked design

Each POC maintains one concise product-governance artifact:

| Artifact | Purpose |
|---|---|
| `docs/poc_product_profile.md` | A five-minute review of value, scope, framework fit, operating model, material risks, proof plan, and decisions. |

The profile preserves the four-part reasoning model: product brief, framework
mapping, Requirements & Risk Profile, and decision log. These are sections, not
separate files. Do not create separate product-governance documents unless a
real implementation requires machine-readable exchange or materially greater
detail.

Existing RCM narratives and evidence contracts remain technical control
documentation. The optional JSON framework-mapping schema remains available
for production integrations, but a separate `framework_mapping.json` is not
required for a portfolio POC.

## Six structural adoption changes

Each POC:

1. pins `grc-control-core` to the approved `v0.3.0` release;
2. completes `docs/poc_product_profile.md` from the shared template;
3. includes concise, evidence-backed framework mappings with unique mapping IDs;
4. references those mapping IDs in the detailed RCM and evidence documentation;
5. records only material requirements, risks, assumptions, and decisions in the
   profile; and
6. adds a lightweight release test for configured rule coverage, evidence
   outputs, unique mapping IDs, cross-document references, the illustrative
   mapping disclaimer, and the human decision boundary.

These changes do not require control-detection logic to change. The profile
should normally contain 3–6 mappings, 5–8 material risks or assumptions, 2–4
success metrics, and 3–6 material decisions. Concision is a review principle,
not a page-count requirement.
