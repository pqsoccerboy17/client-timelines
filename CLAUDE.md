# Client Timelines

Timeline visualization for tracking consulting engagement milestones, stakeholders, and deliverables.

## Tool Preferences (Yelin.io / EasyVista)

> Full details: [memory/context/tools.md](memory/context/tools.md)

**Default Connectors:**
- **Email:** Microsoft 365 (Outlook) — `michael@yelin.io`
- **Calendar:** Microsoft 365 (Outlook) — `michael@yelin.io`
- **Database/CRM:** Notion — "AI Sales Enablement Assessment" workspace
- **Chat:** Microsoft Teams (for EasyVista communications)
- **Meeting Notes:** Granola → auto-syncs to Notion "Granola Notes" database

**When running sales skills (daily-briefing, call-prep, account-research, etc.):**
- Always use O365 tools (`outlook_email_search`, `outlook_calendar_search`) instead of Gmail/GCal
- **CRITICAL: Search Sent Items too** — Critical decisions are often in emails I sent
- Pull pipeline data from Notion when available
- Search Teams chat for EasyVista-related threads
- Check Notion "Granola Notes" for meeting transcripts (not email)

**Multi-System Sync Requirement:**
When updating project status, sync ALL THREE systems:
1. **Notion** (EasyVista Main) → Primary UI
2. **config.json** → Source of truth for timeline
3. **GitHub Pages** → `git push` to update dashboard

## Architecture

**Static-first, config-driven design:**
- Single source of truth: [config.json](config.json) (12KB JSON file)
- Python generator: [generate_timeline.py](generate_timeline.py) parses config → produces 4 derivative artifacts
- No build process: [index.html](index.html) works offline, client-side only (Mermaid.js via CDN)
- Version control first: All changes committed to git for audit trail

**Why this architecture?**
- Fast iteration: Edit config.json, run Python, commit
- Stakeholder-friendly: Embeddable Mermaid diagrams work in Notion, GitHub, HTML
- Offline-capable: No backend required, static hosting compatible
- Investor narrative: Tracks metrics for capital fundraising readiness

## Update Workflow (CRITICAL)

**When updating stakeholder statuses or any config.json data:**
1. Edit [config.json](config.json) only (never edit derivative files directly)
2. Run `python3 generate_timeline.py`
3. Review changes: `git diff`
4. Commit all modified files together

**What generate_timeline.py updates automatically:**
- [easyvista-gantt.mermaid](easyvista-gantt.mermaid) - Gantt chart visualization
- [easyvista-stakeholders.mermaid](easyvista-stakeholders.mermaid) - Stakeholder map with status icons
- [easyvista-timeline.md](easyvista-timeline.md) - Markdown timeline document
- [index.html](index.html) - Stakeholder class assignments for visual colors (lines 792-796)

**⚠️ NEVER manually edit stakeholder colors in index.html** - The script syncs them automatically from config.json to prevent mismatches between data and visualization.

## External Integrations

**Notion API (optional sync):**
- Token in [.claude/settings.local.json](.claude/settings.local.json#L3)
- Target: "AI Sales Enablement Assessment" workspace
- Pattern: GitHub = source of truth, Notion = daily-use interface

**Git workflow (dual-remote setup):**
- **origin** (dev): `git@github.com:pqsoccerboy17/EasyVista.git` — Mike's personal dev repo
- **production**: `git@github.com:yelin-io/EasyVista.git` — Client-facing org repo
- Default push: `git push` → pushes to **origin** (dev)
- Production deploy: `git push production main` → pushes to **yelin-io** org
- Auto-commit enabled via Claude Code settings
- Branch: main
- **Mike is not a developer** — always run git commands for him, don't just show them

## Data Model Constraints

**Stakeholder status model** (5 states):
- `engaged` ✓ - Committed, scheduled meetings
- `scheduled` 📅 - Call booked
- `outreach_sent` 📧 - Waiting for response
- `cold` - Not yet contacted
- `risk` ⚠️ - Adoption resistance (e.g., Rod prefers ChatGPT over Loopio)

**Regional scoping** (affects rollout strategy):
- DACH (Germany/Austria/Switzerland): Lemlist pilot, works council constraints
- US: Baseline validation
- France: Secondary rollout phase

## Operational Context

**Current engagement:** Q1 2026 EasyVista consulting (67 days to deadline)
**Milestone gating:** Mar 7 Go/No-Go decision, Mar 31 hard stop
**Budget allocation:** $10-15K across 3 workstreams (Lemlist, Loopio, Tech DD)

See [TEMPLATE-README.md](TEMPLATE-README.md) for update workflow and schema documentation.
