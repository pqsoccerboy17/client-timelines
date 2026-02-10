# EasyVista Q1 2026 Engagement

Timeline tracker, client portal, and stakeholder dashboards for the EasyVista consulting engagement. Covers three workstreams: Lemlist (sales automation), Loopio (RFP standardization), and Technology Due Diligence.

## Quick Links

| Resource | Description |
|----------|-------------|
| [Client Portal](portal/index.html) | Workstream status, billing, and setup guides |
| [Internal Dashboard](index.html) | Stakeholder map and Gantt chart |
| [Lemlist Guide](portal/guides/lemlist.html) | Lemlist setup and configuration guide |
| [Loopio Guide](portal/guides/loopio.html) | Loopio standardization guide |
| [ROI Calculator](portal/roi.html) | Engagement ROI tracking |

## What's in This Repo

```
config.json                  # Source of truth for all engagement data
generate_timeline.py         # Regenerates dashboards from config
portal/                      # Client-facing portal and guides
  index.html                 # Portal home (workstream status)
  guides/                    # Setup guides (Lemlist, Loopio)
  roi.html                   # ROI calculator
  progress.html              # Progress tracker
index.html                   # Internal timeline dashboard
easyvista-gantt.mermaid      # Generated Gantt chart
easyvista-stakeholders.mermaid  # Generated stakeholder map
easyvista-timeline.md        # Generated markdown timeline
TEMPLATE-README.md           # Full schema documentation
```

## How to Update

All engagement data lives in `config.json`. Never edit the generated files directly — they get overwritten on the next run.

```bash
# 1. Edit the source of truth
#    (update statuses, dates, stakeholders, etc.)
vim config.json

# 2. Regenerate all dashboards and diagrams
python3 generate_timeline.py

# 3. Review what changed
git diff

# 4. Commit everything together
git add config.json generate_timeline.py index.html \
       easyvista-gantt.mermaid easyvista-stakeholders.mermaid \
       easyvista-timeline.md portal/
git commit -m "Update engagement status"

# 5. Deploy to production
git push production main
```

**Generated files** (do not edit manually):
- `easyvista-gantt.mermaid`
- `easyvista-stakeholders.mermaid`
- `easyvista-timeline.md`
- Stakeholder color classes in `index.html` (lines 792-796)

## Architecture

Config-driven, static-first design with no backend or build process. `config.json` is the single source of truth — a Python script generates Mermaid diagrams, a markdown timeline, and updates the HTML dashboard. Everything works offline and can be served from any static host (GitHub Pages, local file, etc.). See [TEMPLATE-README.md](TEMPLATE-README.md) for the full config schema and data model documentation.
