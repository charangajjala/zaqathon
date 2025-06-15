"""Custom exceptions for the order processing system."""


class OrderProcessingError(Exception):
    """Base exception for order processing errors."""

    pass


class ValidationError(OrderProcessingError):
    """Exception raised when order validation fails."""

    pass


class ParsingError(OrderProcessingError):
    """Exception raised when email parsing fails."""

    pass


class CatalogError(OrderProcessingError):
    """Exception raised when catalog operations fail."""

    pass


class LLMError(OrderProcessingError):
    """Exception raised when LLM operations fail."""

    pass
