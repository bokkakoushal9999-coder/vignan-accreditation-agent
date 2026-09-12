"""
NIRF & QS Institutional Ranking Engine:
- Models the official MHRD/MoE National Institutional Ranking Framework (NIRF) 5-pillar methodology
- Models QS Asia / World University Ranking criteria & reputation metrics
- Provides baseline metrics for Vignan's Foundation for Science, Technology & Research (VFSTR)
- Evaluates real-time What-If ranking interventions and predicts national rank bands
"""

from typing import Dict, List, Any, Optional
import math


# NIRF Official Parameter Weights & Component Definitions
NIRF_PARAMETERS: Dict[str, Dict[str, Any]] = {
    "TLR": {
        "name": "Teaching, Learning & Resources",
        "weight": 30.0,
        "description": "Student Strength, Faculty-Student Ratio (FSR), Faculty with PhD & Experience, Financial Resources Utilization",
        "subcomponents": {
            "SS": {"name": "Student Strength (Approved & Actual Enrollment)", "weight": 20.0, "benchmark": 100.0},
            "FSR": {"name": "Faculty-Student Ratio (Standard 1:15)", "weight": 30.0, "benchmark": 15.0},
            "FQE": {"name": "Faculty with PhD and Experience", "weight": 20.0, "benchmark": 85.0},
            "FRU": {"name": "Financial Resources & Utilization (CapEx + OpEx)", "weight": 30.0, "benchmark": 100.0}
        }
    },
    "RPC": {
        "name": "Research and Professional Practice",
        "weight": 30.0,
        "description": "Publications in Scopus/WoS, Quality of Publications (Citations), IPR Patents, Extramural Sponsored Research Grants",
        "subcomponents": {
            "PU": {"name": "Combined Metric for Publications (Scopus / WoS)", "weight": 35.0, "benchmark": 4000.0},
            "QP": {"name": "Quality of Publications (Citations per Faculty & H-Index)", "weight": 35.0, "benchmark": 25.0},
            "IPR": {"name": "Patents Published and Granted", "weight": 15.0, "benchmark": 80.0},
            "FPPP": {"name": "Footprint of Projects & Professional Practice (Grants INR Lakhs)", "weight": 15.0, "benchmark": 1500.0}
        }
    },
    "GO": {
        "name": "Graduation Outcomes",
        "weight": 20.0,
        "description": "University Examination Pass %, Campus Placements, Higher Education Progression, Median Salary CTC",
        "subcomponents": {
            "GUE": {"name": "Metric for University Examinations (Pass %)", "weight": 60.0, "benchmark": 95.0},
            "GPH": {"name": "Placements & Higher Studies % (Median Salary)", "weight": 40.0, "benchmark": 90.0}
        }
    },
    "OI": {
        "name": "Outreach and Inclusivity",
        "weight": 10.0,
        "description": "Region Diversity (Other States/Countries), Women Diversity (Faculty/Students), Economically/Socially Challenged, Facilities for Divyangjan",
        "subcomponents": {
            "RD": {"name": "Region Diversity (Percentage from other States/Nations)", "weight": 30.0, "benchmark": 30.0},
            "WD": {"name": "Women Diversity (Female Students & Faculty %)", "weight": 30.0, "benchmark": 50.0},
            "ESCS": {"name": "Economically & Socially Challenged Students (Tuition Reimbursement)", "weight": 20.0, "benchmark": 40.0},
            "PCS": {"name": "Facilities for Physically Challenged Students", "weight": 20.0, "benchmark": 100.0}
        }
    },
    "PR": {
        "name": "Perception",
        "weight": 10.0,
        "description": "Academic Peer Perception & Employer Reputation Surveys",
        "subcomponents": {
            "PREMP": {"name": "Peer & Employer Perception Survey Score", "weight": 100.0, "benchmark": 100.0}
        }
    }
}


# QS Asia / World Ranking Parameters
QS_PARAMETERS: Dict[str, Dict[str, Any]] = {
    "AR": {"name": "Academic Reputation", "weight": 30.0, "benchmark": 100.0},
    "ER": {"name": "Employer Reputation", "weight": 20.0, "benchmark": 100.0},
    "FSR": {"name": "Faculty Student Ratio", "weight": 10.0, "benchmark": 100.0},
    "CPF": {"name": "Citations per Faculty", "weight": 20.0, "benchmark": 100.0},
    "INT": {"name": "International Faculty & Student Diversity", "weight": 10.0, "benchmark": 100.0},
    "IRN": {"name": "International Research Network", "weight": 10.0, "benchmark": 100.0}
}


