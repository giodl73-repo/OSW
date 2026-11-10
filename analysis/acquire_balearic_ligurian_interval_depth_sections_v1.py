"""Cloud-only Balearic and Ligurian regional currents source wrapper; numerical collector remains frozen."""
from pathlib import Path
import acquire_barents_makassar_interval_depth_sections_v1 as frozen

OPERATOR='research/balearic-ligurian-interval-depth-sections-operator-v1.json'
OUT=Path('balearic-ligurian-interval-depth-sections-v1')

def main():
    frozen.OPERATOR=OPERATOR
    frozen.OUT=OUT
    frozen.main()

if __name__=='__main__':main()
