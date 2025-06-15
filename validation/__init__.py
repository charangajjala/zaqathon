"""Validation module for order processing."""

from .catalog_validator import CatalogValidator
from .result import ValidationResult

__all__ = ["ValidationResult", "CatalogValidator"]
