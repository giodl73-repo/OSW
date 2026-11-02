"""Cloud-only Guinea configuration of the frozen transverse collector."""
from pathlib import Path
import acquire_transverse_depth_sections_v2 as collector

if __name__ == "__main__":
    collector.OPERATOR = "research/guinea-depth-sections-operator-v1.json"
    collector.OUT = Path("guinea-depth-sections-v1")
    collector.main()
