"""
Task Manager Engine:
- Manages corrective remediation tasks for identified accreditation gaps
- Supports status transitions (Open -> In Progress -> In Review -> Resolved)
- Assigns institutional owners, deadlines, priority levels, and evidence attachments
- Seamlessly integrates with SQLite database backend (data/accreditation.db)
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
        "title": "Authenticate Doctoral Degree Equivalence for 14 New Faculty Joinees",
        "metric_id": "2.4.2",
        "criterion_id": "C2",
        "owner": "Dr. N. Veeranjaneyulu (Dean Academics)",
        "priority": "High",
        "status": "Open",
        "deadline": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "estimated_days": 10,
        "action_plan": "Collect authenticated UGC equivalence verification letters for 14 newly recruited faculty members holding doctorates from overseas/interdisciplinary universities.",
        "attached_evidence_id": "EVD-VIG-202",
        "created_date": "2024-09-03",
        "resolution_notes": ""
    },
    {
        "id": "TSK-VIG-005",
        "title": "Audit Captive Solar Rooftop Net-Metering Settlement Statement (1.2 MW)",
        "metric_id": "7.1.2",
        "criterion_id": "C7",
        "owner": "Er. K. Sambasiva Rao (Estate Officer)",
        "priority": "Medium",
        "status": "In Progress",
        "deadline": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "estimated_days": 7,
        "action_plan": "Reconcile Andhra Pradesh Southern Power Distribution Company Ltd (APSPDCL) quarterly net metering billing settlement records for 1.2 MW campus solar installation.",
        "attached_evidence_id": "EVD-VIG-701",
        "created_date": "2024-09-04",
        "resolution_notes": "APSPDCL DISCOM statement received for Q1 & Q2. Reconciling Q3 solar credit."
    },
    {
        "id": "TSK-VIG-006",
        "title": "Complete Formal Financial Assistance Receipts for 380 Rural Girl Students",
        "metric_id": "5.1.2",
        "criterion_id": "C5",
        "owner": "Dr. M. S. S. Rukmini (Dean Student Affairs)",
        "priority": "High",
        "status": "Open",
        "deadline": (datetime.now() + timedelta(days=18)).strftime("%Y-%m-%d"),
        "estimated_days": 12,
        "action_plan": "Compile counter-signed institutional fee-concession ledgers and bank disbursement registers for 380 underprivileged girl student scholars (INR 42.8 Lakhs).",
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
    """
    Manages accreditation remediation tasks with dual-mode support:
    - Persistent SQLite database mode via DatabaseManager (data/accreditation.db)
    - Fallback in-memory mode for standalone testing and disconnected states
    """

    def __init__(
        self,
        initial_tasks: Optional[List[Dict[str, Any]]] = None,
        use_db: bool = True,
        db_path: Optional[str] = None,
        *args,
        **kwargs
    ):
        self.use_db = use_db
        self.db = None
        self._tasks: List[Dict[str, Any]] = []

        if initial_tasks is not None:
            self._tasks = list(initial_tasks)
        elif self.use_db:
            try:
                from core.database import get_database
                self.db = get_database(db_path)
                db_tasks = self.db.get_all_tasks()
                if db_tasks:
                    self._tasks = db_tasks
                else:
                    self._tasks = list(DEFAULT_VIGNAN_TASKS)
            except Exception:
                self.db = None
                self._tasks = list(DEFAULT_VIGNAN_TASKS)
        else:
            self._tasks = list(DEFAULT_VIGNAN_TASKS)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retrieves all tasks from the SQLite database or in-memory list."""
        if self.use_db and self.db:
            try:
                db_tasks = self.db.get_all_tasks()
                if db_tasks:
                    self._tasks = db_tasks
            except Exception:
                pass
        return list(self._tasks)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Finds a single task by ID."""
        for t in self.get_all_tasks():
            if t.get("id") == task_id:
                return dict(t)
        return None

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
        attached_evidence_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Creates and persists a new remediation task."""
        task_id = f"TSK-VIG-{str(uuid.uuid4())[:6].upper()}"
        if not deadline:
            deadline = (datetime.now() + timedelta(days=estimated_days)).strftime("%Y-%m-%d")

        new_task = {
            "id": task_id,
            "title": title,
            "metric_id": metric_id,
            "criterion_id": criterion_id,
            "owner": owner or "Director IQAC",
            "owner_role": owner or "Director IQAC",
            "owner_department": "IQAC",
            "priority": priority or "High",
            "status": "Open",
            "deadline": deadline,
            "estimated_days": estimated_days,
            "action_plan": action_plan or "Remediate identified compliance gap.",
            "attached_evidence_id": attached_evidence_id or "",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "resolution_notes": "",
            "completion_percentage": 0.0
        }

        if self.use_db and self.db:
            try:
                self.db.insert_task(new_task)
                self._tasks = self.db.get_all_tasks()
            except Exception:
                self._tasks.insert(0, new_task)
        else:
            self._tasks.insert(0, new_task)

        return new_task

    def update_task_status(
        self,
        task_id: str,
        new_status: str,
        resolution_notes: Optional[str] = None,
        *args,
        **kwargs
    ) -> bool:
        """Updates the status and resolution notes of a task in SQLite."""
        if self.use_db and self.db:
            try:
                notes = resolution_notes or ""
                success = self.db.update_task_status(task_id, new_status, notes)
                self._tasks = self.db.get_all_tasks()
                if success:
                    return True
            except Exception:
                pass

        # Fallback local update
        for t in self._tasks:
            if t.get("id") == task_id:
                t["status"] = new_status
                if resolution_notes is not None:
                    t["resolution_notes"] = resolution_notes
                return True
        return False

    def delete_task(self, task_id: str) -> bool:
        """Deletes a task by ID."""
        if self.use_db and self.db:
            try:
                success = self.db.delete_task(task_id)
                self._tasks = self.db.get_all_tasks()
                return success
            except Exception:
                pass
        orig_len = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.get("id") != task_id]
        return len(self._tasks) < orig_len

    def filter_tasks(
        self,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        priority: Optional[str] = None,
        criterion_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters tasks by status, owner, priority, or criterion."""
        results = self.get_all_tasks()
        if status and status != "All":
            s_target = status.strip().lower().replace("_", " ")
            results = [t for t in results if str(t.get("status", "")).strip().lower().replace("_", " ") == s_target]
        if owner and owner != "All":
            results = [t for t in results if owner.lower() in str(t.get("owner", "")).lower()]
        if priority and priority != "All":
            results = [t for t in results if str(t.get("priority", "")).strip().lower() == priority.strip().lower()]
        if criterion_id and criterion_id != "All":
            results = [t for t in results if str(t.get("criterion_id", "")).strip().lower() == criterion_id.strip().lower()]
        return results

    def get_task_statistics(self) -> Dict[str, Any]:
        """Calculates summary KPIs for the task board."""
        tasks = self.get_all_tasks()
        total = len(tasks)

        def _norm(status_val):
            return str(status_val or "").strip().upper().replace(" ", "_")

        open_count = sum(1 for t in tasks if _norm(t.get("status")) in ["OPEN", "DRAFT", "PENDING"])
        in_progress = sum(1 for t in tasks if _norm(t.get("status")) in ["IN_PROGRESS", "PROGRESS", "ACTIVE"])
        in_review = sum(1 for t in tasks if _norm(t.get("status")) in ["IN_REVIEW", "REVIEW", "UNDER_REVIEW"])
        resolved = sum(1 for t in tasks if _norm(t.get("status")) in ["RESOLVED", "COMPLETED", "CLOSED"])

        # Any remaining tasks not matching the above buckets get counted as open
        categorized = open_count + in_progress + in_review + resolved
        if categorized < total:
            open_count += (total - categorized)

        critical_count = sum(
            1 for t in tasks
            if str(t.get("priority", "")).strip().lower() == "critical"
            and _norm(t.get("status")) not in ["RESOLVED", "COMPLETED", "CLOSED"]
        )

        return {
            "total_tasks": total,
            "open": open_count,
            "in_progress": in_progress,
            "in_review": in_review,
            "resolved": resolved,
            "resolution_rate_pct": round((resolved / total * 100.0) if total > 0 else 0.0, 1),
            "critical_pending": critical_count
        }
