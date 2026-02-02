#!/usr/bin/env python3
"""
Timeline Generator - Creates md/html/mermaid from config.json
Usage: python generate_timeline.py [config_path] [output_dir]
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)

def generate_gantt(cfg: dict) -> str:
    """Generate mermaid gantt chart from config"""
    lines = [
        "```mermaid",
        "gantt",
        f"    title {cfg['client']['name']} {cfg['client']['deadline_label']} Timeline",
        "    dateFormat YYYY-MM-DD",
        ""
    ]

    for ws in cfg['workstreams']:
        lines.append(f"    section {ws['name']}")
        for i, phase in enumerate(ws['phases']):
            status = "active" if i == 0 else ""
            task_id = f"{ws['id']}_p{i}"
            if i == 0:
                lines.append(f"    {phase['name']} :{status}, {task_id}, {phase['start']}, {phase['end']}")
            else:
                prev_id = f"{ws['id']}_p{i-1}"
                lines.append(f"    {phase['name']} :{task_id}, after {prev_id}, {phase['end']}")
        lines.append("")

    # Milestones
    lines.append("    section Milestones")
    for m in cfg['milestones']:
        crit = "crit, " if m.get('critical') else ""
        lines.append(f"    {m['event']} :{crit}milestone, {m['date']}, 0d")

    lines.append("```")
    return "\n".join(lines)

def generate_stakeholder_map(cfg: dict) -> str:
    """Generate mermaid flowchart from stakeholders"""
    lines = [
        "```mermaid",
        "flowchart TB"
    ]

    # Group stakeholders
    groups = {}
    for s in cfg['stakeholders']:
        g = s['group']
        if g not in groups:
            groups[g] = []
        groups[g].append(s)

    for group, members in groups.items():
        lines.append(f"    subgraph {group.title()}")
        for m in members:
            status_icon = {"engaged": "✓", "outreach_sent": "📧", "risk": "⚠️", "excluded": "❌"}.get(m['status'], "")
            lines.append(f"        {m['name'].replace(' ', '_')}[\"{m['name']}<br/>{m['role']} {status_icon}\"]")
        lines.append("    end")

    lines.append("```")
    return "\n".join(lines)

def calculate_metrics(cfg: dict) -> dict:
    """Calculate progress metrics from config"""
    # Count tasks
    total_tasks = 0
    complete_tasks = 0
    for ws in cfg['workstreams']:
        for phase in ws['phases']:
            for task in phase['tasks']:
                total_tasks += 1
                if task.get('status') == 'complete':
                    complete_tasks += 1

    # Count stakeholders
    total_stakeholders = len(cfg['stakeholders'])
    engaged_stakeholders = sum(1 for s in cfg['stakeholders'] if s['status'] == 'engaged')

    # Calculate days remaining
    deadline = datetime.strptime(cfg['client']['deadline'], '%Y-%m-%d')
    days_left = (deadline - datetime.now()).days

    # Determine urgency level
    if days_left >= 60:
        urgency = 'safe'
    elif days_left >= 30:
        urgency = 'warning'
    else:
        urgency = 'critical'

    # Count risks
    risk_count = len(cfg['risks'])

    return {
        'total_tasks': total_tasks,
        'complete_tasks': complete_tasks,
        'total_stakeholders': total_stakeholders,
        'engaged_stakeholders': engaged_stakeholders,
        'days_left': days_left,
        'urgency': urgency,
        'risk_count': risk_count
    }

def update_index_html_classes(cfg: dict, index_path: str = "index.html"):
    """Update stakeholder class assignments and progress metrics in index.html"""
    import re

    with open(index_path, 'r') as f:
        html = f.read()

    # Calculate metrics
    metrics = calculate_metrics(cfg)

    # Group stakeholders by status
    status_groups = {
        'engaged': [],
        'scheduled': [],
        'outreach': [],
        'cold': [],
        'risk': []
    }

    for s in cfg['stakeholders']:
        name_key = s['name'].replace(' ', '_').replace('-', '_')
        status = s['status']

        if status == 'engaged':
            status_groups['engaged'].append(name_key)
        elif status == 'scheduled':
            status_groups['scheduled'].append(name_key)
        elif status == 'outreach_sent':
            status_groups['outreach'].append(name_key)
        elif status == 'pending':
            status_groups['cold'].append(name_key)
        elif status == 'risk':
            status_groups['risk'].append(name_key)

    # Build new class assignment lines
    new_classes = []
    if status_groups['engaged']:
        new_classes.append(f"    class {','.join(status_groups['engaged'])} engaged")
    if status_groups['scheduled']:
        new_classes.append(f"    class {','.join(status_groups['scheduled'])} scheduled")
    if status_groups['outreach']:
        new_classes.append(f"    class {','.join(status_groups['outreach'])} outreach")
    if status_groups['cold']:
        new_classes.append(f"    class {','.join(status_groups['cold'])} cold")
    if status_groups['risk']:
        new_classes.append(f"    class {','.join(status_groups['risk'])} risk")

    # Replace the class assignments section
    pattern = r'(    classDef risk fill:#f8568b,stroke:#e04477,color:#fff\n\n)(    class .*?\n)+?(?=                </div>)'
    replacement = r'\1' + '\n'.join(new_classes) + '\n'
    html = re.sub(pattern, replacement, html, flags=re.MULTILINE)

    # Update progress stats
    # Tasks complete
    html = re.sub(
        r'<span class="stat-current" id="tasks-complete">\d+</span>\s*<span class="stat-total">/ \d+</span>',
        f'<span class="stat-current" id="tasks-complete">{metrics["complete_tasks"]}</span>\n                    <span class="stat-total">/ {metrics["total_tasks"]}</span>',
        html
    )

    # Stakeholders engaged
    html = re.sub(
        r'<span class="stat-current" id="stakeholders-engaged">\d+</span>\s*<span class="stat-total">/ \d+</span>',
        f'<span class="stat-current" id="stakeholders-engaged">{metrics["engaged_stakeholders"]}</span>\n                    <span class="stat-total">/ {metrics["total_stakeholders"]}</span>',
        html
    )

    # Days remaining with urgency color
    html = re.sub(
        r'<div class="stat-number urgency-\w+" id="days-remaining">\d+</div>',
        f'<div class="stat-number urgency-{metrics["urgency"]}" id="days-remaining">{metrics["days_left"]}</div>',
        html
    )

    # Deadline banner with urgency color
    html = re.sub(
        r'<div class="deadline-banner urgency-\w+" id="deadline-banner">.*?</div>',
        f'<div class="deadline-banner urgency-{metrics["urgency"]}" id="deadline-banner">🎯 Q1 Deadline: March 31, 2026 ({metrics["days_left"]} days remaining)</div>',
        html
    )

    # Active risks count
    html = re.sub(
        r'(<div class="stat-card">\s*<div class="stat-number">)\d+(</div>\s*<div class="stat-label">Active Risks</div>)',
        rf'\g<1>{metrics["risk_count"]}\g<2>',
        html
    )

    # Update footer date
    html = re.sub(
        r'Last updated: .*? \|',
        f'Last updated: {datetime.now().strftime("%b %d, %Y")} |',
        html
    )

    with open(index_path, 'w') as f:
        f.write(html)

    print(f"✓ Updated stakeholder class assignments in {index_path}")
    print(f"  Progress: {metrics['complete_tasks']}/{metrics['total_tasks']} tasks, {metrics['engaged_stakeholders']}/{metrics['total_stakeholders']} stakeholders engaged")
    print(f"  Countdown: {metrics['days_left']} days ({metrics['urgency']})")

def generate_markdown(cfg: dict) -> str:
    """Generate full timeline markdown"""
    c = cfg['client']
    deadline = datetime.strptime(c['deadline'], '%Y-%m-%d')
    days_left = (deadline - datetime.now()).days

    md = f"""# {c['name']} Engagement Timeline
