"""Test data for order processing system."""

from datetime import date

# Sample email texts
SAMPLE_EMAIL_1 = """
From: John Smith <john.smith@email.com>
Subject: New Order Request

Hi,

I would like to place an order for the following items:

- 2x Modern Desk (SKU: MD-001)
- 1x Dining Table (SKU: DT-002)
- 3x Bookshelf (SKU: BS-003)

Please deliver to:
123 Main Street
Anytown, USA 12345

Delivery date: 2025-06-20

Could you please confirm if these items are in stock?

Thanks,
John
"""

SAMPLE_EMAIL_2 = """
From: Jane Doe <jane.doe@email.com>
Subject: Urgent Order

Hello,

Need these items ASAP:

1. 1x Coffee Table (SKU: CT-001)
2. 2x TV Stand (SKU: TVS-002)

Delivery Address:
456 Oak Avenue
Somewhere, CA 90210

Delivery Date: 2025-07-01

Please confirm availability.

Best,
Jane
"""

# Sample catalog data
SAMPLE_CATALOG = [
    {
        "Product Code": "MD-001",
        "Product Name": "Modern Desk",
        "Available Stock": 10,
        "Minimum Order Quantity": 1,
        "Description": "Modern office desk",
    },
    {
        "Product Code": "DT-002",
        "Product Name": "Dining Table",
        "Available Stock": 5,
        "Minimum Order Quantity": 1,
        "Description": "Wooden dining table",
    },
    {
        "Product Code": "BS-003",
        "Product Name": "Bookshelf",
        "Available Stock": 2,
        "Minimum Order Quantity": 2,
        "Description": "Tall bookshelf",
    },
    {
        "Product Code": "CT-001",
        "Product Name": "Coffee Table",
        "Available Stock": 0,
        "Minimum Order Quantity": 1,
        "Description": "Modern coffee table",
    },
    {
        "Product Code": "TVS-002",
        "Product Name": "TV Stand",
        "Available Stock": 3,
        "Minimum Order Quantity": 2,
        "Description": "TV stand with storage",
    },
]

# Expected parsed orders
EXPECTED_ORDER_1 = {
    "customer": "John Smith",
    "address": "123 Main Street\nAnytown, USA 12345",
    "delivery_date": date(2025, 6, 20),
    "items": [
        {"sku": "MD-001", "quantity": 2, "valid": True},
        {"sku": "DT-002", "quantity": 1, "valid": True},
        {"sku": "BS-003", "quantity": 3, "valid": False},
    ],
}

EXPECTED_ORDER_2 = {
    "customer": "Jane Doe",
    "address": "456 Oak Avenue\nSomewhere, CA 90210",
    "delivery_date": date(2025, 7, 1),
    "items": [
        {"sku": "CT-001", "quantity": 1, "valid": False},
        {"sku": "TVS-002", "quantity": 2, "valid": True},
    ],
}
