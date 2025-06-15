"""Core interfaces and protocols for the order processing system."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

from .models import Order, OrderItem

if TYPE_CHECKING:
    from validation.result import ValidationResult


class EmailParser(Protocol):
    """Protocol for email parsing implementations."""

    def parse_email(self, email_text: str) -> Order:
        """Parse email text and return structured Order object."""
        ...


class OrderValidator(Protocol):
    """Protocol for order validation implementations."""

    def validate_item(self, item: OrderItem) -> "ValidationResult":
        """Validate a single order item."""
        ...


class OrderProcessor(Protocol):
    """Protocol for order processing implementations."""

    def process_order(self, email_text: str) -> Order:
        """Process email text and return validated order."""
        ...


class CatalogDataSource(Protocol):
    """Protocol for catalog data source implementations."""

    def get_product_details(self, sku: str) -> dict:
        """Get product details by SKU."""
        ...

    def find_similar_products(self, sku: str) -> list[dict]:
        """Find similar products by SKU pattern."""
        ...


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def create_llm(self, **kwargs):
        """Create and return an LLM instance."""
        pass

    @abstractmethod
    def get_default_config(self) -> dict:
        """Get default configuration for this provider."""
        pass
