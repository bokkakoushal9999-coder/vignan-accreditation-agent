"""
FastAPI REST API Backend for Vignan University AI Accreditation Academic Agent.
Provides RESTful endpoints for criteria, evidence management, evaluation, gap matrices,
remediation tasks, SAR narrative generation, and verification audit trails.
"""

from fastapi import FastAPI, HTTPException, Query, Response, Body, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from core.criteria_registry import get_framework_criteria, get_all_metrics_flat
from core.vignan_demo_data import get_demo_evidence_list, VIGNAN_DEPARTMENTS, VIGNAN_ACADEMIC_YEARS
from core.evidence_engine import EvidenceEngine
from core.scoring_engine import ScoringEngine
from core.gap_matrix_engine import GapMatrixEngine
from core.task_manager import TaskManager
from core.narrative_generator import NarrativeGenerator
from core.audit_verifier import AuditVerifier
from core.evidence_validator import EvidenceValidator
from core.continuous_scanner import ContinuousReadinessScanner
from core.submission_builder import SubmissionPackageBuilder
from core.mock_visit_engine import MockVisitSimulatorEngine
from core.pdf_exporter import generate_accreditation_dossier_pdf
from core.database import get_database, DatabaseManager, get_db_type, is_postgres
from core.ranking_engine import RankingEngine
from core.obe_mapping_engine import OBEMappingEngine
from core.document_store import DocumentStore, DocumentExtractor

