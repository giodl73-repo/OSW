"""Cloud-only Malvinas/EACC configuration of the frozen latitude collector."""
from pathlib import Path
import acquire_latitude_depth_sections_v2 as collector

if __name__ == "__main__":
    collector.OPERATOR = "research/malvinas-eacc-depth-sections-operator-v1.json"
    collector.OUT = Path("malvinas-eacc-depth-sections-v1")
    collector.main()
