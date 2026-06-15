from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from finops_tool.models import CostItem
from finops_tool.providers.aws import AWSAdapter
from finops_tool.providers.azure import AzureAdapter
from finops_tool.providers.base import ProviderAccount, ProviderAdapter
from finops_tool.providers.gcp import GCPAdapter


@dataclass
class DiscoverySnapshot:
    accounts: list[ProviderAccount] = field(default_factory=list)
    cost_items: list[CostItem] = field(default_factory=list)


class DiscoveryService:
    def __init__(self, adapters: Iterable[ProviderAdapter] | None = None):
        self.adapters = list(adapters) if adapters is not None else []

    @classmethod
    def from_config(cls, config: dict | None = None) -> "DiscoveryService":
        config = config or {}
        adapters: list[ProviderAdapter] = []

        aws_cfg = config.get("aws", {})
        if aws_cfg.get("enabled"):
            adapters.append(AWSAdapter(org_id=aws_cfg.get("org_id"), region=aws_cfg.get("region")))

        azure_cfg = config.get("azure", {})
        if azure_cfg.get("enabled"):
            adapters.append(AzureAdapter(tenant_id=azure_cfg.get("tenant_id"), subscription_ids=azure_cfg.get("subscription_ids", [])))

        gcp_cfg = config.get("gcp", {})
        if gcp_cfg.get("enabled"):
            adapters.append(GCPAdapter(organization_id=gcp_cfg.get("organization_id"), project_ids=gcp_cfg.get("project_ids", [])))

        return cls(adapters=adapters)

    def discover(self) -> DiscoverySnapshot:
        accounts: list[ProviderAccount] = []
        cost_items: list[CostItem] = []
        for adapter in self.adapters:
            accounts.extend(adapter.discover_accounts())
            cost_items.extend(adapter.discover_cost_items())
        return DiscoverySnapshot(accounts=accounts, cost_items=cost_items)
