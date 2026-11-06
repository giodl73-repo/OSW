"""Coastal construction, strict land contacts, holes and preserved inventory scope."""
import hashlib,io,json,zipfile
from pathlib import Path
from unittest.mock import patch
import pytest,shapefile
from shapely.geometry import LineString,Point,box
import madagascar_coastline_comparison as coast
import madagascar_reference_curve as curve

def test_shorter_arc_crosses_ring_origin_without_reversing_endpoints():
    ring=LineString([(46,-20),(47,-20),(47,-21),(46,-21),(46,-20)])
    start,end=Point(46.25,-20),Point(46,-20.25)
    result=curve.shorter_arc(ring,start,end)
    assert result[0]==start.coords[0] and result[-1]==end.coords[0]
    assert (46,-20) in result and len(result)==3
    assert 50<curve.distance(result)<60

def test_start_and_cape_gates_choose_declared_sides():
    ring=LineString([(46,-20),(47,-20),(47,-21),(46,-21),(46,-20)])
    assert curve.gate_point(ring,LineString([(45,-20.5),(48,-20.5)]),0,True).equals(Point(47,-20.5))
    assert curve.gate_point(ring,LineString([(46.5,-22),(46.5,-19)]),1,False).equals(Point(46.5,-21))

@pytest.mark.parametrize('line',[LineString([(40,-20.5),(41,-20.5)]),LineString([(46,-20),(47,-20)])])
def test_missing_or_coincident_gates_are_rejected(line):
    ring=LineString([(46,-20),(47,-20),(47,-21),(46,-21),(46,-20)])
    with pytest.raises(ValueError,match='isolated'):curve.gate_point(ring,line,0,True)

def test_point_contact_is_not_clearance_or_positive_length_crossing():
    result=coast.land_result(LineString([(-1,-1),(0,0)]),box(0,0,1,1))
    assert result['land_contact'] is True
    assert result['positive_length_intersection'] is False
    assert result['legacy_coarse_length_gate_rejected'] is False
    assert result['intersection_display_length']==0

def test_geodesic_display_densification_retains_endpoints_and_1km_limit():
    points=[(49,-20),(48,-25)]
    dense=curve.densify(points)
    assert dense[0]==points[0] and dense[-1]==points[-1]
    assert all(curve.GEOD.inv(*a,*b)[2]<=1000.000001 for a,b in zip(dense,dense[1:]))

def fixture_archive(root):
    directory=root/coast.DIRECTORY;directory.mkdir(parents=True)
    handles={k:io.BytesIO() for k in ['shp','shx','dbf']}
    writer=shapefile.Writer(**handles,shapeType=shapefile.POLYGON)
    writer.field('name','C');writer.poly([[(44,-26),(44,-20),(50,-20),(50,-26),(44,-26)],[(46,-24),(48,-24),(48,-22),(46,-22),(46,-24)]]);writer.record('island with lake');writer.close()
    members={'ne_10m_land.'+k:v.getvalue() for k,v in handles.items()}
    members.update({'ne_10m_land.VERSION.txt':b'5.1.1','ne_10m_land.prj':b'GCS_WGS_1984','ne_10m_land.cpg':b'UTF-8','ne_10m_land.README.html':b'test fixture only'})
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w') as archive:
        for name,data in members.items():archive.writestr(name,data)
    data=output.getvalue();digest=hashlib.sha256(data).hexdigest();(root/coast.ARCHIVE).write_bytes(data)
    receipt={'package_version':'5.1.1','sha256':digest,'bytes':len(data),
        'members':{name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in members.items()}}
    (root/coast.RECEIPT).write_text(json.dumps(receipt));return digest

def test_reader_preserves_holes_in_source_polygons(tmp_path):
    digest=fixture_archive(tmp_path)
    with patch.object(coast,'ROOT',tmp_path),patch.object(coast,'SOURCE_SHA',digest):
        land,count=coast.source_land()
    assert count==1 and land.contains(Point(*coast.project(45,-23)))
    assert not land.contains(Point(*coast.project(47,-23)))

def test_changed_original_archive_is_rejected_before_parsing(tmp_path):
    digest=fixture_archive(tmp_path);path=tmp_path/coast.ARCHIVE;path.write_bytes(path.read_bytes()+b'changed')
    with patch.object(coast,'ROOT',tmp_path),patch.object(coast,'SOURCE_SHA',digest):
        with pytest.raises(ValueError,match='archive/edition'):coast.source_land()

def test_rechecks_all_existing_54_scenarios_on_both_land_products():
    doc,_=coast.verify_inputs()
    assert len(doc['attempts'])==54
    assert doc['results']['coastal_v1']['both_land_contacts']==27
    assert doc['results']['offshore_v2']['coarse_land_contacts']==0
    assert doc['results']['offshore_v2']['natural_earth_land_contacts']==0
    assert all(doc[k] is False for k in ['route_admitted','physical_current_axis_verified','width_measurement_admitted','annual_extrema_eligible'])

