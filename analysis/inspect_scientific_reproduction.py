"""Read-only, bounded field differences for exact scientific rebuild failures."""
import importlib
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT=Path(__file__).resolve().parents[1]
TARGETS=[('build_aleutian_p14n_vector_section','research/aleutian-p14n-1993-observed-vector-section.json',{},None),
         ('build_p14n_hydrography_companion','research/aleutian-p14n-1993-hydrography-correspondence.json',{},None),
         ('build_p14n_component_spans','research/aleutian-p14n-1993-component-spans.json',{},None),
         ('build_p14n_native_field_audit','research/aleutian-p14n-1993-native-vector-support.json',{},None),
         ('build_p14n_underway_averages','research/aleutian-p14n-1993-underway-averages.json',{},None),
         ('build_p14n_run_composite','research/aleutian-p14n-1993-run-composite.json',{},None),
         ('loop_durante_composite_contours','research/loop-durante-2026-composite-contour-paths.json',{},None),
         ('build_necc_paired_vector_evidence','research/pacific-necc-paired-vector-direction-evidence.json',{},1),
         ('build_norkyst_continuous_sections','research/source-data/norkyst-ingoy-months-2024/section-diagnostic-pilot.json',{'write_asset':False},None)]


def differences(expected, actual):
    result={'exact':True,'changed_numeric_leaves':0,'changed_other_leaves':0,'maximum_absolute_numeric_difference':0.,'numeric_fields':{},'first_differences':[]}
    def note(path,a,b,numeric=False):
        result['exact']=False
        key='changed_numeric_leaves' if numeric else 'changed_other_leaves';result[key]+=1
        if numeric:
            result['maximum_absolute_numeric_difference']=max(result['maximum_absolute_numeric_difference'],abs(a-b))
            field=next((part for part in reversed(path.split('/')) if part and not part.isdigit()),'[root]')
            if field not in result['numeric_fields'] and len(result['numeric_fields'])>=64:field='[other fields]'
            group=result['numeric_fields'].setdefault(field,{'changed_leaves':0,'maximum_absolute_difference':0.})
            group['changed_leaves']+=1;group['maximum_absolute_difference']=max(group['maximum_absolute_difference'],abs(a-b))
        if len(result['first_differences'])<20:
            row={'pointer':path,'retained':a,'rebuilt':b}
            if numeric:row.update(retained_float_hex=float(a).hex(),rebuilt_float_hex=float(b).hex(),absolute_difference=abs(a-b))
            result['first_differences'].append(row)
    def walk(a,b,path=''):
        if type(a)!=type(b):note(path,str(type(a)),str(type(b)));return
        if isinstance(a,dict):
            if set(a)!=set(b):note(path+'/[keys]',sorted(a),sorted(b))
            for k in sorted(set(a)&set(b)):walk(a[k],b[k],path+'/'+k.replace('~','~0').replace('/','~1'))
        elif isinstance(a,list):
            if len(a)!=len(b):note(path+'/[length]',len(a),len(b))
            for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+'/'+str(i))
        elif a!=b or isinstance(a,float) and a.hex()!=b.hex():note(path,a,b,isinstance(a,(int,float)) and not isinstance(a,bool))
    walk(expected,actual);return result


def main():
    import numpy,pyproj,xarray,netCDF4
    print(json.dumps({'environment':{'python':sys.version,'system':platform.system(),'machine':platform.machine(),
        'numpy':numpy.__version__,'pyproj':pyproj.__version__,'xarray':xarray.__version__,'netCDF4':netCDF4.__version__}}),flush=True)
    failed=False
    for module,path,arguments,tuple_index in TARGETS:
        try:
            producer=importlib.import_module(module);actual=producer.build(**arguments);retained=(ROOT/path).read_bytes()
            if tuple_index is not None:actual=actual[tuple_index]
            options={'separators':(',',':')} if module=='loop_durante_composite_contours' else {'indent':2}
            rebuilt=producer.encoded(actual) if hasattr(producer,'encoded') else (json.dumps(actual,allow_nan=False,**options)+'\n').encode('utf8')
            report=differences(json.loads(retained),actual)
            report.update(encoded_bytes_exact=retained==rebuilt,retained_sha256=hashlib.sha256(retained).hexdigest(),rebuilt_sha256=hashlib.sha256(rebuilt).hexdigest())
            failed|=not report['encoded_bytes_exact'];print(json.dumps({'module':module,'report':report},allow_nan=False),flush=True)
        except Exception as error:
            failed=True;print(json.dumps({'module':module,'error_type':type(error).__name__,'error':str(error)[:1000]}),flush=True)
    return int(failed)


if __name__=='__main__':sys.exit(main())
