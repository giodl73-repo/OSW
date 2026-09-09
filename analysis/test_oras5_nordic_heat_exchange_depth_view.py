import hashlib
import pathlib

from build_oras5_nordic_heat_exchange_depth_view import build


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_heat_exchange_depth_view_is_deterministic(tmp_path: pathlib.Path) -> None:
    first, second = tmp_path / "first.svg", tmp_path / "second.svg"
    source = ROOT / "research/osw-m4-oras5-nordic-heat-exchange-anatomy-2018.json"
    build(source, first); build(source, second)
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    text = first.read_text(encoding="utf-8")
    assert "THE HEAT EXCHANGE LIVES ABOVE 700 METRES" in text
    assert "THE ROOM'S VERTICAL SUM" in text
