"""Explicitly acquire twelve daily snapshots across 2025; never monthly means."""
import hashlib
import json
from pathlib import Path
from fetch_noaa_lsa_geostrophic_repeat import fetch_date, receipt_path, ROOT

OUTPUT = ROOT / "research/gulf-stream-2025-monthly-sample-receipts.json"
DATES = [f"2025-{month:02d}-15" for month in range(1,13)]

def main():
    old = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else None
    observations = []
    for day in DATES:
        path = receipt_path(day)
        if path.exists():
            source = json.loads(path.read_text(encoding="utf-8"))
            if old:
                previous = next((r for r in old["observations"] if r["date"] == day), None)
                if previous and hashlib.sha256(path.read_bytes()).hexdigest() != previous["source_subset_sha256"]:
                    raise ValueError("Changed existing annual sample")
        else:
            source = fetch_date(day, initial_pin=True)
        observations.append({"date":day,"source_subset":str(path.relative_to(ROOT)).replace("\\","/"),"source_subset_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"source_response_sha256":source["source_response_sha256"],"source_url":source["source_url"],"source_algorithm":source["source_algorithm"],"source_product_status":source["source_product_status"]})
        output = {"schema":"osw.current-annual-sample-acquisition.v1","status":"research_only_not_canonical_or_ranked","sampling_year":2025,"requested_dates":DATES,"dates":[r["date"] for r in observations],"sampling_kind":"one_daily_snapshot_per_month_not_monthly_mean","sampling_note":"Fifteenth day of each month in 2025, selected before acquisition. Twelve daily snapshots, not monthly means, climatology or annual extrema.","observations":observations}
        OUTPUT.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
        print(day, source["source_algorithm"], source["source_product_status"], flush=True)

if __name__ == "__main__":
    main()