def test_curve_rebuild_retains_all_conventions_and_both_clearance_checks():
    doc,catalog,pins=curve.verify_inputs()
    assert len(doc['scenarios'])==27
    assert {(r['offset_parameter_projected_metres'],r['start_gate_latitude'],r['end_gate_longitude']) for r in doc['scenarios']}=={(offset,latitude,longitude) for offset in [10000,25000,50000] for latitude in [-19.9,-20,-20.1] for longitude in [45.2,45.3,45.4]}
    assert all(not r['full_contour_finer_land_contact'] and not r['export_finer_land_contact'] and not r['coarse_osw_land_contact'] for r in doc['scenarios'])
    assert doc['nominal_reference_path_km']==819.935 and doc['reported_scenario_range_km']==[700,900]
    assert max(abs(r['full_minus_simplified_length_km']) for r in doc['scenarios'])<.5
    assert doc['rank_eligible_published_estimates'] is False and doc['physical_current_axis_verified'] is False
    assert doc['published_reported_extent_km']==650 and doc['difference_from_reported_extent_km']==169.935
    assert coast.ARCHIVE in pins and curve.FIGURE in pins

def test_working_catalogue_preserves_all_76_prior_rows_and_ranking():
    doc=curve.build();effective=curve.working_catalogue(doc);base=coast.read(curve.BASE_CATALOGUE)
    by_id={r['id']:r for r in effective['candidates']}
    assert len(by_id)==77 and all(by_id[r['id']]==r for r in base['candidates'])
    assert effective['reference_route_length_order']==base['reference_route_length_order']
    assert by_id[curve.ROUTE_ID]['comparison_group']=='osw_offshore_coastal_reference_curves'
    assert by_id[curve.ROUTE_ID]['ordering_sensitivity'] is None
    assert effective['counts']['currents_without_route_candidates']==19
    assert effective['counts']['currents_with_route_candidates']==71
    assert len(effective['remaining_current_decisions'])==90
    plan=next(r for r in effective['remaining_current_decisions'] if r['current_id']=='southern-east-madagascar')
    assert plan['candidate_ids']==[curve.ROUTE_ID] and plan['published_length_rank_eligible'] is True

def test_derived_difference_signed_zero_is_normalized():
    assert curve.readback(-1e-12,6)==0
    assert str(curve.readback(-1e-12,6))=='0.0'

def test_primary_and_land_sources_keep_factual_and_provider_asset_uses_separate():
    before=coast.read('research/southern-east-madagascar-prose-dimension-admissions.json')['source_record']
    after=curve.primary_source_record();land=curve.source_record()
    assert {k for k in before if before[k]!=after[k]}=={'used_in_collections','metadata_note'}
    assert after['provider_asset_redistributed'] is False and after['id']==before['id']
    assert all(k in after['used_in_collections'] for k in ['reference_routes','diagnostics','state_links'])
    assert land['provider_asset_redistributed'] is True and land['license']=='Public domain'
    assert land['dataset_version']=='5.1.1' and land['source_file_sha256']==coast.SOURCE_SHA

def test_default_source_verification_preserves_originals_and_never_uses_network():
    import acquire_natural_earth_land as acquisition
    before=(curve.ROOT/acquisition.RECEIPT).read_bytes()
    with patch('urllib.request.urlopen',side_effect=AssertionError('No network during verification')):
        result=acquisition.verify()
    assert result['status']=='VERIFIED' and result['sha256']==coast.SOURCE_SHA==acquisition.SHA256
    assert (curve.ROOT/acquisition.RECEIPT).read_bytes()==before

def test_working_state_join_preserves_prior_rows_and_adds_only_eafr_navigation():
    doc=curve.build();effective=curve.working_state_join(doc);base=coast.read(curve.BASE_JOIN)
    assert effective['counts']['candidate_state_pairs']==151
    for code,state in base['states'].items():
        if code!='EAFR':assert effective['states'][code]==state
    old={r['candidate_id']:r for r in base['states']['EAFR']['route_candidates']}
    new={r['candidate_id']:r for r in effective['states']['EAFR']['route_candidates']}
    assert all(new[k]==v for k,v in old.items())
    assert new[curve.ROUTE_ID]['crossing_scenario_count']==27
    assert new[curve.ROUTE_ID]['scenario_count']==27 and new[curve.ROUTE_ID]['crosses_in_all_declared_scenarios'] is True
    assert new[curve.ROUTE_ID]['comparison_group']=='osw_offshore_coastal_reference_curves'
