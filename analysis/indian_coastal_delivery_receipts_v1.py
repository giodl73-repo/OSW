"""Pure receipt checks for a saved coastal candidate; no packet reads or publish."""
SOURCE_RUN = 40100017734
SOURCE_COMMIT = '0c2f0dc67a9ba25cbf488f634702b05f30401f2f'
BRANCH = 'codex/current-measurement-gaps'
WORKFLOW = '.github/workflows/indian-coastal-context-candidate.yml'
CONTRACT_SHA = '17609dd034f3739f94965747d3e286b2c3ec41a9bdfd6d125f6e650562febf56'
PARENT = '045d6fd80b871ba7a9863154f390d7c84a450f4b3e960b3f5f4e27b8d6a009b0'
PACKET = '369004f99601dd53db77b50cb671c3875cd350aec6df66d56b0781326b37fc5c'
ENTITIES = ['current:east-african-coastal', 'current:south-java']
STEPS = [
    'Require serialized candidate phase and committed source inputs',
    'Check source scope, candidate preservation and resource refusal',
    'Export one preserved complete-parent candidate',
    'Validate native code then compile the same engine to WASM',
    'Install one browser after compilation finishes',
    'Check exact new contexts, both cards, source index and phone navigation',
    'Preserve existing cards, all current identities and the complete atlas',
    'Run all fourteen existing source-matrix gates sequentially',
]


def verify_run(run, jobs):
    expected = {'id': SOURCE_RUN, 'head_sha': SOURCE_COMMIT, 'head_branch': BRANCH,
                'event': 'push', 'path': WORKFLOW, 'status': 'completed', 'conclusion': 'success'}
    if any(run.get(key) != value for key, value in expected.items()):
        raise ValueError('Exact completed coastal validation run required')
    rows = jobs.get('jobs', [])
    if (jobs.get('total_count') != len(rows) or len(rows) != 2
            or {row.get('name') for row in rows} != {'select-phase', 'candidate-and-views'}
            or any(row.get('status') != 'completed' or row.get('conclusion') != 'success' for row in rows)):
        raise ValueError('Both exact sequential validation jobs must succeed')
    heavy = next(row for row in rows if row['name'] == 'candidate-and-views')
    steps = heavy.get('steps', [])
    if len({step.get('name') for step in steps}) != len(steps):
        raise ValueError('Duplicate validation step names')
    selected = []
    for name in STEPS:
        found = [step for step in steps if step.get('name') == name]
        if len(found) != 1 or found[0].get('status') != 'completed' or found[0].get('conclusion') != 'success':
            raise ValueError('Required complete gate missing/failed: ' + name)
        number = found[0].get('number')
        if type(number) is not int:selected.append(-1)
        else:selected.append(number)
    if any(number <= 0 for number in selected) or any(a >= b for a, b in zip(selected, selected[1:])):
        raise ValueError('Export/native/WASM/browser/source gate order changed')


def verify_receipts(source, browser, prior_cards, source_document_hashes):
    if (source.get('schema') != 'osw.indian-coastal-context-candidate.v1' or source.get('status') != 'PASS'
            or source.get('published') is not False or source.get('contract_sha256') != CONTRACT_SHA
            or source.get('parent_logical_sha256') != PARENT
            or source.get('source_originals_redistributed') is not False
            or source.get('scientific_release_published') is not False):
        raise ValueError('Wrong or unverified coastal source export')
    candidate = source.get('candidate', {})
    if candidate != {'logical_sha256': PACKET, 'logical_bytes': 189905442,
                     'objects': 246, 'rows': 108551, 'named_currents': 106, 'widths': 172}:
        raise ValueError('Wrong saved candidate inventory or identity')
    admission = source.get('admission', {})
    if (admission.get('new_rows') != 7 or admission.get('changed_owner_ids') != ENTITIES
            or admission.get('canonical_delivery_verified') is not False
            or any(type(admission.get(key)) is not int or admission[key] != 0 for key in
                   ['new_paired_widths', 'new_ranked_lengths', 'new_raw_observations',
                    'new_annual_ranges', 'new_current_geometry_or_state_joins'])):
        raise ValueError('Context export promoted to physical measurement coverage')
    preservation = admission.get('preservation', {})
    if (preservation.get('unchanged_objects_verified') != 244 or preservation.get('new_rows') != 7
            or preservation.get('changed_owner_ids') != ENTITIES
            or any(preservation.get(key) is not True for key in
                   ['all_prior_nonobject_rows_exact', 'physical_fields_and_capabilities_preserved',
                    'qualified_published_length_ranks_preserved', 'source_arrays_preserved'])):
        raise ValueError('Prior current/eddy/physical source preservation missing')
    index = source.get('index_extension', {})
    old_receipt = 'research/source-data/painter-eacc-2020/acquisition.json'
    if (len(source_document_hashes) != 6 or old_receipt not in source_document_hashes
            or source_document_hashes.get('research/indian-coastal-dimension-context-query-contract-v1.json') != CONTRACT_SHA):
        raise ValueError('All six pinned source documents including the contract are required')
    if (index.get('original_sources_verified') != 589 or index.get('original_source_strings_preserved') != 588
            or index.get('candidate_source_count') != 594 or index.get('scientific_source_documents_replaced') != 0
            or index.get('replaced_source_paths') != ['research/ocean-motion-dashboard.json']
            or len(index.get('added_source_paths', [])) != 5
            or set(index['added_source_paths']) != set(source_document_hashes) - {old_receipt}
            or index.get('candidate_index_sha256') != 'a988399ca8cba9f3ba72c621c8460581b105bc9fa7f04db2ddc5f933f46fd780'):
        raise ValueError('Historical source index preservation changed')
    if (browser.get('status') != 'PASS' or browser.get('bundle_sha256') != PACKET
            or browser.get('contract_sha256') != CONTRACT_SHA or browser.get('native_wasm_cards') != ENTITIES
            or browser.get('record_queries') != 7 or browser.get('keyboard_queries') != ENTITIES
            or type(browser.get('new_physical_measurements')) is not int or browser['new_physical_measurements'] != 0
            or browser.get('errors') != [] or browser.get('original_downloads') != []):
        raise ValueError('Exact card/query/source browser evidence missing')
    if browser.get('phone_widths_verified') != [
            {'entity_id': entity, 'width_px': width} for entity in ENTITIES for width in [320, 390]]:
        raise ValueError('Both phone widths required for both context cards')
    sources = browser.get('source_documents', [])
    if (len(sources) != len(source_document_hashes)
            or {row.get('path'): row.get('sha256') for row in sources} != source_document_hashes):
        raise ValueError('All exact source documents must be queried in native and WASM')
    if (prior_cards.get('status') != 'PASS' or prior_cards.get('bundle_sha256') != PACKET
            or prior_cards.get('named_currents') != 106
            or prior_cards.get('native_wasm_object_views_equal') !=
                ['west-india-coastal', 'east-india-coastal', 'east-african-coastal', 'south-java', 'brazil']
            or any(prior_cards.get(key) is not True for key in
                   ['keyboard_evidence_query', 'dashboard_all_106_currents', 'dashboard_alias_native_wasm_parity'])
            or prior_cards.get('source_context_coverage_modes_verified') != 4
            or prior_cards.get('phone_horizontal_overflow') is not False
            or prior_cards.get('errors') != [] or prior_cards.get('original_downloads') != []):
        raise ValueError('Preceding cards/dashboard and navigation evidence missing')
    return {'candidate': candidate, 'preservation': preservation,
            'native_wasm_and_browser_receipts_verified': True, 'working_packet_installed': False}
