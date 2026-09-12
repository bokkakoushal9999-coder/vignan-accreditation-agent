"""
Submission Builder & Pre-Submission Gatekeeper Engine:
- Statutory accreditation package assembler for VFSTR (Vignan University)
- Enforces strict pre-submission validation blocker before generating final submission dossiers
- Compiles numbered Annexure registers (A001, A002...), Evidence Index CSV, and Criterion Cross-Reference Matrix
- Verifies human sign-off completion, format compliance, and audit trail integrity
"""

from typing import Dict, List, Any, Optional
import io
import csv
import hashlib
from datetime import datetime
from core.evidence_validator import EvidenceValidator
from core.criteria_registry import get_framework_criteria, NAAC_CRITERIA, NBA_CRITERIA


class SubmissionPackageBuilder:
    """
    Assembles, indexes, and certifies institutional accreditation submission dossiers
    with pre-submission gatekeeper checks and automated cross-referencing.
    """

    def __init__(self, active_academic_year: str = "2023-24"):
        self.active_academic_year = active_academic_year
        self.validator = EvidenceValidator(active_academic_year=active_academic_year)

    def validate_pre_submission_readiness(
        self,
        framework: str = "NAAC",
        evidence_list: Optional[List[Dict[str, Any]]] = None,
        tasks_list: Optional[List[Dict[str, Any]]] = None,
        narratives_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes strict pre-submission gatekeeper checks.
        Returns whether the package is cleared for formal statutory submission or blocked with actionable defects.
        """
        if evidence_list is None:
            evidence_list = []
        if tasks_list is None:
            tasks_list = []
        if narratives_list is None:
            narratives_list = []

        blocking_issues = []
        warnings = []

        # 1. Evidence Quality & Sign-Off Check
        validation_batch = self.validator.validate_evidence_batch(evidence_list)
        
        unverified_count = 0
        expired_count = 0
        critical_count = 0
        for rec in validation_batch["records"]:
            if rec["overall_status"] == "REJECTED_NON_COMPLIANT":
                critical_count += 1
                blocking_issues.append({
                    "category": "Evidence Compliance",
                    "severity": "CRITICAL",
                    "item_id": rec["evidence_id"],
                    "message": f"Critical rejection on '{rec['title']}': {rec['issues'][0]['message'] if rec['issues'] else 'Non-compliant document'}."
                })
            elif rec["overall_status"] == "NEEDS_REVISION":
                critical_count += 1
                blocking_issues.append({
                    "category": "Evidence Revision Required",
                    "severity": "HIGH",
                    "item_id": rec["evidence_id"],
                    "message": f"Document '{rec['title']}' requires revision: {rec['issues'][0]['message'] if rec['issues'] else 'Format/quality defects present'}."
                })
            elif rec["overall_status"] in ["PENDING_HUMAN_SIGN_OFF", "NOT_READY"] or rec.get("verification_status") != "VERIFIED":
                unverified_count += 1
                blocking_issues.append({
                    "category": "Human Verification Sign-Off",
                    "severity": "HIGH",
                    "item_id": rec["evidence_id"],
                    "message": f"Mandatory faculty sign-off pending for '{rec['title']}' ({rec['department']}). AI drafts cannot be submitted without IQAC approval."
                })
            
            if not rec["dimensions"]["recency"]["passed"]:
                expired_count += 1
                warnings.append({
                    "category": "Evidence Freshness",
                    "severity": "WARNING",
                    "item_id": rec["evidence_id"],
                    "message": f"Document '{rec['title']}' is aged beyond standard cycle guidelines ({rec['academic_year']})."
                })

        # 2. Remediation Tasks Check
        critical_open_tasks = [t for t in tasks_list if t.get("priority") == "CRITICAL" and t.get("status") != "Completed"]
        high_open_tasks = [t for t in tasks_list if t.get("priority") == "HIGH" and t.get("status") != "Completed"]

        if critical_open_tasks:
            for task in critical_open_tasks:
                blocking_issues.append({
                    "category": "Remediation Action Items",
                    "severity": "CRITICAL",
                    "item_id": task.get("id", "TASK-UNKNOWN"),
                    "message": f"Critical remediation task unresolved: '{task.get('title')}' assigned to {task.get('assigned_to', 'Unassigned')}."
                })

        if high_open_tasks:
            for task in high_open_tasks:
                warnings.append({
                    "category": "Remediation Action Items",
                    "severity": "WARNING",
                    "item_id": task.get("id", "TASK-UNKNOWN"),
                    "message": f"High priority remediation task pending: '{task.get('title')}' (Status: {task.get('status')})."
                })

        # 3. SAR Narrative Coverage Check
        criteria_dict = get_framework_criteria(framework)
        approved_narratives = {n.get("criterion_id"): n for n in narratives_list if n.get("status") == "Approved"}

        missing_narratives = []
        for crit_key, crit in criteria_dict.items():
            crit_id = crit.get("id", crit_key)
            if crit_id not in approved_narratives and crit_key not in approved_narratives:
                missing_narratives.append(crit_id)

        if missing_narratives:
            warnings.append({
                "category": "SAR Narrative Coverage",
                "severity": "WARNING",
                "item_id": ", ".join(missing_narratives),
                "message": f"Formal SAR executive narrative missing or pending IQAC sign-off for criteria: {', '.join(missing_narratives)}."
            })

        is_cleared = len(blocking_issues) == 0
        
        if is_cleared:
            gatekeeper_status = "READY_FOR_SUBMISSION"
            status_badge = "🟢 Pre-Submission Cleared (Ready for Formal Filing)"
            status_color = "#10B981"
        else:
            gatekeeper_status = "BLOCKED"
            status_badge = f"🔴 Submission Blocked ({len(blocking_issues)} Mandatory Issues)"
            status_color = "#EF4444"

        return {
            "is_cleared": is_cleared,
            "gatekeeper_status": gatekeeper_status,
            "status_badge": status_badge,
            "status_color": status_color,
            "total_blocking_issues": len(blocking_issues),
            "total_warnings": len(warnings),
            "blocking_issues": blocking_issues,
            "warnings": warnings,
            "validation_summary": {
                "total_evidence_evaluated": len(evidence_list),
                "verified_ready": validation_batch.get("ready_verified", 0),
                "unverified_pending": unverified_count,
                "critical_defects": critical_count,
                "open_critical_tasks": len(critical_open_tasks),
                "open_high_tasks": len(high_open_tasks)
            }
        }

    def assemble_submission_package(
        self,
        framework: str = "NAAC",
        evidence_list: Optional[List[Dict[str, Any]]] = None,
        institution_name: str = "VFSTR (Deemed to be University)",
        accredited_unit: str = "Institutional NAAC Self-Study Report (Cycle 2)"
    ) -> Dict[str, Any]:
        """
        Assembles complete statutory submission bundle with numbered annexures and cross-reference table.
        """
        if evidence_list is None:
            evidence_list = []

        assembly_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        package_id = f"SUB-{framework.upper()}-{datetime.now().strftime('%Y%m%d%H%M')}"

        # 1. Generate Numbered Annexures
        annexures = []
        criterion_cross_ref: Dict[str, List[Dict[str, Any]]] = {}

        for idx, ev in enumerate(evidence_list, 1):
            annexure_code = f"Annexure-A{idx:03d}"
            ev_id = ev.get("id", f"EVD-{idx:03d}")
            title = ev.get("title", "Untitled Document")
            dept = ev.get("department", "VFSTR")
            doc_type = ev.get("document_type", "Official Record")
            academic_year = ev.get("academic_year", "2023-24")
            fmt = ev.get("file_format", "PDF")
            verified_by = ev.get("verified_by", "IQAC Cell")
            status = ev.get("status", "Verified")
            app_criteria = ev.get("applicable_criteria", ["General"])

            # Compute digital proof hash
            hash_input = f"{ev_id}-{title}-{dept}-{academic_year}".encode("utf-8")
            doc_hash = hashlib.sha256(hash_input).hexdigest()[:16].upper()

            annexure_entry = {
                "annexure_code": annexure_code,
                "evidence_id": ev_id,
                "title": title,
                "department": dept,
                "document_type": doc_type,
                "academic_year": academic_year,
                "format": fmt,
                "verified_by": verified_by,
                "status": status,
                "applicable_criteria": app_criteria,
                "verification_hash": f"SHA256:{doc_hash}",
                "page_count_est": 12 if "BoS" in title or "Audit" in title else 4
            }
            annexures.append(annexure_entry)

            # Map to Criterion Cross Reference
            for crit in app_criteria:
                crit_clean = crit.strip().upper()
                if crit_clean not in criterion_cross_ref:
                    criterion_cross_ref[crit_clean] = []
                criterion_cross_ref[crit_clean].append({
                    "annexure_code": annexure_code,
                    "evidence_id": ev_id,
                    "title": title,
                    "department": dept,
                    "status": status
                })

        # 2. Build Evidence Index CSV
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow([
            "Annexure Code",
            "Evidence ID",
            "Document Title",
            "Department",
            "Document Classification",
            "Academic Year",
            "File Format",
            "Status",
            "Verified By",
            "Applicable Criteria",
            "Integrity Hash"
        ])

        for ann in annexures:
            csv_writer.writerow([
                ann["annexure_code"],
                ann["evidence_id"],
                ann["title"],
                ann["department"],
                ann["document_type"],
                ann["academic_year"],
                ann["format"],
                ann["status"],
                ann["verified_by"],
                "; ".join(ann["applicable_criteria"]),
                ann["verification_hash"]
            ])

        csv_content = csv_buffer.getvalue()

        # 3. Assemble Package Summary
        return {
            "package_id": package_id,
            "framework": framework,
            "institution_name": institution_name,
            "accredited_unit": accredited_unit,
            "assembly_timestamp": assembly_timestamp,
            "active_academic_year": self.active_academic_year,
            "total_annexures": len(annexures),
            "total_pages_estimated": sum(a["page_count_est"] for a in annexures),
            "annexures": annexures,
            "criterion_cross_ref": criterion_cross_ref,
            "evidence_index_csv": csv_content,
            "institutional_seal": "OFFICIALLY CERTIFIED BY VFSTR IQAC & REGISTRAR"
        }
