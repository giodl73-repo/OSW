"""Render all four native property masks with equivalent complete case tables."""
import json

from acquire_indian_secc_hycom_2013 import pin
from south_indian_front_property_query import ROOT, REPORT, FOLDER, TEMPLATE, evidence


def main():
    report, _, inputs = evidence()
    folder = ROOT/FOLDER
    folder.mkdir(exist_ok=True, parents=True)
    (folder/'index.html').write_bytes((ROOT/TEMPLATE).read_bytes())
    view = {'schema': 'osw.south-indian-property-support-view.v1',
            'report': pin(ROOT/REPORT), 'template': pin(ROOT/TEMPLATE),
            'html': pin(folder/'index.html'),
            'query_adapter': pin(ROOT/'analysis/south_indian_front_property_query.py'),
            'source_input_sha256': inputs, 'cases': len(report['cases']), 'criteria_per_case': 4,
            'temperature_scale_verified': False, 'front_identification_verified': False,
            'current_association_verified': False, 'physical_width_admitted': False}
    (folder/'view.json').write_bytes((json.dumps(view, indent=2)+'\n').encode())
    print('Built complete property-support view:', FOLDER)


if __name__ == '__main__':
    main()
