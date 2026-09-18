"""Complete population reconciliation helpers."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from .errors import ContractValidationError
from .models import PopulationReconciliation


def _keys(values: Iterable[object], name: str) -> list[str]:
    keys: list[str] = []
    for value in values:
        key = str(value).strip()
        if not key:
            raise ContractValidationError(f"{name} contains a blank population key")
        keys.append(key)
    return keys


def reconcile_population(
    authoritative_keys: Iterable[object],
    evaluated_keys: Iterable[object],
    *,
    authoritative_name: str,
    evaluated_name: str,
) -> PopulationReconciliation:
    """Reconcile evaluated keys to the authoritative denominator.

    Duplicate keys are retained as an integrity failure rather than silently
    collapsed. Missing and unexpected keys are reported in stable sort order.
    """

    authoritative = _keys(authoritative_keys, "authoritative_keys")
    evaluated = _keys(evaluated_keys, "evaluated_keys")
    authoritative_counts = Counter(authoritative)
    evaluated_counts = Counter(evaluated)
    authoritative_set = set(authoritative)
    evaluated_set = set(evaluated)
    return PopulationReconciliation(
        authoritative_population=authoritative_name,
        evaluated_population=evaluated_name,
        authoritative_count=len(authoritative),
        evaluated_count=len(evaluated),
        missing_keys=tuple(sorted(authoritative_set - evaluated_set)),
        unexpected_keys=tuple(sorted(evaluated_set - authoritative_set)),
        duplicate_authoritative_keys=tuple(
            sorted(key for key, count in authoritative_counts.items() if count > 1)
        ),
        duplicate_evaluated_keys=tuple(
            sorted(key for key, count in evaluated_counts.items() if count > 1)
        ),
    )
