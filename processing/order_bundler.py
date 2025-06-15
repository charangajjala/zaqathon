"""Smart order bundling to optimize quantities and meet MOQ requirements."""

from typing import Any, Dict, List

from core.interfaces import CatalogDataSource
from core.models import Order


class BundleAnalysisResult:
    """Container for bundling analysis results."""

    def __init__(self, order: Order, bundle_suggestions: Dict[str, Any]):
        self.order = order
        self.bundle_suggestions = bundle_suggestions


class OrderBundler:
    """Analyzes orders and suggests bundling to meet MOQ requirements."""

    def __init__(self, catalog_source: CatalogDataSource):
        self.catalog_source = catalog_source

    def analyze_and_suggest_bundles(self, order: Order) -> Dict[str, Any]:
        """Analyze order and suggest bundling opportunities."""
        try:
            bundle_suggestions = {
                "moq_bundles": self._suggest_moq_bundles(order),
                "category_bundles": self._suggest_category_bundles(order),
                "bulk_discounts": self._suggest_bulk_optimizations(order),
                "summary": self._create_bundle_summary(order),
            }
            return bundle_suggestions
        except Exception as e:
            return {
                "moq_bundles": [],
                "category_bundles": [],
                "bulk_discounts": [],
                "summary": {"error": str(e)},
            }

    def _suggest_moq_bundles(self, order: Order) -> List[Dict[str, Any]]:
        """Suggest combining items to meet MOQ requirements."""
        moq_suggestions = []
        moq_violations = []

        for item in order.items:
            try:
                product = self.catalog_source.get_product_details(item.sku)
                if product and item.quantity < product["moq"]:
                    moq_violations.append(
                        {
                            "item": item,
                            "product": product,
                            "shortfall": product["moq"] - item.quantity,
                        }
                    )
            except Exception:
                continue

        if not moq_violations:
            return []

        category_groups = {}
        for violation in moq_violations:
            category = violation["item"].sku[:3]
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(violation)

        for category, violations in category_groups.items():
            if len(violations) > 1:
                total_quantity = sum(v["item"].quantity for v in violations)
                max_moq = max(v["product"]["moq"] for v in violations)

                if total_quantity >= max_moq:
                    moq_suggestions.append(
                        {
                            "type": "moq_bundle",
                            "category": category,
                            "items": [v["item"].sku for v in violations],
                            "current_total": total_quantity,
                            "suggested_redistribution": self._suggest_redistribution(
                                violations
                            ),
                            "benefit": "Meet MOQ requirements by redistributing quantities",
                        }
                    )

        return moq_suggestions

    def _suggest_category_bundles(self, order: Order) -> List[Dict[str, Any]]:
        """Suggest bundling items from the same category for better deals."""
        category_bundles = []
        category_items = {}

        for item in order.items:
            category = item.sku[:3]
            if category not in category_items:
                category_items[category] = []
            category_items[category].append(item)

        for category, items in category_items.items():
            if len(items) > 1:
                total_quantity = sum(item.quantity for item in items)
                category_name = self._get_category_name(category)

                category_bundles.append(
                    {
                        "type": "category_bundle",
                        "category": category,
                        "category_name": category_name,
                        "items": [item.sku for item in items],
                        "total_quantity": total_quantity,
                        "suggestion": f"You're ordering {len(items)} different {category_name} items",
                        "benefit": "Potential bulk discounts and shipping efficiency",
                    }
                )

        return category_bundles

    def _suggest_bulk_optimizations(self, order: Order) -> List[Dict[str, Any]]:
        """Suggest bulk quantity optimizations."""
        bulk_suggestions = []

        for item in order.items:
            try:
                product = self.catalog_source.get_product_details(item.sku)
                if not product:
                    continue

                current_qty = item.quantity
                bulk_quantities = [5, 10, 25, 50]

                for bulk_qty in bulk_quantities:
                    if bulk_qty > current_qty and bulk_qty <= product["stock"]:
                        efficiency_gain = (bulk_qty - current_qty) / current_qty * 100
                        if efficiency_gain <= 50:
                            bulk_suggestions.append(
                                {
                                    "type": "bulk_optimization",
                                    "sku": item.sku,
                                    "current_quantity": current_qty,
                                    "suggested_quantity": bulk_qty,
                                    "additional_units": bulk_qty - current_qty,
                                    "benefit": "Better bulk pricing and reduced ordering frequency",
                                }
                            )
                        break
            except Exception:
                continue

        return bulk_suggestions

    def _suggest_redistribution(
        self, violations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest how to redistribute quantities to meet MOQ."""
        redistributions = []

        try:
            violations_sorted = sorted(
                violations, key=lambda x: x["product"]["moq"], reverse=True
            )
            primary_item = violations_sorted[0]

            total_available = sum(v["item"].quantity for v in violations)
            primary_moq = primary_item["product"]["moq"]

            if total_available >= primary_moq:
                remaining = total_available - primary_moq

                redistributions.append(
                    {
                        "sku": primary_item["item"].sku,
                        "current": primary_item["item"].quantity,
                        "suggested": primary_moq,
                        "reason": "Prioritize meeting highest MOQ requirement",
                    }
                )

                other_violations = violations_sorted[1:]
                if other_violations and remaining > 0:
                    per_item = max(1, remaining // len(other_violations))
                    for violation in other_violations:
                        suggested_qty = min(per_item, violation["product"]["stock"])
                        redistributions.append(
                            {
                                "sku": violation["item"].sku,
                                "current": violation["item"].quantity,
                                "suggested": suggested_qty,
                                "reason": "Distribute remaining quantity efficiently",
                            }
                        )
        except Exception:
            pass

        return redistributions

    def _get_category_name(self, category_code: str) -> str:
        """Get human-readable category name from code."""
        category_map = {
            "DSK": "Desk",
            "CHR": "Chair",
            "DTB": "Dining Table",
            "DCH": "Dining Chair",
            "BSF": "Bookshelf",
            "SFA": "Sofa",
            "CFT": "Coffee Table",
            "TVS": "TV Stand",
        }
        return category_map.get(category_code, category_code)

    def _create_bundle_summary(self, order: Order) -> Dict[str, Any]:
        """Create a summary of bundling opportunities."""
        try:
            total_items = len(order.items)
            invalid_items = sum(1 for item in order.items if not item.valid)

            categories = {}
            for item in order.items:
                category = item.sku[:3]
                categories[category] = categories.get(category, 0) + 1

            return {
                "total_items": total_items,
                "invalid_items": invalid_items,
                "categories_represented": len(categories),
                "bundling_potential": "High"
                if len(categories) < total_items
                else "Low",
            }
        except Exception as e:
            return {"error": str(e)}
