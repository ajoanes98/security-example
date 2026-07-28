# Workshop / PoC templates

## Crear Proyecto (Port workflows)

Customer-ready **Crear Proyecto** template (parent flow + FinOps / TF / TF J2C / SRE / security / add-infra subprocesses) lives under [`port/`](port/README.md).

- Apply with [`port/scripts/apply.sh`](port/scripts/apply.sh)
- Handoff checklist: [`port/docs/HANDOFF.md`](port/docs/HANDOFF.md)
- Architecture: [`port/docs/ARCHITECTURE.md`](port/docs/ARCHITECTURE.md)

## Security & Compliance workshop example

Dummy **payments gateway** service used to demo the **Security & Compliance** scorecard.

This repo is intentionally **Gold** on Security so attendees can change one rule and see the agentic fix workflow fire.

### Scorecard mapping

| Level | Rule | Evidence in this repo |
|-------|------|------------------------|
| Bronze | `require_codeowners` | `CODEOWNERS` |
| Silver | `require_branch_protection` | `.github/branch-protection.json` |
| Gold | `no_secrets_in_config` | Clean `config/service.env` (no hardcoded secrets) |

### Suggested workshop degrade

```bash
# Remove CODEOWNERS, then patch Port entity has_codeowners=false
rm CODEOWNERS
```

Or trigger a dry-run from Actions → **Port Agentic Scorecard Fixer** → `require_codeowners`.

### Port entity

`example-security-service` — set `repository_url` to this repo after publish.
