"""Retain hydrographic schemas and audit filename joins without asserting identity."""
from collections import Counter
from datetime import datetime,timezone
import json,math,re,zipfile
from build_redsox_ladcp_source_inventory import ROOT,SOURCE,digest,gpl_parts,position,build as ladcp_inventory

OUTPUT=ROOT/'research/redsox-ctd-companion-inventory.json'
RECONCILIATION=ROOT/'research/redsox-cruise-log-metadata-reconciliation.json'
RECONCILIATION_SHA='c20b965126a62925b35cf61c8d7b61cd887d236e478dba57714cbc1b7bba252b'
PINS={
 'ctd-preflight.json':'1230ece2b9c4869d76d94b9f2e751273f10cb9ddd2d3bdbe466408ae7c02a326',
 'ctd-acquisition.json':'56f7c5bb42a7db5f891b47b7c53eb19501d7deb7fa0c2fa4612d0270945dc498',
 'ctd-ascii-originals.zip':'8bce8c17398f9a7cccf8f5a2364c6fbc29411783c784896c00efdeff7b2df478',
}
SCHEMAS=[['p','S','T','sigma_theta','o2','c'],
         ['p','T','S','sigma_theta','o2','c','theta'],
         ['z','p','T','S','sigma_theta','o2','c','theta']]
TEMPERATURE_UNITS=r'\u\s-7o\s+7\dC'


def header_station(label,campaign):
    match=re.fullmatch(r'(?:RSX)?(\d+)',label,re.IGNORECASE)
    if not match:raise ValueError('Unknown CTD header station syntax')
    value=int(match[1])
    if value>=1000:
        if value//1000!=int(campaign[-1]):raise ValueError('CTD header station names another cruise')
        value%=1000
    return value


def parse_ctd(raw):
    h,raw_rows=gpl_parts(raw);sequence=h.get('sequence','').split()
    if sequence not in SCHEMAS:raise ValueError('Changed CTD source schema')
    if int(h['nquan'])!=len(sequence) or len(raw_rows)!=int(h['n_values']) or not raw_rows or any(len(r)!=len(sequence) for r in raw_rows):
        raise ValueError('CTD actual columns/rows disagree with header')
    for key,expected in {'_p_data_units':'dbar','_S_data_units':'psu','_T_data_units':TEMPERATURE_UNITS}.items():
        if h.get(key)!=expected:raise ValueError('Changed CTD pressure/salinity/temperature units')
    sentinel=float(h['bad_flag']);rows=[]
    if not math.isfinite(sentinel) or sentinel>=-1e20:raise ValueError('Changed CTD missing sentinel')
    for row in raw_rows:
        converted=[]
        for cell in row:
            value=float(cell)
            if math.isclose(value,sentinel,rel_tol=1e-6):converted.append(None)
            elif not math.isfinite(value):raise ValueError('Undocumented nonfinite CTD value')
            else:converted.append(value)
        rows.append(converted)
    return h,sequence,rows


