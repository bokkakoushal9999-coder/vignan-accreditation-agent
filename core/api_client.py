"""
Accreditation API Client:
- Provides typed HTTP REST client for communicating with FastAPI backend
- Supports dynamic port resolution and environment variable configuration
- Provides fallback and offline resilience for Streamlit frontend integration
"""

import os
import requests
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

DEFAULT_BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
DEFAULT_BACKEND_URL = os.getenv("BACKEND_API_URL", f"http://127.0.0.1:{DEFAULT_BACKEND_PORT}")
BACKEND_API_BASE = DEFAULT_BACKEND_URL


def get_backend_url(host: Optional[str] = None, port: Optional[Union[int, str]] = None) -> str:
    """Dynamically resolves the FastAPI backend URL from environment or parameters."""
    if os.getenv("BACKEND_API_URL"):
        return os.getenv("BACKEND_API_URL").rstrip("/")
    h = host or os.getenv("HOST", "127.0.0.1")
    p = str(port or os.getenv("BACKEND_PORT", os.getenv("PORT", "8000")))
    return f"http://{h}:{p}".rstrip("/")


class AccreditationApiClient:
    """
    HTTP Client for VFSTR AI Accreditation Agent FastAPI Backend.
    Provides methods covering all REST endpoints with automatic timeout management,
    persistent connection pooling, and graceful fallback handling.
    """

    def __init__(self, base_url: Optional[str] = None):
        if base_url:
            self._base_url: Optional[str] = str(base_url).rstrip("/")
        else:
            self._base_url = None
        self.session = requests.Session()

    @property
    def base_url(self) -> str:
        """Returns explicitly configured base_url or dynamically evaluates environment."""
        if self._base_url:
            return self._base_url
        return get_backend_url()

    @base_url.setter
    def base_url(self, value: Optional[str]):
        self._base_url = str(value).rstrip("/") if value else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Closes the underlying HTTP session."""
        try:
            self.session.close()
        except Exception:
            pass



    def check_health(self) -> Dict[str, Any]:
        """Checks if the FastAPI backend server is reachable."""
        try:
            resp = self.session.get(f"{self.base_url}/api/health", timeout=1.5)
            if resp.status_code == 200:
                return {"connected": True, "data": resp.json()}
        except Exception:
            pass
        return {"connected": False, "data": None}

    def get_criteria(self, framework: str = "NAAC") -> Optional[Dict[str, Any]]:
        """Calls the /api/criteria endpoint."""
        try:
            resp = self.session.get(f"{self.base_url}/api/criteria", params={"framework": framework}, timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_evidence(
        self,
        department: Optional[str] = None,
        academic_year: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Calls the /api/evidence GET endpoint with optional filters."""
        try:
            params = {}
            if department and department != "All Departments":
                params["department"] = department
            if academic_year and academic_year != "All Years":
                params["academic_year"] = academic_year
            if status and status != "All":
                params["status"] = status
            if search:
                params["search"] = search

            resp = self.session.get(f"{self.base_url}/api/evidence", params=params, timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def ingest_evidence(self, evidence_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calls the /api/evidence POST endpoint to ingest and semantically map evidence."""
        try:
            resp = self.session.post(f"{self.base_url}/api/evidence", json=evidence_data, timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def upload_evidence_file(
        self,
        file_bytes: bytes,
        filename: str,
        framework: str = "NAAC",
        department: Optional[str] = None,
        academic_year: Optional[str] = None,
        title: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Calls the /api/evidence/upload POST endpoint with multipart file payload."""
        try:
            files = {"file": (filename, file_bytes, "application/octet-stream")}
            data = {"framework": framework}
            if department:
                data["department"] = department
            if academic_year:
                data["academic_year"] = academic_year
            if title:
                data["title"] = title

            resp = self.session.post(f"{self.base_url}/api/evidence/upload", files=files, data=data, timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def delete_evidence(self, evidence_id: str) -> bool:
        """Calls the /api/evidence/{evidence_id} DELETE endpoint."""
        try:
            resp = self.session.delete(f"{self.base_url}/api/evidence/{evidence_id}", timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    def evaluate_framework(
        self,
        framework: str = "NAAC",
        simulated_adjustments: Optional[Dict[str, float]] = None
    ) -> Optional[Dict[str, Any]]:
        """Calls the /api/evaluate endpoint."""
        try:
            payload = {"framework": framework, "simulated_adjustments": simulated_adjustments or {}}
            resp = self.session.post(f"{self.base_url}/api/evaluate", json=payload, timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_gaps(self, framework: str = "NAAC") -> Optional[Dict[str, Any]]:
        """Calls the /api/gaps endpoint."""
        try:
            resp = self.session.get(f"{self.base_url}/api/gaps", params={"framework": framework}, timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_tasks(self, status: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Calls the /api/tasks endpoint."""
        try:
            params = {}
            if status and status != "All":
                params["status"] = status
            resp = self.session.get(f"{self.base_url}/api/tasks", params=params, timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calls the /api/tasks POST endpoint."""
        try:
            resp = self.session.post(f"{self.base_url}/api/tasks", json=task_data, timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def update_task_status(self, task_id: str, status: str, notes: Optional[str] = None) -> bool:
        """Calls the /api/tasks/{task_id} PATCH endpoint."""
        try:
            payload = {"status": status, "resolution_notes": notes}
            resp = self.session.patch(f"{self.base_url}/api/tasks/{task_id}", json=payload, timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    def generate_narrative(
        self,
        metric_id: str,
        framework: str = "NAAC",
        tone: str = "Executive & Evidence-Backed",
        notes: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Calls the /api/narrative/generate endpoint."""
        try:
            payload = {
                "metric_id": metric_id,
                "framework": framework,
                "focus_tone": tone,
                "additional_notes": notes
            }
            resp = self.session.post(f"{self.base_url}/api/narrative/generate", json=payload, timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def verify_evidence(self, verify_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calls the /api/verify endpoint."""
        try:
            resp = self.session.post(f"{self.base_url}/api/verify", json=verify_data, timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_audit_trail(self) -> Optional[Dict[str, Any]]:
        """Calls the /api/audit-trail endpoint."""
        try:
            resp = self.session.get(f"{self.base_url}/api/audit-trail", timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_audit_summary(self) -> Optional[Dict[str, Any]]:
        """Calls the /api/audit-trail endpoint and extracts the summary object."""
        res = self.get_audit_trail()
        if res and isinstance(res, dict):
            return res.get("summary")
        return None

    def export_pdf(self, framework: str = "NAAC") -> Optional[bytes]:
        """Calls the /api/export-pdf endpoint and returns raw PDF bytes."""
        try:
            resp = self.session.get(f"{self.base_url}/api/export-pdf", params={"framework": framework}, timeout=10.0)
            if resp.status_code == 200:
                return resp.content
        except Exception:
            pass
        return None

    def get_db_stats(self) -> Optional[Dict[str, Any]]:
        """Calls the /api/db/stats endpoint."""
        try:
            resp = self.session.get(f"{self.base_url}/api/db/stats", timeout=2.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def reset_db(self) -> Optional[Dict[str, Any]]:
        """Calls the /api/db/reset endpoint."""
        try:
            resp = self.session.post(f"{self.base_url}/api/db/reset", timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def export_db_json(self) -> Optional[Dict[str, Any]]:
        """Calls the /api/db/export endpoint."""
        try:
            resp = self.session.get(f"{self.base_url}/api/db/export", timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_validation_report(self, target_criterion_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Calls the /api/validation/report endpoint."""
        try:
            params = {}
            if target_criterion_id:
                params["target_criterion_id"] = target_criterion_id
            resp = self.session.get(f"{self.base_url}/api/validation/report", params=params, timeout=4.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def run_scanner(self, framework: str = "NAAC") -> Optional[Dict[str, Any]]:
        """Calls the /api/scanner/run endpoint."""
        try:
            resp = self.session.get(f"{self.base_url}/api/scanner/run", params={"framework": framework}, timeout=4.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def validate_submission(self, framework: str = "NAAC") -> Optional[Dict[str, Any]]:
        """Calls the /api/submission/validate endpoint."""
        try:
            resp = self.session.get(f"{self.base_url}/api/submission/validate", params={"framework": framework}, timeout=4.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def build_submission(self, build_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calls the /api/submission/build POST endpoint."""
        try:
            resp = self.session.post(f"{self.base_url}/api/submission/build", json=build_payload, timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_mock_visit_questions(
        self,
        category: Optional[str] = None,
        criterion_id: Optional[str] = None,
        framework: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Calls the /api/mock-visit/questions endpoint."""
        try:
            params = {}
            if category and category != "All Categories":
                params["category"] = category
            if criterion_id and criterion_id != "All Criteria":
                params["criterion_id"] = criterion_id
            if framework and framework != "All Frameworks":
                params["framework"] = framework
            resp = self.session.get(f"{self.base_url}/api/mock-visit/questions", params=params, timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def evaluate_mock_visit(self, eval_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calls the /api/mock-visit/evaluate endpoint."""
        try:
            resp = self.session.post(f"{self.base_url}/api/mock-visit/evaluate", json=eval_payload, timeout=4.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    # Compatibility and convenience method aliases
    reset_database = reset_db
    get_all_evidence = get_evidence
    get_database_stats = get_db_stats
    get_database_statistics = get_db_stats
    export_database_json = export_db_json



# Global singleton client instance
_api_client_instance: Optional[AccreditationApiClient] = None


def get_api_client(base_url: Optional[str] = None) -> AccreditationApiClient:
    """Returns or creates the shared AccreditationApiClient instance."""
    global _api_client_instance
    if _api_client_instance is None or base_url:
        _api_client_instance = AccreditationApiClient(base_url)
    return _api_client_instance


__all__ = [
    "AccreditationApiClient",
    "get_api_client",
    "get_backend_url",
    "BACKEND_API_BASE",
    "DEFAULT_BACKEND_PORT",
    "DEFAULT_BACKEND_URL"
]

