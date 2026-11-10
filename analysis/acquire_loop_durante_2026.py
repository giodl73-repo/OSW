"""Pinned author-processed Loop Current source intake; no dimension admission."""
import argparse
from datetime import datetime,timedelta
import hashlib,json,stat,zipfile
from pathlib import Path,PurePosixPath
import h5py
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'research/source-data/loop-durante-2026-v0'
PROTOCOL='plans/loop-durante-2026-source-selection-protocol-v1.md'
PROTOCOL_SHA='189b18cfe0687485f843094042852604e49ae4d5d43a5a06311fddc38fb73920'
OPERATOR='analysis/acquire_loop_durante_2026.py'
MEMBER='data/Figures2_4_processed.mat'
ARCHIVE_SHA='2594682dcaa2e007d7d46de8f17344ce5c269dcc91cf64423fabc4a2c01a8a24'
SOURCE_SHA='316daa53a45fc6b2817abfa4ba8da76344323d20c84c781bfa8705163235e073'
METADATA={
 'record.json':'ca9e7925815c108c6afcd43f95cd223fb984a3eff3ac5395d4ca8d4204a73c9a',
 'README.md':'d6ef4f328147f1bf7dd467282728ab99056b4aa8d7d8db071289bb132b337631',
 'CITATION.cff':'f71d9191d3f929a771f4a4b89ffc48bb7cf3c5a6387fe05d7cfbb5bf7d979767',
 'analysis.zip':'08f305cbbab18348bdd43064597eace684538abbf4479a5893761ca4fb584ba6',
 'plotting.zip':'ef9e395e0d422be37f460c0b95a290fe7ba31258f60218754dd911f9ccfe94aa',
 'DATA_DICTIONARY.md':'2d7c0c7275cff1eaa9933817a4489cc76b307c69c5c0488b0127a4858164219c'}
SELECTED=['CurAxisPositive','CurAxisNegative','Cmax','Cmin','Umax','Umin','Vmax','Vmin',
          'ADTmax','ADTmin','ADTmax_a','ADTmin_a','xdu','ydu','xduf','yduf','inma','inmaf',
          'tid','tisp','htimef','area_loop','AMR_loop','inmax_lc','inmin_lc']


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write(path,doc):Path(path).write_bytes((json.dumps(doc,indent=2,allow_nan=False)+'\n').encode())


def validate_members(members):
    names=[m.filename for m in members]
    if len(set(names))!=len(names) or sum(m.file_size for m in members)>150_000_000:raise ValueError('Duplicate or oversized archive inventory')
    for m in members:
        p=PurePosixPath(m.filename)
        if p.is_absolute() or '..' in p.parts or '\\' in m.orig_filename or ':' in m.filename or stat.S_ISLNK(m.external_attr>>16):raise ValueError('Unsafe archive member')
        if m.file_size>50_000_000 or m.compress_type not in [0,8]:raise ValueError('Unsupported archive member size/compression')


def matlab_time(values):
    values=np.asarray(values).reshape(-1);finite=values[np.isfinite(values)]
    if np.any((finite<690000)|(finite>770000)):raise ValueError('Source serial date outside declared calendar plausibility')
    dates=[datetime.fromordinal(int(v))-timedelta(days=366)+timedelta(days=float(v)%1) for v in finite]
    steps=np.diff(finite)
    return {'records':int(values.size),'nonfinite':int((~np.isfinite(values)).sum()),
            'first_finite_calendar':dates[0].isoformat() if dates else None,'last_finite_calendar':dates[-1].isoformat() if dates else None,
            'duplicate_finite_times':int(len(finite)-len(np.unique(finite))),
            'nonpositive_steps':int(np.count_nonzero(steps<=0)),'steps_larger_than_one_day':int(np.count_nonzero(steps>1)),
            'minimum_step_days':float(steps.min()) if len(steps) else None,'maximum_step_days':float(steps.max()) if len(steps) else None,
            'noninteger_serial_times':int(np.count_nonzero(finite!=np.floor(finite))),'timezone':None,
            'timezone_note':'Source documents MATLAB serial days but does not specify timezone here.'}


