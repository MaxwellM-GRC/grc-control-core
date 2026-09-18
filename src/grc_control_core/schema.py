"""Access to bundled, versioned JSON Schemas."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

SCHEMAS = frozenset(
    {
        "control-metadata-v1.schema.json",
        "finding-v1.schema.json",
        "source-provenance-v1.schema.json",
        "evidence-package-v1.schema.json",
    }
)


def load_schema(name: str) -> dict[str, Any]:
    """Load one bundled JSON Schema by exact published name."""

    if name not in SCHEMAS:
        raise KeyError(f"unknown schema {name!r}")
    resource = files("grc_control_core.schemas").joinpath(name)
    return json.loads(resource.read_text(encoding="utf-8"))
