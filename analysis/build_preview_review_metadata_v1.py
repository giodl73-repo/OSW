"""Bibliographic and use-scope metadata only; never load measurement catalogs."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PIN = '5c76767ba3bafa2613c1ba4e043edea1182d7e13'
REPORT = 'research/preview-data-projection-v1.json'
OUT = 'almanac/preview-review-v1'
FIELD = re.compile(r'"(?P<key>citation|source_citation|title|source_title|source_url|primary_url|data_url|doi|url)"\s*:\s*(?P<value>"(?:[^"\\]|\\.)*")')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_metadata(path):
    """Read only bibliographic string matches. Do not JSON-decode source-fact bodies."""
    if not (ROOT / path).is_file():
        raise ValueError('Missing retained metadata file: ' + path)
    result = subprocess.run(['rg', '--no-heading', '--no-filename', '-o', FIELD.pattern, path],
                            cwd=ROOT, capture_output=True, check=False)
    if result.returncode not in (0, 1):
        raise ValueError('Bibliographic search failed: ' + path)
    fields = {}
    for match in FIELD.finditer(result.stdout.decode('utf8')):
        fields.setdefault(match['key'], [])
        value = json.loads(match['value'])  # One bibliographic string, never a data object.
        if value not in fields[match['key']]:
            fields[match['key']].append(value)
    return {'metadata_file': path, 'metadata_file_sha256': sha((ROOT / path).read_bytes()),
            'bibliographic_strings': fields}


def main():
    raw_report = (ROOT / REPORT).read_bytes()
    report = json.loads(raw_report)  # Administrative build/custody report, no measured values.
    paths = (ROOT / OUT)
    paths.mkdir(parents=True, exist_ok=True)
    expected = report['depth_contexts_without_bibliographic_metadata']
    codes = {
        'florida-hycom2022-original-primary-censored-supported-reach': 'build_current_depth_reference_inventory_v3.py',
        'falkland-hycom2022-original-primary-censored-supported-reach': 'build_current_depth_reference_inventory_v4.py',
        'east-african-coastal-hycom2022-original-primary-censored-supported-reach': 'build_current_depth_reference_inventory_v4.py',
        'tsushima-matsuyama1980-common19day-observed-pair-linear-scenarios': 'load_current_depth_reference_inventory_v5.py',
        'jutland-aure1989-salinity-selected-regional-water-inventory': 'load_current_depth_reference_inventory_v6.py',
        'nwasc-baumann1993-2022-selected-noncore': 'load_current_depth_reference_inventory_v7.py',
        'barents-makassar-north-cape-original-interval-core-reach': 'load_current_depth_reference_inventory_v8.py',
        'coastal-upper-layer-norwegian-coastal-original-interval-core-reach': 'load_current_depth_reference_inventory_v8.py',
        'guiana-egcc-east-greenland-coastal-original-interval-core-reach': 'load_current_depth_reference_inventory_v8.py',
        'jutland-nielsen2000-atypical-gbw-pulse-upper-layer': 'load_current_depth_reference_inventory_v9.py',
        'ncc-original-core-hycom2022-practical-salinity35-component10cms': 'load_current_depth_reference_inventory_v10.py',
        'egcc-sutherland2008-reported-coastal-front-foot': 'load_current_depth_reference_inventory_v11.py',
        'full-coastal-norwegian-coastal-hycom2022-original-core': 'load_current_depth_reference_inventory_v12.py',
        'full-coastal-east-greenland-coastal-hycom2022-original-core': 'load_current_depth_reference_inventory_v12.py',
        'ncc-north-61p5-62p25n-hycom2022-original-core': 'load_current_depth_reference_inventory_v13.py',
        'loop-welsh2009-local-progressive-vector-transition': 'load_current_depth_reference_inventory_v14.py',
        'huang2022-8p5n130e-pacific-north-equatorial': 'load_current_depth_reference_inventory_v16.py',
        'huang2022-8p5n130e-pacific-north-equatorial-undercurrent': 'load_current_depth_reference_inventory_v16.py',
        'rim-oguz1999-western-black-sea-april1993': 'load_current_depth_reference_inventory_v17.py',
        'alaska-jarosz2017-kayak-winter2012-2013': 'load_current_depth_reference_inventory_v18.py',
        'gulf-stream-a20-2021-local-fixed96m-direction-cutoffs': 'load_current_depth_reference_inventory_v28.py',
        'agulhas-i06s-2019-native-uv-local-cutoffs': 'load_current_depth_reference_inventory_v30.py',
        'east-australian-p06-2017-native-uv-local-cutoffs': 'load_current_depth_reference_inventory_v33.py',
        'oman-2025-pag-main-plume-fraction-030-spatial-descriptors': 'load_current_depth_reference_inventory_v34.py',
        'red-sea-pratt2000-hanish-mean-velocity-interface': 'load_current_depth_reference_inventory_v35.py',
        'northern-mediterranean-toulon-2011-transect1-geostrophic-depth': 'load_current_depth_reference_inventory_v36.py',
        'azores-ibi-1993-2021-mean-section-depth': 'load_current_depth_reference_inventory_v37.py',
        'norwegian-rudels2026-entering-aw-layer-thickness': 'load_current_depth_reference_inventory_v38.py',
        'jutland-norkyst2024-interior-censored-component-support': 'load_current_depth_reference_inventory_v39.py',
        'leeuwin-watr50-processed-monthly-mean-censor-support': 'load_current_depth_reference_inventory_v40.py',
    }
    fact_files = {
        'tsushima-matsuyama1980-common19day-observed-pair-linear-scenarios': 'research/tsushima-matsuyama-1990-depth-pair-source-facts-v1.json',
        'jutland-aure1989-salinity-selected-regional-water-inventory': 'research/jutland-aure-1990-area-mean-depth-source-facts-v1.json',
        'nwasc-baumann1993-2022-selected-noncore': 'research/nwasc-selected-noncore-depth-source-context-v1.json',
        'jutland-nielsen2000-atypical-gbw-pulse-upper-layer': 'research/jutland-nielsen2000-depth-profile-source-facts-v1.json',
        'egcc-sutherland2008-reported-coastal-front-foot': 'research/egcc-sutherland2008-coastal-front-depth-source-facts-v1.json',
        'loop-welsh2009-local-progressive-vector-transition': 'research/loop-welsh2009-local-transition-depth-source-facts-v1.json',
        'huang2022-8p5n130e-pacific-north-equatorial': 'research/nec-huang2022-filtered-depth-source-facts-v1.json',
        'huang2022-8p5n130e-pacific-north-equatorial-undercurrent': 'research/nec-huang2022-filtered-depth-source-facts-v1.json',
        'rim-oguz1999-western-black-sea-april1993': 'research/rim-oguz1999-native-vertical-source-facts-v1.json',
        'alaska-jarosz2017-kayak-winter2012-2013': 'research/alaska-jarosz2017-winter-reach-source-facts-v1.json',
        'oman-2025-pag-main-plume-fraction-030-spatial-descriptors': 'research/current-depth-oman-2025-published-depth-source-review-v1.json',
        'red-sea-pratt2000-hanish-mean-velocity-interface': 'research/current-depth-pratt2000-hanish-mean-interface-source-review-v1.json',
        'northern-mediterranean-toulon-2011-transect1-geostrophic-depth': 'research/current-depth-northern-toulon-source-review-v1.json',
        'azores-ibi-1993-2021-mean-section-depth': 'research/current-depth-azores-ibi-mean-depth-source-review-v1.json',
        'norwegian-rudels2026-entering-aw-layer-thickness': 'research/current-depth-norwegian-rudels2026-aw-layer-source-review-v1.json',
        'jutland-norkyst2024-interior-censored-component-support': 'research/current-depth-norkyst-native-metadata-source-review-v1.json',
        'leeuwin-watr50-processed-monthly-mean-censor-support': 'research/leeuwin-depth-sensitivity-source-review-v1.json',
    }
    assert set(expected) == set(codes)
    contexts = {}
    cache = {}
    for context_id in expected:
        code = 'analysis/' + codes[context_id]
        code_bytes = (ROOT / code).read_bytes()
        context = {'id': context_id, 'context_role': 'OSW_admission_and_method_context_not_independent_measurement',
                   'title': 'OSW method context: ' + context_id.replace('-', ' '),
                   'method_file': code, 'method_file_sha256': sha(code_bytes),
                   'url': f'https://github.com/giodl73-repo/OSW/blob/{PIN}/{code}',
                   'independent_measurement_added': False,
                   'interpretation': 'This method citation explains how the retained reference was admitted. Primary paper or data attribution remains with the reference; this context is not additional corroborating evidence.'}
        if context_id in fact_files:
            file = fact_files[context_id]
            if file not in cache:
                cache[file] = source_metadata(file)
            context['retained_bibliographic_metadata'] = cache[file]
        elif 'hycom2022' in context_id or 'original-interval-core-reach' in context_id:
            context['primary_data_provider_url'] = 'https://www.hycom.org/dataserver/gofs-3pt1/analysis'
            context['primary_data_citation_scope'] = 'Provider attribution only. Exact input custody, selection, and limits remain in each retained reference and its method record.'
        elif any(s in context_id for s in ['a20-2021', 'i06s-2019', 'p06-2017']):
            cruise = '2021_A20' if 'a20-2021' in context_id else ('2019_I06S' if 'i06s-2019' in context_id else '2017_P06')
            context['primary_data_provider_urls'] = [r['url'] for r in report['additional_factual_source_uses_to_review']
                                                     if f'/downloads/{cruise}/' in r['url']]
        contexts[context_id] = context
    supplement = {'schema': 'osw.preview-context-citations.v1', 'candidate_build_sha256': sha((ROOT / 'almanac/preview-data-candidate-v1/build.json').read_bytes()),
                  'scope': 'Supplement empty context metadata without editing admitted facts or replacing primary citations.',
                  'contexts': contexts, 'measurement_values_read_or_changed': False, 'original_sources_reopened': False}
    entries = []
    for row in report['additional_factual_source_uses_to_review']:
        url = row['url']
        parsed = urlsplit(url)
        host = (parsed.hostname or '').lower()
        dataset = any(s in url for s in ['/tabledap/', '/downloads/', 'data.griidc.org', 'data.csiro.au', 'doi.pangaea.de',
                                        '10.5281/zenodo.', '/dataserver/', 'spraydata.ucsd.edu/products/', '/archive/accession/'])
        media = parsed.path.lower().endswith(('.png', '.gif', '.jpg')) or host in {'www.linkedin.com', 'energies-and-infrastructures-monitoring.groupcls.com'}
        disposition = ('selected_facts_and_OSW_derived_scalar_references_only' if dataset else
                       ('OSW_qualified_reading_references_only_no_source_media' if media else 'attributed_selected_factual_references_only'))
        entries.append({'url': url, 'uses': row['uses'], 'disposition': disposition,
                        'permitted_materials': ['bibliographic_attribution', 'selected_source_scoped_scalar_facts',
                                               'OSW_authored_method_and_qualification', 'OSW_derived_scalar_references'],
                        'excluded_materials': ['original_articles', 'source_images_or_movies', 'publisher_table_assets',
                                               'raw_datasets_or_profiles', 'provider_geometry', 'bulk_provider_registry',
                                               'unverified_named_registry_joins'],
                        'underlying_source_licence_granted': False, 'scientific_claim_review_granted': False,
                        'original_record_eligibility_flags_must_remain_unchanged': True,
                        'basis': 'The existing OSW linked-factual-use policy, applied only to selected facts and OSW-authored references in the pinned candidate. This grants no rights to underlying source assets, datasets, or other extraction.',
                        'policy_file': 'plans/ocean-motion-linked-facts-use-decision.md'})
    decisions = {'schema': 'osw.preview-additional-source-use-decisions.v1', 'decision_date': '2026-11-08',
                 'candidate_build_sha256': supplement['candidate_build_sha256'], 'projection_report_sha256': sha(raw_report),
                 'scope': 'Exact added factual uses in the pinned preview projection, subject to asset/field verification before publication.',
                 'entries': entries, 'source_defined_reference_namespace_allowed': True, 'registry_join_promotion_allowed': False,
                 'original_provider_holds_unchanged': True, 'state_association_review_still_required': True,
                 'not_a_blanket_source_licence': True, 'not_a_publication_approval': True}
    for name, doc in [('contexts.json', supplement), ('source-use.json', decisions)]:
        (paths / name).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    manifest = {'schema': 'osw.preview-review-metadata.v1', 'candidate_build_sha256': supplement['candidate_build_sha256'],
                'context_citation_count': len(contexts), 'additional_source_use_decision_count': len(entries),
                'publication_approved': False, 'measurement_values_read_or_changed': False,
                'files': [{'path': name, 'sha256': sha((paths / name).read_bytes()), 'bytes': (paths / name).stat().st_size}
                          for name in ['contexts.json', 'source-use.json']]}
    (paths / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'status': 'REVIEW_METADATA_PREPARED_NOT_PUBLICATION_APPROVED', 'contexts': len(contexts), 'source_uses': len(entries)}))


if __name__ == '__main__':
    main()
