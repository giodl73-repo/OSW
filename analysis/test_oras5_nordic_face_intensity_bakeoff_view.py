import hashlib
import pathlib

from build_oras5_nordic_face_intensity_bakeoff_view import build


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_face_intensity_bakeoff_is_deterministic(tmp_path: pathlib.Path) -> None:
    first, second = tmp_path / "first.svg", tmp_path / "second.svg"
    args = (ROOT / "research/osw-m4-oras5-nordic-face-heat-map-2018.json", ROOT / "research/osw-m4-oras5-nordic-control-volume.json", ROOT / "atlas/data/oras5-nordic-seas-mesh.nc")
    build(*args, first); build(*args, second)
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    text = first.read_text(encoding="utf-8")
    assert "THE STRONGEST ATLANTIC JET SURVIVES AREA NORMALIZATION" in text
    assert "HEAT PER WET FACE AREA" in text
