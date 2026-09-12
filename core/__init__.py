"""
VFSTR AI Accreditation Academic Agent - Core Package
Exports all core evaluation, scoring, gap analysis, database, models, and narrative engines.
"""

from core.criteria_registry import (
    get_framework_criteria,
    get_all_metrics_flat,
    NAAC_CRITERIA,
    NBA_CRITERIA
)
from core.vignan_demo_data import (
    get_demo_evidence_list,
    VIGNAN_DEPARTMENTS,
    VIGNAN_ACADEMIC_YEARS,
    VIGNAN_EVIDENCE_STORE
)
from core.evidence_engine import EvidenceEngine
from core.scoring_engine import ScoringEngine
from core.gap_matrix_engine import GapMatrixEngine
from core.ranking_engine import (
    RankingEngine,
    NIRF_PARAMETERS,
    QS_PARAMETERS,
    VIGNAN_NIRF_BASELINE
)
from core.obe_mapping_engine import (
    OBEMappingEngine,
    VIGNAN_OBE_DATA
)
from core.task_manager import TaskManager, DEFAULT_VIGNAN_TASKS
from core.narrative_generator import NarrativeGenerator
from core.audit_verifier import AuditVerifier, DEFAULT_AUDIT_LOGS
from core.evidence_validator import EvidenceValidator, REQUIRED_FORMAT_RULES
from core.continuous_scanner import ContinuousReadinessScanner
from core.submission_builder import SubmissionPackageBuilder
from core.mock_visit_engine import MockVisitSimulatorEngine, PEER_VISIT_QUESTION_BANK
from core.pdf_exporter import (
    generate_accreditation_dossier_pdf,
    VignanReportPDF,
    _clean_pdf_text
)
from core.api_client import (
    AccreditationApiClient,
    get_api_client,
    get_backend_url,
    BACKEND_API_BASE,
    DEFAULT_BACKEND_PORT,
    DEFAULT_BACKEND_URL
)
from core.database import (
    init_db,
    get_engine,
    get_db_session,
    get_db,
    get_connection,
    database_health_check,
    get_database,
    DatabaseManager,
    normalize_evidence_dict,
    ensure_db_dir,
    ACCREDITATION_DB_PATH,
    DEFAULT_DB_PATH,
    DB_FILE_PATH,
    DATA_DIR,
    BASE_DIR
)
from core.models import (
    Base,
    AccreditationFramework,
    Criterion,
    Subcriterion,
    Evidence,
    EvidenceRequirement,
    EvidenceRequirementMap,
    ReadinessSnapshot,
    CriterionReadiness,
    Gap,
    Task,
    SARDraft,
    SARSource,
    HumanVerification,
    User,
    AuditLog
)
from core.seed_database import seed_demo_data
import core.repository as repository
import core.schemas as schemas

__all__ = [
    # Criteria Registry
    "get_framework_criteria",
    "get_all_metrics_flat",
    "NAAC_CRITERIA",
    "NBA_CRITERIA",

    # Demo / Institutional Data
    "get_demo_evidence_list",
    "VIGNAN_DEPARTMENTS",
    "VIGNAN_ACADEMIC_YEARS",
    "VIGNAN_EVIDENCE_STORE",

    # Core AI Engines
    "EvidenceEngine",
    "ScoringEngine",
    "GapMatrixEngine",
    "RankingEngine",
    "NIRF_PARAMETERS",
    "QS_PARAMETERS",
    "VIGNAN_NIRF_BASELINE",
    "OBEMappingEngine",
    "VIGNAN_OBE_DATA",
    "EvidenceValidator",
    "REQUIRED_FORMAT_RULES",
    "ContinuousReadinessScanner",
    "SubmissionPackageBuilder",
    "MockVisitSimulatorEngine",
    "PEER_VISIT_QUESTION_BANK",
    "TaskManager",
    "DEFAULT_VIGNAN_TASKS",
    "NarrativeGenerator",
    "AuditVerifier",
    "DEFAULT_AUDIT_LOGS",

    # PDF & API Utilities
    "generate_accreditation_dossier_pdf",
    "VignanReportPDF",
    "_clean_pdf_text",
    "AccreditationApiClient",
    "get_api_client",
    "get_backend_url",
    "BACKEND_API_BASE",
    "DEFAULT_BACKEND_PORT",
    "DEFAULT_BACKEND_URL",

    # Database & ORM
    "init_db",
    "get_engine",
    "get_db_session",
    "get_db",
    "get_connection",
    "database_health_check",
    "get_database",
    "DatabaseManager",
    "normalize_evidence_dict",
    "ensure_db_dir",
    "ACCREDITATION_DB_PATH",
    "DEFAULT_DB_PATH",
    "DB_FILE_PATH",
    "DATA_DIR",
    "BASE_DIR",

    # ORM Models
    "Base",
    "AccreditationFramework",
    "Criterion",
    "Subcriterion",
    "Evidence",
    "EvidenceRequirement",
    "EvidenceRequirementMap",
    "ReadinessSnapshot",
    "CriterionReadiness",
    "Gap",
    "Task",
    "SARDraft",
    "SARSource",
    "HumanVerification",
    "User",
    "AuditLog",

    # Database Seeding & Submodules
    "seed_demo_data",
    "repository",
    "schemas"
]
