"""
Seed Database Script for VFSTR Vignan Accreditation AI Agent.
Populates synthetic demonstration data including:
- Multi-framework regulatory registry: NAAC (7 criteria), NBA (10 criteria), NIRF (5 parameters)
- Complete metrics, benchmarks, and evidence requirements
- All 45 realistic institutional evidence records as the single source of truth in SQLite/Postgres
- Intentional compliance gaps, remediation tasks, SAR drafts, human verifications, and readiness snapshots.

IMPORTANT: Uses synthetic demonstration data only — no private/confidential institution data.
"""

import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from core.database import init_db, get_db_session
from core.models import (
    AccreditationFramework, Criterion, Subcriterion, Evidence,
    EvidenceRequirement, EvidenceRequirementMap, ReadinessSnapshot,
    CriterionReadiness, Gap, Task, SARDraft, SARSource,
    HumanVerification, User, AuditLog
)
from core.repository import (
    create_framework, create_criterion, create_subcriterion,
    create_evidence_requirement, create_evidence, map_evidence_to_requirement,
    create_gap, create_task, create_sar_draft, add_sar_source,
    create_verification, create_readiness_snapshot, create_criterion_readiness
)
from core.criteria_registry import NAAC_CRITERIA, NBA_CRITERIA
from core.vignan_demo_data import VIGNAN_EVIDENCE_STORE


