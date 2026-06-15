from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from finops_tool.config import AllocationRule, FinOpsSettings
from finops_tool.models import ClassifiedCostItem, CostItem


class CostClassifier:
    def __init__(self, settings: FinOpsSettings | None = None):
        self.settings = settings or FinOpsSettings()

    def classify(self, item: CostItem) -> ClassifiedCostItem:
        matched_rule = self._match_rule(item)
        category = matched_rule.category if matched_rule else self._infer_category(item)
        owner = matched_rule.owner if matched_rule else self._infer_owner(category, item)
        cost_center = matched_rule.cost_center if matched_rule else (item.cost_center or "unassigned")
        allocation_method = matched_rule.allocation_method if matched_rule else self._infer_allocation_method(item)
        normalized_amount = round(float(item.amount), 2)
        payload = item.model_dump()
        payload["cost_center"] = cost_center

        return ClassifiedCostItem(
            **payload,
            category=category,
            subcategory=self._infer_subcategory(item, category),
            owner=owner,
            allocation_method=allocation_method,
            normalized_amount=normalized_amount,
            rule_name=matched_rule.name if matched_rule else None,
        )

    def _match_rule(self, item: CostItem) -> AllocationRule | None:
        vendor = item.vendor.lower()
        service = item.service.lower()
        for rule in self.settings.allocation_rules:
            if vendor in (candidate.lower() for candidate in rule.match_vendors):
                return rule
            if service in (candidate.lower() for candidate in rule.match_services):
                return rule
        return None

    def _infer_category(self, item: CostItem) -> str:
        candidate = self._normalize(item.tags.get("category") or item.tags.get("cost_type") or item.service)
        if candidate in self.settings.supported_categories:
            return candidate
        return self.settings.category_aliases.get(candidate, self.settings.default_category)

    def _infer_owner(self, category: str, item: CostItem) -> str:
        if item.team:
            return item.team
        if item.product:
            return item.product
        if category == "cloud":
            return "platform"
        if category == "saas":
            return "business-ops"
        if category == "licenses":
            return "it"
        return "unassigned"

    def _infer_allocation_method(self, item: CostItem) -> str:
        if item.shared_splits:
            return "shared"
        if item.team or item.product or item.cost_center:
            return "direct"
        return "fallback"

    def _infer_subcategory(self, item: CostItem, category: str) -> str:
        if category == "cloud":
            return self._normalize(item.service)
        if category == "saas":
            return self._normalize(item.vendor)
        if category == "licenses":
            return "seat-license"
        return "general"

    @staticmethod
    def _normalize(value: str | None) -> str:
        if not value:
            return ""
        return value.strip().lower().replace("/", "-").replace(" ", "-")


def classify_many(items: Iterable[CostItem], settings: FinOpsSettings | None = None) -> list[ClassifiedCostItem]:
    classifier = CostClassifier(settings)
    return [classifier.classify(item) for item in items]
