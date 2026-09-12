"""
Unit & Integration Tests for SubmissionPackageBuilder, MockVisitSimulatorEngine, and FastAPI REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api import app
from core.submission_builder import SubmissionPackageBuilder
from core.mock_visit_engine import MockVisitSimulatorEngine
from core.vignan_demo_data import get_demo_evidence_list


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def evidence_data():
    return get_demo_evidence_list()


@pytest.fixture
def builder():
    return SubmissionPackageBuilder(active_academic_year="2023-24")


@pytest.fixture
def mock_visit():
    return MockVisitSimulatorEngine()


def test_submission_builder_numbered_annexures(builder, evidence_data):
    """Verifies that the package builder assigns valid Annexure serial codes and SHA-256 hashes."""
    package = builder.assemble_submission_package(
        framework="NAAC",
        evidence_list=evidence_data,
        institution_name="VFSTR"
    )
    assert package["total_annexures"] == len(evidence_data)
    assert package["annexures"][0]["annexure_code"] == "Annexure-A001"
    assert "SHA256:" in package["annexures"][0]["verification_hash"]
    assert "Annexure Code" in package["evidence_index_csv"]
    assert len(package["criterion_cross_ref"]) > 0


def test_submission_builder_gatekeeper(builder, evidence_data):
    """Verifies pre-submission gatekeeper checks on tasks and unverified evidence."""
    # Test with unverified items
    unverified_ev = [{"id": "EVD-001", "title": "Draft Policy", "status": "Under Review", "raw_text": "sample policy content here for verification"}]
    validation = builder.validate_pre_submission_readiness(
        framework="NAAC",
        evidence_list=unverified_ev,
        tasks_list=[{"id": "TASK-1", "priority": "CRITICAL", "status": "Pending", "title": "Fix syllabus"}]
    )
    assert validation["is_cleared"] is False
    assert validation["gatekeeper_status"] == "BLOCKED"
    assert validation["total_blocking_issues"] >= 2


def test_mock_visit_engine_retrieval(mock_visit):
    """Verifies question bank filtering and data integrity."""
    categories = mock_visit.get_all_categories()
    assert len(categories) >= 8
    
    curriculum_qs = mock_visit.get_questions(category="Curriculum Design & CBCS")
    assert len(curriculum_qs) >= 1
    assert "linked_evidence" in curriculum_qs[0]
    assert "follow_up_traps" in curriculum_qs[0]


def test_mock_visit_engine_defense_evaluation(mock_visit):
    """Verifies faculty mock defense evaluation scoring and feedback."""
    eval_res = mock_visit.evaluate_defense_readiness(
        question_id="MV-001",
        faculty_notes="We revised 28.4% of syllabus under R22 regulation incorporating multi-disciplinary minors and student internship credits.",
        attached_evidence_ids=["EVD-VIG-101", "EVD-VIG-102"]
    )
    assert eval_res["success"] is True
    assert eval_res["composite_score"] > 60.0
    assert eval_res["rating"] in ["EXCELLENT_DEFENSE", "SATISFACTORY_DEFENSE"]
    assert len(eval_res["matched_evidence"]) >= 1


# --- API Endpoint Integration Tests ---

def test_api_scanner_endpoint(client):
    """Tests GET /api/scanner/run."""
    response = client.get("/api/scanner/run?framework=NAAC")
    assert response.status_code == 200
    data = response.json()
    assert data["framework"] == "NAAC"
    assert "cgpa_forecast" in data
    assert "criteria_breakdown" in data


def test_api_validation_report_endpoint(client):
    """Tests GET /api/validation/report."""
    response = client.get("/api/validation/report")
    assert response.status_code == 200
    data = response.json()
    assert "total_evaluated" in data
    assert "compliance_rate_pct" in data


def test_api_mock_visit_endpoints(client):
    """Tests GET /api/mock-visit/questions and POST /api/mock-visit/evaluate."""
    # GET questions
    get_resp = client.get("/api/mock-visit/questions")
    assert get_resp.status_code == 200
    q_data = get_resp.json()
    assert q_data["total_returned"] >= 5

    # POST evaluate
    eval_payload = {
        "question_id": "MV-004",
        "faculty_notes": "We received INR 18.42 Crores in research grants from DST-SERB and published 1,840 Scopus papers.",
        "attached_evidence_ids": ["EVD-VIG-301", "EVD-VIG-302"]
    }
    post_resp = client.post("/api/mock-visit/evaluate", json=eval_payload)
    assert post_resp.status_code == 200
    eval_data = post_resp.json()
    assert eval_data["success"] is True
    assert "composite_score" in eval_data


def test_api_submission_endpoints(client):
    """Tests GET /api/submission/validate and POST /api/submission/build."""
    val_resp = client.get("/api/submission/validate?framework=NAAC")
    assert val_resp.status_code == 200
    assert "gatekeeper_status" in val_resp.json()

    build_payload = {
        "framework": "NAAC",
        "institution_name": "VFSTR (Deemed to be University)",
        "accredited_unit": "Self-Study Report Cycle 2"
    }
    build_resp = client.post("/api/submission/build", json=build_payload)
    assert build_resp.status_code == 200
    build_data = build_resp.json()
    assert build_data["total_annexures"] > 0
    assert "evidence_index_csv" in build_data
