import copy,json
from collections import Counter
from decimal import Decimal
from unittest.mock import patch
import pytest
import build_asca_calendar_distributions as calendar

def test_type7_quantiles_and_declared_decimal_readback():
    values=[Decimal('1'),Decimal('2'),Decimal('4'),Decimal('8')]
    assert [calendar.quantile(values,p) for p in [0,'.25','.5','.75',1]]==[1,1.75,3,5,8]
    assert calendar.quantile([],'.5') is None
    assert calendar.quantile([Decimal('1.2345675')],'.5')==1.234568
    with pytest.raises(ValueError):calendar.statistics([None])

def test_all_case_partitions_and_failures_are_conserved():
    doc=calendar.verify()
    for fraction in [.4,.5,.6]:
        whole=next(r for r in doc['records'] if r['cohort_kind']=='source_period' and r['threshold_fraction']==fraction)
        for kind in ['calendar_year','calendar_month']:
            rows=[r for r in doc['records'] if r['cohort_kind']==kind and r['threshold_fraction']==fraction]
            assert sorted(i for r in rows for i in r['source_time_indices'])==list(range(931))
            assert sum(r['resolved_samples'] for r in rows)==whole['resolved_samples']
            assert sorted(i for r in rows for i in r['resolved_source_time_indices'])==whole['resolved_source_time_indices']
            statuses=Counter()
            for r in rows:statuses.update(r['status_counts'])
            assert dict(statuses)==whole['status_counts']

def test_calendar_support_does_not_hide_failed_spans_or_partial_years():
    doc=calendar.verify()
    years={r['year']:r for r in doc['records'] if r['cohort_kind']=='calendar_year' and r['primary_convention']}
    assert years[2017]['complete_nominal_calendar_year_support'] is True
    assert (years[2017]['attempted_samples'],years[2017]['resolved_samples'],years[2017]['unresolved_samples'])==(438,131,307)
    assert not years[2016]['complete_nominal_calendar_year_support'] and not years[2018]['complete_nominal_calendar_year_support']
    assert years[2016]['missing_calendar_months']==[1,2,3]
    assert doc['source_clock_step_seconds_counts']=={'71936':465,'72064':465}
    assert not doc['source_clock_modified'] and not doc['time_samples_independent']
    for r in doc['records']:
        assert r['annual_physical_width_range_km'] is None
        assert not r['width_measurement_admitted'] and not r['seasonal_map_playback_eligible']
        assert not r['quantiles_are_confidence_intervals'] and not r['is_climatology']

def test_no_resolved_values_stay_null_and_status_inconsistency_rejects():
    rows=[{'source_time_index':0,'observed_at':'2017-01-01T00:00:00Z','year':2017,'month':1,
           'cases':[{'fraction':Decimal(str(f)),'span_km':None,'status':'unresolved_no_finite_v'} for f in [.4,.5,.6]]}]
    report=calendar.summarize(rows,{(2017,1):True},'calendar_year',2017)
    assert all(r['statistics']['count']==0 and all(v is None for k,v in r['statistics'].items() if k!='count') for r in report)
    bad=copy.deepcopy(rows);bad[0]['cases'][0]['status']='resolved_component_span'
    with pytest.raises(ValueError,match='status/span'):calendar.summarize(bad,{(2017,1):True},'calendar_year',2017)

def test_source_rebinding_and_derived_record_edits_reject(tmp_path):
    doc=calendar.verify()
    (tmp_path/calendar.REPORT).parent.mkdir(parents=True)
    corrupted=copy.deepcopy(doc);corrupted['records'][0]['statistics']['median_km']=999
    (tmp_path/calendar.REPORT).write_bytes(calendar.encoded(corrupted))
    with patch.object(calendar,'ROOT',tmp_path),patch.object(calendar,'build',return_value=doc):
        with pytest.raises(ValueError,match='Stale ASCA calendar'):calendar.verify()
    with patch.object(calendar,'digest',return_value='0'*64):
        with pytest.raises(ValueError,match='Changed ASCA calendar source'):calendar.build()
