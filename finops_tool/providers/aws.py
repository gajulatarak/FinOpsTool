from __future__ import annotations

import json
import subprocess
from datetime import date
from datetime import timedelta

from finops_tool.models import CostItem
from finops_tool.providers.base import ProviderAccount, ProviderAdapter, DiscoveryError


class AWSAdapter(ProviderAdapter):
    provider_name = "aws"

    def __init__(self, org_id: str | None = None, region: str | None = None):
        self.org_id = org_id
        self.region = region or "us-east-1"

    def discover_accounts(self) -> list[ProviderAccount]:
        try:
            client = self._client()
            accounts: list[ProviderAccount] = []
            paginator = client.get_paginator("list_accounts")
            for page in paginator.paginate():
                for account in page.get("Accounts", []):
                    accounts.append(
                        ProviderAccount(
                            provider=self.provider_name,
                            account_id=account["Id"],
                            account_name=account.get("Name", account["Id"]),
                            status=account.get("Status", "ACTIVE").lower(),
                            metadata={"email": account.get("Email")},
                        )
                    )
            return accounts
        except Exception:
            return self._discover_accounts_with_aws_cli()

    def discover_cost_items(self) -> list[CostItem]:
        client = self._ce_client()
        end_date = date.today() + timedelta(days=1)
        items = client.get_cost_and_usage(
            TimePeriod={"Start": str(date.today().replace(day=1)), "End": str(end_date)},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )
        results: list[CostItem] = []
        for group in items.get("ResultsByTime", []):
            for item in group.get("Groups", []):
                amount = float(item["Metrics"]["UnblendedCost"]["Amount"])
                service = item["Keys"][0]
                results.append(
                    CostItem(
                        source="aws-cost-explorer",
                        vendor="AWS",
                        service=service,
                        amount=amount,
                        currency="USD",
                        period=date.today(),
                        tags={"provider": "aws", "category": "cloud"},
                    )
                )
        return results

    def _client(self):
        try:
            import boto3
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DiscoveryError("boto3 is required for AWS discovery") from exc

        return boto3.client("organizations", region_name=self.region)

    def _ce_client(self):
        try:
            import boto3
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DiscoveryError("boto3 is required for AWS cost discovery") from exc

        return boto3.client("ce", region_name=self.region)

    def _discover_accounts_with_aws_cli(self) -> list[ProviderAccount]:
        try:
            completed = subprocess.run(
                ["aws", "organizations", "list-accounts", "--output", "json"],
                capture_output=True,
                check=True,
                text=True,
            )
        except Exception as exc:  # pragma: no cover - optional dependency
            raise DiscoveryError("AWS discovery requires boto3 or the AWS CLI configured with Organizations access") from exc

        payload = json.loads(completed.stdout or "{}")
        accounts: list[ProviderAccount] = []
        for account in payload.get("Accounts", []):
            accounts.append(
                ProviderAccount(
                    provider=self.provider_name,
                    account_id=account["Id"],
                    account_name=account.get("Name", account["Id"]),
                    status=account.get("Status", "ACTIVE").lower(),
                    metadata={"email": account.get("Email")},
                )
            )
        return accounts
