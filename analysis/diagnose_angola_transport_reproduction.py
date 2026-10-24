"""Classify frozen v1 replay differences without changing products or gates."""
import copy
import gzip
import hashlib
import json
import platform
import sys
import zlib
from angola_nansen_native_sections import ROOT, REPORT, calculate


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    retained = json.loads((ROOT / REPORT).read_bytes())
    rebuilt, products = calculate()
    rows = []
    for section in retained['sections']:
        path = section['field_file']
        old = (ROOT / path).read_bytes()
        new = products[path]
        old_raw, new_raw = gzip.decompress(old), gzip.decompress(new)
        rows.append({'field': path,
                     'retained_compressed_sha256': sha(old),
                     'rebuilt_compressed_sha256': sha(new),
                     'retained_compressed_bytes': len(old),
                     'rebuilt_compressed_bytes': len(new),
                     'compressed_exact': old == new,
                     'retained_header_hex': old[:10].hex(),
                     'rebuilt_header_hex': new[:10].hex(),
                     'retained_decoded_sha256': sha(old_raw),
                     'rebuilt_decoded_sha256': sha(new_raw),
                     'decoded_exact': old_raw == new_raw,
                     'retained_decoded_binding_exact': sha(old_raw) == section['decoded_sha256'],
                     'first_compressed_difference_offset': next((i for i,(a,b) in enumerate(zip(old,new)) if a != b), None)})
    old_meta, new_meta = copy.deepcopy(retained), copy.deepcopy(rebuilt)
    for report in (old_meta,new_meta):
        for section in report['sections']:
            del section['field_sha256']
            del section['field_bytes']
    result = {'schema':'osw.angola-native-v1-replay-diagnostic.v1',
              'environment':{'python':sys.version,'platform':platform.platform(),
                             'zlib_compile':zlib.ZLIB_VERSION,'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION},
              'all_decoded_fields_exact':all(r['decoded_exact'] for r in rows),
              'all_compressed_fields_exact':all(r['compressed_exact'] for r in rows),
              'report_exact_except_compressed_sha256_and_size':old_meta == new_meta,
              'retained_report_sha256':sha((ROOT/REPORT).read_bytes()),
              'scientific_products_changed':False,
              'original_failing_replay_gate_retained':True,'fields':rows}
    directory=ROOT/'.pytest_cache/angola-nansen-sections';directory.mkdir(parents=True,exist_ok=True)
    (directory/'transport-replay-diagnostic.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