def inspect_source(path):
    if sha(path)!=SOURCE_SHA:raise ValueError('Changed author numerical source')
    schema=[];arrays={}
    with h5py.File(path,'r') as source:
        # No external data links or virtual datasets are needed for this file.
        def links(group):
            for name in group:
                link=group.get(name,getlink=True)
                if not isinstance(link,h5py.HardLink):raise ValueError('External/soft source link unsupported')
                value=group[name]
                if isinstance(value,h5py.Group):links(value)
                elif value.is_virtual or value.external:raise ValueError('External/virtual source dataset unsupported')
        links(source)
        for name,obj in source.items():
            cls=obj.attrs.get('MATLAB_class',b'');cls=cls.decode('ascii') if isinstance(cls,bytes) else str(cls)
            row={'field':name,'matlab_class':cls,'kind':'dataset' if isinstance(obj,h5py.Dataset) else 'group'}
            if isinstance(obj,h5py.Dataset):row.update(storage_shape=list(obj.shape),matlab_shape=list(reversed(obj.shape)),dtype=obj.dtype.str)
            else:row['child_fields']=list(obj)
            if name in SELECTED:
                if not isinstance(obj,h5py.Dataset) or obj.dtype.kind not in 'biuf' or cls!='double':raise ValueError('Changed selected numerical source schema')
                value=obj[()];finite=np.isfinite(value)
                row.update(source_array_sha256=hashlib.sha256(value.tobytes(order='C')).hexdigest(),
                           finite=int(finite.sum()),nonfinite=int((~finite).sum()),
                           minimum=float(value[finite].min()) if finite.any() else None,
                           maximum=float(value[finite].max()) if finite.any() else None)
                arrays[name]=value.T.copy() # MATLAB dimensions reverse HDF5 storage dimensions.
            schema.append(row)
    if set(arrays)!=set(SELECTED):raise ValueError('Missing selected author source field')
    axes={}
    for axis in ['CurAxisPositive','CurAxisNegative']:
        if arrays[axis].ndim!=2 or arrays[axis].shape[1]!=2:raise ValueError('Changed source composite-axis association')
        value=arrays[axis];finite=np.isfinite(value);paired=finite.all(axis=1)
        if np.any(np.abs(value[finite[:,0],0])>180) or np.any(np.abs(value[finite[:,1],1])>90):raise ValueError('Invalid source composite coordinates')
        axes[axis]={'source_rows':len(value),'paired_finite_rows':int(paired.sum()),
                    'longitude_only_finite_rows':int((finite[:,0]&~finite[:,1]).sum()),
                    'latitude_only_finite_rows':int((~finite[:,0]&finite[:,1]).sum()),
                    'all_missing_rows':int((~finite.any(axis=1)).sum()),
                    'longitude_bounds':list(map(float,[value[paired,0].min(),value[paired,0].max()])) if paired.any() else None,
                    'latitude_bounds':list(map(float,[value[paired,1].min(),value[paired,1].max()])) if paired.any() else None}
    times={key:matlab_time(arrays[key]) for key in ['tid','tisp','htimef']}
    tid=arrays['tid'].reshape(-1);tisp=arrays['tisp'].reshape(-1)
    if tid.shape!=tisp.shape:raise ValueError('Changed author concurrent time dimensions')
    common=np.isfinite(tid)&np.isfinite(tisp)
    concurrent={'identical_source_time_arrays':bool(np.array_equal(tid,tisp,equal_nan=True)),
                'position_index_basis':'zero_based_native_position; MATLAB index is position plus1',
                'finite_paired_entries':int(common.sum()),'paired_time_differences':int(np.count_nonzero(tid[common]!=tisp[common])),
                'tid_nonfinite_source_indices':np.flatnonzero(~np.isfinite(tid)).tolist(),
                'tisp_nonfinite_source_indices':np.flatnonzero(~np.isfinite(tisp)).tolist(),
                'missing_times_filled_from_other_axis':False}
    n=arrays['tid'].size
    if arrays['area_loop'].size!=n or arrays['AMR_loop'].size!=n:raise ValueError('Area source time association differs')
    masks={}
    for name,grid in [('inma','xdu'),('inmaf','xduf')]:
        index=arrays[name].reshape(-1)
        if not np.isfinite(index).all() or np.any(index!=np.floor(index)) or np.any(index<1) or np.any(index>arrays[grid].size) or len(np.unique(index))!=len(index):raise ValueError('Invalid MATLAB one-based source index')
        masks[name]={'source_indices':len(index),'grid_shape':list(arrays[grid].shape),'indexing':'one_based_MATLAB_column_major','is_verified_coastline':False}
    phases={}
    for name in ['inmax_lc','inmin_lc']:
        index=arrays[name].reshape(-1)
        if not np.isfinite(index).all() or np.any(index!=np.floor(index)) or np.any(index<1) or np.any(index>arrays['htimef'].size):raise ValueError('Invalid source phase/time association')
        phases[name]={'source_indices':len(index),'distinct_indices':len(np.unique(index)),'time_base':'htimef','indexing':'one_based_MATLAB','original_indices':index.astype(int).tolist()}
    report={'schema':'osw.loop-durante-2026-source-quality.v1','source_field_schema':schema,'selected_fields':SELECTED,
            'source_shape_order':'HDF5 storage shape; MATLAB shape is reversed, without rescaling values',
            'times':times,'concurrent_time_association':concurrent,'source_index_masks':masks,'source_phase_indices':phases,'source_composite_axes':axes,
            'composite_axes_are_daily_paths':False,'source_axis_member_support_counts_available':False,
            'underlying_daily_axis_coordinates_available':False,'axis_member_time_association_independently_verified':False,
            'surface_composite_member_support_counts_available':False,
            'independent_original_cmems_canek_reproduction':False,'current_length_admitted':False,'width_measurement_admitted':False,
            'annual_physical_range_admitted':False,'source_file_sha256':SOURCE_SHA,
            'source_numerical_data_are_author_processed':True,'metadata_strings_exposed_in_derived_schema':False}
    return report,arrays


