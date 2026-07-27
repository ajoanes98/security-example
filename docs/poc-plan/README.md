# Port POC plan — Create repository & configure pipeline

PDF plans (phases, epics, and user stories) derived from the customer UML sequence diagram, including a single-workflow architecture diagram with approval gates.

| Document | Language | File |
|---|---|---|
| Port POC Plan | English | [port-poc-create-repo-pipeline-plan-en.pdf](./port-poc-create-repo-pipeline-plan-en.pdf) |
| Plan de POC en Port | Español | [port-poc-crear-repositorio-pipeline-plan-es.pdf](./port-poc-crear-repositorio-pipeline-plan-es.pdf) |
| Architecture diagram (PNG) | — | [architecture-single-workflow.png](./architecture-single-workflow.png) |
| Architecture diagram (Mermaid source) | — | [architecture-single-workflow.mmd](./architecture-single-workflow.mmd) |

## Regenerate

```bash
pip install fpdf2 pillow
# optional: refresh the PNG from Mermaid
npx --yes @mermaid-js/mermaid-cli@11.4.2 \
  -i docs/poc-plan/architecture-single-workflow.mmd \
  -o docs/poc-plan/architecture-single-workflow.png \
  -b white -s 2
python3 docs/poc-plan/generate_poc_pdfs.py
```

Requires DejaVu Sans fonts at `/usr/share/fonts/truetype/dejavu/` (common on Linux).
