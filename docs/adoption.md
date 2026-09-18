# POC adoption and release pinning

Adopt the library independently in each POC. A flag day across the portfolio is not
required, and existing local logic should be removed only after parity is tested.

## 1. Pin a reviewed tag

Add this direct reference to the POC's `requirements.txt`:

```text
grc-control-core @ git+https://github.com/MaxwellM-GRC/grc-control-core.git@v0.1.0
```

For a POC with `pyproject.toml`, use:

```toml
[project]
dependencies = [
  "grc-control-core @ git+https://github.com/MaxwellM-GRC/grc-control-core.git@v0.1.0",
]
```

The tag is the clear compatibility pin. Record the resolved Git commit
in the POC's lock file or build evidence when its toolchain supports that, so a
review can perform the exact installation again.

## 2. Adopt primitives in a lower risk order

1. Replace local severity comparison and stable ID utilities.
2. Map existing control configuration to `ControlMetadata`; keep the control's
   assertions and severities in the POC.
3. Map source manifests to `SourceProvenance` and `SourceSpec`, then run integrity
   checks before any rule evaluation.
4. Reconcile the authoritative denominator to evaluated record keys.
5. Map local findings to `Finding` and render the existing JSON/CSV/case outputs.
6. Construct `EvidencePackage` last so its invariants make the full run fail closed.

Do not move adapters, rules, fixture data, narratives, or remediation actions into
this package during adoption.

## 3. Prove parity

For each POC, add tests that establish:

- the same authoritative record denominator and findings before and after adoption;
- unchanged finding IDs across repeated runs and input ordering;
- missing, changed, duplicate, or unreconciled input blocks evaluation;
- serialized output matches the bundled schema family; and
- exception disappearance does not automatically close a case owned by a person.

Run the POC's entire suite and sample control before merging its adoption PR.

## 4. Upgrade deliberately

Open one reviewed dependency PR per POC when moving to a newer release tag. Read
the changelog, confirm the compatibility table, run package contract tests plus
the POC's tests, inspect representative evidence diffs, and record approval. Do
not use floating branches, tag ranges, or automated major version upgrades.
