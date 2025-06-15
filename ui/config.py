"""Configuration display components for Streamlit UI."""

import os

import streamlit as st

from processing.llm_factory import LLMFactory


class ConfigurationDisplay:
    """Handles the display of configuration options."""

    @staticmethod
    def show_llm_configuration() -> str:
        """Display current LLM configuration in sidebar."""
        st.sidebar.subheader("LLM Configuration")

        # Show available providers
        available_providers = LLMFactory.get_available_providers()
        current_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")

        st.sidebar.write(f"**Current Provider:** {current_provider}")
        st.sidebar.write(f"**Available Providers:** {', '.join(available_providers)}")
        st.sidebar.write(
            f"**Model:** {os.getenv('DEFAULT_MODEL', 'gpt-4-turbo-preview')}"
        )
        st.sidebar.write(f"**Temperature:** {os.getenv('TEMPERATURE', '0.0')}")

        # Provider selection
        selected_provider = st.sidebar.selectbox(
            "Select LLM Provider:",
            available_providers,
            index=available_providers.index(current_provider)
            if current_provider in available_providers
            else 0,
        )

        return selected_provider

    @staticmethod
    def show_app_header():
        """Display application header."""
        st.title("Smart Order Intake System")
        st.markdown("*AI-powered email parsing with modular LLM providers*")

    @staticmethod
    def show_input_section() -> tuple[str, bool]:
        """Display email input section."""
        email_text = st.text_area(
            "Paste customer email here:",
            height=200,
            placeholder="Paste your customer email here...",
        )

        # Processing options
        col1, col2 = st.columns([1, 1])
        with col1:
            process_button = st.button("Process Order", type="primary")
        with col2:
            if st.button("Clear"):
                st.rerun()

        return email_text, process_button