# NIRF Parameters & Submetrics
NIRF_CRITERIA_CONFIG = {
    "NIRF-TLR": {
        "name": "Teaching, Learning & Resources (TLR)",
        "weight": 100.0,
        "required_score": 75.0,
        "description": "Student strength, faculty-student ratio, faculty with PhD and experience, financial resources and utilization.",
        "metrics": {
            "TLR-SS": {
                "name": "Student Strength including Doctoral Students (SS)",
                "weight": 20.0,
                "description": "Total sanctioned student intake and enrolled students across undergraduate, postgraduate, and Ph.D. programs.",
                "required_evidence": ["Sanctioned intake letters", "Enrollment registers", "Doctoral student list"]
            },
            "TLR-FSR": {
                "name": "Faculty-Student Ratio with Emphasis on Permanent Faculty (FSR)",
                "weight": 30.0,
                "description": "Ratio of permanent regular full-time faculty to enrolled students (target 1:15).",
                "required_evidence": ["Faculty appointment orders", "Service registers", "AICTE/UGC sanctioned post approvals"]
            },
            "TLR-FQE": {
                "name": "Combined Metric for Faculty with Ph.D. and Experience (FQE)",
                "weight": 20.0,
                "description": "Percentage of faculty holding Ph.D. degrees and average teaching/research experience.",
                "required_evidence": ["Doctoral degree certificates", "Experience certificates", "Faculty profile master register"]
            },
            "TLR-FRU": {
                "name": "Financial Resources and Their Utilization (FRU)",
                "weight": 30.0,
                "description": "Capital expenditure on academic labs/library and operational expenditure on maintenance and salaries.",
                "required_evidence": ["Statutory audited balance sheets", "Finance committee approval minutes", "Utilization certificates"]
            }
        }
    },
    "NIRF-RPC": {
        "name": "Research and Professional Practice (RPC)",
        "weight": 100.0,
        "required_score": 70.0,
        "description": "Scopus/WoS publications, citation counts, IPR & patents granted, extramural sponsored research and consultancy.",
        "metrics": {
            "RPC-PU": {
                "name": "Combined Metric for Publications (PU)",
                "weight": 35.0,
                "description": "Number of research papers published in journals indexed in Scopus, Web of Science, and PubMed.",
                "required_evidence": ["Scopus citation extracts", "Journal publication reprints with DOI", "Dean R&D publications master"]
            },
            "RPC-QP": {
                "name": "Quality of Publications (QP - Citations)",
                "weight": 35.0,
                "description": "Total citations received and top 25% percentile publications over the last 3 assessment years.",
                "required_evidence": ["SciVal citation reports", "Scopus author profile logs", "h-index reports"]
            },
            "RPC-IPR": {
                "name": "IPR and Patents: Published and Granted (IPR)",
                "weight": 15.0,
                "description": "Intellectual property rights filings, Indian Patent Office published/granted patents, and commercialized technologies.",
                "required_evidence": ["Patent grant certificates", "Indian Patent Journal gazette notifications", "Commercialization agreements"]
            },
            "RPC-FPPP": {
                "name": "Footprint of Projects and Professional Practice (FPPP)",
                "weight": 15.0,
                "description": "Sponsored extramural research funding from DST, SERB, DBT, and revenue from industry consultancy.",
                "required_evidence": ["Research sanction letters", "Fund disbursement orders", "Consultancy invoices and ledgers"]
            }
        }
    },
    "NIRF-GO": {
        "name": "Graduation Outcomes (GO)",
        "weight": 100.0,
        "required_score": 80.0,
        "description": "University examinations pass percentages, campus placement offers, median salary package, and PhD graduates.",
        "metrics": {
            "GO-GUE": {
                "name": "Metric for University Examinations (GUE)",
                "weight": 60.0,
                "description": "Percentage of students graduating in minimum stipulated degree time without backlogs.",
                "required_evidence": ["Controller of Examinations result gazette", "Degree conferment convocation registers"]
            },
            "GO-GPH": {
                "name": "Metric for Number of Ph.D. Students Graduated (GPH)",
                "weight": 20.0,
                "description": "Number of full-time and part-time doctoral degrees awarded in the previous 3 academic years.",
                "required_evidence": ["Ph.D. notification gazettes", "Viva-voce committee evaluation reports"]
            },
            "GO-GMS": {
                "name": "Median Salary of Placed Graduates (GMS)",
                "weight": 20.0,
                "description": "Median annual compensation (LPA) of placed graduates verified through employer offer letters.",
                "required_evidence": ["Campus placement offer letters", "Employer salary breakdown sheets", "Alumni career progression logs"]
            }
        }
    },
    "NIRF-OI": {
        "name": "Outreach and Inclusivity (OI)",
        "weight": 100.0,
        "required_score": 75.0,
        "description": "Regional student diversity, women student and faculty percentages, scholarships for economically backward, and Divyangjan facilities.",
        "metrics": {
            "OI-RD": {
                "name": "Percentage of Students from Other States and Countries (RD)",
                "weight": 30.0,
                "description": "Geographic diversity reflecting pan-India and international student enrollment.",
                "required_evidence": ["State-wise domicile admission lists", "International student visa & enrollment records"]
            },
            "OI-WD": {
                "name": "Percentage of Women Students and Faculty (WD)",
                "weight": 30.0,
                "description": "Gender diversity ratios across student cohorts, faculty designations, and academic leadership roles.",
                "required_evidence": ["Gender enrollment registers", "Women faculty appointment orders"]
            },
            "OI-ESCS": {
                "name": "Economically and Socially Challenged Students (ESCS)",
                "weight": 20.0,
                "description": "Institutional fee waivers, government scholarships, and tuition concessions provided to underprivileged students.",
                "required_evidence": ["V-SAT merit scholarship award letters", "Government scholarship disbursement registers"]
            },
            "OI-PCS": {
                "name": "Facilities for Physically Challenged / Divyangjan Students (PCS)",
                "weight": 20.0,
                "description": "Lifts, wheelchair ramps, accessible restrooms, assistive software, and examination assistance.",
                "required_evidence": ["Campus accessibility audit certificates", "Assistive lab equipment invoices and photos"]
            }
        }
    },
    "NIRF-PR": {
        "name": "Perception (PR)",
        "weight": 100.0,
        "required_score": 65.0,
        "description": "Peer perception rating among academic leaders, corporate recruiters, and research institutions.",
        "metrics": {
            "PR-PREP": {
                "name": "Academic Peer and Employer Perception Survey (PREP)",
                "weight": 100.0,
                "description": "Consolidated perception score evaluated through annual NIRF national stakeholder surveys.",
                "required_evidence": ["NIRF peer feedback scorecards", "Employer survey endorsements", "Academic council citations"]
            }
        }
    }
}


def _compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def seed_demo_data(session: Optional[Session] = None, db_path: Optional[str] = None):
    """Seeds synthetic Vignan accreditation dataset into the database."""
    if session is not None:
        _perform_seed(session)
    else:
        init_db(db_path)
        with get_db_session(db_path) as s:
            _perform_seed(s)


