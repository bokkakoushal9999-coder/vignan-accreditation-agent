"""
End-to-end integration and TaskManager SQLite persistence verification test.
"""
import urllib.request
import json
from core.database import get_database
from core.task_manager import TaskManager
from core.audit_verifier import AuditVerifier


import pytest


def test_streamlit_and_backend_endpoints():
    """
    Always-on end-to-end system verification:
    Validates live server if running on 8000/8501, or falls back to full in-process TestClient
    and Streamlit application module validation to guarantee 100% test execution with zero skips.
    """
    backend_tested = False
    streamlit_tested = False

    # 1. Attempt live HTTP probes
    try:
        resp_api = urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=1)
        if resp_api.getcode() == 200:
            data = json.loads(resp_api.read().decode())
            assert data.get("status") in ["online", "healthy"]
            assert data.get("total_evidence_records") >= 45
            backend_tested = True
    except Exception:
        pass

    try:
        resp_st = urllib.request.urlopen("http://127.0.0.1:8501/_stcore/health", timeout=1)
        if resp_st.getcode() == 200:
            streamlit_tested = True
    except Exception:
        pass

    # 2. Always-on In-Process Full Backend Test via TestClient
    if not backend_tested:
        from fastapi.testclient import TestClient
        from backend.api import app
        client = TestClient(app)

        # Test Root Landing Route
        root_resp = client.get("/")
        assert root_resp.status_code == 200
        root_data = root_resp.json()
        assert root_data["status"] == "online"
        assert "NAAC" in str(root_data["frameworks_supported"])
        assert "NBA" in str(root_data["frameworks_supported"])
        assert "NIRF" in str(root_data["frameworks_supported"])

        # Test Health Endpoint
        health_resp = client.get("/api/health")
        assert health_resp.status_code == 200
        health_data = health_resp.json()
        assert health_data["status"] == "online"
        assert health_data["total_evidence_records"] >= 45

        # Test Multi-Framework Criteria Endpoints
        naac_resp = client.get("/api/criteria?framework=NAAC")
        assert naac_resp.status_code == 200
        assert naac_resp.json()["total_criteria_count"] >= 7

        nirf_resp = client.get("/api/criteria?framework=NIRF")
        assert nirf_resp.status_code == 200
        assert nirf_resp.json()["total_criteria_count"] >= 5

        backend_tested = True

    # 3. Always-on Streamlit Frontend Validation
    if not streamlit_tested:
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file("../app.py", default_timeout=25)
        at.run()
        assert not at.exception
        streamlit_tested = True

    assert backend_tested is True
    assert streamlit_tested is True



def test_task_manager_sqlite_lifecycle():
    # 1. Initialize TaskManager with use_db=True
    tm1 = TaskManager(use_db=True)
    initial_tasks = tm1.get_all_tasks()
    assert len(initial_tasks) > 0

    # 2. Create a new task
    new_task = tm1.add_task(
        title="Test E2E Persistence Task",
        metric_id="1.1.1",
        criterion_id="C1",
        owner="Dr. K. Ramamohan (Director IQAC)",
        priority="Critical",
        action_plan="Verify end-to-end task persistence in data/accreditation.db"
    )
    task_id = new_task["id"]
    assert task_id.startswith("TSK-VIG-")

    # 3. Simulate page refresh / new session: Instantiate fresh TaskManager
    tm2 = TaskManager(use_db=True)
    all_tasks_fresh = tm2.get_all_tasks()
    matching = [t for t in all_tasks_fresh if t["id"] == task_id]
    assert len(matching) == 1
    assert matching[0]["title"] == "Test E2E Persistence Task"
    assert matching[0]["status"].upper() in ["OPEN", "IN PROGRESS", "IN REVIEW", "RESOLVED"]

    # 4. Update task status in SQLite
    update_res = tm2.update_task_status(task_id, "In Progress", "Work has begun by IQAC team.")
    assert update_res is True

    # 5. Verify update across another new instance
    tm3 = TaskManager(use_db=True)
    updated_t = next(t for t in tm3.get_all_tasks() if t["id"] == task_id)
    assert updated_t["status"].upper() in ["IN PROGRESS", "IN_PROGRESS"]

    # 6. Mark resolved
    tm3.update_task_status(task_id, "Resolved", "Completed all verification criteria.")
    tm4 = TaskManager(use_db=True)
    final_t = next(t for t in tm4.get_all_tasks() if t["id"] == task_id)
    assert final_t["status"].upper() == "RESOLVED"


def test_task_statistics_calculation():
    tm = TaskManager(use_db=True)
    stats = tm.get_task_statistics()
    assert stats["total_tasks"] > 0
    assert "resolution_rate_pct" in stats
    assert 0.0 <= stats["resolution_rate_pct"] <= 100.0


def test_audit_verifier_sqlite_integration():
    av1 = AuditVerifier(use_db=True)
    sample_evidence = {
        "id": "EVD-VIG-101",
        "title": "B.Tech Curriculum Structure & BOS Approved Syllabi",
        "status": "Under Review"
    }
    log_entry = av1.record_verification(
        evidence=sample_evidence,
        reviewer_name="Dr. K. Ramamohan",
        reviewer_role="Director IQAC",
        action="VERIFIED_APPROVED",
        audit_notes="Verified against regulatory AICTE guidelines."
    )
    assert "checksum" in log_entry
    assert log_entry["checksum"].startswith("SHA256:")

    av2 = AuditVerifier(use_db=True)
    trail = av2.get_audit_trail()
    assert any(entry.get("reviewer_name") == "Dr. K. Ramamohan" for entry in trail)


def test_evidence_content_summary_robustness():
    from core.database import normalize_evidence_dict
    
    # 1. Evidence with content_summary
    e1 = normalize_evidence_dict({"id": "EVD-1", "title": "Test 1", "content_summary": "Explicit summary"})
    assert e1["content_summary"] == "Explicit summary"
    assert e1["summary"] == "Explicit summary"

    # 2. Old evidence with only 'summary'
    e2 = normalize_evidence_dict({"id": "EVD-2", "title": "Test 2", "summary": "Old summary field"})
    assert e2["content_summary"] == "Old summary field"
    assert e2["summary"] == "Old summary field"

    # 3. Old evidence with only 'description'
    e3 = normalize_evidence_dict({"id": "EVD-3", "title": "Test 3", "description": "Database description"})
    assert e3["content_summary"] == "Database description"

    # 4. Evidence with only raw_text
    e4 = normalize_evidence_dict({"id": "EVD-4", "title": "Test 4", "raw_text": "Sample raw text of evidence."})
    assert "Sample raw text" in e4["content_summary"]

    # 5. Empty record
    e5 = normalize_evidence_dict({})
    assert "content_summary" in e5
    assert len(e5["content_summary"]) > 0
    assert e5["id"] == "EVD-UNKNOWN"

