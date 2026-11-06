"""Render published prose estimates; never infer monthly samples or current geometry."""
import ctypes
import json
import os
from pathlib import Path

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[name] = "1"
if os.name == "nt":
    kernel = ctypes.windll.kernel32
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    kernel.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    assert kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(), 1)
    assert kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/atlantic-ax08-goes-2013-seasonal-core-speeds-v1.json"


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    scopes = {r["current_id"]: r for r in data["current_scopes"]}
    owners = {r["id"] for r in json.loads((ROOT / "research/ocean-current-almanac.json").read_text(encoding="utf-8"))["entries"]}
    assert set(scopes) <= owners
    rows = data["records"]
    assert len({r["id"] for r in rows}) == len(rows) == 6
    assert data["common_support"]["selected_section_count"] == 31
    assert data["common_support"]["reconstruction_values_mixed_into_these_records"] is False
    fig, ax = plt.subplots(figsize=(10.8, 6.3))
    fig.patch.set_facecolor("#f7fafc")
    ax.set_facecolor("#f7fafc")
    fig.subplots_adjust(left=0.35, right=0.82, top=0.77, bottom=0.32)
    colors = {"NECC": "#087e8b", "NEUC": "#3264ad", "SEUC": "#8b4ba8"}
    labels = []
    for index, row in enumerate(rows):
        assert row["calendar_months"] is None
        label = scopes[row["current_id"]]["source_label"]
        color = colors[label]
        kind = row["estimate_kind"]
        numeric_fields = [row[k] is not None for k in ("value_m_s", "interval_m_s", "lower_threshold_m_s")]
        assert sum(numeric_fields) == 1
        if kind == "approximate_point":
            assert row["value_m_s"] is not None
            ax.plot(row["value_m_s"], index, "o", color=color, ms=8)
        elif kind == "approximate_prose_interval":
            lo, hi = row["interval_m_s"]
            assert lo < hi
            ax.plot([lo, hi], [index, index], color=color, lw=5, solid_capstyle="butt")
        elif kind == "reported_greater_than":
            threshold = row["lower_threshold_m_s"]
            assert row["value_m_s"] is None and row["interval_m_s"] is None
            ax.plot(threshold, index, "o", mfc="#f7fafc", mec=color, ms=8, mew=1.5)
            ax.annotate("", xy=(threshold + 0.05, index), xytext=(threshold + 0.012, index), arrowprops={"arrowstyle": "->", "color": color, "lw": 1.5})
        else:
            raise ValueError(kind)
        ax.text(1.03, index, row["display"].replace(" m/s", ""), transform=ax.get_yaxis_transform(), va="center", fontsize=10, color=color)
        labels.append(f"{label}  |  {row['season_label']}")
    ax.set_yticks(range(len(rows)), labels, fontsize=10)
    ax.set_ylim(len(rows)-0.5, -0.5)
    ax.set_xlim(0, 0.55)
    ax.set_xlabel("Geostrophic core velocity (m/s)", fontsize=11)
    ax.xaxis.grid(True, color="#dce5ea")
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=12)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.text(0.045, 0.94, "Atlantic currents: published seasonal core speeds", fontsize=17, weight="bold", color="#163344")
    fig.text(0.045, 0.885, "Central Atlantic AX08 sections | XBT-derived seasonal fit | 2000-2010 sampling context", fontsize=10.5, color="#455b6b")
    fig.text(0.045, 0.83, "NECC: North Equatorial Countercurrent | NEUC / SEUC: North / South Equatorial Undercurrents", fontsize=10, color="#455b6b")
    notes = [
        "Dots: approximate values. Solid span: reported interval, not uncertainty. Open circle + arrow: greater-than threshold.",
        "Author's boreal season labels; exact month windows unavailable. No continuous monthly curve or annual extrema inferred.",
        "31 selected sections shared across currents; no February section and only one each in January, May and June.",
        "Density layers differ: NECC surface-24.5; NEUC/SEUC 24.5-26.8 kg/m3 potential-density anomaly.",
        "Synthetic NEUC summer/fall estimate differs (~0.10 m/s); it is excluded from these XBT-derived rows.",
        "Goes et al. (2013), doi:10.1002/jgrc.20186, sections 4.2.1-4.2.3. Prose extraction; no figure digitization."
    ]
    for i, note in enumerate(notes):
        fig.text(0.045, 0.225-i*0.033, note, fontsize=9, color="#455b6b")
    output = ROOT / data["visualization"]["figure"]
    with matplotlib.rc_context({"svg.hashsalt": "osw-atlantic-ax08-goes-2013-core-speeds-v1", "svg.fonttype": "none"}):
        fig.savefig(output, metadata={"Date": None})
    # Preserve line separators in path attributes while removing generated padding.
    output.write_bytes(("\n".join(line.rstrip() for line in output.read_text(encoding="utf-8").splitlines()) + "\n").encode("utf-8"))
    preview = ROOT / ".pytest_cache/atlantic-ax08-goes-2013-core-speeds-v1.png"
    fig.savefig(preview, dpi=120)
    plt.close(fig)
    print("PASS: six scoped records, three existing owners, distinct estimate encodings; SVG and review PNG generated.")


if __name__ == "__main__":
    main()
