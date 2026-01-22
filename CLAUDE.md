# Client Timelines

Timeline visualization for tracking consulting engagement milestones, stakeholders, and deliverables.

## Architecture

**Static-first, config-driven design:**
- Single source of truth: [config.json](config.json) (12KB JSON file)
- Python generator: [generate_timeline.py](generate_timeline.py) parses config → produces 3 derivative files
- No build process: [index.html](index.html) works offline, client-side only (Mermaid.js via CDN)
- Version control first: All changes committed to git for audit trail

**Why this architecture?**
- Fast iteration: Edit config.json, run Python, commit
- Stakeholder-friendly: Embeddable Mermaid diagrams work in Notion, GitHub, HTML
- Offline-capable: No backend required, static hosting compatible
- Investor narrative: Tracks metrics for capital fundraising readiness

## External Integrations

**Notion API (optional sync):**
- Token in [.claude/settings.local.json](.claude/settings.local.json#L3)
- Target: "AI Sales Enablement Assessment" workspace
- Pattern: GitHub = source of truth, Notion = daily-use interface

**Git workflow:**
- Remote: https://github.com/pqsoccerboy17/client-timelines.git
- Auto-commit enabled via Claude Code settings
- Single branch per client (currently: main for EasyVista)

## Data Model Constraints

**Stakeholder status model** (5 states):
- `engaged` ✓ - Committed, scheduled meetings
- `scheduled` 📅 - Call booked
- `outreach_sent` 📧 - Waiting for response
- `cold` - Not yet contacted
- `risk` ⚠️ - Adoption resistance (e.g., Rod prefers ChatGPT over Loopio)

**Regional scoping** (affects rollout strategy):
- DACH (Germany/Austria/Switzerland): Dripify pilot, works council constraints
- US: Baseline validation
- France: Secondary rollout phase

## Operational Context

**Current engagement:** Q1 2026 EasyVista consulting (67 days to deadline)
**Milestone gating:** Mar 7 Go/No-Go decision, Mar 31 hard stop
**Budget allocation:** $10-15K across 3 workstreams (Dripify, Loopio, Tech DD)

See [TEMPLATE-README.md](TEMPLATE-README.md) for update workflow and schema documentation.
