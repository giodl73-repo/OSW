"""Bind both retained numerical experiments and their independent comparisons."""
import json

from west_australian_regional_streamlines_rk4 import ROOT, REPORT, build, encoded, digest

HELPER='analysis/west_australian_streamline_evidence.py'


def verify():
    document=build()
    if encoded(document)!=(ROOT/REPORT).read_bytes():raise ValueError('Changed refined regional streamline report')
    pins={**document['input_sha256'],REPORT:digest((ROOT/REPORT).read_bytes()),HELPER:digest((ROOT/HELPER).read_bytes())}
    for manifest_path in ['research/west-australian-regional-streamline-figures.json','research/west-australian-regional-streamline-rk4-figures.json']:
        manifest=json.loads((ROOT/manifest_path).read_bytes())
        if manifest['physical_current_geometry_admitted'] is not False:raise ValueError('Changed regional figure admission')
        pins[manifest_path]=digest((ROOT/manifest_path).read_bytes())
        for file_key,hash_key in [('source_file','source_sha256'),('generator_file','generator_sha256'),('supporting_generator_file','supporting_generator_sha256')]:
            if file_key in manifest:
                path=manifest[file_key];expected=manifest[hash_key]
                if digest((ROOT/path).read_bytes())!=expected:raise ValueError('Changed regional source/generator: '+path)
                pins[path]=expected
        for asset in manifest['figures'].values():
            if digest((ROOT/asset['file']).read_bytes())!=asset['sha256'] or (ROOT/asset['file']).stat().st_size!=asset['bytes']:
                raise ValueError('Changed regional comparison asset')
            pins[asset['file']]=asset['sha256']
    return document,pins
