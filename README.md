# FinOps Tool

An enterprise FinOps control plane for small to mid-sized companies.

It centralizes cost taxonomy, allocation rules, and reporting so finance, operations, and engineering can classify spend across cloud, SaaS, licenses, and other vendors, then produce showback and chargeback views without needing a dedicated FinOps platform team.

## Why this exists

Most small and mid-market companies have cost data spread across cloud bills, SaaS invoices, license renewals, and spreadsheets. That makes it hard to answer basic questions like:

- Who owns this spend?
- What portion is shared across teams?
- Which costs should be shown back versus charged back?
- How much of our spend is cloud versus SaaS versus licenses?

This tool starts with a lightweight, practical FinOps model:

- The platform automatically discovers cloud orgs, accounts, subscriptions, and projects where possible.
- Admins define cost categories, owners, cost centers, and allocation rules.
- Cost items are normalized into a single taxonomy.
- Shared costs can be split across teams using configurable weights.
- Reports show spend by category, owner, environment, vendor, and allocation method.

## FinOps practices covered

- FinOps Foundation style allocation and tagging discipline
- Showback and chargeback reporting
- Shared cost allocation
- Cost ownership and accountability
- Category normalization across cloud, SaaS, licenses, and other spend
- Auditability for rule changes
- Lightweight governance for SMB and mid-market teams

## Product shape

1. The platform discovers orgs, accounts, subscriptions, and projects.
2. Finance and ops review the discovered inventory.
3. The engine pulls cost data and classifies spend automatically.
4. Reports expose category splits and chargeback totals.
5. Teams review exceptions and refine the rules.

## Current architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the system design.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn finops_tool.api:app --reload
```

### Run with Podman

```bash
podman build -t finops-tool -f Containerfile .
podman run --rm -p 8000:8000 finops-tool
```

Open:

- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Demo report: [http://127.0.0.1:8000/demo/report](http://127.0.0.1:8000/demo/report)

## Example workflow

1. Post a taxonomy configuration.
2. Upload or submit cost records.
3. Classify and allocate spend.
4. Generate summary reports.

## Repository layout

```text
FinOpsTool/
├── README.md
├── ARCHITECTURE.md
├── requirements.txt
└── finops_tool/
    ├── __init__.py
    ├── api.py
    ├── config.py
    ├── models.py
    └── services/
        ├── __init__.py
        ├── allocation.py
        └── classification.py
```

## Next step

The first version should support automatic cloud discovery, shared-cost allocation, and a simple admin-managed taxonomy stored in JSON or SQLite.