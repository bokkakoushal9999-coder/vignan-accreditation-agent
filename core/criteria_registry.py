"""
Criteria Registry for Accreditation Frameworks:
- NAAC (National Assessment and Accreditation Council - University Manual, 7 Criteria)
- NBA (National Board of Accreditation - Tier-1 Engineering OBE Manual, 10 Criteria)
"""

from typing import Dict, List, Any

# NAAC University Criteria (Total Weightage: 1000)
NAAC_CRITERIA: Dict[str, Dict[str, Any]] = {
    "C1": {
        "id": "C1",
        "name": "Criterion 1: Curricular Aspects",
        "weight": 150,
        "description": "Curriculum design, academic flexibility, curriculum enrichment, and feedback system.",
        "icon": "📚",
        "metrics": {
            "1.1.1": {
                "id": "1.1.1",
                "name": "Curriculum Design & Development with Outcome Based Education (OBE)",
                "type": "QlM",
                "weight": 20,
                "benchmark": 3.8,
                "description": "Curricula developed and implemented have relevance to local, national, regional and global developmental needs with well-defined POs, PSOs and COs.",
                "keywords": ["curriculum", "bos minutes", "obe", "program outcomes", "course outcomes", "bloom taxonomy", "academic council"],
                "required_evidence": ["Board of Studies (BoS) Minutes", "Academic Council Approvals", "PO-PSO-CO Mapping Matrices", "Industry Stakeholder Consultation Reports"]
            },
            "1.1.2": {
                "id": "1.1.2",
                "name": "Percentage of Programs where Syllabus Revision was Carried Out",
                "type": "QnM",
                "weight": 30,
                "benchmark": 85.0,  # % revised in last 5 years
                "description": "Percentage of departments/programs where syllabus revision was carried out during the assessment period.",
                "keywords": ["syllabus revision", "curriculum revision", "credit structure", "elective courses", "emerging technologies"],
                "required_evidence": ["Comparison matrices of old vs new syllabus", "BoS resolutions for revision", "List of newly introduced courses"]
            },
            "1.2.1": {
                "id": "1.2.1",
                "name": "Percentage of New Courses Introduced Across All Programs",
                "type": "QnM",
                "weight": 30,
                "benchmark": 25.0,  # % new courses
                "description": "Percentage of new courses introduced of the total number of courses across all programs during the last five years.",
                "keywords": ["new courses", "course code", "interdisciplinary", "ai ml", "data science", "iot", "biotech advances"],
                "required_evidence": ["Minutes of relevant Academic Council meetings", "Institutional list of new courses introduced", "Syllabus copies with approval dates"]
            },
            "1.3.2": {
                "id": "1.3.2",
                "name": "Value-added Courses Imparting Transferable and Life Skills",
                "type": "QnM",
                "weight": 30,
                "benchmark": 40,  # count of value-added courses
                "description": "Number of value-added courses imparting transferable and life skills offered during the last five years.",
                "keywords": ["value added course", "certificate course", "life skills", "soft skills", "python bootcamp", "industrial automation"],
                "required_evidence": ["Brochures and course content of value-added courses", "Student enrollment and completion certificates", "Attendance sheets"]
            },
            "1.4.1": {
                "id": "1.4.1",
                "name": "Structured Feedback System on Curriculum from All Stakeholders",
                "type": "QnM",
                "weight": 40,
                "benchmark": 95.0,  # % completion
                "description": "Structured feedback on curricula obtained from students, teachers, employers, alumni, and parents with Action Taken Reports (ATR).",
                "keywords": ["stakeholder feedback", "action taken report", "atr", "alumni survey", "employer feedback", "student survey"],
                "required_evidence": ["Stakeholder feedback forms and consolidated analysis", "Action Taken Report (ATR) hosted on university website", "Minutes of Governing Body/IQAC reviewing ATR"]
            }
        }
    },
    "C2": {
        "id": "C2",
        "name": "Criterion 2: Teaching-Learning and Evaluation",
        "weight": 200,
        "description": "Student enrollment, diversity, student-centric methods, teacher quality, and evaluation process.",
        "icon": "🎓",
        "metrics": {
            "2.1.1": {
                "id": "2.1.1",
                "name": "Demand Ratio and Student Enrolment Percentage",
                "type": "QnM",
                "weight": 30,
                "benchmark": 90.0,
                "description": "Average percentage of seats filled against sanctioned intake across all UG and PG programs.",
                "keywords": ["intake", "enrolment", "v-sat admissions", "state quota", "seat matrix", "admission register"],
                "required_evidence": ["Sanctioned intake letters approved by regulatory bodies", "State admission authority allotment lists", "Official admission registers"]
            },
            "2.2.1": {
                "id": "2.2.1",
                "name": "Assessment of Learning Levels & Special Programs for Advanced / Slow Learners",
                "type": "QlM",
                "weight": 25,
                "benchmark": 3.7,
                "description": "Institution assesses learning levels of students after admission and organizes special programs for advanced learners and slow learners.",
                "keywords": ["diagnostic test", "remedial classes", "slow learners", "advanced learners", "peer tutoring", "research fellowships for undergrads"],
                "required_evidence": ["Diagnostic test results and categorization criteria", "Remedial class schedules and attendance", "Advanced learner project competition records"]
            },
            "2.3.1": {
                "id": "2.3.1",
                "name": "Student-Centric Methods (Experiential, Participative & Problem-Solving)",
                "type": "QlM",
                "weight": 35,
                "benchmark": 3.9,
                "description": "Student centric methods such as experiential learning, participative learning and problem solving methodologies are used for enhancing learning experiences.",
                "keywords": ["experiential learning", "participative learning", "project based learning", "flipped classroom", "hackathons", "virtual labs"],
                "required_evidence": ["Project-based learning course reports", "Industrial visit logs and student reports", "LMS usage logs and active learning rubrics"]
            },
            "2.4.2": {
                "id": "2.4.2",
                "name": "Full-Time Faculty with Ph.D. / Highest Degree",
                "type": "QnM",
                "weight": 40,
                "benchmark": 75.0,  # % of faculty with PhD
                "description": "Percentage of full time teachers with Ph.D. / D.Sc. / D.Litt. during the last five years.",
                "keywords": ["faculty phd", "doctorate degrees", "phd certificates", "faculty list", "cadre ratio"],
                "required_evidence": ["Doctoral degree certificates of all full-time faculty", "Faculty appointment orders and joining reports", "IQAC verified faculty master list"]
            },
            "2.5.1": {
                "id": "2.5.1",
                "name": "Continuous Internal Evaluation (CIE) Automation & Transparency",
                "type": "QlM",
                "weight": 35,
                "benchmark": 3.8,
                "description": "Average number of days from the date of last semester-end examination till the declaration of results and automation in evaluation system.",
                "keywords": ["cie", "internal assessment", "exam automation", "erp marks entry", "grievance redressal", "result declaration timeline"],
                "required_evidence": ["Examination manual and standard operating procedures (SOP)", "ERP result declaration logs and timestamps", "Student grievance redressal records for evaluation"]
            },
            "2.6.2": {
                "id": "2.6.2",
                "name": "Attainment of Program Outcomes and Course Outcomes",
                "type": "QnM",
                "weight": 35,
                "benchmark": 80.0,  # % of attainment targets met
                "description": "Attainment of POs and COs evaluated using direct and indirect assessment tools.",
                "keywords": ["co attainment", "po attainment", "direct assessment", "indirect assessment", "course exit survey", "rubrics"],
                "required_evidence": ["Course files with detailed CO-PO attainment calculations", "Program exit survey analytics", "IQAC attainment audit reports"]
            }
        }
    },
    "C3": {
        "id": "C3",
        "name": "Criterion 3: Research, Innovations and Extension",
        "weight": 250,
        "description": "Promotion of research, resource mobilization, innovation ecosystem, publications, and consultancy.",
        "icon": "🔬",
        "metrics": {
            "3.1.1": {
                "id": "3.1.1",
                "name": "Research Facilities & Seed Money Granted to Faculty",
                "type": "QnM",
                "weight": 40,
                "benchmark": 120.0,  # Lakhs INR per year
                "description": "Seed money provided by the institution to its faculty for research during the assessment period.",
                "keywords": ["seed grant", "seed money", "research policy", "sanction letters", "utilization certificates"],
                "required_evidence": ["Institutional research policy document", "Sanction orders of seed money with disbursement proofs", "Audited statements of seed research expenditures"]
            },
            "3.2.1": {
                "id": "3.2.1",
                "name": "Extramural Research Grants from Govt and Non-Govt Agencies",
                "type": "QnM",
                "weight": 50,
                "benchmark": 500.0,  # Lakhs INR per year
                "description": "Total grants received for research projects sponsored by government and non-government agencies.",
                "keywords": ["dst serb", "drdo", "isro", "dbte", "aicte", "sponsored projects", "grant sanction letters"],
                "required_evidence": ["Sanction letters from funding agencies (DST, SERB, ICMR, AICTE, etc.)", "Fund release and bank credit statements", "Project completion and progress reports"]
            },
            "3.3.1": {
                "id": "3.3.1",
                "name": "Innovation Ecosystem, Incubation Centre & Technology Transfer",
                "type": "QlM",
                "weight": 40,
                "benchmark": 3.9,
                "description": "Institution has created an ecosystem for innovations including Incubation centre and other initiatives for creation and transfer of knowledge.",
                "keywords": ["incubation center", "startup", "tbi", "edc", "mou", "technology transfer", "prototypes", "ipr cell"],
                "required_evidence": ["Incubation center registration and facility photographs", "List of incubated startups with revenue/funding records", "Patents commercialized or transferred"]
            },
            "3.4.2": {
                "id": "3.4.2",
                "name": "Patents Published and Granted",
                "type": "QnM",
                "weight": 40,
                "benchmark": 35,  # count
                "description": "Number of patents published / awarded during the assessment period.",
                "keywords": ["patent", "ipr", "indian patent office", "wipo", "patent grant certificate", "patent published"],
                "required_evidence": ["Patent filing application receipts", "Patent publication journals / official gazette copies", "Letters of patent grant issued by patent office"]
            },
            "3.4.5": {
                "id": "3.4.5",
                "name": "Research Papers in Scopus / Web of Science / UGC CARE Indexed Journals",
                "type": "QnM",
                "weight": 50,
                "benchmark": 3.0,  # papers per faculty per year
                "description": "Number of research papers published per teacher in the Journals notified on UGC CARE list / Scopus / Web of Science.",
                "keywords": ["scopus", "web of science", "sci", "ugc care", "h-index", "citations", "doi", "journal publication"],
                "required_evidence": ["Scopus / Web of Science author and institutional extracts", "First page of all indexed publications with university affiliation", "DOI linkage verification table"]
            },
            "3.6.2": {
                "id": "3.6.2",
                "name": "Extension and Outreach Programs in Community / Rural Development",
                "type": "QnM",
                "weight": 30,
                "benchmark": 60,  # programs
                "description": "Number of extension and outreach programs conducted by the institution through NSS/NCC/Red Cross/YRC etc.",
                "keywords": ["nss", "ncc", "unnat bharat abhiyan", "community outreach", "village adoption", "health camps"],
                "required_evidence": ["Detailed event reports with geo-tagged photographs", "Participant attendance lists and certificates", "Appreciation letters from village panchayats / local authorities"]
            }
        }
    },
    "C4": {
        "id": "C4",
        "name": "Criterion 4: Infrastructure and Learning Resources",
        "weight": 100,
        "description": "Physical facilities, library as learning resource, IT infrastructure, and maintenance.",
        "icon": "🏛️",
        "metrics": {
            "4.1.1": {
                "id": "4.1.1",
                "name": "Adequacy of Infrastructure (Smart Classrooms, Labs, Centers of Excellence)",
                "type": "QlM",
                "weight": 25,
                "benchmark": 3.9,
                "description": "The institution has adequate facilities for teaching - learning. viz., classrooms, laboratories, computing equipment, etc.",
                "keywords": ["classrooms", "smart boards", "iot center", "bio-process lab", "supercomputing", "high-end labs"],
                "required_evidence": ["Master layout plan of campus infrastructure", "Geo-tagged photos of laboratories and smart classrooms", "Stock register and asset inventory for major equipment"]
            },
            "4.2.2": {
                "id": "4.2.2",
                "name": "Library Subscriptions (E-Journals, Databases, Shodhganga, E-Books)",
                "type": "QnM",
                "weight": 25,
                "benchmark": 90.0,  # Lakhs INR per year
                "description": "Annual expenditure on purchase of books/e-books and subscription to journals/e-journals.",
                "keywords": ["ieee xplore", "sciencedirect", "springer", "shodhganga", "koha", "delnet", "e-library"],
                "required_evidence": ["Invoices and subscription renewal receipts for IEEE/ScienceDirect", "Remote access usage statistics (INFED/EZproxy)", "Audited statements for library expenditure"]
            },
            "4.3.1": {
                "id": "4.3.1",
                "name": "Bandwidth of Internet Connection & Campus Wi-Fi Coverage",
                "type": "QnM",
                "weight": 25,
                "benchmark": 10.0,  # Gbps leased line
                "description": "Bandwidth of internet connection in the Institution and percentage of campus with high-speed Wi-Fi.",
                "keywords": ["bandwidth", "leased line", "wi-fi 6", "access points", "firewall", "fiber optic backbone"],
                "required_evidence": ["ISP bandwidth contracts and monthly bills (10 Gbps)", "Wi-Fi access point distribution map and network topology diagram", "Firewall and bandwidth utilization reports"]
            },
            "4.4.1": {
                "id": "4.4.1",
                "name": "Budget Allocation for Infrastructure Maintenance & Augmentation",
                "type": "QnM",
                "weight": 25,
                "benchmark": 35.0,  # % of total expenditure excluding salary
                "description": "Average percentage of expenditure incurred on maintenance of physical facilities and academic support facilities.",
                "keywords": ["maintenance budget", "amc", "equipment calibration", "audited balance sheet", "estate office"],
                "required_evidence": ["Audited financial statements with maintenance schedules", "Annual Maintenance Contracts (AMC) for servers, lab machines, power backup", "Standard operating procedures for campus maintenance"]
            }
        }
    },
    "C5": {
        "id": "C5",
        "name": "Criterion 5: Student Support and Progression",
        "weight": 100,
        "description": "Student mentoring, capability enhancement, placements, competitive exams, and alumni engagement.",
        "icon": "🤝",
        "metrics": {
            "5.1.1": {
                "id": "5.1.1",
                "name": "Scholarships and Freeships Provided by Govt and Institution",
                "type": "QnM",
                "weight": 25,
                "benchmark": 65.0,  # % students benefited
                "description": "Percentage of students benefited by scholarships, freeships, etc. provided by the institution and government.",
                "keywords": ["vignan merit scholarship", "jvd fee reimbursement", "fee concessions", "sports scholarship", "economically weak scholarship"],
                "required_evidence": ["Sanction letters of institutional merit scholarships", "Government scholarship disbursement lists", "Audited statements of institutional fee concessions"]
            },
            "5.2.1": {
                "id": "5.2.1",
                "name": "Student Placement and Progression to Higher Education",
                "type": "QnM",
                "weight": 35,
                "benchmark": 85.0,  # % placed or higher studies
                "description": "Percentage of placement of outgoing students and progression to higher education during the last five years.",
                "keywords": ["campus placements", "offer letters", "tcs", "cognizant", "accenture", "amazon", "higher education gate gre"],
                "required_evidence": ["Placement offer letters with CTC details", "List of placed students with employer details", "Admission cards/ID cards for students pursuing higher education"]
            },
            "5.3.1": {
                "id": "5.3.1",
                "name": "Awards / Medals in Sports / Cultural Activities at National / International Level",
                "type": "QnM",
                "weight": 20,
                "benchmark": 40,  # awards
                "description": "Number of awards/medals for outstanding performance in sports/cultural activities at inter-university / state / national / international events.",
                "keywords": ["sports medals", "cultural fest", "mahotsav", "aiu national sports", "youth festival", "trophies"],
                "required_evidence": ["Certificates of merit and medals won", "Official event participation certificates", "Consolidated sports & cultural achievement register"]
            },
            "5.4.1": {
                "id": "5.4.1",
                "name": "Alumni Association Engagement, Chapters & Financial Contributions",
                "type": "QlM",
                "weight": 20,
                "benchmark": 3.8,
                "description": "The Alumni Association is registered and actively contributes to the development of the institution through financial and other support services.",
                "keywords": ["alumni registered", "alumni meet", "guest lectures", "endowments", "mentorship network", "alumni chapters"],
                "required_evidence": ["Alumni association registration certificate", "Audited accounts of alumni financial contributions", "Minutes of alumni annual general body meetings and chapter meets"]
            }
        }
    },
    "C6": {
        "id": "C6",
        "name": "Criterion 6: Governance, Leadership and Management",
        "weight": 100,
        "description": "Institutional vision, strategic plan, decentralization, faculty empowerment, financial management, and IQAC.",
        "icon": "⚖️",
        "metrics": {
            "6.1.1": {
                "id": "6.1.1",
                "name": "Institutional Vision and Leadership in Accordance with NEP 2020",
                "type": "QlM",
                "weight": 20,
                "benchmark": 3.9,
                "description": "The governance and leadership is in accordance with vision and mission of the institution and reflects an effort for continuous improvement.",
                "keywords": ["vision mission", "board of management", "strategic plan 2020-2025", "nep 2020 alignment", "decentralization"],
                "required_evidence": ["Strategic Plan 2020-2025 document with milestones", "Minutes of Board of Management & Academic Council", "Organogram and delegation of administrative/financial powers"]
            },
            "6.2.2": {
                "id": "6.2.2",
                "name": "E-Governance Implementation in Administration, Finance, Admission & Examination",
                "type": "QnM",
                "weight": 20,
                "benchmark": 100.0,  # 5 out of 5 areas covered
                "description": "Implementation of e-governance in areas of operation: Planning & Development, Administration, Finance & Accounts, Student Admission, Examination.",
                "keywords": ["erp system", "vignan portal", "e-governance", "online fees", "lms", "moodle", "examination automation"],
                "required_evidence": ["ERP software license and user subscription agreements", "Screenshots and user access logs for each module", "Annual e-governance audit reports"]
            },
            "6.3.2": {
                "id": "6.3.2",
                "name": "Financial Support to Faculty for Attending Conferences / FDPs",
                "type": "QnM",
                "weight": 20,
                "benchmark": 60.0,  # % of faculty supported
                "description": "Percentage of teachers provided with financial support to attend conferences/workshops and towards membership fee of professional bodies.",
                "keywords": ["travel grant", "fdp registration", "conference reimbursement", "ieee acm membership", "faculty empowerment"],
                "required_evidence": ["Policy for financial assistance to faculty", "Sanction orders and reimbursement vouchers", "Participation certificates of conferences/FDPs"]
            },
            "6.5.1": {
                "id": "6.5.1",
                "name": "Internal Quality Assurance Cell (IQAC) Quality Initiatives & Audits",
                "type": "QlM",
                "weight": 40,
                "benchmark": 4.0,
                "description": "Internal Quality Assurance Cell (IQAC) has contributed significantly for institutionalizing the quality assurance strategies and processes.",
                "keywords": ["iqac minutes", "academic audit", "green audit", "energy audit", "nirf ranking", "quality benchmarks"],
                "required_evidence": ["Minutes of all regular quarterly IQAC meetings with action taken reports", "Annual Quality Assurance Reports (AQAR) submitted to NAAC", "External and internal academic/administrative audit reports"]
            }
        }
    },
    "C7": {
        "id": "C7",
        "name": "Criterion 7: Institutional Values and Best Practices",
        "weight": 100,
        "description": "Gender equity, environmental sustainability, inclusiveness, institutional distinctiveness, and best practices.",
        "icon": "🌱",
        "metrics": {
            "7.1.1": {
                "id": "7.1.1",
                "name": "Measures for the Promotion of Gender Equity and Safety",
                "type": "QlM",
                "weight": 25,
                "benchmark": 3.8,
                "description": "Measures initiated by the Institution for the promotion of gender equity during the last five years.",
                "keywords": ["gender equity", "women empowerment cell", "posh committee", "cctv surveillance", "girls hostel security", "counseling room"],
                "required_evidence": ["Annual gender sensitization action plan", "Reports of gender equity workshops and guest talks", "Photographs and security audit logs of CCTV surveillance & safety facilities"]
            },
            "7.1.2": {
                "id": "7.1.2",
                "name": "Environmental Consciousness, Solar Power & Waste Management",
                "type": "QnM",
                "weight": 25,
                "benchmark": 100.0,  # 5 out of 5 facilities available
                "description": "The Institution has facilities for alternate sources of energy, energy conservation, management of waste, water harvesting, green campus.",
                "keywords": ["solar plant 1mw", "stp water recycling", "sensor based energy", "rainwater harvesting", "biogas", "green audit cert"],
                "required_evidence": ["Solar power plant commissioning certificate & electricity bills", "STP / ETP layout and treated water test reports", "Green, Energy and Environment audit certificates from certified auditors"]
            },
            "7.2.1": {
                "id": "7.2.1",
                "name": "Two Institutional Best Practices Institutionalized",
                "type": "QlM",
                "weight": 25,
                "benchmark": 4.0,
                "description": "Describe two best practices successfully implemented by the Institution as per NAAC format.",
                "keywords": ["best practice", "civil services coaching", "vignan innovation center", "experiential internship", "mentor mentee system"],
                "required_evidence": ["Detailed write-up on Best Practice 1 & 2 in NAAC prescribed format", "Evidence of success and outcome metrics", "Impact evaluation reports and student testimonials"]
            },
            "7.3.1": {
                "id": "7.3.1",
                "name": "Institutional Distinctiveness in Priority Area",
                "type": "QlM",
                "weight": 25,
                "benchmark": 3.9,
                "description": "Portray the performance of the Institution in one area distinctive to its priority and thrust.",
                "keywords": ["distinctiveness", "rural empowerment", "industry immersion", "research driven skilling", "agritech innovation"],
                "required_evidence": ["Comprehensive narrative with verifiable performance metrics", "Media coverage and external awards", "Societal impact assessment report"]
            }
        }
    }
}


