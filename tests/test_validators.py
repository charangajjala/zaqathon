"""Tests for order validators."""

import pandas as pd
import pytest
from models import OrderItem
from validators import CatalogValidator

from .test_data import SAMPLE_CATALOG


@pytest.fixture
def catalog_validator(tmp_path):
    """Create a temporary catalog file and validator."""
    # Create temporary catalog file
    catalog_file = tmp_path / "test_catalog.csv"
    pd.DataFrame(SAMPLE_CATALOG).to_csv(catalog_file, index=False)

    # Create validator
    return CatalogValidator(str(catalog_file))


def test_validate_valid_item(catalog_validator):
    """Test validation of a valid order item."""
    item = OrderItem(sku="MD-001", quantity=2)
    result = catalog_validator.validate_item(item)

    assert result.is_valid
    assert result.notes == "Order item is valid"
    assert not result.suggestions
    assert result.metadata["min_quantity"] == 1
    assert result.metadata["available_stock"] == 10


def test_validate_invalid_sku(catalog_validator):
    """Test validation of item with invalid SKU."""
    item = OrderItem(sku="INVALID-SKU", quantity=1)
    result = catalog_validator.validate_item(item)

    assert not result.is_valid
    assert "not found in catalog" in result.notes
    assert result.suggestions
    assert len(result.suggestions) <= 3


def test_validate_below_moq(catalog_validator):
    """Test validation of item below minimum order quantity."""
    item = OrderItem(sku="BS-003", quantity=1)
    result = catalog_validator.validate_item(item)

    assert not result.is_valid
    assert "below minimum order quantity" in result.notes
    assert result.suggestions
    assert result.suggestions[0]["type"] == "quantity_adjustment"
    assert result.suggestions[0]["suggested_quantity"] == 2


def test_validate_above_stock(catalog_validator):
    """Test validation of item above available stock."""
    item = OrderItem(sku="DT-002", quantity=6)
    result = catalog_validator.validate_item(item)

    assert not result.is_valid
    assert "exceeds available stock" in result.notes
    assert result.suggestions
    assert result.suggestions[0]["type"] == "stock_limit"
    assert result.suggestions[0]["available_quantity"] == 5


def test_validate_out_of_stock(catalog_validator):
    """Test validation of out-of-stock item."""
    item = OrderItem(sku="CT-001", quantity=1)
    result = catalog_validator.validate_item(item)

    assert not result.is_valid
    assert "exceeds available stock" in result.notes
    assert result.suggestions
    assert result.suggestions[0]["available_quantity"] == 0


def test_find_similar_products(catalog_validator):
    """Test finding similar products."""
    similar = catalog_validator._find_similar_products("MD")
    assert len(similar) > 0
    assert any(p["sku"] == "MD-001" for p in similar)


def test_get_product_details(catalog_validator):
    """Test getting product details."""
    details = catalog_validator.get_product_details("MD-001")
    assert details
    assert details["name"] == "Modern Desk"
    assert details["stock"] == 10
    assert details["moq"] == 1
