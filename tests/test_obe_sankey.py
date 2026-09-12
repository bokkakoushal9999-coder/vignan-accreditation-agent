"""
Unit & Integration Tests for OBEMappingEngine (Curriculum-to-Outcome Sankey Flow)
"""

import pytest
from core.obe_mapping_engine import OBEMappingEngine, VIGNAN_OBE_DATA


class TestOBEMappingEngine:
    def test_01_obe_data_structure(self):
        """Validates that authentic Vignan OBE dataset contains PEOs, POs, and Course COs."""
        assert "Computer Science & Engineering" in VIGNAN_OBE_DATA
        cse = VIGNAN_OBE_DATA["Computer Science & Engineering"]
        assert len(cse["peos"]) == 4
        assert len(cse["pos"]) >= 12
        assert len(cse["courses"]) >= 4

    def test_02_sankey_nodes_and_links_integrity(self):
        """Validates that Sankey flow generates valid non-empty nodes and in-bound links."""
        engine = OBEMappingEngine()
        flow = engine.build_sankey_flow("Computer Science & Engineering")

        nodes = flow["nodes"]
        links = flow["links"]

        assert len(nodes["label"]) > 0
        assert len(nodes["color"]) == len(nodes["label"])
        assert len(links["source"]) > 0
        assert len(links["target"]) == len(links["source"])
        assert len(links["value"]) == len(links["source"])

        # Check that all link indices refer to valid nodes
        max_node_idx = len(nodes["label"]) - 1
        for s, t in zip(links["source"], links["target"]):
            assert 0 <= s <= max_node_idx
            assert 0 <= t <= max_node_idx
            assert s != t

    def test_03_summary_kpis_calculation(self):
        """Validates average CO, PO, and PEO attainment calculations."""
        engine = OBEMappingEngine()
        flow = engine.build_sankey_flow("Computer Science & Engineering")
        kpis = flow["summary_kpis"]

        assert 70.0 <= kpis["avg_co_attainment"] <= 100.0
        assert 70.0 <= kpis["avg_po_attainment"] <= 100.0
        assert 70.0 <= kpis["avg_peo_realization"] <= 100.0
        assert kpis["total_cos"] > 0
        assert kpis["total_pos"] >= 12
        assert kpis["total_peos"] == 4
        assert "Threshold" in kpis["obe_compliance_status"]

    def test_04_mapping_strength_filter(self):
        """Validates filtering links by minimum mapping strength."""
        engine = OBEMappingEngine()
        flow_all = engine.build_sankey_flow("Computer Science & Engineering", min_mapping_strength=1)
        flow_strong = engine.build_sankey_flow("Computer Science & Engineering", min_mapping_strength=3)

        assert len(flow_strong["links"]["source"]) <= len(flow_all["links"]["source"])
