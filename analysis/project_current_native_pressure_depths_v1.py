"""Apply the established standard-ocean conversion to eligible native-pressure references."""
import copy,csv,hashlib,io,json,math,socket
from pathlib import Path
import gsw
import load_current_depth_reference_inventory_v26 as inventory_loader
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-pressure-projection-operator-v1.json'
INVENTORY='research/current-depth-reference-inventory-v26.json'
BENGUELA='research/benguela-kersale2019-mean-pressure-source-facts-v1.json'
RIM='research/rim-oguz1999-native-vertical-source-facts-v1.json'
CANARY='research/canary-pies-pressure-conversion-operator-v1.json'
BENGUELA_ID='benguela-kersale2019-34p5s-mean-lower-pressure-extent'
RIM_ID='rim-oguz1999-censored-pressure-reach'
FLAGS=['physical_current_bottom_established','volume_eligible','physical_state_join_eligible','reference_route_projection_eligible','seasonal_playback_eligible','annual_extrema_eligible','physical_depth_ranking_eligible']


def finite_real(value):return type(value) in (int,float) and math.isfinite(value)


def convert(pressure,latitude,*,unit='dbar',pressure_kind='assumed_oceanographic_sea_pressure',dynamic_height=0,sea_surface_geopotential=0):
    if unit!='dbar' or pressure_kind!='assumed_oceanographic_sea_pressure':raise ValueError('Sea pressure in dbar required; never subtract atmosphere twice')
    if not finite_real(pressure) or not 0<=pressure<=12000 or not finite_real(latitude) or not -90<=latitude<=90:raise ValueError('Finite nonnegative ocean pressure and explicit valid latitude required')
    if dynamic_height!=0 or sea_surface_geopotential!=0:raise ValueError('New ocean-state corrections require a distinct reviewed operator')
    z=float(gsw.z_from_p(pressure,latitude,0,0));depth=-z
    if not math.isfinite(depth) or depth<0:raise ValueError('Finite positive-down metric depth required')
    reconstructed=float(gsw.p_from_z(z,latitude,0,0))
    if abs(reconstructed-pressure)>1e-7:raise ValueError('GSW inverse pressure check failed')
    return depth,reconstructed


