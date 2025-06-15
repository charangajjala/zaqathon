"""CSV-based catalog data source implementation."""

from typing import Any, Optional

import pandas as pd

from core.exceptions import CatalogError
from core.interfaces import CatalogDataSource


class CsvCatalogDataSource(CatalogDataSource):
    """CSV file-based catalog data source."""

    def __init__(self, catalog_path: str):
        self.catalog_path = catalog_path
        self._catalog = self._load_catalog()
        self._sku_map = self._create_sku_map()

    def _load_catalog(self) -> pd.DataFrame:
        """Load catalog data from CSV file."""
        try:
            return pd.read_csv(self.catalog_path)
        except Exception as e:
            raise CatalogError(
                f"Failed to load catalog from {self.catalog_path}: {e}"
            ) from e

    def _create_sku_map(self) -> dict[str, dict[str, Any]]:
        """Create mapping of SKUs to product details."""
        sku_map = {}
        for _, row in self._catalog.iterrows():
            # Handle different column name formats
            product_code = row.get("Product Code") or row.get("Product_Code")
            product_name = row.get("Product Name") or row.get("Product_Name")
            stock = row.get("Available Stock") or row.get("Available_in_Stock")
            moq = row.get("Minimum Order Quantity") or row.get("Min_Order_Quantity")
            description = row.get("Description", "")

            if product_code:
                sku_map[product_code] = {
                    "name": product_name,
                    "stock": int(stock) if stock is not None else 0,
                    "moq": int(moq) if moq is not None else 1,
                    "description": description,
                }
        return sku_map

    def get_product_details(self, sku: str) -> Optional[dict[str, Any]]:
        """Get product details by SKU."""
        return self._sku_map.get(sku)

    def find_similar_products(self, sku: str) -> list[dict[str, Any]]:
        """Find similar products based on SKU pattern or product name."""
        if len(sku) < 2:
            return []

        suggestions = []
        sku_upper = sku.upper()

        for catalog_sku, details in self._sku_map.items():
            # Skip exact matches
            if catalog_sku == sku:
                continue

            # Match by SKU prefix (traditional approach)
            if catalog_sku.startswith(sku[:3]):
                suggestions.append(
                    {
                        "sku": catalog_sku,
                        "name": details["name"],
                        "moq": details["moq"],
                        "stock": details["stock"],
                    }
                )
            # Match by product name containing the search term
            elif details["name"] and sku_upper in details["name"].upper():
                suggestions.append(
                    {
                        "sku": catalog_sku,
                        "name": details["name"],
                        "moq": details["moq"],
                        "stock": details["stock"],
                    }
                )

        return suggestions[:5]  # Return top 5 suggestions

    def get_all_products(self) -> dict[str, dict[str, Any]]:
        """Get all products in the catalog."""
        return self._sku_map.copy()
