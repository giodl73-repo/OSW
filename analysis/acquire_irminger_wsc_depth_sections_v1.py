"""Cloud-only Irminger/WSC configuration of the frozen latitude collector."""
from pathlib import Path
import acquire_latitude_depth_sections_v2 as collector

if __name__ == "__main__":
    collector.OPERATOR = "research/irminger-wsc-depth-sections-operator-v1.json"
    collector.OUT = Path("irminger-wsc-depth-sections-v1")
    collector.main()
