"""Year orchestration preserves frozen operators and checks shared source hours."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np

import build_norkyst_continuous_year as year


class ContinuousYearTests(unittest.TestCase):
    def test_complete_year_reconstructs_from_every_original_without_overwriting_assets(self):
        report=json.loads((year.FOLDER/'section-diagnostic-year.json').read_bytes())
        maps=json.loads((year.ROOT/report['regional_maps']['file']).read_bytes())
        data=year.load_sections(year.FOLDER/'acquisition-year.json',year.FOLDER/'acquisition-pilot.json')
        self.assertEqual(len(data['epochs']),8856)
        self.assertEqual(len(data['historical_noon_matches']),12)
        self.assertEqual(len(data['pilot_overlap_dates']),70)
        self.assertEqual(report['calendar_hours'],8784)
        self.assertEqual(report['completed_months'],list(range(1,13)))
        self.assertTrue(report['complete_annual_section_support'])
        self.assertFalse(report['annual_extrema_eligible'])
        self.assertFalse(report['new_width_record_admitted'])
        self.assertIsNone(report['whole_current_width_km'])
        self.assertIsNone(report['annual_width_range_km'])
        self.assertEqual(report['variable_units'],{'salinity':'1','u_eastward':'m/s','v_northward':'m/s'})
        self.assertEqual(year.source.sha((year.ROOT/report['regional_maps']['file']).read_bytes()),report['regional_maps']['sha256'])
        total=0
        for month,times,raw,lowpass in year.monthly_sections(data):
            total+=len(times);entry=report['months'][month-1];asset=report['monthly_assets'][month-1]
            self.assertEqual(asset['month'],month)
            self.assertEqual(year.source.sha((year.ROOT/asset['file']).read_bytes()),asset['sha256'])
            with np.load(year.ROOT/asset['file'],allow_pickle=False) as saved:
                np.testing.assert_array_equal(times,saved['epoch_seconds'])
                for index,name in enumerate(year.source.VARIABLES):
                    for kind,values in [('raw',raw[:,:,index]),('lowpass',lowpass[:,:,index])]:
                        np.testing.assert_allclose(values,saved[kind+'_'+name],rtol=0,atol=1e-11,equal_nan=True)
                        actual=year.operators.summarize(values);expected=entry['summary'][name][kind]
                        self.assertEqual(actual['valid_hours'],expected['valid_hours'])
                        for stat in ['mean','standard_deviation','p05','median','p95']:
                            np.testing.assert_allclose(actual[stat],expected[stat],rtol=0,atol=1.1e-8)
            for kind in ['raw','lowpass']:
                native=data['regional_maps'][month][kind];retained=maps['months'][month-1][kind]
                np.testing.assert_array_equal(native['valid_source_hours'],retained['valid_source_hours'])
                for index,name in enumerate(year.source.VARIABLES):
                    np.testing.assert_allclose(native['mean'][:,:,index],retained['mean'][name],rtol=0,atol=1e-11,equal_nan=True)
        self.assertEqual(total,8784)

    def test_regional_arrow_directions_match_the_existing_map_projection(self):
        from build_norkyst_ingoy_maps import rotated_vectors
        document=json.loads((year.FOLDER/'regional-monthly-means-year.json').read_bytes())
        lon=np.asarray(document['longitude']);lat=np.asarray(document['latitude'])
        for month in document['months']:
            for kind in ['raw','lowpass']:
                item=month[kind];u=np.asarray(item['mean']['u_eastward']);v=np.asarray(item['mean']['v_northward'])
                projected_x,projected_y=rotated_vectors(lon,lat,u,v)
                self.assertEqual(len(item['arrows']),100)
                for arrow in item['arrows']:
                    row,col=arrow['row'],arrow['column']
                    self.assertAlmostEqual(arrow['velocity_x_m_s'],projected_x[row,col],places=11)
                    self.assertAlmostEqual(arrow['velocity_y_m_s'],projected_y[row,col],places=11)
                    self.assertAlmostEqual(np.hypot(arrow['velocity_x_m_s'],arrow['velocity_y_m_s']),np.hypot(u[row,col],v[row,col]),places=11)

    def test_new_reader_reconstructs_both_retained_months_with_the_frozen_operators(self):
        path=year.FOLDER/'acquisition-pilot.json'
        data=year.load_sections(path,path)
        self.assertEqual(len(data['epochs']),1632)
        self.assertEqual(len(data['pilot_overlap_dates']),70)
        self.assertEqual(set(data['historical_noon_matches']),{'1','7'})
        # Presentation order must be chronological even if acquisition phases differ.
        data['acquisition']['requested_months']=[7,1]
        with np.load(year.FOLDER/'section-hourly-pilot.npz',allow_pickle=False) as original:
            observed=[]
            for month,times,raw,lowpass in year.monthly_sections(data):
                observed.append(month);stem=f'month_{month:02d}_'
                np.testing.assert_array_equal(times,original[stem+'epoch_seconds'])
                for field,name in enumerate(year.source.VARIABLES):
                    np.testing.assert_allclose(raw[:,:,field],original[stem+'raw_'+name],rtol=0,atol=1e-11,equal_nan=True)
                    np.testing.assert_allclose(lowpass[:,:,field],original[stem+'lowpass_'+name],rtol=0,atol=1e-11,equal_nan=True)
                _,_,_,rows,cols,weights=year.operators.grid_and_legacy()
                for kind,values in [('raw',raw),('lowpass',lowpass)]:
                    native=data['regional_maps'][month][kind]['mean']
                    projected=np.sum(native[rows,cols,:]*weights[:,:,None],axis=1)
                    np.testing.assert_allclose(projected,np.mean(values,axis=0),rtol=0,atol=1e-11)
            self.assertEqual(observed,[1,7])

    def test_weighted_native_means_match_explicit_filtering_and_streamed_month_average(self):
        accumulator=year.map_accumulators([1]);nt=len(accumulator[1]['raw_weights'])
        t=np.arange(nt,dtype=np.int16)
        series=np.column_stack([4000+t%100,t-400,200-(t%400)])
        arrays={name:np.broadcast_to(series[:,i,None,None],(nt,48,50)).copy() for i,name in enumerate(year.source.VARIABLES)}
        arrays['sea_mask']=np.ones((48,50),dtype=np.int16)
        times=accumulator[1]['first_epoch']+np.arange(nt)*3600
        for start in range(0,nt,24):
            block={name:values[start:start+24] for name,values in arrays.items() if name!='sea_mask'}
            block['sea_mask']=arrays['sea_mask']
            year.accumulate_maps(accumulator,times[start:start+24],block)
        actual=year.finish_maps(accumulator)[1]
        decoded=series.astype(float)*.001;decoded[:,0]+=30
        filtered=year.operators.lowpass(decoded[:,None,:])[:,0]
        np.testing.assert_allclose(actual['raw']['mean'][0,0],np.mean(decoded[36:-36],axis=0),rtol=0,atol=1e-11)
        np.testing.assert_allclose(actual['lowpass']['mean'][0,0],np.mean(filtered[36:-36],axis=0),rtol=0,atol=1e-11)
        self.assertEqual(actual['raw']['expected_source_hours'],744)
        self.assertEqual(actual['lowpass']['expected_source_hours'],814)

    def test_missing_positive_weight_hours_invalidate_means_but_unused_halo_does_not(self):
        for missing,raw_valid,filtered_valid in [(0,True,True),(1,True,False),(40,False,False)]:
            accumulator=year.map_accumulators([1]);nt=len(accumulator[1]['raw_weights'])
            arrays={name:np.zeros((nt,48,50),dtype=np.int16) for name in year.source.VARIABLES}
            arrays['sea_mask']=np.ones((48,50),dtype=np.int16);arrays['u_eastward'][missing,0,0]=-32767
            times=accumulator[1]['first_epoch']+np.arange(nt)*3600
            year.accumulate_maps(accumulator,times,arrays);actual=year.finish_maps(accumulator)[1]
            self.assertEqual(bool(np.isfinite(actual['raw']['mean'][0,0]).all()),raw_valid)
            self.assertEqual(bool(np.isfinite(actual['lowpass']['mean'][0,0]).all()),filtered_valid)
            self.assertTrue(np.isfinite(actual['lowpass']['mean'][1,1]).all())

    def test_partial_or_duplicate_original_requests_reject_before_analysis(self):
        pilot_path=year.FOLDER/'acquisition-pilot.json';pilot=json.loads(pilot_path.read_bytes())
        cache=year.ROOT/'.pytest_cache';cache.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=cache) as temporary:
            path=Path(temporary)/'invalid.json'
            partial={**pilot,'status':'partial_acquisition_not_analysis'}
            duplicate={**pilot,'responses':pilot['responses']+[pilot['responses'][0]]}
            for document in [partial,duplicate]:
                path.write_bytes(json.dumps(document).encode())
                with self.assertRaises(ValueError):year.load_sections(path,pilot_path)

    def test_different_hourly_cut_must_match_all_known_original_cells(self):
        raw=(year.ROOT/'research/norkyst-ingoy-20240115.ascii').read_bytes()
        old_times,old_values=year.source.parse_fields(raw,'2024-01-15',12,12)
        times=np.arange(old_times[0]-7200,old_times[0]+7200,3600)
        values={name:np.repeat(old_values[name],4,axis=0) for name in year.source.VARIABLES}
        # The surrounding synthetic hours differ; only noon matches the retained field.
        for index,offset in [(0,10),(1,20),(3,30)]:values['u_eastward'][index]+=offset
        values['sea_mask']=old_values['sea_mask'].copy()
        old={'date':'2024-01-15','key':'old noon cut','first_hour':12,'last_hour':12,'metadata_sha256':'same metadata'}
        record={**old,'key':'larger hourly cut'}
        with patch.object(year,'read_original',return_value=raw):
            year.verify_overlap(record,times,values,old,{}, {})
            values['u_eastward'][2,0,0]+=1
            with self.assertRaises(ValueError):year.verify_overlap(record,times,values,old,{}, {})
            values['u_eastward'][2,0,0]-=1
            with self.assertRaises(ValueError):year.verify_overlap(record,times+3600,values,old,{}, {})
        with self.assertRaises(ValueError):year.verify_overlap({**record,'metadata_sha256':'different'},times,values,old,{}, {})


if __name__=='__main__':unittest.main()
