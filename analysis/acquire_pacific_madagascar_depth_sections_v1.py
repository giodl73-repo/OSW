"""Cloud-only reuse of the frozen full-section collector with new declared gates."""
from pathlib import Path
import acquire_three_current_depth_sections_v1 as collector


def main():
    collector.OPERATOR='research/pacific-madagascar-depth-sections-operator-v1.json'
    collector.OUT=Path('pacific-madagascar-depth-sections-v1')
    collector.main()


if __name__=='__main__':main()
