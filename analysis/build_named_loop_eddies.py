"""Snapshot factual names and dates from Horizon Marine's public Loop Current table."""

from __future__ import annotations

import json
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


SOURCE = "https://www.horizonmarine.com/loop-current-eddies"
OUTPUT = Path(__file__).resolve().parents[1] / "research" / "named-loop-current-eddies.json"


class FirstTable(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_table = False
        self.finished = False
        self.in_cell = False
        self.current_cell = ""
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table" and not self.finished:
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.current_row = []
        elif self.in_table and tag in {"td", "th"}:
            self.in_cell = True
            self.current_cell = ""

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.current_cell += data

    def handle_endtag(self, tag: str) -> None:
        if self.in_table and tag in {"td", "th"}:
            self.current_row.append(" ".join(self.current_cell.split()))
            self.in_cell = False
        elif self.in_table and tag == "tr" and self.current_row:
            self.rows.append(self.current_row)
        elif self.in_table and tag == "table":
            self.in_table = False
            self.finished = True


def iso_date(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%m/%d/%Y").date().isoformat()
    except ValueError:
        return value  # Preserve the source's partial or unusual date.


def main() -> None:
    request = Request(SOURCE, headers={"User-Agent": "OSW-Almanac/1.0"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
    table = FirstTable()
    table.feed(html)
    entries = []
    for row in table.rows[1:]:
        if len(row) != 8 or not row[0].isdigit():
            raise ValueError(f"Unexpected source row: {row!r}")
        entries.append({
            "source_number": int(row[0]),
            "name": row[1],
            "initial_separation": iso_date(row[2]),
            "dissipation_as_reported": row[3],
            "secondary_name": row[5],
        })
    if len(entries) < 80 or len({item["source_number"] for item in entries}) != len(entries):
        raise ValueError("The source table appears incomplete or duplicated")
    payload = {
        "schema": "osw.almanac.named-loop-current-eddies.v1",
        "scope": "Horizon Marine's named Loop Current eddies in the Gulf of Mexico; not all global eddies",
        "source": SOURCE,
        "retrieved_date": date.today().isoformat(),
        "status_note": "Dissipation labels are copied as historical source text; 'Active' is not a current-status claim.",
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {OUTPUT}")


if __name__ == "__main__":
    main()
