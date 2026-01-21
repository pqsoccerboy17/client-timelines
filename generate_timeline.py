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

    print(f"✓ Generated files for {cfg['client']['name']}")
    print(f"  - {client}-gantt.mermaid")
    print(f"  - {client}-stakeholders.mermaid")
    print(f"  - {client}-timeline.md")

if __name__ == "__main__":
    main()
