from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from finops_tool.models import CostItem


@dataclass
class ProviderAccount:
    provider: str
    account_id: str
    account_name: str
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)


class DiscoveryError(RuntimeError):
    pass


class ProviderAdapter(ABC):
    provider_name: str

    @abstractmethod
    def discover_accounts(self) -> list[ProviderAccount]:
        raise NotImplementedError

    @abstractmethod
    def discover_cost_items(self) -> list[CostItem]:
        raise NotImplementedError
