"""Publish supplementary raw profiles only after complete source verification."""
from pathlib import Path

from acquire_indian_secc_hycom_2013 import pin
from acquire_eac_100m_source import write_json
from south_indian_front_level_query import evidence, ROOT, DESTINATION


def build():
    rows, _, report, inputs = evidence()
    if len(rows) != 23472 or {r['depth_m'] for r in rows} != {100, 200}:
        raise ValueError('Incomplete or wrong supplementary source profile data')
    template = ROOT/'analysis/south_indian_front_level_view.html'
    output = ROOT/'figures/south-indian-front-levels-2013'
    output.mkdir(parents=True, exist_ok=True)
    (output/'index.html').write_bytes(template.read_bytes())
    write_json(output/'view.json', {
        'schema': 'osw.south-indian-front-level-source-view.v1',
        'source_manifest': pin(DESTINATION/'acquisition.json'),
        'template': pin(template), 'html': pin(output/'index.html'),
        'query_adapter': pin(ROOT/'analysis/south_indian_front_level_query.py'),
        'source_input_sha256': inputs,
        'months': 12, 'native_depths_m': [100, 200], 'meridians': 3,
        'selections': 72, 'profiles': 360, 'native_monthly_cells': 23472,
        'displayed_temperature': 'in-situ retained beside conditional potential temperature at0dbar; ITS-90 assumption',
        'derived_report': pin(ROOT/'research/south-indian-2013-front-level-potential-temperature.json'),
        'temperature_scale_verified': False,
        'current_association_verified': False, 'named_current_width_admitted': False})
    print(output.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    build()
