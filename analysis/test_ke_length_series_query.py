"""Complete graph-series admission and atomic failure; scientific bytes frozen."""
import copy
import json

import pytest

import ke_length_series_query as query


def fixture():
    previous = json.loads((query.ROOT / query.BASE).read_text(encoding='utf8'))
    lab = json.loads((query.ROOT / 'research/labrador-latitude-gate-bound-v1.json').read_text(encoding='utf8'))
    rows = copy.deepcopy(previous['length_assessments'])
    rows = [lab['length_assessment'] if r['entity_id'] == 'current:labrador' else r for r in rows]
    return {'length_assessments': rows, 'measurements': [], 'claims': [], 'sources': [],
            'widths': copy.deepcopy(previous['widths'])}


def test_complete_header_readings_and_unranked_assessment_preserve_other_data():
    header, pins = query.evidence()
    collections = fixture()
    old = copy.deepcopy(collections)
    query.append(collections, header)
    assert len(query.records(header)) == 1617
    assert collections['current_length_series'] == [header]
    assert collections['current_length_readings'] == query.reading_rows(header)
    assert len(collections['current_length_readings']) == 1612
    assert [r['graph_reading_order'] for r in collections['current_length_readings']] == list(range(1612))
    for before, after in zip(old['length_assessments'], collections['length_assessments']):
        if before['entity_id'] == query.ENTITY:
            assert after == header['length_assessment']
            assert after['evidence_status'] == 'regional_plot_series'
            assert after['whole_current_evidence_status'] == 'unmeasured'
            assert after['published_length_km'] is None and after['lower_bound_km'] is None
            assert after['rank_eligible'] is False
        else:
            assert after == before
    assert collections['widths'] == old['widths']
    assert sum(r['rank_eligible'] for r in collections['length_assessments']) == 13
    assert header['measurement']['value'] == [1120, 4660]
    assert header['claim']['value'] == [1120, 4660]
    assert header['source_facts_phase'] == 'reviewed_before_numeric_extraction'
    assert query.FILE in pins


@pytest.mark.parametrize('collection,index', [('current_length_series', 0), ('current_length_readings', 1600),
                                            ('measurements', 0), ('claims', 0), ('sources', 0), ('sources', 1)])
def test_duplicate_any_record_rejects_before_any_mutation(collection, index):
    header, _ = query.evidence()
    rows = [r for name, r in query.records(header) if name == collection]
    current = fixture()
    current.setdefault(collection, []).append(copy.deepcopy(rows[index]))
    before = copy.deepcopy(current)
    with pytest.raises(ValueError, match='Duplicate'):
        query.append(current, header)
    assert current == before


def test_changed_prior_or_unverified_header_rejects_atomically():
    header, _ = query.evidence()
    for mode in ('prior', 'header'):
        current = fixture()
        candidate = copy.deepcopy(header)
        if mode == 'prior':
            next(r for r in current['length_assessments'] if r['entity_id'] == query.ENTITY)['rank_eligible'] = True
        else:
            candidate['measurement']['annual_length_range_km'] = [1120, 4660]
        before = copy.deepcopy(current)
        with pytest.raises(ValueError):
            query.append(current, candidate)
        assert current == before


def test_links_offer_complete_ordered_readings_and_scoped_provenance():
    from urllib.parse import parse_qs, urlparse
    header, _ = query.evidence()
    links = query.links(header)
    assert len(links) == 5 and links[0]['url'].endswith('.svg')
    assert '1,120' in links[0]['label'] and '4,660' in links[0]['label']
    request = json.loads(parse_qs(urlparse(links[2]['url']).query)['q'][0])
    assert request['collection'] == 'current_length_readings'
    assert request['filters'] == [{'field': 'series_id', 'op': 'eq', 'value': header['id']}]
    assert request['sort'] == {'field': 'graph_reading_order', 'direction': 'asc'}
    assert request['limit'] == 100
