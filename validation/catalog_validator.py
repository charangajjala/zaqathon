"""Catalog-based order validation."""

from typing import Any

from core.interfaces import CatalogDataSource, OrderValidator
from core.models import OrderItem
from data_sources.catalog_csv import CsvCatalogDataSource

from .result import ValidationResult


class CatalogValidator(OrderValidator):
    """Validates orders against product catalog."""

    def __init__(self, catalog_source: CatalogDataSource):
        self.catalog_source = catalog_source

    @classmethod
    def from_csv(cls, catalog_path: str) -> "CatalogValidator":
        """Create validator from CSV file."""
        catalog_source = CsvCatalogDataSource(catalog_path)
        return cls(catalog_source)

    def validate_item(self, item: OrderItem) -> ValidationResult:
        """Validate order item against catalog."""
        product = self.catalog_source.get_product_details(item.sku)

        if not product:
            return self._handle_invalid_sku(item)

        if item.quantity < product["moq"]:
            return self._handle_moq_violation(item, product)

        if item.quantity > product["stock"]:
            return self._handle_stock_violation(item, product)

        return ValidationResult(
            is_valid=True,
            notes="Order item is valid",
            metadata={
                "min_quantity": product["moq"],
                "available_stock": product["stock"],
            },
        )

    def _handle_invalid_sku(self, item: OrderItem) -> ValidationResult:
        """Handle case when SKU is not found."""
        similar_products = self.catalog_source.find_similar_products(item.sku)
        return ValidationResult(
            is_valid=False,
            notes=f"SKU {item.sku} not found in catalog",
            suggestions=similar_products,
        )

    def _handle_moq_violation(
        self, item: OrderItem, product: dict[str, Any]
    ) -> ValidationResult:
        """Handle minimum order quantity violation."""
        return ValidationResult(
            is_valid=False,
            notes=f"Quantity {item.quantity} is below minimum order quantity of {product['moq']}",
            suggestions=[
                {
                    "type": "quantity_adjustment",
                    "current_quantity": item.quantity,
                    "suggested_quantity": product["moq"],
                    "reason": f"To meet minimum order quantity of {product['moq']}",
                }
            ],
            metadata={"min_quantity": product["moq"]},
        )

    def _handle_stock_violation(
        self, item: OrderItem, product: dict[str, Any]
    ) -> ValidationResult:
        """Handle stock availability violation."""
        return ValidationResult(
            is_valid=False,
            notes=f"Requested quantity {item.quantity} exceeds available stock of {product['stock']}",
            suggestions=[
                {
                    "type": "stock_limit",
                    "current_quantity": item.quantity,
                    "available_quantity": product["stock"],
                    "reason": "Limited by current stock levels",
                }
            ],
            metadata={"available_stock": product["stock"]},
        )
