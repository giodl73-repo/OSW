"""Cloud-only frozen transverse collector for two NEC members and Subarctic flow."""
from pathlib import Path
import acquire_zonal_current_depth_sections_v1 as collector


def main():
    collector.OPERATOR='research/nec-subarctic-depth-sections-operator-v1.json'
    collector.OUT=Path('nec-subarctic-depth-sections-v1')
    collector.main()


if __name__=='__main__':main()
