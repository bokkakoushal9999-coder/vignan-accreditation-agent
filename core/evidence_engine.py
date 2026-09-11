"""
Evidence Engine for Accreditation Analysis:
- Semantic evidence mapping using TF-IDF & Cosine Similarity (Scikit-Learn)
- Missing & incomplete evidence detection
- Evidence quality & validation heuristic assessment
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from core.criteria_registry import get_all_metrics_flat, get_framework_criteria


class EvidenceEngine:
    def __init__(self):
        self._vectorizer = TfidfVectorizer(stop_words='english', max_features=1500, ngram_range=(1, 2))
        self._fitted_framework = None
        self._metric_corpus = []
        self._metric_meta = []
        self._tfidf_matrix = None

    def _build_metric_corpus(self, framework: str = "NAAC"):
        """Builds text corpus of metrics and keywords for TF-IDF semantic indexing."""
        metrics = get_all_metrics_flat(framework)
        corpus = []
        meta = []
        for m in metrics:
            text = f"{m['name']} {m['description']} {' '.join(m.get('keywords', []))} {' '.join(m.get('required_evidence', []))}"
            corpus.append(text)
            meta.append(m)

        self._metric_corpus = corpus
        self._metric_meta = meta
        if corpus:
            self._tfidf_matrix = self._vectorizer.fit_transform(corpus)
            self._fitted_framework = framework

    def map_evidence_to_metrics(
        self,
        evidence_text: str,
        framework: str = "NAAC",
        top_k: int = 3,
        threshold: float = 0.12
    ) -> List[Dict[str, Any]]:
        """
        Semantically maps evidence text to the most relevant accreditation metrics.
        Returns list of matched metrics with confidence score and matching keywords.
        """
        if self._fitted_framework != framework or self._tfidf_matrix is None:
            self._build_metric_corpus(framework)

        if not evidence_text or not self._metric_corpus:
            return []

        doc_vec = self._vectorizer.transform([evidence_text])
        similarities = cosine_similarity(doc_vec, self._tfidf_matrix)[0]

        top_indices = np.argsort(similarities)[::-1]
        matches = []

        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold and len(matches) < top_k:
                metric = self._metric_meta[idx]
                
                # Check keyword overlap for explanation
                ev_lower = evidence_text.lower()
                matched_keywords = [kw for kw in metric.get("keywords", []) if kw.lower() in ev_lower]
                
                matches.append({
                    "metric_id": metric["id"],
                    "metric_name": metric["name"],
                    "criterion_id": metric["criterion_id"],
                    "criterion_name": metric["criterion_name"],
                    "similarity_score": round(score, 4),
                    "confidence_pct": round(min(score * 160, 99.0), 1),
                    "matched_keywords": matched_keywords,
                    "required_evidence": metric.get("required_evidence", [])
                })

        return matches

    def evaluate_evidence_quality(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assesses completeness and quality of an individual evidence artifact.
        Checks for:
        1. Issuing authority & designation
        2. Academic year validity
        3. Detailed description / raw text depth
        4. Official verification status & missing elements
        """
        score = 100
        penalties = []
        recommendations = []

        # Content length check
        raw_text = evidence.get("raw_text", "") or evidence.get("content_summary", "")
        if len(raw_text.split()) < 30:
            score -= 25
            penalties.append("Insufficient text length/summary detail (<30 words)")
            recommendations.append("Provide a more comprehensive excerpt or summary of the institutional document.")

        # Authority check
        authority = evidence.get("issuing_authority", "")
        if not authority or authority.lower() in ["unknown", "n/a", "none"]:
            score -= 15
            penalties.append("Missing or unverified issuing authority")
            recommendations.append("Specify official signing authority (e.g., Dean, HoD, Registrar, Funding Agency).")

        # Academic year check
        year = evidence.get("academic_year", "")
        if not year or year == "Unknown":
            score -= 10
            penalties.append("Missing academic year timestamp")
            recommendations.append("Tag evidence with relevant academic assessment year (e.g. 2023-24).")

        # Existing flagged missing elements
        missing_elems = evidence.get("missing_elements", [])
        if missing_elems:
            score -= len(missing_elems) * 8
            for elem in missing_elems:
                penalties.append(f"Incomplete artifact: {elem}")
                recommendations.append(f"Obtain and attach missing document item: {elem}")

        # Verification status check
        status = evidence.get("status", "Draft")
        if status == "Draft":
            score -= 10
            penalties.append("Document currently in unverified Draft state")
            recommendations.append("Submit for formal IQAC / Peer Review verification.")
        elif status == "Needs Revision":
            score -= 15
            penalties.append("Document flagged as 'Needs Revision' by reviewer")

        final_score = max(min(score, 100), 15)
        
        grade = "Strong"
        if final_score < 60:
            grade = "Deficient"
        elif final_score < 80:
            grade = "Moderate"

        return {
            "quality_score": final_score,
            "quality_grade": grade,
            "penalties": penalties,
            "recommendations": recommendations,
            "is_ready_for_ssr": final_score >= 75
        }

    def detect_missing_evidence(
        self,
        evidence_list: List[Dict[str, Any]],
        framework: str = "NAAC"
    ) -> List[Dict[str, Any]]:
        """
        Audits all metrics in the framework against the evidence store to identify:
        - Completely missing evidence (no documents mapped)
        - Partially covered evidence (mapped documents have quality issues or missing required types)
        - Fully compliant evidence
        """
        criteria_dict = get_framework_criteria(framework)
        metrics_flat = get_all_metrics_flat(framework)
        gaps = []

        for metric in metrics_flat:
            metric_id = metric["id"]
            crit_id = metric["criterion_id"]
            required_types = metric.get("required_evidence", [])

            # Find mapped evidence
            matched_docs = []
            for ev in evidence_list:
                applicable = ev.get("applicable_criteria", [])
                # Direct match or criterion match
                if metric_id in applicable or crit_id in applicable:
                    matched_docs.append(ev)

            # Analyze coverage
            if not matched_docs:
                gaps.append({
                    "framework": framework,
                    "criterion_id": crit_id,
                    "criterion_name": metric["criterion_name"],
                    "metric_id": metric_id,
                    "metric_name": metric["name"],
                    "metric_type": metric["type"],
                    "metric_weight": metric["weight"],
                    "status": "Missing",
                    "severity": "Critical" if metric["weight"] >= 35 else "High",
                    "coverage_score": 0.0,
                    "mapped_docs_count": 0,
                    "mapped_doc_ids": [],
                    "deficiency_reason": f"No institutional evidence uploaded or mapped for metric {metric_id}.",
                    "required_evidence_missing": required_types,
                    "recommended_action": f"Collect and upload {', '.join(required_types[:2])} from concerned department."
                })
            else:
                # Assess completeness of mapped documents
                avg_quality = np.mean([ev.get("completeness_score", 85) for ev in matched_docs])
                missing_items_collected = []
                for ev in matched_docs:
                    missing_items_collected.extend(ev.get("missing_elements", []))

                if avg_quality < 75 or missing_items_collected:
                    severity = "Moderate"
                    if avg_quality < 60 or len(missing_items_collected) > 2:
                        severity = "High"
                    
                    gaps.append({
                        "framework": framework,
                        "criterion_id": crit_id,
                        "criterion_name": metric["criterion_name"],
                        "metric_id": metric_id,
                        "metric_name": metric["name"],
                        "metric_type": metric["type"],
                        "metric_weight": metric["weight"],
                        "status": "Incomplete",
                        "severity": severity,
                        "coverage_score": round(float(avg_quality), 1),
                        "mapped_docs_count": len(matched_docs),
                        "mapped_doc_ids": [d["id"] for d in matched_docs],
                        "deficiency_reason": f"Evidence mapped ({len(matched_docs)} items) contains quality deficiencies or missing signatures/annexures.",
                        "required_evidence_missing": missing_items_collected if missing_items_collected else ["Complete verified signatures / appendix sheets"],
                        "recommended_action": f"Resolve pending items: {'; '.join(missing_items_collected[:2]) if missing_items_collected else 'Perform full verification review'}"
                    })

        return gaps