def project(rows,benguela,rim,policy):
    ids=[r['id'] for r in rows]
    if set(ids)!={BENGUELA_ID,RIM_ID} or len(rows)!=2:raise ValueError('Exactly both native-pressure references in inventoryv26; no silent omissions/duplicates')
    if policy['gsw_version']!='3.6.23' or gsw.__version__!=policy['gsw_version'] or policy['assumed_dynamic_height_m2_s2']!=0 or policy['assumed_sea_surface_geopotential_m2_s2']!=0 or policy['display_rounding_m']!=10:raise ValueError('Preserve validated Canary GSW version, assumptions and display rounding')
    if benguela['reported_observational_months']!=['2013-09','2015-07'] or benguela['records'][0]['source_latitude_degrees_north']!=-34.5 or benguela['records'][0]['source_longitude_band_degrees_east']!=[11,17.5]:raise ValueError('Explicit published section latitude and mean period required')
    if not benguela['methods']['time_mean_reference_velocity'].startswith('OFES') or benguela['methods']['direct_full_column_velocity_observation'] or benguela['methods']['wind_driven_Ekman_velocity_included']:raise ValueError('Hybrid geostrophic field, not direct total velocity')
    if rim['assumed_latitude_degrees_north'] is not None or rim['pressure_datum_independently_verified'] or not rim['records'][1]['sampling_limit_censors_unknown_flow_bottom']:raise ValueError('Frozen unresolved Rim latitude/datum/censor context changed')
    outcomes=[]
    for ref in sorted(rows,key=lambda r:r['id']):
        if ref['unit']!='dbar' or ref['approximate_value_m'] is not None or any(ref.get(k,False) for k in FLAGS):raise ValueError('Native reference units and physical eligibility must remain unchanged')
        row={'native_reference_id':ref['id'],'entity_id':ref['entity_id'],'source_pressure_dbar':ref['approximate_value_dbar'],
          'native_pressure_unit':'dbar','source_metric':ref['metric'],'source_statistic':ref.get('source_statistic'),
          'source_file':ref['source_file'],'source_sha256':ref['source_sha256'],'source_pointer':ref['source_pointer'],
          'source_citation':ref['source_citation'],'source_url':ref['source_url'],'source_locator':ref['source_locator'],
          'source_branch_scope':ref.get('source_branch_scope'),'conversion_latitude_degrees_north':None,
          'pressure_interpretation':'source_pressure_datum_unverified_no_projection_assumption','atmospheric_pressure_subtracted_dbar':None,
          'native_reference':copy.deepcopy(ref),
          'computed_reference_depth_m':None,'display_approximate_reference_depth_m':None,'roundtrip_sea_pressure_dbar':None,
          'reference_depth_unit':'m','vertical_datum':'standard_ocean_positive_down_from_zero_sea_pressure_assuming_zero_geopotential_terms',
          'physical_depth_uncertainty_m':None,'annual_depth_range_m':None,'physical_thickness_m':None,'whole_current_depth_m':None,
          'new_measurement':False,'new_reference_inventory_row':False,'native_reference_modified':False,
          'conversion_is_new_independent_observation':False,'computed_precision_is_physical_accuracy':False,
          **{k:False for k in FLAGS}}
        if ref['id']==BENGUELA_ID:
            if (ref['entity_id'],ref['metric'],ref['approximate_value_dbar'])!=('current:benguela','reported_mean_geostrophic_flow_lower_pressure_extent',1270):raise ValueError('Exact source pressure and regional mean flow extent required')
            source=benguela['records'][0]
            if ref['source_reported_record']!=source:raise ValueError('Reference and exact primary transcription disagree')
            depth,back=convert(ref['approximate_value_dbar'],source['source_latitude_degrees_north'])
            row.update(status='APPROXIMATE_STANDARD_OCEAN_METRE_COMPANION',conversion_latitude_degrees_north=-34.5,
              pressure_interpretation='assumed_oceanographic_sea_pressure',atmospheric_pressure_subtracted_dbar=0,
              computed_reference_depth_m=round(depth,6),display_approximate_reference_depth_m=int(10*round(depth/10)),roundtrip_sea_pressure_dbar=round(back,6),
              source_observational_months=copy.deepcopy(benguela['reported_observational_months']),source_methods=copy.deepcopy(benguela['methods']),
              source_section_longitude_band_degrees_east=[11,17.5],
              qualification='Approximate conversion of the published regional mean pressure extent. Zero dynamic height and zero surface geopotential are reference assumptions, not measured ocean-state corrections. Source pressure approximations, boundary uncertainty and mean-field reconstruction errors remain unknown. Not a flat boundary across the band.')
        else:
            if (ref['entity_id'],ref['metric'],ref['approximate_value_dbar'])!=('current:black-sea-rim','reported_censored_flow_pressure_reach',350):raise ValueError('Exact sampling-censored Rim pressure reach required')
            if ref['source_reported_record']!=rim['records'][1]:raise ValueError('Rim reference/transcription mismatch')
            row.update(status='UNRESOLVED_CONVERSION_LATITUDE_AND_PRESSURE_DATUM',sampling_limit_censors_unknown_flow_bottom=True,
              qualification='No latitude invented from the name Black Sea or a route centroid. Published350dbar reach was sampling-limited and does not establish a physical current bottom; metric projection remains null.')
        outcomes.append(row)
    return outcomes


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());op=read(OP)
    for p,h in op['input_sha256'].items():
        if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h:raise ValueError('Pinned input changed:'+p)
    if op['new_native_ocean_values_allowed']!=0 or op['new_reference_inventory_rows_allowed']!=0 or op['maximum_native_pressure_reference_outcomes']!=2:raise ValueError('Conversion-only scope cannot expand')
    manifest=read(INVENTORY);view=inventory_loader.load_inventory(manifest,lambda p:(root/p).read_bytes());native=[row for row in view['evidence'] if row['unit']=='dbar']
    result=project(native,read(BENGUELA),read(RIM),read(CANARY))
    report={'schema':'osw.current-depth-native-pressure-projections.v1','status':'PRESSURE_REFERENCES_WITH_SCOPED_METRE_COMPANIONS_NOT_NEW_MEASUREMENTS',
      'inventory_file':INVENTORY,'inventory_sha256':hashlib.sha256((root/INVENTORY).read_bytes()).hexdigest(),
      'operator_file':OP,'operator_sha256':hashlib.sha256((root/OP).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],
      'method':'depth_m=-gsw.z_from_p(sea_pressure_dbar,source_latitude,0,0)','gsw_version':gsw.__version__,
      'counts':{'native_pressure_reference_outcomes':len(result),'converted_reference_companions':sum(row['computed_reference_depth_m'] is not None for row in result),
        'unresolved_reference_companions':sum(row['computed_reference_depth_m'] is None for row in result),'new_native_measurements':0,'new_inventory_references':0},
      'records':result,'reference_inventory_counts_unchanged':view['counts'],'native_coordinate_unit_counts_unchanged':view['coordinate_unit_counts'],
      'native_pressure_references_preserved':True,'native_field_requests':0,'new_native_ocean_values_decoded':0,
      'standard_ocean_correction_is_measured_ocean_state':False,'runtime_changed':False,'full_goal_complete':False}
    return report


def csv_bytes(records):
    fields=['native_reference_id','entity_id','status','source_pressure_dbar','native_pressure_unit','conversion_latitude_degrees_north','computed_reference_depth_m','display_approximate_reference_depth_m','reference_depth_unit','physical_depth_uncertainty_m','annual_depth_range_m','physical_thickness_m','physical_current_bottom_established','new_measurement','source_file','source_pointer']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in records:writer.writerow({key:row.get(key) for key in fields})
    return out.getvalue().encode()


def main():
    def denied(*a,**k):raise RuntimeError('Conversion-only producer forbids external network/source replay')
    socket.create_connection=denied;socket.socket=denied
    report=build();folder=ROOT/'current-depth-pressure-projections-v1';folder.mkdir(exist_ok=False)
    raw=(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();table=csv_bytes(report['records'])
    if len(raw)+len(table)>=2400000:raise ValueError('Fixed scientific output chunk cap exceeded')
    (folder/'projections.json').write_bytes(raw);(folder/'projections.csv').write_bytes(table)
    print(json.dumps({'counts':report['counts'],'native_units_unchanged':report['native_coordinate_unit_counts_unchanged'],
      'new_reference_rows':0,'benguela_display_approximate_reference_depth_m':next(row['display_approximate_reference_depth_m'] for row in report['records'] if row['native_reference_id']==BENGUELA_ID)}),flush=True)

if __name__=='__main__':main()