def profile_record(name,raw):
    match=re.fullmatch(r'(RSX[12])/rsx([12])(\d{3})\.ctd\.1m\.asc',name)
    if not match or match[1]!=f'RSX{match[2]}':raise ValueError('Changed CTD source filename/cruise')
    campaign=match[1];station=int(match[3]);h,sequence,rows=parse_ctd(raw)
    if h['cruise']!=('REDSOX I' if campaign=='RSX1' else 'REDSOX II'):raise ValueError('CTD cruise disagreement')
    issues=[]
    try:lon,lat=position(h)
    except ValueError:
        lon=lat=None;issues.append('source_coordinates_invalid_not_repaired')
    try:
        stamp=datetime.strptime(h['start_time'],'%d-%b-%y %H:%M:%S').replace(tzinfo=timezone.utc)
        if stamp.year!=2001:raise ValueError('Unexpected CTD survey year')
    except ValueError:
        stamp=None;issues.append('source_start_time_not_parseable_as_documented_2001_UTC')
    try:stated_station=header_station(h['station'],campaign)
    except ValueError:
        stated_station=None;issues.append('source_station_label_not_parseable_as_a_cast_identifier')
    if stated_station is not None and stated_station!=station:issues.append('filename_and_header_station_disagree')
    if len(sequence)!=8:issues.append('actual_sequence_differs_from_eight_column_README_description')
    if 'z' in sequence:
        if '_z_data_units' not in h and h.get('_z_dat_units')=='m':issues.append('depth_unit_header_uses_z_dat_units_typo')
        elif h.get('_z_data_units')!='m':raise ValueError('Unknown CTD depth units')
    else:issues.append('no_explicit_depth_column_pressure_is_not_depth')
    if h.get('_c_data_units')==r'm s\u\s-7-2\s+7\d':issues.append('sound_speed_source_units_print_m_s_minus2_not_corrected')
    variables={}
    for i,key in enumerate(sequence):
        finite=[row[i] for row in rows if row[i] is not None]
        variables[key]={'missing_samples':len(rows)-len(finite),
            'source_value_range':[min(finite),max(finite)] if finite else None,
            'source_units':h.get(f'_{key}_data_units'),
            'alternate_source_units_header':h.get('_z_dat_units') if key=='z' else None}
    pressure=[row[sequence.index('p')] for row in rows]
    increasing=all(a is not None and b is not None and b>a for a,b in zip(pressure,pressure[1:]))
    if not increasing:issues.append('pressure_axis_not_complete_strictly_increasing')
    return {'id':f'{campaign.lower()}-{station:03d}-ctd','campaign':campaign,
        'filename_station':station,'source_header_station':h['station'],'parsed_header_station':stated_station,
        'source_file':name,'source_sha256':digest(raw),
        'source_coordinate_strings_lon_lat':[h['lon'],h['lat']],
        'position_lon_lat':[lon,lat] if lon is not None and lat is not None else None,
        'source_start_time':h['start_time'],
        'start_time_utc':stamp.isoformat().replace('+00:00','Z') if stamp else None,'sequence':sequence,'samples':len(rows),
        'variables':variables,'source_metadata_issues':issues,
        'georeferencing_independently_verified':False,'salinity_band_is_velocity_width':False}


def join_record(velocity,ctd):
    a=datetime.fromisoformat(velocity['time_utc'].replace('Z','+00:00'))
    b=datetime.fromisoformat(ctd['start_time_utc'].replace('Z','+00:00')) if ctd['start_time_utc'] else None
    return {'ladcp_id':velocity['id'],'ctd_id':ctd['id'],
        'join_basis':'filename_cruise_and_station_only_not_validated_measurement_identity',
        'header_station_agrees_with_filename':ctd['filename_station']==ctd['parsed_header_station'] if ctd['parsed_header_station'] is not None else None,
        'ctd_minus_ladcp_position_degrees':[y-x for x,y in zip(velocity['position_lon_lat'],ctd['position_lon_lat'])] if ctd['position_lon_lat'] is not None else None,
        'ctd_start_minus_ladcp_header_time_seconds':(b-a).total_seconds() if b else None,
        'reviewed_ctd_position_lon_lat':ctd.get('reviewed_source_support',{}).get('position_lon_lat'),
        'same_physical_cast_verified':False,'interpolated_velocity_or_hydrography':False}


def apply_reviewed_support(profiles):
    raw=RECONCILIATION.read_bytes()
    if digest(raw)!=RECONCILIATION_SHA:raise ValueError('Changed frozen cruise-log reconciliation')
    audit=json.loads(raw);by_id={p['id']:p for p in profiles};seen=set()
    for note in audit['reconciliations']:
        identifier=note['profile_id']
        if identifier in seen or identifier not in by_id:raise ValueError('Duplicate or missing reviewed source profile')
        seen.add(identifier);profile=by_id[identifier]
        if note['source_file']!=profile['source_file'] or note['source_profile_sha256']!=profile['source_sha256']:
            raise ValueError('Cruise-log annotation bound to another source profile')
        support={'audit_file':RECONCILIATION.relative_to(ROOT).as_posix(),
            'audit_sha256':RECONCILIATION_SHA,'source_document':note['cruise_report'],
            'source_pdf_page':note['pdf_page'],'source_table_row':note['table_locator'],
            'original_header_rewritten':False}
        if 'reviewed_cast_number' in note:
            if note['reviewed_cast_number']!=profile['filename_station']:raise ValueError('Reviewed cast disagrees with bound filename')
            support['reviewed_cast_number']=note['reviewed_cast_number']
        if 'position_lon_lat_degrees_minutes' in note:
            pairs=note['position_lon_lat_degrees_minutes']
            if len(pairs)!=2 or any(len(pair)!=2 or pair[0]<0 or not 0<=pair[1]<60 for pair in pairs):raise ValueError('Invalid reviewed coordinates')
            support['position_lon_lat']=[degrees+minutes/60 for degrees,minutes in pairs]
            support['source_precision_arcminutes']=audit['source_log_precision_minutes']
            support['position_role']='reviewed_cruise_log_cast_position_not_rewritten_CTD_header'
        if 'cast_event_time_utc' in note:
            support['cast_event_time_utc']=note['cast_event_time_utc']
            support['event_time_is_ctd_start_time']=False
        profile['reviewed_source_support']=support
    return len(seen)


