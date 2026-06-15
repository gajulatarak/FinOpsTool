from __future__ import annotations

import json
from dataclasses import asdict
from html import escape
from typing import Iterable


NAV_ITEMS = [
    ("Dashboard", "/", "home"),
    ("Discovery", "/discovery", "radar"),
    ("Reports", "/reports", "chart"),
    ("Classify", "/classify-ui", "spark"),
    ("Config", "/config", "settings"),
    ("Docs", "/docs", "docs"),
]


def _nav(active: str) -> str:
    items = []
    for label, href, icon in NAV_ITEMS:
        cls = "nav-link active" if active == label.lower() else "nav-link"
        items.append(
            f'<a class="{cls}" href="{escape(href)}"><span class="nav-icon">{escape(icon)}</span><span>{escape(label)}</span></a>'
        )
    return "".join(items)


def _bar_rows(rows: Iterable[dict[str, object]], empty_text: str) -> str:
    rows = list(rows)
    if not rows:
        return f'<div class="empty-state">{escape(empty_text)}</div>'

    max_value = max(float(row["amount"]) for row in rows) if rows else 1.0
    cards = []
    for row in rows:
        amount = float(row["amount"])
        count = int(row.get("count", 0))
        width = 100 if max_value == 0 else (amount / max_value) * 100
        cards.append(
            f'''
            <div class="bar-row">
              <div class="bar-row-head">
                <strong>{escape(str(row["key"]))}</strong>
                <span>{amount:,.2f} • {count} items</span>
              </div>
              <div class="bar-track"><span style="width:{width:.1f}%"></span></div>
            </div>
            '''
        )
    return "".join(cards)


