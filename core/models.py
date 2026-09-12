"""
SQLAlchemy ORM Models for VFSTR Vignan Accreditation AI Agent Database.
Defines all 15 relational tables, foreign key constraints, indexes, and relationships.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Index, Enum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AccreditationFramework(Base):
    """TABLE 1: Stores accreditation frameworks such as NAAC, NBA, NIRF."""
    __tablename__ = "accreditation_frameworks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    version = Column(String(20), default="2024.1")
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    criteria = relationship("Criterion", back_populates="framework", cascade="all, delete-orphan")
    snapshots = relationship("ReadinessSnapshot", back_populates="framework", cascade="all, delete-orphan")
    sar_drafts = relationship("SARDraft", back_populates="framework")


class Criterion(Base):
    """TABLE 2: Stores top-level accreditation criteria."""
    __tablename__ = "criteria"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    framework_id = Column(String(36), ForeignKey("accreditation_frameworks.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(20), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    weight = Column(Float, default=100.0)
    required_score = Column(Float, default=70.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    framework = relationship("AccreditationFramework", back_populates="criteria")
    subcriteria = relationship("Subcriterion", back_populates="criterion", cascade="all, delete-orphan")
    evidence_requirements = relationship("EvidenceRequirement", back_populates="criterion", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="criterion")
    gaps = relationship("Gap", back_populates="criterion", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="criterion", cascade="all, delete-orphan")
    sar_drafts = relationship("SARDraft", back_populates="criterion")
    readiness_records = relationship("CriterionReadiness", back_populates="criterion")


class Subcriterion(Base):
    """TABLE 3: Stores detailed subcriteria under each criterion."""
    __tablename__ = "subcriteria"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    criterion_id = Column(String(36), ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(20), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    weight = Column(Float, default=25.0)
    required_evidence = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    criterion = relationship("Criterion", back_populates="subcriteria")
    evidence_requirements = relationship("EvidenceRequirement", back_populates="subcriterion")
    evidence_items = relationship("Evidence", back_populates="subcriterion")
    gaps = relationship("Gap", back_populates="subcriterion")


class Evidence(Base):
    """TABLE 4: Stores all uploaded institutional accreditation evidence documents."""
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), default="PDF")
    file_path = Column(String(500), default="")
    file_hash = Column(String(64), nullable=False, index=True)
    file_size = Column(Integer, default=0)
    criterion_id = Column(String(36), ForeignKey("criteria.id", ondelete="SET NULL"), nullable=True, index=True)
    subcriterion_id = Column(String(36), ForeignKey("subcriteria.id", ondelete="SET NULL"), nullable=True)
    source_department = Column(String(100), default="VFSTR")
    description = Column(Text, default="")
    extracted_text = Column(Text, default="")
    upload_date = Column(DateTime, default=datetime.now)
    document_date = Column(DateTime, default=datetime.now)
    valid_from = Column(DateTime, default=datetime.now)
    valid_to = Column(DateTime, nullable=True)
    completeness_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=100.0)
    relevance_score = Column(Float, default=0.0)
    applicable_criteria = Column(Text, default="[]")
    status = Column(String(50), default="UPLOADED")  # UPLOADED, PROCESSING, PROCESSED, INCOMPLETE, INSUFFICIENT, PENDING_VERIFICATION, VERIFIED, REJECTED
    created_by = Column(String(100), default="System")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    criterion = relationship("Criterion", back_populates="evidence_items")
    subcriterion = relationship("Subcriterion", back_populates="evidence_items")
    requirement_maps = relationship("EvidenceRequirementMap", back_populates="evidence", cascade="all, delete-orphan")
    sar_sources = relationship("SARSource", back_populates="evidence")
    verifications = relationship("HumanVerification", back_populates="evidence")


class EvidenceRequirement(Base):
    """TABLE 5: Defines required evidence specifications per criterion/subcriterion."""
    __tablename__ = "evidence_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    criterion_id = Column(String(36), ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    subcriterion_id = Column(String(36), ForeignKey("subcriteria.id", ondelete="SET NULL"), nullable=True)
    requirement_name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    required = Column(Boolean, default=True)
    allowed_file_types = Column(String(100), default="PDF,XLSX,CSV,DOCX")
    minimum_completeness = Column(Float, default=80.0)
    validity_period_days = Column(Integer, default=365)
    responsible_department = Column(String(100), default="IQAC")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    criterion = relationship("Criterion", back_populates="evidence_requirements")
    subcriterion = relationship("Subcriterion", back_populates="evidence_requirements")
    requirement_maps = relationship("EvidenceRequirementMap", back_populates="requirement", cascade="all, delete-orphan")
    gaps = relationship("Gap", back_populates="requirement")


class EvidenceRequirementMap(Base):
    """TABLE 6: Maps uploaded evidence documents to specific accreditation requirements."""
    __tablename__ = "evidence_requirement_map"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String(36), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    requirement_id = Column(String(36), ForeignKey("evidence_requirements.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, default=0.0)
    match_reason = Column(Text, default="")
    matched_by = Column(String(50), default="RULE")  # RULE, KEYWORD, SEMANTIC_SEARCH, AI, HUMAN
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    evidence = relationship("Evidence", back_populates="requirement_maps")
    requirement = relationship("EvidenceRequirement", back_populates="requirement_maps")


class ReadinessSnapshot(Base):
    """TABLE 7: Historical readiness assessment snapshots over time."""
    __tablename__ = "readiness_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    framework_id = Column(String(36), ForeignKey("accreditation_frameworks.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float, default=0.0)
    status = Column(String(20), default="GAP")  # READY, PARTIAL, GAP
    total_criteria = Column(Integer, default=0)
    ready_criteria = Column(Integer, default=0)
    partial_criteria = Column(Integer, default=0)
    gap_criteria = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=datetime.now)
    calculated_by = Column(String(100), default="AI Readiness Engine")

    # Relationships
    framework = relationship("AccreditationFramework", back_populates="snapshots")
    criterion_records = relationship("CriterionReadiness", back_populates="snapshot", cascade="all, delete-orphan")


class CriterionReadiness(Base):
    """TABLE 8: Criterion-level scoring breakdown for a specific readiness snapshot."""
    __tablename__ = "criterion_readiness"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_id = Column(String(36), ForeignKey("readiness_snapshots.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(String(36), ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    evidence_score = Column(Float, default=0.0)
    completeness_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=0.0)
    verification_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    status = Column(String(20), default="GAP")  # READY (80-100), PARTIAL (60-79), GAP (0-59)
    calculated_at = Column(DateTime, default=datetime.now)

    # Relationships
    snapshot = relationship("ReadinessSnapshot", back_populates="criterion_records")
    criterion = relationship("Criterion", back_populates="readiness_records")


class Gap(Base):
    """TABLE 9: Stores identified accreditation evidence gaps and missing requirements."""
    __tablename__ = "gaps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    criterion_id = Column(String(36), ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False, index=True)
    subcriterion_id = Column(String(36), ForeignKey("subcriteria.id", ondelete="SET NULL"), nullable=True)
    requirement_id = Column(String(36), ForeignKey("evidence_requirements.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    severity = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    impact = Column(Float, default=8.0)
    effort = Column(Float, default=5.0)
    recommended_action = Column(Text, default="")
    status = Column(String(20), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, IGNORED
    detected_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    criterion = relationship("Criterion", back_populates="gaps")
    subcriterion = relationship("Subcriterion", back_populates="gaps")
    requirement = relationship("EvidenceRequirement", back_populates="gaps")
    tasks = relationship("Task", back_populates="gap", cascade="all, delete-orphan")


class Task(Base):
    """TABLE 10: Actionable corrective remediation tasks created from gaps."""
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gap_id = Column(String(36), ForeignKey("gaps.id", ondelete="SET NULL"), nullable=True)
    criterion_id = Column(String(36), ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    owner_role = Column(String(100), default="IQAC")  # IQAC, Placement Cell, Research Cell, Academic Department, Administration, Student Affairs
    owner_department = Column(String(100), default="IQAC")
    priority = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    deadline = Column(DateTime, nullable=False)
    status = Column(String(20), default="OPEN", index=True)  # OPEN, IN_PROGRESS, COMPLETED, OVERDUE, CANCELLED
    completion_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    gap = relationship("Gap", back_populates="tasks")
    criterion = relationship("Criterion", back_populates="tasks")


class SARDraft(Base):
    """TABLE 11: Self Assessment Report (SAR/SSR) qualitative narrative drafts."""
    __tablename__ = "sar_drafts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    framework_id = Column(String(36), ForeignKey("accreditation_frameworks.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(String(36), ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    draft_text = Column(Text, default="")
    status = Column(String(50), default="DRAFT")  # DRAFT, UNDER_REVIEW, VERIFIED, REJECTED
    version = Column(String(20), default="1.0")
    generated_by = Column(String(100), default="AI DRAFT — HUMAN VERIFICATION REQUIRED")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    framework = relationship("AccreditationFramework", back_populates="sar_drafts")
    criterion = relationship("Criterion", back_populates="sar_drafts")
    sources = relationship("SARSource", back_populates="sar_draft", cascade="all, delete-orphan")
    verifications = relationship("HumanVerification", back_populates="sar_draft")


class SARSource(Base):
    """TABLE 12: Source evidence citations linked to SAR drafts."""
    __tablename__ = "sar_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sar_draft_id = Column(String(36), ForeignKey("sar_drafts.id", ondelete="CASCADE"), nullable=False)
    evidence_id = Column(String(36), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    source_reference = Column(String(255), default="")
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    sar_draft = relationship("SARDraft", back_populates="sources")
    evidence = relationship("Evidence", back_populates="sar_sources")


class HumanVerification(Base):
    """TABLE 13: Human reviewer verification and approval decisions (AI Guardrail)."""
    __tablename__ = "human_verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String(36), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=True)
    sar_draft_id = Column(String(36), ForeignKey("sar_drafts.id", ondelete="CASCADE"), nullable=True)
    reviewer_name = Column(String(100), nullable=False)
    reviewer_role = Column(String(100), nullable=False)
    decision = Column(String(50), nullable=False)  # APPROVED, REJECTED, NEEDS_CORRECTION
    comments = Column(Text, default="")
    verified_at = Column(DateTime, default=datetime.now)

    # Relationships
    evidence = relationship("Evidence", back_populates="verifications")
    sar_draft = relationship("SARDraft", back_populates="verifications")


class User(Base):
    """TABLE 14: Application users and institutional roles."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    role = Column(String(50), default="FACULTY")  # ADMIN, IQAC, ACCREDITATION_COORDINATOR, HOD, FACULTY, REVIEWER
    department = Column(String(100), default="VFSTR")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")


class AuditLog(Base):
    """TABLE 15: Complete immutable system audit trail for all operations."""
    __tablename__ = "audit_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(100), nullable=False)  # EVIDENCE_UPLOADED, EVIDENCE_PROCESSED, CRITERION_MATCHED, READINESS_CALCULATED, GAP_CREATED, TASK_CREATED, SAR_GENERATED, VERIFICATION_REQUESTED, EVIDENCE_VERIFIED, EVIDENCE_REJECTED
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    object_type = Column(String(100), nullable=False)  # Evidence, Criterion, Gap, Task, SARDraft, Verification
    object_id = Column(String(36), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    details = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.now, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
