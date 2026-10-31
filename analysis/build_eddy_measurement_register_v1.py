"""Small retained JSON only: no engine, index or ocean-field processing."""
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
JSON_PATH='research/eddy-measurement-register-v1.json'
CSV_PATH='research/eddy-measurement-register-v1.csv'
RULES='plans/eddy-measurement-register-v1.md'


def pointer(document,path):
    value=document
    for token in path.strip('/').split('/'):
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


def build():
    pins={}
    def read(path):
        raw=(ROOT/path).read_bytes();pins[path]=hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    inventory_path='research/ocean-eddy-name-inventory.json';inventory=read(inventory_path)
    identities={'eddy:'+r['id']:r for r in inventory['entries']}
    assert len(identities)==136 and len(inventory['entries'])==136
    geo_path='research/named-eddy-geography.json';geo=read(geo_path)
    astrid_path='research/astrid-2000-radial-scale-scope-audit.json';astrid=read(astrid_path)
    rings_path='research/agulhas-guerra-2022-ring-radius-scope-audit.json';rings=read(rings_path)
    loops_path='research/named-loop-eddy-published-observations.json';loops=read(loops_path)
    recurrence_path='research/black-sea-eddy-recurrence.json';recurrence=read(recurrence_path)
    extra_path='research/eddy-measurement-register-source-facts-v1.json';extra=read(extra_path)
    for d in [rings,recurrence]:
        raw=(ROOT/d['protocol_file']).read_bytes();pin=hashlib.sha256(raw).hexdigest()
        assert pin==d['protocol_sha256'];pins[d['protocol_file']]=pin
    evidence=[]
    def add(identifier,owner,category,metric,value,unit,path,location,document,**kwargs):
        assert owner in identities and not any(r['id']==identifier for r in evidence)
        raw=pointer(document,location)
        row={'id':identifier,'entity_id':owner,'category':category,'metric':metric,
             'metric_label':metric.replace('_',' '),'value':value,'unit':unit,
             'lower_bound':None,'lower_bound_exclusive':False,'standard_deviation':None,
             'uncertainty':None,'sample_count':None,'period_start':None,'period_end':None,
             'period_label':None,'definition':None,'scope':None,'qualification':None,
             'source_claims':[],'value_conflict':False,'date_conflict':False,
             'source_url':raw.get('source_url') or document.get('source_url'),
             'source_locator':raw.get('source_locator'),'source_file':path,
             'source_pointer':location,'source_sha256':pins[path],'raw_record':raw,
             'rank_eligible':False,'geometry':None,'seasonal_playback_eligible':False,
             'whole_lifetime_inferred':False,'physical_state_join_eligible':False}
        row.update(kwargs)
        assert row['value'] is None or isinstance(row['value'],(int,float)) and row['value']>0
        assert row['source_url'] and row['source_locator'],identifier
        evidence.append(row)
    for n,r in enumerate(astrid['measurements']):
        add(r['id'],r['entity_id'],'size',r['metric'],r['value_km'],'km',astrid_path,f'/measurements/{n}',astrid,
            definition=r['definition'],scope=r['layer'],period_label=r['study_period_context'],
            qualification='Two-layer diagnostic model scale; retain each radius definition separately.')
    for key,entity in rings['entities'].items():
        assert next(r for r in geo['entries'] if r['id']==key)['ring_radius_audit_sha256']==pins[rings_path]
        for n,r in enumerate(entity['measurements']):
            add(r['id'],r['entity_id'],'size',r['metric'],r['value_km'],'km',rings_path,f'/entities/{key}/measurements/{n}',rings,
                source_locator='; '.join(c['source_locator'] for c in r['source_claims']),
                definition=r['definition'],scope=r['layer'],period_label=r['period_label'],
                source_claims=r['source_claims'],value_conflict=r['radius_conflict'],date_conflict=r['date_conflict'],
                qualification='Source radius and year conflicts remain unresolved. Consistent section values are individual points, not annual extrema or an interpolated series.')
    # Structured interpretation of existing prose, with exact expected text guards.
    loop_sizes={
        'published:kraken-2013':('coherent_core_mean_radius',100,'Approximately 100 km mean radius of the coherent core, a definition distinct from the outer instantaneous SSH footprint.'),
        'published:cameron-2009-observed':('author_reported_altimetric_diameter',300,'About 300 km diameter on 2009-01-20, as assessed by the authors from the altimetric eddy field.'),
        'published:darwin-2009-observed':('author_reported_altimetric_diameter',200,'About 200 km diameter on 2009-07-25, as assessed by the authors from the altimetric eddy field.')}
    for n,r in enumerate(loops['entries']):
        if r['eddy_id'] not in loop_sizes:continue
        metric,value,expected=loop_sizes[r['eddy_id']];assert r['reported_measure']==expected
        add(r['eddy_id']+'-size-reference','eddy:'+r['eddy_id'],'size',metric,value,'km',loops_path,f'/entries/{n}',loops,
            definition=r['reported_measure'],scope=r['interpretation'],
            period_label=(r['observation_start']+' to '+r['observation_end']) if 'kraken' in r['eddy_id'] else r['observation_start'],
            qualification='Approximate author-reported value. No radius/diameter conversion or outer footprint is inferred.')
        if r['eddy_id']=='published:kraken-2013':
            elapsed=(date.fromisoformat(r['observation_end'])-date.fromisoformat(r['observation_start'])).days
            add('kraken-2013-core-analysis-interval','eddy:'+r['eddy_id'],'duration','coherent_core_analysis_interval',elapsed,'day',loops_path,f'/entries/{n}',loops,
                period_start=r['observation_start'],period_end=r['observation_end'],
                definition='Elapsed days between the retained coherent-core analysis endpoints.',scope=r['interpretation'],
                qualification='Date subtraction, not a measured full lifetime, inclusive count or continuous observation cadence.')
    for n,r in enumerate(geo['entries']):
        if r.get('reported_track_period'):
            period=r['reported_track_period'];elapsed=(date.fromisoformat(period['end'])-date.fromisoformat(period['start'])).days
            add(r['id']+'-source-track-span','eddy:geography:'+r['id'],'duration','source_track_elapsed_span',elapsed,'day',geo_path,f'/entries/{n}',geo,
                source_url=geo['sources'][r['source']],source_locator='Retained reported_track_period; Guerra et al. (2022), individual-ring track discussion in section 3.1.',
                period_start=period['start'],period_end=period['end'],definition='Elapsed days between source-reported track endpoints.',
                scope=period.get('scope') or r.get('identity_note') or 'Source track window; first/last detections do not independently prove birth or death.',
                qualification='Source identity may span a split or merger. '+r.get('identity_note',r.get('formation',{}).get('note','No full physical lifetime inferred.')))
        if r.get('reported_lifetime_years_approx') is not None:
            for category,metric,value,unit in [('duration','author_reported_approximate_lifetime',r['reported_lifetime_years_approx'],'year'),('travel','author_reported_travel_lower_bound',None,'km')]:
                add(r['id']+'-'+metric,'eddy:geography:'+r['id'],category,metric,value,unit,geo_path,f'/entries/{n}',geo,
                    source_url=geo['sources'][r['source']],source_locator=r['reported_motion_source_locator'],
                    lower_bound=r['reported_travel_km_lower_bound'] if category=='travel' else None,lower_bound_exclusive=category=='travel',
                    definition='Source-reported approximate lifetime.' if category=='duration' else 'Strict lower bound on source-reported travel distance.',
                    scope=r['identity_note'],qualification='No exact start/end dates, calendar conversion, track rejoin or speed calculation inferred.')
    for n,r in enumerate(recurrence['entries']):
        common={'scope':r['scope_note'],'definition':'Published recurrent-region statistic; averaging window and detection threshold unspecified.',
                'qualification':'Recurring-region summary, not the lifespan of an independently dated individual.'}
        add(r['id']+'-presence',r['entity_id'],'recurrence',r['occurrence_metric'],r['reported_occurrence_days_per_year_approx'],'day/year',recurrence_path,f'/entries/{n}',recurrence,**common)
        if r['reported_event_lifetime_approx'] is not None:
            add(r['id']+'-event-duration',r['entity_id'],'duration','regional_'+r['event_lifetime_statistic']+'_event_lifetime',r['reported_event_lifetime_approx'],r['event_lifetime_unit'],recurrence_path,f'/entries/{n}',recurrence,**common)
    for n,r in enumerate(extra['records']):
        add(r['id'],r['entity_id'],'size',r['metric'],r['mean_radius_km'],'km',extra_path,f'/records/{n}',extra,
            standard_deviation=r['standard_deviation_km'],sample_count=r['table_sample_count'],
            definition=extra['definition'],scope=r['longitude_label']+'; long-lived Agulhas ring population, 1993-2016.',
            period_label='1993-2016',qualification=extra['qualification']+' '+r.get('qualification',''))
    records=[]
    for identifier,current in identities.items():
        owned=[r for r in evidence if r['entity_id']==identifier]
        geographic=next((r for r in geo['entries'] if 'eddy:geography:'+r['id']==identifier),None)
        published=next((r for r in loops['entries'] if 'eddy:'+r['eddy_id']==identifier),None)
        records.append({'entity_id':identifier,'name':current['name'],'basin':current['basin'],
            'identity_level':current['identity_level'],'source_collection':current['source_collection'],
            'source_url':current['source_url'],'source_pointer':'/entries/'+str(inventory['entries'].index(current)),
            'evidence_ids':[r['id'] for r in owned],'categories':sorted({r['category'] for r in owned}),
            'size_gap':not any(r['category']=='size' for r in owned),
            'duration_gap':not any(r['category']=='duration' for r in owned),
            'status':'has_measurements' if owned else 'needs_measurements',
            'event_date':current.get('source_event_date') if current['identity_evidence']=='numbered_primary_separation' else None,
            'date_context':current.get('date_evidence'),
            'paper_window_context':({'start':published['observation_start'],'end':published['observation_end'],'interpretation':published['interpretation']} if published else None),
            'identity_note':geographic.get('identity_note') if geographic else None,
            'possible_same_ring_as':published.get('possible_same_ring_as_horizon_id') if published else None,
            'candidate_crosswalk_is_verified':False,'whole_lifetime_days':None,
            'annual_size_range_km':None,'closed_footprint':None,
            'current_card_url':'object.html?id='+identifier,'atlas_url':'index.html'+current['atlas_anchor'],
            'next_action':'Recover definition-qualified dated size and duration evidence; verify identity before joining satellite detections.'})
    owners=lambda category:{r['entity_id'] for r in evidence if r['category']==category}
    return {'schema':'osw.eddy-measurement-register.v1','status':'FIRST_SIZE_DURATION_BATCH_GAPS_OPEN',
        'rules_file':RULES,'rules_sha256':hashlib.sha256((ROOT/RULES).read_bytes()).hexdigest(),
        'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_sha256':pins,
        'scope':inventory['scope'],'identity_rule':'Source records remain separate; possible Horizon/published matches are not verified identity joins.',
        'release_scope':'Full research candidate: 136 source identities. The separate rights-screened release excludes 96 Horizon registry labels.',
        'counts':{'identities':len(records),'individual_source_records':sum(r['identity_level']=='individual_eddy' for r in records),
            'recurrent_regions':sum(r['identity_level']=='recurrent_eddy_region' for r in records),'families':sum(r['identity_level']=='eddy_family' for r in records),
            'evidence_records':len(evidence),'size_records':sum(r['category']=='size' for r in evidence),
            'size_owners':len(owners('size')),'duration_owners':len(owners('duration')),'recurrence_owners':len(owners('recurrence')),
            'identities_with_measurements':sum(bool(r['evidence_ids']) for r in records),
            'identities_without_measurements':sum(not r['evidence_ids'] for r in records),
            'conflicted_size_records':sum(r['value_conflict'] for r in evidence),
            'source_track_spans':sum(r['metric']=='source_track_elapsed_span' for r in evidence)},
        'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def main():
    document=build();(ROOT/JSON_PATH).write_bytes((json.dumps(document,indent=2,ensure_ascii=False)+'\n').encode())
    fields=['entity_id','id','category','metric','value','unit','lower_bound','lower_bound_exclusive','standard_deviation','sample_count','period_start','period_end','period_label','value_conflict','date_conflict','source_claims_json','definition','scope','qualification','source_url','source_locator','source_file','source_pointer','source_sha256']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader()
    for r in document['evidence']:writer.writerow({**r,'source_claims_json':json.dumps(r['source_claims'],ensure_ascii=False)})
    (ROOT/CSV_PATH).write_bytes(out.getvalue().encode());print(json.dumps(document['counts']))


if __name__=='__main__':main()
