import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_detected_mhw_receipt_view.py")
SPEC = importlib.util.spec_from_file_location("build_detected_mhw_receipt_view", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_receipt_view_is_deterministic(tmp_path):
    output = tmp_path / "receipt.svg"
    generated = MODULE.build(output_path=output)
    assert generated == output.read_text(encoding="utf-8")
    assert generated == (ROOT / "figures" / "osw-d1-noaa-crw-mhw-point-2026.svg").read_text(encoding="utf-8")


def test_receipt_view_states_claim_and_boundary():
    svg = MODULE.build(output_path=Path(__file__).parent / "_temporary_mhw_receipt.svg")
    try:
        assert "27" in svg and "PASS" in svg
        assert "Not yet earned" in svg
        assert "one cool day" in svg
        assert "<title>" in svg and "<desc>" in svg
    finally:
        (Path(__file__).parent / "_temporary_mhw_receipt.svg").unlink()
