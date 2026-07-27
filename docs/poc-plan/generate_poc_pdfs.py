#!/usr/bin/env python3
"""Generate English and Spanish POC plan PDFs for Port repository provisioning."""

from pathlib import Path

from fpdf import FPDF
from PIL import Image

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
OUT_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = Path("/opt/cursor/artifacts")
DIAGRAM_PNG = OUT_DIR / "architecture-single-workflow.png"


class PlanPDF(FPDF):
    def __init__(self, lang: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.lang = lang
        self.set_auto_page_break(auto=True, margin=18)
        self.add_font("DejaVu", "", str(FONT_DIR / "DejaVuSans.ttf"))
        self.add_font("DejaVu", "B", str(FONT_DIR / "DejaVuSans-Bold.ttf"))
        self.add_font("DejaVu", "I", str(FONT_DIR / "DejaVuSans.ttf"))

    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(120, 120, 120)
        label = "Página" if self.lang == "es" else "Page"
        self.cell(0, 8, f"{label} {self.page_no()}/{{nb}}", align="C")

    def cover(self, title: str, subtitle: str, meta_lines: list[str]):
        self.add_page()
        self.ln(36)
        self.set_font("DejaVu", "B", 22)
        self.set_text_color(20, 40, 70)
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, 10, title, align="C")
        self.ln(6)
        self.set_font("DejaVu", "", 13)
        self.set_text_color(60, 70, 85)
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, 7, subtitle, align="C")
        self.ln(14)
        self.set_draw_color(40, 100, 160)
        self.set_line_width(0.6)
        mid = self.w / 2
        y = self.get_y()
        self.line(mid - 28, y, mid + 28, y)
        self.ln(14)
        self.set_font("DejaVu", "", 10)
        self.set_text_color(90, 90, 90)
        for line in meta_lines:
            self.set_x(self.l_margin)
            self.multi_cell(self.epw, 6, line, align="C")

    def _write(self, text: str, h: float):
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, h, text)

    def h1(self, text: str):
        self.ln(4)
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(20, 40, 70)
        self._write(text, 9)
        self.ln(1)

    def h2(self, text: str):
        self.ln(3)
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(30, 70, 120)
        self._write(text, 7)
        self.ln(1)

    def h3(self, text: str):
        self.ln(2)
        self.set_font("DejaVu", "B", 10.5)
        self.set_text_color(40, 55, 75)
        self._write(text, 6)
        self.ln(0.5)

    def body(self, text: str):
        self.set_font("DejaVu", "", 9.5)
        self.set_text_color(35, 35, 35)
        self._write(text, 5.2)
        self.ln(1.5)

    def bullet(self, text: str, indent: float = 4):
        self.set_font("DejaVu", "", 9.5)
        self.set_text_color(35, 35, 35)
        x = self.l_margin + indent
        self.set_x(x)
        width = self.w - self.r_margin - x
        self.multi_cell(width, 5.2, f"-  {text}")

    def numbered(self, n: int, text: str, indent: float = 4):
        self.set_font("DejaVu", "", 9.5)
        self.set_text_color(35, 35, 35)
        x = self.l_margin + indent
        self.set_x(x)
        width = self.w - self.r_margin - x
        self.multi_cell(width, 5.2, f"{n}.  {text}")

    def story_row(self, story_id: str, story: str, ac: str):
        if self.get_y() > 255:
            self.add_page()
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(20, 50, 90)
        self._write(f"{story_id}  -  {story}", 5)
        self.set_font("DejaVu", "", 8.5)
        self.set_text_color(50, 50, 50)
        ac_label = "Criterios de aceptación" if self.lang == "es" else "Acceptance criteria"
        self._write(f"{ac_label}: {ac}", 4.8)
        self.ln(2.5)

    def architecture_section(self):
        """Embed the single-workflow architecture diagram across as many pages as needed."""
        if self.lang == "es":
            self.h1("2. Arquitectura: un solo workflow con aprobaciones")
            self.body(
                "El recorrido completo (crear repositorio → añadir equipo → configurar "
                "pipeline/variables → añadir workflow) se modela como una sola ejecución "
                "de Port Workflow, con nodos INPUT de aprobación entre etapas de "
                "Terraform plan/apply. La fase final usa una puerta de merge de PR "
                "(o un INPUT de confirmación) en lugar del ciclo plan/apply."
            )
            self.bullet(
                "Un solo run de workflow posee todo el recorrido; cada rombo es una "
                "puerta humana."
            )
            self.bullet(
                "Las fases 1–3 comparten el patrón: Port despacha GitHub Actions → "
                "Terraform plan → INPUT de DevOps → apply."
            )
            self.bullet(
                "La fase 4 permanece en el mismo workflow, pero la puerta es el merge "
                "del PR (o un INPUT «confirmar merge»)."
            )
            self.bullet(
                "Cualquier rechazo salta a notificar/fallar para no seguir aprovisionando."
            )
            caption = "Diagrama de arquitectura — workflow único en Port"
            continued = "Diagrama de arquitectura (continuación)"
        else:
            self.h1("2. Architecture: single workflow with approvals")
            self.body(
                "The full journey (create repository → add team → configure "
                "pipeline/env vars → add workflow) is modeled as one Port Workflow "
                "run, with INPUT approval nodes between Terraform plan/apply stages. "
                "The final phase uses a PR-merge gate (or a confirmation INPUT) "
                "instead of the plan/apply loop."
            )
            self.bullet(
                "One workflow run owns the whole journey; each diamond is a human gate."
            )
            self.bullet(
                "Phases 1–3 share the same pattern: Port dispatches GitHub Actions → "
                "Terraform plan → DevOps INPUT → apply."
            )
            self.bullet(
                "Phase 4 still sits in the same workflow, but the gate is PR merge "
                "(or an INPUT “confirm merged”)."
            )
            self.bullet(
                "Decline from any approval jumps to notify/fail so provisioning stops."
            )
            caption = "Architecture diagram — single Port workflow"
            continued = "Architecture diagram (continued)"

        self._embed_tall_image(DIAGRAM_PNG, caption=caption, continued=continued)

    def _embed_tall_image(self, image_path: Path, caption: str, continued: str):
        if not image_path.exists():
            self.body(f"[Diagram missing: {image_path.name}]")
            return

        img = Image.open(image_path)
        img_w, img_h = img.size
        page_w = self.epw
        # Keep a little room for caption under each slice.
        max_h = self.h - self.b_margin - self.t_margin - 28
        # Pixel height that fits one page at full content width.
        slice_px = int(img_w * (max_h / page_w))
        slice_px = max(slice_px, 1)

        tmp_dir = OUT_DIR / "_diagram_slices"
        tmp_dir.mkdir(exist_ok=True)

        y0 = 0
        part = 0
        while y0 < img_h:
            y1 = min(y0 + slice_px, img_h)
            # Avoid tiny leftover strips: absorb into previous if very small.
            if img_h - y1 < slice_px * 0.12 and y1 < img_h:
                y1 = img_h
            crop = img.crop((0, y0, img_w, y1))
            part += 1
            slice_path = tmp_dir / f"arch-slice-{part}.png"
            crop.save(slice_path, format="PNG")

            if part == 1:
                self.ln(2)
                self.set_font("DejaVu", "B", 10)
                self.set_text_color(30, 70, 120)
                self._write(caption, 6)
            else:
                self.add_page()
                self.set_font("DejaVu", "B", 10)
                self.set_text_color(30, 70, 120)
                self._write(continued, 6)

            display_h = page_w * ((y1 - y0) / img_w)
            self.image(str(slice_path), x=self.l_margin, w=page_w, h=display_h)
            self.ln(display_h + 2)
            y0 = y1


