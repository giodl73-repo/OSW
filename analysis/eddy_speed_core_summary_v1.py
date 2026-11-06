"""Validate bounded retained speed-core JSON; never loads ocean fields."""
import math

METHOD='osw_speed_contour_named_source_case_v1'
METRICS={
    'area':('osw_speed_contour_area','area_km2','km2',5000),
    'radius':('osw_speed_contour_equivalent_radius','speed_equivalent_radius_km','km',10),
    'east_west':('osw_speed_contour_east_west_bounding_arc','east_west_bounding_arc_km_at_midlatitude','km',25),
    'north_south':('osw_speed_contour_north_south_bounding_arc','north_south_bounding_arc_km','km',25),
    'speed':('osw_maximum_circum_averaged_geostrophic_speed','mean_geostrophic_speed_m_s','m/s',.05),
}


def summarize(report,owner_id,component):
    assert report['schema']=='osw.eddy-speed-core-source-review.v1'
    assert report['status']=='PASS_QUALIFIED_SOURCE_CASE_SPEED_CORE_REFERENCE'
    a=report['case_associations'][owner_id]
    assert a['physical_crosswalk_verified'] is False and a['physical_footprint_admitted'] is False
    assert a['rights_screened_release_eligible'] is False and a['other_eddy_values_inherited'] is False
    cloud=report['cloud_review']['result']
    assert cloud['status']=='PASS_EXECUTION_SPEED_CONTOUR_REVIEW_NO_ADMISSION'
    assert cloud['source']['sha256']=='526fb93bbb0880a4c6ab9390527cef8ecc4706c7c08d0a075ccfd02de922b527'
    assert cloud['measurements_admitted']==cloud['physical_identity_joins_created']==0
    case=next(c for c in cloud['cases'] if c['source_name']==a['source_name'] and c['date']==a['date'])
    assert case['source_point']==a['source_point'] and case['input_height_reference']=='native_daily_ADT_m_not_demeaned'
    assert case['convergence']['status']=='PASS_STEP_CONVERGENCE_DIAGNOSTIC'
    assert [s['level_step_m'] for s in case['sweeps']]==[.005,.0025]
    selected=[]
    for sweep in case['sweeps']:
        assert sweep['status']=='PASS_SPEED_CORE_DIAGNOSTIC' and sweep['maximum_drop_m']==.60
        assert sweep['minimum_interior_samples']==12 and sweep['search_radius_km']==150
        profile=sweep['profile'];index=sweep['selected_profile_index']
        assert 0<index<len(profile)-1 and sweep['selected']==profile[index]
        speeds=[p['mean_geostrophic_speed_m_s'] for p in profile]
        assert all(math.isfinite(v) and v>0 for v in speeds)
        assert sum(math.isclose(v,speeds[index],rel_tol=1e-10,abs_tol=1e-12) for v in speeds)==1
        assert speeds[index]==max(speeds)
        for p in profile:
            assert p['interior_finite_gridpoints']>=12 and p['enclosed_strict_maxima']==1
            assert 'peak_demeaned_adt_m' not in p and p['peak_input_height_m']==sweep['peak']['height_m']
        p=sweep['selected'];w,s,e,n=p['bbox_degrees']
        assert -99<w<e<-79 and 17<s<n<32 and p['vertices']>=4
        assert math.isclose(p['speed_equivalent_radius_km'],math.sqrt(p['area_km2']/math.pi),rel_tol=1e-12)
        assert math.isclose(p['north_south_bounding_arc_km'],6371*math.radians(n-s),rel_tol=1e-12)
        assert len(p['vertices_float64_little_endian_sha256'])==64
        selected.append(p)
    assert case['sweeps'][0]['peak']['lon_lat']==case['sweeps'][1]['peak']['lon_lat']
    limits={'area_km2':.10,'speed_equivalent_radius_km':.05,'mean_geostrophic_speed_m_s':.05,
        'east_west_bounding_arc_km_at_midlatitude':.10,'north_south_bounding_arc_km':.10}
    assert case['convergence']['maximum_relative_differences']==limits
    for key,limit in limits.items():
        difference=abs(selected[0][key]-selected[1][key])/selected[1][key]
        assert math.isclose(case['convergence']['relative_differences'][key],difference,abs_tol=1e-14) and difference<=limit
    metric,key,unit,increment=METRICS[component];values=[s[key] for s in selected]
    return {'method':METHOD,'metric':metric,'unit':unit,'component':component,
        'source_case_name':a['source_name'],'date':a['date'],'scenario_values':values,
        'nominal_audit_value':values[1],'unrounded_extrema':[min(values),max(values)],
        'round_outward_to':increment,
        'range_value':[round(math.floor(min(values)/increment)*increment,12),round(math.ceil(max(values)/increment)*increment,12)],
        'level_steps_m':[.005,.0025],'range_is_numerical_only':True,'independent_observations':False,
        'source_point_lon_lat':a['source_point'],'grid_peak_lon_lat':case['sweeps'][1]['peak']['lon_lat'],
        'source_point_role':a['source_point_role'],
        'peak_distance_from_source_point_km':case['sweeps'][1]['peak']['distance_from_source_point_km'],
        'selected_interior_gridpoints':[p['interior_finite_gridpoints'] for p in selected]}
