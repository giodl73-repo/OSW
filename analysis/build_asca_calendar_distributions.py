"""Conditional calendar summaries of retained ASCA cases, including failures."""
from collections import Counter
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/agulhas-asca-100m-dated-component-spans.json'
SOURCE_SHA='59c839aa4ed6363ddfa75af01a2932d73763424c19cb04cd075ee1a9b2ea3e3a'
PROTOCOL='plans/asca-component-calendar-distribution-protocol-v1.md'
REPORT='research/asca-component-calendar-distributions.json'
OPERATOR='analysis/build_asca_calendar_distributions.py'
ID='diagnostic:agulhas-asca100m-calendar-distributions'
FRACTIONS=(40,50,60)

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def readback(value):
    return float(value.quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP))

def quantile(values,p):
    if not values:return None
    values=sorted(Decimal(str(v)) for v in values)
    h=Decimal(len(values)-1)*Decimal(str(p));lo=int(h)
    return readback(values[lo] if lo==len(values)-1 else values[lo]+(h-lo)*(values[lo+1]-values[lo]))

def statistics(values):
    if any(v is None or not Decimal(str(v)).is_finite() or Decimal(str(v))<=0 for v in values):
        raise ValueError('Invalid resolved ASCA span')
    return {'count':len(values),'minimum_km':quantile(values,0),'q25_km':quantile(values,'.25'),
            'median_km':quantile(values,'.5'),'q75_km':quantile(values,'.75'),'maximum_km':quantile(values,1)}

def summarize(rows,months,kind,key):
    if not rows:raise ValueError('Empty ASCA calendar cohort')
    present=sorted({(r['year'],r['month']) for r in rows})
    supports=[{'year':y,'month':m,'complete_calendar_time_support':months[y,m]} for y,m in present]
    source_months=sorted({m for _,m in present})
    year_complete=kind=='calendar_year' and len(supports)==12 and all(r['complete_calendar_time_support'] for r in supports)
    records=[]
    for percentage in FRACTIONS:
        cases=[]
        for profile in rows:
            case,= [c for c in profile['cases'] if c['fraction']==Decimal(percentage)/100]
            if (case['span_km'] is not None)!=(case['status']=='resolved_component_span'):
                raise ValueError('ASCA status/span disagreement')
            cases.append((profile,case))
        resolved=[(r,c) for r,c in cases if c['span_km'] is not None]
        records.append({'id':f'asca-calendar:{kind}:{key}:f{percentage}','current_id':'agulhas',
            'cohort_kind':kind,'cohort_key':key,'year':key if kind=='calendar_year' else None,
            'month':key if kind=='calendar_month' else None,'threshold_fraction':percentage/100,
            'primary_convention':percentage==50,'depth_m':100,'component':'-v',
            'attempted_samples':len(cases),'resolved_samples':len(resolved),'unresolved_samples':len(cases)-len(resolved),
            'status_counts':dict(sorted(Counter(c['status'] for _,c in cases).items())),
            'source_time_indices':[r['source_time_index'] for r in rows],
            'resolved_source_time_indices':[r['source_time_index'] for r,_ in resolved],
            'first_observed_at':rows[0]['observed_at'],'last_observed_at':rows[-1]['observed_at'],
            'source_month_bins':supports,'calendar_months_present':source_months,
            'missing_calendar_months':sorted(set(range(1,13))-set(source_months)) if kind=='calendar_year' else None,
            'complete_nominal_calendar_year_support':year_complete if kind=='calendar_year' else None,
            'statistics':statistics([c['span_km'] for _,c in resolved]),
            'statistics_conditioned_on_resolved_spans':True,'time_samples_independent':False,
            'is_climatology':False,'quantiles_are_confidence_intervals':False,
            'width_measurement_admitted':False,'annual_physical_width_range_km':None,
            'geographic_current_edges':None,'seasonal_map_playback_eligible':False,
            'source_file':SOURCE,'source_profiles_pointer':'/profiles'})
    return records

