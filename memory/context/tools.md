# Tool Preferences & Integrations

> This file tells Claude which tools to use by default for Yelin.io / EasyVista work.

## Email & Calendar

| Function | Tool | Account | Notes |
|----------|------|---------|-------|
| **Email (Primary)** | Microsoft 365 | michael@yelin.io | Use `outlook_email_search`, NOT Gmail |
| **Calendar (Primary)** | Microsoft 365 | michael@yelin.io | Use `outlook_calendar_search`, NOT GCal |
| **Email (Personal)** | Gmail | michaelduncan17@gmail.com | Only for personal items |

**Critical:** When running sales skills (daily-briefing, call-prep, etc.), ALWAYS:
1. Search **Sent Items** in addition to Inbox — sent emails contain critical context
2. Use MS365 tools first, Gmail only as fallback for personal items
3. Include emails from the past 7 days minimum for full context

## Database & CRM

| Function | Tool | Workspace | Notes |
|----------|------|-----------|-------|
| **CRM/Pipeline** | Notion | "AI Sales Enablement Assessment" | Primary system of record |
| **Meeting Notes** | Granola → Notion | Auto-syncs to "Granola Notes" database | Notes appear automatically after meetings |
| **Client Timeline** | GitHub Pages + config.json | mikeduncan17.github.io/client-timelines | Visual dashboard |

**Notion Structure:**
- `EasyVista Main` — Hub page with workstreams, contacts, critical dates
- `Granola Notes` — Auto-synced meeting transcripts
- `AI Sales Enablement Assessment` — Project details

## Chat & Communication

| Function | Tool | Notes |
|----------|------|-------|
| **EasyVista Team** | Microsoft Teams | Search for EasyVista-related threads |
| **Internal (Yelin.io)** | Email (MS365) | Henry, Russell communications |

## File & Document Management

| Function | Tool | Location |
|----------|------|----------|
| **Shared Docs** | OneDrive/SharePoint | Via MS365 connector |
| **Local Project Files** | ~/Projects/EasyVista | Git-tracked config.json |
| **Attachments** | MS365 email attachments | Action trackers, templates |

## Sync Workflow (EasyVista)

When updating project status, sync ALL THREE systems:

```
1. Notion (EasyVista Main)     → Primary UI for stakeholders
2. config.json                 → Source of truth for timeline
3. GitHub Pages                → Public dashboard
```

**Sync Command Pattern:**
```bash
# After updating config.json:
cd ~/Projects/EasyVista
python3 generate_timeline.py
git add . && git commit -m "Update: [description]" && git push
```

## Search Priorities

When gathering context for briefings or research:

| Priority | Source | What to Search |
|----------|--------|----------------|
| 1 | MS365 Inbox | Unread from key accounts |
| 2 | MS365 Sent Items | Recent actions/commitments I made |
| 3 | Notion | Pipeline status, meeting notes, stakeholders |
| 4 | MS365 Calendar | Today's meetings + recent meetings |
| 5 | Teams | Threaded discussions with EasyVista team |

## Key Accounts to Track

| Account | Primary Contacts | Domain |
|---------|-----------------|--------|
| **EasyVista** | Evan Carlson (COO), Patrice Barbedette (CEO), Chris Hult (RevOps) | @easyvista.com |
| **Yelin.io** | Henry Yelin, Russell Beggs | @yelin.io |
| **Lemlist** | Eduardo | @lemlist.com, @lempire.co |

## MS365 MCP Workflow Patterns

These are interactive workflows (Claude Code sessions), not headless automation — the correct security model for MS365 OAuth.

### Daily Briefing
1. `outlook_email_search` — Unread from @easyvista.com + Sent Items (last 3 days)
2. `outlook_calendar_search` — Today's EasyVista meetings
3. `notion-search` — Recent Granola Notes for meeting transcripts
4. Review config.json stakeholders against email activity
5. Suggest status updates if warranted

### Call Prep
1. `outlook_email_search` — Thread history with stakeholder
2. `notion-fetch` — Stakeholder details from Notion DB
3. Read config.json for current status/notes
4. Generate prep brief

### Post-Meeting Update
1. `notion-search` — Find Granola meeting note
2. Extract status changes, action items, dates
3. Update config.json
4. Run `python3 generate_timeline.py`
5. Update Notion via MCP
6. Commit & push

## Lessons Learned

1. **Always check Sent Items** — Critical decisions (like Dripify→Lemlist pivot) are often in emails I sent, not received
2. **Granola syncs to Notion** — Don't search email for meeting notes; check Notion's Granola Notes database
3. **config.json is the timeline source** — Always update this FIRST, then run generator
4. **Multi-system updates require all three** — Notion, config.json, and git push
