"""Explicit offline extraction of a frozen CSIRO EAC100m source subset."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,io,json,math,zipfile
import h5py
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'research/source-data/eac-csiro-v23-100m'
PROTOCOL='plans/eac-csiro-v23-100m-source-selection-protocol-v1.md'
OPERATOR='analysis/acquire_eac_100m_source.py'
SOURCE_SHA='d27c6d424cd3ab9f2afdb9d353af45ba7a29bd162f3d8a8db693186ece6bef2f'
SOURCE_BYTES=8108045936
FIELDS=('UCUR','VCUR','TEMP','PSAL','UCUR_uncertainty','VCUR_uncertainty','TEMP_uncertainty','PSAL_uncertainty')
COORDINATES=('TIME','DEPTH','LONGITUDE','LATITUDE','BOTTOM_DEPTH')


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def array_pin(array):
    return {'dtype':array.dtype.str,'shape':list(array.shape),'bytes':array.nbytes,
            'sha256':hashlib.sha256(array.tobytes(order='C')).hexdigest()}


def attribute(value):
    if isinstance(value,bytes):return value.decode('utf8')
    if isinstance(value,np.ndarray):return [attribute(v) for v in value.tolist()]
    if isinstance(value,np.generic):return attribute(value.item())
    if isinstance(value,float) and not math.isfinite(value):return {'nonfinite_float':str(value)}
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    return str(value)


def write_json(path,document):
    Path(path).write_bytes((json.dumps(document,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode())


def write_npz(path,arrays):
    """Fixed archive metadata and source bytes, without object/pickle arrays."""
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name in sorted(arrays):
            buffer=io.BytesIO();np.save(buffer,arrays[name],allow_pickle=False)
            info=zipfile.ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3;info.external_attr=0o600<<16
            archive.writestr(info,buffer.getvalue(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)


def acquire(source_path,directory=DIRECTORY):
    source_path=Path(source_path);directory=Path(directory)
    if source_path.stat().st_size!=SOURCE_BYTES or sha(source_path)!=SOURCE_SHA:
        raise ValueError('CSIRO EAC complete source differs from the frozen original')
    directory.mkdir(parents=True,exist_ok=True)
    with h5py.File(source_path,'r') as source:
        arrays={name:source[name][...] for name in COORDINATES}
        indices=np.flatnonzero(arrays['DEPTH']==100)
        if len(indices)!=1:raise ValueError('Expected one exact source100m level')
        depth_index=int(indices[0])
        header={'schema':'osw.netcdf-source-attributes.v1','nonfinite_attribute_encoding':'explicit nonfinite_float object; data arrays retain original float64 bits',
                'global_attributes':{k:attribute(v) for k,v in source.attrs.items()},'datasets':{}}
        for name in [*COORDINATES,*FIELDS]:
            dataset=source[name]
            header['datasets'][name]={'shape':list(dataset.shape),'dtype':dataset.dtype.str,
                'dimension_scale_names':[list(dim.keys()) for dim in dataset.dims],
                'attributes':{k:attribute(v) for k,v in dataset.attrs.items() if k not in ['DIMENSION_LIST','REFERENCE_LIST']}}
        for name in FIELDS:
            dataset=source[name]
            if dataset.shape!=(3770,271,124) or header['datasets'][name]['dimension_scale_names']!=[['TIME'],['DEPTH'],['LONGITUDE']]:
                raise ValueError('Changed EAC variable dimension order or shape: '+name)
            if dataset.dtype.str!='<f8':raise ValueError('Changed EAC source float representation')
            arrays[name]=np.ascontiguousarray(dataset[:,depth_index,:])
        if any(arrays[name].shape!=(3770,124) for name in FIELDS):raise ValueError('Unexpected selected EAC shape')
        subset=directory/'selected-source.npz';write_npz(subset,arrays)
        # A second independent HDF5 read checks every stored selected source bit.
        with np.load(subset,allow_pickle=False) as saved:
            if set(saved.files)!=set(arrays):raise ValueError('Subset fields changed')
            for name in arrays:
                repeated=source[name][:,depth_index,:] if name in FIELDS else source[name][...]
                if array_pin(saved[name])!=array_pin(repeated):raise ValueError('EAC subset source bits changed: '+name)
        write_json(directory/'source-header.json',header)
    receipt={'schema':'osw.eac-fixed-depth-source-subset-acquisition.v1','status':'source_subset_not_current_dimensions',
        'current_id':'east-australian','entity_id':'current:east-australian','dataset_doi':'10.25919/sfw7-hc46',
        'provider_record_url':'https://data.csiro.au/dap/ws/v2/collections/69711',
        'source_download_url':'https://data.csiro.au/dap/ws/v2/collections/69711/data/67390004',
        'collection_common_id':52949,'collection_record_id':69711,'collection_version':23,'data_version':19,
        'original_source_file':'EAC_filled-daily-distance-depth-gridded-product_20120401-20220727.nc',
        'original_source_bytes':SOURCE_BYTES,'original_source_sha256':SOURCE_SHA,'complete_source_checksum_verified':True,
        'original_archive_bytes':381438579,'original_archive_sha256':'0d3a84a6042b3c4bcec123e24610da0dc7d4c8787db106465ee5297fa38d6ff4',
        'depth_m':100,'source_depth_index':depth_index,'source_profiles':3770,'source_positions':124,
        'source_fields':list(FIELDS),'coordinate_fields':list(COORDINATES),
        'source_array_sha256':{name:array_pin(value) for name,value in arrays.items()},
        'subset_file':'selected-source.npz','subset_sha256':sha(subset),'subset_bytes':subset.stat().st_size,
        'source_header_file':'source-header.json','source_header_sha256':sha(directory/'source-header.json'),
        'protocol_file':PROTOCOL,'protocol_sha256':sha(ROOT/PROTOCOL),
        'operator_file':OPERATOR,'operator_sha256':sha(ROOT/OPERATOR),
        'second_source_read_all_selected_bits_equal':True,'source_values_modified':False,'source_timestamps_modified':False,
        'license':'CC BY4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
        'attribution':'Sloyan, Bernadette; Cowley, Rebecca; Chapman, Chris (2023), East Australian Current gridded (depth, distance and time) mooring product. CSIRO collection metadata v23, data v19. doi:10.25919/sfw7-hc46. IMOS, NESP and Marine National Facility.',
        'data_descriptor':'Sloyan, Cowley and Chapman (2024), Scientific Data11,10, doi:10.1038/s41597-023-02857-x.',
        'extracted_utc':datetime.now(timezone.utc).isoformat(),'whole_current_width_km':None,'annual_width_range_km':None,
        'width_measurement_admitted':False,'width_rank_eligible':False,'geographic_current_edges':None}
    write_json(directory/'acquisition.json',receipt)
    return receipt


def verify(directory=DIRECTORY):
    directory=Path(directory);receipt=json.loads((directory/'acquisition.json').read_bytes())
    if receipt['original_source_sha256']!=SOURCE_SHA or receipt['original_source_bytes']!=SOURCE_BYTES:
        raise ValueError('Changed frozen EAC source identity')
    for name,pin in [('protocol_file','protocol_sha256'),('operator_file','operator_sha256')]:
        if sha(ROOT/receipt[name])!=receipt[pin]:raise ValueError('Changed EAC extraction operator/protocol')
    for name,pin in [('subset_file','subset_sha256'),('source_header_file','source_header_sha256')]:
        if sha(directory/receipt[name])!=receipt[pin]:raise ValueError('Changed EAC retained source')
    with np.load(directory/receipt['subset_file'],allow_pickle=False) as selected:
        if set(selected.files)!=set(FIELDS+COORDINATES):raise ValueError('Changed EAC subset members')
        arrays={name:selected[name] for name in selected.files}
    if {name:array_pin(value) for name,value in arrays.items()}!=receipt['source_array_sha256']:
        raise ValueError('Changed EAC selected array bits or shape')
    if any(receipt[key] is not False for key in ['source_values_modified','source_timestamps_modified','width_measurement_admitted','width_rank_eligible']):
        raise ValueError('Promoted EAC source subset')
    if any(receipt[key] is not None for key in ['whole_current_width_km','annual_width_range_km','geographic_current_edges']):
        raise ValueError('Source subset cannot acquire physical current dimensions')
    return receipt,arrays


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-netcdf',type=Path);args=parser.parse_args()
    receipt=acquire(args.source_netcdf) if args.source_netcdf else verify()[0]
    print(json.dumps({'status':'PASS','profiles':receipt['source_profiles'],'positions':receipt['source_positions'],
        'depth_m':receipt['depth_m'],'subset_bytes':receipt['subset_bytes'],'complete_source_checksum_verified':receipt['complete_source_checksum_verified']}))
