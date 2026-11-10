"""Inventory the exact REDSOX archive without diagnosing current widths.

The 12-versus-4 header discrepancy is preserved as a source issue, never
silently repaired. Both ASCII file families retain their stated references.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,math,re,zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/source-data/ncei-redsox-2001'
OUTPUT=ROOT/'research/redsox-ladcp-source-inventory.json'
PINS={
 'preflight.json':'334a989a2b2f5205d345584f8c471641bac3eea7be4a44ab360cb1881a855b41',
 'acquisition.json':'f6453064d837cefa689fa274e72c5d5b84bcae85d119910a48f1092d7f11236c',
 'documentation.json':'12c56f526f1054643cdc72848bf791f6780cdb5aa2615c92a330079cc022bcd2',
 'ladcp-ascii-originals.zip':'950fa2e0481d59c3f5f9bbbd84b3c0df1144306ecdcfded13076c049e395b104',
}
VELOCITY_UNITS=r'm s\u\s-7-1\s+7\d'


def digest(raw):return hashlib.sha256(raw).hexdigest()


def gpl_parts(raw):
    text=raw.decode('ascii')
    if text.count('#END#')!=1:raise ValueError('GPL requires exactly one header terminator')
    before,after=text.split('#END#');header={};last=None
    for line in before.splitlines():
        if line.startswith('# '):
            parts=line[2:].split(None,1)
            if not parts:continue
            last=parts[0]
            if last in header:raise ValueError('Duplicate GPL header key')
            header[last]=parts[1].strip() if len(parts)>1 else ''
        elif line.strip():
            if last is None:raise ValueError('Orphan GPL header continuation')
            header[last]+=' '+line.strip()
    return header,[line.split() for line in after.splitlines() if line.strip()]


def parse_gpl(raw):
    header,rows=gpl_parts(raw)
    sequence=header.get('sequence','').split()
    if sequence!=['hz','zz','ur','vr']:raise ValueError('Changed source column sequence')
    if header.get('coordinates')!='earth':raise ValueError('Changed velocity coordinate frame')
    for key,expected in {'_ur_data_units':VELOCITY_UNITS,'_vr_data_units':VELOCITY_UNITS,
                         '_hz_data_units':'m','_zz_data_units':'m'}.items():
        if header.get(key)!=expected:raise ValueError('Changed GPL source units')
    if not rows or len(rows)!=int(header['n_values']) or any(len(row)!=len(sequence) for row in rows):
        raise ValueError('GPL row count or observed column count disagrees')
    declared=int(header['nquan']);issues=[]
    if declared!=len(sequence):issues.append('declared_nquan_disagrees_with_sequence_and_observed_rows')
    sentinel=float(header['bad_flag'])
    if not math.isfinite(sentinel) or sentinel>=-1e20:raise ValueError('Unexpected source missing sentinel')
    values=[]
    for row in rows:
        converted=[]
        for cell in row:
            value=float(cell)
            if math.isclose(value,sentinel,rel_tol=1e-6):converted.append(None)
            elif not math.isfinite(value):raise ValueError('Undocumented nonfinite source value')
            else:converted.append(value)
        values.append(converted)
    return header,values,issues


def position(header):
    latitude=float(header['lat']);longitude=float(header['lon'])
    if not math.isfinite(latitude) or not math.isfinite(longitude) or not -90<=latitude<=90 or not -180<=longitude<=180:
        raise ValueError('Invalid source coordinates')
    return longitude,latitude


def profile_record(name,raw):
    match=re.fullmatch(r'(RSX[12])/rsx([12])(\d{3})\.downup\.(nav|hr)\.ladcpp\.asc',name)
    if not match or match[1]!=f'RSX{match[2]}':raise ValueError('Unexpected cruise or source filename')
    campaign=match[1];station=int(match[3]);family=match[4]
    h,rows,issues=parse_gpl(raw)
    expected='REDSOX_I' if campaign=='RSX1' else 'REDSOX_II'
    if h['cruise']!=expected:raise ValueError('Filename/header cruise disagreement')
    lon,lat=position(h)
    stamp=datetime.strptime(h['time'],'%d-%b-%y %H:%M:%S').replace(tzinfo=timezone.utc)
    if stamp.year!=2001:raise ValueError('Unexpected survey year')
    if h.get('reference')=='m':issues.append('source_reference_header_is_uninterpretable_m')
    missing={key:sum(row[i] is None for row in rows) for i,key in enumerate(['hz','zz','ur','vr'])}
    missing_pairs=sum((row[2] is None)!=(row[3] is None) for row in rows)
    if missing_pairs:issues.append('eastward_northward_missing_masks_disagree')
    heights=[row[0] for row in rows if row[0] is not None]
    depths=[row[1] for row in rows if row[1] is not None]
    sums=[row[0]+row[1] for row in rows if row[0] is not None and row[1] is not None]
    source_component_notes=[]
    if campaign=='RSX1' and station in [10,63]:
        source_component_notes.append('Author quality note declares downcast bad; inclusion/omission in this distributed product requires review.')
    if campaign=='RSX2' and station in [22,71]:
        source_component_notes.append('Author quality note declares upcast bad; inclusion/omission in this distributed product requires review.')
    return {'id':f'{campaign.lower()}-{station:03d}-{family}',
        'source_file':name,'source_sha256':digest(raw),'campaign':campaign,'station':station,
        'position_lon_lat':[lon,lat],'position_role':'source_profile_metadata_not_current_axis',
        'time_utc':stamp.isoformat().replace('+00:00','Z'),
        'time_role':'source_header_time_in_documented_UTC_not_survey_synoptic_time',
        'file_reference_family':family,'source_reference':h.get('reference'),
        'source_reference_family_meaning':'navigation' if family=='nav' else 'bottom_tracking_family',
        'source_processing_tag':h.get('tag'),
        'declared_nquan':int(h['nquan']),'sequence':['hz','zz','ur','vr'],'actual_columns':4,
        'samples':len(rows),'missing_samples_by_variable':missing,'component_mask_disagreements':missing_pairs,
        'sampled_height_above_bottom_range_m':[min(heights),max(heights)] if heights else None,
        'sampled_depth_range_m':[min(depths),max(depths)] if depths else None,
        'height_plus_depth_range_m':[min(sums),max(sums)] if sums else None,
        'bottom_depth_header_m':{key:float(h[key]) for key in ['Hbo','Hext','Hxtp'] if key in h},
        'source_header_conflicts':issues,'source_component_quality_notes':source_component_notes,
        'source_reference_quality_review_complete':False,
        'descending_plume_membership_verified':False,'current_width_admitted':False}


def build():
    for file,pin in PINS.items():
        if digest((SOURCE/file).read_bytes())!=pin:raise ValueError('Changed frozen REDSOX source '+file)
    receipt=json.loads((SOURCE/'acquisition.json').read_bytes())
    if receipt['status']!='COMPLETE' or receipt['errors'] or receipt['expected_files']!=445:
        raise ValueError('Incomplete original acquisition')
    records=[]
    with zipfile.ZipFile(SOURCE/'ladcp-ascii-originals.zip') as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or set(names)!=set(receipt['files']):raise ValueError('Changed original source membership')
        for name in sorted(names):
            raw=z.read(name);pin=receipt['files'][name]
            if len(raw)!=pin['bytes'] or digest(raw)!=pin['sha256']:raise ValueError('Changed original profile '+name)
            records.append(profile_record(name,raw))
    campaigns=[]
    for campaign,total in [('RSX1',238),('RSX2',227)]:
        selected=[r for r in records if r['campaign']==campaign]
        stations=[r['station'] for r in selected]
        if len(stations)!=len(set(stations)):raise ValueError('Reference alternatives must not count as independent casts')
        campaigns.append({'campaign':campaign,'profiles':len(selected),'published_cruise_cast_count_context':total,
            'published_count_is_distributed_velocity_profile_count':False,
            'station_ids_not_distributed_in_1_to_published_count':sorted(set(range(1,total+1))-set(stations)),
            'source_time_range_utc':[min(r['time_utc'] for r in selected),max(r['time_utc'] for r in selected)],
            'reference_families':dict(sorted(Counter(r['file_reference_family'] for r in selected).items()))})
    return {'schema':'osw.redsox-direct-current-source-inventory.v1',
        'status':'source_inventory_with_unresolved_metadata_and_physical_measurement_gates',
        'current_id':'red-sea-saline-overflow','archive_accession':'0146147','archive_version':'1.2',
        'source_url':'https://www.ncei.noaa.gov/archive/accession/0146147',
        'input_sha256':{'research/source-data/ncei-redsox-2001/'+key:pin for key,pin in PINS.items()},
        'counts':{'profiles':len(records),'samples':sum(r['samples'] for r in records),
            'nquan_conflicts':sum(r['declared_nquan']!=r['actual_columns'] for r in records),
            'uninterpretable_reference_headers':sum(r['source_reference']=='m' for r in records),
            'component_mask_disagreements':sum(r['component_mask_disagreements'] for r in records)},
        'campaigns':campaigns,'profiles':records,
        'quality_context':{'RSX1':{'author_typical_velocity_uncertainty_m_s':0.03,'statistic':'author approximate average quality summary; identifiable profiles worse'},
            'RSX2':{'author_typical_velocity_uncertainty_m_s':0.04,'statistic':'author tentative single-number summary; raw-data and shipboard-reference problems'}},
        'quality_summaries_are_per_cast_intervals':False,'quality_summaries_are_width_uncertainty':False,
        'nquan_conflicts_repaired':False,'uninterpretable_reference_headers_repaired':False,
        'non_synoptic_surveys_are_annual_cycle':False,'all_stations_are_descending_plume':False,
        'whole_current_width_km':None,'annual_width_range_km':None,'whole_current_length_km':None,
        'new_width_record_admitted':False,'physical_current_footprint_inferred':False}


def main():
    data=build();OUTPUT.write_bytes((json.dumps(data,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({'counts':data['counts'],'campaigns':data['campaigns']}))


if __name__=='__main__':main()