def verify(directory=DIRECTORY):
    directory=Path(directory);receipt=json.loads((directory/'acquisition.json').read_bytes())
    if sha(ROOT/PROTOCOL)!=PROTOCOL_SHA or receipt['protocol_sha256']!=PROTOCOL_SHA:raise ValueError('Changed declared source protocol')
    if receipt['operator_sha256']!=sha(ROOT/OPERATOR):raise ValueError('Changed source intake operator')
    if receipt['schema']!='osw.loop-durante-2026-source-acquisition.v1':raise ValueError('Changed source receipt schema')
    required=set(METADATA)|{'Figures2_4_processed.mat','archive-inventory.json','quality.json'}
    if set(receipt['files'])!=required:raise ValueError('Changed retained source inventory')
    for name,entry in receipt['files'].items():
        if sha(directory/name)!=entry['sha256'] or (directory/name).stat().st_size!=entry['bytes']:raise ValueError('Changed retained source bytes '+name)
    archive=receipt['source_archive']
    if archive['sha256']!=ARCHIVE_SHA or archive['md5']!='db5a3615a6b103ff8b2311530785e0c0' or archive['bytes']!=14212662:
        raise ValueError('Changed provider archive identity')
    if receipt['current_length_admitted'] is not False or receipt['width_measurement_admitted'] is not False:raise ValueError('Intake cannot admit dimensions')
    expected={**METADATA,'Figures2_4_processed.mat':SOURCE_SHA,
              'archive-inventory.json':'1eef32f8877f1356372b80d5a864c446443a0d221869f91e00f20495b5c3ae3a'}
    for name,pin in expected.items():
        if sha(directory/name)!=pin or receipt['files'][name]['sha256']!=pin:raise ValueError('Changed retained author source '+name)
    record=json.loads((directory/'record.json').read_bytes())
    if record['metadata']['license']['id']!='cc-by-4.0' or record['metadata']['version']!='0':raise ValueError('Changed source release/license')
    report,arrays=inspect_source(directory/'Figures2_4_processed.mat')
    if json.loads((directory/'quality.json').read_bytes())!=report:raise ValueError('Changed source-quality report')
    return receipt,report,arrays


