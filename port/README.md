# Crear Proyecto — Port template

Workflow-first template that mirrors the prospect BPMN (`port-crear proyecto` + FinOps / TF / TF J2C / SRE / security / add-infra subprocesses).

Customer owns real integrations: replace `https://example.com/port-hooks/...` URLs and `REPLACE_*@example.com` INPUT responders. Until then, webhook nodes use `onFailure: continue` so the human-approval path still demos end-to-end.

## What’s included

| Path | Purpose |
|------|---------|
| `blueprints/cloud_project.json` | Catalog entity + status machine |
| `workflows/01_crear_proyecto.json` | Parent self-service |
| `workflows/02_finops_aprobacion.json` | FinOps (event on `pending_finops`) |
| `workflows/03_provision_tf.json` | Terraform non-J2C |
| `workflows/04_provision_tf_j2c.json` | Terraform J2C |
| `workflows/05_incorporacion_sre.json` | SRE onboarding |
| `workflows/06_agregar_usuarios.json` | Optional users / security |
| `workflows/07_agregar_infraestructura.json` | Optional add infra |
| `workflows/08_reparar_plan_tf.json` | TF plan repair re-entry |
| `workflows/09_requeue_finops.json` | Label-fix re-entry |
| `docs/ARCHITECTURE.md` | Status graph + design notes |
| `docs/HANDOFF.md` | Customer checklist |
| `scripts/apply.sh` | Apply blueprint + workflows via API |

## Apply

1. Create Port API credentials (**... → Credentials**).
2. Edit every workflow: replace `REPLACE_*@example.com` with real Port user emails (INPUT responders must exist in the org).
3. Optionally point webhook URLs at a mock (webhook.site) or leave placeholders for demo of approvals only.
4. Run:

```bash
export PORT_CLIENT_ID=...
export PORT_CLIENT_SECRET=...
# US orgs:
# export PORT_API_URL=https://api.us.port.io

chmod +x port/scripts/apply.sh
./port/scripts/apply.sh
```

5. In Port: **Self-Service → Crear Proyecto** and run a test. Approve FinOps / Ing Cloud / SRE inputs as the configured users.

## Status-driven chaining

Port workflows cannot fan-out from one node. Subprocesses are separate workflows chained by `cloud_project.status`:

```
crear_proyecto → pending_finops
     → finops_aprobacion → finops_approved
          → provision_tf | provision_tf_j2c → infra_created
               → incorporacion_sre → ready
```

Optional bolt-menu actions on the entity: **Agregar usuarios**, **Agregar infraestructura**, **Reparar plan TF**, **Re-encolar FinOps**.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/HANDOFF.md](docs/HANDOFF.md).
