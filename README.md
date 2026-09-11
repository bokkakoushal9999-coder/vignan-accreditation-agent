# 🏛️ Vignan University AI Accreditation Academic Agent (VFSTR)

An intelligent, enterprise-grade AI Accreditation Academic Agent built specifically for **Vignan's Foundation for Science, Technology & Research (VFSTR - Deemed to be University, Vadlamudi, Guntur, AP)**. 

The platform provides continuous assessment of institutional accreditation readiness across **NAAC** (7 Criteria) and **NBA** (Tier-1 10 OBE Criteria) frameworks using local AI semantic mapping, deterministic compliance scoring, gap impact-effort prioritization, automated Self Assessment Report (SAR/SSR) drafting, and an immutable human-in-the-loop verification audit trail.

---

## 🌟 Key Features & Capabilities

1. **Dual Accreditation Frameworks**:
   - **NAAC (University Manual - 1000 Points)**: Evaluates Criterion 1 through 7 with automatic calculation of CGPA on a 4.00 scale and predicted letter grades (`A++`, `A+`, `A`, `B++`, etc.).
   - **NBA (Tier-1 OBE Manual - 1000 Points)**: Evaluates 10 Outcome-Based Education criteria with 3-year provisional vs 6-year full accreditation status determination.

2. **100% Open-Source & Offline AI Engine (Zero Paid APIs)**:
   - **TF-IDF & Cosine Similarity Semantic Mapping**: Automatically maps uploaded institutional evidence documents to corresponding metrics and criteria.
   - **Quality Heuristics & Incompleteness Detector**: Audits evidence for missing signatures, expired calibration dates, incomplete sample sizes, and authority verification.
   - **What-If Scenario Sandbox**: Interactive simulation sliders to model the impact of recruiting Ph.D. faculty, securing R&D grants, or boosting placement rates.

3. **Gap Prioritization Matrix (Impact vs Effort)**:
   - Evaluates identified compliance deficits on a normalized 1-10 scale.
   - Categorizes gaps into an interactive 2x2 matrix:
     - 🟢 **Quick Wins** (High Impact / Low Effort)
     - 🔵 **Major Strategic Projects** (High Impact / High Effort)
     - 🟡 **Fill-in Tasks** (Low Impact / Low Effort)
     - ⚪ **De-prioritized / Long-term** (Low Impact / High Effort)
   - One-click task generation directly from compliance gaps.

4. **Corrective Remediation Task Hub**:
   - Assigns responsible institutional owners (Dean Academics, Dean R&D, Director IQAC, Dean Placements, Estate Officer, etc.) with milestone deadlines and status tracking (`Open`, `In Progress`, `In Review`, `Resolved`).

5. **Automated SAR / SSR Narrative Studio**:
   - Synthesizes executive qualitative sections for NAAC Self Study Reports (SSR) and NBA Self Assessment Reports (SAR).
   - Injects quantitative KPI summary tables, primary evidence citations, institutional strengths, and continuous improvement roadmaps.
   - Live editable markdown workspace with instant download.

6. **Human-in-the-loop IQAC Verification & Audit Trail**:
   - Official review portal allowing IQAC Directors and Peer Reviewers to inspect evidence, adjust completeness scores, record auditor comments, and transition document states (`Verified`, `Needs Revision`, `Rejected`).
   - Maintains an immutable audit trail with reviewer identity, timestamp, and audit rationale.

7. **Multi-Format Institutional Dossier Export Center**:
   - 📄 **Executive PDF Dossier**: Formal multi-page report with scoring breakdowns, radar summaries, gap rankings, and digital IQAC seals.
   - 📊 **Evidence Master Register (CSV)**: Consolidated institutional evidence catalog.
   - 🛡️ **Audit Trail (JSON)**: Cryptographically verifiable audit log.

8. **Authentic Synthetic Vignan Dataset**:
   - Pre-loaded with 50+ realistic institutional records across engineering, management, basic sciences, IQAC, R&D Cell, T&P cell, and campus infrastructure (2020-2025).

---

## 🚀 Installation & Local Execution

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)

### Installation
```bash
# Clone or navigate to the project directory
cd "accreditation academic agent"

# Install required dependencies
pip install streamlit plotly scikit-learn fpdf2 pandas numpy
```

### Running the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to interact with the Vignan AI Accreditation Agent.

---

## 🧪 Running Unit & Integration Tests
```bash
python -m unittest discover -s tests
```
All tests validate semantic mapping, scoring accuracy, gap prioritization, task management, narrative synthesis, and PDF dossier generation.

---

## 🏛️ Project Directory Structure
```
accreditation academic agent/
├── app.py                      # Main Streamlit web application & UI
├── core/
│   ├── __init__.py
│   ├── criteria_registry.py    # Complete NAAC 7 Criteria & NBA 10 Criteria definitions
│   ├── vignan_demo_data.py     # Authentic synthetic Vignan University evidence records
│   ├── evidence_engine.py      # TF-IDF semantic mapper & incompleteness detector
│   ├── scoring_engine.py       # Deterministic CGPA, Grade & Points calculation
│   ├── gap_matrix_engine.py    # 2x2 Impact vs Effort prioritization engine
│   ├── task_manager.py         # Corrective action task lifecycle manager
│   ├── narrative_generator.py  # Offline SAR/SSR qualitative narrative synthesizer
│   ├── audit_verifier.py       # Human-in-the-loop verification & immutable audit trail
│   └── pdf_exporter.py         # Executive PDF Dossier generator (fpdf2)
├── tests/
│   ├── __init__.py
│   └── test_engines.py         # Unit & integration test suite
└── README.md                   # System documentation & usage guide
```

---

## 🛡️ License
Designed and developed for **Vignan's Foundation for Science, Technology & Research (VFSTR)**. All core algorithms are 100% open-source and run locally without external cloud API dependencies.
