# Versioning and compatibility

## Package releases

`grc-control-core` follows Semantic Versioning:

- **Patch** (`0.1.0` to `0.1.1`): compatible defect, documentation, or internal
  implementation correction. No serialized field or validation contract change.
- **Minor** (`0.1.0` to `0.2.0`): public API addition that remains compatible with earlier releases. During
  `0.x`, adopters still review release notes before upgrading.
- **Major** (`1.x` to `2.x`): incompatible Python API, behavior, validation, or
  serialization change.

Every distribution release is an annotated `vX.Y.Z` Git tag plus a matching
GitHub Release. The version in `pyproject.toml`, `grc_control_core.__version__`,
the tag, and the release title must agree.

The project does not publish wheels or source distributions to PyPI. GitHub is
the authoritative source and release channel.

## Schema versions

Serialized contracts have their own Semantic Versioning family. Package `0.1.x`
implements schema `1.x`. A package may add a new schema family without removing
the old one in a compatible minor release. Removing or reinterpreting an existing
field requires a package major version and a new schema major version.

Bundled schema filenames retain their major family, for example
`finding-v1.schema.json`; the serialized `schema_version` identifies the exact
contract revision.

## Catalog compatibility

The package records a control's `catalog_version` but does not embed catalog
content. The compatibility table in the README states the catalog version used
for conformance. A catalog change requires this repository to assess whether the
taxonomy, identifiers, required fields, language rules, or response boundary
changed and to release an appropriate package version.

## Release checklist

1. Update code, schemas, tests, documentation, and `CHANGELOG.md` together.
2. Run the full test and compile commands from the README.
3. Verify package metadata and `__version__` match.
4. Commit the release, create an annotated `vX.Y.Z` tag, and push both.
5. Create GitHub Release `vX.Y.Z` from that tag with the matching changelog.
6. Upgrade POCs individually through reviewed pull requests; never retarget tags.
