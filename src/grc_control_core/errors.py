"""Package exceptions."""

from __future__ import annotations


class ContractValidationError(ValueError):
    """Raised when an object violates the public data contract."""

    def __init__(self, errors: str | list[str] | tuple[str, ...]) -> None:
        if isinstance(errors, str):
            errors = (errors,)
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


class InputIntegrityError(ContractValidationError):
    """Raised when input completeness or integrity cannot be established."""