EN = {
    "filename": "port-poc-create-repo-pipeline-plan-en.pdf",
    "title": "Port POC Plan",
    "subtitle": "Create Repository and Configure Pipeline\n(Phases, Epics & User Stories)",
    "meta": [
        "Based on the customer UML sequence diagram",
        "Orchestration: Port Workflows  ·  IaC: Terraform via GitHub Actions",
        "Document language: English",
    ],
    "sections": "sections_en",
}

ES = {
    "filename": "port-poc-crear-repositorio-pipeline-plan-es.pdf",
    "title": "Plan de POC en Port",
    "subtitle": "Crear repositorio y configurar pipeline\n(Fases, épicas e historias de usuario)",
    "meta": [
        "Basado en el diagrama de secuencia UML del cliente",
        "Orquestación: Port Workflows  ·  IaC: Terraform vía GitHub Actions",
        "Idioma del documento: Español",
    ],
}


def build_english(pdf: PlanPDF):
    pdf.h1("1. POC goal and approach")
    pdf.body(
        "Goal: Prove one end-to-end path a developer can run from Port, with DevOps "
        "approval and status back to the requester — not full production parity on day one."
    )
    pdf.body(
        "Key design choice for the POC: Use Port’s native INPUT approval node for the "
        "Terraform plan→apply gate (matches “DevOps approves in Port” in the diagram). "
        "Keep GitHub Issues as a later optional story if the customer requires "
        "issue-based tracking."
    )
    pdf.body(
        "Slice strategy: Build one vertical slice first (addRepository), then reuse the "
        "same plan→approve→apply skeleton for team and env vars. Treat addWorkflow "
        "(PR merge) as a separate final slice — or keep it in the same workflow behind "
        "a PR-merge / confirmation gate (see architecture)."
    )

    pdf.architecture_section()

    pdf.h1("3. Implementation phases")

    pdf.h2("Phase 0 — Foundations")
    pdf.numbered(1, "Connect Port ↔ GitHub (Ocean / GitHub app).")
    pdf.numbered(
        2,
        "Create a platform control repo holding Terraform modules and workflow_dispatch "
        "GitHub Actions (plan / apply).",
    )
    pdf.numbered(
        3,
        "Define minimal blueprints: service (or reuse built-in), githubRepository "
        "(from integration), optional provisioningRequest for run tracking.",
    )
    pdf.numbered(
        4,
        "Store Port credentials as GitHub secrets; use port-labs/port-github-action "
        "to report run status.",
    )

    pdf.h2("Phase 1 — Vertical slice: Create repository")
    pdf.numbered(
        1,
        "Self-service workflow form: repo name, visibility, team, template.",
    )
    pdf.numbered(
        2,
        "INTEGRATION_ACTION → GitHub Actions plan (Terraform creates repo).",
    )
    pdf.numbered(3, "INPUT node → DevOps approve / decline.")
    pdf.numbered(
        4,
        "On approve → apply workflow; on success → upsert Port entity and notify user.",
    )
    pdf.numbered(5, "Manual test with a throwaway org / sandbox.")

    pdf.h2("Phase 2 — Reuse pattern: Add team")
    pdf.numbered(1, "Second self-service action (or chained step after repo exists).")
    pdf.numbered(2, "Same plan→approve→apply against team membership Terraform.")
    pdf.numbered(3, "Relate repo ↔ team in Port ($team / relations).")

    pdf.h2("Phase 3 — Pipeline and environment variables")
    pdf.numbered(
        1,
        "Form for pipeline type and env var keys/values (secrets via GitHub Environments "
        "/ Actions secrets APIs, behind Terraform or a dedicated GHA).",
    )
    pdf.numbered(
        2,
        "Same approval loop; upsert pipeline/env metadata on the service entity.",
    )

    pdf.h2("Phase 4 — Add workflow files (PR gate)")
    pdf.numbered(
        1,
        "Port dispatches an action that opens a PR with .github/workflows/* "
        "(or scaffolds from a template).",
    )
    pdf.numbered(2, "DevOps merges in GitHub (human gate outside Port).")
    pdf.numbered(
        3,
        "Event trigger / polling / status callback updates Port when the PR is merged.",
    )
    pdf.numbered(4, "Final status notification to the requester.")

    pdf.h2("Phase 5 — Glue into one journey (optional for POC)")
    pdf.numbered(
        1,
        "Either one multi-step workflow with sequential stages, or four workflows plus "
        "a thin orchestrator that chains them via entity status events.",
    )
    pdf.numbered(
        2,
        "Dashboard: provisioning requests, pending approvals, repository catalog.",
    )

    pdf.h1("4. Suggested build order")
    pdf.numbered(1, "A1–A3 + B1–B4 — smallest demo matching UML Phase 1.")
    pdf.numbered(2, "C1–C2 — proves the pattern is reusable.")
    pdf.numbered(3, "D1–D3 — proves secrets and pipeline configuration.")
    pdf.numbered(4, "E1–E3 — proves the different approval mechanism (PR).")
    pdf.numbered(5, "F1–F2 — polish for stakeholder demo.")

    pdf.h1("5. Epics and user stories")

    pdf.h2("Epic A — Platform foundations")
    pdf.story_row(
        "A1",
        "As a platform engineer, I connect Port to our GitHub org so workflows can dispatch Actions.",
        "GitHub integration healthy; can dispatch a no-op workflow_dispatch from Port and see success.",
    )
    pdf.story_row(
        "A2",
        "As a platform engineer, I have a control repo with Terraform + plan/apply Actions that report status to Port.",
        "Plan uploads artifact; apply consumes it; both PATCH Port run logs via port-github-action.",
    )
    pdf.story_row(
        "A3",
        "As a platform engineer, I define blueprints for service / provisioning state.",
        "Entity can track status (requested → planned → approved → applied / failed) and link to GitHub repo URL.",
    )

    pdf.h2("Epic B — Create repository (addRepositorie)")
    pdf.story_row(
        "B1",
        "As a developer, I submit “Create repository” from Port with name, visibility, and owning team.",
        "Form validates inputs; run appears in Port with requester identity.",
    )
    pdf.story_row(
        "B2",
        "As the system, I run Terraform plan for the new repo and pause for approval.",
        "Plan succeeds; DevOps sees pending INPUT approval with plan summary/link; no apply yet.",
    )
    pdf.story_row(
        "B3",
        "As DevOps, I approve or decline the change in Port.",
        "Approve → apply runs; decline → run ends, user notified, no repo created.",
    )
    pdf.story_row(
        "B4",
        "As a developer, I get status when provisioning finishes.",
        "Repo exists in GitHub; Port entity updated; run status SUCCESS/FAILURE matches reality.",
    )
    pdf.h3("POC test script (B)")
    pdf.bullet("Happy path")
    pdf.bullet("Decline path")
    pdf.bullet("Plan failure path (invalid name)")

    pdf.h2("Epic C — Add team (addTeam)")
    pdf.story_row(
        "C1",
        "As a developer, I request team access on an existing repo from Port.",
        "Form selects repo entity + team; only allowed teams shown.",
    )
    pdf.story_row(
        "C2",
        "Same plan→approve→apply loop applies team permissions via Terraform.",
        "After approve, GitHub team has expected permission; Port relations/$team updated.",
    )
    pdf.h3("POC test script (C)")
    pdf.bullet("Add team")
    pdf.bullet("Decline")
    pdf.bullet("Attempt on a repo the user does not own (permission check)")

    pdf.h2("Epic D — Pipeline & env vars (addPipeline / addEnvVars)")
    pdf.story_row(
        "D1",
        "As a developer, I choose a pipeline template and env vars for a repo.",
        "Form captures non-secret + secret refs; secrets never logged in Port run output.",
    )
    pdf.story_row(
        "D2",
        "Plan/apply configures GitHub Environment / variables via Terraform or GHA.",
        "Vars present in GitHub; Port shows “pipeline configured”.",
    )
    pdf.story_row(
        "D3",
        "DevOps approval required before secrets/vars are written.",
        "No mutation until approve.",
    )
    pdf.h3("POC test script (D)")
    pdf.bullet("Staging environment only")
    pdf.bullet("Verify secret redaction in logs")

    pdf.h2("Epic E — Add workflow files (addWorkflow)")
    pdf.story_row(
        "E1",
        "As a developer, I request CI workflow scaffolding for my repo.",
        "Port creates a branch + PR with workflow YAML from a template.",
    )
    pdf.story_row(
        "E2",
        "As DevOps, I review and merge the PR in GitHub.",
        "Merge is the approval gate (as in the UML); no silent push to default branch.",
    )
    pdf.story_row(
        "E3",
        "As a developer, I see final status in Port after merge.",
        "PR merged event (or polling) updates entity; user notified.",
    )
    pdf.h3("POC test script (E)")
    pdf.bullet("Open PR → merge → Port SUCCESS")
    pdf.bullet("Open PR → close without merge → FAILED/CANCELLED")

    pdf.h2("Epic F — Journey UX & observability (thin for POC)")
    pdf.story_row(
        "F1",
        "As a developer, I can see where my request is stuck (plan / approval / apply / PR).",
        "Single run timeline or provisioningRequest entity shows stage.",
    )
    pdf.story_row(
        "F2",
        "As DevOps, I have a queue of pending approvals.",
        "Port page/widget lists open INPUT approvals.",
    )

    pdf.h1("6. Out of scope for POC")
    pdf.bullet("Full GitHub Issue–based approval mirroring the UML (use Port INPUT first).")
    pdf.bullet("Multi-org / multi-cloud Terraform backends.")
    pdf.bullet("Automated chaining of all four phases into one click without intermediate confirmation.")
    pdf.bullet("Production RBAC hardening beyond “Member can request / DevOps team can approve”.")

    pdf.h1("7. UML → Port construct mapping")
    pdf.bullet("User addRepositorie(form) → Workflow SELF_SERVE_TRIGGER")
    pdf.bullet(
        "Port → GithubAPI createRepo → Indirect via Terraform in GHA "
        "(prefer TF for plan/apply parity)"
    )
    pdf.bullet(
        "Terraform execute(plan) / execute(apply) → Two workflow_dispatch Actions + "
        "INTEGRATION_ACTION"
    )
    pdf.bullet(
        "Issues wait(approval) + DevOps sendApprove → Port INPUT node (POC); "
        "optional later: GitHub Issue + callback"
    )
    pdf.bullet(
        "waitUntilEnd / sendStatus → reportWorkflowStatus + port-github-action "
        "PATCH_RUN / entity upsert"
    )
    pdf.bullet(
        "addWorkflow + createPullRequest + Merge → GHA opens PR; human merge; "
        "Port event/status update"
    )

    pdf.h1("8. Demo script")
    pdf.numbered(
        1,
        "Developer opens Create repository in Port and submits the form.",
    )
    pdf.numbered(2, "Show GitHub Actions plan run and pending approval in Port.")
    pdf.numbered(
        3,
        "DevOps approves → apply creates repo → catalog entity appears.",
    )
    pdf.numbered(4, "Developer runs Add team, then Configure pipeline.")
    pdf.numbered(
        5,
        "Developer runs Add workflow → PR opened → DevOps merges → Port shows complete.",
    )

    pdf.h1("9. Risks to call out early")
    pdf.bullet(
        "Long-running async state: plan artifacts must be keyed by Port run ID so apply "
        "uses the correct plan."
    )
    pdf.bullet(
        "Two approval styles: Issue-based (UML) vs Port INPUT vs PR merge — align with "
        "the customer before building Issue automation."
    )
    pdf.bullet(
        "Workflows are open beta: prefer Workflows for new multi-step logic; legacy "
        "Actions & Automations remain supported if already in use."
    )
    pdf.bullet(
        "Secrets: never put secret values in workflow run outputs or entity properties."
    )


