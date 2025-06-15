"""Order processing implementation."""

from core.interfaces import EmailParser, OrderProcessor, OrderValidator
from core.models import Order


class SmartOrderProcessor(OrderProcessor):
    """Main order processor implementation."""

    def __init__(self, parser: EmailParser, validator: OrderValidator):
        self.parser = parser
        self.validator = validator

    def process_order(self, email_text: str) -> Order:
        """Process email text and return validated order."""
        # Parse email
        order = self.parser.parse_email(email_text)

        # Validate each item
        for item in order.items:
            validation_result = self.validator.validate_item(item)
            item.valid = validation_result.is_valid
            item.notes = validation_result.notes
            item.suggestions = validation_result.suggestions

        return order
