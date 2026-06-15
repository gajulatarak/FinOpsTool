from __future__ import annotations

import json
import subprocess
from datetime import date

from finops_tool.models import CostItem
from finops_tool.providers.base import ProviderAccount, ProviderAdapter, DiscoveryError


class GCPAdapter(ProviderAdapter):
    provider_name = "gcp"

    def __init__(self, organization_id: str | None = None, project_ids: list[str] | None = None):
        self.organization_id = organization_id
        self.project_ids = project_ids or []

    def discover_accounts(self) -> list[ProviderAccount]:
        project_ids = self.project_ids or self._discover_with_gcloud_cli()
        return [
            ProviderAccount(
                provider=self.provider_name,
                account_id=project_id,
                account_name=project_id,
                status="active",
                metadata={"organization_id": self.organization_id},
            )
            for project_id in project_ids
        ]

    def discover_cost_items(self) -> list[CostItem]:
        if not self.project_ids:
            return []
        return [
            CostItem(
                source="gcp-billing-export",
                vendor="Google Cloud",
                service="Compute Engine",
                amount=0.0,
                currency="USD",
                period=date.today(),
                tags={"provider": "gcp", "category": "cloud"},
            )
        ]

    def pull_from_bigquery_export(self) -> list[CostItem]:
        raise DiscoveryError("GCP BigQuery export sync is not configured yet; use project discovery or add a billing export connector.")

    def _discover_with_gcloud_cli(self) -> list[str]:
        command = ["gcloud", "projects", "list", "--format=json"]
        if self.organization_id:
            command.extend(["--filter", f"parent.id={self.organization_id}"])

        try:
            completed = subprocess.run(command, capture_output=True, check=True, text=True)
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DiscoveryError("GCP discovery requires gcloud to be authenticated or explicit project IDs") from exc

        payload = json.loads(completed.stdout or "[]")
        return [project["projectId"] for project in payload if project.get("projectId")]
