# Workshop Example — Security & Compliance

Dummy **payments gateway** service used to demo the **Security & Compliance** scorecard.

This repo is intentionally **Gold** on Security so attendees can change one rule and see the agentic fix workflow fire.

## Scorecard mapping

| Level | Rule | Evidence in this repo |
|-------|------|------------------------|
| Bronze | `require_codeowners` | `CODEOWNERS` |
| Silver | `require_branch_protection` | `.github/branch-protection.json` |
| Gold | `no_secrets_in_config` | Clean `config/service.env` (no hardcoded secrets) |

## Suggested workshop degrade

```bash
# Remove CODEOWNERS, then patch Port entity has_codeowners=false
rm CODEOWNERS
```

Or trigger a dry-run from Actions → **Port Agentic Scorecard Fixer** → `require_codeowners`.

## Port entity

`example-security-service` — set `repository_url` to this repo after publish.
