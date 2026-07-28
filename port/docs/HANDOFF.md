# Customer handoff checklist

Use this when transferring the template environment. Items marked **required** must be done before production; others can stay mocked for a sales/PoC demo.

## 0. Region note

This template defaults Port-to-Port webhook calls to **US** (`https://api.us.port.io`). For EU orgs, change those URLs to `https://api.port.io` before apply.

INPUT `notifications` blocks were removed from the JSON — the US API rejected them with a bare 422. Use separate `WEBHOOK` notify nodes (already present) or Port’s UI notification settings instead.

## 1. Port org setup (required)

- [ ] Create / choose the Port organization (EU vs US API URL).
- [ ] Invite FinOps, Ing Cloud, SRE, Security users (emails must match INPUT `responders`).
- [ ] Create API credentials for `scripts/apply.sh`.
- [ ] Create secret `customer_webhook_token` in Port (referenced by webhook `Authorization` headers). Leave unused until hooks exist.

## 2. Replace INPUT responders (required before any real run)

Search workflows for `REPLACE_` and set real emails:

| Placeholder | Workflows |
|-------------|-----------|
| `REPLACE_REQUESTER_OR_TRIAGE@example.com` | `crear_proyecto` |
| `REPLACE_FINOPS@example.com` | `finops_aprobacion` |
| `REPLACE_ING_CLOUD@example.com` | `provision_tf`, `provision_tf_j2c`, `agregar_infraestructura` |
| `REPLACE_SRE@example.com` | `incorporacion_sre` |
| `REPLACE_SECURITY@example.com` | `agregar_usuarios` |

Tip: use a shared team inbox only if that identity is a Port user; otherwise list individuals and raise `numOfResponders` if you need quorum.

## 3. Webhook catalog (customer implements)

All URLs start as `https://example.com/port-hooks/...`. Point each at your gateway (API GW, Cloud Function, Jenkins, GitHub Action dispatcher, etc.).

Suggested contract: **JSON in, JSON out**, HTTP 2xx. For boolean gates, return the fields below; if the call fails, templates default to the happy-path value noted.

### Crear proyecto

| Path | When | Expected response |
|------|------|-------------------|
| `/crear-proyecto/validate` | After form | `{ "valid": true\|false, "message": "..." }` — default valid=true on failure |
| `/crear-proyecto/already-exists` | Duplicate id | notify only |
| `/crear-proyecto/need-more-info` | INPUT notification | notify only |
| `/crear-proyecto/cancelled` | User cancel | notify only |
| `/crear-proyecto/handoff-finops` | Entity created | notify only |

### FinOps

| Path | When | Expected response |
|------|------|-------------------|
| `/finops/review-requested` | INPUT notify | notify only |
| `/finops/correct-label` | Labels wrong | apply / ticket |
| `/finops/budget-alert` | After billing | create budget alert |
| `/finops/approved` | Approved | notify only |

### Terraform (`/tf/...` and `/tf-j2c/...`)

| Path | When | Expected response |
|------|------|-------------------|
| `/fetch-repo` | Start | clone/fetch OK |
| `/check-exists` | Guard | `{ "exists": true\|false }` — default false |
| `/copy-structure` | Scaffold | OK |
| `/write-yaml` | Write config | OK (`tf-j2c` includes `network_policy: j2c`) |
| `/commit-push` | Git | OK |
| `/notify-ing-cloud` | Handoff | notify |
| `/comment-issue` | Plan reject | comment |
| `/run-pipeline` | Apply | `{ "succeeded": true\|false }` — default true |
| `/deliver-info` | Success | notify |
| `/manual-execute` | Fallback | page on-call |
| `/repair-yaml` | Repair action | OK |

### SRE

| Path | When | Notes |
|------|------|-------|
| `/sre/review-owner` | J2C | optional validation |
| `/sre/attach-monitoring-j2c` | J2C | |
| `/sre/attach-gservicio` | J2C (fsoto) | rename to real system |
| `/sre/attach-invtransversal` | J2C (cmartinez) | |
| `/sre/attach-afp-monitoring` | J2C (VGodoy) | |
| `/sre/generate-monitoring-json` | J2C | `{ "monitoring_json": "..." }` |
| `/sre/notify-sre` | Review | |
| `/sre/notify-sre-non-j2c` | Non-J2C | |

### Security / add infra

| Path | When |
|------|------|
| `/security/prepare-grants` | Before approval |
| `/security/deliver-permissions` | After approval |
| `/security/grants-rejected` | Rejected |
| `/infra/create` | Scaffold additive infra |
| `/infra/notify-ing-cloud` | Review |
| `/infra/run-pipeline` | `{ "succeeded": true\|false }` |
| `/infra/deliver` | Done |
| `/infra/plan-rejected` | Rejected |

## 4. Async pipelines (recommended later)

Template webhooks use `synchronized: true` for simplicity. For long TF pipelines:

1. Set `synchronized: false` on `ejecutar_pipeline` / `run_pipeline`.
2. Have the pipeline callback Port to complete the node run (`PATCH` workflow node run — see Port workflows docs).
3. Optionally set `onTimeout: continue` while testing.

## 5. ServiceNow front door (optional)

Today **Crear Proyecto** is the Port form. To keep SNOW as the entry:

- SNOW creates/updates a `cloud_project` (or a request entity) via Port API, **or**
- Add an `EVENT_TRIGGER` sibling on `crear_proyecto` / a thin ingestion workflow that upserts `pending_finops`.

Do not remove the self-service form until SNOW mapping is proven.

## 6. Permissions to tighten later

Self-service triggers currently allow `Member` + `Admin`. After PoC:

- Restrict **Crear Proyecto** to requester roles/teams.
- Restrict repair/requeue actions to platform teams.
- Keep FinOps/SRE/Ing Cloud via INPUT responders (not broad execute permission).

## 7. Smoke test script

1. Apply blueprint + workflows.
2. Run **Crear Proyecto** with a new `project_id`.
3. As FinOps: labels OK → billing → approve.
4. As Ing Cloud: accept plan (webhooks may 404; flow continues).
5. As SRE: approve → status `ready`.
6. From entity ⚡: **Agregar usuarios** (approve as Security).
7. Duplicate `project_id` → `already_exists` path.

## 8. Out of scope for this package

- Real GCP/IAM/GitHub/Terraform code
- ServiceNow catalog item
- Dashboards / scorecards
- Exact customer label taxonomy and billing account enums (add as form `enum` when known)
