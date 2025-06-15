"""Email extraction prompt templates using LangChain."""

from langchain_core.prompts import PromptTemplate


class EmailExtractionPrompt:
    """Email extraction prompt templates."""

    @staticmethod
    def create_extraction_prompt() -> PromptTemplate:
        """Create prompt template for email order extraction."""
        template = """You are an expert at extracting order information from customer emails.

Extract the following information from the email:
- Customer name (full name)
- Delivery address (complete address)
- Delivery date (in YYYY-MM-DD format)
- List of items with SKU and quantity

Be precise and accurate in your extraction. If any information is missing or unclear, use reasonable defaults or mark as unknown.

{format_instructions}

Email text:
{email_text}"""

        return PromptTemplate(
            template=template,
            input_variables=["email_text"],
            partial_variables={"format_instructions": "{format_instructions}"},
        )

    @staticmethod
    def create_validation_prompt() -> PromptTemplate:
        """Create prompt template for order validation feedback."""
        template = """Review the following order validation results and provide customer-friendly feedback:

Order Details:
{order_details}

Validation Issues:
{validation_issues}

Provide a clear, professional response explaining any issues and suggested solutions."""

        return PromptTemplate(
            template=template, input_variables=["order_details", "validation_issues"]
        )
