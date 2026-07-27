# Trigger Spacelift Stack (EU) — Option 2 local apply

Port-as-code for [Trigger a Spacelift stack](https://docs.port.io/guides/all/trigger-spacelift-stack/), adapted for Stark Industries (EU). Cloud Port MCP OAuth was unavailable in the agent session, so this package applies the same resources via the Port REST API.

## What this creates

| Resource | Identifier |
|---|---|
| Blueprint | `space_lift_stack` (relations: `github_repository`, `service`, `owning_team`, `environment`) |
| Mock entity | `mock-spacelift-stack` → repo/service `devops-capstone-project`, team `example_team`, env `staging` |
| Self-service action | `trigger_spacelift_stack` |
| Self-service action | `refresh_spacelift_token` |
| Automation | `spacelift_token_refresh_sync` |

Note: the repo relation is named `github_repository` because the blueprint already has a string property `repository` (identifiers must be unique across properties and relations).

Spacelift GraphQL URLs are placeholders: `https://PLACEHOLDER.app.spacelift.io/graphql`.

## Prerequisites

1. Port EU org credentials (Profile → Credentials → Client ID / Client Secret).
2. `curl` and `jq` installed.

## Apply

```bash
export PORT_CLIENT_ID='...'
export PORT_CLIENT_SECRET='...'
./port/guides/trigger-spacelift-stack/apply.sh
```

Uses `https://api.port.io/v1` (EU / `app.port.io`).

## Skipped (same as Option 2 plan)

- Org secrets `SPACELIFT_API_KEY_ID`, `SPACELIFT_API_KEY_SECRET`, `SPACELIFT_TOKEN` — add in UI (Credentials → Secrets).
- Live `runTrigger` / Spacelift webhook ingest — deferred until real Spacelift credentials exist.
- Do **not** execute `trigger_spacelift_stack` until secrets + real GraphQL URL are set.

## After apply — finish E2E later

1. Profile → Credentials → Secrets → add the three `SPACELIFT_*` secrets.
2. Edit both actions and replace `PLACEHOLDER` with your Spacelift account slug.
3. Replace or keep the mock stack; ingest real stacks when ready.
4. Self-serve → Trigger Spacelift Stack → select a stack → Execute.
