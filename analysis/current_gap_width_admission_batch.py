"""Extend the unchanged72-row source batch with one gated published width."""
import current_gap_admission_batch as source_batch
import eicc_t24_width_admission as width


def documents():
    return (*source_batch.documents(), width.evidence()[0])


def prepare(collections, identity_document, evidence_document, brazil_document, width_document):
    stage, base_receipt = source_batch.prepare(collections, identity_document, evidence_document, brazil_document)
    # The original source batch intentionally shares its physical collections.
    # Detach the three affected lists before appending a newly admitted width.
    touched = set(base_receipt['added_rows'])
    for name, _ in width.records(width_document):
        stage[name] = list(stage.get(name, []))
        touched.add(name)
    width.append(stage, width_document)
    receipt = {
        'schema': 'osw.current-gap-width-batch-receipt.v1',
        'status': 'prepared_scoped_width_batch_not_published',
        'canonical_delivery_verified': False,
        'source_batch': base_receipt,
        'added_rows': {name: len(stage.get(name, [])) - len(collections.get(name, [])) for name in sorted(touched)},
        'scoped_published_width_records_added': 1, 'raw_width_samples_added': 0,
        'annual_width_ranges_added': 0, 'geographic_width_geometries_added': 0,
        'prior_physical_rows_preserved': True,
    }
    if stage['widths'][:-1] != collections.get('widths', []):
        raise ValueError('Prior physical width rows changed')
    return stage, receipt


def append(collections, *documents):
    stage, receipt = prepare(collections, *documents)
    for name in receipt['added_rows']:
        collections[name] = stage[name]
    return receipt
