# Port POC plan — Create repository & configure pipeline

PDF plans (phases, epics, and user stories) derived from the customer UML sequence diagram.

| Document | Language | File |
|---|---|---|
| Port POC Plan | English | [port-poc-create-repo-pipeline-plan-en.pdf](./port-poc-create-repo-pipeline-plan-en.pdf) |
| Plan de POC en Port | Español | [port-poc-crear-repositorio-pipeline-plan-es.pdf](./port-poc-crear-repositorio-pipeline-plan-es.pdf) |

## Regenerate

```bash
pip install fpdf2
python3 docs/poc-plan/generate_poc_pdfs.py
```

Requires DejaVu Sans fonts at `/usr/share/fonts/truetype/dejavu/` (common on Linux).
