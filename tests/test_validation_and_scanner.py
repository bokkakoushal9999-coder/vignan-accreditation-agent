"""
Unit & Integration Tests for EvidenceValidator and ContinuousReadinessScanner.
"""

import pytest
from core.evidence_validator import EvidenceValidator
from core.continuous_scanner import ContinuousReadinessScanner
from core.vignan_demo_data import get_demo_evidence_list


@pytest.fixture
def evidence_data():
    return get_demo_evidence_list()


@pytest.fixture
def validator():
    return EvidenceValidator(active_academic_year="2023-24")


@pytest.fixture
def scanner():
    return ContinuousReadinessScanner(active_academic_year="2023-24")


def test_validator_existence_check(validator):
    """Verifies that empty or too-short documents fail the existence dimension."""
    empty_doc = {
        "id": "EVD-TEST-001",
        "title": "Untitled Document",
        "raw_text": "short",
        "document_type": "Policy & SOP Document",
        "academic_year": "2023-24"
    }
    result = validator.validate_evidence_record(empty_doc)
    assert result["dimensions"]["existence"]["passed"] is False
    assert any(i["dimension"] == "Existence" for i in result["issues"])


def test_validator_recency_expiration(validator):
    """Verifies that documents older than allowed threshold fail recency check."""
    expired_doc = {
        "id": "EVD-TEST-002",
        "title": "Old Statutory Audit Report 2018",
        "raw_text": "auditor chartered balance sheet income expenditure utilization complete financial audit",
        "document_type": "Statutory Audit Report",  # max age is 1 year
        "academic_year": "2018-19",
        "file_format": "PDF",
        "status": "Verified"
    }
    result = validator.validate_evidence_record(expired_doc)
    assert result["dimensions"]["recency"]["passed"] is False
    assert result["dimensions"]["recency"]["age_years"] >= 4


def test_validator_format_check(validator):
    """Verifies that documents with disallowed file extensions fail format check."""
    invalid_format_doc = {
        "id": "EVD-TEST-003",
        "title": "BoS Minutes in TXT",
        "raw_text": "board of studies curriculum resolution members present approved",
        "document_type": "BoS Minutes & Resolutions",  # requires PDF
        "academic_year": "2023-24",
        "file_format": "TXT",
        "status": "Verified"
    }
    result = validator.validate_evidence_record(invalid_format_doc)
    assert result["dimensions"]["format"]["passed"] is False


def test_validator_batch_summary(validator, evidence_data):
    """Verifies batch validation across all seeded demo evidence records."""
    batch_res = validator.validate_evidence_batch(evidence_data)
    assert batch_res["total_evaluated"] == len(evidence_data)
    assert batch_res["ready_verified"] > 0
    assert batch_res["compliance_rate_pct"] > 50.0
    assert "defect_breakdown" in batch_res


def test_continuous_scanner_naac(scanner, evidence_data):
    """Verifies continuous scanner across 7 NAAC criteria."""
    scan = scanner.scan_all_criteria(framework="NAAC", evidence_list=evidence_data)
    assert scan["framework"] == "NAAC"
    assert scan["summary_counts"]["total_criteria"] == 7
    assert scan["overall_readiness_pct"] > 70.0
    assert scan["cgpa_forecast"] >= 3.0
    assert len(scan["criteria_breakdown"]) == 7


def test_continuous_scanner_nba(scanner, evidence_data):
    """Verifies continuous scanner across NBA criteria."""
    scan = scanner.scan_all_criteria(framework="NBA", evidence_list=evidence_data)
    assert scan["framework"] == "NBA"
    assert scan["summary_counts"]["total_criteria"] == 10
    assert scan["overall_readiness_pct"] > 70.0
    assert len(scan["criteria_breakdown"]) == 10


def test_evidence_validator_phase2_seven_dimensions(validator):
    """Verifies that all 14 Phase 2 result fields are populated with expected types and values."""
    ev = {
        "id": "EVD-VIG-101",
        "title": "Academic Council Minutes 2023",
        "department": "Dean Academics",
        "academic_year": "2023-24",
        "document_type": "BoS Minutes & Resolutions",
        "file_format": "PDF",
        "status": "Verified",
        "completeness_score": 92.0,
        "applicable_criteria": ["1.1.1", "C1"],
        "raw_text": "board of studies curriculum resolution members present approved outcome based education",
        "issuing_authority": "Registrar, VFSTR"
    }
    res = validator.validate_evidence_record(ev, target_criterion_id="1.1.1")

    # Assert exact Phase 2 fields exist
    expected_fields = [
        "evidence_id", "criterion_id", "existence_status", "relevance_status",
        "completeness_status", "recency_status", "format_status", "metadata_status",
        "verification_status", "overall_status", "validation_score", "explanation",
        "warnings", "validated_at"
    ]
    for field in expected_fields:
        assert field in res, f"Missing required Phase 2 field: {field}"

    assert res["evidence_id"] == "EVD-VIG-101"
    assert res["criterion_id"] == "1.1.1"
    assert res["existence_status"] == "PASS"
    assert res["relevance_status"] == "PASS"
    assert res["completeness_status"] == "PASS"
    assert res["recency_status"] == "PASS"
    assert res["format_status"] == "PASS"
    assert res["metadata_status"] == "PASS"
    assert res["verification_status"] == "VERIFIED"
    assert res["overall_status"] == "READY_VERIFIED"
    assert res["validation_score"] > 80.0
    assert isinstance(res["explanation"], str) and len(res["explanation"]) > 20
    assert isinstance(res["warnings"], list)
    assert isinstance(res["validated_at"], str)


def test_evidence_validator_prompt_example(validator):
    """
    Verifies the exact scenario from problem statement:
    Required: Academic Audit Report 2025-26, PDF, Signed
    Uploaded: Academic_Audit_2023.docx (expired recency, wrong format docx, signature unknown/not verified)
    Expected: existence=PASS, relevance=POSSIBLE, recency=FAIL, format=FAIL, signature=UNKNOWN/PENDING, overall=NOT_READY
    """
    uploaded_doc = {
        "id": "EVD-TEST-SAMPLE",
        "title": "Academic_Audit_2023.docx",
        "filename": "Academic_Audit_2023.docx",
        "document_type": "Statutory Audit Report",  # max age: 1 year, requires PDF, requires signature
        "academic_year": "2020-21",  # Expired relative to 2023-24 cycle
        "file_format": "DOCX",       # Disallowed format (requires PDF)
        "raw_text": "Academic audit report conducted for faculty and department records with full assessment details.",
        "department": "Dean Academics",
        "status": "Draft",           # Signature not verified
        "completeness_score": 75.0,
        "applicable_criteria": ["C6"]
    }
    # Validate against target criterion 1.1.1 (general criteria mapped to C6, so relevance = POSSIBLE)
    res = validator.validate_evidence_record(uploaded_doc, target_criterion_id="1.1.1")

    assert res["existence_status"] == "PASS"
    assert res["relevance_status"] == "POSSIBLE"
    assert res["recency_status"] == "FAIL"
    assert res["format_status"] == "FAIL"
    assert res["verification_status"] in ["UNKNOWN", "PENDING"]
    assert res["overall_status"] == "NOT_READY"
    assert len(res["warnings"]) >= 0
    assert "NOT_READY" in res["explanation"]
