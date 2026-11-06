"""Prospective DAP2 array subset bounds; no network, field decoding or endpoint discovery."""
import copy,re
PRODUCT='ECCO_L4_OCEAN_VEL_05DEG_DAILY_V4R4'
ROLES=('time','level','lat','lon')
SIZES={'Float32':4,'Float64':8}
CAPS={'profiles':150,'levels':40,'cells':20000,'native_bytes':7000000,'numeric_values':250000}

def integer(value,label):
    if type(value) is not int or value<0:raise ValueError('Nonnegative integer required:'+label)
    return value

def identifier(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',value):raise ValueError('Unsupported array identifier')
    return value

def plan_subset(metadata,window):
    if metadata.get('product')!=PRODUCT or metadata.get('protocol')!='DAP2':raise ValueError('Exact product and DAP2 metadata required')
    if not re.fullmatch('[a-f0-9]{64}',metadata.get('metadata_sha256','')):raise ValueError('Metadata custody digest required;not proof by itself')
    axes=metadata['axis_names']
    if set(axes)!=set(ROLES) or len(set(axes.values()))!=4:raise ValueError('Four distinct named axes required')
    axes={r:identifier(axes[r]) for r in ROLES};dims=metadata['dimensions']
    if set(window)!=set(ROLES):raise ValueError('One complete contiguous window;no implicit or stride axes')
    lengths={};slabs={}
    for role,axis in axes.items():
        size=integer(dims[axis],'dimension');pair=window[role]
        if not isinstance(pair,(tuple,list)) or len(pair)!=2:raise ValueError('Inclusive start/stop required')
        start=integer(pair[0],'start');stop=integer(pair[1],'stop')
        if not start<=stop<size:raise ValueError('Window outside metadata dimension')
        lengths[role]=stop-start+1;slabs[axis]='['+str(start)+':1:'+str(stop)+']'
    profiles=lengths['time']*lengths['lat']*lengths['lon'];levels=lengths['level'];cells=profiles*levels
    if not 3<=profiles<=CAPS['profiles'] or levels>CAPS['levels'] or cells>CAPS['cells']:raise ValueError('Whole-window profile/level/cell cap')
    fields=metadata['fields'];coords=metadata['coordinate_fields']
    if set(coords)!=set(ROLES)|{'level_bounds'}:raise ValueError('All coordinates and vertical interfaces required')
    names=['EVEL','NVEL']+[identifier(coords[r]) for r in ROLES]+[identifier(coords['level_bounds'])]
    if len(set(names))!=len(names):raise ValueError('Unique coordinate and velocity names required')
    projection=[];native_bytes=0;numeric_values=0
    for name in names:
        item=fields[name]
        if item.get('kind')!='Array' or item.get('dtype') not in SIZES:raise ValueError('Unsupported Grid/structure/packed datatype;do not guess payload')
        field_dims=item['dimensions']
        if not isinstance(field_dims,list) or len(set(field_dims))!=len(field_dims):raise ValueError('Distinct explicit field dimensions required')
        selected={axis:lengths[r] for r,axis in axes.items()};field_slabs=dict(slabs)
        if name in ['EVEL','NVEL']:
            if set(field_dims)!=set(axes.values()) or len(field_dims)!=4 or item.get('units') not in ['m/s','m s-1']:raise ValueError('Geographic velocity dimensions/units required')
            if item.get('fill_metadata_present') is not True:raise ValueError('Velocity missing-value metadata required')
        elif name==coords['level_bounds']:
            extra=[d for d in field_dims if d!=axes['level']]
            if len(field_dims)!=2 or axes['level'] not in field_dims or len(extra)!=1 or integer(dims[extra[0]],'bounds')!=2 or item.get('units')!='m':raise ValueError('Two explicit vertical interfaces per level required')
            identifier(extra[0]);selected[extra[0]]=2;field_slabs[extra[0]]='[0:1:1]'
        else:
            role=next(r for r in ROLES if coords[r]==name)
            if field_dims!=[axes[role]]:raise ValueError('Coordinate must share selected axis')
            if role=='level' and item.get('units')!='m':raise ValueError('Depth coordinates must remain metres')
        count=1;expression=identifier(name)
        for dimension in field_dims:
            identifier(dimension)
            if dimension not in selected:raise ValueError('Unknown axis cannot be left unconstrained')
            count*=selected[dimension];expression+=field_slabs[dimension]
        numeric_values+=count;native_bytes+=count*SIZES[item['dtype']];projection.append(expression)
    if numeric_values>CAPS['numeric_values'] or native_bytes>CAPS['native_bytes']:raise ValueError('Whole-window numeric/native cap')
    return {'schema':'osw.ecco-prospective-subset-plan.v1','product':PRODUCT,'metadata_sha256':metadata['metadata_sha256'],'constraint_expression':','.join(projection),'window':copy.deepcopy(window),'profiles':profiles,'levels':levels,'cells':cells,'native_array_bytes':native_bytes,'numeric_values':numeric_values,'native_bytes_include_transport_overhead':False,'actual_endpoint_verified':False,'actual_transport_bound_verified':False,'actual_field_data_acquired':False,'current_axis_or_identity_validated':False,'scientific_depth_operator_frozen':False,'full_goal_complete':False}

def prerequisite_report(*,earthdata_available,metadata_verified,server_subset_verified,transport_bound_verified,scientific_operator_frozen):
    declared={'earthdata_available':earthdata_available,'metadata_verified':metadata_verified,'server_subset_verified':server_subset_verified,'transport_bound_verified':transport_bound_verified,'scientific_operator_frozen':scientific_operator_frozen}
    if any(type(v) is not bool for v in declared.values()):raise ValueError('Explicit boolean declarations only')
    return {'declared_missing_prerequisites':[k for k,v in declared.items() if not v],'all_declared_prerequisites_met':all(declared.values()),'actual_acquisition_verified':False,'interpretation':'Declarations alone do not verify a provider,credential,transport bound or scientific operator.'}