def _perform_seed(session: Session):
    # 1. Users / Roles
    users_data = [
        {"name": "Dr. K. Ramamohan", "email": "iqac_director@vignan.ac.in", "role": "IQAC", "department": "IQAC"},
        {"name": "Dr. N. Veeranjaneyulu", "email": "dean_academics@vignan.ac.in", "role": "ACCREDITATION_COORDINATOR", "department": "Academic Affairs"},
        {"name": "Dr. G. Srinivasa Rao", "email": "dean_rd@vignan.ac.in", "role": "HOD", "department": "Research & Development"},
        {"name": "Dr. D. Vijaya Ramu", "email": "dean_placements@vignan.ac.in", "role": "FACULTY", "department": "Training & Placement Cell"},
        {"name": "Dr. P. M. V. Rao", "email": "registrar@vignan.ac.in", "role": "ADMIN", "department": "Administration"},
        {"name": "Prof. External Auditor", "email": "peer_review@naac.gov.in", "role": "REVIEWER", "department": "NAAC Peer Committee"}
    ]
    for u in users_data:
        existing = session.query(User).filter(User.email == u["email"]).first()
        if not existing:
            session.add(User(**u))
    session.flush()

    # 2. Accreditation Frameworks: NAAC, NBA, NIRF
    naac = create_framework(
        session=session,
        name="National Assessment and Accreditation Council (University Manual)",
        code="NAAC",
        version="2024.2",
        description="Comprehensive quality accreditation for Universities and Autonomous Higher Education Institutions (7 Criteria).",
        is_active=True
    )

    nba = create_framework(
        session=session,
        name="National Board of Accreditation",
        code="NBA",
        version="2024.1",
        description="Outcome-Based Education (OBE) program accreditation for Tier-1 undergraduate engineering programs (10 Criteria).",
        is_active=True
    )

    nirf = create_framework(
        session=session,
        name="National Institutional Ranking Framework (MoE / MHRD)",
        code="NIRF",
        version="2024",
        description="National university and engineering institutional rankings across 5 core parameters.",
        is_active=True
    )

    # 3. Seed Criteria, Subcriteria, and Requirements
    criteria_map: Dict[str, Criterion] = {}
    subcrit_map: Dict[str, Subcriterion] = {}
    req_map: Dict[str, EvidenceRequirement] = {}

    # 3.1 NAAC Framework (Full 7 Criteria)
    for c_code, c_data in NAAC_CRITERIA.items():
        crit = create_criterion(
            session=session,
            framework_id=naac.id,
            code=c_code,
            name=c_data["name"],
            description=c_data.get("description", ""),
            weight=float(c_data.get("weight", 100.0)),
            required_score=75.0
        )
        criteria_map[c_code] = crit
        for m_code, m_data in c_data.get("metrics", {}).items():
            sub = create_subcriterion(
                session=session,
                criterion_id=crit.id,
                code=m_code,
                name=m_data["name"],
                description=m_data.get("description", ""),
                weight=float(m_data.get("weight", 20.0)),
                required_evidence=", ".join(m_data.get("required_evidence", []))
            )
            subcrit_map[m_code] = sub
            for req_title in m_data.get("required_evidence", []):
                r_key = f"{m_code}_{req_title[:30]}"
                req = create_evidence_requirement(
                    session=session,
                    criterion_id=crit.id,
                    subcriterion_id=sub.id,
                    requirement_name=req_title,
                    description=m_data.get("description", ""),
                    allowed_file_types="PDF,DOCX,XLSX,CSV",
                    minimum_completeness=80.0,
                    responsible_department="Academic Department"
                )
                req_map[r_key] = req

    # 3.2 NBA Framework (Full 10 Criteria)
    for c_code, c_data in NBA_CRITERIA.items():
        crit = create_criterion(
            session=session,
            framework_id=nba.id,
            code=c_code,
            name=c_data["name"],
            description=c_data.get("description", ""),
            weight=float(c_data.get("weight", 100.0)),
            required_score=70.0
        )
        criteria_map[c_code] = crit
        for m_code, m_data in c_data.get("metrics", {}).items():
            sub = create_subcriterion(
                session=session,
                criterion_id=crit.id,
                code=m_code,
                name=m_data["name"],
                description=m_data.get("description", ""),
                weight=float(m_data.get("weight", 20.0)),
                required_evidence=", ".join(m_data.get("required_evidence", []))
            )
            subcrit_map[m_code] = sub
            for req_title in m_data.get("required_evidence", []):
                r_key = f"{m_code}_{req_title[:30]}"
                req = create_evidence_requirement(
                    session=session,
                    criterion_id=crit.id,
                    subcriterion_id=sub.id,
                    requirement_name=req_title,
                    description=m_data.get("description", ""),
                    allowed_file_types="PDF,DOCX,XLSX,CSV",
                    minimum_completeness=80.0,
                    responsible_department="Engineering Department"
                )
                req_map[r_key] = req

    # 3.3 NIRF Framework (5 Parameters)
    for c_code, c_data in NIRF_CRITERIA_CONFIG.items():
        crit = create_criterion(
            session=session,
            framework_id=nirf.id,
            code=c_code,
            name=c_data["name"],
            description=c_data.get("description", ""),
            weight=float(c_data.get("weight", 100.0)),
            required_score=c_data.get("required_score", 70.0)
        )
        criteria_map[c_code] = crit
        for m_code, m_data in c_data.get("metrics", {}).items():
            sub = create_subcriterion(
                session=session,
                criterion_id=crit.id,
                code=m_code,
                name=m_data["name"],
                description=m_data.get("description", ""),
                weight=float(m_data.get("weight", 25.0)),
                required_evidence=", ".join(m_data.get("required_evidence", []))
            )
            subcrit_map[m_code] = sub
            for req_title in m_data.get("required_evidence", []):
                r_key = f"{m_code}_{req_title[:30]}"
                req = create_evidence_requirement(
                    session=session,
                    criterion_id=crit.id,
                    subcriterion_id=sub.id,
                    requirement_name=req_title,
                    description=m_data.get("description", ""),
                    allowed_file_types="PDF,DOCX,XLSX,CSV",
                    minimum_completeness=85.0,
                    responsible_department="IQAC / R&D / Placements"
                )
                req_map[r_key] = req

    session.flush()

    # 4. Seed All 45 Evidence Records Directly into SQLite/Postgres (Single Source of Truth)
    evidence_entities = {}
    for ev in VIGNAN_EVIDENCE_STORE:
        ev_id = ev["id"]
        # Find matching criterion in database
        matched_crit_id = None
        matched_subcrit_id = None
        applicable = ev.get("applicable_criteria", [])

        for app_code in applicable:
            if app_code in criteria_map:
                matched_crit_id = criteria_map[app_code].id
                break
            if app_code in subcrit_map:
                sub = subcrit_map[app_code]
                matched_subcrit_id = sub.id
                matched_crit_id = sub.criterion_id
                break

        # Fallback to C1 if not matched
        if not matched_crit_id and "C1" in criteria_map:
            matched_crit_id = criteria_map["C1"].id

        f_hash = _compute_hash(f"{ev_id}_{ev.get('title', '')}_{ev.get('raw_text', '')}")
        file_fmt = str(ev.get("file_format") or "PDF").upper().replace(".", "").strip()
        desc = ev.get("content_summary") or ev.get("summary") or ev.get("description") or ""
        raw = ev.get("raw_text") or ev.get("extracted_text") or desc
        status_val = "VERIFIED" if ev.get("status") == "Verified" else "IN_REVIEW"

        ev_entity, _ = create_evidence(
            session=session,
            filename=f"{ev_id}.{file_fmt.lower()}",
            original_filename=ev.get("title", f"{ev_id}.pdf"),
            file_hash=f_hash,
            file_type=file_fmt,
            file_path=f"data/documents/{ev_id}.{file_fmt.lower()}",
            file_size=int(len(raw) * 128 + 102400),
            criterion_id=matched_crit_id,
            subcriterion_id=matched_subcrit_id,
            source_department=ev.get("department", "VFSTR"),
            description=desc,
            extracted_text=raw,
            completeness_score=float(ev.get("completeness_score", 90.0)),
            freshness_score=95.0,
            applicable_criteria=json.dumps(applicable),
            status=status_val
        )
        # Preserve explicit ID
        ev_entity.id = ev_id
        session.flush()
        evidence_entities[ev_id] = ev_entity

        # Auto-map to first requirement under this criterion if available
        if matched_crit_id:
            first_req = session.query(EvidenceRequirement).filter(
                EvidenceRequirement.criterion_id == matched_crit_id
            ).first()
            if first_req:
                map_evidence_to_requirement(
                    session=session,
                    evidence_id=ev_entity.id,
                    requirement_id=first_req.id,
                    match_score=float(ev.get("completeness_score", 90.0)),
                    matched_by="SEMANTIC_TFIDF"
                )

    session.flush()

    # 5. Seed Intentional Gaps (Hackathon Demo Scenarios)
    c2_crit = criteria_map.get("C2") or criteria_map.get("C1")
    c1_crit = criteria_map.get("C1")
    c3_crit = criteria_map.get("C3")

    sub_2_1 = subcrit_map.get("2.1.1") or subcrit_map.get("1.1.1")
    req_plc = session.query(EvidenceRequirement).filter(
        EvidenceRequirement.criterion_id == c2_crit.id
    ).first()

    gap1 = create_gap(
        session=session,
        criterion_id=c2_crit.id,
        subcriterion_id=sub_2_1.id if sub_2_1 else None,
        requirement_id=req_plc.id if req_plc else None,
        title="European hiring partner offer letters pending formal seal",
        description="68 offer letters from international and European hiring partners lack official HR seal and stamped verification on institutional manifest.",
        severity="HIGH",
        impact=9.0,
        effort=4.0,
        recommended_action="Coordinate with Placement Cell to collect stamped employer verification letters or verified digital offer emails."
    )

    gap2 = create_gap(
        session=session,
        criterion_id=c1_crit.id if c1_crit else c2_crit.id,
        requirement_id=None,
        title="Faculty doctoral equivalence pending for 14 recent joinees",
        description="14 newly appointed faculty members in Biotechnology and Mechanical departments have provisional certificates pending doctoral equivalence verification.",
        severity="MEDIUM",
        impact=7.0,
        effort=3.0,
        recommended_action="Request Dean Academics to obtain verified UGC degree copies from respective awarding universities."
    )

    gap3 = create_gap(
        session=session,
        criterion_id=c3_crit.id if c3_crit else c2_crit.id,
        requirement_id=None,
        title="Statutory auditor signature pending on seed money UCs",
        description="3 Utilization Certificates for Biotechnology internal research seed grants (INR 14.5 Lakhs) require statutory chartered accountant endorsement.",
        severity="MEDIUM",
        impact=6.5,
        effort=2.0,
        recommended_action="Submit seed money expense ledgers to Finance Office for statutory auditor endorsement."
    )

    # 6. Actionable Tasks (Assigned to Institutional Roles)
    create_task(
        session=session,
        criterion_id=c2_crit.id,
        gap_id=gap1.id,
        title="Collect stamped employer validation for European hiring partners",
        description="Dispatch formal email request to overseas employers for verified appointment manifests.",
        owner_role="Placement Cell",
        owner_department="Training & Placement Cell (T&P)",
        priority="HIGH",
        deadline=datetime.now() + timedelta(days=14)
    )

    create_task(
        session=session,
        criterion_id=c1_crit.id if c1_crit else c2_crit.id,
        gap_id=gap2.id,
        title="Reconcile doctoral degree verification for 14 new faculty joinees",
        description="Coordinate with registrar office to authenticate Ph.D. degree credentials.",
        owner_role="Academic Department",
        owner_department="Office of Dean Academics",
        priority="MEDIUM",
        deadline=datetime.now() + timedelta(days=10)
    )

    create_task(
        session=session,
        criterion_id=c3_crit.id if c3_crit else c2_crit.id,
        gap_id=gap3.id,
        title="Obtain statutory auditor endorsement on Biotechnology seed grant UCs",
        description="Finalize utilization certificates with university chartered accountant.",
        owner_role="Research Cell",
        owner_department="Office of Dean R&D",
        priority="MEDIUM",
        deadline=datetime.now() + timedelta(days=7)
    )

    # 7. SAR Qualitative Drafts with Evidence Traceability
    ev_101 = evidence_entities.get("EVD-VIG-101")
    ev_201 = evidence_entities.get("EVD-VIG-201")

    sar1 = create_sar_draft(
        session=session,
        framework_id=naac.id,
        criterion_id=c1_crit.id if c1_crit else None,
        title="SAR Qualitative Narrative: Criterion 1.1 — Curricular Design & OBE",
        draft_text=(
            "Vignan's Foundation for Science, Technology and Research (VFSTR) exercises participative governance "
            "through active statutory bodies including the Board of Management, Academic Council, and Board of Studies. "
            "All policy decisions adhere to UGC Regulations and Outcome-Based Education (OBE) principles with regular peer reviews."
        ),
        version="1.0",
        generated_by="AI DRAFT — HUMAN VERIFICATION REQUIRED"
    )
    if ev_101:
        add_sar_source(session, sar1.id, ev_101.id, source_reference="BoS Minutes R22 Section 3.2", relevance_score=0.98)

    sar2 = create_sar_draft(
        session=session,
        framework_id=naac.id,
        criterion_id=c2_crit.id if c2_crit else None,
        title="SAR Qualitative Narrative: Criterion 2.1 — Student Admissions & Teaching Diversity",
        draft_text=(
            "VFSTR maintains an equitable, merit-based admission policy via V-SAT and state quota allotments. "
            "Enrolled students benefit from experiential, participative learning methods and student-centric pedagogy."
        ),
        version="1.0",
        generated_by="AI DRAFT — HUMAN VERIFICATION REQUIRED"
    )
    if ev_201:
        add_sar_source(session, sar2.id, ev_201.id, source_reference="Admissions Register 2023-24 Summary Table 1", relevance_score=0.94)

    # 8. Human Verifications (Guardrail Demonstration)
    if ev_101:
        create_verification(
            session=session,
            reviewer_name="Dr. K. Ramamohan",
            reviewer_role="Director IQAC",
            decision="APPROVED",
            evidence_id=ev_101.id,
            comments="Verified against approved Academic Council minutes with Dean seal."
        )

    ev_102 = evidence_entities.get("EVD-VIG-102")
    if ev_102:
        create_verification(
            session=session,
            reviewer_name="Dr. N. Veeranjaneyulu",
            reviewer_role="Dean Academics",
            decision="APPROVED",
            evidence_id=ev_102.id,
            comments="Stakeholder feedback verified across all 5 categories with Academic Council ATR."
        )

    # 9. Historical Readiness Snapshots (Showing progression over time)
    for months_ago, score, status, r_crit in [
        (3, 74.5, "PARTIAL", 3),
        (2, 79.2, "PARTIAL", 4),
        (1, 84.8, "READY", 5),
        (0, 88.6, "READY", 6)
    ]:
        snap = create_readiness_snapshot(
            session=session,
            framework_id=naac.id,
            overall_score=score,
            status=status,
            total_criteria=7,
            ready_criteria=r_crit,
            partial_criteria=7 - r_crit,
            gap_criteria=1 if score < 85 else 0,
            calculated_by="Continuous Readiness Scanner"
        )
        if months_ago > 0:
            snap.calculated_at = datetime.now() - timedelta(days=months_ago * 30)

        # Detail breakdown for current month
        if months_ago == 0:
            for c_code, crit_obj in criteria_map.items():
                if crit_obj.framework_id == naac.id:
                    create_criterion_readiness(
                        session=session,
                        snapshot_id=snap.id,
                        criterion_id=crit_obj.id,
                        evidence_score=score + 2.0 if score < 95 else 95.0,
                        completeness_score=score,
                        freshness_score=92.0,
                        verification_score=85.0
                    )

    session.commit()
    print(f"[SEED] Successfully seeded complete VFSTR accreditation database: NAAC (7 criteria), NBA (10 criteria), NIRF (5 parameters), and 45 single-source-of-truth evidence records.")


if __name__ == "__main__":
    seed_demo_data()
