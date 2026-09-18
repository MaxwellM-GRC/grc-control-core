# Contributing

Create a branch, add focused tests with the change, and run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Changes to public dataclasses, serialized fields, validation behavior, or bundled
JSON Schemas are contract changes and must follow the compatibility policy in
[`docs/versioning.md`](docs/versioning.md).
