"""
Repository Layer for VFSTR Vignan Accreditation AI Agent Database.
Provides clean, transactional CRUD operations using SQLAlchemy sessions without exposing raw SQL.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc


from core.models import (
    AccreditationFramework, Criterion, Subcriterion, Evidence,
    EvidenceRequirement, EvidenceRequirementMap, ReadinessSnapshot,
    CriterionReadiness, Gap, Task, SARDraft, SARSource,
    HumanVerification, User, AuditLog
)
from core.schemas import validate_score_range


# -----------------------------------------------------------------------------
# 1. ACCREDITATION FRAMEWORKS
# -----------------------------------------------------------------------------
def create_framework(
    session: Session,
    name: str,
    code: str,
    version: str = "2024.1",
    description: str = "",
    is_active: bool = True
) -> AccreditationFramework:
    """Creates a new regulatory accreditation framework."""
    existing = session.query(AccreditationFramework).filter(AccreditationFramework.code == code).first()
    if existing:
        return existing
    framework = AccreditationFramework(
        name=name,
        code=code.upper(),
        version=version,
        description=description,
        is_active=is_active
    )
    session.add(framework)
    session.flush()
    create_audit_log(session, "FRAMEWORK_CREATED", "AccreditationFramework", framework.id, details=f"Framework {code} created.")
    return framework


def get_framework(session: Session, framework_id: str) -> Optional[AccreditationFramework]:
    return session.query(AccreditationFramework).filter(AccreditationFramework.id == framework_id).first()


def get_framework_by_code(session: Session, code: str) -> Optional[AccreditationFramework]:
    return session.query(AccreditationFramework).filter(AccreditationFramework.code == code.upper()).first()


def get_frameworks(session: Session, active_only: bool = False) -> List[AccreditationFramework]:
    query = session.query(AccreditationFramework)
    if active_only:
        query = query.filter(AccreditationFramework.is_active == True)
    return query.order_by(AccreditationFramework.name).all()


# -----------------------------------------------------------------------------
# 2. CRITERIA & SUBCRITERIA
# -----------------------------------------------------------------------------
def create_criterion(
    session: Session,
    framework_id: str,
    code: str,
    name: str,
    description: str = "",
    weight: float = 100.0,
    required_score: float = 70.0
) -> Criterion:
    """Creates a top-level accreditation criterion."""
    validate_score_range(required_score)
    existing = session.query(Criterion).filter(
        Criterion.framework_id == framework_id,
        Criterion.code == code
    ).first()
    if existing:
        return existing

    criterion = Criterion(
        framework_id=framework_id,
        code=code,
        name=name,
        description=description,
        weight=weight,
        required_score=required_score
    )
    session.add(criterion)
    session.flush()
    create_audit_log(session, "CRITERION_CREATED", "Criterion", criterion.id, details=f"Criterion {code} added.")
    return criterion


def get_criterion(session: Session, criterion_id: str) -> Optional[Criterion]:
    return session.query(Criterion).filter(Criterion.id == criterion_id).first()


def get_criterion_by_code(session: Session, framework_id: str, code: str) -> Optional[Criterion]:
    return session.query(Criterion).filter(
        Criterion.framework_id == framework_id,
        Criterion.code == code
    ).first()


def get_criteria(session: Session, framework_id: Optional[str] = None) -> List[Criterion]:
    query = session.query(Criterion)
    if framework_id:
        query = query.filter(Criterion.framework_id == framework_id)
    return query.order_by(Criterion.code).all()


def create_subcriterion(
    session: Session,
    criterion_id: str,
    code: str,
    name: str,
    description: str = "",
    weight: float = 25.0,
    required_evidence: str = ""
) -> Subcriterion:
    """Creates a subcriterion child record."""
    existing = session.query(Subcriterion).filter(
        Subcriterion.criterion_id == criterion_id,
        Subcriterion.code == code
    ).first()
    if existing:
        return existing

    sub = Subcriterion(
        criterion_id=criterion_id,
        code=code,
        name=name,
        description=description,
        weight=weight,
        required_evidence=required_evidence
    )
    session.add(sub)
    session.flush()
    return sub


def get_subcriteria(session: Session, criterion_id: str) -> List[Subcriterion]:
    return session.query(Subcriterion).filter(Subcriterion.criterion_id == criterion_id).order_by(Subcriterion.code).all()


# -----------------------------------------------------------------------------
# 3. EVIDENCE REQUIREMENTS & MAPPING
# -----------------------------------------------------------------------------
def create_evidence_requirement(
    session: Session,
    criterion_id: str,
    requirement_name: str,
    subcriterion_id: Optional[str] = None,
    description: str = "",
    allowed_file_types: str = "PDF,XLSX,CSV,DOCX",
    minimum_completeness: float = 80.0,
    responsible_department: str = "IQAC"
) -> EvidenceRequirement:
    validate_score_range(minimum_completeness)
    req = EvidenceRequirement(
        criterion_id=criterion_id,
        subcriterion_id=subcriterion_id,
        requirement_name=requirement_name,
        description=description,
        allowed_file_types=allowed_file_types,
        minimum_completeness=minimum_completeness,
        responsible_department=responsible_department
    )
    session.add(req)
    session.flush()
    return req


def get_evidence_requirements(session: Session, criterion_id: Optional[str] = None) -> List[EvidenceRequirement]:
    query = session.query(EvidenceRequirement)
    if criterion_id:
        query = query.filter(EvidenceRequirement.criterion_id == criterion_id)
    return query.all()


def map_evidence_to_requirement(
    session: Session,
    evidence_id: str,
    requirement_id: str,
    match_score: float = 85.0,
    match_reason: str = "Rule-based requirement match",
    matched_by: str = "RULE"
) -> EvidenceRequirementMap:
    """Maps an evidence record to an accreditation requirement."""
    validate_score_range(match_score)
    existing = session.query(EvidenceRequirementMap).filter(
        EvidenceRequirementMap.evidence_id == evidence_id,
        EvidenceRequirementMap.requirement_id == requirement_id
    ).first()
    if existing:
        return existing

    mapping = EvidenceRequirementMap(
        evidence_id=evidence_id,
        requirement_id=requirement_id,
        match_score=match_score,
        match_reason=match_reason,
        matched_by=matched_by
    )
    session.add(mapping)
    session.flush()
    create_audit_log(session, "CRITERION_MATCHED", "EvidenceRequirementMap", mapping.id, details=f"Matched evidence {evidence_id} to requirement {requirement_id} by {matched_by}")
    return mapping


# -----------------------------------------------------------------------------
# 4. EVIDENCE REPOSITORY (IMMUTABLE HISTORY & DEDUPLICATION)
# -----------------------------------------------------------------------------
def create_evidence(
    session: Session,
    filename: str,
    original_filename: str,
    file_hash: str,
    file_type: str = "PDF",
    file_path: str = "",
    file_size: int = 0,
    criterion_id: Optional[str] = None,
    subcriterion_id: Optional[str] = None,
    source_department: str = "VFSTR",
    description: str = "",
    extracted_text: str = "",
    completeness_score: float = 80.0,
    freshness_score: float = 100.0,
    status: str = "UPLOADED",
    applicable_criteria: str = "[]",
    created_by: str = "System"
) -> Tuple[Evidence, bool]:
    """
    Creates an evidence record.
    Returns (evidence, is_new).
    If file_hash already exists, returns existing evidence (is_new = False) to prevent duplicate ingestion.
    """
    validate_score_range(completeness_score)
    validate_score_range(freshness_score)

    existing = session.query(Evidence).filter(Evidence.file_hash == file_hash).first()
    if existing:
        return existing, False

    evidence = Evidence(
        filename=filename,
        original_filename=original_filename,
        file_hash=file_hash,
        file_type=file_type,
        file_path=file_path,
        file_size=file_size,
        criterion_id=criterion_id,
        subcriterion_id=subcriterion_id,
        source_department=source_department,
        description=description,
        extracted_text=extracted_text,
        completeness_score=completeness_score,
        freshness_score=freshness_score,
        applicable_criteria=applicable_criteria,
        status=status,
        created_by=created_by
    )
    session.add(evidence)
    session.flush()
    create_audit_log(session, "EVIDENCE_UPLOADED", "Evidence", evidence.id, details=f"Evidence {filename} uploaded for {source_department}")
    return evidence, True


def get_evidence(session: Session, evidence_id: str) -> Optional[Evidence]:
    return session.query(Evidence).filter(Evidence.id == evidence_id).first()


def get_evidence_by_hash(session: Session, file_hash: str) -> Optional[Evidence]:
    return session.query(Evidence).filter(Evidence.file_hash == file_hash).first()


def get_evidence_by_criterion(session: Session, criterion_id: str) -> List[Evidence]:
    return session.query(Evidence).filter(Evidence.criterion_id == criterion_id).all()


def get_all_evidence(session: Session, department: Optional[str] = None) -> List[Evidence]:
    query = session.query(Evidence)
    if department and department != "All Departments":
        query = query.filter(Evidence.source_department == department)
    return query.order_by(desc(Evidence.created_at)).all()


def update_evidence_status(session: Session, evidence_id: str, new_status: str, notes: str = "") -> Optional[Evidence]:
    ev = get_evidence(session, evidence_id)
    if not ev:
        return None
    old_status = ev.status
    ev.status = new_status
    session.flush()
    create_audit_log(session, "EVIDENCE_PROCESSED", "Evidence", ev.id, old_value=old_status, new_value=new_status, details=notes)
    return ev


# -----------------------------------------------------------------------------
# 5. READINESS SNAPSHOTS & CRITERION SCORING
# -----------------------------------------------------------------------------
def create_readiness_snapshot(
    session: Session,
    framework_id: str,
    overall_score: float,
    status: str = "PARTIAL",
    total_criteria: int = 0,
    ready_criteria: int = 0,
    partial_criteria: int = 0,
    gap_criteria: int = 0,
    calculated_by: str = "AI Readiness Engine"
) -> ReadinessSnapshot:
    validate_score_range(overall_score)
    snapshot = ReadinessSnapshot(
        framework_id=framework_id,
        overall_score=overall_score,
        status=status,
        total_criteria=total_criteria,
        ready_criteria=ready_criteria,
        partial_criteria=partial_criteria,
        gap_criteria=gap_criteria,
        calculated_by=calculated_by
    )
    session.add(snapshot)
    session.flush()
    create_audit_log(session, "READINESS_CALCULATED", "ReadinessSnapshot", snapshot.id, details=f"Readiness calculated: {overall_score}% ({status})")
    return snapshot


def create_criterion_readiness(
    session: Session,
    snapshot_id: str,
    criterion_id: str,
    evidence_score: float,
    completeness_score: float,
    freshness_score: float,
    verification_score: float
) -> CriterionReadiness:
    """Calculates weighted overall criterion readiness using the official formula."""
    validate_score_range(evidence_score)
    validate_score_range(completeness_score)
    validate_score_range(freshness_score)
    validate_score_range(verification_score)

    overall_score = (
        evidence_score * 0.40 +
        completeness_score * 0.30 +
        freshness_score * 0.15 +
        verification_score * 0.15
    )

    status = "READY" if overall_score >= 80.0 else ("PARTIAL" if overall_score >= 60.0 else "GAP")

    rec = CriterionReadiness(
        snapshot_id=snapshot_id,
        criterion_id=criterion_id,
        evidence_score=evidence_score,
        completeness_score=completeness_score,
        freshness_score=freshness_score,
        verification_score=verification_score,
        overall_score=round(overall_score, 2),
        status=status
    )
    session.add(rec)
    session.flush()
    return rec


def get_latest_snapshot(session: Session, framework_id: str) -> Optional[ReadinessSnapshot]:
    return session.query(ReadinessSnapshot).filter(
        ReadinessSnapshot.framework_id == framework_id
    ).order_by(desc(ReadinessSnapshot.calculated_at)).first()


def get_snapshot_history(session: Session, framework_id: str, limit: int = 12) -> List[ReadinessSnapshot]:
    return session.query(ReadinessSnapshot).filter(
        ReadinessSnapshot.framework_id == framework_id
    ).order_by(ReadinessSnapshot.calculated_at).limit(limit).all()


# -----------------------------------------------------------------------------
# 6. GAPS & TASKS
# -----------------------------------------------------------------------------
def create_gap(
    session: Session,
    criterion_id: str,
    title: str,
    description: str = "",
    subcriterion_id: Optional[str] = None,
    requirement_id: Optional[str] = None,
    severity: str = "HIGH",
    impact: float = 8.0,
    effort: float = 5.0,
    recommended_action: str = ""
) -> Gap:
    gap = Gap(
        criterion_id=criterion_id,
        subcriterion_id=subcriterion_id,
        requirement_id=requirement_id,
        title=title,
        description=description,
        severity=severity.upper(),
        impact=impact,
        effort=effort,
        recommended_action=recommended_action,
        status="OPEN"
    )
    session.add(gap)
    session.flush()
    create_audit_log(session, "GAP_CREATED", "Gap", gap.id, details=f"Gap identified: {title} ({severity})")
    return gap


def get_gaps(session: Session, criterion_id: Optional[str] = None) -> List[Gap]:
    query = session.query(Gap)
    if criterion_id:
        query = query.filter(Gap.criterion_id == criterion_id)
    return query.order_by(desc(Gap.detected_at)).all()


def get_open_gaps(session: Session) -> List[Gap]:
    return session.query(Gap).filter(Gap.status.in_(["OPEN", "IN_PROGRESS"])).all()


def resolve_gap(session: Session, gap_id: str, notes: str = "") -> Optional[Gap]:
    gap = session.query(Gap).filter(Gap.id == gap_id).first()
    if not gap:
        return None
    gap.status = "RESOLVED"
    gap.resolved_at = datetime.now()
    session.flush()
    create_audit_log(session, "GAP_RESOLVED", "Gap", gap.id, details=notes)
    return gap


def create_task(
    session: Session,
    criterion_id: str,
    title: str,
    deadline: datetime,
    gap_id: Optional[str] = None,
    description: str = "",
    owner_role: str = "IQAC",
    owner_department: str = "IQAC",
    priority: str = "HIGH"
) -> Task:
    task = Task(
        criterion_id=criterion_id,
        gap_id=gap_id,
        title=title,
        description=description,
        owner_role=owner_role,
        owner_department=owner_department,
        priority=priority.upper(),
        deadline=deadline,
        status="OPEN",
        completion_percentage=0.0
    )
    session.add(task)
    session.flush()
    create_audit_log(session, "TASK_CREATED", "Task", task.id, details=f"Task {title} assigned to {owner_role}")
    return task


def get_tasks(session: Session, status: Optional[str] = None) -> List[Task]:
    query = session.query(Task)
    if status and status != "All":
        query = query.filter(Task.status == status.upper())
    return query.order_by(Task.deadline).all()


def get_open_tasks(session: Session) -> List[Task]:
    return session.query(Task).filter(Task.status.in_(["OPEN", "IN_PROGRESS"])).all()


def update_task_status(session: Session, task_id: str, new_status: str, percentage: Optional[float] = None) -> Optional[Task]:
    task = session.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    old_status = task.status
    task.status = new_status.upper()
    if percentage is not None:
        validate_score_range(percentage)
        task.completion_percentage = percentage
    if new_status.upper() == "COMPLETED":
        task.completed_at = datetime.now()
        task.completion_percentage = 100.0
    session.flush()
    create_audit_log(session, "TASK_UPDATED", "Task", task.id, old_value=old_status, new_value=new_status)
    return task


# -----------------------------------------------------------------------------
# 7. SAR DRAFTS & CITATIONS
# -----------------------------------------------------------------------------
def create_sar_draft(
    session: Session,
    framework_id: str,
    criterion_id: str,
    title: str,
    draft_text: str,
    version: str = "1.0",
    generated_by: str = "AI DRAFT — HUMAN VERIFICATION REQUIRED"
) -> SARDraft:
    """Creates a qualitative SAR draft (always marked as unverified AI draft initially)."""
    draft = SARDraft(
        framework_id=framework_id,
        criterion_id=criterion_id,
        title=title,
        draft_text=draft_text,
        status="DRAFT",
        version=version,
        generated_by=generated_by
    )
    session.add(draft)
    session.flush()
    create_audit_log(session, "SAR_GENERATED", "SARDraft", draft.id, details=f"SAR narrative generated for criterion {criterion_id}")
    return draft


def get_sar_drafts(session: Session, criterion_id: Optional[str] = None) -> List[SARDraft]:
    query = session.query(SARDraft)
    if criterion_id:
        query = query.filter(SARDraft.criterion_id == criterion_id)
    return query.order_by(desc(SARDraft.created_at)).all()


def add_sar_source(
    session: Session,
    sar_draft_id: str,
    evidence_id: str,
    source_reference: str = "",
    relevance_score: float = 1.0
) -> SARSource:
    source = SARSource(
        sar_draft_id=sar_draft_id,
        evidence_id=evidence_id,
        source_reference=source_reference,
        relevance_score=relevance_score
    )
    session.add(source)
    session.flush()
    return source


# -----------------------------------------------------------------------------
# 8. HUMAN VERIFICATIONS (MANDATORY AI GUARDRAIL)
# -----------------------------------------------------------------------------
def create_verification(
    session: Session,
    reviewer_name: str,
    reviewer_role: str,
    decision: str,  # APPROVED, REJECTED, NEEDS_CORRECTION
    evidence_id: Optional[str] = None,
    sar_draft_id: Optional[str] = None,
    comments: str = ""
) -> HumanVerification:
    """
    Records human approval/rejection decision.
    MANDATORY GUARDRAIL: AI cannot create an APPROVED record;
    only this explicit human verification workflow can record it.
    """
    decision_clean = decision.upper()
    if decision_clean not in ["APPROVED", "REJECTED", "NEEDS_CORRECTION"]:
        raise ValueError(f"Invalid verification decision: {decision}. Must be APPROVED, REJECTED, or NEEDS_CORRECTION.")

    verif = HumanVerification(
        evidence_id=evidence_id,
        sar_draft_id=sar_draft_id,
        reviewer_name=reviewer_name,
        reviewer_role=reviewer_role,
        decision=decision_clean,
        comments=comments
    )
    session.add(verif)

    # If verifying evidence, update evidence status
    if evidence_id:
        ev = get_evidence(session, evidence_id)
        if ev:
            old_status = ev.status
            ev.status = "VERIFIED" if decision_clean == "APPROVED" else ("REJECTED" if decision_clean == "REJECTED" else "INCOMPLETE")
            create_audit_log(session, "EVIDENCE_VERIFIED" if decision_clean == "APPROVED" else "EVIDENCE_REJECTED", "Evidence", ev.id, old_value=old_status, new_value=ev.status, details=f"Reviewed by {reviewer_name} ({reviewer_role})")

    # If verifying SAR draft, update SAR status
    if sar_draft_id:
        sar = session.query(SARDraft).filter(SARDraft.id == sar_draft_id).first()
        if sar:
            sar.status = "VERIFIED" if decision_clean == "APPROVED" else "REJECTED"

    session.flush()
    return verif


def get_verifications(session: Session, evidence_id: Optional[str] = None) -> List[HumanVerification]:
    query = session.query(HumanVerification)
    if evidence_id:
        query = query.filter(HumanVerification.evidence_id == evidence_id)
    return query.order_by(desc(HumanVerification.verified_at)).all()


# -----------------------------------------------------------------------------
# 9. AUDIT LOG (COMPLETE TRACEABILITY)
# -----------------------------------------------------------------------------
def create_audit_log(
    session: Session,
    action: str,
    object_type: str,
    object_id: str,
    user_id: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    details: str = ""
) -> AuditLog:
    """Records an immutable audit event."""
    log = AuditLog(
        action=action,
        user_id=user_id,
        object_type=object_type,
        object_id=str(object_id),
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        details=details
    )
    session.add(log)
    session.flush()
    return log


def get_audit_logs(session: Session, limit: int = 100) -> List[AuditLog]:
    return session.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit).all()
