"""
Vignan University AI Accreditation Academic Agent (VFSTR)
Streamlit Application for Continuous Accreditation Readiness Assessment (NAAC & NBA)
"""

import json
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

from core.criteria_registry import get_framework_criteria, get_all_metrics_flat
from core.vignan_demo_data import get_demo_evidence_list, VIGNAN_DEPARTMENTS, VIGNAN_ACADEMIC_YEARS
from core.evidence_engine import EvidenceEngine
from core.scoring_engine import ScoringEngine
from core.gap_matrix_engine import GapMatrixEngine
from core.task_manager import TaskManager
from core.narrative_generator import NarrativeGenerator
from core.audit_verifier import AuditVerifier
from core.pdf_exporter import generate_accreditation_dossier_pdf

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Vignan AI Accreditation Agent | VFSTR",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Vignan University Branding and Modern Glassmorphism UI
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Vignan University Palette Variables */
    :root {
        --vignan-maroon: #800000;
        --vignan-crimson: #8B1E28;
        --vignan-gold: #D4AF37;
        --vignan-gold-light: #FDF6B2;
        --accent-blue: #3B82F6;
        --accent-green: #10B981;
        --accent-amber: #F59E0B;
        --accent-red: #EF4444;
        --card-bg: rgba(30, 41, 59, 0.7);
        --card-border: rgba(255, 255, 255, 0.08);
    }

    /* Header Banner */
    .vignan-header {
        background: linear-gradient(135deg, #670000 0%, #8B1E28 50%, #4A0000 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(128, 0, 0, 0.4);
        border: 1px solid rgba(212, 175, 55, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .vignan-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF;
    }

    .vignan-subtitle {
        font-size: 14px;
        color: #F3E8FF;
        margin-top: 4px;
        opacity: 0.95;
    }

    .vignan-badge {
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
        color: #1A1A1A;
        font-size: 12px;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: inline-block;
    }

    /* Glassmorphism KPI Cards */
    .kpi-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.3);
        border-color: rgba(212, 175, 55, 0.4);
    }

    .kpi-label {
        font-size: 13px;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 800;
        color: #F8FAFC;
        margin: 6px 0 2px 0;
    }

    .kpi-subtext {
        font-size: 12px;
        color: #64748B;
    }

    /* Status Badges */
    .badge-success {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }

    .badge-warning {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }

    .badge-danger {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }

    .badge-info {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Section Cards */
    .section-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0B1120;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
def init_session_state():
    if "evidence_list" not in st.session_state:
        st.session_state.evidence_list = get_demo_evidence_list()
    if "ev_engine" not in st.session_state:
        st.session_state.ev_engine = EvidenceEngine()
    if "scoring_engine" not in st.session_state:
        st.session_state.scoring_engine = ScoringEngine()
    if "gap_engine" not in st.session_state:
        st.session_state.gap_engine = GapMatrixEngine()
    if "task_manager" not in st.session_state:
        st.session_state.task_manager = TaskManager()
    if "narrative_gen" not in st.session_state:
        st.session_state.narrative_gen = NarrativeGenerator()
    if "audit_verifier" not in st.session_state:
        st.session_state.audit_verifier = AuditVerifier()
    if "simulated_adjustments" not in st.session_state:
        st.session_state.simulated_adjustments = {}

init_session_state()

# Header Component
st.markdown("""
<div class="vignan-header">
    <div>
        <div class="vignan-title">🏛️ VFSTR AI ACCREDITATION ACADEMIC AGENT</div>
        <div class="vignan-subtitle">Vignan's Foundation for Science, Technology & Research (Deemed to be University) | Vadlamudi, Guntur, AP</div>
    </div>
    <div>
        <span class="vignan-badge">✨ NAAC A+ | NIRF Top 100</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.0.3", caption="VFSTR Campus Intelligence", use_container_width=True)
    st.markdown("### ⚙️ Accreditation Framework")
    framework = st.selectbox(
        "Select Regulatory Framework",
        ["NAAC", "NBA"],
        help="NAAC: University Manual (7 Criteria) | NBA: Tier-1 Outcome Based Education (10 Criteria)"
    )

    st.markdown("---")
    st.markdown("### 🏢 Department & Year Filters")
    selected_dept = st.selectbox("Department Filter", ["All Departments"] + VIGNAN_DEPARTMENTS)
    selected_year = st.selectbox("Assessment Academic Year", ["All Years"] + VIGNAN_ACADEMIC_YEARS)

    st.markdown("---")
    st.markdown("### 👤 Human Reviewer Session")
    reviewer_profile = st.selectbox(
        "Current Reviewer",
        [
            "Dr. K. Ramamohan (Director IQAC)",
            "Dr. N. Veeranjaneyulu (Dean Academics)",
            "Dr. G. Srinivasa Rao (Dean R&D)",
            "Dr. P. M. V. Rao (Registrar)",
            "Prof. External Peer Auditor (NAAC/NBA Committee)"
        ]
    )

    st.markdown("---")
    if st.button("🔄 Reset to Vignan Demo Dataset", use_container_width=True):
        st.session_state.evidence_list = get_demo_evidence_list()
        st.session_state.task_manager = TaskManager()
        st.session_state.audit_verifier = AuditVerifier()
        st.session_state.simulated_adjustments = {}
        st.success("Repository reset to default authentic Vignan records!")
        st.rerun()

# Filter evidence based on sidebar selections
filtered_evidence = st.session_state.evidence_list
if selected_dept != "All Departments":
    filtered_evidence = [e for e in filtered_evidence if e.get("department") == selected_dept]
if selected_year != "All Years":
    filtered_evidence = [e for e in filtered_evidence if e.get("academic_year") == selected_year]

# Run Core Calculations
eval_result = st.session_state.scoring_engine.evaluate_framework(
    evidence_list=st.session_state.evidence_list,
    framework=framework,
    simulated_adjustments=st.session_state.simulated_adjustments
)
outcome = eval_result["outcome"]
detected_gaps = st.session_state.ev_engine.detect_missing_evidence(st.session_state.evidence_list, framework=framework)
gap_matrix = st.session_state.gap_engine.build_prioritized_matrix(detected_gaps)
tasks = st.session_state.task_manager.get_all_tasks()
task_stats = st.session_state.task_manager.get_task_statistics()
audit_summary = st.session_state.audit_verifier.get_audit_summary()

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏛️ Executive Dashboard",
    "📁 Evidence Repository",
    "🎯 Criteria Mapping",
    "⚡ Gap Prioritization Matrix",
    "📋 Remediation Hub",
    "✍️ SAR Narrative Studio",
    "🛡️ IQAC Audit & Exports"
])


# ==========================================
# TAB 1: EXECUTIVE DASHBOARD
# ==========================================
with tab1:
    st.markdown("### 📊 Institutional Accreditation Readiness Overview")

    # KPI Metric Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if framework == "NAAC":
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Simulated CGPA</div>
                <div class="kpi-value" style="color: #34D399;">{outcome['cgpa']} <span style="font-size:16px;color:#94A3B8;">/ 4.00</span></div>
                <div class="kpi-subtext">Grade: <strong>{outcome['grade']}</strong></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">NBA Score</div>
                <div class="kpi-value" style="color: #34D399;">{round(outcome['total_points'])} <span style="font-size:16px;color:#94A3B8;">/ 1000</span></div>
                <div class="kpi-subtext">{outcome['grade']}</div>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Readiness Index</div>
            <div class="kpi-value" style="color: #60A5FA;">{outcome['overall_score_pct']}%</div>
            <div class="kpi-subtext">{outcome['status_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Verified Evidence</div>
            <div class="kpi-value" style="color: #FBBF24;">{len(st.session_state.evidence_list)}</div>
            <div class="kpi-subtext">{sum(1 for e in st.session_state.evidence_list if e.get('status') == 'Verified')} Officially Approved</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Compliance Gaps</div>
            <div class="kpi-value" style="color: #F87171;">{gap_matrix['total_gaps_count']}</div>
            <div class="kpi-subtext">{gap_matrix['critical_severity_count']} Critical Deficiencies</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Task Resolution</div>
            <div class="kpi-value" style="color: #A78BFA;">{task_stats['resolution_rate_pct']}%</div>
            <div class="kpi-subtext">{task_stats['resolved']} of {task_stats['total_tasks']} Resolved</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts: Radar Chart & Weighted Contribution
    col_radar, col_bar = st.columns([1, 1])

    with col_radar:
        st.markdown("#### 🎯 Criterion-Wise Compliance Radar")
        criteria_data = eval_result["criteria_breakdown"]
        radar_categories = [f"{c_id}: {c_data['name'].split(':')[1].strip()[:20]}" if ':' in c_data['name'] else c_id for c_id, c_data in criteria_data.items()]
        radar_scores = [c_data["score_pct"] for c_data in criteria_data.values()]
        radar_targets = [90.0] * len(radar_scores)

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_scores + [radar_scores[0]],
            theta=radar_categories + [radar_categories[0]],
            fill='toself',
            fillcolor='rgba(128, 0, 0, 0.45)',
            line=dict(color='#D4AF37', width=2.5),
            name='VFSTR Achieved'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_targets + [radar_targets[0]],
            theta=radar_categories + [radar_categories[0]],
            line=dict(color='#10B981', width=1.5, dash='dash'),
            name='Target Benchmark (90%)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color='#94A3B8')),
                angularaxis=dict(tickfont=dict(color='#E2E8F0', size=11))
            ),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=380,
            margin=dict(l=40, r=40, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_bar:
        st.markdown(f"#### 📈 Points Achieved vs Maximum Weight ({framework})")
        bar_df = pd.DataFrame([
            {
                "Criterion": c_id,
                "Achieved Points": c_data["achieved_points"],
                "Max Weight": c_data["weight"],
                "Deficit Points": round(c_data["weight"] - c_data["achieved_points"], 1)
            }
            for c_id, c_data in criteria_data.items()
        ])

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=bar_df["Criterion"],
            y=bar_df["Achieved Points"],
            name="Achieved Score",
            marker_color='#800000',
            text=bar_df["Achieved Points"],
            textposition='auto'
        ))
        fig_bar.add_trace(go.Bar(
            x=bar_df["Criterion"],
            y=bar_df["Deficit Points"],
            name="Compliance Gap",
            marker_color='rgba(239, 68, 68, 0.45)',
            text=bar_df["Deficit Points"],
            textposition='auto'
        ))
        fig_bar.update_layout(
            barmode='stack',
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=380,
            xaxis=dict(title="Criterion ID"),
            yaxis=dict(title="Points"),
            margin=dict(l=20, r=20, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Department Readiness Ranking
    st.markdown("---")
    st.markdown("#### 🏢 Department-Wise Accreditation Readiness Rankings")
    dept_stats = st.session_state.scoring_engine.get_department_breakdown(st.session_state.evidence_list)
    dept_cols = st.columns(3)
    for i, d in enumerate(dept_stats[:6]):
        with dept_cols[i % 3]:
            badge_class = "badge-success" if d["status"] == "Ready" else ("badge-warning" if d["status"] == "Moderate" else "badge-danger")
            st.markdown(f"""
            <div class="kpi-card" style="margin-bottom: 12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#F1F5F9; font-size:14px;">{d['department']}</span>
                    <span class="{badge_class}">{d['status']}</span>
                </div>
                <div style="margin: 10px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:4px;">
                        <span>Readiness: {d['readiness_pct']}%</span>
                        <span>Evidence: {d['evidence_count']} docs ({d['verified_count']} verified)</span>
                    </div>
                    <div style="width:100%; background:rgba(255,255,255,0.1); border-radius:4px; height:8px;">
                        <div style="width:{d['readiness_pct']}%; background:linear-gradient(90deg, #800000, #D4AF37); height:8px; border-radius:4px;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # What-If Scenario Sandbox
    st.markdown("---")
    with st.expander("🧪 What-If Accreditation Scenario Simulator (Interactive)", expanded=False):
        st.markdown("Simulate the quantitative impact of institutional interventions on your predicted NAAC CGPA or NBA points.")
        sim_c1, sim_c2, sim_c3 = st.columns(3)
        with sim_c1:
            sim_phd = st.slider("Faculty with Ph.D. Percentage (Metric 2.4.2 / NBA-5.3)", min_value=50.0, max_value=100.0, value=75.7, step=1.0)
            st.session_state.simulated_adjustments["2.4.2"] = sim_phd
            st.session_state.simulated_adjustments["NBA-5.3"] = sim_phd
        with sim_c2:
            sim_grants = st.slider("Extramural Research Grants (Lakhs INR) (Metric 3.2.1 / NBA-5.5)", min_value=200.0, max_value=1000.0, value=682.4, step=25.0)
            st.session_state.simulated_adjustments["3.2.1"] = sim_grants
            st.session_state.simulated_adjustments["NBA-5.5"] = sim_grants
        with sim_c3:
            sim_placement = st.slider("Placement & Higher Ed % (Metric 5.2.1 / NBA-4.3)", min_value=60.0, max_value=100.0, value=86.4, step=1.0)
            st.session_state.simulated_adjustments["5.2.1"] = sim_placement
            st.session_state.simulated_adjustments["NBA-4.3"] = sim_placement

        if st.button("Apply Simulation"):
            st.rerun()


# ==========================================
# TAB 2: EVIDENCE REPOSITORY & INGESTION
# ==========================================
with tab2:
    st.markdown("### 📁 Institutional Evidence Repository & Smart Ingestion Engine")

    # Ingestion Form & Text Uploader
    with st.expander("⚡ Upload / Ingest New Institutional Evidence Document", expanded=False):
        st.markdown("Upload any institutional report, circular, audit statement, or BoS minutes for **AI-powered semantic mapping** to accreditation criteria.")
        
        up_col1, up_col2 = st.columns([1, 1])
        with up_col1:
            doc_title = st.text_input("Document Title", placeholder="e.g. Board of Studies Minutes - R24 Curriculum Revision CSE")
            doc_dept = st.selectbox("Originating Department / Cell", VIGNAN_DEPARTMENTS, key="up_dept")
            doc_year = st.selectbox("Academic Assessment Year", VIGNAN_ACADEMIC_YEARS, key="up_year")
            doc_authority = st.text_input("Issuing Authority", placeholder="e.g. Dean Academics & HoD CSE")

        with up_col2:
            doc_type = st.selectbox("Document Classification", [
                "BoS Minutes & Resolutions", "Statutory Audit Report", "Sanction Order", 
                "Policy & SOP Document", "Survey & ATR Report", "Examination Gazette",
                "Patent / Grant Certificate", "MoU Agreement", "Spreadsheet Register"
            ])
            uploaded_file = st.file_uploader("Upload Evidence File (PDF, DOCX, XLSX, TXT)", type=["pdf", "docx", "xlsx", "csv", "txt"])
            raw_text_input = st.text_area("Document Text Excerpt (for semantic indexing)", height=100, placeholder="Paste executive text excerpt from the document...")

        if st.button("⚡ Ingest & Semantically Map Evidence", use_container_width=True):
            content_to_index = raw_text_input.strip()
            if uploaded_file and not content_to_index:
                content_to_index = f"{uploaded_file.name} - Official record uploaded by {doc_authority} for {doc_dept} ({doc_year})."
            
            if not doc_title or not content_to_index:
                st.error("Please provide both a Document Title and Document Text content.")
            else:
                # Run semantic mapping
                matches = st.session_state.ev_engine.map_evidence_to_metrics(content_to_index, framework=framework, top_k=3)
                matched_criteria_ids = [m["criterion_id"] for m in matches] + [m["metric_id"] for m in matches]

                new_ev = {
                    "id": f"EVD-VIG-{len(st.session_state.evidence_list) + 101}",
                    "title": doc_title,
                    "department": doc_dept,
                    "academic_year": doc_year,
                    "document_type": doc_type,
                    "issuing_authority": doc_authority or "VFSTR Directorate",
                    "content_summary": content_to_index[:250] + ("..." if len(content_to_index) > 250 else ""),
                    "raw_text": content_to_index,
                    "status": "Under Review",
                    "completeness_score": 88,
                    "missing_elements": [],
                    "applicable_criteria": list(set(matched_criteria_ids)),
                    "verified_by": None,
                    "verification_date": None,
                    "file_format": uploaded_file.name.split('.')[-1].upper() if uploaded_file else "TXT",
                    "file_size": f"{round(len(content_to_index)/1024, 1)} KB"
                }

                # Evaluate quality
                quality = st.session_state.ev_engine.evaluate_evidence_quality(new_ev)
                new_ev["completeness_score"] = quality["quality_score"]
                new_ev["missing_elements"] = quality["penalties"]

                st.session_state.evidence_list.insert(0, new_ev)
                st.success(f"✅ Successfully ingested `{new_ev['id']}`! Automatically mapped to {len(matches)} metrics with {quality['quality_score']}% Quality Score.")
                st.rerun()

    # Evidence Search & Filter Table
    st.markdown("---")
    st.markdown("#### 📚 Uploaded Evidence Master List")
    
    search_q = st.text_input("🔍 Search evidence by keyword, title, or ID", placeholder="Search 'Scopus', 'Solar', 'BoS', 'Placements'...")
    display_docs = filtered_evidence
    if search_q.strip():
        display_docs = [
            e for e in display_docs
            if search_q.lower() in e["title"].lower() or search_q.lower() in e.get("raw_text", "").lower() or search_q.lower() in e["id"].lower()
        ]

    st.markdown(f"*Showing {len(display_docs)} institutional evidence records.*")

    for ev in display_docs:
        with st.container():
            col_id, col_info, col_status = st.columns([1, 4, 1.5])
            with col_id:
                st.markdown(f"**`{ev['id']}`**")
                st.caption(f"{ev.get('file_format', 'PDF')} ({ev.get('file_size', '2.5 MB')})")
            with col_info:
                st.markdown(f"**{ev['title']}**")
                st.caption(f"🏢 {ev['department']} | 📅 {ev['academic_year']} | ✍️ {ev.get('issuing_authority', 'Registrar')}")
                st.markdown(f"<span style='font-size:12px; color:#94A3B8;'>{ev['content_summary']}</span>", unsafe_allow_html=True)
                
                # Tags for mapped criteria
                tags_html = " ".join([f"<span class='badge-info' style='font-size:10px;'>{crit}</span>" for crit in ev.get("applicable_criteria", [])[:4]])
                st.markdown(tags_html, unsafe_allow_html=True)
            with col_status:
                status_cls = "badge-success" if ev["status"] == "Verified" else ("badge-warning" if ev["status"] == "Under Review" else "badge-danger")
                st.markdown(f"<span class='{status_cls}'>{ev['status']}</span>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:12px; margin-top:4px;'>Quality: <strong>{ev.get('completeness_score', 90)}%</strong></div>", unsafe_allow_html=True)
                if ev.get("missing_elements"):
                    st.markdown(f"<span style='font-size:11px; color:#F87171;'>⚠️ {len(ev['missing_elements'])} item(s) pending</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:10px 0; opacity:0.1;'>", unsafe_allow_html=True)


# ==========================================
# TAB 3: CRITERIA & REQUIREMENT MAPPING
# ==========================================
with tab3:
    st.markdown(f"### 🎯 {framework} Criteria & Requirement Compliance Engine")

    criteria_dict = get_framework_criteria(framework)
    crit_keys = list(criteria_dict.keys())
    
    selected_crit_key = st.selectbox(
        "Select Accreditation Criterion to Audit",
        crit_keys,
        format_func=lambda k: f"{criteria_dict[k]['icon']} {criteria_dict[k]['name']} ({criteria_dict[k]['weight']} Pts)"
    )

    crit_info = criteria_dict[selected_crit_key]
    crit_eval = eval_result["criteria_breakdown"][selected_crit_key]

    # Criterion Header Summary
    c_hdr1, c_hdr2, c_hdr3, c_hdr4 = st.columns(4)
    with c_hdr1:
        st.metric("Total Weightage", f"{crit_info['weight']} Pts")
    with c_hdr2:
        st.metric("Achieved Score", f"{crit_eval['achieved_points']} Pts")
    with c_hdr3:
        st.metric("Readiness %", f"{crit_eval['score_pct']}%")
    with c_hdr4:
        st.metric("Status", crit_eval["status"])

    st.markdown(f"*{crit_info['description']}*")
    st.markdown("---")

    # Metrics Breakdown
    st.markdown("#### 📋 Detailed Metrics & Evidence Mapping")

    for metric_eval in crit_eval["metrics"]:
        m_id = metric_eval["metric_id"]
        m_name = metric_eval["metric_name"]
        m_type = metric_eval["type"]
        m_weight = metric_eval["weight"]
        m_score = metric_eval["score_pct"]

        # Find mapped evidence
        mapped_docs = [
            e for e in st.session_state.evidence_list
            if m_id in e.get("applicable_criteria", []) or selected_crit_key in e.get("applicable_criteria", [])
        ]

        with st.expander(f"📌 [{m_id}] {m_name} ({m_weight} Pts | {m_type}) — Score: {m_score}%", expanded=True):
            mc1, mc2 = st.columns([2, 1])
            with mc1:
                st.markdown(f"**Metric Description:** {crit_info['metrics'][m_id]['description']}")
                st.markdown(f"**Benchmark Target:** `{crit_info['metrics'][m_id]['benchmark']}` | **Achieved Value:** `{metric_eval['achieved_value']}` | **Weighted Points:** `{metric_eval['weighted_score']} / {m_weight}`")
                
                st.markdown("**Mandatory Evidence Checklist:**")
                req_types = crit_info['metrics'][m_id].get("required_evidence", [])
                for req in req_types:
                    # Check if evidence matches
                    has_ev = any(req.lower() in e["title"].lower() or req.lower() in e.get("document_type", "").lower() for e in mapped_docs)
                    check_icon = "🟢" if has_ev else "🟡"
                    st.markdown(f"- {check_icon} {req}")

            with mc2:
                st.markdown("**Mapped Evidence Records:**")
                if mapped_docs:
                    for md in mapped_docs[:3]:
                        st.markdown(f"- **`{md['id']}`**: {md['title'][:40]}... *(Quality: {md.get('completeness_score', 90)}%)*")
                else:
                    st.warning("⚠️ No evidence records directly mapped to this metric.")

                # Action button to trigger SAR narrative
                if st.button(f"✍️ Draft Narrative for {m_id}", key=f"btn_nar_{m_id}"):
                    st.session_state.target_narrative_metric = m_id
                    st.info(f"Navigate to 'SAR Narrative Studio' to view the generated draft for {m_id}!")


# ==========================================
# TAB 4: GAP PRIORITIZATION MATRIX (IMPACT vs EFFORT)
# ==========================================
with tab4:
    st.markdown("### ⚡ Accreditation Gap Prioritization Matrix (Impact vs Effort)")
    st.markdown("Actionable 2x2 prioritization framework classifying institutional deficiencies by compliance impact against resolution effort.")

    # 2x2 Plotly Scatter Quadrant Chart
    gaps_ranked = gap_matrix["all_gaps_ranked"]
    if gaps_ranked:
        gap_df = pd.DataFrame([
            {
                "Metric": g["metric_id"],
                "Criterion": g["criterion_id"],
                "Impact Score": g["impact_score"],
                "Effort Score": g["effort_score"],
                "Quadrant": g["quadrant"],
                "Deficiency": g["deficiency_reason"],
                "Timeline": g["recommended_timeline"],
                "Owner": g["suggested_owner"],
                "Severity": g["severity"]
            }
            for g in gaps_ranked
        ])

        fig_quad = px.scatter(
            gap_df,
            x="Effort Score",
            y="Impact Score",
            color="Quadrant",
            text="Metric",
            hover_data=["Deficiency", "Owner", "Timeline", "Severity"],
            size=[14] * len(gap_df),
            color_discrete_map={
                "Quick Win": "#10B981",
                "Major Strategic Project": "#3B82F6",
                "Fill-in Task": "#F59E0B",
                "Deprioritized / Long-term": "#94A3B8"
            }
        )

        # Draw Quadrant Dividers & Annotations
        fig_quad.add_hline(y=5.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig_quad.add_vline(x=5.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")

        fig_quad.add_annotation(x=2.5, y=9.0, text="🟢 QUICK WINS<br>(High Impact, Low Effort)", showarrow=False, font=dict(color="#10B981", size=11))
        fig_quad.add_annotation(x=8.5, y=9.0, text="🔵 MAJOR STRATEGIC PROJECTS<br>(High Impact, High Effort)", showarrow=False, font=dict(color="#3B82F6", size=11))
        fig_quad.add_annotation(x=2.5, y=2.0, text="🟡 FILL-IN TASKS<br>(Low Impact, Low Effort)", showarrow=False, font=dict(color="#F59E0B", size=11))
        fig_quad.add_annotation(x=8.5, y=2.0, text="⚪ DE-PRIORITIZED<br>(Low Impact, High Effort)", showarrow=False, font=dict(color="#94A3B8", size=11))

        fig_quad.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=440,
            xaxis=dict(title="Resolution Effort (1: Minimal -> 10: Heavy Capital/Time)", range=[0.5, 10.5]),
            yaxis=dict(title="Accreditation Compliance Impact (1: Low -> 10: Critical)", range=[0.5, 10.5]),
            margin=dict(l=40, r=40, t=20, b=30)
        )
        st.plotly_chart(fig_quad, use_container_width=True)

    # Detailed Prioritized Gaps List
    st.markdown("---")
    st.markdown("#### 🎯 Prioritized Remediation Action List")
    
    quad_filter = st.selectbox("Filter by Strategic Quadrant", ["All Quadrants", "Quick Win", "Major Strategic Project", "Fill-in Task", "Deprioritized / Long-term"])
    filtered_gaps = gaps_ranked
    if quad_filter != "All Quadrants":
        filtered_gaps = [g for g in filtered_gaps if g["quadrant"] == quad_filter]

    for g in filtered_gaps:
        with st.container():
            gc1, gc2, gc3 = st.columns([1.5, 3.5, 1.5])
            with gc1:
                st.markdown(f"**`{g['metric_id']}`** ({g['criterion_id']})")
                st.markdown(f"<span class='badge-info'>{g['quadrant_badge']}</span>", unsafe_allow_html=True)
                st.caption(f"Impact: **{g['impact_score']}/10** | Effort: **{g['effort_score']}/10**")
            with gc2:
                st.markdown(f"**{g['metric_name']}**")
                st.markdown(f"<span style='font-size:12px; color:#F87171;'>Deficiency: {g['deficiency_reason']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='font-size:12px; color:#34D399;'>Action: {g['recommended_action']}</span>", unsafe_allow_html=True)
                st.caption(f"Suggested Owner: 👤 {g['suggested_owner']} | ⏱️ Target: {g['recommended_timeline']}")
            with gc3:
                if st.button("➕ Convert to Task", key=f"btn_task_{g['metric_id']}"):
                    new_t = st.session_state.task_manager.add_task(
                        title=f"Remediate Gap in {g['metric_id']}: {g['metric_name'][:40]}",
                        metric_id=g['metric_id'],
                        criterion_id=g['criterion_id'],
                        owner=g['suggested_owner'],
                        priority="Critical" if g['impact_score'] >= 7.5 else "High",
                        action_plan=g['recommended_action']
                    )
                    st.success(f"Created Task `{new_t['id']}`! Assigned to {g['suggested_owner']}.")
                    st.rerun()
            st.markdown("<hr style='margin:10px 0; opacity:0.1;'>", unsafe_allow_html=True)


# ==========================================
# TAB 5: REMEDIATION ACTION HUB
# ==========================================
with tab5:
    st.markdown("### 📋 Corrective Remediation Task Management Hub")

    # Task Statistics KPI Row
    tc1, tc2, tc3, tc4 = st.columns(4)
    with tc1:
        st.metric("Total Action Items", task_stats["total_tasks"])
    with tc2:
        st.metric("Open / In Progress", task_stats["open"] + task_stats["in_progress"])
    with tc3:
        st.metric("In Review / Verification", task_stats["in_review"])
    with tc4:
        st.metric("Resolved", task_stats["resolved"], delta=f"{task_stats['resolution_rate_pct']}% rate")

    st.markdown("---")

    # Create Custom Task Expander
    with st.expander("➕ Create New Corrective Action Task", expanded=False):
        t_form_c1, t_form_c2 = st.columns(2)
        with t_form_c1:
            new_task_title = st.text_input("Task Title", placeholder="e.g. Conduct external green audit review")
            new_task_metric = st.text_input("Metric Reference", value="7.1.2")
            new_task_owner = st.selectbox("Designated Institutional Owner", [
                "Dr. K. Ramamohan (Director IQAC)",
                "Dr. N. Veeranjaneyulu (Dean Academics)",
                "Dr. G. Srinivasa Rao (Dean R&D)",
                "Dr. D. Vijaya Ramu (Dean Placements)",
                "Er. K. Sambasiva Rao (Estate Officer)",
                "Dr. M. S. S. Rukmini (Dean Student Affairs)",
                "Dr. P. M. V. Rao (Registrar)"
            ])
        with t_form_c2:
            new_task_priority = st.selectbox("Priority Level", ["Critical", "High", "Medium", "Low"])
            new_task_days = st.slider("Target Turnaround Time (Days)", 1, 60, 14)
            new_task_plan = st.text_area("Detailed Action Plan", placeholder="Describe exact steps for resolution...")

        if st.button("Save Action Task", use_container_width=True):
            if not new_task_title:
                st.error("Please provide a task title.")
            else:
                st.session_state.task_manager.add_task(
                    title=new_task_title,
                    metric_id=new_task_metric,
                    criterion_id="C" + new_task_metric[0] if new_task_metric[0].isdigit() else "NBA",
                    owner=new_task_owner,
                    priority=new_task_priority,
                    estimated_days=new_task_days,
                    action_plan=new_task_plan
                )
                st.success("Corrective task saved!")
                st.rerun()

    # Filterable Task Table & Status Updater
    st.markdown("#### 📌 Active Remediation Tasks Board")
    status_filter = st.selectbox("Filter Tasks by Status", ["All", "Open", "In Progress", "In Review", "Resolved"])
    filtered_tasks = st.session_state.task_manager.filter_tasks(status=status_filter)

    for t in filtered_tasks:
        with st.container():
            col_t_id, col_t_desc, col_t_act = st.columns([1.2, 3.5, 2.3])
            with col_t_id:
                st.markdown(f"**`{t['id']}`**")
                p_cls = "badge-danger" if t["priority"] == "Critical" else ("badge-warning" if t["priority"] == "High" else "badge-info")
                st.markdown(f"<span class='{p_cls}'>{t['priority']}</span>", unsafe_allow_html=True)
                st.caption(f"Ref: Metric `{t['metric_id']}`")
            with col_t_desc:
                st.markdown(f"**{t['title']}**")
                st.markdown(f"<span style='font-size:12px; color:#94A3B8;'>{t['action_plan']}</span>", unsafe_allow_html=True)
                st.caption(f"👤 {t['owner']} | 📅 Deadline: **{t['deadline']}**")
                if t.get("resolution_notes"):
                    st.markdown(f"<span style='font-size:11px; color:#34D399;'>Notes: {t['resolution_notes']}</span>", unsafe_allow_html=True)
            with col_t_act:
                current_status = t["status"]
                new_st = st.selectbox(
                    "Status",
                    ["Open", "In Progress", "In Review", "Resolved"],
                    index=["Open", "In Progress", "In Review", "Resolved"].index(current_status),
                    key=f"status_sel_{t['id']}"
                )
                if new_st != current_status:
                    st.session_state.task_manager.update_task_status(t["id"], new_st)
                    st.rerun()
            st.markdown("<hr style='margin:8px 0; opacity:0.1;'>", unsafe_allow_html=True)


# ==========================================
# TAB 6: AUTOMATED SAR / SSR NARRATIVE STUDIO
# ==========================================
with tab6:
    st.markdown(f"### ✍️ {framework} Self Assessment Report (SSR / SAR) Narrative Studio")
    st.markdown("Offline AI narrative synthesizer producing executive-grade, peer-review-ready qualitative sections with verifiable evidence citations.")

    all_metrics = get_all_metrics_flat(framework)
    metric_options = {f"{m['id']}: {m['name']} ({m['type']})": m for m in all_metrics}

    selected_metric_str = st.selectbox("Select Metric to Draft Narrative for", list(metric_options.keys()))
    curr_metric = metric_options[selected_metric_str]

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        narrative_tone = st.selectbox("Narrative Synthesis Style", ["Executive & Evidence-Backed", "Technical & Process-Oriented", "Brief Regulatory Summary"])
    with col_opt2:
        custom_notes = st.text_input("Additional Department Context / Specific Achievements", placeholder="e.g. Include mention of 2023 IEEE Conference hosted by CSE...")

    # Find mapped evidence
    mapped_evidence_for_metric = [
        e for e in st.session_state.evidence_list
        if curr_metric["id"] in e.get("applicable_criteria", []) or curr_metric["criterion_id"] in e.get("applicable_criteria", [])
    ]

    if st.button("✨ Generate Executive SSR / SAR Narrative", use_container_width=True):
        generated = st.session_state.narrative_gen.generate_metric_narrative(
            metric=curr_metric,
            mapped_evidence=mapped_evidence_for_metric,
            framework=framework,
            focus_tone=narrative_tone,
            additional_notes=custom_notes
        )
        st.session_state.active_narrative = generated["markdown_content"]

    if "active_narrative" in st.session_state:
        st.markdown("---")
        st.markdown("#### 📄 Generated Narrative Draft (Editable & Exportable)")
        
        edit_tab, preview_tab = st.tabs(["✏️ Edit Markdown Source", "👁️ Live Formatted Preview"])
        with edit_tab:
            edited_narrative = st.text_area("Markdown Content", value=st.session_state.active_narrative, height=450)
            st.session_state.active_narrative = edited_narrative
        with preview_tab:
            st.markdown(st.session_state.active_narrative)

        st.download_button(
            label="📥 Download Narrative (.md)",
            data=st.session_state.active_narrative,
            file_name=f"VFSTR_{framework}_Narrative_{curr_metric['id'].replace('.', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )


# ==========================================
# TAB 7: IQAC HUMAN VERIFICATION & EXPORTS
# ==========================================
with tab7:
    st.markdown("### 🛡️ Human-in-the-Loop IQAC Verification & Official Exports")
    st.markdown("Formal review portal for IQAC Director, Deans, and Peer Auditors to authenticate evidence and export official compliance dossiers.")

    # Reviewer Action Panel
    st.markdown("#### 🔍 Evidence Verification Workbench")
    unverified_docs = [e for e in st.session_state.evidence_list if e.get("status") in ["Under Review", "Draft", "Needs Revision"]]
    
    if unverified_docs:
        doc_to_audit_title = st.selectbox("Select Evidence Document to Audit", [f"{e['id']}: {e['title']}" for e in unverified_docs])
        doc_id_to_audit = doc_to_audit_title.split(":")[0]
        active_doc = next(e for e in st.session_state.evidence_list if e["id"] == doc_id_to_audit)

        v_col1, v_col2 = st.columns([1.5, 1])
        with v_col1:
            st.markdown(f"**Document Title:** {active_doc['title']}")
            st.markdown(f"**Department:** {active_doc['department']} | **Year:** {active_doc['academic_year']}")
            st.markdown(f"**Current Status:** `{active_doc['status']}` | **Current Completeness:** `{active_doc.get('completeness_score', 85)}%`")
            st.text_area("Raw Text Preview", value=active_doc.get("raw_text", active_doc["content_summary"]), height=120, disabled=True)

        with v_col2:
            audit_action = st.selectbox("Verification Decision", [
                "VERIFIED_APPROVED", "VERIFIED_WITH_CONCERNS", "REQUEST_REVISION", "REJECTED"
            ])
            completeness_adj = st.slider("Verified Completeness Score", 10, 100, active_doc.get("completeness_score", 90))
            audit_comment = st.text_area("Official Auditor Rationale & Remarks", placeholder="e.g. Verified against original BoS minutes. All signatures authenticated.")

            if st.button("Submit Formal Verification Record", use_container_width=True):
                role_parts = reviewer_profile.split("(")
                rev_name = role_parts[0].strip()
                rev_role = role_parts[1].replace(")", "").strip() if len(role_parts) > 1 else "Reviewer"

                st.session_state.audit_verifier.record_verification(
                    evidence=active_doc,
                    reviewer_name=rev_name,
                    reviewer_role=rev_role,
                    action=audit_action,
                    audit_notes=audit_comment,
                    completeness_adjustment=completeness_adj
                )
                st.success(f"Formal verification recorded for `{active_doc['id']}`! Status updated to `{active_doc['status']}`.")
                st.rerun()
    else:
        st.success("🎉 All institutional evidence documents have been reviewed and verified!")

    # Immutable Audit Log Table
    st.markdown("---")
    st.markdown("#### 📜 Immutable Audit Trail Log")
    audit_logs = st.session_state.audit_verifier.get_audit_trail()
    audit_df = pd.DataFrame(audit_logs)
    if not audit_df.empty:
        st.dataframe(audit_df[["timestamp", "reviewer_name", "reviewer_role", "evidence_id", "action", "new_status", "audit_notes"]], use_container_width=True)

    # Export Center
    st.markdown("---")
    st.markdown("#### 📥 Official Accreditation Dossier Export Center")
    exp_c1, exp_c2, exp_c3 = st.columns(3)

    with exp_c1:
        st.markdown("**1. Executive PDF Dossier**")
        st.caption("Complete multi-page executive report with scoring matrix, gap analysis, task logs, and IQAC seal.")
        pdf_bytes = generate_accreditation_dossier_pdf(
            evaluation_result=eval_result,
            gap_matrix_result=gap_matrix,
            tasks=st.session_state.task_manager.get_all_tasks(),
            audit_trail=st.session_state.audit_verifier.get_audit_trail()
        )
        st.download_button(
            label="📄 Download Official PDF Dossier",
            data=pdf_bytes,
            file_name=f"VFSTR_{framework}_Accreditation_Readiness_Dossier_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with exp_c2:
        st.markdown("**2. Evidence Master Register (CSV)**")
        st.caption("Consolidated spreadsheet of all institutional evidence records and completeness scores.")
        ev_df = pd.DataFrame(st.session_state.evidence_list)
        csv_data = ev_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Evidence CSV",
            data=csv_data,
            file_name=f"VFSTR_Evidence_Master_Register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_c3:
        st.markdown("**3. Immutable Audit Logs (JSON)**")
        st.caption("Cryptographically verifiable JSON audit trail of all peer verification decisions.")
        json_data = json.dumps(audit_logs, indent=2)
        st.download_button(
            label="🛡️ Download Audit Trail JSON",
            data=json_data,
            file_name=f"VFSTR_Accreditation_Audit_Trail_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
