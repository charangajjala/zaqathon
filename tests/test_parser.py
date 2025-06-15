"""Tests for email parser."""

from datetime import date
from parser import EmailData, LangChainEmailParser
from unittest.mock import Mock, patch

import pytest
from models import Order, OrderItem

from .test_data import (
    EXPECTED_ORDER_1,
    EXPECTED_ORDER_2,
    SAMPLE_EMAIL_1,
    SAMPLE_EMAIL_2,
)


@pytest.fixture
def mock_llm_factory():
    """Create a mock LLM factory."""
    with patch("parser.LLMFactory") as mock_factory:
        # Mock the LLM instance
        mock_llm = Mock()
        mock_llm.invoke.return_value = """
        {
            "customer_name": "John Smith",
            "delivery_address": "123 Main Street\\nAnytown, USA 12345",
            "delivery_date": "2025-06-20",
            "items": [
                {"sku": "MD-001", "quantity": 2},
                {"sku": "DT-002", "quantity": 1},
                {"sku": "BS-003", "quantity": 3}
            ]
        }
        """

        # Mock the factory method
        mock_factory.create_llm.return_value = mock_llm
        yield mock_factory


@pytest.fixture
def mock_output_parser():
    """Create a mock output parser."""
    with patch("parser.PydanticOutputParser") as mock_parser_class:
        mock_parser = Mock()
        mock_parser.get_format_instructions.return_value = "Format instructions here"
        mock_parser.parse.return_value = EmailData(
            customer_name="John Smith",
            delivery_address="123 Main Street\nAnytown, USA 12345",
            delivery_date="2025-06-20",
            items=[
                {"sku": "MD-001", "quantity": 2},
                {"sku": "DT-002", "quantity": 1},
                {"sku": "BS-003", "quantity": 3},
            ],
        )
        mock_parser_class.return_value = mock_parser
        yield mock_parser


@pytest.fixture
def parser(mock_llm_factory, mock_output_parser):
    """Create a parser with mocked dependencies."""
    return LangChainEmailParser(llm_provider="openai")


def test_parser_initialization(mock_llm_factory):
    """Test parser initialization with different providers."""
    LangChainEmailParser(llm_provider="openai")
    mock_llm_factory.create_llm.assert_called_once_with(provider="openai")


def test_parser_initialization_with_config(mock_llm_factory):
    """Test parser initialization with custom config."""
    config = {"model": "gpt-4", "temperature": 0.5}
    LangChainEmailParser(llm_provider="openai", llm_config=config)
    mock_llm_factory.create_llm.assert_called_once_with(provider="openai", **config)


def test_parse_email_basic(parser):
    """Test basic email parsing with chain."""
    with (
        patch.object(parser, "prompt") as mock_prompt,
        patch.object(parser, "llm"),
        patch.object(parser, "output_parser"),
    ):
        # Mock the chain execution
        mock_chain = Mock()
        mock_chain.invoke.return_value = EmailData(
            customer_name="John Smith",
            delivery_address="123 Main Street\nAnytown, USA 12345",
            delivery_date="2025-06-20",
            items=[
                {"sku": "MD-001", "quantity": 2},
                {"sku": "DT-002", "quantity": 1},
                {"sku": "BS-003", "quantity": 3},
            ],
        )

        # Mock the chain creation (prompt | llm | parser)
        mock_prompt.__or__ = Mock(return_value=mock_chain)

        order = parser.parse_email(SAMPLE_EMAIL_1)

        assert isinstance(order, Order)
        assert order.customer == "John Smith"
        assert order.address == "123 Main Street\nAnytown, USA 12345"
        assert order.delivery_date == date(2025, 6, 20)
        assert len(order.items) == 3


def test_parse_email_items(parser):
    """Test parsing of order items."""
    with (
        patch.object(parser, "prompt") as mock_prompt,
        patch.object(parser, "llm"),
        patch.object(parser, "output_parser"),
    ):
        mock_chain = Mock()
        mock_chain.invoke.return_value = EmailData(
            customer_name="John Smith",
            delivery_address="123 Main Street\nAnytown, USA 12345",
            delivery_date="2025-06-20",
            items=[
                {"sku": "MD-001", "quantity": 2},
                {"sku": "DT-002", "quantity": 1},
                {"sku": "BS-003", "quantity": 3},
            ],
        )

        mock_prompt.__or__ = Mock(return_value=mock_chain)

        order = parser.parse_email(SAMPLE_EMAIL_1)

        for expected, actual in zip(EXPECTED_ORDER_1["items"], order.items):
            assert isinstance(actual, OrderItem)
            assert actual.sku == expected["sku"]
            assert actual.quantity == expected["quantity"]
            assert actual.valid is True  # Initial state before validation


