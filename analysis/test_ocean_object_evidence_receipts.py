import csv
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "build_ocean_object_evidence_receipts.py"
RECEIPTS = ROOT / "research" / "ocean-object-evidence-receipts.json"


def canonical_text_sha256(path):
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


REGISTRY = ROOT / "research" / "ocean-object-classification.csv"


def load_builder():
    spec = importlib.util.spec_from_file_location("object_receipts", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_evidence_receipt_contract():
    payload = json.loads(RECEIPTS.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw.ocean-object-evidence-receipts.v1"
    assert payload["receipt_count"] == len(payload["receipts"]) == 18
    assert set(payload["vocabularies"]) == {"evidence_origin", "claim_stage", "evidence_status", "identity_result"}

    with REGISTRY.open(encoding="utf-8", newline="") as handle:
        objects = {row["object_id"]: row for row in csv.DictReader(handle)}

    receipt_ids = set()
    results = set()
    for receipt in payload["receipts"]:
        assert receipt["receipt_id"] not in receipt_ids
        receipt_ids.add(receipt["receipt_id"])
        assert receipt["evidence_origin"] in payload["vocabularies"]["evidence_origin"]
        assert receipt["claim_stage"] in payload["vocabularies"]["claim_stage"]
        assert receipt["evidence_status"] in payload["vocabularies"]["evidence_status"]
        assert receipt["supports"] and receipt["does_not_support"]
        assert receipt["next_evidence"] and receipt["boundary"]
        source = ROOT / receipt["source_artifact"]["path"]
        assert source.is_file()
        assert canonical_text_sha256(source) == receipt["source_artifact"]["artifact_sha256"]
        for object_id in receipt["registry_matches"]:
            assert object_id in objects
        for check in receipt["identity_evaluations"]:
            assert check["object_id"] in objects
            assert check["preferred_name"] == objects[check["object_id"]]["preferred_name"]
            assert check["required_identity_test"] == objects[check["object_id"]]["identity_test"]
            assert check["result"] in payload["vocabularies"]["identity_result"]
            results.add(check["result"])

    assert {"pass", "not_tested"} <= results
    assert "marine heatwave" in payload["receipts"][0]["does_not_support"]
    assert "ocean heat content" in payload["receipts"][1]["does_not_support"]
    assert "heat convergence" in payload["receipts"][2]["does_not_support"]
    assert "complete heat budget" in payload["receipts"][3]["does_not_support"]
    assert payload["receipts"][4]["claim_stage"] == "detected_object"
    assert payload["receipts"][4]["identity_evaluations"][0]["result"] == "pass"
    assert payload["receipts"][5]["representation"] == "native_grid_connected_component"
    assert "spatiotemporally tracked footprint" in payload["receipts"][5]["does_not_support"][0]
    assert payload["receipts"][6]["claim_stage"] == "tracked_object"
    assert "2026-08-11" in payload["receipts"][6]["supports"][2]
    assert payload["receipts"][7]["claim_stage"] == "identity_sensitivity"
    assert payload["receipts"][7]["identity_evaluations"][0]["result"] == "policy_dependent"
    assert payload["receipts"][8]["representation"] == "connectivity_by_overlap_policy_matrix"
    assert "four- and eight-neighbor" in payload["receipts"][8]["supports"][0]
    assert "three of 21" in payload["receipts"][8]["supports"][1]
    assert payload["receipts"][9]["representation"] == "branch_selection_policy_bakeoff"
    assert "12-cell splinter" in payload["receipts"][9]["supports"][1]
    assert payload["receipts"][10]["representation"] == "directed_acyclic_component_lineage_graph"
    assert "28-node, 29-edge" in payload["receipts"][10]["supports"][0]
    assert payload["receipts"][11]["representation"] == "anchor_connected_graph_pruning_ladder"
    assert "seven, four, four, two, one, and zero" in payload["receipts"][11]["supports"][1]
    assert payload["receipts"][12]["representation"] == "multi_edge_type_temporal_component_graph"
    assert "35-node, 36-edge" in payload["receipts"][12]["supports"][1]
    assert payload["receipts"][13]["representation"] == "paired_product_fixed_box_surface_temperature_crosscheck"
    assert "0.13 C cooling" in payload["receipts"][13]["supports"][1]
    assert payload["receipts"][14]["representation"] == "partial_surface_temperature_tendency_decomposition"
    assert "13.1%" in payload["receipts"][14]["supports"][1]
    assert payload["receipts"][14]["evidence_origin"] == "operational_assimilative_model"
    assert payload["receipts"][15]["representation"] == "cross_system_mixed_layer_energy_scale_screen"
    assert "+112.61 W/m2" in payload["receipts"][15]["supports"][0]
    assert "native GFS or RTOFS heat-budget closure" in payload["receipts"][15]["does_not_support"]
    assert payload["receipts"][16]["representation"] == "fixed_depth_standard_level_heat_storage_proxy"
    assert "+236.03 W/m2" in payload["receipts"][16]["supports"][1]
    assert payload["receipts"][16]["identity_evaluations"][1]["result"] == "policy_dependent"
    assert payload["receipts"][17]["representation"] == "cross_system_partial_fixed_column_budget_screen"
    assert "+171.21 W/m2" in payload["receipts"][17]["supports"][0]
    assert "native RTOFS tracer flux" in payload["receipts"][17]["does_not_support"]


def test_evidence_receipts_build_is_deterministic(tmp_path):
    builder = load_builder()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    builder.build(first)
    builder.build(second)
    assert first.read_bytes() == second.read_bytes() == RECEIPTS.read_bytes()
