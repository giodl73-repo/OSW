import hashlib
import pathlib

from build_oras5_nordic_heat_relay_view import build


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_heat_relay_view_is_deterministic(tmp_path: pathlib.Path) -> None:
    source = ROOT / "research/osw-m4-oras5-nordic-heat-relay-2018.json"
    first, second = tmp_path / "first.svg", tmp_path / "second.svg"
    build(source, first); build(source, second)
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    text = first.read_text(encoding="utf-8")
    assert "THE NORDIC SEAS ACT LIKE A SEASONAL HEAT RELAY" in text
    assert "SAME MONTH IS THE STRONGEST ALIGNMENT" in text
    assert "does not measure parcel transit or causality" in text
