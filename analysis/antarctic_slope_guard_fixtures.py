"""Prepare native-verified scope mutations without JavaScript numeric rewriting."""
import copy
import hashlib
import json
import subprocess
from test_rust_query_browser import ROOT,CLI


def prepare(directory,mode):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    targets=[]
    cases=['count','date','depth'] if mode=='metadata' else ['value','depth','coverage','years','owner','collection']
    for case in cases:
        bad=copy.deepcopy(packet)
        owner=next(r for r in bad['collections']['objects'] if r['id']=='current:antarctic-slope')
        if mode=='metadata':
            receipt=bad['manifest']['dashboard_receipt'];source=json.loads(receipt['source_json'])
            entry=next(r for r in source['entries'] if r['id']==owner['id'])
            for row in [owner,entry]:
                if case=='count':row['capabilities']['observed_velocity']=1
                elif case=='date':row['latest_observation_date']='2026-10-09'
                else:next(s for s in row['series'] if s['evidence_role']=='local_observed_velocity_summaries_not_current_dimensions')['nominal_depth_m']=506
            receipt['source_json']=json.dumps(source,ensure_ascii=False)
            receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
            bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        else:
            rows=bad['collections']['current_velocity_samples']
            if case=='value':rows[0]['eastward_mean_cm_s']=0
            elif case=='depth':rows[0]['nominal_depth_m']=506
            elif case=='coverage':rows[0]['hourly_coverage_fraction']=1
            elif case=='years':rows[50]['contributing_years'].append(2017)
            elif case=='owner':owner['velocity_sample_ids']=[]
            else:del bad['collections']['current_velocity_samples']
        target=directory/f'm6-{mode}-{case}.json'
        target.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf8')
        result=subprocess.run([str(CLI),str(target)],capture_output=True,text=True,encoding='utf8')
        expected=['M6 observed'] if mode=='metadata' else ['M6 velocity','Unresolved current_velocity_samples']
        assert result.returncode==2 and any(e in result.stderr for e in expected),result.stderr
        targets.append(target)
    return targets


def wasm_rejections(page,targets):
    return page.evaluate('''async paths=>{
      const results=[];
      for(const path of paths){
        const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports,
          raw=new Uint8Array(await(await fetch(path)).arrayBuffer()),ptr=e.osw_alloc(raw.length);
        try{new Uint8Array(e.memory.buffer,ptr,raw.length).set(raw);e.osw_load(ptr,raw.length);
          results.push(JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len()))));
        }finally{e.osw_dealloc(ptr,raw.length);}
      }return results;
    }''',['/'+p.relative_to(ROOT).as_posix() for p in targets])