def build_spanish(pdf: PlanPDF):
    pdf.h1("1. Objetivo y enfoque del POC")
    pdf.body(
        "Objetivo: Demostrar un camino de extremo a extremo que un desarrollador pueda "
        "ejecutar desde Port, con aprobación de DevOps y estado de vuelta al solicitante "
        "— no paridad completa de producción el primer día."
    )
    pdf.body(
        "Decisión de diseño clave para el POC: Usar el nodo nativo INPUT de Port para la "
        "puerta de aprobación Terraform plan→apply (alineado con “DevOps aprueba en Port” "
        "en el diagrama). Mantener Issues de GitHub como historia opcional posterior si el "
        "cliente exige seguimiento basado en issues."
    )
    pdf.body(
        "Estrategia de cortes: Construir primero un corte vertical (addRepository) y luego "
        "reutilizar el mismo esqueleto plan→aprobar→apply para equipos y variables de "
        "entorno. Tratar addWorkflow (merge de PR) como un corte final separado — o "
        "mantenerlo en el mismo workflow detrás de una puerta de merge / confirmación "
        "(ver arquitectura)."
    )

    pdf.architecture_section()

    pdf.h1("3. Fases de implementación")

    pdf.h2("Fase 0 — Fundamentos")
    pdf.numbered(1, "Conectar Port ↔ GitHub (Ocean / aplicación de GitHub).")
    pdf.numbered(
        2,
        "Crear un repositorio de control de plataforma con módulos Terraform y GitHub "
        "Actions workflow_dispatch (plan / apply).",
    )
    pdf.numbered(
        3,
        "Definir blueprints mínimos: service (o reutilizar el integrado), "
        "githubRepository (de la integración), provisioningRequest opcional para "
        "seguimiento de ejecuciones.",
    )
    pdf.numbered(
        4,
        "Guardar credenciales de Port como secretos de GitHub; usar "
        "port-labs/port-github-action para reportar el estado de la ejecución.",
    )

    pdf.h2("Fase 1 — Corte vertical: Crear repositorio")
    pdf.numbered(
        1,
        "Formulario de self-service: nombre del repo, visibilidad, equipo, plantilla.",
    )
    pdf.numbered(
        2,
        "INTEGRATION_ACTION → plan de GitHub Actions (Terraform crea el repo).",
    )
    pdf.numbered(3, "Nodo INPUT → DevOps aprueba / rechaza.")
    pdf.numbered(
        4,
        "Si se aprueba → workflow de apply; si tiene éxito → upsert de entidad en Port "
        "y notificación al usuario.",
    )
    pdf.numbered(5, "Prueba manual con una organización / sandbox desechable.")

    pdf.h2("Fase 2 — Reutilizar el patrón: Añadir equipo")
    pdf.numbered(
        1,
        "Segunda acción de self-service (o paso encadenado tras existir el repo).",
    )
    pdf.numbered(
        2,
        "Mismo ciclo plan→aprobar→apply sobre Terraform de membresía de equipo.",
    )
    pdf.numbered(3, "Relacionar repo ↔ equipo en Port ($team / relations).")

    pdf.h2("Fase 3 — Pipeline y variables de entorno")
    pdf.numbered(
        1,
        "Formulario para tipo de pipeline y claves/valores de variables de entorno "
        "(secretos vía GitHub Environments / APIs de secretos de Actions, detrás de "
        "Terraform o un GHA dedicado).",
    )
    pdf.numbered(
        2,
        "Mismo ciclo de aprobación; upsert de metadatos de pipeline/env en la entidad service.",
    )

    pdf.h2("Fase 4 — Añadir archivos de workflow (puerta por PR)")
    pdf.numbered(
        1,
        "Port despacha una acción que abre un PR con .github/workflows/* "
        "(o genera desde una plantilla).",
    )
    pdf.numbered(2, "DevOps hace merge en GitHub (puerta humana fuera de Port).")
    pdf.numbered(
        3,
        "Trigger de evento / polling / callback de estado actualiza Port cuando el PR "
        "se fusiona.",
    )
    pdf.numbered(4, "Notificación final de estado al solicitante.")

    pdf.h2("Fase 5 — Unificar el recorrido (opcional para el POC)")
    pdf.numbered(
        1,
        "Un workflow multi-paso con etapas secuenciales, o cuatro workflows más un "
        "orquestador ligero que los encadene vía eventos de estado de entidad.",
    )
    pdf.numbered(
        2,
        "Dashboard: solicitudes de aprovisionamiento, aprobaciones pendientes, "
        "catálogo de repositorios.",
    )

    pdf.h1("4. Orden de construcción sugerido")
    pdf.numbered(1, "A1–A3 + B1–B4 — demo mínima alineada con la Fase 1 del UML.")
    pdf.numbered(2, "C1–C2 — demuestra que el patrón es reutilizable.")
    pdf.numbered(3, "D1–D3 — demuestra secretos y configuración de pipeline.")
    pdf.numbered(4, "E1–E3 — demuestra el mecanismo de aprobación distinto (PR).")
    pdf.numbered(5, "F1–F2 — pulido para la demo a stakeholders.")

    pdf.h1("5. Épicas e historias de usuario")

    pdf.h2("Épica A — Fundamentos de plataforma")
    pdf.story_row(
        "A1",
        "Como ingeniero de plataforma, conecto Port a nuestra organización de GitHub "
        "para que los workflows puedan despachar Actions.",
        "Integración de GitHub saludable; se puede despachar un workflow_dispatch vacío "
        "desde Port y ver éxito.",
    )
    pdf.story_row(
        "A2",
        "Como ingeniero de plataforma, tengo un repo de control con Terraform + Actions "
        "plan/apply que reportan estado a Port.",
        "El plan sube un artefacto; apply lo consume; ambos hacen PATCH de logs de "
        "ejecución en Port vía port-github-action.",
    )
    pdf.story_row(
        "A3",
        "Como ingeniero de plataforma, defino blueprints para service / estado de "
        "aprovisionamiento.",
        "La entidad puede rastrear status (requested → planned → approved → applied / "
        "failed) y enlazar a la URL del repo de GitHub.",
    )

    pdf.h2("Épica B — Crear repositorio (addRepositorie)")
    pdf.story_row(
        "B1",
        "Como desarrollador, envío “Crear repositorio” desde Port con nombre, "
        "visibilidad y equipo propietario.",
        "El formulario valida entradas; la ejecución aparece en Port con la identidad "
        "del solicitante.",
    )
    pdf.story_row(
        "B2",
        "Como sistema, ejecuto Terraform plan para el nuevo repo y pausamos por aprobación.",
        "El plan tiene éxito; DevOps ve una aprobación INPUT pendiente con resumen/enlace "
        "del plan; aún no hay apply.",
    )
    pdf.story_row(
        "B3",
        "Como DevOps, apruebo o rechazo el cambio en Port.",
        "Aprobar → se ejecuta apply; rechazar → la ejecución termina, se notifica al "
        "usuario, no se crea el repo.",
    )
    pdf.story_row(
        "B4",
        "Como desarrollador, recibo el estado cuando termina el aprovisionamiento.",
        "El repo existe en GitHub; la entidad en Port se actualiza; el status "
        "SUCCESS/FAILURE coincide con la realidad.",
    )
    pdf.h3("Guion de prueba del POC (B)")
    pdf.bullet("Camino feliz")
    pdf.bullet("Camino de rechazo")
    pdf.bullet("Fallo del plan (nombre inválido)")

    pdf.h2("Épica C — Añadir equipo (addTeam)")
    pdf.story_row(
        "C1",
        "Como desarrollador, solicito acceso de equipo a un repo existente desde Port.",
        "El formulario selecciona entidad de repo + equipo; solo se muestran equipos permitidos.",
    )
    pdf.story_row(
        "C2",
        "El mismo ciclo plan→aprobar→apply aplica permisos de equipo vía Terraform.",
        "Tras aprobar, el equipo de GitHub tiene el permiso esperado; relations/$team "
        "en Port actualizados.",
    )
    pdf.h3("Guion de prueba del POC (C)")
    pdf.bullet("Añadir equipo")
    pdf.bullet("Rechazar")
    pdf.bullet("Intento sobre un repo que el usuario no posee (chequeo de permisos)")

    pdf.h2("Épica D — Pipeline y variables de entorno (addPipeline / addEnvVars)")
    pdf.story_row(
        "D1",
        "Como desarrollador, elijo una plantilla de pipeline y variables de entorno "
        "para un repo.",
        "El formulario captura no-secretos + referencias a secretos; los secretos nunca "
        "se registran en la salida de la ejecución de Port.",
    )
    pdf.story_row(
        "D2",
        "Plan/apply configura GitHub Environment / variables vía Terraform o GHA.",
        "Las variables están presentes en GitHub; Port muestra “pipeline configurado”.",
    )
    pdf.story_row(
        "D3",
        "Se requiere aprobación de DevOps antes de escribir secretos/variables.",
        "Sin mutación hasta aprobar.",
    )
    pdf.h3("Guion de prueba del POC (D)")
    pdf.bullet("Solo entorno de staging")
    pdf.bullet("Verificar redacción de secretos en los logs")

    pdf.h2("Épica E — Añadir archivos de workflow (addWorkflow)")
    pdf.story_row(
        "E1",
        "Como desarrollador, solicito el andamiaje de workflow de CI para mi repo.",
        "Port crea una rama + PR con YAML de workflow desde una plantilla.",
    )
    pdf.story_row(
        "E2",
        "Como DevOps, reviso y hago merge del PR en GitHub.",
        "El merge es la puerta de aprobación (como en el UML); sin push silencioso a "
        "la rama por defecto.",
    )
    pdf.story_row(
        "E3",
        "Como desarrollador, veo el estado final en Port tras el merge.",
        "El evento de PR fusionado (o polling) actualiza la entidad; se notifica al usuario.",
    )
    pdf.h3("Guion de prueba del POC (E)")
    pdf.bullet("Abrir PR → merge → Port SUCCESS")
    pdf.bullet("Abrir PR → cerrar sin merge → FAILED/CANCELLED")

    pdf.h2("Épica F — UX del recorrido y observabilidad (ligera para el POC)")
    pdf.story_row(
        "F1",
        "Como desarrollador, puedo ver dónde está atascada mi solicitud "
        "(plan / aprobación / apply / PR).",
        "Una línea de tiempo de ejecución o la entidad provisioningRequest muestra la etapa.",
    )
    pdf.story_row(
        "F2",
        "Como DevOps, tengo una cola de aprobaciones pendientes.",
        "Una página/widget de Port lista las aprobaciones INPUT abiertas.",
    )

    pdf.h1("6. Fuera de alcance del POC")
    pdf.bullet(
        "Aprobación completa basada en GitHub Issues espejando el UML "
        "(usar Port INPUT primero)."
    )
    pdf.bullet("Backends Terraform multi-organización / multi-nube.")
    pdf.bullet(
        "Encadenamiento automático de las cuatro fases en un solo clic sin confirmación "
        "intermedia."
    )
    pdf.bullet(
        "Endurecimiento RBAC de producción más allá de “Member puede solicitar / "
        "equipo DevOps puede aprobar”."
    )

    pdf.h1("7. Mapeo UML → constructos de Port")
    pdf.bullet("Usuario addRepositorie(form) → Workflow SELF_SERVE_TRIGGER")
    pdf.bullet(
        "Port → GithubAPI createRepo → Indirecto vía Terraform en GHA "
        "(preferir TF por paridad plan/apply)"
    )
    pdf.bullet(
        "Terraform execute(plan) / execute(apply) → Dos Actions workflow_dispatch + "
        "INTEGRATION_ACTION"
    )
    pdf.bullet(
        "Issues wait(approval) + DevOps sendApprove → Nodo INPUT de Port (POC); "
        "opcional después: GitHub Issue + callback"
    )
    pdf.bullet(
        "waitUntilEnd / sendStatus → reportWorkflowStatus + port-github-action "
        "PATCH_RUN / upsert de entidad"
    )
    pdf.bullet(
        "addWorkflow + createPullRequest + Merge → GHA abre PR; merge humano; "
        "actualización de evento/estado en Port"
    )

    pdf.h1("8. Guion de demostración")
    pdf.numbered(
        1,
        "El desarrollador abre Crear repositorio en Port y envía el formulario.",
    )
    pdf.numbered(
        2,
        "Mostrar la ejecución de plan en GitHub Actions y la aprobación pendiente en Port.",
    )
    pdf.numbered(
        3,
        "DevOps aprueba → apply crea el repo → aparece la entidad en el catálogo.",
    )
    pdf.numbered(4, "El desarrollador ejecuta Añadir equipo y luego Configurar pipeline.")
    pdf.numbered(
        5,
        "El desarrollador ejecuta Añadir workflow → se abre el PR → DevOps hace merge → "
        "Port muestra completado.",
    )

    pdf.h1("9. Riesgos a señalar temprano")
    pdf.bullet(
        "Estado asíncrono de larga duración: los artefactos del plan deben indexarse por "
        "el run ID de Port para que apply use el plan correcto."
    )
    pdf.bullet(
        "Dos estilos de aprobación: basado en Issues (UML) vs Port INPUT vs merge de PR "
        "— alinear con el cliente antes de construir automatización de Issues."
    )
    pdf.bullet(
        "Workflows están en open beta: preferir Workflows para lógica multi-paso nueva; "
        "Actions & Automations legacy siguen soportadas si ya se usan."
    )
    pdf.bullet(
        "Secretos: nunca poner valores secretos en salidas de ejecución de workflow ni "
        "en propiedades de entidades."
    )


def generate(lang: str, out_name: str, title: str, subtitle: str, meta: list[str], builder):
    pdf = PlanPDF(lang=lang)
    pdf.alias_nb_pages()
    pdf.cover(title, subtitle, meta)
    pdf.add_page()
    builder(pdf)
    for directory in (OUT_DIR, ARTIFACT_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / out_name
        pdf.output(str(path))
        print(f"Wrote {path}")
    # Also publish the architecture diagram asset for download.
    if DIAGRAM_PNG.exists():
        artifact_png = ARTIFACT_DIR / DIAGRAM_PNG.name
        artifact_png.write_bytes(DIAGRAM_PNG.read_bytes())
        print(f"Wrote {artifact_png}")


def main():
    generate(
        "en",
        EN["filename"],
        EN["title"],
        EN["subtitle"],
        EN["meta"],
        build_english,
    )
    generate(
        "es",
        ES["filename"],
        ES["title"],
        ES["subtitle"],
        ES["meta"],
        build_spanish,
    )


if __name__ == "__main__":
    main()
