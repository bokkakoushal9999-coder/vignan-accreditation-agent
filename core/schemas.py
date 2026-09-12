"""
Pydantic Schemas and Validation Models for Vignan Accreditation AI Agent.
Enforces data integrity, score constraints (0-100), enumerations, and validation guardrails.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# --- Enums ---
class FrameworkCodeEnum(str, Enum):
    NAAC = "NAAC"
    NBA = "NBA"
    NIRF = "NIRF"
    ABET = "ABET"


class EvidenceStatusEnum(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    INCOMPLETE = "INCOMPLETE"
    INSUFFICIENT = "INSUFFICIENT"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class MatchedByEnum(str, Enum):
    RULE = "RULE"
    KEYWORD = "KEYWORD"
    SEMANTIC_SEARCH = "SEMANTIC_SEARCH"
    AI = "AI"
    HUMAN = "HUMAN"


class ReadinessStatusEnum(str, Enum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    GAP = "GAP"


class SeverityEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PriorityEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GapStatusEnum(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class TaskStatusEnum(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class SARDraftStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class HumanDecisionEnum(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_CORRECTION = "NEEDS_CORRECTION"


class UserRoleEnum(str, Enum):
    ADMIN = "ADMIN"
    IQAC = "IQAC"
    ACCREDITATION_COORDINATOR = "ACCREDITATION_COORDINATOR"
    HOD = "HOD"
    FACULTY = "FACULTY"
    REVIEWER = "REVIEWER"


class AuditActionEnum(str, Enum):
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED"
    EVIDENCE_PROCESSED = "EVIDENCE_PROCESSED"
    CRITERION_MATCHED = "CRITERION_MATCHED"
    READINESS_CALCULATED = "READINESS_CALCULATED"
    GAP_CREATED = "GAP_CREATED"
    TASK_CREATED = "TASK_CREATED"
    SAR_GENERATED = "SAR_GENERATED"
    VERIFICATION_REQUESTED = "VERIFICATION_REQUESTED"
    EVIDENCE_VERIFIED = "EVIDENCE_VERIFIED"
    EVIDENCE_REJECTED = "EVIDENCE_REJECTED"


# --- Validation Helper ---
def validate_score_range(v: float) -> float:
    if v < 0.0 or v > 100.0:
        raise ValueError(f"Score must be between 0.0 and 100.0 (received {v})")
    return round(float(v), 2)


# --- Framework Schemas ---
class FrameworkCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    version: str = "2024.1"
    description: str = ""
    is_active: bool = True


class FrameworkOut(FrameworkCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Criterion Schemas ---
class CriterionCreate(BaseModel):
    framework_id: str
    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=2, max_length=255)
    description: str = ""
    weight: float = Field(default=100.0, ge=0.0)
    required_score: float = Field(default=70.0)
    is_active: bool = True

    @field_validator("required_score")
    @classmethod
    def check_score(cls, v):
        return validate_score_range(v)


class CriterionOut(CriterionCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Subcriterion Schemas ---
class SubcriterionCreate(BaseModel):
    criterion_id: str
    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=2, max_length=255)
    description: str = ""
    weight: float = Field(default=25.0, ge=0.0)
    required_evidence: str = ""


class SubcriterionOut(SubcriterionCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Evidence Requirement Schemas ---
class EvidenceRequirementCreate(BaseModel):
    criterion_id: str
    subcriterion_id: Optional[str] = None
    requirement_name: str = Field(..., min_length=2, max_length=255)
    description: str = ""
    required: bool = True
    allowed_file_types: str = "PDF,XLSX,CSV,DOCX"
    minimum_completeness: float = Field(default=80.0)
    validity_period_days: int = Field(default=365, ge=1)
    responsible_department: str = "IQAC"

    @field_validator("minimum_completeness")
    @classmethod
    def check_completeness(cls, v):
        return validate_score_range(v)


class EvidenceRequirementOut(EvidenceRequirementCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Evidence Schemas ---
class EvidenceCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_type: str = "PDF"
    file_path: str = ""
    file_hash: str = Field(..., min_length=8, max_length=64)
    file_size: int = Field(default=0, ge=0)
    criterion_id: Optional[str] = None
    subcriterion_id: Optional[str] = None
    source_department: str = "VFSTR"
    description: str = ""
    extracted_text: str = ""
    upload_date: Optional[datetime] = None
    document_date: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    completeness_score: float = Field(default=0.0)
    freshness_score: float = Field(default=100.0)
    relevance_score: float = Field(default=0.0)
    status: EvidenceStatusEnum = EvidenceStatusEnum.UPLOADED
    created_by: str = "System"

    @field_validator("completeness_score", "freshness_score", "relevance_score")
    @classmethod
    def check_scores(cls, v):
        return validate_score_range(v)


class EvidenceOut(EvidenceCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Gap Schemas ---
class GapCreate(BaseModel):
    criterion_id: str
    subcriterion_id: Optional[str] = None
    requirement_id: Optional[str] = None
    title: str = Field(..., min_length=3, max_length=255)
    description: str = ""
    severity: SeverityEnum = SeverityEnum.HIGH
    impact: float = Field(default=8.0, ge=0.0, le=10.0)
    effort: float = Field(default=5.0, ge=0.0, le=10.0)
    recommended_action: str = ""
    status: GapStatusEnum = GapStatusEnum.OPEN


class GapOut(GapCreate):
    id: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Task Schemas ---
class TaskCreate(BaseModel):
    gap_id: Optional[str] = None
    criterion_id: str
    title: str = Field(..., min_length=3, max_length=255)
    description: str = ""
    owner_role: str = "IQAC"
    owner_department: str = "IQAC"
    priority: PriorityEnum = PriorityEnum.HIGH
    deadline: datetime
    status: TaskStatusEnum = TaskStatusEnum.OPEN
    completion_percentage: float = Field(default=0.0)

    @field_validator("completion_percentage")
    @classmethod
    def check_completion(cls, v):
        return validate_score_range(v)


class TaskOut(TaskCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- SAR Draft Schemas ---
class SARDraftCreate(BaseModel):
    framework_id: str
    criterion_id: str
    title: str = Field(..., min_length=3, max_length=255)
    draft_text: str = ""
    status: SARDraftStatusEnum = SARDraftStatusEnum.DRAFT
    version: str = "1.0"
    generated_by: str = "AI DRAFT — HUMAN VERIFICATION REQUIRED"


class SARDraftOut(SARDraftCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Human Verification Schemas ---
class HumanVerificationCreate(BaseModel):
    evidence_id: Optional[str] = None
    sar_draft_id: Optional[str] = None
    reviewer_name: str = Field(..., min_length=2, max_length=100)
    reviewer_role: str = Field(..., min_length=2, max_length=100)
    decision: HumanDecisionEnum = HumanDecisionEnum.APPROVED
    comments: str = ""

    @field_validator("decision")
    @classmethod
    def check_human_guardrail(cls, v):
        # Enforce that only valid human decisions can be recorded
        if v not in [HumanDecisionEnum.APPROVED, HumanDecisionEnum.REJECTED, HumanDecisionEnum.NEEDS_CORRECTION]:
            raise ValueError(f"Invalid verification decision: {v}")
        return v


class HumanVerificationOut(HumanVerificationCreate):
    id: str
    verified_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Audit Log Schemas ---
class AuditLogCreate(BaseModel):
    action: str
    user_id: Optional[str] = None
    object_type: str
    object_id: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    details: str = ""


class AuditLogOut(AuditLogCreate):
    id: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
