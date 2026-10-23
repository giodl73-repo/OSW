"""Lossless supplementary native100m/200m rows; no current-dimension admission.

The source reconstruction and profile browser gate precede atlas integration.
"""
import calendar
import json
import math
from pathlib import Path

import numpy as np

from acquire_indian_secc_hycom_2013 import pin
from acquire_south_indian_front_levels import FIELDS, BASE
from package_south_indian_front_levels import DESTINATION, ROOT

COLLECTION = 'hydrography_samples'
SOURCE_ID = 'source:hycom-south-indian-front-levels-2013'
FIELD_NAMES = {'water_u':'eastward_velocity_m_s', 'water_v':'northward_velocity_m_s',
               'water_temp':'in_situ_temperature_c', 'salinity':'salinity_psu'}


def samples(document, selection):
    """Keep every native cell, missing means, counts and unrounded numbers."""
    if (document.get('schema') != 'osw.south-indian-hycom-front-level-monthly.v1'
            or document.get('dataset_url') != BASE or document.get('source_model_year') != 2013
            or document.get('units') != {n:v[1] for n,v in FIELDS.items()}):
        raise ValueError('Changed source identity/year/units')
    for key in ['current_association_verified', 'physical_width_admitted',
                'physical_axis_admitted', 'seasonal_footprint_admitted']:
        if document.get(key) is not False:
            raise ValueError('Source rows cannot admit current association or dimensions')
    lat,lon,depth = [document[n] for n in ['latitude_degrees_north','longitude_degrees_east','depth_m']]
    if len(lat)!=326 or len(lon)!=3 or depth!=[100,200]:
        raise ValueError('Changed native grid shape/depth')
    if (not all(math.isfinite(v) for v in [*lat,*lon,*depth])
            or not all(a<b for a,b in zip(lat,lat[1:]))
            or not all(a<b for a,b in zip(lon,lon[1:])) or lon[1]!=80):
        raise ValueError('Invalid native coordinates')
    if selection['selection']!={'depth':[19,22],'lat':list(range(800,1126)),'lon':[3249,3250,3251]}:
        raise ValueError('Changed supplementary native source indices')
    months=document['months']
    if [m['month'] for m in months]!=list(range(1,13)):
        raise ValueError('Missing, reordered or repeated month')
    rows=[]
    for month in months:
        m=month['month'];minimum=math.ceil(.8*calendar.monthrange(2013,m)[1])
        expected_days=sum(len(r['time_indices']) for r in selection['requests'] if r['month']==m)
        if month['minimum_common_samples']!=minimum or month['sample_days']!=expected_days:
            raise ValueError('Changed common-calendar sample support')
        counts=np.asarray(month['common_samples'],dtype=object)
        fields={name:np.asarray(month['fields'][name],dtype=object) for name in FIELDS}
        if any(a.shape!=(2,326,3) for a in [counts,*fields.values()]):
            raise ValueError('Changed monthly field/count shape')
        for zi,z in enumerate(depth):
            for yi,y in enumerate(lat):
                for xi,x in enumerate(lon):
                    count=counts[zi,yi,xi]
                    if type(count) is not int or not 0<=count<=expected_days:
                        raise ValueError('Invalid common sample count')
                    values={FIELD_NAMES[name]:a[zi,yi,xi] for name,a in fields.items()}
                    eligible=count>=minimum
                    for value in values.values():
                        if (value is None)!= (not eligible):
                            raise ValueError('Mean/missingness differs from common eligibility')
                        if value is not None and (type(value) not in [float,int] or not math.isfinite(value)):
                            raise ValueError('Invalid model mean')
                    rows.append({'id':f'hydrography:front-levels:south-indian:2013:m{m:02d}:z{zi}:y{yi}:x{xi}',
                                 'profile_id':f'front-levels:m{m:02d}-z{zi}-x{xi}',
                                 'investigation_current_id':'south-indian', 'source_id':SOURCE_ID,
                                 'model_year':2013,'month':m,'depth_m':z,
                                 'latitude_degrees_north':y,'longitude_degrees_east':x,
                                 'source_depth_index':selection['selection']['depth'][zi],
                                 'source_latitude_index':selection['selection']['lat'][yi],
                                 'source_longitude_index':selection['selection']['lon'][xi],
                                 'common_daily_samples':count,'minimum_common_daily_samples':minimum,
                                 'eligible':eligible,**values,
                                 'current_association_verified':False,'physical_width_admitted':False})
    return rows


