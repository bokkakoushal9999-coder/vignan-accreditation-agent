# 🏛️ Vignan University AI Accreditation Academic Agent (VFSTR)

An intelligent, enterprise-grade AI Accreditation Academic Agent built specifically for **Vignan's Foundation for Science, Technology & Research (VFSTR — Deemed to be University, Vadlamudi, Guntur, AP)**.

The platform provides continuous assessment of institutional accreditation readiness across **NAAC** (7 Criteria / 39 metrics), **NBA** (10 OBE Criteria), and **NIRF** (5 Parameters) using a production-style **SQLAlchemy ORM + SQLite / PostgreSQL Database Backend**, a **FastAPI REST API**, an **OCR-powered document ingestion pipeline**, and an interactive **Streamlit Web Application** — with zero paid API dependencies.

---

## 🗄️ Database Architecture

The backend persistence layer supports both **SQLite** (default, zero-config) and **PostgreSQL** (cloud/production), auto-detected at startup:

```
ACCREDITATION_DB_PATH=sqlite:///data/accreditation.db   # default
DATABASE_URL=postgresql://user:pass@host/db             # cloud override
```

### Entity Hierarchy

```
Framework (NAAC / NBA / NIRF)
    ↓
Criteria  (NAAC: 7 | NBA: 10 | NIRF: 5)
    ↓
Subcriteria / Metrics
    ↓
Evidence Requirements (allowed formats, minimum completeness %)
    ↓
Evidence Records  [45 records — single source of truth, SHA-256 deduplicated]
    ↓
Evidence Requirement Map (rule / keyword / semantic matching)
    ↓
Gaps (intentional deficiencies & missing proof) ──► Actionable Tasks (org. roles)
    ↓
SAR Drafts (qualitative narratives) ──► SAR Sources (citations)
    ↓
Human Verifications (MANDATORY IQAC guardrail — AI cannot approve)
    ↓
Audit Log (immutable timestamped traceability)
```

---

## 📊 Database Tables (15 Relational Tables)

| # | Table | Purpose | Key Fields |
|---|:---|:---|:---|
| 1 | `accreditation_frameworks` | Regulatory bodies (NAAC, NBA, NIRF) | `id`, `name`, `code`, `version`, `is_active` |
| 2 | `criteria` | Top-level criteria per framework | `id`, `framework_id`, `code`, `name`, `weight`, `required_score` |
| 3 | `subcriteria` | Detailed subcriteria / metrics | `id`, `criterion_id`, `code`, `name`, `weight`, `required_evidence` |
| 4 | `evidence` | Uploaded institutional proof documents | `id`, `filename`, `file_hash`, `completeness_score`, `status`, `extracted_text`, `applicable_criteria` |
| 5 | `evidence_requirements` | Required evidence definitions | `id`, `criterion_id`, `requirement_name`, `allowed_file_types`, `minimum_completeness` |
| 6 | `evidence_requirement_map` | Maps evidence to requirements | `id`, `evidence_id`, `requirement_id`, `match_score`, `matched_by` |
| 7 | `readiness_snapshots` | Historical readiness over time | `id`, `framework_id`, `overall_score`, `status`, `total_criteria` |
| 8 | `criterion_readiness` | Criterion-level scoring | `id`, `snapshot_id`, `criterion_id`, `evidence_score`, `overall_score` |
| 9 | `gaps` | Missing / incomplete evidence | `id`, `criterion_id`, `title`, `severity`, `impact`, `effort`, `status` |
| 10 | `tasks` | Remediation action items | `id`, `gap_id`, `title`, `owner_role`, `owner_department`, `priority`, `deadline` |
| 11 | `sar_drafts` | SSR / SAR narratives (AI-generated) | `id`, `framework_id`, `criterion_id`, `title`, `draft_text`, `status`, `generated_by` |
| 12 | `sar_sources` | Traceability citations for SAR | `id`, `sar_draft_id`, `evidence_id`, `source_reference`, `relevance_score` |
| 13 | `human_verifications` | IQAC approval / rejection decisions | `id`, `evidence_id`, `sar_draft_id`, `reviewer_name`, `reviewer_role`, `decision` |
| 14 | `users` | Application users and roles | `id`, `name`, `email`, `role`, `department`, `is_active` |
| 15 | `audit_log` | Immutable audit trail | `id`, `action`, `object_type`, `object_id`, `old_value`, `new_value`, `timestamp` |

