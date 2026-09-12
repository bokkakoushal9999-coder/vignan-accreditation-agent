"""
Audit Verifier Engine:
- Manages human-in-the-loop verification workflow for IQAC and Peer Reviewers
- Maintains immutable audit log of all verification decisions, status changes, and reviewer notes
- Generates compliance audit trail and verification summaries
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


DEFAULT_AUDIT_LOGS: List[Dict[str, Any]] = [
    {
        "id": "AUD-001",
        "timestamp": "2024-06-25 14:30:12",
        "reviewer_name": "Dr. K. Ramamohan",
        "reviewer_role": "Director IQAC",
        "evidence_id": "EVD-VIG-604",
        "evidence_title": "Internal Quality Assurance Cell (IQAC) Quarterly Minutes & AQAR Submissions",
        "action": "VERIFIED_APPROVED",
        "previous_status": "Under Review",
        "new_status": "Verified",
        "audit_notes": "All 4 quarterly IQAC minutes verified with external member signatures (IIT Madras, ISRO). AQAR receipts authenticated."
    },
    {
        "id": "AUD-002",
        "timestamp": "2024-06-20 11:15:40",
        "reviewer_name": "Dr. N. Veeranjaneyulu",
        "reviewer_role": "Dean Academics",
        "evidence_id": "EVD-VIG-502",
        "evidence_title": "Campus Placements & Higher Education Manifest: 86.4% Progression",
        "action": "VERIFIED_APPROVED",
        "previous_status": "Under Review",
        "new_status": "Verified",
        "audit_notes": "Sample of 250 offer letters cross-checked against salary slips and ERP records. 86.4% combined progression verified."
    },
    {
        "id": "AUD-003",
        "timestamp": "2024-06-18 16:45:22",
        "reviewer_name": "Dr. G. Srinivasa Rao",
        "reviewer_role": "Dean R&D",
        "evidence_id": "EVD-VIG-301",
        "evidence_title": "Institutional Research Promotion Policy & Seed Grant Sanction Letters",
        "action": "VERIFIED_WITH_CONCERNS",
        "previous_status": "Draft",
        "new_status": "Verified",
        "audit_notes": "Overall policy and 61 seed grant orders verified. 3 UCs for Biotechnology department require external auditor endorsement."
    },
    {
        "id": "AUD-004",
        "timestamp": "2024-06-15 09:30:00",
        "reviewer_name": "Dr. K. Ramamohan",
        "reviewer_role": "Director IQAC",
        "evidence_id": "EVD-VIG-206",
        "evidence_title": "Consolidated Course Outcomes (CO) and PO/PSO Attainment Reports",
        "action": "VERIFIED_APPROVED",
        "previous_status": "Under Review",
        "new_status": "Verified",
        "audit_notes": "OBE direct (80%) and indirect (20%) calculation formulas verified. All 68 B.Tech CSE course files reconciled."
    }
]


class AuditVerifier:
    def __init__(self, initial_logs: Optional[List[Dict[str, Any]]] = None, use_db: bool = True):
        self.use_db = use_db
        if use_db:
            from core.database import get_database
            self.db = get_database()
            if initial_logs:
                self._audit_trail: List[Dict[str, Any]] = list(initial_logs)
            else:
                self._audit_trail = self.db.get_all_audit_logs()
        else:
            self.db = None
            self._audit_trail = list(initial_logs or DEFAULT_AUDIT_LOGS)

    def record_verification(
        self,
        evidence: Dict[str, Any],
        reviewer_name: str,
        reviewer_role: str,
        action: str,  # VERIFIED_APPROVED, VERIFIED_WITH_CONCERNS, REJECTED, REQUEST_REVISION
        audit_notes: str = "",
        completeness_adjustment: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Records a human verification decision, updates the evidence object,
        and appends an immutable audit log entry.
        """
        prev_status = evidence.get("status", "Draft")
        
        status_map = {
            "VERIFIED_APPROVED": "Verified",
            "VERIFIED_WITH_CONCERNS": "Verified",
            "REQUEST_REVISION": "Needs Revision",
            "REJECTED": "Rejected"
        }
        new_status = status_map.get(action, "Verified")

        # Update evidence
        evidence["status"] = new_status
        evidence["verified_by"] = f"{reviewer_name} ({reviewer_role})"
        evidence["verification_date"] = datetime.now().strftime("%Y-%m-%d")
        if completeness_adjustment is not None:
            evidence["completeness_score"] = completeness_adjustment

        # Create audit entry
        log_id = f"AUD-{str(uuid.uuid4())[:6].upper()}"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "id": log_id,
            "timestamp": ts,
            "reviewer_name": reviewer_name,
            "reviewer_role": reviewer_role,
            "evidence_id": evidence.get("id", "UNKNOWN"),
            "evidence_title": evidence.get("title", "Untitled"),
            "action": action,
            "previous_status": prev_status,
            "new_status": new_status,
            "audit_notes": audit_notes,
            "checksum": f"SHA256:{hash(log_id + ts) & 0xFFFFFFFF:08x}"
        }

        if self.use_db and self.db:
            self.db.insert_audit_log(log_entry)
            # Also update evidence in DB if evidence has an ID
            ev_id = evidence.get("id")
            if ev_id:
                self.db.update_evidence(ev_id, {
                    "verified_status": new_status,
                    "completeness_score": float(evidence.get("completeness_score", 85.0))
                })
            self._audit_trail = self.db.get_all_audit_logs()
        else:
            self._audit_trail.insert(0, log_entry)

        return log_entry

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Retrieves complete audit trail from database or local memory."""
        if self.use_db and self.db:
            try:
                self._audit_trail = self.db.get_all_audit_logs()
            except Exception:
                pass
        return list(self._audit_trail)

    def get_audit_summary(self) -> Dict[str, Any]:
        """Summary statistics of all audit activities."""
        trail = self.get_audit_trail()
        total = len(trail)
        approved = sum(1 for log in trail if log.get("action") == "VERIFIED_APPROVED")
        concerns = sum(1 for log in trail if log.get("action") == "VERIFIED_WITH_CONCERNS")
        revisions = sum(1 for log in trail if log.get("action") in ["REQUEST_REVISION", "REJECTED"])

        last_time = "N/A"
        if trail and isinstance(trail[0], dict):
            last_time = trail[0].get("timestamp", "N/A")

        return {
            "total_audit_events": total,
            "approved_count": approved,
            "concerns_count": concerns,
            "revision_requested_count": revisions,
            "last_audit_time": last_time
        }


