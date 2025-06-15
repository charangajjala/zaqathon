"""Tests for order processor."""

from unittest.mock import Mock

import pytest
from app import SmartOrderProcessor
from models import Order, OrderItem
from validators import ValidationResult

from .test_data import EXPECTED_ORDER_1, SAMPLE_EMAIL_1


@pytest.fixture
def mock_parser():
    """Create a mock email parser."""
    parser = Mock()
    parser.parse_email.return_value = Order(
        customer=EXPECTED_ORDER_1["customer"],
        address=EXPECTED_ORDER_1["address"],
        delivery_date=EXPECTED_ORDER_1["delivery_date"],
        items=[
            OrderItem(sku=item["sku"], quantity=item["quantity"])
            for item in EXPECTED_ORDER_1["items"]
        ],
    )
    return parser


@pytest.fixture
def mock_validator():
    """Create a mock order validator."""
    validator = Mock()

    def mock_validate(item):
        if item.sku == "MD-001":
            return ValidationResult(True, "Valid item")
        elif item.sku == "DT-002":
            return ValidationResult(True, "Valid item")
        else:
            return ValidationResult(
                False,
                "Invalid item",
                suggestions=[{"type": "quantity_adjustment", "suggested_quantity": 2}],
            )

    validator.validate_item.side_effect = mock_validate
    return validator


@pytest.fixture
def processor(mock_parser, mock_validator):
    """Create a processor with mocked dependencies."""
    return SmartOrderProcessor(mock_parser, mock_validator)


def test_process_order_basic(processor, mock_parser, mock_validator):
    """Test basic order processing."""
    order = processor.process_order(SAMPLE_EMAIL_1)

    # Verify parser was called
    mock_parser.parse_email.assert_called_once_with(SAMPLE_EMAIL_1)

    # Verify validator was called for each item
    assert mock_validator.validate_item.call_count == len(EXPECTED_ORDER_1["items"])

    # Verify order structure
    assert isinstance(order, Order)
    assert order.customer == EXPECTED_ORDER_1["customer"]
    assert order.address == EXPECTED_ORDER_1["address"]
    assert order.delivery_date == EXPECTED_ORDER_1["delivery_date"]
    assert len(order.items) == len(EXPECTED_ORDER_1["items"])


def test_process_order_validation(processor):
    """Test order validation results."""
    order = processor.process_order(SAMPLE_EMAIL_1)

    # Verify validation results
    for item in order.items:
        if item.sku in ["MD-001", "DT-002"]:
            assert item.valid
            assert item.notes == "Valid item"
            assert not item.suggestions
        else:
            assert not item.valid
            assert item.notes == "Invalid item"
            assert item.suggestions
            assert item.suggestions[0]["type"] == "quantity_adjustment"


def test_process_order_empty_email(processor):
    """Test processing empty email."""
    with pytest.raises((ValueError, RuntimeError)):
        processor.process_order("")


def test_process_order_parser_error(processor, mock_parser):
    """Test handling of parser errors."""
    mock_parser.parse_email.side_effect = Exception("Parser error")

    with pytest.raises(Exception) as exc_info:
        processor.process_order(SAMPLE_EMAIL_1)

    assert "Parser error" in str(exc_info.value)


def test_process_order_validator_error(processor, mock_validator):
    """Test handling of validator errors."""
    mock_validator.validate_item.side_effect = Exception("Validator error")

    with pytest.raises(Exception) as exc_info:
        processor.process_order(SAMPLE_EMAIL_1)

    assert "Validator error" in str(exc_info.value)
