from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from finops_tool.models import AllocationLine, AllocationResult, ClassifiedCostItem, SummaryRow


class CostAllocator:
    def allocate(self, item: ClassifiedCostItem) -> AllocationResult:
        if item.shared_splits:
            allocations = self._split(item)
        else:
            allocations = [AllocationLine(entity=item.owner, amount=item.normalized_amount, weight=1.0)]

        return AllocationResult(**item.model_dump(), allocations=allocations)

    def summarize_by_category(self, items: Iterable[AllocationResult]) -> list[SummaryRow]:
        buckets: dict[str, dict[str, float | int]] = defaultdict(lambda: {"amount": 0.0, "count": 0})
        for item in items:
            bucket = buckets[item.category]
            bucket["amount"] = float(bucket["amount"]) + item.normalized_amount
            bucket["count"] = int(bucket["count"]) + 1
        return [SummaryRow(key=key, amount=round(float(value["amount"]), 2), count=int(value["count"])) for key, value in buckets.items()]

    def summarize_by_owner(self, items: Iterable[AllocationResult]) -> list[SummaryRow]:
        buckets: dict[str, dict[str, float | int]] = defaultdict(lambda: {"amount": 0.0, "count": 0})
        for item in items:
            for allocation in item.allocations:
                bucket = buckets[allocation.entity]
                bucket["amount"] = float(bucket["amount"]) + allocation.amount
                bucket["count"] = int(bucket["count"]) + 1
        return [SummaryRow(key=key, amount=round(float(value["amount"]) , 2), count=int(value["count"])) for key, value in buckets.items()]

    def _split(self, item: ClassifiedCostItem) -> list[AllocationLine]:
        total_weight = sum(split.weight for split in item.shared_splits)
        if total_weight <= 0:
            return [AllocationLine(entity=item.owner, amount=item.normalized_amount, weight=1.0)]

        allocations: list[AllocationLine] = []
        allocated = 0.0
        for index, split in enumerate(item.shared_splits, start=1):
            if index == len(item.shared_splits):
                amount = round(item.normalized_amount - allocated, 2)
            else:
                amount = round(item.normalized_amount * (split.weight / total_weight), 2)
                allocated += amount
            allocations.append(AllocationLine(entity=split.entity, amount=amount, weight=split.weight))
        return allocations
