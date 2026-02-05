# Git Setup — EasyVista Repo

## Dual-Remote Architecture

Mike uses a two-remote setup to separate development from production:

| Remote | URL | Purpose |
|--------|-----|---------|
| **origin** | `git@github.com:pqsoccerboy17/EasyVista.git` | Dev (Mike's personal GitHub) |
| **production** | `git@github.com:yelin-io/EasyVista.git` | Production (yelin-io org, client-facing) |

## GitHub Accounts

- **Personal:** pqsoccerboy17 (Mike's GitHub username)
- **Organization:** yelin-io (company org, invited by Henry @henry-yelin-io)

## Common Commands (run these FOR Mike, don't just show them)

```bash
# Day-to-day development pushes
git push                    # pushes to origin (pqsoccerboy17)

# Deploy to production
git push production main    # pushes to yelin-io org

# Push to both
git push && git push production main

# Check remotes
git remote -v
```

## Important Notes

- Mike is NOT a developer — always execute git commands on his behalf
- SSH auth is configured on Mike's local machine (not available in Cowork sandbox)
- If a push fails in Cowork due to auth, tell Mike the exact command to run in his terminal
- Branch: main (single branch workflow)
- The yelin-io remote exists so "pqsoccerboy17" doesn't show up in client-facing URLs

## Setup History

- Feb 5, 2026: Henry invited Mike to yelin-io org
- Feb 5, 2026: Pushed all code to yelin-io/EasyVista
- Feb 5, 2026: Configured dual-remote (origin=dev, production=client-facing)
