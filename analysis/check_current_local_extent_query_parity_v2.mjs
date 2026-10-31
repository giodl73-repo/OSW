// Cloud-only small-target parity against the previously verified general engine.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,realpathSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {resolve,sep} from 'node:path';

assert.equal(process.env.GITHUB_ACTIONS,'true');
assert.equal(process.env.GITHUB_REF,'refs/heads/codex/current-measurement-gaps');
assert.equal(process.platform,'linux');
assert.match(readFileSync('/proc/self/status','utf8'),/^Cpus_allowed_list:\s*\d+\s*$/m);
for(const key of ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'])assert.equal(process.env[key],'1');
const root=realpathSync(process.cwd());
const inside=path=>{const value=realpathSync(resolve(path));assert.ok(value.startsWith(root+sep));return value;};
const fullNative=inside(process.argv[2]),smallNative=inside(process.argv[3]);
const smallPath=inside(process.argv[4]),baselinePath=inside(process.argv[5]);
const dataPath=inside('research/eacc-local-extent-evidence-bundle-v1.json');
const raw=readFileSync(dataPath),sha=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(raw.length,835839);
assert.equal(sha(raw),'e4ca7c532c39d22efc2d6600a89424f48558669fe6e6682b1c6ec9442d00cdf8');
const baselineReport=JSON.parse(readFileSync('research/current-local-extent-query-parity-result-v1.json','utf8'));
const baselineBytes=readFileSync(baselinePath),smallBytes=readFileSync(smallPath);
assert.equal(baselineBytes.length,baselineReport.wasm_bytes);
assert.equal(sha(baselineBytes),baselineReport.wasm_sha256);
assert.ok(smallBytes.length<=2*1024*1024,'Dedicated WASM exceeds2MiB raw delivery budget');
const makeEngine=async bytes=>{
  const {instance}=await WebAssembly.instantiate(bytes,{}),engine=instance.exports;
  const decode=()=>{
    const length=engine.osw_result_len();assert.ok(length<=2*1024*1024);
    return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(new Uint8Array(engine.memory.buffer,engine.osw_result_ptr(),length)));
  };
  return {memory:()=>engine.memory.buffer.byteLength,invoke:(name,value)=>{
    const payload=value instanceof Uint8Array?value:new TextEncoder().encode(JSON.stringify(value));
    const ptr=engine.osw_alloc(payload.length);
    try{new Uint8Array(engine.memory.buffer,ptr,payload.length).set(payload);engine[name](ptr,payload.length);return decode();}
    finally{engine.osw_dealloc(ptr,payload.length);}
  },metadata:()=>{engine.osw_local_extents_metadata();return decode();}};
};
const small=await makeEngine(smallBytes),baseline=await makeEngine(baselineBytes);
const nativeCall=(binary,query,record=false)=>{
  const args=['--local-extents',dataPath,...(query===undefined?[]:record?['--record','-']:['-'])];
  const result=spawnSync(binary,args,{input:query===undefined?undefined:JSON.stringify(query),encoding:'utf8',maxBuffer:2*1024*1024});
  assert.ifError(result.error);
  return result.status===0?JSON.parse(result.stdout):{ok:false,error:result.stderr.trim()};
};
const metadata=small.invoke('osw_local_extents_load',raw);
assert.equal(metadata.ok,true);
assert.deepEqual(metadata,baseline.invoke('osw_local_extents_load',raw));
assert.deepEqual(metadata,nativeCall(fullNative));assert.deepEqual(metadata,nativeCall(smallNative));
const collection='current_local_extents',cases='current_local_extent_cases';
const primary=[{field:'native_latitude_offset',op:'eq',value:0},{field:'normal_sample_step_km',op:'eq',value:5},
  {field:'threshold_fraction',op:'eq',value:.5},{field:'quantity',op:'eq',value:'core_to_positive_normal_threshold_extent'}];
