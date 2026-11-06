"""Strict declared HYCOM packed fields, independently checked against netCDF4."""
import json,re
import numpy as np
import netCDF4

FIELDS={'water_u':('m/s','eastward_sea_water_velocity','0.0'),'water_v':('m/s','northward_sea_water_velocity','0.0'),'salinity':('psu','sea_water_salinity','20.0')}


def specification(das,field):
    if field not in FIELDS:raise ValueError('Only original three native fields supported')
    text=das.decode('utf8');block=re.search(r'(?ms)^ {4}'+field+r'\s*\{\s*\n(.*?)^ {4}\}',text)
    if not block:raise ValueError('Original native field DAS block required')
    attrs={}
    for dtype,key,value in re.findall(r'\b(String|Int16|Int32|Float32|Float64|UInt16|UInt32|Byte)\s+(\w+)\s+([^;]+);',block.group(1)):
        if key in attrs:raise ValueError('Unique original typed field attributes required')
        attrs[key]={'type':dtype,'literal':value.strip()}
    if any(key in attrs for key in ['_Unsigned','valid_min','valid_max','valid_range']):raise ValueError('Undeclared extra CF validity/unsigned rules require a new decoder version')
    units,standard,offset=FIELDS[field]
    expected={'units':('String',json.dumps(units)),'standard_name':('String',json.dumps(standard)),'_FillValue':('Int16','-30000'),'missing_value':('Int16','-30000'),'scale_factor':('Float32','0.001'),'add_offset':('Float32',offset)}
    if any(attrs.get(key)!={'type':dtype,'literal':literal} for key,(dtype,literal) in expected.items()):raise ValueError('Exact original typed units/frame/fill/Float32scale+offset required')
    return {'schema':'osw.hycom-packed-int16-field-specification.v1','field':field,'attributes':attrs,'decode_dtype':'float32','mask_before_scale':True,'physical_current_bottom_established':False}


def validate(spec):
    field=spec['field']
    if field not in FIELDS or spec['decode_dtype']!='float32' or spec['mask_before_scale'] is not True:raise ValueError('Original packed-field decoder contract required')
    attrs=spec['attributes'];units,standard,offset=FIELDS[field]
    for key,dtype,literal in [('units','String',json.dumps(units)),('standard_name','String',json.dumps(standard)),('_FillValue','Int16','-30000'),('missing_value','Int16','-30000'),('scale_factor','Float32','0.001'),('add_offset','Float32',offset)]:
        if attrs.get(key)!={'type':dtype,'literal':literal}:raise ValueError('Frozen typed original packed metadata required')
    if any(key in attrs for key in ['_Unsigned','valid_min','valid_max','valid_range']):raise ValueError('Unsupported CF validity attribute')


def decode(raw,spec):
    validate(spec)
    if not isinstance(raw,np.ndarray) or raw.dtype.kind!='i' or raw.dtype.itemsize!=2:raise ValueError('Actual native signed Int16 array required before decoding')
    masked=np.ma.array(raw,mask=(raw==np.int16(-30000)),copy=False)
    result=masked*np.float32(spec['attributes']['scale_factor']['literal'])+np.float32(spec['attributes']['add_offset']['literal'])
    if result.dtype!=np.dtype('float32'):raise ValueError('Original Float32 CF arithmetic must be preserved')
    return result


def conformance(specs):
    raw=np.asarray([-32768,-30000,-20000,-1000,-1,0,1,1000,14999,15000,30000,32767],dtype=np.int16);records=[]
    if set(specs)!=set(FIELDS):raise ValueError('All three original fields required')
    for field,spec in specs.items():
        validate(spec)
        with netCDF4.Dataset('packed-fixture','w',diskless=True,persist=False) as ds:
            ds.createDimension('n',len(raw));var=ds.createVariable(field,'i2',('n',),fill_value=np.int16(-30000));var.setncattr('missing_value',np.int16(-30000));var.setncattr('scale_factor',np.float32(spec['attributes']['scale_factor']['literal']));var.setncattr('add_offset',np.float32(spec['attributes']['add_offset']['literal']));var.set_auto_maskandscale(False);var[:]=raw;var.set_auto_maskandscale(True);expected=var[:]
        actual=decode(raw,spec);mask=np.ma.getmaskarray(expected)
        if not np.array_equal(np.ma.getmaskarray(actual),mask) or actual.dtype!=expected.dtype or not np.array_equal(actual.data[~mask],expected.data[~mask]) or np.ma.filled(actual,np.nan).tobytes()!=np.ma.filled(expected,np.nan).tobytes():raise ValueError('Decoder differs from independent netCDF4auto-mask/scale Float32 reference')
        records.append({'field':field,'reference':'netCDF4.Variable auto_maskandscale on synthetic in-memory Int16 fixture','mask_equal':True,'dtype_equal':True,'nonmissing_values_equal':True,'filled_float32_bytes_equal':True,'fixture_values':len(raw),'source_field_requests':0})
    return {'schema':'osw.hycom-packed-field-decoder-conformance.v1','status':'ALL3_FIELDS_EXACT_NETCDF4_FLOAT32_MASK_SCALE_MATCH','records':records,'live_source_fields_read':0,'physical_current_bottom_established':False}