# NBA Tier-1 OBE Criteria (Total Points: 1000)
NBA_CRITERIA: Dict[str, Dict[str, Any]] = {
    "NBA-C1": {
        "id": "NBA-C1",
        "name": "Criterion 1: Vision, Mission and PEOs",
        "weight": 50,
        "description": "Vision and Mission of Department, Program Educational Objectives (PEOs), Process for definition and consistency.",
        "icon": "🎯",
        "metrics": {
            "NBA-1.1": {
                "id": "NBA-1.1",
                "name": "State the Vision and Mission of the Department and Institute",
                "type": "QlM",
                "weight": 10,
                "benchmark": 4.0,
                "description": "Availability and dissemination of Vision & Mission among internal and external stakeholders.",
                "keywords": ["vision", "mission", "dissemination", "website", "department corridors", "stakeholder awareness"],
                "required_evidence": ["Published Vision & Mission statements", "Dissemination records (website, handbooks, lab boards)", "Stakeholder awareness survey results"]
            },
            "NBA-1.2": {
                "id": "NBA-1.2",
                "name": "Process of Formulation and Definition of PEOs",
                "type": "QlM",
                "weight": 15,
                "benchmark": 3.8,
                "description": "Articulate the process that establishes the PEOs with stakeholder involvement.",
                "keywords": ["peo formulation", "dab minutes", "pac minutes", "stakeholder consultation", "alumni survey"],
                "required_evidence": ["Department Advisory Board (DAB) minutes", "Program Assessment Committee (PAC) minutes", "Survey instruments and consolidated feedback"]
            },
            "NBA-1.3": {
                "id": "NBA-1.3",
                "name": "Mapping and Consistency of PEOs with Mission of Department",
                "type": "QlM",
                "weight": 25,
                "benchmark": 3.9,
                "description": "Establish the correlation matrix between PEOs and Mission statements with justification.",
                "keywords": ["peo mission matrix", "correlation level", "justification", "attainment tracking"],
                "required_evidence": ["PEO-Mission mapping matrix with detailed justification", "Annual PEO review records"]
            }
        }
    },
    "NBA-C2": {
        "id": "NBA-C2",
        "name": "Criterion 2: Program Curriculum & Teaching-Learning Processes",
        "weight": 100,
        "description": "Curriculum structure, delivery modes, innovative teaching, initiatives for bright & weak students.",
        "icon": "📖",
        "metrics": {
            "NBA-2.1": {
                "id": "NBA-2.1",
                "name": "Program Curriculum Alignment with POs and PSOs",
                "type": "QlM",
                "weight": 30,
                "benchmark": 3.8,
                "description": "Curriculum structure adherence to AICTE model curriculum with adequate balance of BS, ES, PC, PE, OE, Projects.",
                "keywords": ["aicte model curriculum", "credit distribution", "po mapping", "course balance"],
                "required_evidence": ["Curriculum structure document with AICTE comparison", "Course-PO mapping matrix"]
            },
            "NBA-2.2": {
                "id": "NBA-2.2",
                "name": "Teaching-Learning Processes & Innovative Pedagogy",
                "type": "QlM",
                "weight": 40,
                "benchmark": 3.9,
                "description": "Instructional methods, pedagogical initiatives, ICT tools, flipped classrooms, and lab experiments beyond syllabus.",
                "keywords": ["pedagogy", "flipped classroom", "virtual labs", "content beyond syllabus", "project-based learning"],
                "required_evidence": ["Course files with innovative teaching plans", "LMS activity reports", "Laboratory manuals with beyond-syllabus experiments"]
            },
            "NBA-2.3": {
                "id": "NBA-2.3",
                "name": "Continuous Assessment & Quality of Internal Semester Question Papers",
                "type": "QlM",
                "weight": 30,
                "benchmark": 3.7,
                "description": "Process for assessing student work, question paper quality with Bloom's Taxonomy mapping and CO coverage.",
                "keywords": ["blooms taxonomy", "question paper audit", "co coverage", "rubrics", "moderation committee"],
                "required_evidence": ["Internal exam question papers with Bloom's levels marked", "Question paper audit committee minutes", "Evaluation rubrics for lab and projects"]
            }
        }
    },
    "NBA-C3": {
        "id": "NBA-C3",
        "name": "Criterion 3: Course Outcomes (COs) and Program Outcomes (POs)",
        "weight": 175,
        "description": "Attainment of Course Outcomes, Direct & Indirect Attainment of POs and PSOs.",
        "icon": "📊",
        "metrics": {
            "NBA-3.1": {
                "id": "NBA-3.1",
                "name": "Establish the Correlation between the Courses and the POs & PSOs",
                "type": "QlM",
                "weight": 25,
                "benchmark": 3.9,
                "description": "CO-PO/PSO articulation matrix for all courses with defined correlation levels (1: Low, 2: Medium, 3: High).",
                "keywords": ["articulation matrix", "co po mapping", "correlation level", "course syllabus"],
                "required_evidence": ["Course articulation matrices for all courses", "Department consensus workshop minutes"]
            },
            "NBA-3.2": {
                "id": "NBA-3.2",
                "name": "Attainment of Course Outcomes (Direct & Indirect Assessment)",
                "type": "QnM",
                "weight": 50,
                "benchmark": 82.0,
                "description": "Attainment calculation methodologies, target setting, and percentage of courses achieving targets.",
                "keywords": ["co attainment calculation", "direct tool", "indirect tool", "target threshold", "course end survey"],
                "required_evidence": ["CO attainment calculation sheets in course files", "Target revision records for continuous improvement"]
            },
            "NBA-3.3": {
                "id": "NBA-3.3",
                "name": "Attainment of Program Outcomes and Program Specific Outcomes",
                "type": "QnM",
                "weight": 100,
                "benchmark": 80.0,
                "description": "PO and PSO direct attainment from course-level computation plus indirect attainment from exit surveys, alumni and employer surveys.",
                "keywords": ["po attainment summary", "direct 80%", "indirect 20%", "exit survey", "alumni survey", "employer survey"],
                "required_evidence": ["PO/PSO attainment summary for graduating batches", "Indirect assessment survey analysis and raw response sheets"]
            }
        }
    },
    "NBA-C4": {
        "id": "NBA-C4",
        "name": "Criterion 4: Students' Performance",
        "weight": 100,
        "description": "Success rate without backlog, academic performance in 2nd/3rd/4th years, placements and higher studies.",
        "icon": "🌟",
        "metrics": {
            "NBA-4.1": {
                "id": "NBA-4.1",
                "name": "Enrolment Ratio (Sanctioned vs Admitted)",
                "type": "QnM",
                "weight": 20,
                "benchmark": 92.0,
                "description": "Average percentage of students admitted against sanctioned intake over the assessment period.",
                "keywords": ["intake", "enrolment ratio", "first year admissions", "lateral entry"],
                "required_evidence": ["AICTE approval letter for intake", "Admission authority allotment list"]
            },
            "NBA-4.2": {
                "id": "NBA-4.2",
                "name": "Success Rate Without Backlog in Stipulated Period",
                "type": "QnM",
                "weight": 40,
                "benchmark": 75.0,
                "description": "Success index of students completing the degree without backlogs in four years.",
                "keywords": ["success index", "graduation rate", "no backlog", "examination records"],
                "required_evidence": ["Batch graduation data sheets verified by Controller of Examinations"]
            },
            "NBA-4.3": {
                "id": "NBA-4.3",
                "name": "Placement, Higher Studies and Professional Entrepreneurship",
                "type": "QnM",
                "weight": 40,
                "benchmark": 85.0,
                "description": "Placement index combining percentage of students placed in industry, pursuing higher studies, or starting ventures.",
                "keywords": ["placement index", "campus offers", "higher study admit cards", "entrepreneurs"],
                "required_evidence": ["Offer letters with package details", "GATE/CAT/GRE/IELTS admit proofs", "Company incorporation certs"]
            }
        }
    },
    "NBA-C5": {
        "id": "NBA-C5",
        "name": "Criterion 5: Faculty Information and Contributions",
        "weight": 200,
        "description": "Student-Faculty Ratio (SFR), Faculty Cadre Ratio, Faculty Qualification, Retention, and Research.",
        "icon": "👨‍🏫",
        "metrics": {
            "NBA-5.1": {
                "id": "NBA-5.1",
                "name": "Student-Faculty Ratio (SFR)",
                "type": "QnM",
                "weight": 25,
                "benchmark": 15.0,  # 1:15 ratio or better
                "description": "Student to faculty ratio maintained across the program.",
                "keywords": ["sfr", "student faculty ratio", "1:15", "faculty list", "total students"],
                "required_evidence": ["Consolidated faculty list with designation and joining dates", "Student enrollment registers"]
            },
            "NBA-5.2": {
                "id": "NBA-5.2",
                "name": "Faculty Cadre Ratio (Professor : Assoc Prof : Asst Prof)",
                "type": "QnM",
                "weight": 25,
                "benchmark": 90.0,  # Cadre proportion score (1:2:6 target)
                "description": "Cadre ratio compliance with regulatory norms (1 Professor : 2 Assoc Professors : 6 Asst Professors).",
                "keywords": ["cadre ratio", "professors", "associate professors", "assistant professors", "selection committee"],
                "required_evidence": ["Selection committee proceedings and appointment letters"]
            },
            "NBA-5.3": {
                "id": "NBA-5.3",
                "name": "Faculty Qualification (Percentage with Ph.D.)",
                "type": "QnM",
                "weight": 25,
                "benchmark": 75.0,
                "description": "Faculty qualification index based on Ph.D. degree holders.",
                "keywords": ["phd qualification", "doctorate degrees", "faculty qualification index"],
                "required_evidence": ["Ph.D. degree certificates of all departmental faculty"]
            },
            "NBA-5.4": {
                "id": "NBA-5.4",
                "name": "Faculty Retention Rate (Stayed >= 3 Years)",
                "type": "QnM",
                "weight": 25,
                "benchmark": 85.0,
                "description": "Percentage of faculty retained over the last three assessment years.",
                "keywords": ["faculty retention", "service continuity", "joining dates", "experience letters"],
                "required_evidence": ["Service continuity records from Registrar / HR office"]
            },
            "NBA-5.5": {
                "id": "NBA-5.5",
                "name": "Faculty Research Publications, Funded Projects & Consultancy",
                "type": "QnM",
                "weight": 100,
                "benchmark": 85.0,
                "description": "Faculty research publications in SCI/Scopus, sponsored R&D grants, consultancy projects, and IPR.",
                "keywords": ["scopus", "sci", "consultancy", "sponsored research", "patents", "h-index"],
                "required_evidence": ["Scopus author profiles", "Project sanction letters", "Consultancy invoices and bank proofs"]
            }
        }
    },
    "NBA-C6": {
        "id": "NBA-C6",
        "name": "Criterion 6: Facilities and Technical Support",
        "weight": 80,
        "description": "Classrooms, laboratories, computing facilities, language labs, and technical manpower.",
        "icon": "💻",
        "metrics": {
            "NBA-6.1": {
                "id": "NBA-6.1",
                "name": "Adequacy and Maintenance of Laboratories and Equipment",
                "type": "QlM",
                "weight": 40,
                "benchmark": 3.9,
                "description": "Adequacy of well-equipped laboratories, safety measures, calibration, and technical support staff.",
                "keywords": ["laboratories", "equipment list", "lab manuals", "technicians", "safety measures"],
                "required_evidence": ["Laboratory layout and equipment stock register", "Safety audit certificates and first aid logs"]
            },
            "NBA-6.2": {
                "id": "NBA-6.2",
                "name": "Computing Facilities & Licensed Software",
                "type": "QnM",
                "weight": 40,
                "benchmark": 95.0,
                "description": "Student to computer ratio, legal system/application software, and high-speed campus network.",
                "keywords": ["computer ratio", "matlab", "cadence", "ansys", "licensed software", "firewall"],
                "required_evidence": ["Software license procurement invoices", "Lab computing hardware specifications"]
            }
        }
    },
    "NBA-C7": {
        "id": "NBA-C7",
        "name": "Criterion 7: Continuous Improvement",
        "weight": 75,
        "description": "Actions taken on PO/PSO attainment gaps, improvement in academic performance, placements, and faculty quality.",
        "icon": "📈",
        "metrics": {
            "NBA-7.1": {
                "id": "NBA-7.1",
                "name": "Actions Taken Based on Results of Evaluation of Each PO and PSO",
                "type": "QlM",
                "weight": 35,
                "benchmark": 3.8,
                "description": "Identification of PO/PSO attainment gaps and documented corrective action plans with measurable improvement.",
                "keywords": ["continuous improvement", "action taken", "gap mitigation", "pac meetings", "curriculum tweak"],
                "required_evidence": ["PAC closing-the-loop action reports", "Evidence of implemented changes (new assignments, workshops)"]
            },
            "NBA-7.2": {
                "id": "NBA-7.2",
                "name": "Improvement in Academic Performance, Placements & Research",
                "type": "QlM",
                "weight": 40,
                "benchmark": 3.9,
                "description": "Demonstrable year-on-year improvement in student graduation rates, average package, and research output.",
                "keywords": ["yoy improvement", "trend analysis", "placement growth", "publication growth"],
                "required_evidence": ["Comparative 3-year performance analysis charts", "Dean Academic audit validation report"]
            }
        }
    },
    "NBA-C8": {
        "id": "NBA-C8",
        "name": "Criterion 8: First Year Academics",
        "weight": 50,
        "description": "First year student-faculty ratio, faculty qualifications, teaching-learning, and first-year academic results.",
        "icon": "🌱",
        "metrics": {
            "NBA-8.1": {
                "id": "NBA-8.1",
                "name": "First Year Student-Faculty Ratio & Faculty Qualification",
                "type": "QnM",
                "weight": 25,
                "benchmark": 85.0,
                "description": "First year SFR and percentage of basic sciences & humanities faculty with Ph.D.",
                "keywords": ["first year faculty", "basic sciences", "maths", "physics", "chemistry", "english", "sfr"],
                "required_evidence": ["First-year faculty master list with Ph.D. degrees and workload statements"]
            },
            "NBA-8.2": {
                "id": "NBA-8.2",
                "name": "First Year Academic Performance and Pass Percentage",
                "type": "QnM",
                "weight": 25,
                "benchmark": 80.0,
                "description": "Pass percentage and average GPA attained by first-year students.",
                "keywords": ["first year pass percentage", "gpa", "induction program", "bridge courses"],
                "required_evidence": ["First-year examination result gazette", "Bridge course attendance and evaluation logs"]
            }
        }
    },
    "NBA-C9": {
        "id": "NBA-C9",
        "name": "Criterion 9: Student Support Systems",
        "weight": 50,
        "description": "Mentoring system, feedback mechanisms, professional chapters, co-curricular and extra-curricular facilities.",
        "icon": "🛡️",
        "metrics": {
            "NBA-9.1": {
                "id": "NBA-9.1",
                "name": "Mentoring System to Help Students at Individual Level",
                "type": "QlM",
                "weight": 25,
                "benchmark": 3.9,
                "description": "Types of mentoring (professional guidance/career advancement/course work), mentor-mentee ratio, and review records.",
                "keywords": ["mentoring", "mentor mentee ratio 1:20", "counseling diary", "mentoring register"],
                "required_evidence": ["Mentor allotment circulars", "Sample student mentoring logbooks with follow-up remarks"]
            },
            "NBA-9.2": {
                "id": "NBA-9.2",
                "name": "Professional Chapters (IEEE, ACM, CSI, ASME) and Student Clubs",
                "type": "QlM",
                "weight": 25,
                "benchmark": 3.8,
                "description": "Active student professional bodies, technical events, symposiums, and student club activities.",
                "keywords": ["ieee student branch", "acm chapter", "csi", "asme", "hackathons", "technical symposium"],
                "required_evidence": ["Professional chapter establishment letters", "Activity reports with student lists and photographs"]
            }
        }
    },
    "NBA-C10": {
        "id": "NBA-C10",
        "name": "Criterion 10: Governance, Institutional Support & Financial Resources",
        "weight": 120,
        "description": "Organization and governance, budget allocation and utilization, library and internet facilities.",
        "icon": "🏛️",
        "metrics": {
            "NBA-10.1": {
                "id": "NBA-10.1",
                "name": "Organization, Governance and Transparency",
                "type": "QlM",
                "weight": 40,
                "benchmark": 3.9,
                "description": "Governing body composition, service rules, policies, grievance redressal, and anti-ragging committees.",
                "keywords": ["governing body", "service rules", "grievance cell", "anti-ragging committee", "icc"],
                "required_evidence": ["Published service rules and handbook", "Minutes of Governing Body meetings", "Anti-ragging and ICC committee orders"]
            },
            "NBA-10.2": {
                "id": "NBA-10.2",
                "name": "Budget Allocation, Utilization and Financial Audits",
                "type": "QnM",
                "weight": 40,
                "benchmark": 95.0,  # % utilization of allocated budget
                "description": "Adequacy of budget allocation for academic and infrastructure needs and utilization percentage.",
                "keywords": ["budget allocation", "financial utilization", "audited accounts", "finance committee"],
                "required_evidence": ["Finance committee approval minutes", "Audited balance sheets for last 3 financial years"]
            },
            "NBA-10.3": {
                "id": "NBA-10.3",
                "name": "Central Library Facilities and E-Resources",
                "type": "QlM",
                "weight": 40,
                "benchmark": 3.8,
                "description": "Library resources, digital library terminals, automated LMS, subscriptions, and usage statistics.",
                "keywords": ["central library", "digital library", "e-books", "scopus database", "turnitin"],
                "required_evidence": ["Central library floor plan and terminal count", "Subscription list of international journals and databases"]
            }
        }
    }
}


def get_framework_criteria(framework: str = "NAAC") -> Dict[str, Dict[str, Any]]:
    """Returns the criteria dictionary for the selected framework."""
    if framework == "NBA":
        return NBA_CRITERIA
    return NAAC_CRITERIA


def get_all_metrics_flat(framework: str = "NAAC") -> List[Dict[str, Any]]:
    """Returns a flat list of all metrics with their criterion ID."""
    criteria_dict = get_framework_criteria(framework)
    metrics_list = []
    for crit_id, crit_info in criteria_dict.items():
        for metric_id, metric_info in crit_info["metrics"].items():
            item = dict(metric_info)
            item["criterion_id"] = crit_id
            item["criterion_name"] = crit_info["name"]
            metrics_list.append(item)
    return metrics_list
