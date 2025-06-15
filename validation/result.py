"""Validation result data class."""

from typing import Any


class ValidationResult:
    """Data class for validation results."""

    def __init__(
        self,
        is_valid: bool,
        notes: str,
        suggestions: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.is_valid = is_valid
        self.notes = notes
        self.suggestions = suggestions or []
        self.metadata = metadata or {}