app = FastAPI(
    title="VFSTR AI Accreditation Academic Agent API",
    description="REST API backend with persistent multi-framework database for continuous accreditation readiness assessment (NAAC, NBA, NIRF)",
    version="2.5.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent Database & Backend State
db = get_database()
evidence_store = db.get_all_evidence()
document_store = DocumentStore()
evidence_engine = EvidenceEngine()
scoring_engine = ScoringEngine()
gap_engine = GapMatrixEngine()
task_manager = TaskManager(use_db=True)
narrative_gen = NarrativeGenerator()
audit_verifier = AuditVerifier(use_db=True)
evidence_validator = EvidenceValidator()
continuous_scanner = ContinuousReadinessScanner()
submission_builder = SubmissionPackageBuilder()
mock_visit_engine = MockVisitSimulatorEngine()
ranking_engine = RankingEngine()
obe_engine = OBEMappingEngine()


@app.get("/")
def root_landing():
    """
    Root landing route for the VFSTR AI Accreditation Academic Agent.
    Provides API overview, interactive documentation links, active database backend,
    supported frameworks (NAAC, NBA, NIRF), and full endpoint directory.
    """
    return {
        "title": "VFSTR Vignan AI Accreditation Academic Agent API",
        "description": "Continuous Institutional Quality & Accreditation Intelligence Platform (NAAC, NBA, NIRF)",
        "version": "2.5.0",
        "status": "online",
        "database": {
            "type": get_db_type(),
            "status": "connected",
            "evidence_count": len(evidence_store),
            "tasks_count": len(task_manager.get_all_tasks())
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "frameworks_supported": [
            "NAAC (National Assessment and Accreditation Council - 7 Criteria)",
            "NBA (National Board of Accreditation - 10 Criteria Tier-1)",
            "NIRF (National Institutional Ranking Framework - 5 Parameters)"
        ],
        "endpoints": {
            "root": "GET /",
            "health": "GET /api/health",
            "frameworks": "GET /api/frameworks",
            "criteria": "GET /api/criteria?framework=NAAC",
            "evidence_list": "GET /api/evidence",
            "evidence_upload": "POST /api/evidence/upload (Multipart/Form-Data File + OCR)",
            "evidence_ingest": "POST /api/evidence (Text Ingestion)",
            "evaluate": "POST /api/evaluate",
            "gaps": "GET /api/gaps?framework=NAAC",
            "tasks": "GET /api/tasks, POST /api/tasks",
            "narratives": "POST /api/narrative/generate",
            "ranking_nirf": "POST /api/ranking/nirf",
            "ranking_qs": "GET /api/ranking/qs",
            "obe_flow": "GET /api/obe/flow",
            "audit_trail": "GET /api/audit/trail",
            "bujji_chat": "POST /api/bujji/chat"
        },
        "timestamp": datetime.now().isoformat()
    }



# --- Pydantic Request Models ---
class IngestEvidenceRequest(BaseModel):
    title: str
    department: str
    academic_year: str
    document_type: str
    issuing_authority: str
    raw_text: str
    framework: str = "NAAC"


class EvaluationRequest(BaseModel):
    framework: str = "NAAC"
    simulated_adjustments: Optional[Dict[str, float]] = None


class CreateTaskRequest(BaseModel):
    title: str
    metric_id: str
    criterion_id: str
    owner: str
    priority: str = "High"
    deadline: Optional[str] = None
    estimated_days: int = 7
    action_plan: str = ""
    attached_evidence_id: Optional[str] = None


class UpdateTaskStatusRequest(BaseModel):
    status: str
    resolution_notes: Optional[str] = None


class NarrativeRequest(BaseModel):
    metric_id: str
    framework: str = "NAAC"
    focus_tone: str = "Executive & Evidence-Backed"
    additional_notes: str = ""


class VerifyEvidenceRequest(BaseModel):
    evidence_id: str
    reviewer_name: str
    reviewer_role: str
    action: str  # VERIFIED_APPROVED, VERIFIED_WITH_CONCERNS, REQUEST_REVISION, REJECTED
    audit_notes: str = ""
    completeness_adjustment: Optional[int] = None


class MockVisitEvaluateRequest(BaseModel):
    question_id: str
    faculty_notes: str = ""
    attached_evidence_ids: List[str] = []


class SubmissionBuildRequest(BaseModel):
    framework: str = "NAAC"
    institution_name: str = "VFSTR (Deemed to be University)"
    accredited_unit: str = "Institutional NAAC Self-Study Report (Cycle 2)"


# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    """Health check endpoint confirming API status and uptime."""
    return {
        "status": "online",
        "service": "VFSTR AI Accreditation Agent Backend",
        "version": "2.5.0",
        "timestamp": datetime.now().isoformat(),
        "total_evidence_records": len(evidence_store),
        "total_tasks": len(task_manager.get_all_tasks()),
        "total_audit_events": len(audit_verifier.get_audit_trail())
    }


@app.get("/api/frameworks")
def list_frameworks():
    """Returns all supported accreditation and ranking frameworks."""
    fws = db.get_frameworks_from_db() if db else []
    return {
        "count": len(fws),
        "frameworks": fws
    }


@app.get("/api/criteria")
def get_criteria(framework: str = Query("NAAC", description="NAAC, NBA, or NIRF")):
    """Retrieves all criteria and detailed metrics for selected framework directly from DB or registry."""
    framework_up = framework.upper()
    if framework_up not in ["NAAC", "NBA", "NIRF"]:
        raise HTTPException(status_code=400, detail="Framework must be NAAC, NBA, or NIRF")

    # Query database first, falling back to registry
    if db:
        criteria = db.get_criteria_from_db(framework_up)
    else:
        criteria = get_framework_criteria(framework_up)

    metrics_flat = get_all_metrics_flat(framework_up) if framework_up in ["NAAC", "NBA"] else []
    if not metrics_flat and criteria:
        for crit_id, crit_info in criteria.items():
            for m_id, m_info in crit_info.get("metrics", {}).items():
                item = dict(m_info)
                item["criterion_id"] = crit_id
                item["criterion_name"] = crit_info["name"]
                metrics_flat.append(item)

    return {
        "framework": framework_up,
        "criteria": criteria,
        "metrics_flat": metrics_flat,
        "total_criteria_count": len(criteria),
        "total_metrics_count": len(metrics_flat)
    }


@app.get("/api/evidence")
def list_evidence(
    department: Optional[str] = None,
    academic_year: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Lists institutional evidence with multi-field filtering from single-source-of-truth database."""
    results = list(evidence_store)
    if department and department != "All Departments":
        results = [e for e in results if e.get("department") == department]
    if academic_year and academic_year != "All Years":
        results = [e for e in results if e.get("academic_year") == academic_year]
    if status and status != "All":
        results = [e for e in results if e.get("status") == status]
    if search:
        s_lower = search.lower()
        results = [
            e for e in results
            if s_lower in e["title"].lower() or s_lower in e.get("raw_text", "").lower() or s_lower in e["id"].lower()
        ]
    return {
        "count": len(results),
        "evidence": results
    }


@app.post("/api/evidence/upload")
async def upload_evidence_document(
    file: UploadFile = File(...),
    framework: str = Form("NAAC"),
    department: Optional[str] = Form(None),
    academic_year: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    title: Optional[str] = Form(None)
):
    """
    Multipart file upload endpoint with full OCR & DocumentStore extraction pipeline:
    - Stores file with SHA-256 deduplication in data/documents/
    - Extracts text and layout (PDF, DOCX, CSV/XLSX, or scanned Image OCR)
    - Automatically maps extracted text semantically to accreditation metrics
    - Evaluates evidence quality and inserts record into the database.
    """
    global evidence_store
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 1. Save document to DocumentStore
    doc_meta = document_store.save_file(content_bytes, file.filename)

    # 2. Run extraction and OCR pipeline
    extraction = DocumentExtractor.extract_text(content_bytes, file.filename)
    raw_text = extraction["extracted_text"]
    detected_meta = extraction.get("detected_metadata", {})

    resolved_title = title or detected_meta.get("document_type") or Path(file.filename).stem.replace("_", " ").title()
    resolved_dept = department or detected_meta.get("department") or "Internal Quality Assurance Cell (IQAC)"
    resolved_year = academic_year or detected_meta.get("academic_year") or "2023-24"
    resolved_doc_type = document_type or detected_meta.get("document_type") or doc_meta["file_format"]
    resolved_auth = issuing_authority or detected_meta.get("issuing_authority") or "Dr. K. Ramamohan (Director IQAC)"

    # 3. Map semantically to criteria & evaluate quality
    matches = evidence_engine.map_evidence_to_metrics(raw_text, framework=framework, top_k=3)
    matched_criteria_ids = [m["criterion_id"] for m in matches] + [m["metric_id"] for m in matches]
    if not matched_criteria_ids:
        matched_criteria_ids = ["C1"]

    new_ev = {
        "id": f"EVD-VIG-{len(evidence_store) + 101}",
        "title": resolved_title,
        "filename": doc_meta["filename"],
        "original_filename": file.filename,
        "department": resolved_dept,
        "academic_year": resolved_year,
        "document_type": resolved_doc_type,
        "issuing_authority": resolved_auth,
        "content_summary": raw_text[:300] + ("..." if len(raw_text) > 300 else ""),
        "summary": raw_text[:300] + ("..." if len(raw_text) > 300 else ""),
        "description": raw_text[:300] + ("..." if len(raw_text) > 300 else ""),
        "raw_text": raw_text,
        "extracted_text": raw_text,
        "status": "Under Review",
        "completeness_score": 85,
        "missing_elements": [],
        "applicable_criteria": list(set(matched_criteria_ids)),
        "verified_by": None,
        "verification_date": None,
        "file_format": doc_meta["file_format"],
        "file_size": doc_meta["file_size"],
        "file_hash": doc_meta["file_hash"],
        "file_path": doc_meta["file_path"],
        "ocr_applied": extraction.get("ocr_applied", False),
        "ocr_engine": extraction.get("ocr_engine", "Native Parser")
    }

    quality = evidence_engine.evaluate_evidence_quality(new_ev)
    new_ev["completeness_score"] = quality["quality_score"]
    new_ev["missing_elements"] = quality["penalties"]

    if db:
        db.insert_evidence(new_ev)
        evidence_store = db.get_all_evidence()
    else:
        evidence_store.insert(0, new_ev)

    return {
        "message": "File successfully uploaded, stored on disk, OCR processed, and persisted to database.",
        "evidence": new_ev,
        "extraction_summary": {
            "ocr_applied": extraction.get("ocr_applied", False),
            "ocr_engine": extraction.get("ocr_engine"),
            "word_count": extraction.get("word_count", 0),
            "confidence_score": extraction.get("confidence_score", 0.9),
            "file_size": doc_meta["file_size"],
            "sha256_hash": doc_meta["file_hash"]
        },
        "matched_metrics": matches,
        "quality_evaluation": quality
    }


@app.post("/api/evidence")
def ingest_evidence(req: IngestEvidenceRequest):
    """Ingests and semantically maps new evidence text to criteria."""
    global evidence_store
    matches = evidence_engine.map_evidence_to_metrics(req.raw_text, framework=req.framework, top_k=3)
    matched_criteria_ids = [m["criterion_id"] for m in matches] + [m["metric_id"] for m in matches]


    new_ev = {
        "id": f"EVD-VIG-{len(evidence_store) + 101}",
        "title": req.title,
        "department": req.department,
        "academic_year": req.academic_year,
        "document_type": req.document_type,
        "issuing_authority": req.issuing_authority or "VFSTR Directorate",
        "content_summary": req.raw_text[:250] + ("..." if len(req.raw_text) > 250 else ""),
        "summary": req.raw_text[:250] + ("..." if len(req.raw_text) > 250 else ""),
        "description": req.raw_text[:250] + ("..." if len(req.raw_text) > 250 else ""),
        "raw_text": req.raw_text,
        "extracted_text": req.raw_text,
        "status": "Under Review",
        "completeness_score": 88,
        "missing_elements": [],
        "applicable_criteria": list(set(matched_criteria_ids)),
        "verified_by": None,
        "verification_date": None,
        "file_format": "TXT/DOC",
        "file_size": f"{round(len(req.raw_text)/1024, 1)} KB"
    }

    quality = evidence_engine.evaluate_evidence_quality(new_ev)
    new_ev["completeness_score"] = quality["quality_score"]
    new_ev["missing_elements"] = quality["penalties"]

    if db:
        db.insert_evidence(new_ev)
        evidence_store = db.get_all_evidence()
    else:
        evidence_store.insert(0, new_ev)

    return {
        "message": "Evidence successfully ingested, persisted to SQLite, and semantically mapped",
        "evidence": new_ev,
        "matched_metrics": matches,
        "quality_evaluation": quality
    }


@app.post("/api/evaluate")
def evaluate_accreditation(req: EvaluationRequest):
    """Computes criterion-wise and overall accreditation scores, CGPA, and grade."""
    eval_result = scoring_engine.evaluate_framework(
        evidence_list=evidence_store,
        framework=req.framework,
        simulated_adjustments=req.simulated_adjustments
    )
    dept_breakdown = scoring_engine.get_department_breakdown(evidence_store)
    return {
        **eval_result,
        "department_breakdown": dept_breakdown
    }


@app.get("/api/gaps")
def get_prioritized_gaps(framework: str = Query("NAAC", description="NAAC or NBA")):
    """Detects missing/incomplete evidence and returns 2x2 Impact vs Effort matrix."""
    gaps = evidence_engine.detect_missing_evidence(evidence_store, framework=framework)
    matrix_result = gap_engine.build_prioritized_matrix(gaps)
    return matrix_result


@app.get("/api/tasks")
def list_tasks(
    status: Optional[str] = None,
    owner: Optional[str] = None,
    priority: Optional[str] = None,
    criterion_id: Optional[str] = None
):
    """Retrieves corrective action tasks with optional filtering."""
    filtered = task_manager.filter_tasks(status=status, owner=owner, priority=priority, criterion_id=criterion_id)
    stats = task_manager.get_task_statistics()
    return {
        "tasks": filtered,
        "statistics": stats
    }


@app.post("/api/tasks")
def create_task(req: CreateTaskRequest):
    """Creates a new remediation action item."""
    task = task_manager.add_task(
        title=req.title,
        metric_id=req.metric_id,
        criterion_id=req.criterion_id,
        owner=req.owner,
        priority=req.priority,
        deadline=req.deadline or "",
        estimated_days=req.estimated_days,
        action_plan=req.action_plan,
        attached_evidence_id=req.attached_evidence_id
    )
    return {
        "message": "Task created successfully",
        "task": task
    }


@app.patch("/api/tasks/{task_id}")
def update_task_status(task_id: str, req: UpdateTaskStatusRequest):
    """Updates status and resolution notes for a remediation task."""
    success = task_manager.update_task_status(task_id, req.status, req.resolution_notes)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    return {
        "message": "Task updated successfully",
        "task_id": task_id,
        "new_status": req.status
    }


@app.post("/api/narrative/generate")
def generate_narrative(req: NarrativeRequest):
    """Generates peer-review ready Qualitative Self Assessment Report (SSR/SAR) narrative."""
    all_metrics = get_all_metrics_flat(req.framework)
    metric = next((m for m in all_metrics if m["id"] == req.metric_id), None)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric {req.metric_id} not found in {req.framework}")

    matched_evidence = [
        e for e in evidence_store
        if req.metric_id in e.get("applicable_criteria", []) or metric["criterion_id"] in e.get("applicable_criteria", [])
    ]

    narrative = narrative_gen.generate_metric_narrative(
        metric=metric,
        mapped_evidence=matched_evidence,
        framework=req.framework,
        focus_tone=req.focus_tone,
        additional_notes=req.additional_notes
    )
    return narrative


@app.post("/api/verify")
def verify_evidence(req: VerifyEvidenceRequest):
    """Records human verification decision by IQAC reviewer in immutable audit log."""
    target_ev = next((e for e in evidence_store if e["id"] == req.evidence_id), None)
    if not target_ev:
        raise HTTPException(status_code=404, detail=f"Evidence with ID {req.evidence_id} not found")

    log_entry = audit_verifier.record_verification(
        evidence=target_ev,
        reviewer_name=req.reviewer_name,
        reviewer_role=req.reviewer_role,
        action=req.action,
        audit_notes=req.audit_notes,
        completeness_adjustment=req.completeness_adjustment
    )
    return {
        "message": "Verification successfully recorded",
        "audit_log": log_entry,
        "updated_evidence": target_ev
    }


@app.get("/api/audit-trail")
def get_audit_trail():
    """Returns complete audit log and summary stats."""
    logs = audit_verifier.get_audit_trail()
    summary = audit_verifier.get_audit_summary()
    return {
        "audit_trail": logs,
        "summary": summary
    }


@app.get("/api/export-pdf")
def export_pdf_dossier(framework: str = Query("NAAC", description="NAAC or NBA")):
    """Generates and returns executive PDF accreditation readiness dossier."""
    ev_list = db.get_all_evidence() if db else evidence_store
    eval_result = scoring_engine.evaluate_framework(ev_list, framework=framework)
    gaps = evidence_engine.detect_missing_evidence(ev_list, framework=framework)
    matrix_res = gap_engine.build_prioritized_matrix(gaps)
    tasks = task_manager.get_all_tasks()
    audit_trail = audit_verifier.get_audit_trail()

    pdf_bytes = generate_accreditation_dossier_pdf(eval_result, matrix_res, tasks, audit_trail)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=VFSTR_{framework}_Accreditation_Dossier_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )


# --- Multi-Dimensional Validation & Continuous Scanner Endpoints ---

@app.get("/api/validation/report")
def get_validation_report(target_criterion_id: Optional[str] = None):
    """Runs 6-dimensional validation pipeline on all evidence records."""
    ev_list = db.get_all_evidence() if db else evidence_store
    return evidence_validator.validate_evidence_batch(ev_list, target_criterion_id=target_criterion_id)


@app.get("/api/scanner/run")
def run_continuous_readiness_scan(framework: str = Query("NAAC", description="NAAC or NBA")):
    """Executes continuous readiness audit across all criteria and predicts CGPA / Letter Grade."""
    ev_list = db.get_all_evidence() if db else evidence_store
    return continuous_scanner.scan_all_criteria(framework=framework, evidence_list=ev_list)


# --- Pre-Submission Gatekeeper & Annexure Builder Endpoints ---

@app.get("/api/submission/validate")
def validate_submission_readiness(framework: str = Query("NAAC", description="NAAC or NBA")):
    """Evaluates strict pre-submission blocker rules (unresolved tasks, unverified proofs, defects)."""
    ev_list = db.get_all_evidence() if db else evidence_store
    tasks = task_manager.get_all_tasks()
    narratives = db.get_narratives() if db else []
    return submission_builder.validate_pre_submission_readiness(
        framework=framework,
        evidence_list=ev_list,
        tasks_list=tasks,
        narratives_list=narratives
    )


@app.post("/api/submission/build")
def build_final_submission_package(req: SubmissionBuildRequest):
    """Compiles numbered annexures (A001-A045), Evidence Index CSV, and cross-reference table."""
    ev_list = db.get_all_evidence() if db else evidence_store
    return submission_builder.assemble_submission_package(
        framework=req.framework,
        evidence_list=ev_list,
        institution_name=req.institution_name,
        accredited_unit=req.accredited_unit
    )


# --- Mock Visit Peer-Team Simulator Endpoints ---

@app.get("/api/mock-visit/questions")
def get_mock_visit_questions(
    category: Optional[str] = None,
    criterion_id: Optional[str] = None,
    framework: Optional[str] = None
):
    """Retrieves mock visit peer-team question bank with evidence linkages and defense answers."""
    questions = mock_visit_engine.get_questions(
        category=category,
        criterion_id=criterion_id,
        framework=framework
    )
    categories = mock_visit_engine.get_all_categories()
    summary = mock_visit_engine.get_simulation_summary()
    return {
        "summary": summary,
        "categories": categories,
        "total_returned": len(questions),
        "questions": questions
    }


@app.post("/api/mock-visit/evaluate")
def evaluate_mock_visit_defense(req: MockVisitEvaluateRequest):
    """Evaluates faculty defense response against linked benchmark evidence and hard metrics."""
    return mock_visit_engine.evaluate_defense_readiness(
        question_id=req.question_id,
        faculty_notes=req.faculty_notes,
        attached_evidence_ids=req.attached_evidence_ids
    )


# --- Database Management Endpoints ---

@app.get("/api/db/stats")
def get_database_statistics():
    """Returns persistent SQLite database statistics and record counts."""
    return db.get_db_stats()


@app.post("/api/db/reset")
def reset_database_to_default():
    """Resets SQLite database tables and re-seeds factory default Vignan data."""
    global evidence_store
    db.reset_database()
    evidence_store = db.get_all_evidence()
    return {
        "message": "SQLite database successfully reset and re-seeded with authentic Vignan University dataset.",
        "stats": db.get_db_stats()
    }


@app.get("/api/db/export")
def export_database_json():
    """Exports full database contents as a JSON payload."""
    return {
        "database_stats": db.get_db_stats(),
        "evidence": db.get_all_evidence(),
        "tasks": db.get_all_tasks(),
        "audit_logs": db.get_all_audit_logs(),
        "narratives": db.get_narratives()
    }


@app.delete("/api/evidence/{evidence_id}")
def delete_evidence_item(evidence_id: str):
    """Deletes an evidence record from persistent SQLite storage."""
    global evidence_store
    success = db.delete_evidence(evidence_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Evidence with ID {evidence_id} not found")
    evidence_store = db.get_all_evidence()
    return {"message": f"Evidence {evidence_id} deleted successfully"}

