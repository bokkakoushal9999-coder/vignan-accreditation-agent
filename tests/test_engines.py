"""
Unit & Integration Tests for AI Accreditation Academic Agent Engines.
"""

import unittest
from core.criteria_registry import get_framework_criteria, get_all_metrics_flat
from core.vignan_demo_data import get_demo_evidence_list
from core.evidence_engine import EvidenceEngine
from core.scoring_engine import ScoringEngine
from core.gap_matrix_engine import GapMatrixEngine
from core.task_manager import TaskManager
from core.narrative_generator import NarrativeGenerator
from core.audit_verifier import AuditVerifier
from core.pdf_exporter import generate_accreditation_dossier_pdf


class TestAccreditationAgent(unittest.TestCase):

    def setUp(self):
        self.evidence_list = get_demo_evidence_list()
        self.ev_engine = EvidenceEngine()
        self.scoring_engine = ScoringEngine()
        self.gap_engine = GapMatrixEngine()
        self.task_mgr = TaskManager()
        self.narrative_gen = NarrativeGenerator()
        self.audit_verifier = AuditVerifier()

    def test_criteria_registry(self):
        naac = get_framework_criteria("NAAC")
        nba = get_framework_criteria("NBA")
        self.assertEqual(len(naac), 7)
        self.assertEqual(len(nba), 10)
        
        naac_flat = get_all_metrics_flat("NAAC")
        self.assertGreater(len(naac_flat), 15)

    def test_semantic_evidence_mapping(self):
        test_text = "Board of Studies BoS curriculum revision with AI, machine learning and cyber security elective courses mapped with Program Outcomes PO and Bloom Taxonomy."
        matches = self.ev_engine.map_evidence_to_metrics(test_text, framework="NAAC", top_k=3)
        self.assertTrue(len(matches) > 0)
        # Check that top match relates to C1 / 1.1.1 or 1.1.2 or 1.2.1
        self.assertIn("1.", matches[0]["metric_id"])

    def test_quality_and_missing_evidence_detection(self):
        sample_ev = self.evidence_list[0]
        quality = self.ev_engine.evaluate_evidence_quality(sample_ev)
        self.assertGreaterEqual(quality["quality_score"], 80)
        
        gaps = self.ev_engine.detect_missing_evidence(self.evidence_list, framework="NAAC")
        self.assertIsInstance(gaps, list)

    def test_scoring_engine_naac_and_nba(self):
        # NAAC Evaluation
        naac_eval = self.scoring_engine.evaluate_framework(self.evidence_list, framework="NAAC")
        self.assertIn("outcome", naac_eval)
        self.assertGreaterEqual(naac_eval["outcome"]["cgpa"], 3.0)
        self.assertIn(naac_eval["outcome"]["grade"], ["A++", "A+", "A"])

        # NBA Evaluation
        nba_eval = self.scoring_engine.evaluate_framework(self.evidence_list, framework="NBA")
        self.assertIn("outcome", nba_eval)
        self.assertGreaterEqual(nba_eval["outcome"]["total_points"], 650)

    def test_gap_matrix_prioritization(self):
        gaps = self.ev_engine.detect_missing_evidence(self.evidence_list, framework="NAAC")
        matrix_res = self.gap_engine.build_prioritized_matrix(gaps)
        self.assertIn("all_gaps_ranked", matrix_res)
        self.assertIn("quadrants", matrix_res)

    def test_task_manager(self):
        initial_count = len(self.task_mgr.get_all_tasks())
        new_task = self.task_mgr.add_task(
            title="Test Task Title",
            metric_id="1.1.1",
            criterion_id="C1",
            owner="Test Owner",
            priority="High"
        )
        self.assertEqual(len(self.task_mgr.get_all_tasks()), initial_count + 1)
        
        updated = self.task_mgr.update_task_status(new_task["id"], "Resolved", "Completed in unit test.")
        self.assertTrue(updated)

    def test_narrative_generation(self):
        metrics = get_all_metrics_flat("NAAC")
        sample_m = metrics[0]
        matched = [ev for ev in self.evidence_list if sample_m["id"] in ev.get("applicable_criteria", [])]
        narrative = self.narrative_gen.generate_metric_narrative(sample_m, matched, framework="NAAC")
        self.assertIn("Executive Summary", narrative["markdown_content"])
        self.assertGreater(narrative["word_count"], 100)

    def test_audit_verifier(self):
        sample_ev = dict(self.evidence_list[0])
        log = self.audit_verifier.record_verification(
            evidence=sample_ev,
            reviewer_name="Dr. Test Reviewer",
            reviewer_role="Senior Auditor",
            action="VERIFIED_APPROVED",
            audit_notes="Unit test approval note."
        )
        self.assertEqual(log["action"], "VERIFIED_APPROVED")
        self.assertEqual(sample_ev["status"], "Verified")

    def test_pdf_export(self):
        naac_eval = self.scoring_engine.evaluate_framework(self.evidence_list, framework="NAAC")
        gaps = self.ev_engine.detect_missing_evidence(self.evidence_list, framework="NAAC")
        matrix_res = self.gap_engine.build_prioritized_matrix(gaps)
        tasks = self.task_mgr.get_all_tasks()
        audit_trail = self.audit_verifier.get_audit_trail()

        pdf_bytes = generate_accreditation_dossier_pdf(naac_eval, matrix_res, tasks, audit_trail)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