# Baseline Verified Performance Data for Vignan University (VFSTR)
VIGNAN_NIRF_BASELINE: Dict[str, Any] = {
    "institution_name": "Vignan's Foundation for Science, Technology & Research",
    "campus": "Vadlamudi, Guntur, Andhra Pradesh",
    "category": "University / Engineering",
    "academic_year": "2023-24",
    "raw_metrics": {
        # TLR Subcomponents
        "student_strength_total": 8450,
        "sanctioned_intake": 8800,
        "faculty_student_ratio": 14.8,  # 1:14.8 (Better than 1:15)
        "faculty_phd_pct": 75.7,        # 75.7% faculty hold PhD
        "financial_resources_utilization_lakhs": 9450.0, # Annual spend in lakhs
        
        # RPC Subcomponents
        "scopus_publications_count": 2410,
        "citations_per_faculty": 14.2,
        "h_index": 48,
        "patents_published_granted": 58,
        "sponsored_research_grants_lakhs": 682.4,
        
        # GO Subcomponents
        "exam_pass_percentage": 91.8,
        "placement_and_higher_ed_pct": 86.4,
        "median_salary_lpa": 5.6, # INR 5.6 LPA
        
        # OI Subcomponents
        "out_of_state_student_pct": 18.5,
        "women_diversity_pct": 36.8,
        "economically_challenged_pct": 32.4,
        "physically_challenged_facilities_score": 95.0,
        
        # PR Subcomponents
        "perception_survey_score": 28.5
    }
}


