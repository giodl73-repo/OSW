import json
import pathlib

import prepare_nordic_seas_budget as budget


def test_contract_separates_closed_boundary_from_observational_proxy(tmp_path: pathlib.Path) -> None:
    payload = budget.build(tmp_path)
    assert payload["status"] == "contract_frozen_geometry_not_ready"
    assert payload["control_volume"]["boundaries"]["east"]["id"] == "norway_svalbard"
    assert "Fugløya–Bear" in payload["control_volume"]["warning"]
    assert len(payload["control_volume"]["boundaries"]["south"]) == 3
    assert payload["readiness_summary"] == {"pass": 0, "open": 6, "blocked": 2}


def test_repository_contract_has_existing_north_and_east_geometry() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    payload = budget.build(root)
    assert payload["status"] == "offline_partial_budget_ready_public_native_terms_unavailable"
    statuses = {item["id"]: item["status"] for item in payload["readiness"]}
    assert statuses["native_mesh"] == "pass"
    assert statuses["northern_and_eastern_sections"] == "pass"
    assert statuses["southern_sections"] == "pass"
    assert statuses["closed_t_cell_mask"] == "pass"
    assert statuses["full_depth_geometry"] == "pass"
    assert statuses["cell_metrics_and_surface_flux"] == "pass"
    assert statuses["monthly_state"] == "pass"
    assert payload["readiness_summary"] == {"pass": 7, "open": 1, "blocked": 0}
    assert len(payload["available_state_months"]) == 12
    assert payload["sources"]["storage_crosscheck"]["present"]
    assert payload["sources"]["native_budget_availability"]["present"]


def test_committed_contract_matches_builder() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    committed = json.loads((root / "research/osw-m4-nordic-seas-budget-contract.json").read_text(encoding="utf-8"))
    assert committed == budget.build(root)