const requests=[
  {collection,filters:primary,sort:{field:'month',direction:'asc'},limit:100},
  {collection:cases,filters:[{field:'native_latitude_offset',op:'eq',value:0},{field:'normal_sample_step_km',op:'eq',value:10},{field:'status',op:'eq',value:'missing_supported_profile'}],sort:{field:'month'}},
  {collection,filters:[{field:'whole_current_width_km',op:'eq',value:null}],limit:500},
  {collection,filters:[{field:'whole_current_width_km',op:'eq',value:0}]},
  {collection,offset:500,limit:500},
  {collection,filters:[{field:'status',op:'contains',value:'missing'}],limit:5},
  {collection,state_code:'NAT'},
  {collection,filters:[{field:'width_km',op:'eq',value:100}]},
  {collection,limit:501},
  {collection:'objects'},
  {collection,filters:[{field:'extent_bracket_km',op:'exists',value:false}],limit:500},
  {collection,filters:[{field:'status',op:'ne',value:'missing_supported_profile'}],sort:{field:'month',direction:'desc'},limit:35},
  {collection,filters:[{field:'threshold_fraction',op:'lt',value:.5}],limit:25},
  {collection,filters:[{field:'maximum_native_cell_scale_km',op:'gt',value:0}],limit:25},
  {collection,text:'  M07:OFFSET0  ',limit:100},
  {collection,sort:{field:'extent_bracket_km'}},
  {collection,filters:[{field:'source_scale_gate_passed',op:'in',value:[true]}]},
  {collection,filters:[{field:'threshold_fraction',op:'gt',value:'0.5'}]},
  {collection,filters:[{field:'status',op:'exists',value:1}]},
  {collection,sort:{field:'quantity',direction:'desc'},offset:3,limit:20},
  {collection,offset:4294967295,limit:1},
];
const checks=[];
for(const query of requests){
  const actual=small.invoke('osw_local_extents_query',query);
  assert.deepEqual(actual,nativeCall(smallNative,query));assert.deepEqual(actual,nativeCall(fullNative,query));
  assert.deepEqual(actual,baseline.invoke('osw_local_extents_query',query));
  checks.push({collection:query.collection,ok:actual.ok,total:actual.total??null});
}
// Platform-width overflow was never a valid WASM pagination request. The new
// native and WASM implementations must now reject it consistently as well.
for(const field of ['offset','limit']){
  const query={collection,[field]:4294967296};
  const actual=small.invoke('osw_local_extents_query',query);
  assert.equal(actual.ok,false);assert.deepEqual(actual,nativeCall(smallNative,query));assert.deepEqual(actual,nativeCall(fullNative,query));
  assert.equal(baseline.invoke('osw_local_extents_query',query).ok,false);
}
const rows=small.invoke('osw_local_extents_query',requests[0]).rows;assert.equal(rows.length,12);
for(const row of [rows[0],rows[6],rows[11]]){
  const request={collection,id:row.id},actual=small.invoke('osw_local_extents_record',request);
  assert.deepEqual(actual,baseline.invoke('osw_local_extents_record',request));
  assert.deepEqual(actual,nativeCall(fullNative,request,true));assert.deepEqual(actual,nativeCall(smallNative,request,true));
  assert.equal(actual.case_context.id,actual.record.case_id);
}
const changed=Buffer.from(raw);changed[0]=32;
for(const engine of [small,baseline]){
  assert.equal(engine.invoke('osw_local_extents_load',changed).ok,false);
  assert.deepEqual(engine.invoke('osw_local_extents_query',requests[0]),{ok:false,error:'Local-extent store not loaded'});
  assert.equal(engine.invoke('osw_local_extents_load',raw).ok,true);assert.deepEqual(engine.metadata(),metadata);
}
assert.ok(small.memory()<=64*1024*1024,'Dedicated engine exceeded64MiB memory budget on scalar checks');
const output=resolve('.pytest_cache/current-local-extent-query-check-v2');mkdirSync(output,{recursive:true});
const report={schema:'osw.current-local-extent-query.small-target-parity.v2',source_commit:process.env.GITHUB_SHA,
  run_id:process.env.GITHUB_RUN_ID,run_attempt:process.env.GITHUB_RUN_ATTEMPT,node_version:process.version,
  source_bytes:raw.length,source_sha256:sha(raw),wasm_bytes:smallBytes.length,wasm_sha256:sha(smallBytes),
  raw_wasm_budget_bytes:2*1024*1024,memory_budget_bytes:64*1024*1024,checked_memory_bytes:small.memory(),
  baseline_wasm_bytes:baselineBytes.length,baseline_wasm_sha256:sha(baselineBytes),query_parity_checks:checks,
  pagination_overflow_refusals_verified:2,record_case_resolution_checks:3,failed_reload_invalidates_scope:true,
  complete_atlas_loaded:false,physical_width_inventory_increment:0,source_velocity_arrays_processed:false};
writeFileSync(resolve(output,'parity.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({query_parity_checks:checks.length,record_checks:3,wasm_bytes:smallBytes.length,checked_memory_bytes:small.memory()}));