def _layout(
    *,
    active: str,
    title: str,
    eyebrow: str,
    headline: str,
    lead: str,
    stats: list[dict[str, str]],
    sections: list[str],
) -> str:
    stat_cards = []
    for stat in stats:
        stat_cards.append(
            f'''
            <div class="stat-card">
              <div class="stat-label">{escape(stat["label"])}</div>
              <div class="stat-value">{stat["value"]}</div>
              <div class="stat-note">{escape(stat.get("note", ""))}</div>
            </div>
            '''
        )

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #050816;
      --bg2: #0a1428;
      --panel: rgba(11, 20, 40, 0.82);
      --panel-2: rgba(18, 31, 57, 0.94);
      --line: rgba(255,255,255,0.09);
      --text: #eef4ff;
      --muted: #97abc8;
      --accent: #8de7ff;
      --accent-2: #8af2b9;
      --accent-3: #f6b86d;
      --danger: #ff8b8b;
      --shadow: 0 30px 80px rgba(0, 0, 0, 0.42);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--text);
      font-family: Inter, "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      background:
        radial-gradient(circle at 20% 0%, rgba(141, 231, 255, 0.15), transparent 25%),
        radial-gradient(circle at 80% 10%, rgba(138, 242, 185, 0.12), transparent 22%),
        linear-gradient(180deg, #040814 0%, #07101e 46%, #03050b 100%);
      min-height: 100vh;
    }}
    a {{ color: inherit; }}
    .app {{ display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }}
    .rail {{
      padding: 24px 18px;
      border-right: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(6,12,24,0.94), rgba(8,15,28,0.82));
      backdrop-filter: blur(16px);
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; margin-bottom: 26px; }}
    .brand-mark {{
      width: 42px; height: 42px; border-radius: 14px;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      box-shadow: 0 12px 30px rgba(141,231,255,0.3);
    }}
    .brand-title {{ font-size: 18px; font-weight: 800; line-height: 1.05; }}
    .brand-sub {{ font-size: 12px; color: var(--muted); margin-top: 3px; }}
    .rail-note {{ margin: 18px 0 18px; color: var(--muted); font-size: 13px; line-height: 1.5; }}
    .nav {{ display: grid; gap: 8px; margin-top: 18px; }}
    .nav-link {{
      display: grid; grid-template-columns: 24px 1fr; gap: 10px; align-items: center;
      padding: 12px 12px; border-radius: 14px; text-decoration: none;
      border: 1px solid transparent; color: #dbe6fb; background: transparent;
    }}
    .nav-link:hover {{ background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.05); }}
    .nav-link.active {{
      background: linear-gradient(135deg, rgba(141,231,255,0.18), rgba(138,242,185,0.10));
      border-color: rgba(141,231,255,0.22);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
    }}
    .nav-icon {{
      width: 24px; height: 24px; border-radius: 8px;
      display: grid; place-items: center; font-size: 12px;
      background: rgba(255,255,255,0.05); color: var(--muted);
    }}
    .rail-footer {{ margin-top: 28px; padding-top: 18px; border-top: 1px solid var(--line); color: var(--muted); font-size: 12px; line-height: 1.55; }}
    .main {{ padding: 26px; }}
    .hero {{
      display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(340px, 520px);
      gap: 18px; align-items: stretch;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 26px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }}
    .hero-main {{ padding: 28px; position: relative; overflow: hidden; }}
    .hero-main::after {{
      content: ""; position: absolute; inset: auto -50px -70px auto; width: 240px; height: 240px;
      background: radial-gradient(circle, rgba(141,231,255,0.14) 0%, rgba(141,231,255,0.02) 40%, transparent 60%);
      pointer-events: none;
    }}
    .eyebrow {{
      display: inline-flex; align-items: center; gap: 8px; text-transform: uppercase;
      letter-spacing: 0.16em; font-size: 11px; color: var(--accent);
      padding: 8px 12px; border-radius: 999px; border: 1px solid rgba(141,231,255,0.18);
      background: rgba(141,231,255,0.08);
    }}
    h1 {{ margin: 16px 0 12px; font-size: clamp(2rem, 4vw, 4.2rem); line-height: 0.98; letter-spacing: -0.04em; }}
    .lead {{ margin: 0; color: var(--muted); line-height: 1.75; font-size: 1rem; max-width: 72ch; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }}
    .chip {{
      padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,0.04);
      border: 1px solid var(--line); color: #dce8fb; font-size: 13px;
    }}
    .hero-side {{ padding: 22px; display: grid; gap: 14px; }}
    .stat-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .stat-card, .card {{
      background: var(--panel-2); border: 1px solid var(--line); border-radius: 20px; padding: 16px;
    }}
    .stat-label, .section-kicker {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; }}
    .stat-value {{ margin-top: 8px; font-size: 1.6rem; font-weight: 800; }}
    .stat-note {{ margin-top: 8px; font-size: 13px; color: var(--muted); line-height: 1.45; }}
    .section {{ margin-top: 18px; padding: 22px; }}
    .section-head {{ display: flex; justify-content: space-between; gap: 16px; align-items: end; flex-wrap: wrap; margin-bottom: 18px; }}
    .section h2 {{ margin: 0 0 6px; font-size: 1.26rem; letter-spacing: -0.02em; }}
    .section p {{ margin: 0; color: var(--muted); line-height: 1.6; }}
    .grid-2 {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }}
    .endpoint {{
      display: grid; gap: 8px; text-decoration: none; color: var(--text);
      padding: 15px; border-radius: 18px; border: 1px solid var(--line);
      background: rgba(255,255,255,0.03); transition: transform .18s ease, border-color .18s ease, background .18s ease;
    }}
    .endpoint:hover {{ transform: translateY(-2px); border-color: rgba(141,231,255,0.28); background: rgba(255,255,255,0.05); }}
    .endpoint span {{ font-weight: 700; }}
    .endpoint code, .codebox, pre {{
      color: #d9e6fa; background: rgba(0,0,0,0.24); border: 1px solid rgba(255,255,255,0.06);
      border-radius: 14px; padding: 12px; overflow: auto; white-space: pre-wrap; word-break: break-word;
    }}
    .empty-state {{
      padding: 18px; border-radius: 16px; border: 1px dashed rgba(255,255,255,0.15);
      color: var(--muted); background: rgba(255,255,255,0.02);
    }}
    .table-wrap {{ overflow: auto; border-radius: 18px; border: 1px solid var(--line); }}
    table {{ width: 100%; border-collapse: collapse; min-width: 640px; background: rgba(255,255,255,0.02); }}
    th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--line); }}
    th {{ font-size: 12px; text-transform: uppercase; letter-spacing: .09em; color: var(--muted); }}
    .bar-row {{ margin-bottom: 14px; }}
    .bar-row-head {{ display: flex; justify-content: space-between; gap: 12px; font-size: 14px; margin-bottom: 8px; }}
    .bar-row-head span {{ color: var(--muted); }}
    .bar-track {{ height: 11px; border-radius: 999px; background: rgba(255,255,255,0.06); overflow: hidden; }}
    .bar-track span {{ display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }}
    .split {{ display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr); gap: 14px; }}
    .field-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    label {{ display: grid; gap: 8px; font-size: 13px; color: var(--muted); }}
    input, select, textarea {{
      width: 100%; border-radius: 14px; border: 1px solid var(--line); background: rgba(5,12,22,0.9);
      color: var(--text); padding: 12px 14px; font: inherit;
    }}
    textarea {{ min-height: 260px; resize: vertical; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
    input[type="checkbox"] {{ width: 18px; height: 18px; accent-color: var(--accent); }}
    .toggle {{ display: flex; align-items: center; gap: 10px; }}
    .button-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }}
    .btn {{
      display: inline-flex; align-items: center; gap: 8px; cursor: pointer; text-decoration: none;
      border: 0; border-radius: 999px; padding: 12px 16px; font-weight: 800;
    }}
    .btn-primary {{ background: linear-gradient(135deg, var(--accent), var(--accent-2)); color: #05111f; }}
    .btn-secondary {{ background: rgba(255,255,255,0.06); color: var(--text); border: 1px solid var(--line); }}
    .btn-danger {{ background: rgba(255, 139, 139, 0.14); color: #ffd6d6; border: 1px solid rgba(255,139,139,0.18); }}
    .hint {{ color: var(--muted); font-size: 13px; line-height: 1.55; }}
    .screen-title {{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }}
    .screen-pill {{
      padding: 8px 12px; border-radius: 999px; background: rgba(141,231,255,0.09);
      color: var(--accent); border: 1px solid rgba(141,231,255,0.18); font-size: 12px;
    }}
    .footer-note {{ margin-top: 12px; color: var(--muted); font-size: 12px; line-height: 1.55; }}
    @media (max-width: 1180px) {{ .app {{ grid-template-columns: 1fr; }} .rail {{ border-right: 0; border-bottom: 1px solid var(--line); }} }}
    @media (max-width: 900px) {{ .hero, .grid-2, .grid-3, .grid-4, .split, .field-grid, .stat-grid {{ grid-template-columns: 1fr; }} .main {{ padding: 18px; }} }}
  </style>
</head>
<body>
  <div class="app">
    <aside class="rail">
      <div class="brand">
        <div class="brand-mark"></div>
        <div>
          <div class="brand-title">FinOps Tool</div>
          <div class="brand-sub">Control plane for SMB and mid-market spend</div>
        </div>
      </div>
      <div class="rail-note">Auto-discovery, taxonomy, allocation, and showback in one interface. Separate screens keep config, discovery, reporting, and classification cleanly isolated.</div>
      <nav class="nav">{_nav(active)}</nav>
      <div class="rail-footer">
        Designed for cloud, SaaS, license, and other spend.<br />
        Local-first today. Provider-connected next.
      </div>
    </aside>

    <main class="main">
      <div class="hero">
        <section class="panel hero-main">
          <div class="eyebrow">{escape(eyebrow)}</div>
          <h1>{escape(headline)}</h1>
          <p class="lead">{escape(lead)}</p>
          <div class="chips">
            <span class="chip">Cloud org discovery</span>
            <span class="chip">Showback / chargeback</span>
            <span class="chip">Shared-cost allocation</span>
            <span class="chip">Policy-driven config</span>
          </div>
        </section>

        <section class="panel hero-side">
          <div class="stat-grid">{''.join(stat_cards)}</div>
          <div class="card">
            <div class="section-kicker">Navigation</div>
            <div class="hint" style="margin-top:8px;">Each major workflow has its own screen. Config is separate from discovery, reports, and classification so the tool feels like a real FinOps console, not a landing page.</div>
          </div>
        </section>
      </div>

      {''.join(sections)}
    </main>
  </div>
</body>
</html>'''


def _report_snapshot_text(report: dict) -> str:
  return json.dumps(report, indent=2, default=str)


def render_dashboard_page(*, settings: object, discovery: object, report: dict) -> str:
    summary = report["summary"]
    discovery_count = len(report.get("discovery", {}).get("accounts", []))
    stats = [
        {"label": "Status", "value": "Live", "note": "API and UI running"},
        {"label": "Discovery", "value": str(discovery_count), "note": "auto-detected accounts"},
        {"label": "Spend", "value": f"${summary['total_spend']:,.2f}", "note": "sample and discovered spend"},
        {"label": "Unallocated", "value": str(summary["unallocated_count"]), "note": "needs review"},
    ]

    quick_links = "".join(
        [
            '<a class="endpoint" href="/config"><span>Open config</span><code>Separate screen for cloud providers and rules</code></a>',
            '<a class="endpoint" href="/discovery"><span>Review discovery</span><code>See orgs / accounts / projects</code></a>',
            '<a class="endpoint" href="/reports"><span>View reports</span><code>Spend, owners, and allocation</code></a>',
        ]
    )

    sections = [
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Mission control</h2>
              <p>Fast access to the core workflows the user actually needs.</p>
            </div>
            <div class="screen-pill">Dashboard</div>
          </div>
          <div class="grid-3">{quick_links}</div>
        </section>
        ''',
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Top spend mix</h2>
              <p>Live breakdown by category from the current engine output.</p>
            </div>
            <div class="screen-pill">Reports</div>
          </div>
          <div class="grid-2">
            <div class="card">{_bar_rows(summary["by_category"], "No category data available.")}</div>
            <div class="card">{_bar_rows(summary["by_owner"], "No owner data available.")}</div>
          </div>
        </section>
        ''',
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Snapshot</h2>
              <p>Config and provider readiness at a glance.</p>
            </div>
            <div class="screen-pill">JSON</div>
          </div>
          <div class="grid-2">
            <div class="card"><div class="section-kicker">Settings</div><pre>{escape(json.dumps(asdict(settings), indent=2, default=str))}</pre></div>
            <div class="card"><div class="section-kicker">Summary</div><pre>{escape(_report_snapshot_text(report))}</pre></div>
          </div>
        </section>
        ''',
    ]

    return _layout(
        active="dashboard",
        title="FinOps Tool | Dashboard",
        eyebrow="FinOps Command Center",
        headline="A premium FinOps control plane with separate screens for config, discovery, reporting, and classification.",
        lead="This dashboard is designed as a real operating console: the page is clean, the actions are grouped by workflow, and the design is meant to feel closer to a commercial FinOps product than a demo UI.",
        stats=stats,
        sections=sections,
    )


def render_discovery_page(*, settings: object, discovery: object, report: dict) -> str:
    snapshot = report.get("discovery", {})
    accounts = snapshot.get("accounts", [])
    configured = getattr(settings.discovery, "__dict__", {})
    stats = [
        {"label": "Providers", "value": str(sum(1 for k in ["aws", "azure", "gcp"] if configured.get(k, {}).get("enabled"))), "note": "enabled in config"},
        {"label": "Accounts", "value": str(len(accounts)), "note": "org / subscription / project inventory"},
        {"label": "Mode", "value": "Auto", "note": "pulls from provider APIs"},
        {"label": "Fallback", "value": "Sample", "note": "used when no providers are enabled"},
    ]

    if accounts:
        rows = "".join(
            f'<tr><td>{escape(a["provider"])}</td><td>{escape(a["account_name"])}</td><td>{escape(a["status"])}</td><td>{escape(json.dumps(a.get("metadata", {})))}</td></tr>'
            for a in accounts
        )
        table = f'''
        <div class="table-wrap">
          <table>
            <thead><tr><th>Provider</th><th>Account</th><th>Status</th><th>Metadata</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        '''
    else:
        table = '''
        <div class="empty-state">
          No cloud accounts or projects are currently enabled. Open the config screen and switch on AWS, Azure, or GCP discovery to pull inventory automatically.
        </div>
        '''

    sections = [
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Discovered inventory</h2>
              <p>Organization, subscription, or project records pulled from provider adapters.</p>
            </div>
            <div class="screen-pill">Discovery</div>
          </div>
          {table}
        </section>
        ''',
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Enabled source configuration</h2>
              <p>These are the controls that decide what the adapters try to discover.</p>
            </div>
            <div class="screen-pill">Settings</div>
          </div>
          <div class="grid-3">
            <div class="card"><div class="section-kicker">AWS</div><pre>{escape(json.dumps(configured.get("aws", {}), indent=2, default=str))}</pre></div>
            <div class="card"><div class="section-kicker">Azure</div><pre>{escape(json.dumps(configured.get("azure", {}), indent=2, default=str))}</pre></div>
            <div class="card"><div class="section-kicker">GCP</div><pre>{escape(json.dumps(configured.get("gcp", {}), indent=2, default=str))}</pre></div>
          </div>
        </section>
        ''',
    ]

    return _layout(
        active="discovery",
        title="FinOps Tool | Discovery",
        eyebrow="Automatic Discovery",
        headline="Org and account inventory from AWS, Azure, and GCP.",
        lead="This screen is where the platform shows what it can pull automatically from cloud providers. It replaces manual account entry with a live source-of-truth view.",
        stats=stats,
        sections=sections,
    )


def render_reports_page(*, settings: object, discovery: object, report: dict) -> str:
    summary = report["summary"]
    stats = [
        {"label": "Total spend", "value": f"${summary['total_spend']:,.2f}", "note": "from current allocation run"},
        {"label": "Categories", "value": str(len(summary["by_category"])), "note": "cloud, SaaS, licenses, other"},
        {"label": "Owners", "value": str(len(summary["by_owner"])), "note": "teams and cost centers"},
        {"label": "Unallocated", "value": str(summary["unallocated_count"]), "note": "requires policy review"},
    ]

    sections = [
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Showback / chargeback</h2>
              <p>Category and owner splits generated by the allocation engine.</p>
            </div>
            <div class="screen-pill">Reports</div>
          </div>
          <div class="grid-2">
            <div class="card"><div class="section-kicker">By category</div>{_bar_rows(summary["by_category"], "No category data available.")}</div>
            <div class="card"><div class="section-kicker">By owner</div>{_bar_rows(summary["by_owner"], "No owner data available.")}</div>
          </div>
        </section>
        ''',
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Allocation summary</h2>
              <p>Useful for finance, engineering, and business review.</p>
            </div>
            <div class="screen-pill">Audit</div>
          </div>
          <div class="grid-2">
            <div class="card"><div class="section-kicker">Summary JSON</div><pre>{escape(json.dumps(summary, indent=2))}</pre></div>
            <div class="card"><div class="section-kicker">Allocations JSON</div><pre>{escape(json.dumps(report.get("items", []), indent=2, default=str))}</pre></div>
          </div>
        </section>
        ''',
    ]

    return _layout(
        active="reports",
        title="FinOps Tool | Reports",
        eyebrow="FinOps Reporting",
        headline="Showback and chargeback views built for small teams that still need control.",
        lead="The reporting screen keeps spend visible in a way that finance and engineering can use quickly: by category, by owner, and by allocation output.",
        stats=stats,
        sections=sections,
    )


def render_classify_page(*, settings: object, discovery: object, report: dict) -> str:
    default_input = json.dumps(
        [
            {
                "source": "cloud-billing",
                "vendor": "AWS",
                "service": "S3",
                "amount": 155.25,
                "currency": "USD",
                "period": "2026-06-01",
                "tags": {"category": "cloud"},
                "shared_splits": [],
            }
        ],
        indent=2,
    )

    demo_input = json.dumps(
        [
            {
                "source": "cloud-billing",
                "vendor": "AWS",
                "service": "EC2",
                "amount": 1240.5,
                "currency": "USD",
                "period": "2026-06-01",
                "tags": {"category": "cloud"},
                "shared_splits": [],
            },
            {
                "source": "saas-invoice",
                "vendor": "Slack",
                "service": "Business+",
                "amount": 420,
                "currency": "USD",
                "period": "2026-06-01",
                "tags": {"category": "saas"},
                "shared_splits": [],
            },
        ],
        indent=2,
    )

    stats = [
        {"label": "Inputs", "value": "JSON", "note": "paste spend records"},
        {"label": "Rules", "value": str(len(settings.allocation_rules)), "note": "allocation policies"},
        {"label": "Categories", "value": str(len(settings.supported_categories)), "note": "cloud, SaaS, licenses, other"},
        {"label": "Mode", "value": "Live", "note": "calls /classify"},
    ]

    rule_list = "".join(
        f'<div class="card"><div class="section-kicker">{escape(rule.name)}</div><div class="hint" style="margin-top:8px;">{escape(rule.category)} • {escape(rule.owner)} • {escape(rule.allocation_method)}</div><div class="codebox" style="margin-top:10px;">{escape(json.dumps(asdict(rule), indent=2, default=str))}</div></div>'
        for rule in settings.allocation_rules
    )

    sections = [
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Classification lab</h2>
              <p>Paste one or more cost items and classify them using the current allocation rules.</p>
            </div>
            <div class="screen-pill">Classifier</div>
          </div>
          <div class="split">
            <div class="card">
              <label>Cost items JSON
                <textarea id="inputBox">{escape(default_input)}</textarea>
              </label>
              <div class="button-row">
                <button class="btn btn-primary" type="button" onclick="runClassify()">Classify spend</button>
                <button class="btn btn-secondary" type="button" onclick="loadDemo()">Load demo data</button>
                <a class="btn btn-secondary" href="/config">Open config</a>
              </div>
              <div class="footer-note">Manual input is still available for testing, but in normal use the data should come from provider discovery and exports.</div>
            </div>
            <div class="card">
              <div class="section-kicker">Classification result</div>
              <pre id="resultBox">Waiting for input...</pre>
            </div>
          </div>
        </section>
        ''',
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Rule order</h2>
              <p>How the engine decides category and ownership in practice.</p>
            </div>
            <div class="screen-pill">Policy</div>
          </div>
          <div class="grid-4">{rule_list}</div>
        </section>
        ''',
    ]

    bootstrap = json.dumps(default_input)
    demo = json.dumps(demo_input)
    script = f'''
    <script>
    const DEFAULT_INPUT = {bootstrap};
    const DEMO_INPUT = {demo};

    async function runClassify() {{
      try {{
        const payload = JSON.parse(document.getElementById('inputBox').value);
        const response = await fetch('/classify', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload),
        }});
        const data = await response.json();
        document.getElementById('resultBox').textContent = JSON.stringify(data, null, 2);
      }} catch (error) {{
        document.getElementById('resultBox').textContent = String(error);
      }}
    }}

    function loadDemo() {{
      document.getElementById('inputBox').value = DEMO_INPUT;
    }}
    </script>
    '''

    page = _layout(
        active="classify",
        title="FinOps Tool | Classify",
        eyebrow="Classification Lab",
        headline="Turn raw spend into governed FinOps categories and owner allocations.",
        lead="This screen is the working lab for validation: it uses the same classifier and allocator as the dashboard, but keeps the input and output isolated in one focused view.",
        stats=stats,
        sections=sections,
    )
    return page.replace("</body>", f"{script}</body>")


def render_config_page(*, settings: object, discovery: object, report: dict) -> str:
    discovery_cfg = settings.discovery.__dict__
    stats = [
        {"label": "Company", "value": escape(settings.company_name), "note": "top-level profile"},
        {"label": "Currency", "value": escape(settings.currency), "note": "reporting currency"},
        {"label": "Providers", "value": str(sum(1 for x in ["aws", "azure", "gcp"] if discovery_cfg.get(x, {}).get("enabled"))), "note": "enabled connections"},
        {"label": "Rules", "value": str(len(settings.allocation_rules)), "note": "allocation policies"},
    ]

    provider_cards = []
    for key, label, hint in [
        ("aws", "AWS", "Organizations + Cost Explorer"),
        ("azure", "Azure", "Tenant + subscriptions"),
        ("gcp", "GCP", "Organization + projects"),
    ]:
        cfg = discovery_cfg.get(key, {})
        provider_cards.append(
            f'''
            <div class="card">
              <div class="section-kicker">{label}</div>
              <div class="hint" style="margin-top:8px;">{escape(hint)}</div>
              <div style="margin-top:12px;" class="toggle">
                <input type="checkbox" name="{key}_enabled" value="true" {"checked" if cfg.get("enabled") else ""} />
                <span>Enabled</span>
              </div>
              <div class="field-grid" style="margin-top:12px;">
                <label>{label} org / tenant / org ID
                  <input type="text" name="{key}_org_id" value="{escape(str(cfg.get('org_id') or cfg.get('tenant_id') or cfg.get('organization_id') or ''))}" placeholder="optional" />
                </label>
                <label>Region / notes
                  <input type="text" name="{key}_region" value="{escape(str(cfg.get('region') or ''))}" placeholder="optional" />
                </label>
              </div>
              <div class="field-grid" style="margin-top:12px;">
                <label>Subscriptions / projects
                  <textarea name="{key}_children" placeholder="comma-separated IDs">{escape(', '.join(cfg.get('subscription_ids') or cfg.get('project_ids') or []))}</textarea>
                </label>
              </div>
            </div>
            '''
        )

    sections = [
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Provider config</h2>
              <p>Keep cloud sources separate and editable from the main dashboard.</p>
            </div>
            <div class="screen-pill">Config</div>
          </div>
          <form method="post" action="/config/apply">
            <div class="grid-2">
              <div class="card">
                <div class="section-kicker">Company profile</div>
                <div class="field-grid" style="margin-top:12px;">
                  <label>Company name
                    <input type="text" name="company_name" value="{escape(settings.company_name)}" />
                  </label>
                  <label>Reporting currency
                    <input type="text" name="currency" value="{escape(settings.currency)}" />
                  </label>
                </div>
                <div class="field-grid" style="margin-top:12px;">
                  <label>Default category
                    <input type="text" name="default_category" value="{escape(settings.default_category)}" />
                  </label>
                  <label>Supported categories
                    <input type="text" name="supported_categories" value="{escape(', '.join(settings.supported_categories))}" />
                  </label>
                </div>
                <div class="footer-note">Edits update the live in-memory profile. This is enough for a startup/demo and can be persisted later to SQLite or JSON.</div>
              </div>
              <div class="card">
                <div class="section-kicker">Provider connections</div>
                <div class="hint" style="margin-top:8px;">Use comma-separated IDs for Azure subscriptions or GCP projects.</div>
                <div class="grid-3" style="margin-top:12px;">{''.join(provider_cards)}</div>
              </div>
            </div>
            <div class="button-row">
              <button class="btn btn-primary" type="submit">Save config</button>
              <a class="btn btn-secondary" href="/discovery">View discovery</a>
              <a class="btn btn-secondary" href="/reports">View reports</a>
            </div>
          </form>
        </section>
        ''',
        f'''
        <section class="panel section">
          <div class="section-head">
            <div>
              <h2>Current config JSON</h2>
              <p>What the app is using right now.</p>
            </div>
            <div class="screen-pill">Live</div>
          </div>
          <div class="grid-2">
            <div class="card"><div class="section-kicker">Settings</div><pre>{escape(json.dumps(asdict(settings), indent=2, default=str))}</pre></div>
            <div class="card"><div class="section-kicker">Discovery state</div><pre>{escape(json.dumps(asdict(settings.discovery), indent=2, default=str))}</pre></div>
          </div>
        </section>
        ''',
    ]

    return _layout(
        active="config",
        title="FinOps Tool | Config",
        eyebrow="Configuration",
        headline="Separate screens for company profile, cloud providers, and allocation policy.",
        lead="This screen is intentionally isolated so administrators can manage provider discovery and FinOps policy without mixing it with reporting or classification.",
        stats=stats,
        sections=sections,
    )
