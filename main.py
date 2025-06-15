"""Main application entry point."""

import os

import streamlit as st
from dotenv import load_dotenv

from core.interfaces import EmailParser, OrderValidator
from parsing.email_parser import LangChainEmailParser
from processing.llm_factory import LLMFactory
from processing.order_processor import SmartOrderProcessor
from ui.config import ConfigurationDisplay
from ui.display import OrderDisplay
from validation.catalog_validator import CatalogValidator


def initialize_components(selected_provider: str) -> tuple[EmailParser, OrderValidator]:
    """Initialize application components."""
    load_dotenv()

    # Get LLM configuration
    llm_config = {
        "model": os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview"),
        "temperature": float(os.getenv("TEMPERATURE", "0.0")),
    }

    # Create LLM instance
    llm = LLMFactory.create_llm(provider=selected_provider, **llm_config)

    # Initialize parser
    parser = LangChainEmailParser(llm)

    # Initialize validator
    validator = CatalogValidator.from_csv("rezaqaround2zaqathon/Product Catalog.csv")

    return parser, validator


def main():
    """Main application entry point."""
    # Display header
    ConfigurationDisplay.show_app_header()

    # Show LLM configuration
    selected_provider = ConfigurationDisplay.show_llm_configuration()

    # Initialize components
    try:
        parser, validator = initialize_components(selected_provider)
        processor = SmartOrderProcessor(parser, validator)
        display = OrderDisplay()

    except Exception as e:
        st.error(f"Failed to initialize components: {str(e)}")
        st.info("Please check your environment configuration and API keys.")
        return

    # Show input section
    email_text, process_button = ConfigurationDisplay.show_input_section()

    if process_button:
        if not email_text.strip():
            st.error("Please enter an email")
            return

        try:
            with st.spinner(f"Processing with {selected_provider}..."):
                # Process order
                order = processor.process_order(email_text)

                # Display results
                display.show_order_details(order)
                display.show_validation_results(order)
                display.show_processing_summary(order)

        except Exception as e:
            st.error(f"Error processing order: {str(e)}")
            st.info("Please check your email format and try again.")


if __name__ == "__main__":
    main()