---

## 🛡️ Human Verification Guardrail

> [!IMPORTANT]
> **This is an accreditation support system — not a decision engine.**
> - The AI **MUST NOT** certify, approve, or make final accreditation decisions.
> - AI-generated SAR drafts are marked: `AI DRAFT — HUMAN VERIFICATION REQUIRED`.
> - Analyzed evidence enters `PENDING_VERIFICATION` or `UNDER_REVIEW` status only.
> - **Only a designated human authority** (Director IQAC, Dean Academics, Reviewer) can create an `APPROVED` record.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize the Database
```bash
python -c "from core.database import init_db; init_db(); print('DB OK')"
```

### 3. Seed Full Demonstration Dataset
```bash
python -m core.seed_database
```

Seeds the complete multi-framework dataset:
- **NAAC**: 7 criteria, 39 subcriteria/metrics
- **NBA**: 10 OBE criteria with Programme Outcomes mapping
- **NIRF**: 5 parameters (TLR, RPC, GO, OI, PERCEPTION)
- **45 institutional evidence records** (single source of truth, SHA-256 deduplicated)
- Intentional compliance gaps, remediation tasks, SAR drafts, human verifications, and historical readiness snapshots

### 4. Run Tests
```bash
pytest -v
```
**63 tests collected — all always-on (no skips).**

### 5. One-Click Full Stack Launch
```bash
python start_all.py
```

This starts:
- **FastAPI** backend on `http://localhost:8000`
- **Streamlit** frontend on `http://localhost:8501`

---

## 🌐 REST API Endpoints (`http://localhost:8000`)

| Method | Route | Description |
|:---|:---|:---|
| `GET` | `/` | **Root landing** — API health, version, DB type, endpoint index |
| `GET` | `/health` | Database health diagnostics |
| `GET` | `/api/criteria` | List criteria (filter by `framework`, `search`) |
| `GET` | `/api/criteria/{id}/evidence` | Evidence mapped to a criterion |
| `GET` | `/api/evidence` | All evidence records |
| `POST` | `/api/evidence/upload` | **Multipart file upload with OCR extraction** |
| `POST` | `/api/evidence/analyze` | Analyze evidence completeness |
| `GET` | `/api/gaps` | Gap matrix (filter by framework, severity) |
| `GET` | `/api/tasks` | Remediation task list |
| `POST` | `/api/sar/generate` | Generate SAR narrative for a criterion |
| `GET` | `/api/audit/trail` | Full immutable audit trail |
| `GET` | `/api/readiness/snapshot` | Current readiness snapshot |
| `POST` | `/api/submission/build` | Build submission package |
| `GET` | `/api/ranking/simulate` | NIRF ranking simulation |
| `POST` | `/api/mock-visit/simulate` | Mock accreditation visit simulation |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/redoc` | ReDoc API documentation |

---

## 📄 Document Ingestion & OCR Pipeline

Evidence files are handled by `core/document_store.py`:

1. **Upload** via `POST /api/evidence/upload` (multipart) or via the Streamlit UI tab.
2. **SHA-256 deduplication** — identical files are detected before storage.
3. **Text extraction** — PDF text layer → fallback to `pytesseract` OCR → raw bytes.
4. **Mapping** — extracted text is matched against criteria evidence requirements.
5. **Storage** — files persisted to `data/documents/`, metadata written to SQLite/PostgreSQL.

---

## ☁️ PostgreSQL / Cloud Deployment

To switch from SQLite to PostgreSQL:

```bash
# Set environment variable before starting
DATABASE_URL=postgresql://user:password@host:5432/accreditation python start_all.py
```

Migrate existing SQLite data to PostgreSQL:
```bash
python scripts/migrate_postgres.py
```

The `DATABASE_URL` environment variable takes full precedence over `ACCREDITATION_DB_PATH`.

---

## 🎨 Streamlit UI — 8 Interactive Tabs

| # | Tab | Key Features |
|---|:---|:---|
| 1 | `🤖 Bujji — Agentic AI Copilot` | 3D avatar hero, offline NLP, quick action chips |
| 2 | `🏛️ Executive Dashboard` | Readiness radar, CGPA simulator, point-deficit bar charts |
| 3 | `📁 Evidence Repository` | File upload → OCR pipeline, completeness scoring, semantic matching |
| 4 | `🎯 Criteria Mapping` | NAAC / NBA / NIRF criterion and metric drilldown |
| 5 | `⚡ Gap Prioritization Matrix` | Impact vs Effort strategic scatter quadrant |
| 6 | `📋 Remediation Hub` | Corrective tasks, deadline trackers, status lifecycles |
| 7 | `✍️ SAR Narrative Studio` | AI SSR/SAR narrative generation, Markdown export |
| 8 | `🛡️ IQAC Audit & Exports` | Human-in-the-loop review, immutable audit trail, PDF/CSV/JSON export |

---

## 🔍 Inspecting the Database

**Python:**
```python
from core.database import database_health_check, get_db_session
from core.models import Criterion, Evidence, Gap, Task