def verify(directory=DESTINATION):
    """Check retained product pins and JSON/NPZ equality before producing rows."""
    directory=Path(directory)
    manifest=json.loads((directory/'acquisition.json').read_bytes())
    if (manifest.get('schema')!='osw.south-indian-front-level-retained-source.v1'
            or manifest.get('source_model_year')!=2013 or manifest.get('native_depths_m')!=[100,200]
            or manifest.get('source_temperature_is_potential_temperature') is not False
            or any(manifest.get(k) is not False for k in ['current_association_verified',
                'physical_width_admitted','physical_axis_admitted','physical_length_admitted',
                'seasonal_footprint_admitted','annual_extrema_admitted'])):
        raise ValueError('Changed supplementary source identity or admission status')
    inputs={}
    def check(path,expected=None):
        actual=pin(path)
        if expected is not None and actual!=expected:
            raise ValueError('Changed source/query dependency: '+str(path))
        inputs[path.relative_to(ROOT).as_posix()]=actual['sha256']
    check(directory/'acquisition.json')
    for name,expected in manifest['files'].items():
        check(directory/name,expected)
    for name,expected in manifest['dependencies'].items():
        check(ROOT/name,expected)
    selection=json.loads((directory/'selection.json').read_bytes())
    document=json.loads((directory/'monthly-fields.json').read_bytes())
    if document['selection']!=pin(directory/'selection.json'):
        raise ValueError('Changed monthly selection binding')
    rows=samples(document,selection)
    with np.load(directory/'monthly.npz',allow_pickle=False) as arrays:
        for name in FIELDS:
            np.testing.assert_array_equal(np.asarray([m['fields'][name] for m in document['months']],dtype=float),arrays[name])
        np.testing.assert_array_equal([m['common_samples'] for m in document['months']],arrays['common_samples'])
        for field,name in [('latitude_degrees_north','lat'),('longitude_degrees_east','lon'),('depth_m','depth')]:
            np.testing.assert_array_equal(document[field],arrays[name])
        np.testing.assert_array_equal([m['month'] for m in document['months']],arrays['month'])
    check(ROOT/'analysis/south_indian_front_level_query.py')
    source={'id':SOURCE_ID,'kind':'model_source','title':'HYCOM 2013 South Indian supplementary 100m/200m native section',
            'url':BASE,'model_year':2013,'depths_m':[100,200],
            'source_file':(directory/'monthly-fields.json').relative_to(ROOT).as_posix(),
            'acquisition_file':(directory/'acquisition.json').relative_to(ROOT).as_posix(),
            'variables':{FIELD_NAMES[n]:{'provider_variable':n,'units':v[1]} for n,v in FIELDS.items()},
            'sampling':'Daily00Z common-valid monthly sample means; ceil80% calendar days; missing dates retained.',
            'interpretation':'Total model velocity and in-situ temperature at exact native depths; not geostrophic-reference velocity, layer mean, climatology or named-current footprint.',
            'rights':'Approved for public release. Distribution unlimited. Original NAVO metadata retained.',
            'current_association_verified':False,'physical_width_admitted':False}
    return rows,source,inputs


def evidence():
    """Join conditional derived properties without substituting raw temperature."""
    from build_south_indian_front_temperature import build, REPORT, THETA
    rows, source, inputs = verify()
    report = build()
    if (ROOT/REPORT).read_bytes() != (json.dumps(report, indent=2, allow_nan=False)+'\n').encode():
        raise ValueError('Changed conditional front-level temperature report')
    inputs.update(report['dependencies'])
    inputs[REPORT] = pin(ROOT/REPORT)['sha256']
    for row in rows:
        zi = report['depth_m'].index(row['depth_m'])
        yi = row['source_latitude_index']-800
        xi = row['source_longitude_index']-3249
        month = report['months'][row['month']-1]
        if month['common_samples'][zi][yi][xi] != row['common_daily_samples']:
            raise ValueError('Derived and raw cell support differs')
        row.update({THETA: month['fields'][THETA][zi][yi][xi],
                    'absolute_salinity_g_kg': month['fields']['absolute_salinity_g_kg'][zi][yi][xi],
                    'sea_pressure_dbar': report['sea_pressure_dbar'][zi][yi][xi],
                    'temperature_scale_verified': False, 'temperature_scale_assumption': 'ITS-90',
                    'potential_temperature_source_file': REPORT})
    source.update(derived_temperature_file=REPORT,
                  derived_temperature_gsw_version=report['gsw_version'],
                  temperature_scale_verified=False, temperature_scale_assumption='ITS-90',
                  derived_variables={THETA: report['units'][THETA],
                                     'absolute_salinity_g_kg': report['units']['absolute_salinity_g_kg'],
                                     'sea_pressure_dbar': 'dbar; depth-derived approximation'})
    return rows, source, report, inputs


def view_evidence():
    rows, source, report, inputs = evidence()
    folder = 'figures/south-indian-front-levels-2013/'
    template = 'analysis/south_indian_front_level_view.html'
    view = json.loads((ROOT/folder/'view.json').read_bytes())
    for key, path in [('source_manifest', (DESTINATION/'acquisition.json').relative_to(ROOT).as_posix()),
                      ('template', template), ('html', folder+'index.html'),
                      ('query_adapter', 'analysis/south_indian_front_level_query.py'),
                      ('derived_report', 'research/south-indian-2013-front-level-potential-temperature.json')]:
        if view[key] != pin(ROOT/path):
            raise ValueError('Changed supplementary profile-view dependency: '+key)
    if (view.get('native_depths_m') != [100, 200] or view.get('profiles') != 360
            or view.get('temperature_scale_verified') is not False
            or view.get('named_current_width_admitted') is not False):
        raise ValueError('Changed supplementary profile-view interpretation')
    for path in [folder+'index.html', folder+'view.json', template,
                 'analysis/build_south_indian_front_level_view.py']:
        inputs[path] = pin(ROOT/path)['sha256']
    return rows, source, report, inputs


def card_links():
    from urllib.parse import quote
    from build_south_indian_front_temperature import REPORT
    q = {'collection': COLLECTION, 'filters': [{'field': 'source_id', 'op': 'eq', 'value': SOURCE_ID}], 'limit': 100}
    links = [{'label': 'Explore 100m/200m profiles and conditional potential temperature',
              'url': '../figures/south-indian-front-levels-2013/'},
             {'label': 'Query supplementary native cells and derived properties',
              'url': 'query.html?q='+quote(json.dumps(q, separators=(',', ':')), safe='')}]
    for label, path in [('Query complete supplementary raw monthly fields',
                         'research/source-data/hycom-south-indian-front-levels-2013/monthly-fields.json'),
                        ('Query conditional potential temperature and its support', REPORT)]:
        q = {'document': path, 'pointer': '/months', 'limit': 1, 'offset': 0}
        links.append({'label': label, 'url': 'query.html?source-q='+quote(json.dumps(q, separators=(',', ':')), safe='')+'#source-query-title'})
    return links

