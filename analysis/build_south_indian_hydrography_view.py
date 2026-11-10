"""Publish the checked source-profile UI without copying full scientific arrays."""
import json
from pathlib import Path
from acquire_indian_secc_hycom_2013 import pin
from acquire_eac_100m_source import write_json
from package_south_indian_hycom_hydrography import DESTINATION, ROOT


def build():
    manifest = json.loads((DESTINATION/'acquisition.json').read_bytes())
    for name, expected in manifest['files'].items():
        if pin(DESTINATION/name) != expected:
            raise ValueError('Changed source product: '+name)
    output = ROOT/'figures/south-indian-hydrography-2013'
    output.mkdir(parents=True, exist_ok=True)
    template = ROOT/'analysis/south_indian_hydrography_view.html'
    (output/'index.html').write_bytes(template.read_bytes())
    write_json(output/'view.json', {'schema': 'osw.south-indian-hydrography-view.v1',
               'source_manifest': pin(DESTINATION/'acquisition.json'),
               'template': pin(template), 'html': pin(output/'index.html'),
               'months': 12, 'depths': 2, 'meridians': 3,
               'profiles': 288, 'named_current_width_admitted': False})
    print(output.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    build()
