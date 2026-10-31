"""Versioned complete atlas card and support-page presentation projection."""
import copy
import html

import pacific_secc_reference_delivery_v1 as prior
import pacific_secc_publication_admission_v1 as admission

PAGE = admission.query.PAGE
PREPARED_PAGE = 'research/pacific-secc-reference-presentation-history-v1/support-prepared.html.source'
RENDERING_ROLE = 'derived_inline_editorial_reach_card_not_additional_observation'


def catalog_projection(catalog, collections):
    result = admission.runtime.catalog_projection(catalog, collections, admission.runtime.build_contract())
    entries = [r for r in result['candidates'] if r['id'] == admission.query.ROUTE]
    if len(entries) != 1:
        raise ValueError('Exactly one new Pacific reference atlas card required')
    entry = entries[0]
    entry['figure'] = entry['figure_file']
    entry['report_inline']['rendering_role'] = RENDERING_ROLE
    return result


def support_page(root=admission.ROOT):
    prepared = (root / PREPARED_PAGE).read_bytes()
    if prepared != admission.query.page(admission.query.build_contract()):
        raise ValueError('Exact saved prepared support page required')
    old = '<section><h2>Query and atlas delivery</h2><p>This source page is prepared. The new route is awaiting native/WASM and atlas installation; installed coverage totals are unchanged.</p>\n</section>'
    document = admission.query.build_contract()
    new = ('<section><h2>Explore this reference</h2><p>'
           '<a href="' + html.escape(document['query_url_after_installation'], quote=True)
           + '">Open the reference record and query map</a></p><p><a href="'
           + html.escape(document['atlas_url_after_installation'], quote=True)
           + '">Explore this current in the global atlas</a></p>'
           '<p>The route is an editorial regional reference. Whole-current length and seasonal dimensions remain unresolved.</p></section>')
    text = prepared.decode()
    if text.count(old) != 1:
        raise ValueError('Unique prepared delivery-status section required')
    return text.replace(old, new).encode()


candidate = prior.candidate
source_index = prior.source_index
packet_manifest = prior.packet_manifest
