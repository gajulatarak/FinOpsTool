from __future__ import annotations

import json
import subprocess
from datetime import date

from finops_tool.models import CostItem
from finops_tool.providers.base import ProviderAccount, ProviderAdapter, DiscoveryError


class AzureAdapter(ProviderAdapter):
    provider_name = "azure"

    def __init__(self, tenant_id: str | None = None, subscription_ids: list[str] | None = None):
        self.tenant_id = tenant_id
        self.subscription_ids = subscription_ids or []

    def discover_accounts(self) -> list[ProviderAccount]:
        subscription_ids = self.subscription_ids or self._discover_with_azure_cli()
        return [
            ProviderAccount(
                provider=self.provider_name,
                account_id=sub_id,
                account_name=sub_id,
                status="active",
                metadata={"tenant_id": self.tenant_id},
            )
            for sub_id in subscription_ids
        ]

    def discover_cost_items(self) -> list[CostItem]:
        if not self.subscription_ids:
            return []
        return [
            CostItem(
                source="azure-billing-export",
                vendor="Microsoft Azure",
                service="Compute",
                amount=0.0,
                currency="USD",
                period=date.today(),
                tags={"provider": "azure", "category": "cloud"},
            )
        ]

    def pull_from_rest(self) -> list[CostItem]:
        raise DiscoveryError("Azure REST billing pull is not configured yet; use subscription discovery or add exporter integration.")

    def _discover_with_azure_cli(self) -> list[str]:
        try:
            completed = subprocess.run(
                ["az", "account", "list", "--output", "json"],
                capture_output=True,
                check=True,
                text=True,
            )
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DiscoveryError("Azure discovery requires the Azure CLI to be signed in or explicit subscription IDs") from exc

        payload = json.loads(completed.stdout or "[]")
        return [account["id"] for account in payload if account.get("id")]
