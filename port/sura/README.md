# Flujos AFP — SURA (Port US)

Implementación demo de los dos golden paths AFP en **Port Workflows** (org SURA, región US).

## Qué está desplegado

### Blueprints
| Identifier | Descripción |
|---|---|
| `gcp_project` | Proyectos GCP (mock) |
| `bq_dataset` | Datasets BigQuery |
| `bq_table` | Tablas gobernadas por el flujo |
| `finops_tag` | Tags FinOps unificados (8 dimensiones) |
| `development_cell` | Células de desarrollo |

Reutiliza: `githubOrganization`, `githubRepository` (integración GitHub existente).

### Equipos (`_team`)
- `devops` — aprueba creación de repos
- `qa` — aprueba promoción QA → prod
- `ingenieria_cloud` — reservado para revisión TF
- `gobierno_de_datos` — reservado para gobierno

### Workflows
| Identifier | Categoría | Descripción |
|---|---|---|
| `create_github_repository` | AFP DevOps | Formulario → dry-run → aprobación DevOps → ejecución (webhooks placeholder) |
| `manage_bigquery_table` | AFP Datos | CRUD/review BQ con formulario shift-left (4 operaciones) |
| `promote_bq_table_to_prod` | AFP Datos | Promoción manual o automática; aprobación equipo **QA** |
| `bq_table_qa_applied_promote` | AFP Datos | Evento: tabla `applied` en QA → dispara promoción |

### Datos mock
- Proyectos: `gcp-afp-datos-dev`, `gcp-afp-datos-qa`, `gcp-afp-datos-prod`
- Datasets por proyecto (`raw_landing`, `curated`)
- Células: `zenith`, `atlas`
- Org GitHub: `gservicios-it`
- ~10 tags FinOps representativos

## Aplicar / actualizar desde código

Los JSON de workflows están en `workflows/`. Para re-aplicar en Port US usar MCP `upsert_workflow` o la API.

### Cargar tags FinOps desde Excel

```bash
pip install openpyxl requests
export PORT_CLIENT_ID=...
export PORT_CLIENT_SECRET=...
python port/sura/scripts/seed_finops_from_excel.py --file /path/to/u_tags_de_finops.xlsx
```

Normalización: minúsculas en identifier; `_` y `-` equivalentes.

## Conectar backends (fase 2)

1. **Repos GitHub**: sustituir URLs `example.com/port-hooks/afp/create-repo/*` por `INTEGRATION_ACTION` → `gservicios-it/port-automations` workflow `create-repo.yml` (WIF + Cloud Run).
2. **BigQuery**: sustituir webhooks por `CrossGH/bigquery-platform` → `manage-bq-table.yml`.
3. **Promoción automática**: configurar secreto `port_api_token` en Port para que `bq_table_qa_applied_promote` pueda invocar la API de workflows.
4. **Asignar usuarios** a equipos `devops` y `qa` en Port (Settings → Teams).

## ServiceNow

Port y SNOW pueden convivir sin sincronización bidireccional obligatoria. Mínimo viable: guardar `snow_request_number` en la entidad y crear el RITM al inicio vía webhook. Sincronizar estado de vuelta es opcional (webhook al cerrar run en Port → API SNOW).
