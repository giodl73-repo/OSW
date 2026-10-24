"""Read exact OSCAR pairs and compare the old target u field without admission."""
import csv,datetime as dt,hashlib,io,json,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/source-data/oscar-necc-vectors-2013'
OLD=ROOT/'research/source-data/oscar-necc-2013-140w/section.csv'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def declaration():
    d=json.loads((BASE/'preflight.json').read_bytes())
    for name,pin in d['input_sha256'].items():
        if digest(ROOT/name)!=pin:raise ValueError('Changed declared NECC input '+name)
    if d['fully_blinded'] or d['v_or_neighboring_velocities_viewed_before_declaration'] or not d['previous_u_exposure']:raise ValueError('Changed exposure history')
    return d

def metadata():
    d=json.loads((BASE/'metadata.json').read_bytes());attrs={(r[1],r[2]):r[4] for r in d['table']['rows'] if r[0]=='attribute'}
    if attrs['NC_GLOBAL','version']!='2017.0' or any(attrs.get((v,'units'))!='m s-1' for v in ['u','v']):raise ValueError('Changed OSCAR version or units')
    return attrs

def rows(path,columns,units):
    reader=csv.reader(io.StringIO(Path(path).read_text(encoding='utf8')))
    if next(reader,None)!=columns or next(reader,None)!=units:raise ValueError('Changed source CSV columns or units')
    for row in reader:
        if not row:continue
        if len(row)!=len(columns):raise ValueError('Malformed source row')
        yield dict(zip(columns,row))

def number(text,fills=()):
    try:value=float(text)
    except ValueError as error:raise ValueError('Malformed source number') from error
    return value if math.isfinite(value) and value not in fills else None

def stamp(text):
    value=dt.datetime.fromisoformat(text.replace('Z','+00:00'))
    if value.tzinfo!=dt.timezone.utc or value.strftime('%Y-%m-%dT%H:%M:%SZ')!=text:raise ValueError('Noncanonical source UTC timestamp')
    return text

def old_target():
    result={}
    for r in rows(OLD,['time','depth','latitude','longitude','u'],['UTC','m','degrees_north','degrees_east','m s-1']):
        key=(stamp(r['time']),float(r['latitude']),float(r['longitude']))
        if float(r['depth'])!=15 or key in result:raise ValueError('Changed old target support')
        result[key]=number(r['u'])
    if len(result)!=2664:raise ValueError('Changed old target count')
    return result

def longitude_axis(path):
    values=[float(r['longitude']) for r in rows(path,['longitude'],['degrees_east'])]
    if len(values)!=3 or values!=sorted(set(values)) or values[1]!=220 or any(abs(b-a-1/3)>1e-4 for a,b in zip(values,values[1:])):raise ValueError('Unexpected native neighboring longitudes')
    return values

def parse(path,axis_path):
    declaration();attrs=metadata();old=old_target();longitudes=longitude_axis(axis_path)
    fills={}
    for v in ['u','v']:
        fills[v]=set()
        for key in ['_FillValue','missing_value']:
            if (v,key) in attrs:
                try:
                    value=float(attrs[v,key])
                    if math.isfinite(value):fills[v].add(value)
                except ValueError:raise ValueError('Unsupported source fill declaration')
    times=sorted({k[0] for k in old});latitudes=sorted({k[1] for k in old});vectors={}
    for r in rows(path,['time','depth','latitude','longitude','u','v'],['UTC','m','degrees_north','degrees_east','m s-1','m s-1']):
        key=(stamp(r['time']),float(r['latitude']),float(r['longitude']))
        if float(r['depth'])!=15 or key in vectors:raise ValueError('Duplicate vector or changed depth')
        vectors[key]=(number(r['u'],fills['u']),number(r['v'],fills['v']))
    expected={(t,lat,lon) for t in times for lat in latitudes for lon in longitudes}
    if len(times)!=72 or len(latitudes)!=37 or set(vectors)!=expected:raise ValueError('Incomplete or changed vector support')
    for key,value in old.items():
        actual=vectors[key][0]
        if (actual is None)!=(value is None) or (value is not None and struct.pack('!d',value)!=struct.pack('!d',actual)):raise ValueError('Changed target u value or mask')
    return {'times':times,'latitudes':latitudes,'longitudes':longitudes,'vectors':vectors,'old_target_values_exact':len(old),'paired_finite_positions':sum(u is not None and v is not None for u,v in vectors.values()),'vector_positions':len(vectors)}
