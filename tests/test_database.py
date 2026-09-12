"""
Comprehensive Test Suite for VFSTR Vignan Accreditation Database Backend.
Tests database initialization, 15 relational tables, CRUD operations, foreign keys,
duplicate hash detection, score range validations, human verification guardrails, and health checks.
"""

import os
import tempfile
import pytest
import unittest
from datetime import datetime, timedelta

from core.database import (
    init_db, get_engine, get_session_factory, get_db_session,
    database_health_check, Base
)
from core.models import (
    AccreditationFramework, Criterion, Subcriterion, Evidence,
    EvidenceRequirement, EvidenceRequirementMap, ReadinessSnapshot,
    CriterionReadiness, Gap, Task, SARDraft, SARSource,
    HumanVerification, User, AuditLog
)
from core.repository import (
    create_framework, get_framework, get_framework_by_code, get_frameworks,
    create_criterion, get_criterion, get_criterion_by_code, get_criteria,
    create_subcriterion, get_subcriteria,
    create_evidence_requirement, get_evidence_requirements,
    create_evidence, get_evidence, get_evidence_by_hash, get_evidence_by_criterion,
    get_all_evidence, update_evidence_status, map_evidence_to_requirement,
    create_readiness_snapshot, create_criterion_readiness, get_latest_snapshot, get_snapshot_history,
    create_gap, get_gaps, get_open_gaps, resolve_gap,
    create_task, get_tasks, get_open_tasks, update_task_status,
    create_sar_draft, get_sar_drafts, add_sar_source,
    create_verification, get_verifications,
    create_audit_log, get_audit_logs
)
from core.seed_database import seed_demo_data


class TestAccreditationDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.test_db_path = os.path.join(cls.temp_dir.name, "test_accreditation.db")
        os.environ["ACCREDITATION_DB_PATH"] = cls.test_db_path
        init_db(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_database_initialization(self):
        """Validates that init_db creates all 15 required tables and indexes."""
        engine = get_engine(self.test_db_path)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        
        expected_tables = {
            "accreditation_frameworks", "criteria", "subcriteria", "evidence",
            "evidence_requirements", "evidence_requirement_map", "readiness_snapshots",
            "criterion_readiness", "gaps", "tasks", "sar_drafts", "sar_sources",
            "human_verifications", "users", "audit_log"
        }
        self.assertTrue(expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}")

    def test_02_framework_crud(self):
        """Tests framework creation, unique code enforcement, and retrieval."""
        with get_db_session(self.test_db_path) as session:
            fw = create_framework(session, name="National Board of Accreditation", code="NBA", version="2024.1")
            self.assertIsNotNone(fw.id)
            self.assertEqual(fw.code, "NBA")

            fetched = get_framework_by_code(session, "NBA")
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.name, "National Board of Accreditation")

    def test_03_criterion_and_subcriterion_crud(self):
        """Tests criterion and subcriterion creation with parent-child relationship."""
        with get_db_session(self.test_db_path) as session:
            fw = get_framework_by_code(session, "NBA")
            crit = create_criterion(session, framework_id=fw.id, code="NBA-1", name="Vision, Mission and PEOs", weight=50.0, required_score=75.0)
            self.assertIsNotNone(crit.id)

            sub = create_subcriterion(session, criterion_id=crit.id, code="NBA-1.1", name="State Vision and Mission", weight=25.0)
            self.assertIsNotNone(sub.id)

            sub_list = get_subcriteria(session, criterion_id=crit.id)
            self.assertGreater(len(sub_list), 0)
            self.assertEqual(sub_list[0].code, "NBA-1.1")

    def test_04_evidence_creation_and_deduplication(self):
        """Tests evidence creation and duplicate hash prevention."""
        with get_db_session(self.test_db_path) as session:
            fw = get_framework_by_code(session, "NBA")
            crit = get_criterion_by_code(session, fw.id, "NBA-1")
            
            file_hash = "abc1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            ev1, is_new1 = create_evidence(
                session=session,
                filename="vision_mission_document.pdf",
                original_filename="Vision_Mission_2024.pdf",
                file_hash=file_hash,
                criterion_id=crit.id,
                source_department="Academic Affairs",
                completeness_score=90.0
            )
            self.assertTrue(is_new1)
            self.assertIsNotNone(ev1.id)

            # Try inserting duplicate hash
            ev2, is_new2 = create_evidence(
                session=session,
                filename="duplicate_vision_mission.pdf",
                original_filename="Vision_Mission_2024_copy.pdf",
                file_hash=file_hash,
                criterion_id=crit.id
            )
            self.assertFalse(is_new2)
            self.assertEqual(ev1.id, ev2.id, "Duplicate file_hash must return existing evidence record")

    def test_05_score_validation_guardrails(self):
        """Tests that invalid scores (<0 or >100) raise ValueError."""
        with get_db_session(self.test_db_path) as session:
            fw = get_framework_by_code(session, "NBA")
            crit = get_criterion_by_code(session, fw.id, "NBA-1")

            # Score > 100
            with self.assertRaises(ValueError):
                create_evidence(
                    session=session,
                    filename="invalid_score.pdf",
                    original_filename="invalid.pdf",
                    file_hash="hash_invalid_score_1",
                    completeness_score=150.0  # Invalid
                )

            # Score < 0
            with self.assertRaises(ValueError):
                create_evidence(
                    session=session,
                    filename="negative_score.pdf",
                    original_filename="negative.pdf",
                    file_hash="hash_invalid_score_2",
                    completeness_score=-10.0  # Invalid
                )

    def test_06_gaps_and_tasks_lifecycle(self):
        """Tests gap identification, task assignment, status transitions, and resolution."""
        with get_db_session(self.test_db_path) as session:
            fw = get_framework_by_code(session, "NBA")
            crit = get_criterion_by_code(session, fw.id, "NBA-1")

            gap = create_gap(
                session=session,
                criterion_id=crit.id,
                title="Stakeholder advisory consultation missing",
                description="PEOs review lacks industry advisory council endorsement.",
                severity="HIGH"
            )
            self.assertIsNotNone(gap.id)
            self.assertEqual(gap.status, "OPEN")

            task = create_task(
                session=session,
                criterion_id=crit.id,
                gap_id=gap.id,
                title="Convene Industry Advisory Board meeting",
                deadline=datetime.now() + timedelta(days=15),
                owner_role="Academic Department",
                priority="HIGH"
            )
            self.assertIsNotNone(task.id)
            self.assertEqual(task.status, "OPEN")

            # Update task status
            updated_task = update_task_status(session, task.id, "COMPLETED", percentage=100.0)
            self.assertEqual(updated_task.status, "COMPLETED")
            self.assertEqual(updated_task.completion_percentage, 100.0)

            # Resolve gap
            resolved = resolve_gap(session, gap.id, notes="Advisory board ratified PEOs.")
            self.assertEqual(resolved.status, "RESOLVED")

    def test_07_sar_draft_and_source_traceability(self):
        """Tests SAR narrative drafting and evidence citation traceability."""
        with get_db_session(self.test_db_path) as session:
            fw = get_framework_by_code(session, "NBA")
            crit = get_criterion_by_code(session, fw.id, "NBA-1")
            ev = get_evidence_by_criterion(session, crit.id)[0]

            sar = create_sar_draft(
                session=session,
                framework_id=fw.id,
                criterion_id=crit.id,
                title="NBA Criterion 1 SAR Narrative",
                draft_text="The institution has clearly stated Vision and Mission published on portal...",
                generated_by="AI DRAFT — HUMAN VERIFICATION REQUIRED"
            )
            self.assertIsNotNone(sar.id)
            self.assertEqual(sar.status, "DRAFT")
            self.assertEqual(sar.generated_by, "AI DRAFT — HUMAN VERIFICATION REQUIRED")

            # Add source citation
            source = add_sar_source(session, sar.id, ev.id, source_reference="Vision Mission Manual 2024", relevance_score=0.95)
            self.assertIsNotNone(source.id)

    def test_08_human_verification_guardrail(self):
        """
        Tests the Human Verification Guardrail:
        - AI cannot create an APPROVED record
        - Only human verification can transition evidence or SAR to APPROVED/VERIFIED
        - Invalid decisions are rejected
        """
        with get_db_session(self.test_db_path) as session:
            fw = get_framework_by_code(session, "NBA")
            crit = get_criterion_by_code(session, fw.id, "NBA-1")
            ev = get_evidence_by_criterion(session, crit.id)[0]

            # Invalid decision rejected
            with self.assertRaises(ValueError):
                create_verification(
                    session=session,
                    reviewer_name="System Agent",
                    reviewer_role="AI",
                    decision="AUTO_APPROVED",  # Invalid
                    evidence_id=ev.id
                )

            # Human reviewer approves
            verif = create_verification(
                session=session,
                reviewer_name="Dr. K. Ramamohan",
                reviewer_role="Director IQAC",
                decision="APPROVED",
                evidence_id=ev.id,
                comments="Document physically verified with seal."
            )
            self.assertIsNotNone(verif.id)
            self.assertEqual(verif.decision, "APPROVED")

            # Evidence status transitioned to VERIFIED
            refreshed_ev = get_evidence(session, ev.id)
            self.assertEqual(refreshed_ev.status, "VERIFIED")

    def test_09_audit_log_traceability(self):
        """Tests that state-changing actions generate immutable audit log records."""
        with get_db_session(self.test_db_path) as session:
            logs = get_audit_logs(session, limit=20)
            self.assertGreater(len(logs), 0)
            actions = [l.action for l in logs]
            self.assertTrue(any("EVIDENCE_" in a or "FRAMEWORK_" in a or "CRITERION_" in a for a in actions))

    def test_10_seed_demo_data_and_health_check(self):
        """Tests complete seed_demo_data execution and database_health_check."""
        seed_demo_data(db_path=self.test_db_path)
        health = database_health_check(self.test_db_path)
        
        self.assertEqual(health["database"], "OK")
        self.assertEqual(health["tables"], "OK")
        self.assertEqual(health["foreign_keys"], "OK")
        self.assertEqual(health["seed_data"], "OK")
        self.assertEqual(health["duplicate_hashes"], "OK")
        self.assertEqual(health["score_validation"], "OK")
        self.assertEqual(health["status"], "HEALTHY")


if __name__ == "__main__":
    unittest.main()
