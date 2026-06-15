from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from finops_tool.models import AllocationResult, SummaryRow


@dataclass
class FinOpsReport:
    total_spend: float
    by_category: list[SummaryRow]
    by_owner: list[SummaryRow]
    unallocated_count: int


class ReportService:
    def build(self, items: Iterable[AllocationResult], category_rows: list[SummaryRow], owner_rows: list[SummaryRow]) -> FinOpsReport:
        materialized = list(items)
        total_spend = round(sum(item.normalized_amount for item in materialized), 2)
        unallocated_count = sum(1 for item in materialized if item.allocation_method == "fallback")
        return FinOpsReport(
            total_spend=total_spend,
            by_category=category_rows,
            by_owner=owner_rows,
            unallocated_count=unallocated_count,
        )
