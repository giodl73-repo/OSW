"""Audit original product headers without reading ocean or ship velocity arrays."""
from pathlib import Path
import hashlib,json,math
import xarray as xr

ROOT=Path(__file__).resolve().parents[1]
BASE='research/source-data/jasadcp-p14n-1993-native/'
OUTPUT='research/aleutian-p14n-1993-native-product-metadata.json'
FROZEN_INPUTS={'research/source-data/jasadcp-p14n-1993-native/00016_short.nc': '5b81d211bbb7aadc60c065f7c66ace16572f79569d7642bc96436923785bc6f8', 'research/source-data/jasadcp-p14n-1993-native/00016_long.nc': 'bbd76e9d7322c54d8476f6ef545bcc10ebb0678c5e145c897554cbe13c82f746', 'research/source-data/jasadcp-p14n-1993-native/acquisition.json': 'be53aa8de06de0355ce4fa597a0a6250873f955ed863bdc408c883364c704bc1', 'analysis/acquire_p14n_native_products.py': 'da4018dc0d9dc7af1b7f55f74360f92516f1f4c00d063843109509976ec8948c', 'plans/aleutian-p14n-native-source-preflight-v1.md': 'a5c49bc002ccbf72dee754dcc3ff12dea24e8328e9e2b2daf38601613355fb3e', 'research/source-data/jasadcp-p14n-1993/gateway.html': 'e2ada40a24ef2674d7c3c243936648f0b8cc7fad56682fb95afdbe6367b89f2b'}

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(data):return (json.dumps(data,indent=2,allow_nan=False)+'\n').encode()
def clean(value):
    if hasattr(value,'tolist'):return clean(value.tolist())
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean(v) for v in value]
    if isinstance(value,bytes):return value.decode('utf8',errors='strict')
    if isinstance(value,float) and not math.isfinite(value):return str(value)
    return value

def build():
    if len(FROZEN_INPUTS)!=6:raise ValueError('Missing native source/custody/declaration pins')
    for name,pin in FROZEN_INPUTS.items():
        if digest(name)!=pin:raise ValueError('Changed native metadata input: '+name)
    receipt=json.loads((ROOT/(BASE+'acquisition.json')).read_bytes())
    for row in receipt['source_files']:
        if row['sha256']!=FROZEN_INPUTS[row['file']] or (ROOT/row['file']).stat().st_size!=row['byte_count']:raise ValueError('Changed native custody binding')
    if receipt['producer_sha256']!=FROZEN_INPUTS[receipt['producer_file']] or receipt['protocol_sha256']!=FROZEN_INPUTS[receipt['protocol_file']]:raise ValueError('Changed native declaration binding')
    products=[]
    for name in ['00016_short.nc','00016_long.nc']:
        with xr.open_dataset(ROOT/(BASE+name),decode_cf=False,create_default_indexes=False) as data:
            if dict(data.sizes)!={'time':11455,'depth_cell':120}:raise ValueError('Changed native dimensions')
            if data.attrs['SACID']!='00016' or '325023_1' not in data.attrs['cruise_id']:raise ValueError('Changed native cruise identity')
            if data.time.attrs['units']!='days since 1993-01-01 00:00:00':raise ValueError('Changed native time units')
            for key in ['u','v','depth']:
                if data[key].dims!=('time','depth_cell'):raise ValueError('Changed profile/depth representation')
            if name=='00016_short.nc':
                for key in ['u','v','uship','vship']:
                    if data[key].attrs['units']!='meter second-1':raise ValueError('Changed ocean/ship velocity units')
                if 'Time at the end of the ensemble' not in data.attrs['CODAS_variables']:raise ValueError('Changed time support definition')
                if 'used to mask u, v' not in data.attrs['CODAS_variables']:raise ValueError('Changed editing-mask definition')
            variables={key:{'dimensions':list(var.dims),'shape':list(var.shape),'dtype':str(var.dtype),'attributes':clean(var.attrs)} for key,var in data.variables.items()}
            attrs={key:clean(data.attrs[key]) for key in ['featureType','history','Conventions','software','hg_changeset','title','description','cruise_id','yearbase','SACID','project','platform','contributor_name','contributor_institute','contributor_role','QC_Manual','QC_indicator','QC_software']}
            # Definitions are distinct from variable arrays; keep native profile-bit meanings separate from CTD WOCE codes.
            products.append({'source_file':BASE+name,'source_sha256':digest(BASE+name),'dimensions':dict(data.sizes),'attributes':attrs,'variables':variables,
                             'provider_variable_definitions':data.attrs['CODAS_variables'],'provider_processing_note_sha256':hashlib.sha256(data.attrs['CODAS_processing_note'].encode()).hexdigest()})
    return {'schema':'osw.native-product-metadata.v1','current_id':'aleutian','status':'source_metadata_only_pending_underway_operator',
            'input_sha256':dict(FROZEN_INPUTS),'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'products':products,'ocean_and_ship_velocity_arrays_inspected':False,'selected_local_profile_count':None,'actual_sample_intervals_determined':False,
            'profile_flag_bit_meanings':{'1':'bad bin','2':'bad percent good','4':'below bottom'},'profile_flags_are_woce_ctd_quality_codes':False,
            'interpretation':['Both files expose 11,455 time records and 120 depth cells for the entire cruise, not a local branch count.',
            'The short product already contains Earth-coordinate ocean u/v and ship uship/vship. Do not add ship motion again.',
            'Short-product time and GPS coordinates refer to ensemble end. Bin centers are nominal metres without sound-speed-profile correction; depth is a time-by-cell array.',
            'Profile editing flags are CODAS bits, not WOCE CTD quality codes. A CODAS bit4 below-bottom flag has a different meaning from a CTD quality number.',
            'Native time spacing, velocity support, short/long numerical correspondence and underway segmentation require a separately declared field audit.'],
            'new_width_record_admitted':False,'current_association_verified':False,'whole_current_width_km':None,'annual_width_range_km':None,'physical_edge_geometry_admitted':False}

def verify():
    report=build()
    if (ROOT/OUTPUT).read_bytes()!=encoded(report):raise ValueError('Stale native metadata audit')
    return report

if __name__=='__main__':
    report=build();(ROOT/OUTPUT).write_bytes(encoded(report))
    print(json.dumps({'products':len(report['products']),'metadata_records_per_product':11455,'depth_cells_per_record':120,'velocity_arrays_inspected':False}))
