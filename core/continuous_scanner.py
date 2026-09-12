"""
Continuous Readiness Scanner Engine:
- Automated continuous audit scanner evaluating institutional accreditation criteria against live evidence
- Detects criterion-level compliance, expiring evidence, unverified drafts, and documentation gaps
- Generates actionable diagnostic reports with direct remediation links
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from core.evidence_validator import EvidenceValidator
from core.criteria_registry import get_framework_criteria, NAAC_CRITERIA, NBA_CRITERIA


class ContinuousReadinessScanner:
    """
    Continuous accreditation readiness scanner that systematically evaluates
    compliance across all NAAC and NBA criteria against the institutional evidence repository.
    """

    def __init__(self, active_academic_year: str = "2023-24"):
        self.active_academic_year = active_academic_year
        self.validator = EvidenceValidator(active_academic_year=active_academic_year)

    def scan_all_criteria(
        self,
        framework: str = "NAAC",
        evidence_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Runs comprehensive continuous readiness scan across all criteria in the specified framework.
        """
        if evidence_list is None:
            evidence_list = []

        criteria_dict = get_framework_criteria(framework)
        scan_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        criterion_results = []
        total_max_marks = 0.0
        total_estimated_score = 0.0
        all_expiring_evidence = []
        all_unverified_evidence = []
        all_critical_gaps = []

        # Validate all evidence records first for lookup
        validation_report = self.validator.validate_evidence_batch(evidence_list)
        evidence_by_id = {r["evidence_id"]: r for r in validation_report["records"]}

        for crit_key, crit in criteria_dict.items():
            crit_id = crit.get("id", crit_key)
            crit_name = crit["name"]
            crit_weight = float(crit.get("weight", 100))
            total_max_marks += crit_weight

            # Find evidence mapped to this criterion
            matching_evidence = []
            for ev in evidence_list:
                app_crits = [c.strip().upper() for c in ev.get("applicable_criteria", [])]
                if (crit_id.upper() in app_crits or 
                    any(crit_id.upper() in c for c in app_crits) or 
                    crit_key.upper() in app_crits or 
                    any(crit_key.upper() in c for c in app_crits)):
                    matching_evidence.append(ev)

            # Analyze matching evidence health
            crit_ev_count = len(matching_evidence)
            verified_count = 0
            pending_count = 0
            expired_count = 0
            defect_count = 0

            for ev in matching_evidence:
                ev_id = ev.get("id")
                val_rec = evidence_by_id.get(ev_id)
                if val_rec:
                    if val_rec["overall_status"] == "READY_VERIFIED":
                        verified_count += 1
                    elif val_rec["overall_status"] == "PENDING_HUMAN_SIGN_OFF":
                        pending_count += 1
                        all_unverified_evidence.append({
                            "criterion_id": crit_id,
                            "evidence_id": ev_id,
                            "title": ev.get("title"),
                            "department": ev.get("department")
                        })
                    else:
                        defect_count += 1

                    if not val_rec["dimensions"]["recency"]["passed"]:
                        expired_count += 1
                        all_expiring_evidence.append({
                            "criterion_id": crit_id,
                            "evidence_id": ev_id,
                            "title": ev.get("title"),
                            "academic_year": ev.get("academic_year"),
                            "department": ev.get("department")
                        })

            # Calculate Criterion Readiness Health
            # Minimum expected evidence count is 3 per criterion
            expected_min_evidence = 3
            coverage_ratio = min(crit_ev_count / expected_min_evidence, 1.0)
            quality_ratio = (verified_count + 0.7 * pending_count) / max(crit_ev_count, 1) if crit_ev_count > 0 else 0.0

            criterion_readiness_pct = round((coverage_ratio * 0.4 + quality_ratio * 0.6) * 100.0, 1)
            estimated_marks = round((criterion_readiness_pct / 100.0) * crit_weight, 1)
            total_estimated_score += estimated_marks

            # Status classification
            if criterion_readiness_pct >= 85.0 and defect_count == 0:
                status = "COMPLIANT"
                status_label = "🟢 Compliant & Audit Ready"
                status_color = "#10B981"
            elif criterion_readiness_pct >= 60.0:
                status = "AT_RISK"
                status_label = "🟡 At Risk / Pending Sign-offs"
                status_color = "#F59E0B"
            else:
                status = "CRITICAL_GAP"
                status_label = "🔴 Critical Documentation Gap"
                status_color = "#EF4444"
                all_critical_gaps.append({
                    "criterion_id": crit_id,
                    "criterion_name": crit_name,
                    "readiness_pct": criterion_readiness_pct,
                    "evidence_count": crit_ev_count,
                    "action_required": f"Upload mandatory verified evidence documents for {crit_name} (Current: {crit_ev_count}/{expected_min_evidence})."
                })

            criterion_results.append({
                "criterion_id": crit_id,
                "criterion_name": crit_name,
                "max_weight": crit_weight,
                "estimated_marks": estimated_marks,
                "readiness_pct": criterion_readiness_pct,
                "status": status,
                "status_label": status_label,
                "status_color": status_color,
                "evidence_count": crit_ev_count,
                "verified_count": verified_count,
                "pending_count": pending_count,
                "expired_count": expired_count,
                "defect_count": defect_count,
                "sub_criteria": crit.get("sub_criteria", [])
            })

        # Calculate Institutional Aggregate Score & Grade Forecast
        overall_readiness_pct = round((total_estimated_score / total_max_marks * 100.0), 1) if total_max_marks > 0 else 0.0
        
        # NAAC CGPA Forecast (scale of 4.00)
        cgpa_forecast = round((overall_readiness_pct / 100.0) * 4.0, 2)
        if cgpa_forecast >= 3.51:
            grade_forecast = "A++ (Institution of Excellence)"
            grade_color = "#10B981"
        elif cgpa_forecast >= 3.26:
            grade_forecast = "A+ (Very Good)"
            grade_color = "#3B82F6"
        elif cgpa_forecast >= 3.01:
            grade_forecast = "A (Good)"
            grade_color = "#6366F1"
        elif cgpa_forecast >= 2.01:
            grade_forecast = "B++ / B+ (Satisfactory)"
            grade_color = "#F59E0B"
        else:
            grade_forecast = "C / Not Accredited"
            grade_color = "#EF4444"

        compliant_criteria_count = sum(1 for c in criterion_results if c["status"] == "COMPLIANT")
        at_risk_criteria_count = sum(1 for c in criterion_results if c["status"] == "AT_RISK")
        critical_gap_criteria_count = sum(1 for c in criterion_results if c["status"] == "CRITICAL_GAP")

        return {
            "framework": framework,
            "scan_timestamp": scan_timestamp,
            "active_academic_year": self.active_academic_year,
            "overall_readiness_pct": overall_readiness_pct,
            "cgpa_forecast": cgpa_forecast,
            "grade_forecast": grade_forecast,
            "grade_color": grade_color,
            "total_max_marks": total_max_marks,
            "total_estimated_score": round(total_estimated_score, 1),
            "summary_counts": {
                "total_criteria": len(criterion_results),
                "compliant": compliant_criteria_count,
                "at_risk": at_risk_criteria_count,
                "critical_gaps": critical_gap_criteria_count,
                "total_evidence_evaluated": len(evidence_list),
                "expiring_evidence_count": len(all_expiring_evidence),
                "unverified_evidence_count": len(all_unverified_evidence)
            },
            "expiring_evidence": all_expiring_evidence,
            "unverified_evidence": all_unverified_evidence,
            "critical_gaps": all_critical_gaps,
            "criteria_breakdown": criterion_results
        }
