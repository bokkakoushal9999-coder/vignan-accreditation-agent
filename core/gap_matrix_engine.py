"""
Gap Prioritization Matrix Engine:
- Calculates Impact (1-10) and Effort (1-10) for identified accreditation gaps
- Categorizes gaps into 4 strategic quadrants: Quick Wins, Major Projects, Fill-in Tasks, Deprioritized
- Generates actionable remediation recommendations
"""

from typing import List, Dict, Any
import numpy as np


class GapMatrixEngine:
    def __init__(self):
        pass

    def calculate_gap_priority(
        self,
        gap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates normalized Impact and Effort scores for an identified compliance gap.
        """
        metric_weight = gap.get("metric_weight", 25)
        status = gap.get("status", "Incomplete")
        severity = gap.get("severity", "Moderate")
        metric_type = gap.get("metric_type", "QlM")
        coverage_score = gap.get("coverage_score", 50.0)

        # 1. Calculate Impact Score (Scale 1.0 - 10.0)
        # Weight contribution (25 to 50 pts is huge)
        base_impact = (metric_weight / 50.0) * 5.0  # Up to 5.0
        
        # Status deficit impact
        status_impact = 4.0 if status == "Missing" else (2.5 if severity == "High" else 1.5)
        
        # Coverage deficit
        coverage_deficit = (100.0 - coverage_score) / 100.0 * 1.5

        raw_impact = base_impact + status_impact + coverage_deficit
        impact_score = round(float(np.clip(raw_impact, 1.0, 10.0)), 1)

        # 2. Calculate Effort Score (Scale 1.0 - 10.0)
        # Missing documents require gathering, scanning, or creating approvals
        base_effort = 4.0
        
        # High-effort criteria (e.g. extramural research grants, faculty PhD recruitments, solar installations)
        crit_id = gap.get("criterion_id", "")
        metric_id = gap.get("metric_id", "")
        
        if metric_id in ["2.4.2", "3.2.1", "3.4.2", "4.1.1", "NBA-5.1", "NBA-5.5", "NBA-10.2"]:
            # High capital / long cycle effort
            base_effort = 7.5
        elif metric_id in ["1.4.1", "2.5.1", "6.2.2", "7.1.1", "NBA-1.1", "NBA-2.3", "NBA-9.1"]:
            # Policy, ERP, or survey administrative effort (Low/Medium effort)
            base_effort = 3.5
        elif status == "Incomplete":
            # Just missing a signature or appendix
            base_effort = 3.0
        else:
            base_effort = 5.5

        # Adjust for missing item count
        missing_count = len(gap.get("required_evidence_missing", []))
        effort_score = round(float(np.clip(base_effort + (missing_count * 0.4), 1.0, 10.0)), 1)

        # 3. Determine Quadrant Assignment
        # Thresholds: Impact >= 6.0 (High), Effort < 5.5 (Low)
        if impact_score >= 6.0:
            if effort_score < 5.5:
                quadrant = "Quick Win"
                quadrant_badge = "🟢 Quick Win (High Impact / Low Effort)"
                priority_rank = 1
                recommended_timeline = "1 to 2 Weeks"
            else:
                quadrant = "Major Strategic Project"
                quadrant_badge = "🔵 Major Project (High Impact / High Effort)"
                priority_rank = 2
                recommended_timeline = "1 to 3 Months"
        else:
            if effort_score < 5.5:
                quadrant = "Fill-in Task"
                quadrant_badge = "🟡 Fill-in Task (Low Impact / Low Effort)"
                priority_rank = 3
                recommended_timeline = "2 to 4 Weeks"
            else:
                quadrant = "Deprioritized / Long-term"
                quadrant_badge = "⚪ Long-term (Low Impact / High Effort)"
                priority_rank = 4
                recommended_timeline = "Next Assessment Cycle"

        # 4. Suggest Default Responsible Owner
        owner = self._suggest_task_owner(gap)

        return {
            **gap,
            "impact_score": impact_score,
            "effort_score": effort_score,
            "quadrant": quadrant,
            "quadrant_badge": quadrant_badge,
            "priority_rank": priority_rank,
            "recommended_timeline": recommended_timeline,
            "suggested_owner": owner
        }

    def _suggest_task_owner(self, gap: Dict[str, Any]) -> str:
        """Determines the most appropriate institutional owner based on metric focus."""
        crit_id = gap.get("criterion_id", "")
        metric_id = gap.get("metric_id", "")

        if "C1" in crit_id or "1." in metric_id or "NBA-1." in metric_id or "NBA-2." in metric_id:
            return "Dr. N. Veeranjaneyulu (Dean Academics) & HoDs"
        elif "C2" in crit_id or "2." in metric_id or "NBA-3." in metric_id or "NBA-8." in metric_id:
            return "Dr. K. Ramamohan (Director IQAC) & OBE Cell"
        elif "C3" in crit_id or "3." in metric_id or "NBA-5.5" in metric_id:
            return "Dr. G. Srinivasa Rao (Dean R&D)"
        elif "C4" in crit_id or "4." in metric_id or "NBA-6." in metric_id:
            return "Er. K. Sambasiva Rao (Estate Officer) & Head IT"
        elif "C5" in crit_id or "5." in metric_id or "NBA-4.3" in metric_id or "NBA-9." in metric_id:
            if "5.2.1" in metric_id or "NBA-4.3" in metric_id:
                return "Dr. D. Vijaya Ramu (Dean Placements & Training)"
            return "Dr. M. S. S. Rukmini (Dean Student Affairs)"
        elif "C6" in crit_id or "6." in metric_id or "NBA-10." in metric_id:
            return "Dr. P. M. V. Rao (Registrar) & Finance Officer"
        elif "C7" in crit_id or "7." in metric_id:
            return "Dr. K. Ramamohan (Director IQAC) & Green Committee"
        
        return "Internal Quality Assurance Cell (IQAC)"

    def build_prioritized_matrix(
        self,
        gaps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processes a list of detected gaps, calculates impact/effort for each,
        and returns organized buckets and summary stats.
        """
        prioritized = [self.calculate_gap_priority(g) for g in gaps]
        # Sort by priority rank (1 to 4) then descending impact score
        prioritized.sort(key=lambda x: (x["priority_rank"], -x["impact_score"], x["effort_score"]))

        quadrants = {
            "Quick Win": [g for g in prioritized if g["quadrant"] == "Quick Win"],
            "Major Strategic Project": [g for g in prioritized if g["quadrant"] == "Major Strategic Project"],
            "Fill-in Task": [g for g in prioritized if g["quadrant"] == "Fill-in Task"],
            "Deprioritized / Long-term": [g for g in prioritized if g["quadrant"] == "Deprioritized / Long-term"]
        }

        return {
            "all_gaps_ranked": prioritized,
            "quadrants": quadrants,
            "total_gaps_count": len(prioritized),
            "quick_wins_count": len(quadrants["Quick Win"]),
            "major_projects_count": len(quadrants["Major Strategic Project"]),
            "fill_in_count": len(quadrants["Fill-in Task"]),
            "deprioritized_count": len(quadrants["Deprioritized / Long-term"]),
            "critical_severity_count": sum(1 for g in prioritized if g.get("severity") == "Critical")
        }
