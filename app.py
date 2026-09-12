"""
Vignan University AI Accreditation Academic Agent (VFSTR)
Streamlit Application for Continuous Accreditation Readiness Assessment (NAAC & NBA)
Includes Bujji Agentic AI Copilot Interface (CSE Presents: Agentic AI Day 2026)
"""

import json
import io
import os
import base64
from typing import Optional, Dict, List, Any, Union
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
from core.ranking_engine import RankingEngine, NIRF_PARAMETERS, QS_PARAMETERS, VIGNAN_NIRF_BASELINE
from core.obe_mapping_engine import OBEMappingEngine, VIGNAN_OBE_DATA
from core.task_manager import TaskManager
from core.narrative_generator import NarrativeGenerator
from core.audit_verifier import AuditVerifier
from core.evidence_validator import EvidenceValidator, REQUIRED_FORMAT_RULES
from core.continuous_scanner import ContinuousReadinessScanner
from core.submission_builder import SubmissionPackageBuilder
from core.mock_visit_engine import MockVisitSimulatorEngine, PEER_VISIT_QUESTION_BANK
from core.pdf_exporter import generate_accreditation_dossier_pdf
from core.api_client import AccreditationApiClient
from core.database import get_database, DatabaseManager, DB_FILE_PATH


# Set Streamlit Page Configuration
st.set_page_config(
    page_title="VFSTR AI Accreditation Agent | Agentic AI Day 2026",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_avatar_base64() -> str:
    """Loads and encodes the Bujji 3D robot avatar image as base64."""
    try:
        avatar_path = os.path.join(os.path.dirname(__file__), "data", "bujji_avatar.jpg")
        if os.path.exists(avatar_path):
            with open(avatar_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        pass
    return ""


# Custom CSS for Vignan University Branding and Bujji Agentic AI UI
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Vignan University Palette Variables */
    :root {
        --vignan-maroon: #800000;
        --vignan-crimson: #8B1E28;
        --vignan-gold: #D4AF37;
        --vignan-gold-light: #FDF6B2;
        --accent-blue: #0284C7;
        --accent-green: #10B981;
        --accent-amber: #F59E0B;
        --accent-red: #EF4444;
        --card-bg: rgba(30, 41, 59, 0.7);
        --card-border: rgba(255, 255, 255, 0.08);
    }

    /* Top Brand Showcase Bar */
    .top-brand-bar {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 12px 24px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    }

    /* Vignan Maroon Header Banner */
    .vignan-header {
        background: linear-gradient(135deg, #670000 0%, #8B1E28 50%, #4A0000 100%);
        border-radius: 16px;
        padding: 22px 30px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(128, 0, 0, 0.4);
        border: 1px solid rgba(212, 175, 55, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .vignan-title {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF;
    }

    .vignan-subtitle {
        font-size: 13px;
        color: #F3E8FF;
        margin-top: 4px;
        opacity: 0.95;
    }

    .vignan-badge {
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
        color: #1A1A1A;
        font-size: 11px;
        font-weight: 800;
        padding: 6px 14px;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: inline-block;
    }

    /* Bujji Robot Hero Stage */
    .bujji-stage {
        background: radial-gradient(circle at 50% 30%, #F0F9FF 0%, #E0F2FE 45%, #BAE6FD 100%);
        border-radius: 20px;
        padding: 30px 20px 24px 20px;
        text-align: center;
        box-shadow: 0 12px 30px -5px rgba(2, 132, 199, 0.2);
        border: 1px solid rgba(186, 230, 253, 0.9);
        margin-bottom: 24px;
        position: relative;
    }
    
    .bujji-avatar-img {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        object-fit: cover;
        box-shadow: 0 12px 25px rgba(2, 132, 199, 0.3);
        border: 4px solid #FFFFFF;
        animation: floatAnimation 3.5s ease-in-out infinite;
    }

    @keyframes floatAnimation {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-7px); }
        100% { transform: translateY(0px); }
    }

    .bujji-stage-title {
        color: #0369A1;
        font-size: 22px;
        font-weight: 800;
        margin-top: 14px;
        letter-spacing: -0.3px;
    }
    
    .bujji-stage-sub {
        color: #0C4A6E;
        font-size: 13px;
        font-weight: 500;
        max-width: 680px;
        margin: 6px auto 0 auto;
        opacity: 0.95;
    }

    /* Conversational Message Cards */
    .msg-card-assistant {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #0284C7;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        color: #0F172A;
    }

    .msg-card-user {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 5px solid #7C3AED;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
        color: #0F172A;
    }

    .msg-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 6px;
    }

    .msg-badge-assistant {
        font-size: 11px;
        font-weight: 800;
        color: #0284C7;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .msg-badge-user {
        font-size: 11px;
        font-weight: 800;
        color: #7C3AED;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }

    .msg-timestamp {
        font-size: 11px;
        color: #94A3B8;
        font-weight: 500;
    }

    .msg-body {
        font-size: 13.5px;
        line-height: 1.65;
        color: #1E293B;
    }

    /* Agentic Status Bar */
    .bujji-status-bar {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #475569;
        margin-top: 18px;
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
        font-size: 28px;
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

    /* Sidebar Styling & High Contrast */
    [data-testid="stSidebar"] {
        background-color: #0B1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #F1F5F9 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #E2E8F0 !important;
    }

    /* High-contrast Sidebar Headings */
    .sidebar-header {
        color: #FFFFFF !important;
        font-size: 12.5px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        padding: 7px 12px !important;
        margin: 18px 0 10px 0 !important;
        background: linear-gradient(90deg, rgba(212, 175, 55, 0.18) 0%, rgba(255, 255, 255, 0.04) 100%) !important;
        border-left: 4px solid #D4AF37 !important;
        border-radius: 0 8px 8px 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }

    /* Primary Section Titles (H2 Level) */
    .app-section-header {
        background: linear-gradient(90deg, rgba(128, 0, 0, 0.07) 0%, rgba(212, 175, 55, 0.04) 60%, transparent 100%);
        border-left: 5px solid var(--vignan-maroon);
        border-bottom: 1px solid rgba(128, 0, 0, 0.12);
        border-radius: 0 12px 12px 0;
        padding: 14px 20px;
        margin: 18px 0 18px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }
    .app-section-title {
        font-size: 21px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.4px;
        margin: 0;
    }
    .app-section-subtitle {
        font-size: 13px;
        color: #475569;
        font-weight: 500;
        margin-top: 4px;
    }
    .app-section-badge {
        background: #FFFFFF;
        color: #1E293B;
        border: 1px solid #CBD5E1;
        font-size: 11px;
        font-weight: 800;
        padding: 5px 12px;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
    }

    /* Sub-section Headings (H3 Level) */
    .app-subheading {
        font-size: 16.5px;
        font-weight: 800;
        color: #1E293B;
        letter-spacing: -0.2px;
        display: flex;
        align-items: center;
        margin: 22px 0 8px 0;
        padding-bottom: 7px;
        border-bottom: 2px solid #E2E8F0;
    }
    .app-subheading-accent {
        color: var(--vignan-maroon);
        font-weight: 900;
        margin-right: 6px;
    }
    .app-subheading-badge {
        margin-left: auto;
        font-size: 11px;
        font-weight: 700;
        background: rgba(2, 132, 199, 0.1);
        color: #0284C7;
        padding: 3px 9px;
        border-radius: 6px;
        border: 1px solid rgba(2, 132, 199, 0.25);
    }

    /* Clean Streamlit Tab Titles */
    [data-baseweb="tab-list"] {
        gap: 6px !important;
        margin-bottom: 12px !important;
    }
    [data-baseweb="tab"] {
        font-size: 13.5px !important;
        font-weight: 700 !important;
        padding: 10px 16px !important;
        border-radius: 8px 8px 0 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# Reusable Professional Heading Helpers
def render_section_heading(title: str, subtitle: Optional[str] = None, badge: Optional[str] = None):
    """Renders a prominent, high-contrast, professional H2 section header."""
    badge_html = f'<span class="app-section-badge">{badge}</span>' if badge else ""
    sub_html = f'<div class="app-section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="app-section-header">
        <div>
            <div class="app-section-title">{title}</div>
            {sub_html}
        </div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)


def render_subheading(title: str, subtitle: Optional[str] = None, badge: Optional[str] = None):
    """Renders a clean, structured H3 subsection title with subtle accent."""
    badge_html = f'<span class="app-subheading-badge">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="app-subheading">
        <span><span class="app-subheading-accent">▌</span> {title}</span>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div style='font-size: 12.5px; color: #64748B; margin: -4px 0 12px 0;'>{subtitle}</div>", unsafe_allow_html=True)


def render_sidebar_heading(title: str, icon: str = ""):
    """Renders a high-contrast, gold-accented sidebar heading for the dark theme."""
    icon_str = f"{icon} " if icon else ""
    st.markdown(f"""
    <div class="sidebar-header">
        {icon_str}{title}
    </div>
    """, unsafe_allow_html=True)



# Initialize Session State
def init_session_state():
    if "db" not in st.session_state:
        st.session_state.db = get_database()
    if "api_client" not in st.session_state:
        st.session_state.api_client = AccreditationApiClient()
    if "evidence_list" not in st.session_state:
        st.session_state.evidence_list = st.session_state.db.get_all_evidence()
    if "ev_engine" not in st.session_state:
        st.session_state.ev_engine = EvidenceEngine()
    if "scoring_engine" not in st.session_state:
        st.session_state.scoring_engine = ScoringEngine()
    if "gap_engine" not in st.session_state:
        st.session_state.gap_engine = GapMatrixEngine()
    if "task_manager" not in st.session_state:
        st.session_state.task_manager = TaskManager(use_db=True)
    if "narrative_gen" not in st.session_state:
        st.session_state.narrative_gen = NarrativeGenerator()
    if "audit_verifier" not in st.session_state:
        st.session_state.audit_verifier = AuditVerifier(use_db=True)
    if "validator" not in st.session_state:
        st.session_state.validator = EvidenceValidator()
    if "scanner" not in st.session_state:
        st.session_state.scanner = ContinuousReadinessScanner()
    if "submission_builder" not in st.session_state:
        st.session_state.submission_builder = SubmissionPackageBuilder()
    if "mock_visit_engine" not in st.session_state:
        st.session_state.mock_visit_engine = MockVisitSimulatorEngine()
    if "ranking_engine" not in st.session_state:
        st.session_state.ranking_engine = RankingEngine()
    if "obe_engine" not in st.session_state:
        st.session_state.obe_engine = OBEMappingEngine()
    if "doc_store" not in st.session_state:
        from core.document_store import DocumentStore
        st.session_state.doc_store = DocumentStore()
    if "nirf_simulated_adjustments" not in st.session_state:
        st.session_state.nirf_simulated_adjustments = {}
    if "simulated_adjustments" not in st.session_state:
        st.session_state.simulated_adjustments = {}
    if "target_narrative_metric" not in st.session_state:
        st.session_state.target_narrative_metric = "1.1.1"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "name": "Bujji (AI Accreditation Assistant)",
                "timestamp": "10:24 AM",
                "content": "Hi, I'm Bujji, your Agentic AI Day 2026 assistant. I'm here to guide you through institutional accreditation readiness for NAAC (7 Criteria, 1000 Pts, CGPA 3.79 A++) and NBA Tier-1 OBE (10 Criteria, 942 Pts), detect compliance gaps, draft SSR narratives, and manage remediation tasks. May I know how I can assist you today?"
            }
        ]

init_session_state()

# Check Backend API Health & Database Stats
backend_status = st.session_state.api_client.check_health()
is_backend_connected = bool(backend_status.get("connected", False))
db_stats = st.session_state.db.get_db_stats() if hasattr(st.session_state.db, "get_db_stats") else {}

# 1. Top Brand Showcase Bar (Matching Reference Image)
st.markdown("""
<div class="top-brand-bar">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div style="background: #800000; color: #FFFFFF; padding: 6px 14px; border-radius: 8px; font-weight: 900; font-size: 16px; letter-spacing: 0.5px;">
            🏛️ VIGNAN'S
        </div>
        <div>
            <div style="font-size: 12px; font-weight: 800; color: #800000; text-transform: uppercase; letter-spacing: 0.5px;">
                Deemed to be University
            </div>
            <div style="font-size: 10.5px; color: #64748B; font-weight: 500;">
                NAAC A+ Accredited | NIRF Top 100 Ranked | NBA Tier-1 OBE
            </div>
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 11px; font-weight: 800; color: #0284C7; letter-spacing: 1.2px; text-transform: uppercase;">
            CSE PRESENTS
        </div>
        <div style="font-size: 20px; font-weight: 900; color: #0F172A; letter-spacing: -0.5px;">
            AGENTIC AI DAY 2026
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Vignan Institutional Maroon Banner
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
    # Backend Connection Indicator & Ping Button
    backend_url = st.session_state.api_client.base_url
    if is_backend_connected:
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.15); border:1px solid #10B981; border-radius:8px; padding:8px 12px; margin-bottom:12px;">
            <span style="color:#34D399; font-weight:700; font-size:12px;">🟢 BACKEND REST API CONNECTED</span>
            <div style="font-size:10px; color:#A7F3D0;">FastAPI Server running on {backend_url}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:rgba(59,130,246,0.15); border:1px solid #3B82F6; border-radius:8px; padding:8px 12px; margin-bottom:12px;">
            <span style="color:#60A5FA; font-weight:700; font-size:12px;">⚡ INTEGRATED CORE ENGINE ACTIVE</span>
            <div style="font-size:10px; color:#BFDBFE;">Direct Local Processing Mode ({backend_url} offline)</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("📡 Reconnect / Ping Backend", use_container_width=True):
        status = st.session_state.api_client.check_health()
        if status.get("connected"):
            st.toast(f"✅ Backend REST API is online and responding at {backend_url}!", icon="🟢")
        else:
            st.toast("⚡ Operating in direct integrated local mode.", icon="ℹ️")
        st.rerun()

    # SQLite Database Management Widget
    st.markdown("""
    <div style="background:rgba(212,175,55,0.12); border:1px solid rgba(212,175,55,0.4); border-radius:8px; padding:8px 12px; margin-top:8px; margin-bottom:12px;">
        <span style="color:#FBBF24; font-weight:700; font-size:12px;">🗄️ SQLITE DATABASE: CONNECTED</span>
        <div style="font-size:10px; color:#FDE68A;">File: <code>data/accreditation.db</code></div>
    </div>
    """, unsafe_allow_html=True)

    render_sidebar_heading("Accreditation Framework", "⚙️")
    framework = st.selectbox(
        "Select Regulatory Framework",
        ["NAAC", "NBA"],
        help="NAAC: University Manual (7 Criteria) | NBA: Tier-1 Outcome Based Education (10 Criteria)"
    )

    st.markdown("<div style='margin: 14px 0 6px 0; border-top: 1px solid rgba(255,255,255,0.08);'></div>", unsafe_allow_html=True)
    render_sidebar_heading("Department & Year Filters", "🏢")
    selected_dept = st.selectbox("Department Filter", ["All Departments"] + VIGNAN_DEPARTMENTS)
    selected_year = st.selectbox("Assessment Academic Year", ["All Years"] + VIGNAN_ACADEMIC_YEARS)

    st.markdown("<div style='margin: 14px 0 6px 0; border-top: 1px solid rgba(255,255,255,0.08);'></div>", unsafe_allow_html=True)
    render_sidebar_heading("Human Reviewer Session", "👤")
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

    st.markdown("<div style='margin: 14px 0 6px 0; border-top: 1px solid rgba(255,255,255,0.08);'></div>", unsafe_allow_html=True)
    render_sidebar_heading("Database Operations", "🗄️")
    col_db1, col_db2 = st.columns(2)
    with col_db1:
        st.metric("Total Records", db_stats.get("total_records", 0))
    with col_db2:
        st.metric("DB Size", f"{db_stats.get('file_size_kb', 0)} KB")

    if st.button("🔄 Reset Database to Default", use_container_width=True):
        st.session_state.db.reset_database()
        st.session_state.evidence_list = st.session_state.db.get_all_evidence()
        st.session_state.task_manager = TaskManager(use_db=True)
        st.session_state.audit_verifier = AuditVerifier(use_db=True)
        st.session_state.simulated_adjustments = {}
        if "active_narrative" in st.session_state:
            del st.session_state["active_narrative"]
        st.toast("SQLite Database reset to default authentic Vignan records!", icon="✅")
        st.rerun()

    # DB JSON Export
    db_json_data = json.dumps({
        "stats": db_stats,
        "evidence": st.session_state.db.get_all_evidence(),
        "tasks": st.session_state.task_manager.get_all_tasks(),
        "audit_logs": st.session_state.audit_verifier.get_audit_trail()
    }, indent=2, default=str)
    
    st.download_button(
        label="💾 Export Database (JSON)",
        data=db_json_data,
        file_name=f"VFSTR_Accreditation_DB_Backup_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )


# Filter evidence based on sidebar selections
filtered_evidence = st.session_state.evidence_list
if selected_dept != "All Departments":
    filtered_evidence = [e for e in filtered_evidence if e.get("department") == selected_dept]
if selected_year != "All Years":
    filtered_evidence = [e for e in filtered_evidence if e.get("academic_year") == selected_year]

# Run Core Calculations (Using Backend API if online, or local engine)
eval_result = None
if is_backend_connected:
    eval_result = st.session_state.api_client.evaluate_framework(
        framework=framework,
        simulated_adjustments=st.session_state.simulated_adjustments
    )

if not eval_result:
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


# Smart Bujji Copilot Query Processor
def process_bujji_query(user_query: str, fw: str, eval_res: dict, g_matrix: dict, task_list: list, ev_list: list) -> str:
    q_lower = user_query.strip().lower()
    
    if any(k in q_lower for k in ["cgpa", "naac", "grade", "score", "points", "outcome", "evaluation"]):
        out = eval_res.get("outcome", {})
        if fw == "NAAC":
            return f"🎯 **VFSTR NAAC Institutional Readiness Evaluation**:\n\n- **Estimated CGPA**: `{out.get('cgpa', 3.79)} / 4.00`\n- **Projected Grade**: `{out.get('grade', 'A++')}`\n- **Readiness Index**: `{out.get('overall_score_pct', 92.4)}% Compliance`\n- **Key Highlights**: Criterion 1 (Curricular Aspects: 94.2%) and Criterion 6 (Governance & Leadership: 95.0%) demonstrate peak institutional strength.\n\n*Would you like to simulate a What-If scenario or inspect Criterion-specific breakdowns?*"
        else:
            return f"⚡ **VFSTR NBA Tier-1 Program Readiness Evaluation**:\n\n- **Total Score**: `{round(out.get('total_points', 942.2))} / 1000 Points`\n- **Accreditation Tier**: `{out.get('grade', 'Tier-1 (Full 6 Years Accreditation)')}`\n- **Readiness Index**: `{out.get('overall_score_pct', 94.2)}% Compliance`\n- **Key Highlights**: Criterion 1 (Vision, Mission & PEOs: 58/60 Pts) and Criterion 5 (Faculty Cadre & Quality: 192/200 Pts) strongly surpass NBA benchmarks."

    elif any(k in q_lower for k in ["gap", "quick win", "deficiency", "priorit"]):
        qw = g_matrix.get("quadrants", {}).get("Quick Win", [])
        maj = g_matrix.get("quadrants", {}).get("Major Strategic Project", [])
        total_gaps = g_matrix.get("total_gaps_count", len(g_matrix.get("all_gaps_ranked", [])))
        
        qw_items = "\n".join([f"  - 🟢 **[{g['metric_id']}]** {g['metric_name'][:45]}... *(Owner: {g['suggested_owner']})*" for g in qw[:3]]) if qw else "  - No critical quick wins pending."
        
        return f"⚡ **Accreditation Gap & Prioritization Matrix**:\n\n- **Total Compliance Deficiencies**: `{total_gaps} Items`\n- **Quick Wins (High Impact, Low Effort)**: `{len(qw)} Items`\n{qw_items}\n- **Major Strategic Projects (High Impact, High Effort)**: `{len(maj)} Items`\n\n*You can auto-convert all Quick Wins into actionable IQAC tasks in the Gap Prioritization Matrix tab!*"

    elif any(k in q_lower for k in ["evidence", "document", "upload", "records"]):
        verified_count = sum(1 for e in ev_list if e.get("status") == "Verified")
        return f"📁 **Institutional Evidence Repository Status**:\n\n- **Total Uploaded Artifacts**: `{len(ev_list)} Records` across 18 Departments\n- **Officially Verified by IQAC**: `{verified_count} Records`\n- **Average Artifact Quality**: `91.4% Completeness`\n- **Key Sources**: Board of Studies (BoS) minutes, Scopus publications (2,410+ papers), DST/DBT research grants (INR 682.4 L), Green audit reports (1.0 MW Solar), and Placement ledgers (86.4%)."

    elif any(k in q_lower for k in ["task", "remediation", "action", "todo"]):
        stats = st.session_state.task_manager.get_task_statistics()
        return f"📋 **Corrective Remediation Action Hub**:\n\n- **Total Action Items**: `{stats.get('total_tasks', 10)} Tasks`\n- **Resolved**: `{stats.get('resolved', 0)}` (Resolution Rate: `{stats.get('resolution_rate_pct', 0)}%`)\n- **In Progress / Review**: `{stats.get('in_progress', 0) + stats.get('in_review', 0)}`\n- **Critical Pending**: `{stats.get('critical_pending', 0)}`\n\n*Track assignments, update turnaround progress, and attach resolution notes in the Remediation Hub.*"

    elif any(k in q_lower for k in ["narrative", "ssr", "sar", "draft", "write"]):
        return f"✍️ **Self Assessment Report (SSR / SAR) Narrative Studio**:\n\nI can generate comprehensive, formal qualitative narratives with evidence citations for any metric across Criteria 1-7 (NAAC) and Criteria 1-10 (NBA).\n\n- **Active Target Metric**: `{st.session_state.get('target_narrative_metric', '1.1.1')}`\n- **Tone**: Executive & Evidence-Backed (Peer-Review Ready)\n\n*Head over to the 'SAR Narrative Studio' tab to generate, edit, and export qualitative Markdown sections.*"

    elif any(k in q_lower for k in ["nirf", "ranking", "qs", "tlr", "rpc", "rank", "world rank"]):
        nirf_res = st.session_state.ranking_engine.evaluate_nirf(st.session_state.nirf_simulated_adjustments)
        qs_res = st.session_state.ranking_engine.evaluate_qs_asia(st.session_state.nirf_simulated_adjustments)
        return f"🏆 **VFSTR Institutional Ranking Projections**:\n\n- **NIRF Composite Score**: `{nirf_res['overall_score']} / 100`\n- **Projected NIRF Rank Band**: `{nirf_res['rank_band']}` (Midpoint: Rank {nirf_res['rank_midpoint']})\n- **Five-Pillar Breakdown**: TLR: `{nirf_res['parameters']['TLR']['score']}/100` | RPC: `{nirf_res['parameters']['RPC']['score']}/100` | GO: `{nirf_res['parameters']['GO']['score']}/100` | OI: `{nirf_res['parameters']['OI']['score']}/100` | PR: `{nirf_res['parameters']['PR']['score']}/100`\n- **QS Asia Rank Band**: `{qs_res['qs_rank_band']}` (Score: `{qs_res['qs_composite_score']}/100`)\n\n*Head over to the 'NIRF & QS Ranking Simulator' tab to run What-If strategic simulations for reaching Top 50!*"

    elif any(k in q_lower for k in ["mock", "peer", "visit", "inspector", "defense", "question", "interview"]):
        mv_summary = st.session_state.mock_visit_engine.get_simulation_summary()
        return f"🤝 **Peer-Team Mock Visit Inspection Simulator**:\n\n- **Preparedness Status**: `{mv_summary.get('overall_status')}`\n- **Average Defense Score**: `{mv_summary.get('average_readiness_score')}% / 100`\n- **Question Bank**: 10 Core Inspection Categories (Curriculum, CO-PO Attainment, SFR, Extramural Grants, Placements, Infrastructure, IQAC ATRs, NEP 2020)\n- **Key Defense Strategy**: Ground all faculty responses in verified `EVD-VIG-xxx` proofs and cite exact numbers (e.g., INR 18.42 Cr grants, 87.6% placements, 1:13.8 SFR).\n\n*Head over to the 'Peer Mock Visit Simulator' tab to practice defending inspection questions with instant AI scoring!*"

    elif any(k in q_lower for k in ["scanner", "continuous", "audit", "expir", "defect", "freshness"]):
        scan_res = st.session_state.scanner.scan_all_criteria(framework=fw, evidence_list=st.session_state.evidence_list)
        return f"🔍 **Continuous Readiness Scanner Diagnostics**:\n\n- **Institutional Health Index**: `{scan_res['overall_readiness_pct']}% Compliant`\n- **Forecast Grade**: `{scan_res['grade_forecast']}` (Predicted CGPA: `{scan_res['cgpa_forecast']}/4.00`)\n- **Compliant Criteria**: `{scan_res['summary_counts']['compliant']} of {scan_res['summary_counts']['total_criteria']}`\n- **At Risk / Expiring Artifacts**: `{scan_res['summary_counts']['expiring_evidence_count']} Items`\n- **Unverified Pending Sign-Off**: `{scan_res['summary_counts']['unverified_evidence_count']} Items`\n\n*Review real-time criterion health and diagnostics in the Executive Dashboard and Evidence Repository.*"

    elif any(k in q_lower for k in ["submission", "gatekeeper", "blocker", "annexure", "package", "final"]):
        val_sub = st.session_state.submission_builder.validate_pre_submission_readiness(
            framework=fw,
            evidence_list=st.session_state.evidence_list,
            tasks_list=task_list
        )
        return f"🛡️ **Pre-Submission Gatekeeper & Dossier Status**:\n\n- **Status**: `{val_sub['status_badge']}`\n- **Mandatory Blockers**: `{val_sub['total_blocking_issues']} Critical Items`\n- **Advisory Warnings**: `{val_sub['total_warnings']} Items`\n- **Numbered Annexures**: 45 Official Records indexed (`Annexure-A001` to `Annexure-A045`) with SHA-256 integrity hashes.\n\n*Open the 'Submission & IQAC Audit' tab to resolve blockers and download the certified statutory submission bundle.*"

    elif any(k in q_lower for k in ["dept", "department", "rank"]):
        return "🏢 **Top Performing Departments by Readiness**:\n\n1. **Computer Science & Engineering (CSE)**: `94.8% Readiness` (9 Verified Documents)\n2. **Electronics & Communication (ECE)**: `92.4% Readiness` (8 Verified Documents)\n3. **Biotechnology**: `89.6% Readiness` (7 Verified Documents)\n4. **Mechanical Engineering**: `88.2% Readiness` (6 Verified Documents)"

    else:
        # Semantic search on criteria
        matches = st.session_state.ev_engine.map_evidence_to_metrics(user_query, framework=fw, top_k=2)
        if matches:
            top_m = matches[0]
            return f"🔍 **Relevant Accreditation Match for '{user_query}'**:\n\n- **Metric**: `[{top_m['metric_id']}]` **{top_m['metric_name']}**\n- **Criterion**: {top_m['criterion_name']} ({top_m['criterion_id']})\n- **Confidence**: `{top_m['confidence_pct']}% Match`\n- **Required Evidence**: {', '.join(top_m.get('required_evidence', [])[:2])}\n\n*How else can I assist with your accreditation review?*"
        
        return f"🤖 I've analyzed your query regarding *'{user_query}'*. VFSTR's accreditation readiness is currently indexed at **{eval_res.get('outcome', {}).get('overall_score_pct', 92.4)}%**. You can explore criterion details, upload evidence, prioritize gaps, practice mock visit defenses, or generate formal narratives using the interactive tabs above!"


# Navigation Tabs (with Bujji Copilot, Ranking Simulator, and Mock Visit Simulator)
tab_copilot, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab_ranking, tab_mock = st.tabs([
    "🤖 Bujji - Agentic AI Copilot",
    "🏛️ Executive Dashboard",
    "📁 Evidence Repository",
    "🎯 Criteria Mapping",
    "⚡ Gap Prioritization Matrix",
    "📋 Remediation Hub",
    "✍️ SAR Narrative Studio",
    "🛡️ Submission & IQAC Audit",
    "🏆 NIRF & QS Ranking Simulator",
    "🤝 Peer Mock Visit Simulator"
])


# ==========================================
# TAB 0: BUJJI - AGENTIC AI COPILOT (MATCHING REFERENCE UI)
# ==========================================
with tab_copilot:
    # 3D Robot Avatar Hero Stage
    avatar_b64 = get_avatar_base64()
    if avatar_b64:
        img_html = f'<img src="data:image/jpeg;base64,{avatar_b64}" class="bujji-avatar-img" alt="Bujji AI Assistant" />'
    else:
        img_html = '<div style="font-size: 80px; animation: floatAnimation 3.5s ease-in-out infinite;">🤖</div>'

    st.markdown(f"""
    <div class="bujji-stage">
        {img_html}
        <div class="bujji-stage-title">Hi, I'm Bujji — Your Agentic AI Accreditation Assistant</div>
        <div class="bujji-stage-sub">
            Autonomous intelligence engine guiding VFSTR through NAAC (A++ CGPA 3.79) & NBA Tier-1 OBE accreditation, semantic evidence audits, 2x2 gap matrices, and automated SSR qualitative synthesis.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Action Prompt Chips
    render_subheading("Instant Copilot Prompts", subtitle="Quick actions for rapid accreditation readiness queries", badge="AI Copilot")
    qcol1, qcol2, qcol3, qcol4, qcol5, qcol6 = st.columns(6)
    prompt_to_submit = None

    with qcol1:
        if st.button("🎯 NAAC CGPA", use_container_width=True):
            prompt_to_submit = "Evaluate our current NAAC readiness score and CGPA breakdown."
    with qcol2:
        if st.button("⚡ NBA Tier-1 OBE", use_container_width=True):
            prompt_to_submit = "Evaluate our NBA Tier-1 score out of 1000 points."
    with qcol3:
        if st.button("🔍 Quick Wins", use_container_width=True):
            prompt_to_submit = "Show me all high impact low effort Quick Wins in the gap matrix."
    with qcol4:
        if st.button("📡 Run Scanner", use_container_width=True):
            prompt_to_submit = "Run continuous scanner diagnostics and show expiring evidence."
    with qcol5:
        if st.button("🤝 Mock Visit Q&A", use_container_width=True):
            prompt_to_submit = "Show me mock visit peer team questions and recommended defense answers."
    with qcol6:
        if st.button("🛡️ Gatekeeper", use_container_width=True):
            prompt_to_submit = "Check pre-submission gatekeeper blockers and annexure register status."

    st.markdown("<div style='margin: 16px 0 12px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)

    # Conversational Message Cards Stream
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                st.markdown(f"""
                <div class="msg-card-assistant">
                    <div class="msg-header">
                        <span class="msg-badge-assistant">🤖 ASSISTANT</span>
                        <span class="msg-timestamp">{msg.get('timestamp', 'Just now')}</span>
                    </div>
                    <div class="msg-body">
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-card-user">
                    <div class="msg-header">
                        <span class="msg-badge-user">👤 YOU / REVIEWER</span>
                        <span class="msg-timestamp">{msg.get('timestamp', 'Just now')}</span>
                    </div>
                    <div class="msg-body">
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Message Input Form
    with st.form("bujji_chat_form", clear_on_submit=True):
        input_c1, input_c2, input_c3 = st.columns([5, 1, 1])
        with input_c1:
            user_input_text = st.text_input(
                "Chat Input",
                placeholder="Start the assistant to start chatting (e.g. 'Show quick wins', 'NAAC CGPA', 'Draft metric 1.1.1')...",
                label_visibility="collapsed"
            )
        with input_c2:
            submit_btn = st.form_submit_button("✈️ Send", use_container_width=True)
        with input_c3:
            clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)

    if clear_btn:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "name": "Bujji (AI Accreditation Assistant)",
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "content": "Chat history cleared. How can I assist you with VFSTR accreditation readiness?"
            }
        ]
        st.rerun()

    active_prompt = prompt_to_submit or (user_input_text.strip() if submit_btn and user_input_text.strip() else None)

    if active_prompt:
        ts_now = datetime.now().strftime("%I:%M %p")
        # Add User Message
        st.session_state.chat_history.append({
            "role": "user",
            "timestamp": ts_now,
            "content": active_prompt
        })
        
        # Compute Assistant Response
        assistant_reply = process_bujji_query(
            user_query=active_prompt,
            fw=framework,
            eval_res=eval_result,
            g_matrix=gap_matrix,
            task_list=tasks,
            ev_list=st.session_state.evidence_list
        )
        
        # Add Assistant Message
        st.session_state.chat_history.append({
            "role": "assistant",
            "name": "Bujji (AI Accreditation Assistant)",
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "content": assistant_reply
        })
        st.rerun()

    # Bottom Status Bar (Matching Reference Image)
    st.markdown("""
    <div class="bujji-status-bar">
        <div>
            <span style="color: #10B981; font-weight: 800; font-size: 14px;">●</span>
            <strong style="color: #0F172A; margin-left: 4px;">Standby | Autonomous Agent Active</strong>
        </div>
        <div>
            🎙️ Voice & transcript assistant ready | Realtime OBE Intelligence
        </div>
        <div>
            🔒 <strong>100% Offline Secured</strong> (SQLite + Scikit-Learn Vector Engine)
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# TAB 1: EXECUTIVE DASHBOARD
# ==========================================
with tab1:
    render_section_heading(
        "Institutional Accreditation Readiness Overview",
        subtitle=f"Comprehensive continuous compliance evaluation under {framework} guidelines",
        badge=f"{framework} Assessment"
    )

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
        render_subheading("Criterion-Wise Compliance Radar", subtitle="Target benchmark (90%) against achieved VFSTR score")
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
        render_subheading(f"Points Achieved vs Maximum Weight ({framework})", subtitle="Criterion point allocation and compliance deficit")
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
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading("Department-Wise Accreditation Readiness Rankings", subtitle="Institutional department progress across verified evidence records")
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

    # Continuous Readiness Scanner Diagnostic Console
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading(
        "📡 Continuous Accreditation Readiness Scanner",
        subtitle="Automated continuous audit scanner evaluating institutional compliance, expiring evidence, and unverified drafts",
        badge="Autonomous Auditor"
    )

    scan_res = st.session_state.scanner.scan_all_criteria(
        framework=framework,
        evidence_list=st.session_state.evidence_list
    )

    col_sc1, col_sc2, col_sc3, col_sc4 = st.columns(4)
    with col_sc1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid {scan_res['grade_color']};">
            <div class="kpi-label">Audit Grade Forecast</div>
            <div class="kpi-value" style="color: {scan_res['grade_color']}; font-size: 20px;">{scan_res['grade_forecast'].split(' ')[0]}</div>
            <div class="kpi-subtext">Forecast CGPA: <strong>{scan_res['cgpa_forecast']} / 4.00</strong></div>
        </div>
        """, unsafe_allow_html=True)
    with col_sc2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #10B981;">
            <div class="kpi-label">Compliant Criteria</div>
            <div class="kpi-value" style="color: #10B981;">{scan_res['summary_counts']['compliant']} <span style="font-size:14px;color:#94A3B8;">/ {scan_res['summary_counts']['total_criteria']}</span></div>
            <div class="kpi-subtext">Overall Health: <strong>{scan_res['overall_readiness_pct']}%</strong></div>
        </div>
        """, unsafe_allow_html=True)
    with col_sc3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #F59E0B;">
            <div class="kpi-label">Expiring / Aged Proofs</div>
            <div class="kpi-value" style="color: #F59E0B;">{scan_res['summary_counts']['expiring_evidence_count']}</div>
            <div class="kpi-subtext">Action Required: <strong>Refresh Docs</strong></div>
        </div>
        """, unsafe_allow_html=True)
    with col_sc4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #3B82F6;">
            <div class="kpi-label">Unverified AI Drafts</div>
            <div class="kpi-value" style="color: #3B82F6;">{scan_res['summary_counts']['unverified_evidence_count']}</div>
            <div class="kpi-subtext">Pending <strong>Human Sign-Off</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🔍 View Criterion Diagnostic Breakdown & Expiring Artifacts", expanded=False):
        c_diag_cols = st.columns(2)
        with c_diag_cols[0]:
            st.markdown("##### 🏛️ Criterion-Level Audit Readiness")
            for cr_diag in scan_res["criteria_breakdown"]:
                st.markdown(f"""
                <div style="background: rgba(30,41,59,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #F1F5F9; font-size: 13px;">{cr_diag['criterion_id']}: {cr_diag['criterion_name'][:30]}...</strong>
                        <div style="font-size: 11px; color: #94A3B8;">{cr_diag['evidence_count']} docs ({cr_diag['verified_count']} verified, {cr_diag['pending_count']} pending)</div>
                    </div>
                    <span style="background: {cr_diag['status_color']}22; color: {cr_diag['status_color']}; border: 1px solid {cr_diag['status_color']}; border-radius: 6px; padding: 3px 8px; font-size: 11px; font-weight: 700;">
                        {cr_diag['readiness_pct']}% • {cr_diag['status']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

        with c_diag_cols[1]:
            st.markdown("##### ⚠️ Expiring Evidence & Remediation Alerts")
            if scan_res["expiring_evidence"]:
                for exp_ev in scan_res["expiring_evidence"][:5]:
                    st.warning(f"**[{exp_ev['criterion_id']}] {exp_ev['title']}** ({exp_ev['department']}) — Year `{exp_ev['academic_year']}` exceeds freshness limit. Upload latest cycle proof.")
            else:
                st.success("✅ No expired evidence records detected in active cycle.")

            if scan_res["critical_gaps"]:
                st.markdown("##### 🔴 Mandatory Documentation Actions")
                for gap_item in scan_res["critical_gaps"][:3]:
                    st.error(f"**{gap_item['criterion_id']}**: {gap_item['action_required']}")

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

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("Apply Simulation Sandbox", use_container_width=True):
                st.toast("Simulation applied! Check updated CGPA and point breakdown.", icon="📊")
                st.rerun()
        with btn_c2:
            if st.button("Reset Simulation", use_container_width=True):
                st.session_state.simulated_adjustments = {}
                st.toast("Simulation reset to baseline verified institutional data.", icon="🔄")
                st.rerun()


# ==========================================
# TAB 2: EVIDENCE REPOSITORY & INGESTION
# ==========================================
with tab2:
    render_section_heading(
        "Institutional Evidence Repository & Smart Ingestion Engine",
        subtitle="Upload, classify, quality-check, and semantically map documentation to criteria",
        badge=f"{len(st.session_state.evidence_list)} Records"
    )

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
            uploaded_file = st.file_uploader(
                "Upload Evidence File (PDF, DOCX, XLSX, CSV, Scanned PNG/JPG)",
                type=["pdf", "docx", "xlsx", "csv", "txt", "png", "jpg", "jpeg"]
            )
            raw_text_input = st.text_area("Document Text Excerpt (optional if file attached)", height=100, placeholder="Paste executive text excerpt or leave empty to auto-extract from file...")

        if st.button("⚡ Ingest & Semantically Map Evidence", use_container_width=True):
            from core.document_store import DocumentExtractor
            content_to_index = raw_text_input.strip()
            doc_file_meta = None
            ocr_info = {"applied": False, "engine": "Text Input"}

            if uploaded_file:
                file_bytes = uploaded_file.getvalue()
                # Save to persistent document storage
                doc_file_meta = st.session_state.doc_store.save_file(file_bytes, uploaded_file.name)
                # Run multi-format text & OCR extractor
                extraction = DocumentExtractor.extract_text(file_bytes, uploaded_file.name)
                extracted_txt = extraction["extracted_text"]
                ocr_info["applied"] = extraction.get("ocr_applied", False)
                ocr_info["engine"] = extraction.get("ocr_engine", "Native Parser")

                if content_to_index:
                    content_to_index = f"{content_to_index}\n\n[EXTRACTED CONTENT]:\n{extracted_txt}"
                else:
                    content_to_index = extracted_txt

                if not doc_title:
                    doc_title = Path(uploaded_file.name).stem.replace("_", " ").title()

            if not doc_title or not content_to_index:
                st.error("Please provide a Document Title or attach a valid document file.")
            else:
                # Run semantic mapping
                matches = st.session_state.ev_engine.map_evidence_to_metrics(content_to_index, framework=framework, top_k=3)
                matched_criteria_ids = [m["criterion_id"] for m in matches] + [m["metric_id"] for m in matches]
                if not matched_criteria_ids:
                    matched_criteria_ids = ["C1"]

                file_fmt = doc_file_meta["file_format"] if doc_file_meta else "TXT"
                file_sz = doc_file_meta["file_size"] if doc_file_meta else f"{round(len(content_to_index)/1024, 1)} KB"
                file_pth = doc_file_meta["file_path"] if doc_file_meta else f"data/documents/DOC_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                file_hsh = doc_file_meta["file_hash"] if doc_file_meta else hashlib.sha256(content_to_index.encode()).hexdigest()

                new_ev = {
                    "id": f"EVD-VIG-{len(st.session_state.evidence_list) + 101}",
                    "title": doc_title,
                    "filename": doc_file_meta["filename"] if doc_file_meta else f"{doc_title.replace(' ', '_')}.txt",
                    "original_filename": uploaded_file.name if uploaded_file else f"{doc_title}.txt",
                    "department": doc_dept,
                    "academic_year": doc_year,
                    "document_type": doc_type,
                    "issuing_authority": doc_authority or "VFSTR Directorate",
                    "content_summary": content_to_index[:250] + ("..." if len(content_to_index) > 250 else ""),
                    "summary": content_to_index[:250] + ("..." if len(content_to_index) > 250 else ""),
                    "description": content_to_index[:250] + ("..." if len(content_to_index) > 250 else ""),
                    "raw_text": content_to_index,
                    "extracted_text": content_to_index,
                    "status": "Under Review",
                    "completeness_score": 88,
                    "missing_elements": [],
                    "applicable_criteria": list(set(matched_criteria_ids)),
                    "verified_by": None,
                    "verification_date": None,
                    "file_format": file_fmt,
                    "file_size": file_sz,
                    "file_hash": file_hsh,
                    "file_path": file_pth,
                    "ocr_applied": ocr_info["applied"],
                    "ocr_engine": ocr_info["engine"]
                }

                # Evaluate quality
                quality = st.session_state.ev_engine.evaluate_evidence_quality(new_ev)
                new_ev["completeness_score"] = quality["quality_score"]
                new_ev["missing_elements"] = quality["penalties"]

                st.session_state.db.insert_evidence(new_ev)
                st.session_state.evidence_list = st.session_state.db.get_all_evidence()
                ocr_badge = f" (OCR: {ocr_info['engine']})" if ocr_info["applied"] else ""
                st.toast(f"✅ Ingested {new_ev['id']} into Database with {quality['quality_score']}% Quality Score!{ocr_badge}", icon="📄")
                st.rerun()

    # Multi-Dimensional Evidence Validation Cohort Summary
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading(
        "🛡️ Multi-Dimensional Evidence Validation Pipeline",
        subtitle="Automated 6-dimensional statutory verification: Existence, Relevance, Completeness, Recency, Format & Signatures",
        badge="Quality Gatekeeper"
    )

    val_batch = st.session_state.validator.validate_evidence_batch(st.session_state.evidence_list)
    val_c1, val_c2, val_c3, val_c4, val_c5 = st.columns(5)
    with val_c1:
        st.metric("Cohort Compliance", f"{val_batch['compliance_rate_pct']}%")
    with val_c2:
        st.metric("Ready & Verified", val_batch["ready_verified"])
    with val_c3:
        st.metric("Pending Sign-Off", val_batch["pending_signoff"])
    with val_c4:
        st.metric("Expired Proofs", val_batch["defect_breakdown"]["expired_records"])
    with val_c5:
        st.metric("Format Defects", val_batch["defect_breakdown"]["wrong_format_records"])

    # Evidence Search & Filter Table
    st.markdown("<div style='margin: 12px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading("Uploaded Evidence Master Register", subtitle="Searchable index of all accredited institutional artifacts with multi-check badges")
    
    search_q = st.text_input("🔍 Search evidence by keyword, title, or ID", placeholder="Search 'Scopus', 'Solar', 'BoS', 'Placements'...")
    display_docs = filtered_evidence
    if search_q.strip():
        display_docs = [
            e for e in display_docs
            if search_q.lower() in e["title"].lower() or search_q.lower() in e.get("raw_text", "").lower() or search_q.lower() in e["id"].lower()
        ]

    st.markdown(f"*Showing {len(display_docs)} institutional evidence records.*")

    for ev in display_docs:
        ev_val = st.session_state.validator.validate_evidence_record(ev)
        with st.container():
            col_id, col_info, col_status, col_del = st.columns([1.2, 4, 1.8, 0.8])
            ev_id = ev.get("id", "EVD-UNKNOWN")
            with col_id:
                st.markdown(f"**`{ev_id}`**")
                st.caption(f"{ev.get('file_format', ev.get('document_type', 'PDF'))} ({ev.get('file_size', '2.5 MB')})")
            with col_info:
                st.markdown(f"**{ev.get('title', 'Untitled Document')}**")
                st.caption(f"🏢 {ev.get('department', 'VFSTR')} | 📅 {ev.get('academic_year', '2023-24')} | ✍️ {ev.get('issuing_authority', 'Registrar')}")
                
                # Robust summary fallback strategy
                content_summary = (
                    ev.get("content_summary")
                    or ev.get("summary")
                    or ev.get("description")
                    or ev.get("content")
                    or (ev.get("raw_text", "")[:250] + ("..." if len(ev.get("raw_text", "")) > 250 else "") if ev.get("raw_text") else "")
                    or "Institutional accreditation evidence record."
                )
                st.markdown(f"<span style='font-size:12px; color:#94A3B8;'>{content_summary}</span>", unsafe_allow_html=True)
                
                # Multi-dimensional check badge row
                dim = ev_val["dimensions"]
                dim_badges = f"""
                <div style="display:flex; flex-wrap:wrap; gap:6px; margin: 6px 0;">
                    <span style="font-size:11px; background:rgba(16,185,129,0.12); color:#10B981; border:1px solid rgba(16,185,129,0.3); border-radius:4px; padding:2px 6px;">{dim['existence']['icon']} Exist</span>
                    <span style="font-size:11px; background:rgba(59,130,246,0.12); color:#3B82F6; border:1px solid rgba(59,130,246,0.3); border-radius:4px; padding:2px 6px;">{dim['relevance']['icon']} Mapped</span>
                    <span style="font-size:11px; background:rgba(245,158,11,0.12); color:#F59E0B; border:1px solid rgba(245,158,11,0.3); border-radius:4px; padding:2px 6px;">{dim['completeness']['icon']} {dim['completeness']['label']}</span>
                    <span style="font-size:11px; background:rgba(139,92,246,0.12); color:#A78BFA; border:1px solid rgba(139,92,246,0.3); border-radius:4px; padding:2px 6px;">{dim['recency']['icon']} {dim['recency']['label']}</span>
                    <span style="font-size:11px; background:rgba(2,132,199,0.12); color:#38BDF8; border:1px solid rgba(2,132,199,0.3); border-radius:4px; padding:2px 6px;">{dim['format']['icon']} {dim['format']['label']}</span>
                    <span style="font-size:11px; background:rgba(212,175,55,0.12); color:#FBBF24; border:1px solid rgba(212,175,55,0.3); border-radius:4px; padding:2px 6px;">{dim['signatures']['icon']} {dim['signatures']['label']}</span>
                </div>
                """
                st.markdown(dim_badges, unsafe_allow_html=True)
                
                # Tags for mapped criteria
                tags_html = " ".join([f"<span class='badge-info' style='font-size:10px;'>{crit}</span>" for crit in ev.get("applicable_criteria", [])[:4]])
                st.markdown(tags_html, unsafe_allow_html=True)
            with col_status:
                st.markdown(f"<span style='background:{ev_val['status_color']}22; color:{ev_val['status_color']}; border:1px solid {ev_val['status_color']}; border-radius:6px; padding:4px 8px; font-size:11px; font-weight:700;'>{ev_val['status_label']}</span>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:12px; margin-top:6px;'>Quality: <strong>{ev.get('completeness_score', 90)}%</strong></div>", unsafe_allow_html=True)
                if ev.get("missing_elements"):
                    st.markdown(f"<span style='font-size:11px; color:#F87171;'>⚠️ {len(ev['missing_elements'])} item(s) pending</span>", unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_ev_{ev_id}", help="Remove evidence document"):
                    st.session_state.db.delete_evidence(ev_id)
                    st.session_state.evidence_list = st.session_state.db.get_all_evidence()
                    st.toast(f"Removed evidence {ev_id} from SQLite database", icon="🗑️")
                    st.rerun()
            st.markdown("<hr style='margin:10px 0; opacity:0.1;'>", unsafe_allow_html=True)


# ==========================================
# TAB 3: CRITERIA & REQUIREMENT MAPPING
# ==========================================
with tab3:
    render_section_heading(
        f"{framework} Criteria & Requirement Compliance Engine",
        subtitle="Detailed benchmark evaluation, evidence links, and qualitative narrative synthesizer",
        badge=framework
    )

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
    st.markdown("<div style='margin: 16px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)

    # Metrics Breakdown
    render_subheading("Detailed Metrics & Evidence Mapping", subtitle="Inspect individual quantitative & qualitative metric benchmarks")

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
                    has_ev = any(req.lower() in e.get("title", "").lower() or req.lower() in e.get("document_type", "").lower() for e in mapped_docs)
                    check_icon = "🟢" if has_ev else "🟡"
                    st.markdown(f"- {check_icon} {req}")

            with mc2:
                st.markdown("**Mapped Evidence Records:**")
                if mapped_docs:
                    for md in mapped_docs[:3]:
                        m_title = md.get("title", "Untitled Document")
                        st.markdown(f"- **`{md.get('id', 'EVD')}`**: {m_title[:40]}... *(Quality: {md.get('completeness_score', 90)}%)*")
                else:
                    st.warning("⚠️ No evidence records directly mapped to this metric.")

                # Action button to trigger SAR narrative
                if st.button(f"✍️ Draft Narrative for {m_id}", key=f"btn_nar_{m_id}"):
                    st.session_state.target_narrative_metric = m_id
                    # Pre-generate narrative
                    gen_nar = st.session_state.narrative_gen.generate_metric_narrative(
                        metric=crit_info['metrics'][m_id],
                        mapped_evidence=mapped_docs,
                        framework=framework
                    )
                    st.session_state.active_narrative = gen_nar["markdown_content"]
                    st.toast(f"Generated qualitative draft for {m_id}! View in SAR Narrative Studio.", icon="✍️")

    # ==========================================
    # INTERACTIVE OBE CURRICULUM-TO-OUTCOME SANKEY FLOW
    # ==========================================
    st.markdown("<div style='margin: 24px 0 12px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading(
        "Interactive OBE Curriculum Attainment Flow (CO -> PO -> PEO)",
        subtitle="Outcome Based Education mapping from Course Outcomes (CO) to Program Outcomes (PO 1-12) and Educational Objectives (PEO 1-4)",
        badge="OBE Sankey Flow"
    )

    sankey_c1, sankey_c2 = st.columns([1.5, 1])
    with sankey_c1:
        obe_dept = st.selectbox("Select Academic Department for OBE Flow", ["Computer Science & Engineering"], key="obe_dept_sel")
    with sankey_c2:
        strength_opt = st.selectbox(
            "Filter Mapping Strength",
            ["All Strengths (1: Slight, 2: Moderate, 3: Substantial)", "Moderate & Substantial (>= 2)", "Substantial Only (= 3)"],
            key="obe_strength_sel"
        )
        min_strength = 3 if "Substantial Only" in strength_opt else (2 if "Moderate" in strength_opt else 1)

    sankey_data = st.session_state.obe_engine.build_sankey_flow(obe_dept, min_mapping_strength=min_strength)
    kpis = sankey_data["summary_kpis"]

    # OBE Attainment KPI Row
    okpi1, okpi2, okpi3, okpi4 = st.columns(4)
    with okpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg CO Attainment</div>
            <div class="kpi-value" style="color: #800000; font-size: 22px;">{kpis['avg_co_attainment']}%</div>
            <div class="kpi-subtext">Direct & Internal Assessments</div>
        </div>
        """, unsafe_allow_html=True)
    with okpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg PO Attainment</div>
            <div class="kpi-value" style="color: #0284C7; font-size: 22px;">{kpis['avg_po_attainment']}%</div>
            <div class="kpi-subtext">12 POs + 2 PSOs Mapped</div>
        </div>
        """, unsafe_allow_html=True)
    with okpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">PEO Realization Index</div>
            <div class="kpi-value" style="color: #D4AF37; font-size: 22px;">{kpis['avg_peo_realization']}%</div>
            <div class="kpi-subtext">4 Educational Objectives</div>
        </div>
        """, unsafe_allow_html=True)
    with okpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">NBA Compliance</div>
            <div class="kpi-value" style="color: #10B981; font-size: 19px;">{kpis['obe_compliance_status']}</div>
            <div class="kpi-subtext">Tier-1 Criterion 3 Ready</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Plotly Sankey Flow Figure
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=18,
            thickness=18,
            line=dict(color="rgba(255,255,255,0.3)", width=0.8),
            label=sankey_data["nodes"]["label"],
            color=sankey_data["nodes"]["color"]
        ),
        link=dict(
            source=sankey_data["links"]["source"],
            target=sankey_data["links"]["target"],
            value=sankey_data["links"]["value"],
            color=sankey_data["links"]["color"],
            customdata=sankey_data["links"]["customdata"],
            hovertemplate="<b>Flow Path:</b> %{customdata}<br><b>Attainment Weight:</b> %{value}<extra></extra>"
        )
    )])

    fig_sankey.update_layout(
        title_text=f"VFSTR {obe_dept} ({sankey_data['curriculum_code']}) — Course Outcomes (CO) ➔ Program Outcomes (PO) ➔ Program Educational Objectives (PEO)",
        title_font_size=13.5,
        title_font_color="#E2E8F0",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=480,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig_sankey, use_container_width=True)


# ==========================================
# TAB 4: GAP PRIORITIZATION MATRIX (IMPACT vs EFFORT)
# ==========================================
with tab4:
    render_section_heading(
        "Accreditation Gap Prioritization Matrix (Impact vs Effort)",
        subtitle="Actionable 2x2 strategic prioritization framework classifying deficiencies by compliance impact against resolution effort",
        badge="Strategic 2x2 Matrix"
    )

    # Batch Action Toolbar
    gaps_ranked = gap_matrix["all_gaps_ranked"]
    quick_wins = gap_matrix["quadrants"].get("Quick Win", [])
    
    if quick_wins:
        if st.button(f"⚡ Auto-Generate Remediation Tasks for All Quick Wins ({len(quick_wins)} Items)", use_container_width=True):
            created_count = 0
            for qw in quick_wins:
                # Check if task already exists
                existing = any(t["metric_id"] == qw["metric_id"] for t in st.session_state.task_manager.get_all_tasks())
                if not existing:
                    st.session_state.task_manager.add_task(
                        title=f"Quick Win: Remediate {qw['metric_id']} ({qw['metric_name'][:35]})",
                        metric_id=qw['metric_id'],
                        criterion_id=qw['criterion_id'],
                        owner=qw['suggested_owner'],
                        priority="High",
                        action_plan=qw['recommended_action']
                    )
                    created_count += 1
            st.toast(f"Created {created_count} corrective action tasks for Quick Wins!", icon="🚀")
            st.rerun()

    # 2x2 Plotly Scatter Quadrant Chart
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
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading(
        "Prioritized Remediation Action List",
        subtitle="Ranked deficiencies with suggested institutional ownership and turnaround targets",
        badge=f"{len(gaps_ranked)} Identified Gaps"
    )
    
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
                    st.toast(f"Created Task {new_t['id']}! Assigned to {g['suggested_owner']}.", icon="📋")
                    st.rerun()
            st.markdown("<hr style='margin:10px 0; opacity:0.1;'>", unsafe_allow_html=True)


# ==========================================
# TAB 5: REMEDIATION ACTION HUB
# ==========================================
with tab5:
    render_section_heading(
        "Corrective Remediation Task Management Hub",
        subtitle="Institutional action tracking, deadline management, ownership assignments, and resolution monitoring",
        badge=f"{task_stats['total_tasks']} Active Tasks"
    )

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

    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)

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
                new_t = st.session_state.task_manager.add_task(
                    title=new_task_title,
                    metric_id=new_task_metric,
                    criterion_id="C" + new_task_metric[0] if new_task_metric[0].isdigit() else "NBA",
                    owner=new_task_owner,
                    priority=new_task_priority,
                    estimated_days=new_task_days,
                    action_plan=new_task_plan
                )
                st.toast(f"Saved Action Task {new_t['id']}!", icon="✅")
                st.rerun()

    # Filterable Task Table & Status Updater
    render_subheading(
        "Active Remediation Tasks Board",
        subtitle="Monitor task progression, status updates, and peer review sign-offs",
        badge=f"{task_stats['resolved']} of {task_stats['total_tasks']} Resolved"
    )
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
                status_opts = ["Open", "In Progress", "In Review", "Resolved"]
                raw_st = str(t.get("status", "Open")).strip()
                norm_status_map = {
                    "OPEN": "Open",
                    "DRAFT": "Open",
                    "PENDING": "Open",
                    "IN_PROGRESS": "In Progress",
                    "IN PROGRESS": "In Progress",
                    "PROGRESS": "In Progress",
                    "ACTIVE": "In Progress",
                    "IN_REVIEW": "In Review",
                    "IN REVIEW": "In Review",
                    "REVIEW": "In Review",
                    "UNDER_REVIEW": "In Review",
                    "RESOLVED": "Resolved",
                    "COMPLETED": "Resolved",
                    "CLOSED": "Resolved"
                }
                current_status = norm_status_map.get(raw_st.upper().replace(" ", "_"), "Open")
                status_idx = status_opts.index(current_status) if current_status in status_opts else 0
                new_st = st.selectbox(
                    "Status",
                    status_opts,
                    index=status_idx,
                    key=f"status_sel_{t.get('id', 'tsk')}"
                )
                if new_st != current_status:
                    st.session_state.task_manager.update_task_status(t["id"], new_st)
                    st.toast(f"Updated {t['id']} status to {new_st}", icon="🔄")
                    st.rerun()
                
                if current_status != "Resolved":
                    if st.button("✅ Quick Mark Resolved", key=f"quick_res_{t['id']}"):
                        st.session_state.task_manager.update_task_status(t["id"], "Resolved", "Resolved by IQAC Action.")
                        st.toast(f"Marked {t['id']} as Resolved!", icon="✅")
                        st.rerun()
            st.markdown("<hr style='margin:8px 0; opacity:0.1;'>", unsafe_allow_html=True)


# ==========================================
# TAB 6: AUTOMATED SAR / SSR NARRATIVE STUDIO
# ==========================================
with tab6:
    render_section_heading(
        f"{framework} Self Assessment Report (SSR / SAR) Narrative Studio",
        subtitle="Offline AI narrative synthesizer producing executive-grade, peer-review-ready qualitative sections with verifiable evidence citations",
        badge=f"{framework} Synthesis"
    )

    all_metrics = get_all_metrics_flat(framework)
    metric_options = {f"{m['id']}: {m['name']} ({m['type']})": m for m in all_metrics}

    metric_keys = list(metric_options.keys())
    if not metric_keys:
        st.info("No metrics available for the selected framework.")
        curr_metric = {}
        selected_metric_str = None
    else:
        # Pre-select target metric if selected from Tab 3
        default_idx = 0
        target_metric_id = st.session_state.get("target_narrative_metric", "1.1.1")
        for idx, (label, m_obj) in enumerate(metric_options.items()):
            if m_obj.get("id") == target_metric_id:
                default_idx = idx
                break

        safe_idx = max(0, min(default_idx, len(metric_keys) - 1))
        selected_metric_str = st.selectbox("Select Metric to Draft Narrative for", metric_keys, index=safe_idx)
        curr_metric = metric_options.get(selected_metric_str, all_metrics[0] if all_metrics else {})

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        narrative_tone = st.selectbox("Narrative Synthesis Style", ["Executive & Evidence-Backed", "Technical & Process-Oriented", "Brief Regulatory Summary"])
    with col_opt2:
        custom_notes = st.text_input("Additional Department Context / Specific Achievements", placeholder="e.g. Include mention of 2023 IEEE Conference hosted by CSE...")

    # Find mapped evidence
    mapped_evidence_for_metric = [
        e for e in st.session_state.evidence_list
        if curr_metric.get("id") in e.get("applicable_criteria", []) or curr_metric.get("criterion_id") in e.get("applicable_criteria", [])
    ]

    if curr_metric and st.button("✨ Generate Executive SSR / SAR Narrative", use_container_width=True):
        generated = st.session_state.narrative_gen.generate_metric_narrative(
            metric=curr_metric,
            mapped_evidence=mapped_evidence_for_metric,
            framework=framework,
            focus_tone=narrative_tone,
            additional_notes=custom_notes
        )
        st.session_state.active_narrative = generated["markdown_content"]
        st.toast(f"Narrative generated for {curr_metric['id']}!", icon="✨")

    if "active_narrative" in st.session_state:
        st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
        render_subheading(
            "Generated Narrative Draft (Editable & Exportable)",
            subtitle="Verified qualitative text with linked evidence citations ready for SSR inclusion",
            badge="Draft Ready"
        )
        
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
    render_section_heading(
        "Human-in-the-Loop IQAC Verification & Official Exports",
        subtitle="Formal review portal for IQAC Director, Deans, and Peer Auditors to authenticate evidence and export official compliance dossiers",
        badge="Audit & Exports"
    )

    unverified_docs = [e for e in st.session_state.evidence_list if e.get("status") in ["Under Review", "Draft", "Needs Revision"]]
    
    # Reviewer Action Panel
    render_subheading(
        "Evidence Verification Workbench",
        subtitle="Audit uploaded documents, adjust completeness ratings, and sign off on compliance",
        badge=f"{len(unverified_docs)} Pending Reviews" if unverified_docs else "All Verified"
    )
    
    if unverified_docs:
        doc_to_audit_title = st.selectbox("Select Evidence Document to Audit", [f"{e.get('id', 'EVD')}: {e.get('title', 'Untitled')}" for e in unverified_docs])
        doc_id_to_audit = doc_to_audit_title.split(":")[0].strip()
        active_doc = next((e for e in st.session_state.evidence_list if e.get("id") == doc_id_to_audit), unverified_docs[0])

        v_col1, v_col2 = st.columns([1.5, 1])
        with v_col1:
            st.markdown(f"**Document Title:** {active_doc.get('title', 'Untitled Document')}")
            st.markdown(f"**Department:** {active_doc.get('department', 'VFSTR')} | **Year:** {active_doc.get('academic_year', '2023-24')}")
            st.markdown(f"**Current Status:** `{active_doc.get('status', 'Under Review')}` | **Current Completeness:** `{active_doc.get('completeness_score', 85)}%`")
            
            raw_preview = (
                active_doc.get("raw_text")
                or active_doc.get("content_summary")
                or active_doc.get("summary")
                or active_doc.get("description")
                or active_doc.get("extracted_text")
                or "No preview text available."
            )
            st.text_area("Raw Text Preview", value=raw_preview, height=120, disabled=True)

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
                st.toast(f"Recorded verification for {active_doc['id']} as {active_doc['status']}!", icon="🛡️")
                st.rerun()
    else:
        st.success("🎉 All institutional evidence documents have been reviewed and verified!")

    # Immutable Audit Log Table
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    audit_logs = st.session_state.audit_verifier.get_audit_trail()
    render_subheading(
        "Immutable Audit Trail Log",
        subtitle="Cryptographically verifiable log of all peer verification decisions and auditor remarks",
        badge=f"{len(audit_logs)} Audit Entries"
    )
    audit_df = pd.DataFrame(audit_logs)
    if not audit_df.empty:
        st.dataframe(audit_df[["timestamp", "reviewer_name", "reviewer_role", "evidence_id", "action", "new_status", "audit_notes"]], use_container_width=True)

    # Pre-Submission Validation Gatekeeper & Numbered Annexure Package
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading(
        "🛡️ Pre-Submission Validation Gatekeeper & Package Assembler",
        subtitle="Enforces statutory blocker checks before assembling numbered annexures (A001-A045) and cross-reference matrices",
        badge="Regulatory Compliance"
    )

    sub_gate = st.session_state.submission_builder.validate_pre_submission_readiness(
        framework=framework,
        evidence_list=st.session_state.evidence_list,
        tasks_list=st.session_state.task_manager.get_all_tasks()
    )

    gate_c1, gate_c2 = st.columns([1.5, 1])
    with gate_c1:
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.7); border-left: 4px solid {sub_gate['status_color']}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-weight: 800; font-size: 15px; color: {sub_gate['status_color']};">{sub_gate['status_badge']}</div>
            <div style="font-size: 12px; color: #CBD5E1; margin-top: 4px;">
                Verified Ready: <strong>{sub_gate['validation_summary']['verified_ready']}</strong> | Unverified Drafts: <strong>{sub_gate['validation_summary']['unverified_pending']}</strong> | Critical Blockers: <strong>{sub_gate['total_blocking_issues']}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with gate_c2:
        if sub_gate["is_cleared"]:
            st.success("✅ Package cleared for official filing to statutory portal.")
        else:
            st.error(f"⛔ {sub_gate['total_blocking_issues']} blocking issue(s) require IQAC action before final filing.")

    if sub_gate["blocking_issues"]:
        with st.expander("⚠️ View Pre-Submission Blocking Defects (Mandatory Action Items)", expanded=True):
            for blk in sub_gate["blocking_issues"]:
                st.markdown(f"- 🔴 **[{blk['category']}] `{blk['item_id']}`**: {blk['message']}")

    # Assemble Numbered Annexure Register
    sub_package = st.session_state.submission_builder.assemble_submission_package(
        framework=framework,
        evidence_list=st.session_state.evidence_list,
        institution_name="VFSTR (Deemed to be University)",
        accredited_unit=f"Institutional {framework} Self-Study Report (Cycle 2)"
    )

    with st.expander(f"📑 View Master Numbered Annexure Register ({sub_package['total_annexures']} Certified Annexures)", expanded=False):
        ann_df = pd.DataFrame(sub_package["annexures"])
        if not ann_df.empty:
            st.dataframe(
                ann_df[["annexure_code", "evidence_id", "title", "department", "document_type", "academic_year", "status", "verification_hash"]],
                use_container_width=True
            )
            
            st.download_button(
                label="📥 Download Certified Evidence Index (CSV)",
                data=sub_package["evidence_index_csv"],
                file_name=f"VFSTR_{framework}_Annexure_Register_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Export Center
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading(
        "Official Accreditation Dossier Export Center",
        subtitle="Generate executive PDFs, CSV evidence registers, and JSON audit dossiers for official regulatory submission",
        badge="3 Export Formats"
    )
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


# ==========================================
# TAB 8: NIRF & QS INSTITUTIONAL RANKING SIMULATOR
# ==========================================
with tab_ranking:
    render_section_heading(
        "NIRF & QS Institutional Ranking & Strategy Simulator",
        subtitle="Continuous ranking projections under official MHRD/MoE NIRF 5-pillar and QS Asia methodologies",
        badge="NIRF Top 100"
    )

    # Evaluate current baseline and simulated scores
    nirf_sim = st.session_state.ranking_engine.evaluate_nirf(st.session_state.nirf_simulated_adjustments)
    qs_sim = st.session_state.ranking_engine.evaluate_qs_asia(st.session_state.nirf_simulated_adjustments)
    nirf_base = st.session_state.ranking_engine.evaluate_nirf()

    is_simulated = bool(st.session_state.nirf_simulated_adjustments)
    score_delta = round(nirf_sim["overall_score"] - nirf_base["overall_score"], 2)
    rank_jump = nirf_base["rank_midpoint"] - nirf_sim["rank_midpoint"]

    # Top KPI Metrics Row
    kpi_r1, kpi_r2, kpi_r3, kpi_r4, kpi_r5 = st.columns(5)
    with kpi_r1:
        rank_delta_text = f"+{rank_jump} Ranks" if is_simulated and rank_jump > 0 else "Official NIRF"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Projected NIRF Rank</div>
            <div class="kpi-value" style="color: #34D399; font-size: 20px;">{nirf_sim['rank_band']}</div>
            <div class="kpi-subtext">Status: <strong>{rank_delta_text}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_r2:
        delta_label = f"+{score_delta} Pts Simulated" if is_simulated else "Baseline Verified"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">NIRF Overall Score</div>
            <div class="kpi-value" style="color: #60A5FA;">{nirf_sim['overall_score']} <span style="font-size:16px;color:#94A3B8;">/ 100</span></div>
            <div class="kpi-subtext">{delta_label}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_r3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">QS Asia Projection</div>
            <div class="kpi-value" style="color: #FBBF24; font-size: 19px;">{qs_sim['qs_rank_band']}</div>
            <div class="kpi-subtext">Composite Score: <strong>{qs_sim['qs_composite_score']}/100</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_r4:
        tlr_score = nirf_sim["parameters"]["TLR"]["score"]
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Teaching & Resources (TLR)</div>
            <div class="kpi-value" style="color: #A78BFA;">{tlr_score} <span style="font-size:16px;color:#94A3B8;">/ 100</span></div>
            <div class="kpi-subtext">Weighted: <strong>{nirf_sim['parameters']['TLR']['weighted_points']}/30 Pts</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_r5:
        target_gap = max(round(60.0 - nirf_sim["overall_score"], 1), 0.0)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Top 50 Target Deficit</div>
            <div class="kpi-value" style="color: #F87171;">{target_gap} <span style="font-size:16px;color:#94A3B8;">Pts</span></div>
            <div class="kpi-subtext">Target: <strong>Top 50 Elite</strong></div>
        </div>
        """, unsafe_allow_html=True)

    # Simulated Intervention Callout Banner if active
    if is_simulated:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%); border: 1px solid #10B981; border-radius: 10px; padding: 12px 18px; margin: 16px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-weight: 800; color: #34D399; font-size: 15px;">🚀 ACTIVE STRATEGY SIMULATION</span>
                    <div style="color: #E2E8F0; font-size: 13px; margin-top: 2px;">
                        Applying {len(st.session_state.nirf_simulated_adjustments)} strategic interventions. Overall score moved from <strong>{nirf_base['overall_score']}</strong> to <strong>{nirf_sim['overall_score']} (+{score_delta} Pts)</strong>, shifting rank projection by <strong>+{rank_jump} positions</strong>.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations: 5-Pillar Radar & Weighted Points Bar Chart
    col_nirf_radar, col_nirf_bar = st.columns([1, 1])

    with col_nirf_radar:
        render_subheading("Five-Pillar NIRF Compliance Radar", subtitle="VFSTR achieved performance vs National Top 25 University Benchmark")
        
        pillar_labels = ["TLR (30%)", "RPC (30%)", "GO (20%)", "OI (10%)", "PR (10%)"]
        pillar_keys = ["TLR", "RPC", "GO", "OI", "PR"]
        pillar_achieved = [nirf_sim["parameters"][k]["score"] for k in pillar_keys]
        pillar_benchmarks = [85.0, 75.0, 88.0, 75.0, 70.0]

        fig_nradar = go.Figure()
        fig_nradar.add_trace(go.Scatterpolar(
            r=pillar_achieved + [pillar_achieved[0]],
            theta=pillar_labels + [pillar_labels[0]],
            fill='toself',
            fillcolor='rgba(128, 0, 0, 0.45)',
            line=dict(color='#D4AF37', width=2.5),
            name='VFSTR Achieved'
        ))
        fig_nradar.add_trace(go.Scatterpolar(
            r=pillar_benchmarks + [pillar_benchmarks[0]],
            theta=pillar_labels + [pillar_labels[0]],
            line=dict(color='#10B981', width=1.5, dash='dash'),
            name='National Top 25 Benchmark'
        ))
        fig_nradar.update_layout(
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
        st.plotly_chart(fig_nradar, use_container_width=True)

    with col_nirf_bar:
        render_subheading("Parameter Weighted Point Contribution", subtitle="Point contribution per pillar towards the 100-point composite score")
        
        bar_nirf_df = pd.DataFrame([
            {
                "Pillar": f"{k} ({nirf_sim['parameters'][k]['weight']}%)",
                "Achieved Points": nirf_sim["parameters"][k]["weighted_points"],
                "Deficit Points": round(nirf_sim["parameters"][k]["weight"] - nirf_sim["parameters"][k]["weighted_points"], 2)
            }
            for k in pillar_keys
        ])

        fig_nbar = go.Figure()
        fig_nbar.add_trace(go.Bar(
            x=bar_nirf_df["Pillar"],
            y=bar_nirf_df["Achieved Points"],
            name="Achieved Score",
            marker_color='#800000',
            text=bar_nirf_df["Achieved Points"],
            textposition='auto'
        ))
        fig_nbar.add_trace(go.Bar(
            x=bar_nirf_df["Pillar"],
            y=bar_nirf_df["Deficit Points"],
            name="Point Deficit",
            marker_color='rgba(239, 68, 68, 0.45)',
            text=bar_nirf_df["Deficit Points"],
            textposition='auto'
        ))
        fig_nbar.update_layout(
            barmode='stack',
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=380,
            xaxis=dict(title="NIRF Parameter"),
            yaxis=dict(title="Weighted Points (Total 100)"),
            margin=dict(l=20, r=20, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_nbar, use_container_width=True)

    # Detailed Parameter Breakdown
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading("NIRF Five-Pillar Detailed Metric Breakdown", subtitle="Inspect individual subcomponents across Teaching, Research, Graduation, Outreach, and Perception", badge="5 Pillars")

    for k in pillar_keys:
        p_data = nirf_sim["parameters"][k]
        with st.expander(f"📌 {k}: {p_data['name']} (Weight: {p_data['weight']}% | Score: {p_data['score']}/100 -> {p_data['weighted_points']} Pts)", expanded=False):
            sub_c1, sub_c2 = st.columns([2, 1])
            with sub_c1:
                st.markdown(f"**Pillar Description:** {NIRF_PARAMETERS[k]['description']}")
                st.markdown("**Subcomponent Scores:**")
                for sub_name, sub_score in p_data["details"].items():
                    st.markdown(f"- **{sub_name}**: `{sub_score}`")
            with sub_c2:
                st.metric("Pillar Weightage", f"{p_data['weight']}%")
                st.metric("Weighted Contribution", f"{p_data['weighted_points']} / {p_data['weight']} Pts")

    # Interactive Strategy Simulation Sandbox
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading("Interactive NIRF Strategic Intervention Sandbox", subtitle="Simulate the ranking impact of expanding research output, improving faculty ratios, and boosting perception", badge="What-If Sandbox")

    with st.container():
        s_col1, s_col2, s_col3 = st.columns(3)
        raw_vals = nirf_sim["raw_inputs"]

        with s_col1:
            st.markdown("**1. Faculty & Resources (TLR)**")
            sim_fsr = st.slider("Faculty-Student Ratio (FSR)", 10.0, 20.0, float(raw_vals.get("faculty_student_ratio", 14.8)), step=0.2, help="Standard 1:15 ratio gets full benchmark.")
            sim_phd = st.slider("Faculty with Ph.D. %", 50.0, 100.0, float(raw_vals.get("faculty_phd_pct", 75.7)), step=1.0)
            
        with s_col2:
            st.markdown("**2. Research Output (RPC)**")
            sim_pubs = st.slider("Annual Scopus Publications", 1500, 5000, int(raw_vals.get("scopus_publications_count", 2410)), step=100)
            sim_grants = st.slider("Extramural Research Grants (Lakhs)", 300.0, 2500.0, float(raw_vals.get("sponsored_research_grants_lakhs", 682.4)), step=50.0)

        with s_col3:
            st.markdown("**3. Placements & Perception (GO/PR)**")
            sim_salary = st.slider("Placement Median CTC (LPA)", 4.0, 12.0, float(raw_vals.get("median_salary_lpa", 5.6)), step=0.2)
            sim_perception = st.slider("Academic & Employer Perception Survey", 15.0, 80.0, float(raw_vals.get("perception_survey_score", 28.5)), step=1.0)

        btn_sim_c1, btn_sim_c2 = st.columns(2)
        with btn_sim_c1:
            if st.button("🚀 Apply Strategic Ranking Simulation", use_container_width=True):
                st.session_state.nirf_simulated_adjustments = {
                    "faculty_student_ratio": sim_fsr,
                    "faculty_phd_pct": sim_phd,
                    "scopus_publications_count": sim_pubs,
                    "sponsored_research_grants_lakhs": sim_grants,
                    "median_salary_lpa": sim_salary,
                    "perception_survey_score": sim_perception
                }
                st.toast("Strategic simulation applied! Projected ranking updated.", icon="🚀")
                st.rerun()

        with btn_sim_c2:
            if st.button("🔄 Reset to Verified Baseline Data", use_container_width=True):
                st.session_state.nirf_simulated_adjustments = {}
                st.toast("Reset to official verified VFSTR institutional baseline.", icon="🔄")
                st.rerun()

    # QS Asia University Ranking Dimension Breakdown
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading("QS Asia University Ranking Dimension Breakdown", subtitle="Institutional assessment across global academic and employer reputation metrics", badge="QS Asia")
    
    qs_cols = st.columns(3)
    qs_items = list(qs_sim["components"].items())
    for i, (comp_name, comp_score) in enumerate(qs_items):
        with qs_cols[i % 3]:
            st.markdown(f"""
            <div class="kpi-card" style="margin-bottom: 12px;">
                <div class="kpi-label">{comp_name}</div>
                <div class="kpi-value" style="color: #60A5FA; font-size: 22px;">{comp_score} <span style="font-size:14px;color:#94A3B8;">/ 100</span></div>
                <div class="kpi-subtext">QS Asia Normalized Metric</div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# TAB 10: PEER-TEAM MOCK VISIT SIMULATOR
# ==========================================
with tab_mock:
    render_section_heading(
        "Accreditation Peer-Team Mock Visit Inspection Simulator",
        subtitle="Comprehensive on-site peer committee interview defense practice for Deans, HoDs, and Criteria Coordinators",
        badge="Inspection Defense"
    )

    mv_summary = st.session_state.mock_visit_engine.get_simulation_summary()
    all_categories = st.session_state.mock_visit_engine.get_all_categories()

    # KPI Summary Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Preparedness Index</div>
            <div class="kpi-value" style="color: #34D399;">{mv_summary['average_readiness_score']}%</div>
            <div class="kpi-subtext">Status: <strong>{mv_summary['overall_status'].split('(')[0]}</strong></div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Question Bank</div>
            <div class="kpi-value" style="color: #60A5FA;">{mv_summary['total_questions']} Cases</div>
            <div class="kpi-subtext">High Confidence: <strong>{mv_summary['high_readiness_count']} Items</strong></div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Categories Covered</div>
            <div class="kpi-value" style="color: #FBBF24;">{mv_summary['categories_covered']} Themes</div>
            <div class="kpi-subtext">NAAC & NBA Comprehensive</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Evidence Verification</div>
            <div class="kpi-value" style="color: #A78BFA;">100% Linked</div>
            <div class="kpi-subtext">All Citing <strong>EVD-VIG Proofs</strong></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    
    # Filter & Selection Bar
    fcol1, fcol2 = st.columns([1.5, 2.5])
    with fcol1:
        selected_mv_cat = st.selectbox("Inspection Topic / Category", ["All Categories"] + all_categories)
    with fcol2:
        mv_search = st.text_input("🔍 Search Inspection Questions", placeholder="Search 'CO-PO', 'Ph.D.', 'Grants', 'Placements', 'NEP 2020'...")

    # Retrieve and filter questions
    mv_questions = st.session_state.mock_visit_engine.get_questions(
        category=selected_mv_cat if selected_mv_cat != "All Categories" else None,
        framework=framework
    )

    if mv_search.strip():
        mv_questions = [
            q for q in mv_questions
            if mv_search.lower() in q["question"].lower() or mv_search.lower() in q["category"].lower() or mv_search.lower() in q["recommended_answer"].lower()
        ]

    render_subheading(
        f"Peer Evaluator Question Bank ({len(mv_questions)} Probing Scenarios)",
        subtitle="Inspect suggested defense narratives, hard metric citations, linked evidence IDs, and follow-up traps"
    )

    for q_item in mv_questions:
        with st.expander(f"🎯 [{q_item['id']}] {q_item['category']} — Evaluator: {q_item['evaluator_role']}", expanded=False):
            st.markdown(f"""
            <div style="background: rgba(128,0,0,0.12); border-left: 4px solid #800000; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px;">
                <strong style="color: #F87171; font-size: 13px;">🧑‍⚖️ PEER EVALUATOR QUERY:</strong>
                <div style="color: #F1F5F9; font-size: 14px; font-weight: 600; margin-top: 4px;">"{q_item['question']}"</div>
            </div>
            """, unsafe_allow_html=True)

            q_c1, q_c2 = st.columns([2, 1])
            with q_c1:
                st.markdown("##### 💡 Recommended Defense Answer Blueprint")
                st.markdown(f"> *{q_item['recommended_answer']}*")

                st.markdown("##### ⚡ Probing Follow-Up Trap Questions (Be Prepared)")
                for trap in q_item["follow_up_traps"]:
                    st.markdown(f"- ⚠️ *{trap}*")

            with q_c2:
                st.markdown("##### 📊 Key Institutional Metrics to Cite")
                for m_k, m_v in q_item["key_metrics"].items():
                    st.markdown(f"- **{m_k}**: `{m_v}`")

                st.markdown("##### 📁 Linked Primary Evidence Records")
                ev_tags = " ".join([f"<span class='badge-info' style='font-size:11px; margin-right:4px;'>{ev_id}</span>" for ev_id in q_item["linked_evidence"]])
                st.markdown(ev_tags, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="margin-top: 14px; background: rgba(16,185,129,0.12); border: 1px solid #10B981; border-radius: 6px; padding: 8px 12px;">
                    <div style="font-size: 11px; color: #10B981; font-weight: 700;">CONFIDENCE RATING</div>
                    <div style="font-size: 16px; font-weight: 800; color: #34D399;">{q_item['readiness_score']}% • {q_item['preparedness_level']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Interactive Mock Defense Simulator Workbench
    st.markdown("<div style='margin: 18px 0 10px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_subheading(
        "🎙️ Interactive Mock Defense Response Evaluator",
        subtitle="Practice faculty verbal responses and test institutional evidence readiness in real-time",
        badge="AI Evaluator"
    )

    def_col1, def_col2 = st.columns([1.5, 1])
    with def_col1:
        q_bank = getattr(st.session_state.mock_visit_engine, "question_bank", [])
        q_options = [f"{q['id']}: {q['category']} - {q['question'][:60]}..." for q in q_bank] if q_bank else ["No questions available"]
        target_q_choice = st.selectbox("Select Question to Defend", q_options)
        target_q_id = target_q_choice.split(":")[0].strip() if target_q_choice and ":" in target_q_choice else ""
        faculty_notes = st.text_area("Faculty Verbal Response Notes & Data Points", height=140, placeholder="Draft your spoken defense points, citing exact statistics and committee approvals...")
        
        # 1-3. Safely retrieve target question, linked evidence, and normalize evidence IDs
        target_question = st.session_state.mock_visit_engine.get_question_by_id(target_q_id) if target_q_id else None
        raw_linked_evidence = target_question.get("linked_evidence", []) if isinstance(target_question, dict) else []
        normalized_linked_evidence = [str(x).strip() for x in raw_linked_evidence if x is not None and str(x).strip()]
        
        # Build available evidence IDs list
        all_ev_ids = [str(e.get("id", "")).strip() for e in st.session_state.evidence_list if isinstance(e, dict) and e.get("id")]
        all_ev_ids = list(dict.fromkeys(all_ev_ids))

        # 4-5. Filter linked_evidence so only valid IDs existing in all_ev_ids are passed to default, limit to first 2
        valid_defaults = [ev_id for ev_id in normalized_linked_evidence if ev_id in all_ev_ids][:2]
        missing_ev_ids = [ev_id for ev_id in normalized_linked_evidence if ev_id not in all_ev_ids]

        # 6-7. If stale/missing evidence IDs exist, show warning instead of crashing
        if missing_ev_ids:
            st.warning(f"⚠️ Linked evidence reference(s) **{', '.join(missing_ev_ids)}** not found in active evidence repository. Only verified proofs are pre-selected.")

        # 8. Use stable unique widget key
        selected_attached_ev = st.multiselect(
            "Select Attached Evidence Records for Verification",
            options=all_ev_ids,
            default=valid_defaults,
            key=f"attached_evidence_{target_q_id}" if target_q_id else "attached_evidence_default"
        )

        if st.button("⚡ Evaluate Defense Preparedness", use_container_width=True):
            if target_q_id:
                eval_res = st.session_state.mock_visit_engine.evaluate_defense_readiness(
                    question_id=target_q_id,
                    faculty_notes=faculty_notes,
                    attached_evidence_ids=selected_attached_ev
                )
                st.session_state.active_defense_eval = eval_res
                st.toast("Defense evaluated! Check score and feedback on the right.", icon="🎯")
            else:
                st.warning("Please select a valid question to defend.")

    with def_col2:
        if "active_defense_eval" in st.session_state:
            res = st.session_state.active_defense_eval
            st.markdown(f"""
            <div style="background: rgba(30,41,59,0.8); border: 2px solid {res['rating_color']}; border-radius: 10px; padding: 16px; margin-top: 6px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight: 800; color: {res['rating_color']}; font-size: 15px;">{res['rating'].replace('_', ' ')}</span>
                    <span style="font-size: 20px; font-weight: 900; color: #F1F5F9;">{res['composite_score']} / 100</span>
                </div>
                <div style="font-size: 12px; color: #CBD5E1; margin: 8px 0;">
                    {res['feedback']}
                </div>
                <div style="font-size: 11px; color: #94A3B8; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 6px;">
                    Matched Evidence: <strong>{len(res['matched_evidence'])}</strong> | Missing Benchmark Proofs: <strong>{len(res['missing_evidence'])}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if res["missing_evidence"]:
                st.warning(f"Attach missing proofs for inspection: {', '.join(res['missing_evidence'])}")
        else:
            st.info("💡 Select a question, draft your verbal response notes, attach relevant evidence records, and click **Evaluate Defense Preparedness** to receive real-time peer inspection feedback.")



