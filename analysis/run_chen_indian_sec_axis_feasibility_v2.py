"""Execution-control correction only; reuse the frozen v1 scientific producer."""
from pathlib import Path
import chen_indian_sec_axis_feasibility_v1 as producer

if __name__ == '__main__':
    producer.REQUEST = 'research/chen-indian-sec-axis-feasibility-request-v2.json'
    producer.OUTPUT = Path('.pytest_cache/chen-indian-sec-axis-feasibility-v2')
    producer.main()
