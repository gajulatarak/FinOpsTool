from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AllocationRule:
    name: str
    category: str
    match_vendors: List[str] = field(default_factory=list)
    match_services: List[str] = field(default_factory=list)
    owner: str = "unassigned"
    cost_center: str = "unassigned"
    allocation_method: str = "direct"


@dataclass
class DiscoveryConfig:
    aws: dict = field(default_factory=lambda: {"enabled": False, "org_id": None, "region": "us-east-1"})
    azure: dict = field(default_factory=lambda: {"enabled": False, "tenant_id": None, "subscription_ids": []})
    gcp: dict = field(default_factory=lambda: {"enabled": False, "organization_id": None, "project_ids": []})


@dataclass
class FinOpsSettings:
    company_name: str = "Your Company"
    currency: str = "USD"
    default_category: str = "other"
    supported_categories: List[str] = field(default_factory=lambda: [
        "cloud",
        "saas",
        "licenses",
        "other",
    ])
    category_aliases: Dict[str, str] = field(default_factory=lambda: {
        "infrastructure": "cloud",
        "platform": "cloud",
        "subscriptions": "saas",
        "software": "licenses",
    })
    allocation_rules: List[AllocationRule] = field(default_factory=lambda: [
        AllocationRule(
            name="Cloud provider rule",
            category="cloud",
            match_vendors=["aws", "amazon web services", "microsoft azure", "google cloud", "gcp"],
            owner="platform",
            cost_center="cloud-platform",
            allocation_method="direct",
        ),
        AllocationRule(
            name="SaaS rule",
            category="saas",
            match_vendors=["salesforce", "slack", "zoom", "atlassian", "notion", "workday"],
            owner="business-ops",
            cost_center="shared-saas",
            allocation_method="direct",
        ),
        AllocationRule(
            name="License rule",
            category="licenses",
            match_vendors=["microsoft", "adobe", "jetbrains", "oracle"],
            owner="it",
            cost_center="software-licenses",
            allocation_method="direct",
        ),
    ])
    discovery: DiscoveryConfig = field(default_factory=DiscoveryConfig)