## Internal Review | {datetime.now().strftime('%B %d, %Y')}

**Contact:** {c['primary_contact']} ({c['contact_role']})
**Deadline:** {c['deadline_label']} ({c['deadline']})
**Days Remaining:** ~{days_left} days
**Budget:** ${c['budget_min']:,}-${c['budget_max']:,}

---

## Executive Summary

"""

    # Workstreams
    for ws in cfg['workstreams']:
        md += f"""## {ws['name']}

**Goal:** {ws['goal']}
**Scope:** {ws['scope']}
**Success Metric:** {ws['success_metric']}

### Phases
"""
        for phase in ws['phases']:
            md += f"\n#### {phase['name']} ({phase['start']} - {phase['end']})\n\n"
            md += "| Task | Owner | Due |\n|------|-------|-----|\n"
            for t in phase['tasks']:
                milestone = " 🎯" if t.get('milestone') else ""
                md += f"| {t['task']}{milestone} | {t['owner']} | {t['due']} |\n"
        md += "\n---\n\n"

    # Risks
    md += "## Risks\n\n| Risk | Likelihood | Impact | Mitigation |\n|------|------------|--------|------------|\n"
    for r in cfg['risks']:
        md += f"| {r['risk']} | {r['likelihood']} | {r['impact']} | {r['mitigation']} |\n"

    # Milestones
    md += "\n---\n\n## Key Milestones\n\n"
    for m in cfg['milestones']:
        crit = "🎯 " if m.get('critical') else ""
        md += f"- **{m['date']}** — {crit}{m['event']}\n"

    # Open questions
    md += "\n---\n\n## Open Questions\n\n"
    for q in cfg['open_questions']:
        md += f"- [ ] {q}\n"

    md += f"\n---\n\n*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
    return md

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    output_dir = Path(sys.argv[2] if len(sys.argv) > 2 else ".")

    cfg = load_config(config_path)
    client = cfg['client']['name'].lower().replace(' ', '-')

    # Generate files
    gantt = generate_gantt(cfg)
    stakeholders = generate_stakeholder_map(cfg)
    md = generate_markdown(cfg)

    # Write outputs
    (output_dir / f"{client}-gantt.mermaid").write_text(gantt)
    (output_dir / f"{client}-stakeholders.mermaid").write_text(stakeholders)
    (output_dir / f"{client}-timeline.md").write_text(md)

    # Update index.html stakeholder class assignments
    update_index_html_classes(cfg, output_dir / "index.html")

    print(f"✓ Generated files for {cfg['client']['name']}")
    print(f"  - {client}-gantt.mermaid")
    print(f"  - {client}-stakeholders.mermaid")
    print(f"  - {client}-timeline.md")
    print(f"  - index.html (stakeholder classes updated)")

if __name__ == "__main__":
    main()
