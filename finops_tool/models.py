from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class SharedSplit(BaseModel):
    entity: str = Field(..., description="Team, product, department, or cost center receiving the share")
    weight: float = Field(..., gt=0, description="Share weight; values are normalized across all splits")


class CostItem(BaseModel):
    source: str = Field(..., description="Source system, such as cloud-billing, saas-invoice, or manual-upload")
    vendor: str = Field(..., description="Vendor or provider name")
    service: str = Field(..., description="Service or product name")
    amount: float = Field(..., ge=0)
    currency: str = Field(default="USD")
    period: date
    team: Optional[str] = None
    product: Optional[str] = None
    cost_center: Optional[str] = None
    tags: dict[str, str] = Field(default_factory=dict)
    notes: Optional[str] = None
    shared_splits: List[SharedSplit] = Field(default_factory=list)


class ClassifiedCostItem(CostItem):
    category: str
    subcategory: str = "general"
    owner: str
    allocation_method: str
    normalized_amount: float
    rule_name: Optional[str] = None


class AllocationLine(BaseModel):
    entity: str
    amount: float
    weight: float


class AllocationResult(ClassifiedCostItem):
    allocations: List[AllocationLine] = Field(default_factory=list)


class SummaryRow(BaseModel):
    key: str
    amount: float
    count: int
