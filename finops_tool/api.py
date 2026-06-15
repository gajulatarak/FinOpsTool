from __future__ import annotations

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from finops_tool.config import FinOpsSettings
from finops_tool.models import AllocationResult, CostItem
from finops_tool.services.allocation import CostAllocator
from finops_tool.services.classification import CostClassifier
from finops_tool.services.discovery import DiscoveryService
from finops_tool.services.reporting import ReportService
from finops_tool.ui import (
    render_classify_page,
    render_config_page,
    render_dashboard_page,
    render_discovery_page,
    render_reports_page,
)

app = FastAPI(
    title="FinOps Tool",
    version="0.1.0",
    description="Enterprise FinOps control plane for SMB and mid-market teams.",
)

settings = FinOpsSettings()
classifier = CostClassifier(settings)
allocator = CostAllocator()
reporter = ReportService()


def _discovery_service() -> DiscoveryService:
    return DiscoveryService.from_config(settings.discovery.__dict__)


def _report_payload() -> dict:
    snapshot = _discovery_service().discover()
    discovered_items = snapshot.cost_items or SAMPLE_COSTS
    results = [allocator.allocate(classifier.classify(item)) for item in discovered_items]
    report = reporter.build(
        items=results,
        category_rows=allocator.summarize_by_category(results),
        owner_rows=allocator.summarize_by_owner(results),
    )
    return {
        "summary": {
            "total_spend": report.total_spend,
            "unallocated_count": report.unallocated_count,
            "by_category": [row.model_dump() for row in report.by_category],
            "by_owner": [row.model_dump() for row in report.by_owner],
        },
        "items": [item.model_dump() for item in results],
        "discovery": {
            "accounts": [account.__dict__ for account in snapshot.accounts],
            "source": "auto-discovery" if snapshot.cost_items else "sample-data-fallback",
        },
    }


SAMPLE_COSTS = [
    CostItem(
        source="cloud-billing",
        vendor="AWS",
        service="EC2",
        amount=1240.50,
        currency="USD",
        period="2026-06-01",
        team="platform",
        cost_center="engineering-platform",
        tags={"env": "prod", "category": "cloud"},
        shared_splits=[],
    ),
    CostItem(
        source="saas-invoice",
        vendor="Slack",
        service="Business+",
        amount=420.00,
        currency="USD",
        period="2026-06-01",
        team="all-hands",
        tags={"category": "saas"},
        shared_splits=[],
    ),
    CostItem(
        source="license-export",
        vendor="Adobe",
        service="Creative Cloud",
        amount=180.00,
        currency="USD",
        period="2026-06-01",
        cost_center="marketing",
        tags={"category": "licenses"},
        shared_splits=[],
    ),
    CostItem(
        source="manual-upload",
        vendor="Shared Services",
        service="Finance Tools",
        amount=300.00,
        currency="USD",
        period="2026-06-01",
        tags={"category": "other"},
        shared_splits=[
            {"entity": "finance", "weight": 2},
            {"entity": "operations", "weight": 1},
        ],
    ),
]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "finops-tool"}


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(render_dashboard_page(settings=settings, discovery=_discovery_service(), report=_report_payload()))


@app.get("/ui", response_class=HTMLResponse)
def ui() -> HTMLResponse:
    return HTMLResponse(render_dashboard_page(settings=settings, discovery=_discovery_service(), report=_report_payload()))


@app.get("/discovery", response_class=HTMLResponse)
def discovery_page() -> HTMLResponse:
    payload = _report_payload()
    return HTMLResponse(render_discovery_page(settings=settings, discovery=_discovery_service(), report=payload))


@app.get("/reports", response_class=HTMLResponse)
def reports_page() -> HTMLResponse:
    payload = _report_payload()
    return HTMLResponse(render_reports_page(settings=settings, discovery=_discovery_service(), report=payload))


@app.get("/classify-ui", response_class=HTMLResponse)
def classify_page() -> HTMLResponse:
    payload = _report_payload()
    return HTMLResponse(render_classify_page(settings=settings, discovery=_discovery_service(), report=payload))


@app.get("/config", response_class=HTMLResponse)
def config_page() -> HTMLResponse:
    payload = _report_payload()
    return HTMLResponse(render_config_page(settings=settings, discovery=_discovery_service(), report=payload))


@app.post("/config/apply")
def apply_config(
    company_name: str = Form(...),
    currency: str = Form(...),
    default_category: str = Form(...),
    supported_categories: str = Form(...),
    aws_enabled: bool = Form(False),
    aws_org_id: str = Form(""),
    aws_region: str = Form(""),
    aws_children: str = Form(""),
    azure_enabled: bool = Form(False),
    azure_org_id: str = Form(""),
    azure_region: str = Form(""),
    azure_children: str = Form(""),
    gcp_enabled: bool = Form(False),
    gcp_org_id: str = Form(""),
    gcp_region: str = Form(""),
    gcp_children: str = Form(""),
) -> RedirectResponse:
    def split_csv(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    settings.company_name = company_name
    settings.currency = currency
    settings.default_category = default_category
    settings.supported_categories = split_csv(supported_categories)
    settings.discovery.aws = {
        "enabled": aws_enabled,
        "org_id": aws_org_id or None,
        "region": aws_region or "us-east-1",
        "subscription_ids": split_csv(aws_children),
    }
    settings.discovery.azure = {
        "enabled": azure_enabled,
        "tenant_id": azure_org_id or None,
        "region": azure_region or None,
        "subscription_ids": split_csv(azure_children),
    }
    settings.discovery.gcp = {
        "enabled": gcp_enabled,
        "organization_id": gcp_org_id or None,
        "region": gcp_region or None,
        "project_ids": split_csv(gcp_children),
    }
    return RedirectResponse(url="/config", status_code=303)


@app.get("/settings")
def get_settings() -> dict:
    return {
        "company_name": settings.company_name,
        "currency": settings.currency,
        "supported_categories": settings.supported_categories,
        "allocation_rules": [rule.__dict__ for rule in settings.allocation_rules],
        "discovery": settings.discovery.__dict__,
    }


@app.get("/discovery/snapshot")
def discovery_snapshot() -> dict:
    snapshot = _discovery_service().discover()
    return {
        "accounts": [account.__dict__ for account in snapshot.accounts],
        "cost_items": [item.model_dump() for item in snapshot.cost_items],
    }


@app.post("/classify", response_model=list[AllocationResult])
def classify_costs(items: list[CostItem]) -> list[AllocationResult]:
    results: list[AllocationResult] = []
    for item in items:
        classified = classifier.classify(item)
        results.append(allocator.allocate(classified))
    return results


@app.get("/demo/report")
def demo_report() -> dict:
    return _report_payload()
