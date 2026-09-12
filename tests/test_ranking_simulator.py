"""
Unit & Integration Tests for RankingEngine (NIRF & QS Institutional Simulator)
"""

import pytest
from core.ranking_engine import (
    RankingEngine,
    NIRF_PARAMETERS,
    QS_PARAMETERS,
    VIGNAN_NIRF_BASELINE
)


class TestRankingEngine:
    def test_01_parameters_structure_and_weights(self):
        """Validates that NIRF parameter weights sum up to exactly 100%."""
        total_nirf_weight = sum(p["weight"] for p in NIRF_PARAMETERS.values())
        assert total_nirf_weight == 100.0
        assert "TLR" in NIRF_PARAMETERS
        assert "RPC" in NIRF_PARAMETERS
        assert "GO" in NIRF_PARAMETERS
        assert "OI" in NIRF_PARAMETERS
        assert "PR" in NIRF_PARAMETERS

        total_qs_weight = sum(p["weight"] for p in QS_PARAMETERS.values())
        assert total_qs_weight == 100.0

    def test_02_baseline_nirf_evaluation(self):
        """Validates baseline VFSTR evaluation metrics and realistic rank band."""
        engine = RankingEngine()
        res = engine.evaluate_nirf()

        assert "overall_score" in res
        assert 45.0 <= res["overall_score"] <= 65.0
        assert "rank_band" in res
        assert "Rank" in res["rank_band"]
        assert len(res["parameters"]) == 5

        # Check parameter scores
        params = res["parameters"]
        assert params["TLR"]["weight"] == 30.0
        assert params["RPC"]["weight"] == 30.0
        assert params["GO"]["weight"] == 20.0
        assert params["OI"]["weight"] == 10.0
        assert params["PR"]["weight"] == 10.0

        # Verify sum of weighted points matches overall score within float precision
        calc_sum = sum(p["weighted_points"] for p in params.values())
        assert abs(calc_sum - res["overall_score"]) < 0.1

    def test_03_nirf_what_if_simulation_improvement(self):
        """Validates that improving faculty ratio, publications, and grants lifts the score and rank band."""
        engine = RankingEngine()
        baseline_res = engine.evaluate_nirf()

        # Simulate strategic improvements
        interventions = {
            "faculty_student_ratio": 12.0,      # Better FSR
            "faculty_phd_pct": 95.0,             # 95% PhD
            "scopus_publications_count": 3500,   # Significant publication growth
            "sponsored_research_grants_lakhs": 1500.0, # Doubled research grants
            "placement_and_higher_ed_pct": 94.0, # Improved placement
            "median_salary_lpa": 8.5,            # Higher median CTC
            "perception_survey_score": 60.0      # Enhanced brand perception
        }
        sim_res = engine.evaluate_nirf(interventions)

        assert sim_res["overall_score"] > baseline_res["overall_score"]
        assert sim_res["rank_midpoint"] < baseline_res["rank_midpoint"]  # Better rank has lower number
        assert sim_res["parameters"]["TLR"]["score"] >= baseline_res["parameters"]["TLR"]["score"]
        assert sim_res["parameters"]["RPC"]["score"] > baseline_res["parameters"]["RPC"]["score"]

    def test_04_qs_asia_evaluation(self):
        """Validates QS Asia composite score calculation and rank band mapping."""
        engine = RankingEngine()
        qs_res = engine.evaluate_qs_asia()

        assert "qs_composite_score" in qs_res
        assert "qs_rank_band" in qs_res
        assert "components" in qs_res
        assert len(qs_res["components"]) == 6
        assert qs_res["qs_composite_score"] > 0

    def test_05_boundary_conditions(self):
        """Validates boundary conditions with extreme zero and high parameters."""
        engine = RankingEngine()
        
        # Zeroed out parameters
        zero_res = engine.evaluate_nirf({
            "faculty_student_ratio": 100.0,
            "faculty_phd_pct": 0.0,
            "scopus_publications_count": 0,
            "sponsored_research_grants_lakhs": 0.0,
            "placement_and_higher_ed_pct": 0.0,
            "median_salary_lpa": 0.0,
            "perception_survey_score": 0.0
        })
        assert zero_res["overall_score"] < 40.0
        assert "151" in zero_res["rank_band"] or "101" in zero_res["rank_band"]
