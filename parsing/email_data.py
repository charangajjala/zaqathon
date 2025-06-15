"""Email data model for parsing."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class EmailData(BaseModel):
    """Pydantic model for parsed email data."""

    customer_name: str = Field(description="Full name of the customer")
    delivery_address: str = Field(description="Complete delivery address")
    delivery_date: str = Field(
        description="Requested delivery date in YYYY-MM-DD format"
    )
    items: list[dict] = Field(description="List of ordered items with SKU and quantity")

    @field_validator("delivery_date")
    @classmethod
    def validate_date_format(cls, v):
        """Validate date format."""
        try:
            date.fromisoformat(v)
            return v
        except ValueError as e:
            raise ValueError("Date must be in YYYY-MM-DD format") from e

    @field_validator("items")
    @classmethod
    def validate_items(cls, v):
        """Validate items structure and normalize field names."""
        if not isinstance(v, list):
            raise ValueError("Items must be a list")

        normalized_items = []
        for item in v:
            if not isinstance(item, dict):
                raise ValueError("Each item must be a dictionary")

            # Normalize field names - handle both 'sku'/'SKU' and 'quantity'/'Quantity'
            normalized_item = {}

            # Find SKU field (case-insensitive)
            sku_key = None
            for key in item.keys():
                if key.lower() == "sku":
                    sku_key = key
                    break

            if sku_key is None:
                raise ValueError("Each item must have 'sku' or 'SKU' field")

            # Find quantity field (case-insensitive)
            quantity_key = None
            for key in item.keys():
                if key.lower() == "quantity":
                    quantity_key = key
                    break

            if quantity_key is None:
                raise ValueError("Each item must have 'quantity' or 'Quantity' field")

            # Normalize to lowercase field names
            normalized_item["sku"] = item[sku_key]
            normalized_item["quantity"] = item[quantity_key]

            # Validate quantity
            if (
                not isinstance(normalized_item["quantity"], int)
                or normalized_item["quantity"] <= 0
            ):
                raise ValueError("Quantity must be a positive integer")

            normalized_items.append(normalized_item)

        return normalized_items
