"""Cloud-only Basin SEC configuration of the frozen transverse collector."""
from pathlib import Path
import acquire_transverse_depth_sections_v2 as collector

if __name__ == "__main__":
    collector.OPERATOR = "research/sec-basin-depth-sections-operator-v1.json"
    collector.OUT = Path("sec-basin-depth-sections-v1")
    collector.main()
