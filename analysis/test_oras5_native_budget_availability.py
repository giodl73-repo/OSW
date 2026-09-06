import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_native_budget_availability_receipt_is_explicit() -> None:
    payload = json.loads((ROOT / "research/osw-m4-oras5-native-budget-availability.json").read_text(encoding="utf-8"))
    assert payload["catalog"]["variable_family_count"] == 23
    assert payload["archived_partial_diagnostics"]["total_column_heat_content"]
    assert not any(term["available"] for term in payload["required_native_terms"].values())
    assert "not proof" in payload["boundary"]