def build():
    for name,pin in PINS.items():
        if digest((SOURCE/name).read_bytes())!=pin:raise ValueError('Changed frozen CTD companion source '+name)
    receipt=json.loads((SOURCE/'ctd-acquisition.json').read_bytes())
    if receipt['status']!='COMPLETE' or receipt['errors'] or receipt['expected_files']!=461:raise ValueError('Incomplete CTD acquisition')
    profiles=[]
    with zipfile.ZipFile(SOURCE/'ctd-ascii-originals.zip') as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or set(names)!=set(receipt['files']):raise ValueError('Changed CTD source membership')
        for name in sorted(names):
            raw=z.read(name);pin=receipt['files'][name]
            if len(raw)!=pin['bytes'] or digest(raw)!=pin['sha256']:raise ValueError('Changed CTD original '+name)
            profiles.append(profile_record(name,raw))
    reviewed=apply_reviewed_support(profiles)
    velocity=ladcp_inventory();by_key={(r['campaign'],r['filename_station']):r for r in profiles}
    if len(by_key)!=len(profiles):raise ValueError('Duplicate CTD filename cast')
    joins=[];unmatched=[]
    for v in velocity['profiles']:
        c=by_key.get((v['campaign'],v['station']))
        if c is None:unmatched.append(v['id'])
        else:joins.append(join_record(v,c))
    joined={r['ctd_id'] for r in joins}
    return {'schema':'osw.redsox-hydrography-companion-source-inventory.v1',
        'status':'source_companion_inventory_not_validated_cast_association_or_current_measurement',
        'current_id':'red-sea-saline-overflow','archive_accession':'0146147','archive_version':'1.2',
        'source_url':'https://www.ncei.noaa.gov/archive/accession/0146147',
        'input_sha256':{**{'research/source-data/ncei-redsox-2001/'+k:v for k,v in PINS.items()},
            RECONCILIATION.relative_to(ROOT).as_posix():RECONCILIATION_SHA},
        'counts':{'ctd_profiles':len(profiles),'samples':sum(r['samples'] for r in profiles),
            'campaigns':dict(Counter(r['campaign'] for r in profiles)),
            'schemas':dict(Counter(' '.join(r['sequence']) for r in profiles)),
            'header_filename_station_conflicts':sum(r['parsed_header_station'] is not None and r['filename_station']!=r['parsed_header_station'] for r in profiles),
            'unparseable_source_station_labels':sum(r['parsed_header_station'] is None for r in profiles),
            'unparseable_source_times':sum(r['start_time_utc'] is None for r in profiles),
            'invalid_source_positions':sum(r['position_lon_lat'] is None for r in profiles),
            'filename_joins':len(joins),'unmatched_ladcp_profiles':len(unmatched),
            'ctd_profiles_without_ladcp_filename_match':len(profiles)-len(joined)},
        'reviewed_support_counts':{'profiles':reviewed,
            'positions':sum('position_lon_lat' in r.get('reviewed_source_support',{}) for r in profiles),
            'cast_numbers':sum('reviewed_cast_number' in r.get('reviewed_source_support',{}) for r in profiles),
            'cast_event_times':sum('cast_event_time_utc' in r.get('reviewed_source_support',{}) for r in profiles)},
        'profiles':profiles,'filename_joins':joins,'unmatched_ladcp_ids':unmatched,
        'ctd_ids_without_ladcp_filename_match':[r['id'] for r in profiles if r['id'] not in joined],
        'pressure_is_depth':False,'filename_1m_is_verified_geometric_sampling':False,
        'header_errors_repaired':False,'source_file_identity_joins_are_validated_physical_casts':False,
        'new_width_record_admitted':False,'whole_current_width_km':None,'annual_width_range_km':None,
        'preflight_clarification':'The companion preflight expected the README eight columns; three actual schemas are preserved, with six/seven-column records flagged. The inherited velocity-quality context belongs to LADCP and supplies no CTD calibration error.'}


if __name__=='__main__':
    data=build();OUTPUT.write_bytes((json.dumps(data,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps(data['counts']))
