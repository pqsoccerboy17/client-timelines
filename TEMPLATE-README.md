# Client Engagement Timeline Template

## Quick Start
1. Copy `config.json` → update client data
2. Run generator OR manually replace `{{placeholders}}`
3. Files auto-reference each other

## File Structure
```
/templates/
├── config.json          # Client data (single source of truth)
├── timeline.md          # Master doc (pulls from config)
├── timeline.html        # Interactive dashboard
├── gantt.mermaid        # Gantt chart (embed in Notion/HTML)
├── stakeholders.mermaid # Org chart
└── TEMPLATE-README.md   # This file
```

## Data Flow
```
config.json → md/html/mermaid files → Notion sync (optional)
     ↓
  GitHub (version control)
```

## Config Schema (config.json)
```json
{
  "client": {
    "name": "ClientName",
    "contact": "Name",
    "email": "x@x.com",
    "deadline": "YYYY-MM-DD",
    "budget": "$XX-XXK"
  },
  "team": {
    "lead": "Mike",
    "partner": "Henry",
    "engineer": "Russell"
  },
  "workstreams": [
    {
      "name": "Workstream 1",
      "goal": "...",
      "scope": "...",
      "phases": [...]
    }
  ],
  "stakeholders": [...],
  "risks": [...],
  "milestones": [...]
}
```

## Storage Options

### Option A: Local + GitHub (Recommended)
- Store in `~/Projects/client-timelines/`
- Git repo for version history
- Branch per client or folder per client

### Option B: Notion-Primary
- Create from template in Notion
- Export mermaid/html as needed
- Less version control

### Option C: Hybrid (Best for YourCo)
- **config.json** → GitHub (source of truth)
- **Notion page** → linked/synced for daily use
- **HTML/mermaid** → generated on demand

## Notion Integration
1. Create "Client Timelines" database in Operations Hub
2. Template button creates new timeline page
3. Embed mermaid charts via code blocks
4. Link to GitHub for file downloads

## Update Workflow
1. Edit config.json with changes
2. Regenerate files (or manual edit)
3. Commit to git
4. Update Notion if needed

## Placeholder Syntax
- `{{CLIENT_NAME}}` - client name
- `{{DEADLINE}}` - target date
- `{{LEAD}}` - project lead
- `{{WORKSTREAM_1_NAME}}` - dynamic workstream

## Version History
| Date | Change | Author |
|------|--------|--------|
| 2026-01-21 | Initial template from EasyVista | Mike |
