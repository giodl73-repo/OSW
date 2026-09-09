import hashlib
import pathlib

from build_oras5_nordic_storage_crosscheck_view import build


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_storage_crosscheck_view_is_deterministic(tmp_path: pathlib.Path) -> None:
    first = tmp_path / "first.svg"
    second = tmp_path / "second.svg"
    source = ROOT / "research/osw-m4-oras5-nordic-storage-crosscheck-2018.json"
    build(source, first)
    build(source, second)
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    text = first.read_text(encoding="utf-8")
    assert "STORAGE IS NOT THE MISSING 38 TW" in text
    assert "TWO INDEPENDENT STORAGE ESTIMATES OVERLAP" in text