# Health diagnostics
print(database_health_check())

# Query records
with get_db_session() as session:
    print("Criteria Total:", session.query(Criterion).count())
    print("Evidence Records:", session.query(Evidence).count())
    print("Open Gaps:", session.query(Gap).filter(Gap.status == 'OPEN').count())
    print("Tasks:", session.query(Task).count())
```

**SQLite CLI:**
```bash
sqlite3 data/accreditation.db ".tables"
sqlite3 data/accreditation.db "SELECT code, name, required_score FROM criteria;"
sqlite3 data/accreditation.db "SELECT title, severity, status FROM gaps;"
sqlite3 data/accreditation.db "SELECT COUNT(*) FROM evidence;"
```

---

## 📁 Project Structure

```
accreditation-academic-agent/
├── app.py                        # Streamlit frontend (8 tabs)
├── start_all.py                  # One-click launcher (FastAPI + Streamlit)
├── requirements.txt
├── pytest.ini
├── .env.example                  # Environment variable template
│
├── backend/
│   ├── api.py                    # FastAPI app — all REST endpoints
│   └── run_server.py             # Uvicorn server runner
│
├── core/
│   ├── database.py               # SQLite + PostgreSQL ORM layer
│   ├── models.py                 # SQLAlchemy ORM models (15 tables)
│   ├── repository.py             # DB CRUD operations
│   ├── seed_database.py          # Full multi-framework demo data seeder
│   ├── document_store.py         # File store + OCR extraction pipeline
│   ├── criteria_registry.py      # NAAC/NBA criteria definitions
│   ├── vignan_demo_data.py       # 45 evidence records (single source of truth)
│   ├── evidence_engine.py        # Evidence completeness analysis
│   ├── evidence_validator.py     # Validation rules
│   ├── scoring_engine.py         # Readiness scoring formulas
│   ├── gap_matrix_engine.py      # Gap impact/effort matrix
│   ├── task_manager.py           # Remediation task lifecycle
│   ├── narrative_generator.py    # SAR narrative generation
│   ├── audit_verifier.py         # Audit trail management
│   ├── continuous_scanner.py     # Continuous readiness scanner
│   ├── submission_builder.py     # Submission package builder
│   ├── mock_visit_engine.py      # Mock accreditation visit simulator
│   ├── ranking_engine.py         # NIRF ranking simulator
│   ├── obe_mapping_engine.py     # NBA OBE Programme Outcome mapping
│   ├── pdf_exporter.py           # PDF dossier export
│   └── schemas.py                # Pydantic API schemas
│
├── scripts/
│   └── migrate_postgres.py       # SQLite → PostgreSQL migration utility
│
├── tests/                        # 63 tests — always-on, no skips
│   ├── test_database.py
│   ├── test_document_pipeline_and_db.py
│   ├── test_e2e_flow.py
│   ├── test_engines.py
│   ├── test_full_system.py
│   ├── test_obe_sankey.py
│   ├── test_ranking_simulator.py
│   ├── test_submission_and_mock_visit.py
│   └── test_validation_and_scanner.py
│
└── data/
    ├── accreditation.db          # SQLite database (auto-created)
    └── documents/                # Uploaded evidence files (auto-created)
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|:---|:---|:---|
| `ACCREDITATION_DB_PATH` | `data/accreditation.db` | SQLite DB file path |
| `DATABASE_URL` | *(unset)* | PostgreSQL connection string (overrides SQLite) |
| `FASTAPI_PORT` | `8000` | FastAPI server port |
| `STREAMLIT_PORT` | `8501` | Streamlit server port |

Copy `.env.example` to `.env` and configure before launch.