def test_email_data_validation():
    """Test EmailData validation."""
    # Valid data
    valid_data = EmailData(
        customer_name="John Smith",
        delivery_address="123 Main St",
        delivery_date="2025-06-20",
        items=[{"sku": "MD-001", "quantity": 2}],
    )
    assert valid_data.customer_name == "John Smith"

    # Invalid date format
    with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
        EmailData(
            customer_name="John Smith",
            delivery_address="123 Main St",
            delivery_date="invalid-date",
            items=[{"sku": "MD-001", "quantity": 2}],
        )

    # Invalid items structure
    with pytest.raises(
        ValueError, match="Each item must have 'sku' and 'quantity' fields"
    ):
        EmailData(
            customer_name="John Smith",
            delivery_address="123 Main St",
            delivery_date="2025-06-20",
            items=[{"sku": "MD-001"}],  # Missing quantity
        )

    # Invalid quantity
    with pytest.raises(ValueError, match="Quantity must be a positive integer"):
        EmailData(
            customer_name="John Smith",
            delivery_address="123 Main St",
            delivery_date="2025-06-20",
            items=[{"sku": "MD-001", "quantity": 0}],
        )


def test_parse_email_error_handling(parser):
    """Test error handling in email parsing."""
    with (
        patch.object(parser, "prompt") as mock_prompt,
        patch.object(parser, "llm"),
        patch.object(parser, "output_parser"),
    ):
        # Mock chain that raises an exception
        mock_chain = Mock()
        mock_chain.invoke.side_effect = Exception("Chain execution failed")
        mock_prompt.__or__ = Mock(return_value=mock_chain)

        with pytest.raises(Exception, match="Chain execution failed"):
            parser.parse_email(SAMPLE_EMAIL_1)


def test_parse_email_alternate_format(parser, mock_llm_factory):
    """Test parsing email with alternate format."""
    mock_llm_factory.create_llm.return_value.invoke.return_value.content = """
    {
        "customer_name": "Jane Doe",
        "delivery_address": "456 Oak Avenue\\nSomewhere, CA 90210",
        "delivery_date": "2025-07-01",
        "items": [
            {"sku": "CT-001", "quantity": 1},
            {"sku": "TVS-002", "quantity": 2}
        ]
    }
    """

    order = parser.parse_email(SAMPLE_EMAIL_2)

    assert isinstance(order, Order)
    assert order.customer == EXPECTED_ORDER_2["customer"]
    assert order.address == EXPECTED_ORDER_2["address"]
    assert order.delivery_date == EXPECTED_ORDER_2["delivery_date"]
    assert len(order.items) == len(EXPECTED_ORDER_2["items"])


def test_parse_email_missing_data(parser, mock_llm_factory):
    """Test handling of missing data in email."""
    mock_llm_factory.create_llm.return_value.invoke.return_value.content = """
    {
        "customer_name": "John Smith",
        "delivery_address": "123 Main Street",
        "delivery_date": "2025-06-20",
        "items": []
    }
    """

    order = parser.parse_email(SAMPLE_EMAIL_1)

    assert isinstance(order, Order)
    assert order.customer == "John Smith"
    assert order.address == "123 Main Street"
    assert order.delivery_date == date(2025, 6, 20)
    assert len(order.items) == 0


def test_parse_email_invalid_date(parser, mock_llm_factory):
    """Test handling of invalid date format."""
    mock_llm_factory.create_llm.return_value.invoke.return_value.content = """
    {
        "customer_name": "John Smith",
        "delivery_address": "123 Main Street",
        "delivery_date": "invalid-date",
        "items": []
    }
    """

    with pytest.raises(ValueError):
        parser.parse_email(SAMPLE_EMAIL_1)
