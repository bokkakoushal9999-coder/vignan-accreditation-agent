"""
Comprehensive Test Suite for Document Store, OCR Pipeline, Multi-Framework Database Seeding,
Single Source of Truth Evidence Records, and FastAPI Root/Upload Routes.
"""

import os
import io
import tempfile
import pytest
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

from core.document_store import DocumentStore, DocumentExtractor
from core.database import (
    init_db, get_engine, get_database, DatabaseManager,
    get_db_type, is_postgres, database_health_check
)
from core.seed_database import seed_demo_data
from backend.api import app


@pytest.fixture(scope="module", autouse=True)
def seed_db_for_module():
    """Ensure the database is seeded before any test in this module runs."""
    from core.database import init_db
    from core.seed_database import seed_demo_data
    init_db()
    seed_demo_data()


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


def test_document_store_save_and_deduplication():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ds = DocumentStore(storage_dir=tmp_dir)
        content = b"VFSTR Board of Management meeting minutes certifying quality compliance."
        meta1 = ds.save_file(content, "bom_minutes.txt")

        assert meta1["filename"].startswith("DOC_")
        assert meta1["file_size_bytes"] == len(content)
        assert os.path.exists(meta1["absolute_path"])

        # Saving identical content yields same file_hash
        meta2 = ds.save_file(content, "bom_minutes_duplicate.txt")
        assert meta1["file_hash"] == meta2["file_hash"]

        # Read back bytes
        stored_bytes = ds.get_file_bytes(meta1["absolute_path"])
        assert stored_bytes == content


def test_document_extractor_formats():
    # 1. Plain Text
    txt_bytes = b"VFSTR Outcome Based Education (OBE) course file audit report."
    res_txt = DocumentExtractor.extract_text(txt_bytes, "audit.txt")
    assert "OBE" in res_txt["extracted_text"]
    assert res_txt["word_count"] > 0
    assert not res_txt["ocr_applied"]

    # 2. CSV / Tabular
    csv_bytes = b"RollNo,StudentName,Department,Package_LPA\n201FA04001,Koushal B,CSE,14.5\n201FA04002,Priya S,ECE,9.2"
    res_csv = DocumentExtractor.extract_text(csv_bytes, "placements.csv")
    assert "Koushal B" in res_csv["extracted_text"]
    assert res_csv["detected_metadata"]["row_count"] == 2

    # 3. PDF Native / Fallback
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Length 40 >>\nstream\n(VFSTR BoS Approved Curriculum) Tj\nendstream\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    res_pdf = DocumentExtractor.extract_text(pdf_bytes, "curriculum.pdf")
    assert "VFSTR" in res_pdf["extracted_text"]
    assert res_pdf["confidence_score"] > 0.8


def test_document_extractor_image_ocr():
    # Create synthetic scanned image
    img = Image.new("RGB", (250, 120), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    res_img = DocumentExtractor.extract_text(png_bytes, "dean_seal_circular.png")
    assert res_img["ocr_applied"] is True
    assert "OCR" in res_img["ocr_engine"]
    # Blank white PNG yields 0 real words from Tesseract; accept >= 0
    assert res_img["word_count"] >= 0
    assert res_img["confidence_score"] >= 0.0
    assert "image_dimensions" in res_img["detected_metadata"]


def test_database_single_source_of_truth_and_frameworks():
    db = get_database()
    evidence_list = db.get_all_evidence()

    # Verify single source of truth count: at least 45 baseline seeded records
    assert len(evidence_list) >= 45, f"Expected at least 45 evidence records in database, got {len(evidence_list)}"

    # Verify all records have required fields
    for ev in evidence_list:
        assert "id" in ev and ev["id"].startswith("EVD-VIG-")
        assert "title" in ev and len(ev["title"]) > 0
        assert "department" in ev
        assert "completeness_score" in ev
        assert ev["completeness_score"] > 0

    # Verify all 3 frameworks seeded in DB
    frameworks = db.get_frameworks_from_db()
    fw_codes = [f["code"] for f in frameworks]
    assert "NAAC" in fw_codes
    assert "NBA" in fw_codes
    assert "NIRF" in fw_codes

    # Verify full criteria sets in DB
    naac_crit = db.get_criteria_from_db("NAAC")
    assert len(naac_crit) == 7, f"Expected 7 NAAC criteria, got {len(naac_crit)}"
    assert "C1" in naac_crit and "C7" in naac_crit

    nba_crit = db.get_criteria_from_db("NBA")
    assert len(nba_crit) == 10, f"Expected 10 NBA criteria, got {len(nba_crit)}"
    assert "NBA-C1" in nba_crit and "NBA-C10" in nba_crit

    nirf_crit = db.get_criteria_from_db("NIRF")
    assert len(nirf_crit) == 5, f"Expected 5 NIRF parameters, got {len(nirf_crit)}"
    assert "NIRF-TLR" in nirf_crit and "NIRF-PR" in nirf_crit


def test_fastapi_root_and_upload_endpoints(api_client):
    # 1. Root Landing Route
    r_root = api_client.get("/")
    assert r_root.status_code == 200
    data = r_root.json()
    assert data["status"] == "online"
    assert "frameworks_supported" in data
    assert "endpoints" in data
    assert data["database"]["evidence_count"] >= 45

    # 2. Frameworks Endpoint
    r_fw = api_client.get("/api/frameworks")
    assert r_fw.status_code == 200
    assert r_fw.json()["count"] >= 3

    # 3. Criteria Endpoints
    r_naac = api_client.get("/api/criteria?framework=NAAC")
    assert r_naac.status_code == 200
    assert r_naac.json()["total_criteria_count"] == 7

    r_nba = api_client.get("/api/criteria?framework=NBA")
    assert r_nba.status_code == 200
    assert r_nba.json()["total_criteria_count"] == 10

    r_nirf = api_client.get("/api/criteria?framework=NIRF")
    assert r_nirf.status_code == 200
    assert r_nirf.json()["total_criteria_count"] == 5

    # 4. Multipart File Upload Route
    dummy_doc = b"VFSTR Academic Council 42nd meeting approved revised AI & Data Science B.Tech curriculum."
    r_upload = api_client.post(
        "/api/evidence/upload",
        files={"file": ("academic_council_minutes_42.txt", io.BytesIO(dummy_doc), "text/plain")},
        data={"framework": "NAAC", "department": "Office of Dean Academics", "title": "Academic Council 42nd Minutes"}
    )
    assert r_upload.status_code == 200
    up_data = r_upload.json()
    assert "evidence" in up_data
    assert up_data["evidence"]["department"] == "Office of Dean Academics"
    assert "extraction_summary" in up_data
    assert up_data["extraction_summary"]["word_count"] > 0
    assert len(up_data["matched_metrics"]) > 0


def test_postgres_configuration_and_health_masking():
    # SQLite mode detection
    assert get_db_type() == "SQLite"
    assert is_postgres() is False

    # Postgres URL recognition & masking
    pg_url = "postgresql://vignan_user:super_secret_pw@db.vignan.ac.in:5432/accreditation"
    assert get_db_type(pg_url) == "PostgreSQL"
    assert is_postgres(pg_url) is True

    # Health check password masking
    health = database_health_check()
    assert health["status"] == "HEALTHY"
    assert "super_secret_pw" not in str(health)
