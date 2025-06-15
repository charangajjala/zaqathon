"""Core data models for the order processing system."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """Represents a single item in an order."""

    sku: str = Field(description="Product SKU code")
    quantity: int = Field(description="Quantity ordered", gt=0)
    valid: bool = Field(default=True, description="Whether the order item is valid")
    notes: Optional[str] = Field(default=None, description="Validation notes")
    suggestions: Optional[list[dict]] = Field(
        default=None, description="Validation suggestions"
    )


class Order(BaseModel):
    """Represents a customer order."""

    customer: str = Field(description="Customer name")
    address: str = Field(description="Delivery address")
    delivery_date: date = Field(description="Requested delivery date")
    items: list[OrderItem] = Field(description="List of ordered items")

    class Config:
        json_schema_extra = {
            "example": {
                "customer": "John Smith",
                "address": "123 Main St, Anytown, USA",
                "delivery_date": "2025-06-20",
                "items": [
                    {
                        "sku": "MD-001",
                        "quantity": 2,
                        "valid": True,
                        "notes": None,
                        "suggestions": None,
                    }
                ],
            }
        }
