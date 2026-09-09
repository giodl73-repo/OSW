import hashlib
import pathlib

from build_oras5_nordic_face_persistence_view import build


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_face_persistence_view_is_deterministic(tmp_path: pathlib.Path) -> None:
    source = ROOT / "research/osw-m4-oras5-nordic-face-heat-map-2018.json"
    first, second = tmp_path / "first.svg", tmp_path / "second.svg"
    build(source, first); build(source, second)
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    text = first.read_text(encoding="utf-8")
    assert "THE ATLANTIC HEAT JET IS NOT AN ANNUAL-MEAN MIRAGE" in text
    assert "THE LEADER NEVER SURRENDERS #1" in text
    assert "monthly range 14–19" in text
