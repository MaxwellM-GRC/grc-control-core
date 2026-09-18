# grc-control-core

[![CI](https://github.com/MaxwellM-GRC/grc-control-core/actions/workflows/ci.yml/badge.svg)](https://github.com/MaxwellM-GRC/grc-control-core/actions/workflows/ci.yml)

Shared Python primitives that can be reused across the Automated GRC POC portfolio.
The package makes evidence contracts consistent without centralizing the rules,
adapters, or narratives that make each POC independent and understandable.

This repository is the distribution source. **The package is not published to
PyPI.** Portfolio repositories consume a reviewed GitHub release tag such as
`v0.1.0`.

## What belongs here

- versioned control metadata, finding, provenance, and evidence package models;
- CSV/JSON input integrity validation that fails closed;
- complete population reconciliation;
- deterministic finding IDs and severity helpers;
- an exception case lifecycle that requires human approval;
- deterministic JSON, CSV, and Markdown rendering;
- configuration and control-language validation; and
- bundled Draft 2020-12 JSON Schemas and contract conformance tests.

## What deliberately does not belong here

- detection rules that are specific to a control;
- cloud, SaaS, identity, ticketing, or GRC platform adapters;
- legal or regulatory interpretations;
- POC narratives, sample companies, or production evidence; and
- automated remediation, risk acceptance, or exception closure.

Those boundaries keep POCs independently reviewable and prevent a shared
library from becoming an opaque policy engine.

## Install from a pinned GitHub release

Add this exact line to a POC's `requirements.txt`:

```text
grc-control-core @ git+https://github.com/MaxwellM-GRC/grc-control-core.git@v0.1.0
```

Or add the same direct reference to `project.dependencies` in `pyproject.toml`:

```toml
dependencies = [
  "grc-control-core @ git+https://github.com/MaxwellM-GRC/grc-control-core.git@v0.1.0",
]
```

Never depend on `main`, an untagged branch, or an unreviewed commit. See the
[adoption guide](docs/adoption.md) for a staged POC migration and upgrade
checklist.

## Small example

```python
from grc_control_core import reconcile_population, stable_finding_id

population = reconcile_population(
    authoritative_keys=["record-1", "record-2"],
    evaluated_keys=["record-2", "record-1"],
    authoritative_name="source export",
    evaluated_name="rule results",
)

assert population.reconciled

finding_id = stable_finding_id(
    "ITGC-XX-001",
    "XX-01",
    "record-2",
    discriminator={"criterion": "approved-state"},
)
```

See [`examples/basic_usage.py`](examples/basic_usage.py) for a complete evidence
package that is not specific to a control.

## Behavior that fails closed

`validate_source` checks exact file bytes, retained row counts, required fields,
blank values, and duplicate primary keys. `reconcile_population` exposes missing,
unexpected, and duplicate keys. An `EvidencePackage` cannot use `complete` status
unless source provenance is present and the population reconciles; a `blocked`
package cannot report control findings. Incomplete input therefore cannot look
like a clean control result.

Automation may open and route an exception case. `close_exception_case` requires
a remediation record, mitigation/lookback, root cause, closure evidence, an
approver, an approval timestamp, and an explicit assertion of human approval.

## Supported contract

Release `v0.1.0` supports:

| Package | Schema family | Python | Portfolio catalog |
|---|---|---|---|
| `0.1.x` | `1.x` | 3.10–3.13 | `1.0.0` |

The implementation is governed by the portfolio's `docs/control_catalog.yaml`
and `docs/control_language_standard.md`; human facing prose follows
`docs/writing_style.md`. The enforced contract includes the six risk categories,
both required language prefixes, standard IDs, versioned provenance, complete
population evidence, and response and closure owned by people.
See [contract mapping](docs/contract-mapping.md) and
[versioning policy](docs/versioning.md).

## Development

The runtime has no third-party dependencies.

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q src tests
```

The public API is exported from `grc_control_core`. JSON Schema resources can be
loaded with `load_schema(...)` or consumed directly from
`src/grc_control_core/schemas/`.

## License

MIT
