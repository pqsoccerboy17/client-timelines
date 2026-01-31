# Claude Knowledge Base — Mike Duncan

> **Purpose:** Persistent context for Claude across sessions. Complements project-specific docs (CLAUDE.md, easyvista-timeline.md).
> **Last Updated:** January 30, 2026 19:15 UTC
> **Version:** 2.0
> **Sync Status:** IN_SYNC (verified)
> **Notion Mirror:** [Claude Context & Knowledge Base](https://www.notion.so/2f89df26e04081a389f8d39cf29cb49d)

---

## About Mike

- **Name:** Mike Duncan
- **Email:** michaelduncan17@gmail.com
- **Location:** Austin, Texas
- **Background:** 8 years at ServiceNow (Sales/GTM), now independent consultant
- **Current Role:** Sales/GTM AI Consultant at Yelin.io

### Working Preferences
- Enjoys learning new concepts with direct coaching and facts
- Appreciates highlighting key details as needed
- Financial mentors: Charlie Munger, Warren Buffett, JL Collins
- Prefers agents and subagents for enriched outcomes
- Claude Max subscriber — leverage Claude Code and Cowork capabilities

---

## 🤖 Claude Operating Instructions

> **CRITICAL:** These instructions define how Claude should operate for Mike. Follow these protocols in every session.
> **Version:** 2.0 (Updated with resilience, atomicity, and expanded triggers)

### Agent-First Architecture

**Principle:** ALWAYS prefer spawning agents/subagents over sequential single-threaded work. This is non-negotiable.

#### Agent Decision Tree

```
IF task has 2+ independent subtasks → SPAWN PARALLEL AGENTS
IF task requires research + analysis → SPAWN research agent, THEN analyze results
IF task involves verification → SPAWN verification agent (never self-verify)
IF task touches multiple Notion pages → SPAWN agent per page (max 5 concurrent)
IF task is simple lookup (< 2 steps) → DO DIRECTLY (no agent needed)
```

#### Agent Type Selection

| Task Type | Agent | Max Concurrent | Notes |
|-----------|-------|----------------|-------|
| Notion queries | `general-purpose` | 5 | Use for multi-page fetches |
| Research/exploration | `Explore` | 3 | Quick codebase/file searches |
| Verification | `general-purpose` | 1 | Always verify complex outputs |
| Bash operations | `Bash` | 2 | Git, npm, system commands |
| Planning/architecture | `Plan` | 1 | For implementation design |

#### Resource Limits
- **Max concurrent agents:** 5 (prevent resource exhaustion)
- **Agent timeout:** 60 seconds (escalate if exceeded)
- **Retry budget:** 2 attempts per agent before failing gracefully

### Session Start Protocol

**On every new session, Claude MUST execute this sequence:**

#### Step 1: Context Fetch (with Fallback Cascade)

```
TRY: Fetch Notion page `2f89df26-e040-81a3-89f8-d39cf29cb49d`
  IF SUCCESS → Use Notion as source of truth
  IF FAIL (timeout/auth/network):
    TRY: Read local `claude-knowledge-base.md`
      IF SUCCESS → Use local file (warn: "Using cached context")
      IF FAIL:
        WARN Mike: "Operating without context. Please provide key info."
```

#### Step 2: Freshness Check

- Compare "Last Updated" timestamp to current date
- IF > 7 days stale → WARN: "Context may be outdated"
- IF > 30 days stale → REQUIRE: "Please confirm context is still valid"

#### Step 3: Deadline Scan

- Parse Critical Dates section
- Flag any deadlines within 7 days
- Highlight OVERDUE items in red

#### Step 4: New Meeting Detection

- Query Granola Notes for entries since last session
- IF new meetings found → Spawn agent to summarize key points
- Surface any action items or decisions from new meetings

#### Step 5: Confirmation Message

```
"Context loaded:
- [X] stakeholders tracked
- [Y] active workstreams
- Next deadline: [DATE] ([DAYS] days) - [EVENT]
- [Z] new meetings since last session
- Data freshness: [FRESH/STALE]"
```

### Session End Protocol

**Before ending any substantive session, execute this sync sequence:**

#### Step 1: Change Detection

Identify ALL new information from this session:
- [ ] New contacts mentioned
- [ ] Project status changes
- [ ] New deadlines or milestones
- [ ] Decisions made
- [ ] Action items created
- [ ] Risks identified
- [ ] Budget updates

#### Step 2: Conflict Check (CRITICAL)

```
BEFORE writing:
  1. Re-fetch Notion page
  2. Compare Notion "Last Updated" vs session start time
  3. IF Notion was modified during session:
     SHOW diff to Mike
     ASK: "Notion was updated externally. Merge or overwrite?"
     WAIT for confirmation
  4. Compare local file mod time vs session start
  5. IF both changed → 3-way merge required
```

#### Step 3: Atomic Sync (Both or Neither)

```
1. Write changes to Notion (draft state)
2. IF Notion write fails → ABORT, report error, DO NOT touch local
3. Write changes to local file
4. IF local write fails → ROLLBACK Notion changes, report error
5. ONLY IF both succeed → Confirm sync complete
```

#### Step 4: Verification

- Re-read both Notion and local file
- Confirm changes persisted correctly
- Log sync in Session Log with timestamp

#### Step 5: Confirmation Message

```
"Session synced:
- Added: [list new items]
- Updated: [list changed items]
- Sync status: ✅ Both Notion and local updated
- Next session will have full context"
```

### Auto-Capture Triggers (Expanded)

**When Mike mentions these, Claude should automatically capture:**

#### Tier 1: Always Capture (High Confidence)

| Trigger | Action | Confirm? |
|---------|--------|----------|
| New person + role + company | Add to Stakeholders | No |
| Explicit deadline ("by March 31") | Add to Critical Dates | No |
| Status change ("Dripify is now live") | Update Workstreams | No |
| Decision made ("We decided to...") | Log in Session Log | No |
| Budget number mentioned | Update Budget tracking | No |

#### Tier 2: Capture with Confirmation (Medium Confidence)

| Trigger | Action | Confirm? |
|---------|--------|----------|
| Person name without role | Ask: "What's their role?" | Yes |
| Vague date ("next week") | Ask: "Specific date?" | Yes |
| Implied blocker | Ask: "Should I log as risk?" | Yes |
| Tool/software mentioned | Ask: "Add to tech stack?" | Yes |

#### Tier 3: Flag for Review (Low Confidence)

| Trigger | Action | Confirm? |
|---------|--------|----------|
| Competitor mentioned | Flag: "Log competitive intel?" | Yes |
| Pricing/budget range | Flag: "Update budget tracking?" | Yes |
| Meeting referenced | Flag: "Fetch from Granola?" | Yes |

#### NEW Triggers (Added v2.0)

| Trigger | Detection Pattern | Action |
|---------|-------------------|--------|
| Email thread reference | "email from...", "thread about..." | Link to source |
| Calendar event | "meeting on...", "call scheduled..." | Add to Critical Dates |
| Slack mention | "#channel", "in Slack..." | Flag for context |
| Success metric | Numbers + "target", "goal", "KPI" | Update Proven Results |
| Risk escalation language | "non-negotiable", "hard deadline", "must" | Flag as Critical |
| Budget change | "$" + different number than stored | Confirm and update |
| Geographic context | Country/region + project | Link to regional owner |
| Tool adoption signal | "started using", "switched to" | Update tech stack |

### Error Handling & Resilience

#### Sync Failure Recovery

```
IF Notion sync fails:
  1. Log error with timestamp
  2. Save changes to local file as backup
  3. Create `sync-pending.json` with queued changes
  4. Next session: Retry sync before proceeding
  5. After 3 failures: Alert Mike to manually verify
```

#### Data Integrity Rules

- **Never overwrite without reading first**
- **Always preserve existing data when adding**
- **Never delete without explicit confirmation**
- **Log all destructive operations**

### Tool & Integration Priorities

**Preferred tools (in order):**
1. **Notion MCP** — Primary knowledge store (source of truth)
2. **Local files** — Backup and offline access
3. **Granola Notes** — Meeting intelligence
4. **Calendar** — Deadline verification (when available)
5. **Web search** — External research
6. **Browser tools** — Last resort when MCP unavailable

**Integration Health Checks:**
- Before each session, verify Notion MCP is authenticated
- If MCP fails, notify Mike and offer alternatives
- Always check for MCP connectors before using browser automation

### Data Freshness Tracking

**Every data point should have:**
- Source (where did this come from?)
- Date added (when was it captured?)
- Last verified (when was it confirmed accurate?)
- Confidence (High/Medium/Low)

**Freshness Rules:**
- Contact info > 90 days old → Flag for verification
- Deadlines in past → Archive or confirm new date
- Workstream "In Progress" > 60 days → Check for status update

---

## Active Engagement: EasyVista

> **Detailed project docs:** See `easyvista-timeline.md` and `CLAUDE.md` in this folder

### Quick Context
- **Client:** EasyVista (mid-market ITSM software, preparing for exit)
- **Sponsor:** Evan Carlson (COO)
- **Partner:** Henry Yellen (Yelin.io founder, Paris)
- **Timeline:** Q1 2026 (hard deadline March 31)
- **Budget:** $10-15K across workstreams

### Active Workstreams

| Workstream | Status | Owner | Target |
|------------|--------|-------|--------|
| Dripify (LinkedIn) | Validation | Mike | 25-30 opps/period |
| Lupio (RFP) | Expanding | Dalila/Jan | 100% adoption by Mar 31 |
| GitHub Copilot | Complete | Engineering | All 60 devs |
| Claude Code POC | In Progress | Engineering | Legacy refactor |

### Critical Dates
- **Feb 4, 2026** — Mandatory Lupio alignment (4:30 PM France / 10:30 AM ET)
- **Feb 9, 2026** — New West BDR onboarding + Dripify training
- **Mar 7, 2026** — Dripify Go/No-Go decision
- **Mar 31, 2026** — Q1 hard deadline
- **April 2026** — Non-negotiable product release

---

## Key Stakeholders

### EasyVista Leadership
| Name | Role | Notes |
|------|------|-------|
| Patrice Barbedette | CEO | Final decision-maker |
| Evan Carlson | COO | Primary sponsor, budget approver |
| Ludovic | CTO | Engineering prioritization, "hardworking and rational" |
| Loic | VP Product | Works with Ludovic on prioritization |

### Regional Sales
| Name | Role | Region | Notes |
|------|------|--------|-------|
| Tim B | NA BDR Manager | North America | 11+ years at EasyVista, key champion |
| Sean Herbert | VP Sales | Northern Europe | Custom ChatGPT for RFPs, Gong advocate |
| Rafael Munyes | Sales Director | France | 3 SEs, 6 AMs, 3 BDRs |
| Christopher | COO | OTRS/DACH | Germany works council constraints |
| Sima | BDR | OTRS | Multilingual, Dripify pilot |
| Cédric | Sales Lead | France | Parallel dialing consideration |

### Presales/RFP Team
| Name | Role | Notes |
|------|------|-------|
| Delia | Global Head of Presales | NAM, LatAm, Europe oversight |
| Jan Mercier | France Presales Lead | 100% Lupio adoption, global knowledge owner |
| Todd Russell | US Presales | NAM point person |

### Power Users to Watch
| Name | Behavior | Implication |
|------|----------|-------------|
| Rod Schmidt | ChatGPT 100x/day instead of Lupio | Shadow IT risk; interview needed |
| Sean Herbert | Built custom ChatGPT agent for RFPs | Capture methodology for scaling |

### Consulting Team
| Name | Role | Location |
|------|------|----------|
| Henry Yellen | Yelin.io Founder | Paris |
| Russell | Engineering Consultant | Remote |
| Mike Duncan | Sales/GTM AI | Austin |

---

## Known Challenges

1. **Multi-language Lupio** — No native support; 2-3x admin overhead; Mike committed to solving by February
2. **West Territory** — No rep has ever hit quota (ServiceNow HQ competition in San Jose)
3. **Shadow IT** — Rod, Sean using personal ChatGPT/Claude instead of approved tools
4. **Regional Adoption Gaps** — France 100% vs NAM 0% on Lupio
5. **Engineering Capacity** — Too many initiatives competing for April release

---

## Proven Results (for reference)

- France Lupio: 100% adoption, 2-3x faster RFP completion
- Rod's Texas RFP: <1 hour with AI vs 4-5 hours traditional
- Developer sentiment: Shifted from job displacement fears to active AI experimentation
- GitHub Copilot: All 60 developers now have access

---

## Notion Resources

Quick-fetch these for deeper context:

| Resource | Notion ID | Use Case |
|----------|-----------|----------|
| Claude Context Page | `2f89df26-e040-81a3-89f8-d39cf29cb49d` | Full knowledge base |
| EasyVista Main | `2df9df26-e040-81d8-a08f-ebffc6a4cd80` | Project overview |
| Granola Notes | `2f89df26-e040-819a-9419-c3ec90c117ae` | Meeting history |
| Stakeholders DB | `1447853a4ae04cc2b5600879e5f97374` | Contact details |
| **Action Items DB** | `e1ff5279c9fa4d3a8a162f39213fe8eb` | Task tracking |
| **Decisions Log DB** | `127f8ebd4f1a4410a8a90db7f56a4356` | Decision audit trail |
| **Critical Dates DB** | `fbd894564cb94e63ab5885660c568a53` | Deadline calendar |

**Command:** "Fetch my Claude context from Notion" → retrieves full session continuity

### Database Usage Guide

| When... | Use This DB | Action |
|---------|-------------|--------|
| New task assigned | Action Items | Create entry with owner, due date, priority |
| Decision made | Decisions Log | Log with rationale, decision maker, status |
| New deadline | Critical Dates | Add with type, owner, prep required flag |
| Meeting scheduled | Critical Dates | Add as "Meeting" type |
| Task completed | Action Items | Update status to "Completed" |
| Decision reversed | Decisions Log | Update status to "Reversed", add rationale |

---

## Session Log

| Date | Key Actions | Notes |
|------|-------------|-------|
| 2026-01-30 | Initial knowledge base created | Consumed all Granola meetings, created Notion + local backup |
| 2026-01-30 | v2.0: Self-reflection & gap analysis | Added: sync atomicity, fallback cascades, expanded triggers, agent decision trees, error handling, data freshness tracking |
| 2026-01-30 | Loop testing & drift fix | Tested Session Start Protocol (PASS), Sync Verification (fixed drift), Notion fully synced |
| 2026-01-30 | Created supporting databases | Action Items DB, Decisions Log DB, Critical Dates DB (with 5 initial entries) |
| 2026-01-30 | Updated client-timelines site | Created config.json, marked Jan 22-24 milestones complete, added Feb 4 Loopio alignment |

---

*This file is the local backup. Primary source of truth: [Notion Claude Context Page](https://www.notion.so/2f89df26e04081a389f8d39cf29cb49d)*
