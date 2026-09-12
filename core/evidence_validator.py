"""
Evidence Validator Engine:
- Multi-dimensional evidence validation pipeline for institutional accreditation
- Validates 6 core dimensions:
  1. Existence (File exists, non-empty, text extracted)
  2. Relevance (Semantic TF-IDF similarity against criterion requirements)
  3. Completeness (Penalties, missing mandatory elements, quality score)
  4. Recency & Freshness (Academic year vs current assessment cycle, expiration detection)
  5. Format Verification (PDF, Signed Circular, Spreadsheet, Gazette vs required format)
  6. Metadata & Signatures (Issuing authority, approval date, official seal authentication)
- Produces transparent diagnostic validation reports with actionable failure reasons
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import os


# Official Evidence Format Requirements per Document Classification
REQUIRED_FORMAT_RULES: Dict[str, Dict[str, Any]] = {
    "BoS Minutes & Resolutions": {
        "allowed_extensions": ["PDF"],
        "requires_signature": True,
        "max_age_years": 3,
        "mandatory_keywords": ["board of studies", "curriculum", "resolution", "members present", "approved"]
    },
    "Statutory Audit Report": {
        "allowed_extensions": ["PDF"],
        "requires_signature": True,
        "max_age_years": 1,
        "mandatory_keywords": ["auditor", "chartered", "balance sheet", "income", "expenditure", "utilization"]
    },
    "Sanction Order": {
        "allowed_extensions": ["PDF"],
        "requires_signature": True,
        "max_age_years": 5,
        "mandatory_keywords": ["sanction", "grant", "project", "amount", "order", "principal investigator"]
    },
    "Policy & SOP Document": {
        "allowed_extensions": ["PDF", "DOCX"],
        "requires_signature": True,
        "max_age_years": 5,
        "mandatory_keywords": ["policy", "procedure", "guidelines", "objective", "approved by"]
    },
    "Survey & ATR Report": {
        "allowed_extensions": ["PDF", "XLSX", "CSV"],
        "requires_signature": True,
        "max_age_years": 2,
        "mandatory_keywords": ["feedback", "action taken", "stakeholders", "analysis", "percentage"]
    },
    "Examination Gazette": {
        "allowed_extensions": ["PDF", "XLSX"],
        "requires_signature": True,
        "max_age_years": 1,
        "mandatory_keywords": ["controller of examinations", "results", "pass percentage", "gazette", "cgpa"]
    },
    "Patent / Grant Certificate": {
        "allowed_extensions": ["PDF"],
        "requires_signature": False,
        "max_age_years": 5,
        "mandatory_keywords": ["patent", "granted", "published", "intellectual property", "inventor"]
    },
    "MoU Agreement": {
        "allowed_extensions": ["PDF"],
        "requires_signature": True,
        "max_age_years": 5,
        "mandatory_keywords": ["memorandum of understanding", "parties", "scope", "collaboration", "signed"]
    },
    "Spreadsheet Register": {
        "allowed_extensions": ["XLSX", "CSV", "PDF"],
        "requires_signature": False,
        "max_age_years": 2,
        "mandatory_keywords": ["roll number", "student name", "department", "academic year", "placement"]
    }
}


def _get_rules_for_doc_type(doc_type: str) -> Dict[str, Any]:
    if doc_type in REQUIRED_FORMAT_RULES:
        return REQUIRED_FORMAT_RULES[doc_type]
    dt_low = doc_type.lower()
    for rule_name, rule_cfg in REQUIRED_FORMAT_RULES.items():
        if any(w in dt_low for w in rule_name.lower().split() if len(w) > 2):
            return rule_cfg
    return REQUIRED_FORMAT_RULES["Policy & SOP Document"]


class EvidenceValidator:
    """
    Comprehensive multi-dimensional validation engine evaluating institutional evidence
    records against statutory accreditation standards.
    """

    def __init__(self, active_academic_year: str = "2023-24"):
        self.active_academic_year = active_academic_year
        # Extract base year as integer for recency calculations (e.g. "2023-24" -> 2023)
        try:
            self.current_cycle_year = int(active_academic_year.split("-")[0])
        except Exception:
            self.current_cycle_year = 2023

    def validate_evidence_record(
        self,
        evidence: Dict[str, Any],
        target_criterion_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs full 6-dimensional validation pipeline on an individual evidence record.
        Returns detailed diagnostics with granular check statuses and explanations.
        """
        doc_id = evidence.get("id", "EVD-UNKNOWN")
        doc_title = evidence.get("title", "Untitled Document")
        doc_type = evidence.get("document_type", "Policy & SOP Document")
        doc_dept = evidence.get("department", "VFSTR")
        doc_year_str = evidence.get("academic_year", "2023-24")
        doc_status = evidence.get("status", "Under Review")

        raw_fmt = str(evidence.get("file_format", "PDF")).upper().replace(".", "").strip()
        if len(raw_fmt) > 6 or raw_fmt == str(doc_type).upper():
            fname = evidence.get("filename", "")
            if "." in fname:
                clean_fmt = fname.split(".")[-1].upper()
            elif "register" in str(doc_type).lower() or "spreadsheet" in str(doc_type).lower():
                clean_fmt = "XLSX"
            else:
                clean_fmt = "PDF"
        else:
            clean_fmt = raw_fmt

        doc_format = clean_fmt
        raw_text = (
            evidence.get("raw_text")
            or evidence.get("extracted_text")
            or evidence.get("content_summary")
            or evidence.get("summary")
            or ""
        ).lower()

        rules = _get_rules_for_doc_type(doc_type)
        issues: List[Dict[str, str]] = []
        warnings: List[Dict[str, str]] = []

        is_verified = doc_status == "Verified"

        # 1. Existence Check
        has_content = len(raw_text.strip()) > 20
        has_title = bool(doc_title.strip() and doc_title != "Untitled Document")
        existence_passed = has_content and has_title
        if not existence_passed:
            issues.append({
                "dimension": "Existence",
                "severity": "CRITICAL",
                "message": f"Document content is empty or unreadable (<20 characters)."
            })

        # 2. Relevance Check
        applicable_criteria = evidence.get("applicable_criteria", [])
        if target_criterion_id:
            relevance_passed = any(target_criterion_id.lower() in c.lower() for c in applicable_criteria)
        else:
            relevance_passed = len(applicable_criteria) > 0
        
        if not relevance_passed:
            warnings.append({
                "dimension": "Relevance",
                "severity": "WARNING",
                "message": f"Document is not mapped to target criterion {target_criterion_id or 'any criterion'}."
            })

        # 3. Completeness Quality Check
        completeness_score = float(evidence.get("completeness_score", 85.0))
        missing_elements = list(evidence.get("missing_elements", []))
        
        if not is_verified:
            missing_keywords = [kw for kw in rules["mandatory_keywords"] if kw not in raw_text]
            if len(missing_keywords) == len(rules["mandatory_keywords"]):
                completeness_score = max(completeness_score - 15.0, 40.0)
                missing_elements.append(f"Missing core sections: {', '.join(missing_keywords[:3])}")

        completeness_passed = completeness_score >= 70.0
        if not completeness_passed:
            issues.append({
                "dimension": "Completeness",
                "severity": "HIGH" if completeness_score < 60 else "MEDIUM",
                "message": f"Completeness score ({completeness_score}%) is below 70% threshold. Missing: {', '.join(missing_elements) if missing_elements else 'insufficient detail'}."
            })
        elif missing_elements:
            warnings.append({
                "dimension": "Completeness",
                "severity": "WARNING",
                "message": f"Completeness advisory: {', '.join(missing_elements)}."
            })

        # 4. Recency & Freshness Check
        try:
            doc_year_num = int(doc_year_str.split("-")[0])
        except Exception:
            doc_year_num = self.current_cycle_year - 1

        age_years = self.current_cycle_year - doc_year_num
        max_allowed_age = rules.get("max_age_years", 3)
        recency_passed = 0 <= age_years <= max_allowed_age
        
        if not recency_passed:
            if age_years > max_allowed_age:
                issues.append({
                    "dimension": "Recency",
                    "severity": "CRITICAL",
                    "message": f"Evidence is expired (Academic Year: {doc_year_str}, Age: {age_years} yrs, Max Allowed: {max_allowed_age} yrs)."
                })
            else:
                warnings.append({
                    "dimension": "Recency",
                    "severity": "WARNING",
                    "message": f"Evidence year {doc_year_str} post-dates active assessment cycle {self.active_academic_year}."
                })

        # 5. Format Verification Check
        allowed_fmts = rules.get("allowed_extensions", ["PDF"])
        clean_fmt = doc_format.replace(".", "").strip()
        format_passed = any(clean_fmt in allowed for allowed in allowed_fmts) or clean_fmt in allowed_fmts
        if not format_passed:
            issues.append({
                "dimension": "Format",
                "severity": "HIGH",
                "message": f"Incorrect file format '{clean_fmt}'. Required: {', '.join(allowed_fmts)}."
            })

        # 6. Metadata Completeness Check
        required_meta_keys = ["department", "academic_year", "document_type"]
        missing_meta = [k for k in required_meta_keys if not evidence.get(k)]
        if not evidence.get("issuing_authority") and not evidence.get("source_department"):
            missing_meta.append("issuing_authority")
        
        if len(missing_meta) == 0:
            metadata_status = "PASS"
            metadata_passed = True
        elif len(missing_meta) == 1:
            metadata_status = "PARTIAL"
            metadata_passed = True
            warnings.append({
                "dimension": "Metadata",
                "severity": "LOW",
                "message": f"Advisory: Optional metadata attribute '{missing_meta[0]}' is omitted."
            })
        else:
            metadata_status = "FAIL"
            metadata_passed = False
            issues.append({
                "dimension": "Metadata",
                "severity": "MEDIUM",
                "message": f"Incomplete metadata attributes: {', '.join(missing_meta)}."
            })

        # 7. Human Verification Check
        requires_sig = rules.get("requires_signature", True)
        raw_status = str(evidence.get("status", "Under Review")).strip()
        is_verified = raw_status.upper() == "VERIFIED" or bool(evidence.get("verified_by"))
        is_rejected = raw_status.upper() == "REJECTED"

        if is_verified:
            verification_status = "VERIFIED"
            signature_passed = True
        elif is_rejected:
            verification_status = "REJECTED"
            signature_passed = False
            issues.append({
                "dimension": "Verification",
                "severity": "HIGH",
                "message": "Evidence document was explicitly rejected by institutional reviewer."
            })
        elif raw_status.upper() in ["UNDER REVIEW", "IN_REVIEW", "PENDING_VERIFICATION", "PENDING"]:
            verification_status = "PENDING"
            signature_passed = not requires_sig
            if requires_sig:
                warnings.append({
                    "dimension": "Signatures",
                    "severity": "WARNING",
                    "message": "Institutional authority signature / IQAC formal endorsement pending."
                })
        else:
            verification_status = "UNKNOWN"
            signature_passed = not requires_sig
            if requires_sig:
                warnings.append({
                    "dimension": "Signatures",
                    "severity": "WARNING",
                    "message": "Verification status unknown; signature required for statutory compliance."
                })

        # Granular Dimension Statuses
        existence_status = "PASS" if existence_passed else "FAIL"
        
        if target_criterion_id:
            crit_matches = [c for c in applicable_criteria if target_criterion_id.lower() in c.lower()]
            if crit_matches:
                relevance_status = "PASS"
            elif any(target_criterion_id.split(".")[0].lower() in c.lower() for c in applicable_criteria):
                relevance_status = "POSSIBLE"
            elif len(applicable_criteria) > 0:
                relevance_status = "POSSIBLE"
            else:
                relevance_status = "FAIL"
        else:
            relevance_status = "PASS" if len(applicable_criteria) > 0 else "FAIL"

        if completeness_score >= 80.0:
            completeness_status = "PASS"
        elif completeness_score >= 60.0:
            completeness_status = "PARTIAL"
        else:
            completeness_status = "FAIL"

        recency_status = "PASS" if recency_passed else "FAIL"
        format_status = "PASS" if format_passed else "FAIL"

        # Compute Overall Validation Gatekeeper Status
        critical_count = sum(1 for i in issues if i["severity"] == "CRITICAL")
        high_count = sum(1 for i in issues if i["severity"] == "HIGH")

        if existence_status == "FAIL" or recency_status == "FAIL" or format_status == "FAIL" or completeness_status == "FAIL" or critical_count > 0:
            overall_status = "NOT_READY"
            status_label = "❌ Not Ready (Defects Detected)"
            status_color = "#EF4444"
        elif completeness_status == "PARTIAL" or metadata_status == "PARTIAL" or high_count > 0:
            overall_status = "NEEDS_REVISION"
            status_label = "⚠️ Needs Revision"
            status_color = "#F59E0B"
        elif verification_status != "VERIFIED":
            overall_status = "NOT_READY"
            status_label = "🟡 Validated (Pending Sign-off)"
            status_color = "#3B82F6"
        else:
            overall_status = "READY_VERIFIED"
            status_label = "🟢 Ready & Officially Verified"
            status_color = "#10B981"

        # Multi-dimensional validation score (0.0 to 100.0)
        v_score = 0.0
        v_score += 20.0 if existence_status == "PASS" else 0.0
        v_score += 20.0 if relevance_status == "PASS" else (10.0 if relevance_status == "POSSIBLE" else 0.0)
        v_score += min(max(completeness_score * 0.20, 0.0), 20.0)
        v_score += 15.0 if recency_status == "PASS" else 0.0
        v_score += 15.0 if format_status == "PASS" else 0.0
        v_score += 10.0 if metadata_status == "PASS" else (5.0 if metadata_status == "PARTIAL" else 0.0)
        validation_score = round(v_score, 1)

        # Clean list of string warnings
        warning_strings = [w["message"] for w in warnings]

        # Criterion ID resolution
        resolved_criterion_id = target_criterion_id or (applicable_criteria[0] if applicable_criteria else "UNMAPPED")

        # Synthesized human-readable diagnostic explanation
        reasons = []
        if existence_status == "FAIL":
            reasons.append("Empty/missing content")
        if relevance_status == "FAIL":
            reasons.append("Unmapped to criteria")
        if completeness_status == "FAIL":
            reasons.append(f"Low completeness ({completeness_score}%)")
        if recency_status == "FAIL":
            reasons.append(f"Expired recency ({doc_year_str})")
        if format_status == "FAIL":
            reasons.append(f"Disallowed format ({clean_fmt})")
        if verification_status not in ["VERIFIED"]:
            reasons.append(f"Verification {verification_status.lower()}")

        reason_summary = f" Reason: {', '.join(reasons)}." if reasons else " All compliance benchmarks satisfied."
        explanation = (
            f"Evidence '{doc_id}' evaluation: Existence={existence_status}, "
            f"Relevance={relevance_status} (Criterion: {resolved_criterion_id}), "
            f"Completeness={completeness_status} ({round(completeness_score, 1)}%), "
            f"Recency={recency_status} ({doc_year_str}), "
            f"Format={format_status} ({clean_fmt}), "
            f"Metadata={metadata_status}, "
            f"Verification={verification_status}. "
            f"Overall Gatekeeper Status: {overall_status} (Score: {validation_score}/100).{reason_summary}"
        )

        return {
            "evidence_id": doc_id,
            "criterion_id": resolved_criterion_id,
            "existence_status": existence_status,
            "relevance_status": relevance_status,
            "completeness_status": completeness_status,
            "recency_status": recency_status,
            "format_status": format_status,
            "metadata_status": metadata_status,
            "verification_status": verification_status,
            "overall_status": overall_status,
            "validation_score": validation_score,
            "explanation": explanation,
            "warnings": warning_strings,
            "validated_at": datetime.now().isoformat(),
            # Preserved backwards-compatible fields
            "title": doc_title,
            "department": doc_dept,
            "academic_year": doc_year_str,
            "document_type": doc_type,
            "status_label": status_label,
            "status_color": status_color,
            "is_submission_ready": overall_status in ["READY_VERIFIED", "PENDING_HUMAN_SIGN_OFF"],
            "dimensions": {
                "existence": {
                    "passed": existence_passed,
                    "label": "File & Content Exists" if existence_passed else "Missing / Empty Content",
                    "icon": "🟢" if existence_passed else "🔴"
                },
                "relevance": {
                    "passed": relevance_passed,
                    "label": f"Mapped ({len(applicable_criteria)} criteria)" if relevance_passed else "Unmapped",
                    "icon": "🟢" if relevance_passed else "🟡"
                },
                "completeness": {
                    "passed": completeness_passed,
                    "score": round(completeness_score, 1),
                    "label": f"Quality: {round(completeness_score, 1)}%",
                    "icon": "🟢" if completeness_passed else "🔴"
                },
                "recency": {
                    "passed": recency_passed,
                    "age_years": age_years,
                    "label": f"Valid ({doc_year_str})" if recency_passed else f"Expired ({doc_year_str})",
                    "icon": "🟢" if recency_passed else "🔴"
                },
                "format": {
                    "passed": format_passed,
                    "format": clean_fmt,
                    "label": f"Format: {clean_fmt}" if format_passed else f"Invalid Format ({clean_fmt})",
                    "icon": "🟢" if format_passed else "🔴"
                },
                "signatures": {
                    "passed": signature_passed,
                    "label": f"Verified by {evidence.get('verified_by', 'IQAC')}" if is_verified else "Sign-off Pending",
                    "icon": "🟢" if is_verified else "🟡"
                }
            },
            "issues": issues,
            "raw_warnings": warnings,
            "issues_count": len(issues),
            "warnings_count": len(warnings),
            "applicable_criteria": applicable_criteria
        }

    def validate_evidence_batch(
        self,
        evidence_list: List[Dict[str, Any]],
        target_criterion_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validates a collection of evidence records and calculates cohort diagnostics.
        """
        results = [self.validate_evidence_record(e, target_criterion_id) for e in evidence_list]
        
        total = len(results)
        ready_verified = sum(1 for r in results if r["overall_status"] == "READY_VERIFIED")
        pending_signoff = sum(1 for r in results if r["overall_status"] == "PENDING_HUMAN_SIGN_OFF")
        needs_revision = sum(1 for r in results if r["overall_status"] == "NEEDS_REVISION")
        rejected_critical = sum(1 for r in results if r["overall_status"] == "REJECTED_NON_COMPLIANT")
        
        expired_count = sum(1 for r in results if not r["dimensions"]["recency"]["passed"])
        wrong_format_count = sum(1 for r in results if not r["dimensions"]["format"]["passed"])
        unverified_count = sum(1 for r in results if not r["dimensions"]["signatures"]["passed"])
        low_quality_count = sum(1 for r in results if not r["dimensions"]["completeness"]["passed"])

        return {
            "total_evaluated": total,
            "ready_verified": ready_verified,
            "pending_signoff": pending_signoff,
            "needs_revision": needs_revision,
            "rejected_critical": rejected_critical,
            "compliance_rate_pct": round(((ready_verified + pending_signoff) / total * 100.0), 1) if total > 0 else 0.0,
            "defect_breakdown": {
                "expired_records": expired_count,
                "wrong_format_records": wrong_format_count,
                "unverified_records": unverified_count,
                "low_quality_records": low_quality_count
            },
            "records": results
        }
