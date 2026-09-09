import json
import pathlib

from build_indonesian_gate_readiness_view import LAND_SHA256, build


ROOT = pathlib.Path(__file__).parent.parent


def test_committed_view_exposes_all_gate_verdicts():
    svg = (ROOT / "figures/osw-motion-indonesian-gate-readiness-2018.svg").read_text(encoding="utf-8")
    assert "ONE THROUGHFLOW. FIVE GATES." in svg
    assert LAND_SHA256 in svg
    for code in ("MAK", "LIF", "LOM", "OMB", "TIM"):
        assert f">{code}<" in svg
    assert "SURFACE SIGN CONFLICT" in svg
    assert "UNDERRESOLVED" in svg
    assert "GRID SUPPORT · NOT HEAT TRANSPORT" in svg
