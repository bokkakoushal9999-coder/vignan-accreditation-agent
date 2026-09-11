"""
Task Manager Engine:
- Manages corrective remediation tasks for identified accreditation gaps
- Supports status transitions (Open -> In Progress -> In Review -> Resolved)
- Assigns institutional owners, deadlines, priority levels, and evidence attachments
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


DEFAULT_VIGNAN_TASKS: List[Dict[str, Any]] = [
    {
        "id": "TSK-VIG-001",
        "title": "Obtain External Auditor Signatures on Biotechnology Seed Grant UCs",
        "metric_id": "3.1.1",
        "criterion_id": "C3",
        "owner": "Dr. G. Srinivasa Rao (Dean R&D)",
        "priority": "High",
        "status": "In Progress",
        "deadline": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
        "estimated_days": 10,
        "action_plan": "Coordinate with statutory auditor to stamp and certify 3 pending utilization certificates for Biotechnology department seed grants (INR 14.5 Lakhs).",
        "attached_evidence_id": "EVD-VIG-301",
        "created_date": "2024-09-01",
        "resolution_notes": "Statutory auditor scheduled audit on 18th Sept. Draft certificates reviewed."
    },
    {
        "id": "TSK-VIG-002",
        "title": "Renew Calibration Certificate for Biotechnology GC-MS Lab Instrument",
        "metric_id": "4.4.1",
        "criterion_id": "C4",
        "owner": "Er. K. Sambasiva Rao (Estate Officer)",
        "priority": "High",
        "status": "In Progress",
        "deadline": (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
        "estimated_days": 5,
        "action_plan": "Expedite NABL-accredited vendor visit for recalibrating the Gas Chromatography Mass Spectrometer (GC-MS) in Central Research Facility.",
        "attached_evidence_id": "EVD-VIG-404",
        "created_date": "2024-09-02",
        "resolution_notes": "Service engineer scheduled for on-site calibration on 15th Sept."
    },
    {
        "id": "TSK-VIG-003",
        "title": "Consolidate Formal Employer Feedback Stamped Copies from European Partners",
        "metric_id": "1.4.1",
        "criterion_id": "C1",
        "owner": "Dr. D. Vijaya Ramu (Dean Placements & Training)",
        "priority": "Medium",
        "status": "Open",
        "deadline": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
        "estimated_days": 14,
        "action_plan": "Dispatch official email requests to hiring partners in Germany and UK for stamped feedback on Vignan engineering curriculum alignment.",
        "attached_evidence_id": "EVD-VIG-102",
        "created_date": "2024-09-03",
        "resolution_notes": ""
    },
    {
        "id": "TSK-VIG-004",
        "title": "Publish Comprehensive CO-PO Attainment Gap Remediation Report for Batch 2024",
        "metric_id": "2.6.2",
        "criterion_id": "C2",
        "owner": "Dr. K. Ramamohan (Director IQAC)",
        "priority": "Critical",
        "status": "In Progress",
        "deadline": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "estimated_days": 12,
        "action_plan": "Synthesize Program Assessment Committee (PAC) gap action plans for PO4 (Investigation of Complex Problems) across ECE and Mechanical departments.",
        "attached_evidence_id": "EVD-VIG-206",
        "created_date": "2024-09-01",
        "resolution_notes": "ECE PAC report completed; waiting for Mechanical final review."
    },
    {
        "id": "TSK-VIG-005",
        "title": "Collect Counter-Signed Attendance Registers for Skill Certification Batch 2",
        "metric_id": "1.3.2",
        "criterion_id": "C1",
        "owner": "Dr. N. Veeranjaneyulu (Dean Academics)",
        "priority": "Medium",
        "status": "Resolved",
        "deadline": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "estimated_days": 3,
        "action_plan": "Obtain physical counter-signatures from Biotechnology HoD on student attendance rosters for EV Powertrain & Bioinformatics certificate courses.",
        "attached_evidence_id": "EVD-VIG-103",
        "created_date": "2024-08-20",
        "resolution_notes": "All 4 attendance registers counter-signed and scanned copy uploaded to digital evidence locker."
    },
    {
        "id": "TSK-VIG-006",
        "title": "Secure AIU Seal Verification Copies for 3 National Taekwondo Medals",
        "metric_id": "5.3.1",
        "criterion_id": "C5",
        "owner": "Dr. M. S. S. Rukmini (Dean Student Affairs)",
        "priority": "Low",
        "status": "Open",
        "deadline": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
        "estimated_days": 15,
        "action_plan": "Send formal representation to Association of Indian Universities (AIU) Sports Division, New Delhi for authenticated copies with official seal.",
        "attached_evidence_id": "EVD-VIG-503",
        "created_date": "2024-09-04",
        "resolution_notes": ""
    },
    {
        "id": "TSK-VIG-007",
        "title": "Integrate Remotely Authenticated Digital Signatures on Bay Area Alumni Minutes",
        "metric_id": "5.4.1",
        "criterion_id": "C5",
        "owner": "Dr. K. Ramamohan (Director IQAC)",
        "priority": "Low",
        "status": "In Review",
        "deadline": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "estimated_days": 4,
        "action_plan": "Receive DocuSign authenticated meeting minutes from Bay Area USA Alumni Chapter President and link to Criterion 5 repository.",
        "attached_evidence_id": "EVD-VIG-504",
        "created_date": "2024-09-02",
        "resolution_notes": "DocuSign copy received from Chapter President, pending final IQAC seal."
    },
    {
        "id": "TSK-VIG-008",
        "title": "Deploy Bi-annual Academic & Administrative Audit (AAA) External Peer Report",
        "metric_id": "6.5.1",
        "criterion_id": "C6",
        "owner": "Dr. K. Ramamohan (Director IQAC)",
        "priority": "Critical",
        "status": "In Progress",
        "deadline": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "estimated_days": 8,
        "action_plan": "Host 2 external peer auditors from IIT Tirupati and NIT Warangal for evaluating institutional governance and department audits.",
        "attached_evidence_id": "EVD-VIG-604",
        "created_date": "2024-09-01",
        "resolution_notes": "Auditors confirmed dates for 22nd-23rd Sept. Department dossiers printed."
    }
]


class TaskManager:
    def __init__(self, initial_tasks: Optional[List[Dict[str, Any]]] = None):
        self._tasks: List[Dict[str, Any]] = list(initial_tasks or DEFAULT_VIGNAN_TASKS)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        return list(self._tasks)

    def add_task(
        self,
        title: str,
        metric_id: str,
        criterion_id: str,
        owner: str,
        priority: str = "High",
        deadline: str = "",
        estimated_days: int = 7,
        action_plan: str = "",
        attached_evidence_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates and stores a new remediation task."""
        task_id = f"TSK-VIG-{str(uuid.uuid4())[:6].upper()}"
        if not deadline:
            deadline = (datetime.now() + timedelta(days=estimated_days)).strftime("%Y-%m-%d")

        new_task = {
            "id": task_id,
            "title": title,
            "metric_id": metric_id,
            "criterion_id": criterion_id,
            "owner": owner,
            "priority": priority,
            "status": "Open",
            "deadline": deadline,
            "estimated_days": estimated_days,
            "action_plan": action_plan,
            "attached_evidence_id": attached_evidence_id or "",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "resolution_notes": ""
        }
        self._tasks.insert(0, new_task)
        return new_task

    def update_task_status(
        self,
        task_id: str,
        new_status: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Updates the status and resolution notes of a task."""
        for t in self._tasks:
            if t["id"] == task_id:
                t["status"] = new_status
                if resolution_notes is not None:
                    t["resolution_notes"] = resolution_notes
                return True
        return False

    def filter_tasks(
        self,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        priority: Optional[str] = None,
        criterion_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters tasks by criteria."""
        results = self._tasks
        if status and status != "All":
            results = [t for t in results if t["status"] == status]
        if owner and owner != "All":
            results = [t for t in results if owner.lower() in t["owner"].lower()]
        if priority and priority != "All":
            results = [t for t in results if t["priority"] == priority]
        if criterion_id and criterion_id != "All":
            results = [t for t in results if t["criterion_id"] == criterion_id]
        return results

    def get_task_statistics(self) -> Dict[str, Any]:
        """Calculates summary KPIs for task board."""
        total = len(self._tasks)
        open_count = sum(1 for t in self._tasks if t["status"] == "Open")
        in_progress = sum(1 for t in self._tasks if t["status"] == "In Progress")
        in_review = sum(1 for t in self._tasks if t["status"] == "In Review")
        resolved = sum(1 for t in self._tasks if t["status"] == "Resolved")
        critical_count = sum(1 for t in self._tasks if t["priority"] == "Critical" and t["status"] != "Resolved")

        return {
            "total_tasks": total,
            "open": open_count,
            "in_progress": in_progress,
            "in_review": in_review,
            "resolved": resolved,
            "resolution_rate_pct": round((resolved / total * 100.0) if total > 0 else 0, 1),
            "critical_pending": critical_count
        }