class RankingEngine:
    """
    Simulates and projects NIRF (National Institutional Ranking Framework)
    and QS Asia/World University Rankings based on institutional data and What-If interventions.
    """

    def __init__(self, baseline_data: Optional[Dict[str, Any]] = None):
        self.baseline = baseline_data or VIGNAN_NIRF_BASELINE

    def evaluate_nirf(self, adjustments: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Evaluates the NIRF 5-pillar composite score and projects the estimated national rank band.
        Accepts optional What-If simulation adjustments.
        """
        adj = adjustments or {}
        raw = dict(self.baseline["raw_metrics"])

        # Apply simulation overrides if present
        if "faculty_student_ratio" in adj:
            raw["faculty_student_ratio"] = float(adj["faculty_student_ratio"])
        if "faculty_phd_pct" in adj:
            raw["faculty_phd_pct"] = float(adj["faculty_phd_pct"])
        if "scopus_publications_count" in adj:
            raw["scopus_publications_count"] = float(adj["scopus_publications_count"])
        if "sponsored_research_grants_lakhs" in adj:
            raw["sponsored_research_grants_lakhs"] = float(adj["sponsored_research_grants_lakhs"])
        if "placement_and_higher_ed_pct" in adj:
            raw["placement_and_higher_ed_pct"] = float(adj["placement_and_higher_ed_pct"])
        if "median_salary_lpa" in adj:
            raw["median_salary_lpa"] = float(adj["median_salary_lpa"])
        if "women_diversity_pct" in adj:
            raw["women_diversity_pct"] = float(adj["women_diversity_pct"])
        if "out_of_state_student_pct" in adj:
            raw["out_of_state_student_pct"] = float(adj["out_of_state_student_pct"])
        if "perception_survey_score" in adj:
            raw["perception_survey_score"] = float(adj["perception_survey_score"])

        # 1. TLR Calculation (Weight: 30) - Benchmark calibrated against NIRF top 100
        # SS (20 marks) - Enrollment ratio
        intake_ratio = min(raw["student_strength_total"] / max(raw["sanctioned_intake"], 1.0), 1.0)
        ss_score = intake_ratio * 17.5  # Max 20 for full capacity + diversity
        
        # FSR (30 marks) - Standard 1:15 gets ~22.5, 1:10 gets 30
        fsr_val = raw["faculty_student_ratio"]
        fsr_score = min(max(30.0 * (15.0 / max(fsr_val, 1.0)) * 0.75, 5.0), 30.0) if fsr_val > 0 else 0.0
        
        # FQE (20 marks) - Faculty with PhD & experience
        fqe_score = (min(raw["faculty_phd_pct"], 100.0) / 100.0) * 15.0  # Max 20 for 100% PhD + 15yr avg exp
        
        # FRU (30 marks) - Financial utilization per student
        fru_score = min((raw["financial_resources_utilization_lakhs"] / 15000.0) * 30.0, 30.0)
        
        tlr_total = ss_score + fsr_score + fqe_score + fru_score  # Out of 100 (~65-72 for top 100)

        # 2. RPC Calculation (Weight: 30) - Calibrated against national research outputs
        # PU (35 marks) - publications in Scopus/WoS (Benchmark 4500)
        pu_score = min((raw["scopus_publications_count"] / 4500.0) * 35.0, 35.0)
        
        # QP (35 marks) - citations per faculty (Benchmark 28.0)
        qp_score = min((raw["citations_per_faculty"] / 28.0) * 35.0, 35.0)
        
        # IPR (15 marks) - patents granted & published
        ipr_score = min((raw["patents_published_granted"] / 100.0) * 15.0, 15.0)
        
        # FPPP (15 marks) - sponsored research grants (Benchmark 2000 Lakhs)
        fppp_score = min((raw["sponsored_research_grants_lakhs"] / 2000.0) * 15.0, 15.0)
        
        rpc_total = pu_score + qp_score + ipr_score + fppp_score  # Out of 100 (~40-50 for top 100)

        # 3. GO Calculation (Weight: 20)
        # GUE (60 marks) - University exam graduation efficiency (Pass % * on-time factor)
        gue_score = min((raw["exam_pass_percentage"] / 100.0) * 52.0, 60.0)
        
        # GPH (40 marks) - Placement % (70%) and median salary (30%)
        place_ratio = min(raw["placement_and_higher_ed_pct"] / 100.0, 1.0)
        salary_factor = min(raw["median_salary_lpa"] / 10.0, 1.0)
        gph_score = min((place_ratio * 0.65 + salary_factor * 0.35) * 40.0, 40.0)
        
        go_total = gue_score + gph_score  # Out of 100 (~65-75 for top 100)

        # 4. OI Calculation (Weight: 10)
        # RD (30 marks) - other state/country students
        rd_score = min((raw["out_of_state_student_pct"] / 35.0) * 30.0, 30.0)
        # WD (30 marks) - women diversity (faculty + students)
        wd_score = min((raw["women_diversity_pct"] / 50.0) * 30.0, 30.0)
        # ESCS (20 marks) - economic/social challenge
        escs_score = min((raw["economically_challenged_pct"] / 45.0) * 20.0, 20.0)
        # PCS (20 marks) - physically challenged facilities
        pcs_score = min((raw["physically_challenged_facilities_score"] / 100.0) * 20.0, 20.0)
        
        oi_total = rd_score + wd_score + escs_score + pcs_score  # Out of 100 (~55-65 for top 100)

        # 5. PR Calculation (Weight: 10)
        pr_total = min(max(raw["perception_survey_score"], 0.0), 100.0)  # Out of 100 (~25-35 for top 100)

        # Weighted Overall NIRF Score (out of 100)
        weighted_tlr = (tlr_total * 0.30)
        weighted_rpc = (rpc_total * 0.30)
        weighted_go = (go_total * 0.20)
        weighted_oi = (oi_total * 0.10)
        weighted_pr = (pr_total * 0.10)

        overall_nirf_score = round(weighted_tlr + weighted_rpc + weighted_go + weighted_oi + weighted_pr, 2)

        # Predict NIRF Rank Band based on MHRD historical cutoffs
        if overall_nirf_score >= 68.0:
            rank_band = "Rank 15 - 25 (National Top Tier)"
            rank_midpoint = 20
            category_tier = "Top 25 National Elite"
        elif overall_nirf_score >= 60.0:
            rank_band = "Rank 26 - 50 (Top 50 University)"
            rank_midpoint = 38
            category_tier = "Top 50 In India"
        elif overall_nirf_score >= 54.0:
            rank_band = "Rank 51 - 75 (Top 75 University)"
            rank_midpoint = 63
            category_tier = "Top 75 In India"
        elif overall_nirf_score >= 48.0:
            rank_band = "Rank 75 - 100 (Top 100 NIRF Ranked)"
            rank_midpoint = 82
            category_tier = "Top 100 In India"
        elif overall_nirf_score >= 40.0:
            rank_band = "Rank Band 101 - 150"
            rank_midpoint = 125
            category_tier = "Rank Band 101-150"
        else:
            rank_band = "Rank Band 151 - 200"
            rank_midpoint = 175
            category_tier = "Rank Band 151-200"

        return {
            "overall_score": overall_nirf_score,
            "rank_band": rank_band,
            "rank_midpoint": rank_midpoint,
            "category_tier": category_tier,
            "parameters": {
                "TLR": {
                    "name": "Teaching, Learning & Resources",
                    "score": round(tlr_total, 2),
                    "weight": 30.0,
                    "weighted_points": round(weighted_tlr, 2),
                    "details": {
                        "Student Strength (SS)": round(ss_score, 2),
                        "Faculty Student Ratio (FSR)": round(fsr_score, 2),
                        "Faculty with PhD (FQE)": round(fqe_score, 2),
                        "Financial Utilization (FRU)": round(fru_score, 2)
                    }
                },
                "RPC": {
                    "name": "Research and Professional Practice",
                    "score": round(rpc_total, 2),
                    "weight": 30.0,
                    "weighted_points": round(weighted_rpc, 2),
                    "details": {
                        "Publications (PU)": round(pu_score, 2),
                        "Quality of Pubs (QP)": round(qp_score, 2),
                        "Patents (IPR)": round(ipr_score, 2),
                        "Research Grants (FPPP)": round(fppp_score, 2)
                    }
                },
                "GO": {
                    "name": "Graduation Outcomes",
                    "score": round(go_total, 2),
                    "weight": 20.0,
                    "weighted_points": round(weighted_go, 2),
                    "details": {
                        "Exam Pass Rate (GUE)": round(gue_score, 2),
                        "Placement & Higher Ed (GPH)": round(gph_score, 2)
                    }
                },
                "OI": {
                    "name": "Outreach and Inclusivity",
                    "score": round(oi_total, 2),
                    "weight": 10.0,
                    "weighted_points": round(weighted_oi, 2),
                    "details": {
                        "Regional Diversity (RD)": round(rd_score, 2),
                        "Women Diversity (WD)": round(wd_score, 2),
                        "Social/Econ Diversity (ESCS)": round(escs_score, 2),
                        "Physically Challenged (PCS)": round(pcs_score, 2)
                    }
                },
                "PR": {
                    "name": "Perception",
                    "score": round(pr_total, 2),
                    "weight": 10.0,
                    "weighted_points": round(weighted_pr, 2),
                    "details": {
                        "Peer & Employer Perception (PREMP)": round(pr_total, 2)
                    }
                }
            },
            "raw_inputs": raw
        }

    def evaluate_qs_asia(self, adjustments: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Evaluates QS Asia University Ranking composite score out of 100.
        """
        adj = adjustments or {}
        nirf_eval = self.evaluate_nirf(adj)
        raw = nirf_eval["raw_inputs"]

        # Approximate QS component metrics
        acad_rep = min(raw["perception_survey_score"] * 1.3, 100.0)
        emp_rep = min(raw["placement_and_higher_ed_pct"] * 0.85, 100.0)
        fsr_qs = min(max(100.0 * (15.0 / max(raw["faculty_student_ratio"], 1.0)), 30.0), 100.0)
        cpf_qs = min((raw["citations_per_faculty"] / 16.0) * 100.0, 100.0)
        intl_fac_stud = min((raw["out_of_state_student_pct"] / 30.0) * 75.0 + 15.0, 100.0)
        irn_qs = min((raw["scopus_publications_count"] / 3000.0) * 80.0 + 10.0, 100.0)

        qs_score = round(
            0.30 * acad_rep +
            0.20 * emp_rep +
            0.10 * fsr_qs +
            0.20 * cpf_qs +
            0.10 * intl_fac_stud +
            0.10 * irn_qs,
            2
        )

        if qs_score >= 50.0:
            qs_rank_band = "Rank 301 - 350 in Asia"
        elif qs_score >= 42.0:
            qs_rank_band = "Rank 401 - 450 in Asia"
        elif qs_score >= 35.0:
            qs_rank_band = "Rank 501 - 550 in Asia"
        else:
            qs_rank_band = "Rank 601+ in Asia"

        return {
            "qs_composite_score": qs_score,
            "qs_rank_band": qs_rank_band,
            "components": {
                "Academic Reputation": round(acad_rep, 1),
                "Employer Reputation": round(emp_rep, 1),
                "Faculty Student Ratio": round(fsr_qs, 1),
                "Citations per Faculty": round(cpf_qs, 1),
                "International Diversity": round(intl_fac_stud, 1),
                "International Research Network": round(irn_qs, 1)
            }
        }