def ingest(archive_path,metadata_dir,directory=DIRECTORY,resume=False):
    directory=Path(directory);metadata_dir=Path(metadata_dir);archive_path=Path(archive_path)
    if directory.exists() and not resume:raise ValueError('Refusing overwrite of retained source; use explicit resume after inspection')
    def retain(name,data):
        path=directory/name
        if path.exists():
            if path.read_bytes()!=data:raise ValueError('Refusing changed retained original '+name)
        else:path.write_bytes(data)
    if sha(ROOT/PROTOCOL)!=PROTOCOL_SHA or sha(archive_path)!=ARCHIVE_SHA:raise ValueError('Changed source archive/protocol')
    for name,pin in METADATA.items():
        if sha(metadata_dir/name)!=pin:raise ValueError('Changed source metadata '+name)
    with zipfile.ZipFile(archive_path) as archive:
        members=archive.infolist();validate_members(members)
        if archive.testzip() is not None:raise ValueError('Source archive CRC failure')
        data=archive.read(MEMBER);dictionary=archive.read('data/DATA_DICTIONARY.md')
        if hashlib.sha256(data).hexdigest()!=SOURCE_SHA:raise ValueError('Changed selected author member')
        directory.mkdir(parents=True,exist_ok=resume)
        for name in METADATA:retain(name,(metadata_dir/name).read_bytes())
        retain('Figures2_4_processed.mat',data);retain('DATA_DICTIONARY.md',dictionary)
        write(directory/'archive-inventory.json',[{'name':m.filename,'bytes':m.file_size,'crc32':format(m.CRC,'08x')} for m in members])
    report,arrays=inspect_source(directory/'Figures2_4_processed.mat');write(directory/'quality.json',report)
    acquisition=json.loads((metadata_dir/'data.zip.receipt.json').read_bytes())
    files={p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in directory.iterdir() if p.is_file() and p.name!='acquisition.json'}
    receipt={'schema':'osw.loop-durante-2026-source-acquisition.v1','source_doi':'10.5281/zenodo.22652650','source_version':'0',
             'source_archive':acquisition,'selected_member':MEMBER,'source_license':'CC BY 4.0 per retained public API metadata',
             'documentary_disagreements':['README license-selection TODO remains despite API cc-by-4.0','CITATION.cff version1.0.0 versus record0','Manuscript DOI placeholder; publication status not verified','Advertised MANIFEST.sha256 absent from archive listing'],
             'protocol_file':PROTOCOL,'protocol_sha256':PROTOCOL_SHA,'operator_file':OPERATOR,'operator_sha256':sha(ROOT/OPERATOR),
             'files':files,'current_length_admitted':False,'width_measurement_admitted':False}
    write(directory/'acquisition.json',receipt);return verify(directory)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path);parser.add_argument('--metadata-dir',type=Path);parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    receipt,report,arrays=ingest(args.archive,args.metadata_dir,resume=args.resume) if args.archive else verify()
    print(json.dumps({'selected_fields':len(arrays),'times':report['times'],'phases':{k:v['source_indices'] for k,v in report['source_phase_indices'].items()}}))
