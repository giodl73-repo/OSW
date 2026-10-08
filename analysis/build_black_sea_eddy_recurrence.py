"""Reproduce scoped prose extraction; never infer dated events or footprints."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUTPUT='research/black-sea-eddy-recurrence.json'
SOURCE='research/source-data/korotaev-black-sea-2011/journal-article.pdf'
PROTOCOL='plans/black-sea-eddy-recurrence-protocol-v1.md'
SOURCE_SHA='26d601a3d6e980c773bc3ca13ba25cc4f9b86fb61e64cea463ef5da8ac4852ab'
# Manually checked prose, section 3.1, printed p. 633, right column.
# A month remains a month; occurrence per year is not an event lifetime.
EXTRACTION=[
 ('bosphorus',260,85,'day','mean','No preferred season specified.'),
 ('batumi',210,None,None,None,'Usually forms in early March and persists until late October; these are narrative bounds, not exact event dates.'),
 ('sukhumi',120,1,'month','typical','Mostly autumn to early winter, following collapse of the Batumi gyre.'),
 ('caucasus',160,None,None,None,'Appearance begins in spring; no exact month or end date supplied.'),
 ('kerch',240,80,'day','mean','Spring and autumn favored.'),
 ('crimea',115,1,'month','mean','Mainly August and September.'),
 ('sevastopol',150,50,'day','mean','Winter and summer favored for formation.'),
 ('constantsa',190,50,'day','typical','No preferred season specified.'),
 ('kaliakra',190,50,'day','typical','No preferred season specified.'),
]

def build():
    raw=(ROOT/SOURCE).read_bytes()
    if len(raw)!=5120633 or hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise ValueError('Changed Black Sea primary PDF; renewed extraction required')
    geo=json.loads((ROOT/'research/named-eddy-geography.json').read_bytes())
    identities={r['id']:r for r in geo['entries']}
    rows=[]
    for stem,occurrence,lifetime,unit,statistic,season in EXTRACTION:
        source_id=stem+'-eddy-region'; identity=identities[source_id]
        if identity['identity_level']!='recurrent_eddy_region' or identity['basin']!='Black Sea':
            raise ValueError('Black Sea recurrence identity changed')
        rows.append({'id':'eddy-recurrence:korotaev-2011:'+stem,
            'entity_id':'eddy:geography:'+source_id,'label':identity['name'],
            'identity_level':'recurrent_eddy_region','basin':'Black Sea',
            'related_current_id':'black-sea-rim','relation_role':'published_circulation_context_not_dated_interaction',
            'status':'editorial_published_summary_scientific_review_pending',
            'reported_occurrence_days_per_year_approx':occurrence,
            'occurrence_metric':'author_reported_average_presence_days_per_year',
            'reported_event_lifetime_approx':lifetime,'event_lifetime_unit':unit,
            'event_lifetime_statistic':statistic,'seasonal_description':season,
            'observation_period':None,'calendar_months':None,'uncertainty_interval':None,
            'geometry':None,'individual_track_id':None,'dated_event_identity':False,
            'seasonal_playback_eligible':False,'physical_state_join_eligible':False,
            'source_url':'https://os.copernicus.org/articles/7/629/2011/os-7-629-2011.pdf',
            'source_locator':'Section 3.1, printed page 633 (PDF page index 4), coastal anticyclone paragraph spanning both columns.',
            'source_citation':'Korotaev et al. (2011), Ocean Science 7, 629–649, doi:10.5194/os-7-629-2011.',
            'source_document_sha256':SOURCE_SHA,
            'scope_note':'Published regional recurrence summary, not a dated individual or current-day forecast. Presence days can comprise separate events; month lifetimes are not converted to days. The summary does not specify its averaging window or detection criterion.'})
    return {'schema':'osw.eddy-recurrence-summary.v1','as_of':'2026-10-07',
        'source_document_file':SOURCE,'source_document_sha256':SOURCE_SHA,
        'source_document_bytes':len(raw),'source_license':'CC Attribution 3.0',
        'protocol_file':PROTOCOL,'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest(),
        'generator_file':'analysis/build_black_sea_eddy_recurrence.py',
        'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Nine named recurrent Black Sea regions with numerical occurrence evidence in section 3.1. Danube has no extracted numerical recurrence here; the collection is not a global eddy census.',
        'entries':rows}

def validate(document):
    if document!=build():raise ValueError('Black Sea recurrence differs from pinned prose extraction')

if __name__=='__main__':
    document=build();(ROOT/OUTPUT).write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Built nine source-scoped Black Sea recurrence records')
