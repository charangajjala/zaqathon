"""Order display components for Streamlit UI."""

import streamlit as st

from core.models import Order


class OrderDisplay:
    """Handles the display of order information."""

    @staticmethod
    def show_order_details(order: Order):
        """Display order details."""
        st.subheader("Order Details")
        st.json(order.model_dump())

    @staticmethod
    def show_validation_results(order: Order):
        """Display validation results with suggestions."""
        st.subheader("Validation Results")

        for item in order.items:
            col1, col2 = st.columns([1, 3])

            with col1:
                status = "✅" if item.valid else "❌"
                st.write(f"{status} {item.sku}")
                st.write(f"Quantity: {item.quantity}")

            with col2:
                st.write(f"Status: {item.notes}")

                if not item.valid and item.suggestions:
                    st.write("Suggestions:")
                    OrderDisplay._display_suggestions(item.suggestions)

    @staticmethod
    def _display_suggestions(suggestions: list):
        """Display validation suggestions."""
        for suggestion in suggestions:
            suggestion_type = suggestion.get("type")

            if suggestion_type == "quantity_adjustment":
                st.write(
                    f"• Adjust quantity to {suggestion['suggested_quantity']} to meet MOQ"
                )
            elif suggestion_type == "stock_limit":
                st.write(
                    f"• Reduce quantity to {suggestion['available_quantity']} due to stock limits"
                )
            else:
                # Similar product suggestion
                st.write(
                    f"• Similar product: {suggestion['sku']} - {suggestion['name']}"
                )
                st.write(f"  MOQ: {suggestion['moq']}, Stock: {suggestion['stock']}")

    @staticmethod
    def show_processing_summary(order: Order):
        """Show processing summary."""
        valid_items = sum(1 for item in order.items if item.valid)
        total_items = len(order.items)

        if valid_items == total_items:
            st.success(f"✅ All {total_items} items are valid!")
        else:
            st.warning(
                f"⚠️ {valid_items}/{total_items} items are valid. Please review suggestions above."
            )
