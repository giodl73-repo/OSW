"""Small source-only chart; no scientific field processing or runtime build."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(data, monthly=False):
    rows = data["monthly_records"] if monthly else data["records"]
    period = "monthly" if monthly else "seasonal"
    height = 330 + (len(rows) - 3) * 48
    footer = height - 98
    assert sum(r["observation_count"] for r in rows) == data["method"]["observations"]
    assert (sorted(r["month"] for r in rows) if monthly else
            sorted(m for r in rows for m in r["months"])) == list(range(1, 13))
    x = lambda v: 210 + v * 270
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 {height}" role="img" aria-labelledby="title desc">',
             f'<title id="title">Pemba Channel {period} drifter speeds</title>',
             '<desc id="desc">Pooled summaries. Lines show observed minima to maxima; dots show medians. These are regional speeds, not current dimensions or confidence intervals.</desc>',
             f'<rect width="800" height="{height}" fill="#f8fafc"/>',
             '<g font-family="system-ui,sans-serif" fill="#172e46">',
             f'<text x="24" y="32" font-size="21">Pemba Channel: {period} near-surface speed</text>',
             f'<text x="24" y="57" font-size="13">Semba et al. 2019 · Table {4 if monthly else 2} · pooled 1986–2017 observations</text>']
    for i, row in enumerate(rows):
        assert 0 <= row["minimum"] <= row["median"] <= row["maximum"] <= 2
        y = 100 + i * 48
        label = ("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[row["month"] - 1]
                 if monthly else row["season"])
        parts += [f'<text x="24" y="{y+5}" font-size="15">{label} · n={row["observation_count"]}</text>',
                  f'<line x1="{x(row["minimum"])}" x2="{x(row["maximum"])}" y1="{y}" y2="{y}" stroke="#387a9c" stroke-width="5"/>',
                  f'<circle cx="{x(row["median"])}" cy="{y}" r="6" fill="#182e46"/>',
                  f'<text x="700" y="{y+5}" font-size="14">{row["median"]:.2f}</text>']
    for tick in [0, 0.5, 1, 1.5, 2]:
        parts.append(f'<text x="{x(tick)}" y="{footer}" text-anchor="middle" font-size="13">{tick:g}</text>')
    parts += [f'<text x="445" y="{footer+21}" text-anchor="middle" font-size="13">Speed (m/s) · line: observed range · dot: median</text>',
              f'<text x="24" y="{footer+48}" font-size="12">SE: May–Sep · IN: Apr, Oct · NE: Nov–Mar. Unequal sampling; 45 unique drifters.</text>',
              f'<text x="24" y="{footer+68}" font-size="12">NE minimum: table 0.05; prose 0.04 m/s. Conflict retained. Ranges are not uncertainty.</text>',
              f'<text x="24" y="{footer+88}" font-size="12">doi:10.1371/journal.pone.0210303 · Source-review chart; runtime integration pending.</text>', '</g></svg>']
    return '\n'.join(parts) + '\n'


if __name__ == "__main__":
    data = json.loads((ROOT / "research/eacc-pemba-semba-2019-seasonal-speed-v1.json").read_text())
    path = ROOT / "figures/eacc-pemba-seasonal-speed-v1.svg"
    path.write_text(render(data), encoding="utf-8")
    print(path)
    monthly_path = ROOT / "figures/eacc-pemba-monthly-speed-v1.svg"
    monthly_path.write_text(render(data, monthly=True), encoding="utf-8")
    print(monthly_path)