def build():
    if digest(SOURCE)!=SOURCE_SHA:raise ValueError('Changed ASCA calendar source; renew declared protocol first')
    source=json.loads((ROOT/SOURCE).read_bytes(),parse_float=Decimal)
    if source['operator']['primary_fraction']!=Decimal('.5') or source['operator']['component']!='-v':
        raise ValueError('Changed ASCA primary convention')
    rows=source['profiles']
    if len(rows)!=931 or sum(len(r['cases']) for r in rows)!=2793:raise ValueError('Incomplete ASCA cases')
    dates=[datetime.fromisoformat(r['observed_at'].replace('Z','+00:00')) for r in rows]
    if any(a>=b for a,b in zip(dates,dates[1:])):raise ValueError('Non-increasing ASCA timestamps')
    for i,(r,t) in enumerate(zip(rows,dates)):
        if (r['source_time_index'],r['year'],r['month'])!=(i,t.year,t.month):raise ValueError('Changed ASCA time association')
    months={}
    for item in source['monthly_summaries']:
        key=(item['year'],item['month'])
        if key in months or type(item['complete_calendar_time_support']) is not bool:raise ValueError('Changed source-month support')
        indices=[r['source_time_index'] for r in rows if (r['year'],r['month'])==key]
        if indices!=item['source_time_indices']:raise ValueError('Changed source-month membership')
        months[key]=item['complete_calendar_time_support']
    if set(months)!={(r['year'],r['month']) for r in rows}:raise ValueError('Missing source months')
    records=summarize(rows,months,'source_period','all')
    for year in sorted({r['year'] for r in rows}):
        records+=summarize([r for r in rows if r['year']==year],months,'calendar_year',year)
    for month in range(1,13):
        records+=summarize([r for r in rows if r['month']==month],months,'calendar_month',month)
    return {'schema':'osw.asca-component-calendar-distributions.v1',
        'status':'conditional_source_sample_distributions_not_physical_width',
        'current_id':'agulhas','entity_id':'current:agulhas','depth_m':100,
        'input_sha256':{SOURCE:SOURCE_SHA,PROTOCOL:digest(PROTOCOL),OPERATOR:digest(OPERATOR)},
        'source_file':SOURCE,'source_doi':source['source_doi'],'source_url':source['source_url'],
        'source_citation':source['source_citation'],'source_license':source['source_license'],
        'source_method':source['source_method'],'source_quality_limits':source['interpretation'],
        'source_first_date':rows[0]['observed_at'],'source_last_date':rows[-1]['observed_at'],
        'unique_source_profiles':931,'unique_threshold_attempts':2793,'records':records,
        'quantile_rule':'type7; Decimal arithmetic from stored spans; final km readback6places half up',
        'weighting':'Each mapped source timestamp once per cohort/threshold; no equal-year weighting; no pooled thresholds.',
        'source_clock_step_seconds_counts':dict(sorted(Counter(str(int((b-a).total_seconds())) for a,b in zip(dates,dates[1:])).items())),
        'source_clock_modified':False,'nominal_time_step_hours':20,'low_pass_filter_hours':40,
        'time_samples_independent':False,'is_climatology':False,'percentiles_are_confidence_intervals':False,
        'physical_width_admitted':False,'whole_current_width_km':None,'annual_physical_width_range_km':None,
        'geographic_current_edges':None,'seasonal_map_playback_eligible':False,
        'limitations':['Conditional statistics exclude unresolved spans but retain their counts and membership.',
            'Full nominal calendar support does not imply all attempts resolve or physical annual extrema were observed.',
            'Partial endpoint years and uneven pooled-month support cannot establish an interannual trend or climatology.',
            'Fixed-array -v component spans are not flow-normal current widths; all source quality limitations remain.']}

def verify():
    expected=build()
    if (ROOT/REPORT).read_bytes()!=encoded(expected):raise ValueError('Stale ASCA calendar distributions')
    return expected

def record(document):
    return {'id':ID,'label':'Agulhas ASCA100m source-sample calendar distributions','entity_id':'current:agulhas',
            'current_id':'agulhas','status':document['status'],'rank_eligible':False,'source_file':REPORT,
            'source_file_sha256':digest(REPORT),'source_json':(ROOT/REPORT).read_text(encoding='utf-8'),'document':document}

def verify_inputs():
    document=verify();figure_path='research/asca-component-calendar-distributions-figure.json'
    figure=json.loads((ROOT/figure_path).read_bytes())
    if figure['source_file']!=REPORT or figure['source_sha256']!=digest(REPORT) or figure['primary_fraction']!=.5 or figure['plotted_groups']!=16:
        raise ValueError('Changed ASCA calendar figure source or coverage')
    inputs={**document['input_sha256'],REPORT:digest(REPORT),figure_path:digest(figure_path),
        figure['generator_file']:figure['generator_sha256']}
    for asset in figure['figures'].values():inputs[asset['file']]=asset['sha256']
    for path,pin in inputs.items():
        if digest(path)!=pin:raise ValueError('Changed ASCA calendar dependency: '+path)
    return document,figure,inputs

if __name__=='__main__':
    doc=build();(ROOT/REPORT).write_bytes(encoded(doc))
    print(json.dumps({'records':len(doc['records']),'unique_profiles':931,'unique_attempts':2793,'physical_width_admitted':False}))
