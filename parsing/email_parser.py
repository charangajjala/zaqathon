"""LangChain-based email parser implementation."""

from datetime import date

from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import PydanticOutputParser

from core.exceptions import ParsingError
from core.interfaces import EmailParser
from core.models import Order, OrderItem
from prompts.email_extraction import EmailExtractionPrompt

from .email_data import EmailData


class LangChainEmailParser(EmailParser):
    """Email parser implementation using LangChain."""

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.output_parser = PydanticOutputParser(pydantic_object=EmailData)
        self.prompt = self._create_prompt()

    def _create_prompt(self):
        """Create prompt template with format instructions."""
        base_prompt = EmailExtractionPrompt.create_extraction_prompt()
        return base_prompt.partial(
            format_instructions=self.output_parser.get_format_instructions()
        )

    def parse_email(self, email_text: str) -> Order:
        """Parse email text and return structured Order object."""
        try:
            # Create the chain using LangChain syntax
            chain = self.prompt | self.llm | self.output_parser

            # Execute the chain
            parsed_data = chain.invoke({"email_text": email_text})

            # Convert parsed data to Order object
            return self._create_order(parsed_data)

        except Exception as e:
            raise ParsingError(f"Failed to parse email: {e}") from e

    def _create_order(self, data: EmailData) -> Order:
        """Create Order object from parsed data."""
        order_items = [
            OrderItem(
                sku=item["sku"],
                quantity=item["quantity"],
                valid=True,  # Will be validated later
            )
            for item in data.items
        ]

        return Order(
            customer=data.customer_name,
            address=data.delivery_address,
            delivery_date=date.fromisoformat(data.delivery_date),
            items=order_items,
        )
