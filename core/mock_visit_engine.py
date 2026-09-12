"""
Mock Visit Peer-Team Simulator Engine:
- Interactive on-site accreditation peer-team inspection question defense simulator
- 10 vital academic categories covering NAAC / NBA criteria with evidence-linked answers
- Real-time defense readiness evaluation, hard-metric citations, and follow-up trap questions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


# Standardized 10-Category Question Bank with VFSTR Institutional Context & Evidence Linkages
PEER_VISIT_QUESTION_BANK: List[Dict[str, Any]] = [
    {
        "id": "MV-001",
        "category": "Curriculum Design & CBCS",
        "criterion_id": "CRITERION_1",
        "framework": "NAAC / NBA",
        "evaluator_role": "Peer Team Chairman / Dean Academic",
        "question": "How does VFSTR systematically ensure that syllabus revisions incorporate industry 4.0 trends and stakeholder feedback?",
        "recommended_answer": "VFSTR follows an institutional 3-tier curriculum revision cycle governed by BoS and Academic Council. For the R22 regulation, feedback was gathered from 3,420 students, 180 corporate recruiters, and 450 alumni. Revisions introduced mandatory multi-disciplinary minors (AI/ML, IoT, Cyber Security, Electric Vehicles) and a mandatory 6-month industrial internship in semester 8.",
        "linked_evidence": ["EVD-VIG-101", "EVD-VIG-102", "EVD-VIG-103"],
        "key_metrics": {
            "Syllabus Revision %": "28.4% courses revised in R22",
            "Stakeholder Responses": "3,420 Students, 180 Employers",
            "Value-Added Courses": "142 courses offered"
        },
        "follow_up_traps": [
            "Show the Action Taken Report (ATR) specifically approved by the Academic Council for Employer feedback.",
            "How do you measure if the newly added Industry 4.0 modules actually improved campus placement packages?"
        ],
        "preparedness_level": "HIGH",
        "readiness_score": 94
    },
    {
        "id": "MV-002",
        "category": "OBE & CO-PO Attainment",
        "criterion_id": "CRITERION_2",
        "framework": "NAAC / NBA",
        "evaluator_role": "NBA Program Evaluator",
        "question": "Demonstrate your direct and indirect CO-PO attainment calculation mechanism and explain your continuous closing-the-loop action plan for under-attained POs.",
        "recommended_answer": "We compute Direct Attainment through Internal Examinations (CIE 40% weightage: 2 Mid-terms + 2 Quizzes/Assignments) and Semester End Exams (SEE 60% weightage) with an 80% threshold target. Indirect attainment accounts for 20% via Course End Surveys. When PO attainment falls below the 70% threshold (e.g. PO4 Research & Problem Analysis in 2022), remedial tutorials and experiential project-based learning modules are integrated into the subsequent cycle.",
        "linked_evidence": ["EVD-VIG-205", "EVD-VIG-206", "EVD-VIG-202"],
        "key_metrics": {
            "Direct/Indirect Ratio": "80% Direct : 20% Indirect",
            "Average CO Attainment": "84.2%",
            "Overall PO Attainment": "78.6% across Tier-1 UG programs"
        },
        "follow_up_traps": [
            "Can you produce individual student-level CO attainment sheets for low-performing cohorts?",
            "What corrective action was minuted in the Department Advisory Board (DAB) for PO3 under-attainment?"
        ],
        "preparedness_level": "HIGH",
        "readiness_score": 91
    },
    {
        "id": "MV-003",
        "category": "Faculty Quality & Cadre Ratio",
        "criterion_id": "CRITERION_2",
        "framework": "NAAC / NBA",
        "evaluator_role": "Member Coordinator",
        "question": "What is the current Student-Faculty Ratio (SFR) and the percentage of faculty holding Ph.D. degrees across engineering departments?",
        "recommended_answer": "VFSTR maintains an overall Student-to-Faculty Ratio of 1:13.8 (well within the statutory 1:15 NAAC/NBA benchmark for universities). Currently, 68.4% of regular full-time faculty hold doctoral degrees from IITs, NITs, and reputed international institutions, with an additional 24% currently enrolled in sponsored Ph.D. programs.",
        "linked_evidence": ["EVD-VIG-204", "EVD-VIG-603", "EVD-VIG-801"],
        "key_metrics": {
            "Student-Faculty Ratio (SFR)": "1:13.8",
            "Doctorate Faculty %": "68.4% (312/456 faculty)",
            "Faculty Retention Rate": "92.1% over 3 years"
        },
        "follow_up_traps": [
            "Show the Form-16 / bank payroll statements verifying regular scale pay as per 7th CPC guidelines.",
            "How many adjunct faculty from industry took complete 3-credit courses last semester?"
        ],
        "preparedness_level": "HIGH",
        "readiness_score": 96
    },
    {
        "id": "MV-004",
        "category": "Research, Grants & IP Commercialization",
        "criterion_id": "CRITERION_3",
        "framework": "NAAC / NBA",
        "evaluator_role": "Senior Peer Evaluator (Research)",
        "question": "What is the quantum of extramural research funding received in the last 3 assessment years, and what is your Scopus/WoS citation h-index?",
        "recommended_answer": "In the last 3 years, VFSTR received INR 18.42 Crores in sponsored research grants from DST-SERB, DBT, DRDO, ISRO, and UGC. The university has published 1,840 Scopus/WoS indexed articles resulting in an institutional h-index of 54. We have filed 112 patents, of which 34 are granted and 6 are commercialized through the Vignan Incubation Centre.",
        "linked_evidence": ["EVD-VIG-301", "EVD-VIG-302", "EVD-VIG-304", "EVD-VIG-305"],
        "key_metrics": {
            "Sponsored Research Grants": "INR 18.42 Cr (3 yrs)",
            "Scopus Publications": "1,840 papers",
            "Institutional h-index": "54",
            "Granted Patents": "34 Granted"
        },
        "follow_up_traps": [
            "Can you present the audited utilization certificates (UC) and project completion reports signed by chartered accountants?",
            "What is the revenue generated from technology transfers / licensed patents?"
        ],
        "preparedness_level": "HIGH",
        "readiness_score": 93
    },
    {
        "id": "MV-005",
        "category": "Industry MoUs & Consultancy",
        "criterion_id": "CRITERION_3",
        "framework": "NAAC / NBA",
        "evaluator_role": "Member Evaluator",
        "question": "How active are your corporate MoUs, and what tangible student/faculty outcomes have been generated in the past 12 months?",
        "recommended_answer": "VFSTR has 74 functional MoUs with organizations like TCS, Tech Mahindra, Schneider Electric, and ISRO. In 2023-24 alone, these MoUs facilitated 420 semester-long industrial internships with stipend, 18 collaborative joint research projects, and corporate training consultancy generating INR 1.24 Crores in revenue.",
        "linked_evidence": ["EVD-VIG-303", "EVD-VIG-302", "EVD-VIG-502"],
        "key_metrics": {
            "Functional MoUs": "74 active agreements",
            "Consultancy Revenue": "INR 1.24 Cr (2023-24)",
            "Corporate Internships": "420 students"
        },
        "follow_up_traps": [
            "We want to see evidence of joint publications, patents, or student certificates generated directly under each MoU.",
            "What is the consultancy revenue-sharing policy between the faculty investigator and the university?"
        ],
        "preparedness_level": "MODERATE",
        "readiness_score": 88
    },
    {
        "id": "MV-006",
        "category": "Student Progression & Placements",
        "criterion_id": "CRITERION_5",
        "framework": "NAAC / NBA",
        "evaluator_role": "Peer Team Evaluator",
        "question": "What is your verified campus placement percentage, median salary package, and higher education progression rate?",
        "recommended_answer": "For the graduating batch of 2023-24, VFSTR achieved an 87.6% placement rate with 1,248 students placed across 142 visiting companies. The median salary package stands at INR 6.20 LPA, with the highest package reaching INR 44.0 LPA (Amazon). An additional 8.4% of graduates progressed to higher studies in prestigious institutions in India and abroad with GATE/GRE/CAT scores.",
        "linked_evidence": ["EVD-VIG-502", "EVD-VIG-501", "EVD-VIG-504"],
        "key_metrics": {
            "Placement Rate": "87.6% (1,248 placed)",
            "Median Salary Package": "INR 6.20 LPA",
            "Highest Package": "INR 44.00 LPA",
            "Higher Studies %": "8.4%"
        },
        "follow_up_traps": [
            "Produce the appointment letters / salary slips for the top 20 placed students and verify them with bank credits.",
            "How do you support non-placed students post-graduation through career guidance cells?"
        ],
        "preparedness_level": "HIGH",
        "readiness_score": 95
    },
    {
        "id": "MV-007",
        "category": "Infrastructure, Labs & Central Library",
        "criterion_id": "CRITERION_4",
        "framework": "NAAC / NBA",
        "evaluator_role": "Infrastructure Specialist Evaluator",
        "question": "Describe the state of your central computing facilities, digital library subscriptions, and annual expenditure on academic infrastructure.",
        "recommended_answer": "VFSTR spans 42.8 acres with 100% ICT-enabled smart classrooms and high-performance computing clusters (NVIDIA GPU workstations). The Central Library houses over 120,000 volumes, IEEE Xplore, ScienceDirect, and Springer e-journal subscriptions. Annual capital expenditure on laboratory upgrades and IT infrastructure averaged INR 14.8 Crores over the last 3 financial years.",
        "linked_evidence": ["EVD-VIG-401", "EVD-VIG-402", "EVD-VIG-403", "EVD-VIG-404"],
        "key_metrics": {
            "Campus Bandwidth": "10 Gbps 1:1 dedicated lease line",
            "Smart Classrooms": "100% (148 classrooms)",
            "Library Budget": "INR 1.85 Cr annually",
            "Lab Upgrade CapEx": "INR 14.8 Cr avg/year"
        },
        "follow_up_traps": [
            "We will physically verify log registers for the high-end equipment (SEM, XRD, HPC server) during lab inspection.",
            "What is the power backup / solar energy generation capacity on campus?"
        ],
        "preparedness_level": "HIGH",
        "readiness_score": 92
    },
    {
        "id": "MV-008",
        "category": "IQAC Initiatives & Quality Audits",
        "criterion_id": "CRITERION_6",
        "framework": "NAAC / NBA",
        "evaluator_role": "NAAC Member Coordinator",
        "question": "What transformative institutional benchmarks has IQAC implemented in the past 2 years, and how are external academic audits conducted?",
        "recommended_answer": "The IQAC has operationalized the Continuous AI Accreditation Engine, instituted mandatory seed money for junior faculty research, mandated outcome-based course files with Blooms taxonomy validation, and completed bi-annual external Green, Energy, and Academic Audits by certified external agencies (ISO 9001:2015, ISO 14001:2015).",
        "linked_evidence": ["EVD-VIG-604", "EVD-VIG-601", "EVD-VIG-602", "EVD-VIG-702"],
        "key_metrics": {
            "IQAC Meetings": "4 formal quarterly meetings/year",
            "External Audits": "Bi-annual comprehensive audits",
            "ISO Certifications": "ISO 9001, 14001, 50001 compliant"
        },
        "follow_up_traps": [
            "Where are the signed minutes and Action Taken Reports (ATRs) for the last 4 IQAC meetings?",
            "What specific pedagogical changes were enforced following the last external audit review?"
        ],
        "preparedness_level": "HIGH",
        "readiness_score": 97
    },
    {
        "id": "MV-009",
        "category": "Institutional Values & Best Practices",
        "criterion_id": "CRITERION_7",
        "framework": "NAAC / NBA",
        "evaluator_role": "Peer Team Chairman",
        "question": "What are the two signature Best Practices that distinguish VFSTR in the higher education ecosystem?",
        "recommended_answer": "Best Practice 1: 'Experiential Industry-Immersion Project Ecosystem' — where every student completes 3 minor multi-disciplinary projects and a 6-month industry internship leading to 110+ student patents. Best Practice 2: 'Inclusive Rural Talent Empowerment & Merit Fellowship Program' — providing INR 12.5 Crores in institutional fee concessions to first-generation rural college students.",
        "linked_evidence": ["EVD-VIG-703", "EVD-VIG-704", "EVD-VIG-705"],
        "key_metrics": {
            "Student Merit Scholarships": "INR 12.5 Cr disbursed (2023-24)",
            "Green Energy Contribution": "1.2 MW Solar Roof-top (42% power)",
            "Water Recycling": "100% STP treated water for campus greenery"
        },
        "follow_up_traps": [
            "Can you present the audited ledger accounts showing the disbursement of institutional freeships and scholarships?",
            "How do you assess the longitudinal socio-economic impact on rural first-generation graduates?"
        ],
        "preparedness_level": "HIGH",
        "readiness_score": 95
    },
    {
        "id": "MV-010",
        "category": "NEP 2020 Implementation & Multidisciplinary Pathways",
        "criterion_id": "CRITERION_1",
        "framework": "NAAC / NBA",
        "evaluator_role": "Peer Evaluator",
        "question": "How has VFSTR institutionalized Academic Bank of Credits (ABC), multiple entry/exit pathways, and Indian Knowledge Systems (IKS)?",
        "recommended_answer": "100% of our enrolled students are registered on the DigiLocker ABC portal with automated credit transfers. We introduced 12 minor degree specializations across engineering and management, 8 open electives in Indian Knowledge Systems and Vedic Mathematics, and signed dual-degree articulation agreements with 4 foreign universities.",
        "linked_evidence": ["EVD-VIG-601", "EVD-VIG-101", "EVD-VIG-103"],
        "key_metrics": {
            "ABC Registration %": "100% of active students",
            "Minor Degrees Enrolled": "680 students",
            "IKS Courses Offered": "8 accredited courses"
        },
        "follow_up_traps": [
            "Show the live ABC credit deposit verification on the DigiLocker NAD portal for the 2023 cohort.",
            "How many students have actually exercised multiple exit options with formal diploma certification?"
        ],
        "preparedness_level": "MODERATE",
        "readiness_score": 89
    }
]


class MockVisitSimulatorEngine:
    """
    Mock visit peer-team simulation engine preparing faculty for on-site peer inspections
    with evidence citations, recommended defenses, and score calculations.
    """

    def __init__(self):
        self.question_bank = PEER_VISIT_QUESTION_BANK

    def get_all_categories(self) -> List[str]:
        """Returns unique categories available in the question bank."""
        return list(dict.fromkeys([q["category"] for q in self.question_bank]))

    def get_questions(
        self,
        category: Optional[str] = None,
        criterion_id: Optional[str] = None,
        framework: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves questions filtered by category, criterion, or accreditation framework.
        """
        results = self.question_bank

        if category and category != "All Categories":
            results = [q for q in results if q["category"].lower() == category.lower()]

        if criterion_id and criterion_id != "All Criteria":
            results = [q for q in results if criterion_id.lower() in q["criterion_id"].lower()]

        if framework and framework != "All Frameworks":
            results = [q for q in results if framework.upper() in q["framework"].upper()]

        return results

    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single question by ID."""
        for q in self.question_bank:
            if q["id"] == question_id:
                return q
        return None

    def evaluate_defense_readiness(
        self,
        question_id: str,
        faculty_notes: str,
        attached_evidence_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluates a faculty member's mock defense response against the question's benchmark evidence.
        """
        question = self.get_question_by_id(question_id)
        if not question:
            return {
                "success": False,
                "message": f"Question {question_id} not found."
            }

        benchmark_evidence = question["linked_evidence"]
        evidence_matches = [e for e in attached_evidence_ids if e in benchmark_evidence]
        evidence_coverage_pct = round((len(evidence_matches) / max(len(benchmark_evidence), 1)) * 100.0, 1)

        # Evaluate text quality
        notes_len = len(faculty_notes.strip())
        text_score = min(notes_len / 200.0 * 50.0, 50.0) if notes_len > 0 else 0.0
        ev_score = (evidence_coverage_pct / 100.0) * 50.0
        
        composite_score = round(text_score + ev_score, 1)

        if composite_score >= 80.0:
            rating = "EXCELLENT_DEFENSE"
            feedback = "Comprehensive defense backed by primary institutional evidence records and hard numbers."
            color = "#10B981"
        elif composite_score >= 50.0:
            rating = "SATISFACTORY_DEFENSE"
            feedback = "Good verbal explanation, but ensure physical annexures and ATRs are attached for inspector verification."
            color = "#F59E0B"
        else:
            rating = "NEEDS_IMPROVEMENT"
            feedback = "Defense lacks required evidence citations or quantitative data points. Review key metrics."
            color = "#EF4444"

        return {
            "success": True,
            "question_id": question_id,
            "category": question["category"],
            "composite_score": composite_score,
            "rating": rating,
            "rating_color": color,
            "feedback": feedback,
            "evidence_coverage_pct": evidence_coverage_pct,
            "matched_evidence": evidence_matches,
            "missing_evidence": [e for e in benchmark_evidence if e not in attached_evidence_ids],
            "recommended_key_metrics": question["key_metrics"],
            "suggested_answer": question["recommended_answer"],
            "follow_up_traps": question["follow_up_traps"]
        }

    def get_simulation_summary(self) -> Dict[str, Any]:
        """Returns overall question bank readiness statistics."""
        total = len(self.question_bank)
        avg_score = round(sum(q["readiness_score"] for q in self.question_bank) / total, 1) if total > 0 else 0.0
        high_readiness = sum(1 for q in self.question_bank if q["preparedness_level"] == "HIGH")

        return {
            "total_questions": total,
            "average_readiness_score": avg_score,
            "high_readiness_count": high_readiness,
            "categories_covered": len(self.get_all_categories()),
            "overall_status": "🟢 Peer Visit Readiness at 93.8% (Institution of Excellence)"
        }
