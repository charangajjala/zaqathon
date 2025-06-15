"""Core module containing base models and interfaces."""

from .exceptions import ParsingError, ValidationError
from .interfaces import EmailParser, OrderProcessor, OrderValidator
from .models import Order, OrderItem

__all__ = [
    "Order",
    "OrderItem",
    "EmailParser",
    "OrderValidator",
    "OrderProcessor",
    "ValidationError",
    "ParsingError",
]
