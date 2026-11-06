// Cloud-only native/WASM parity on the small reviewed scalar snapshot.
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
const native=inside(process.argv[2]),wasmPath=inside(process.argv[3]);
const source=inside('research/eacc-local-extent-evidence-bundle-v1.json');
const raw=readFileSync(source),sha=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(raw.length,835839);
assert.equal(sha(raw),'e4ca7c532c39d22efc2d6600a89424f48558669fe6e6682b1c6ec9442d00cdf8');
const wasmBytes=readFileSync(wasmPath);
const {instance}=await WebAssembly.instantiate(wasmBytes,{}),engine=instance.exports;
const decode=()=>{
  const length=engine.osw_result_len();assert.ok(length<=2*1024*1024);
  return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(new Uint8Array(engine.memory.buffer,engine.osw_result_ptr(),length)));
};
const invoke=(name,value)=>{
  const bytes=value instanceof Uint8Array?value:new TextEncoder().encode(JSON.stringify(value));
  const ptr=engine.osw_alloc(bytes.length);
  try{new Uint8Array(engine.memory.buffer,ptr,bytes.length).set(bytes);engine[name](ptr,bytes.length);return decode();}
  finally{engine.osw_dealloc(ptr,bytes.length);}
};
const nativeCall=(query,record=false)=>{
  const args=['--local-extents',source,...(query===undefined?[]:record?['--record','-']:['-'])];
  const result=spawnSync(native,args,{input:query===undefined?undefined:JSON.stringify(query),encoding:'utf8',maxBuffer:2*1024*1024});
  assert.ifError(result.error);
  if(result.status!==0)return {ok:false,error:result.stderr.trim()};
  return JSON.parse(result.stdout);
};
const metadata=invoke('osw_local_extents_load',raw);
assert.equal(metadata.ok,true);assert.deepEqual(metadata,nativeCall());
assert.equal(metadata.complete_atlas_loaded,false);
assert.equal(metadata.physical_width_inventory_increment,0);
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
];
const checks=[];
for(const query of requests){
  const actual=invoke('osw_local_extents_query',query),expected=nativeCall(query);
  assert.deepEqual(actual,expected);
  checks.push({collection:query.collection,ok:actual.ok,total:actual.total??null});
}
const rows=invoke('osw_local_extents_query',requests[0]).rows;
assert.equal(rows.length,12);
const request={collection,id:rows[0].id};
const record=invoke('osw_local_extents_record',request);
assert.deepEqual(record,nativeCall(request,true));
assert.equal(record.case_context.id,record.record.case_id);
// Failed loads must invalidate only this scope, without stale-query success.
const changed=Buffer.from(raw);changed[0]=32;
assert.equal(invoke('osw_local_extents_load',changed).ok,false);
assert.deepEqual(invoke('osw_local_extents_query',requests[0]),{ok:false,error:'Local-extent store not loaded'});
assert.equal(invoke('osw_local_extents_load',raw).ok,true);
engine.osw_local_extents_metadata();assert.deepEqual(decode(),metadata);
const output=resolve('.pytest_cache/current-local-extent-query-check-v1');mkdirSync(output,{recursive:true});
const report={schema:'osw.current-local-extent-query.parity.v1',source_commit:process.env.GITHUB_SHA,
  run_id:process.env.GITHUB_RUN_ID,run_attempt:process.env.GITHUB_RUN_ATTEMPT,
  node_version:process.version,source_bytes:raw.length,source_sha256:sha(raw),wasm_sha256:sha(wasmBytes),wasm_bytes:wasmBytes.length,
  query_parity_checks:checks,record_case_resolution_verified:true,failed_reload_invalidates_scope:true,
  complete_atlas_loaded:false,physical_width_inventory_increment:0,source_velocity_arrays_processed:false};
writeFileSync(resolve(output,'parity.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({query_parity_checks:checks.length,record_parity:true,failed_reload_verified:true,wasm_bytes:wasmBytes.length}));
