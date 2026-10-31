// Cloud-only complete-response equality, including an installed-parent capture.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {invoke} from './check_south_java_compiled_catalog_v1.mjs';
import {responseBudget} from './eicc_reference_response_budget_v1.mjs';
assert.equal(process.env.GITHUB_ACTIONS,'true');
assert.equal(process.env.GITHUB_REPOSITORY,'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF,'refs/heads/codex/current-measurement-gaps');
assert.equal(process.env.OSW_CORE_VELOCITY_DELIVERY_V1,'1');
const [mode,wasmPath,payloadPath,fixturePath,metadataPath,outputPath,expectedWasmSha]=process.argv.slice(2);
assert.equal(process.argv.slice(2).length,7);assert(['parent','main','index'].includes(mode));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert(fs.statSync(wasmPath).size<=64000000);
assert(fs.statSync(payloadPath).size<=(mode==='index'?536870912:210000000));
assert(fs.statSync(fixturePath).size<=16777216);
const fixture=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
assert.equal(fixture.queries.length,mode==='parent'?1:mode==='main'?41:20);
let binary=fs.readFileSync(wasmPath);assert.equal(sha(binary),expectedWasmSha);
const {instance}=await WebAssembly.instantiate(binary,{});binary=null;
const engine=instance.exports;
let payload=fs.readFileSync(payloadPath);assert.equal(sha(payload),fixture.payload_sha256);
let metadata=invoke(engine,mode==='index'?'osw_index_load':'osw_load',payload,payload.length+2097152);payload=null;
assert.equal(metadata.ok,true,metadata.error);
if(mode!=='parent')assert.deepEqual(metadata,JSON.parse(fs.readFileSync(metadataPath,'utf8')));
metadata=null;
const policy=JSON.parse(fs.readFileSync(new URL('../research/eicc-reference-response-budgets-v1.json',import.meta.url)));
const checks=[],responses=[];let maximum=engine.memory.buffer.byteLength;
for(const {request,expected} of fixture.queries){
  const actual=invoke(engine,mode==='index'?'osw_index_query':'osw_query',new TextEncoder().encode(JSON.stringify(request)),responseBudget(policy,mode==='index'?'index':'main',request));
  assert.equal(actual.ok,true,actual.error);
  if(mode==='parent')responses.push(actual);else assert.deepEqual(actual,expected,'Complete response differs from native');
  maximum=Math.max(maximum,engine.memory.buffer.byteLength);assert(maximum<=3221225472);
  checks.push({request,total:actual.total,entire_response_equal:mode!=='parent'});
}
if(mode==='index'){
  const refused=invoke(engine,'osw_index_load',new TextEncoder().encode('{"schema":"osw.almanac-index-bundle.v1","documents":{}}'),32768);
  assert.equal(refused.ok,false);assert.match(refused.error,/Changed index bundle or compiled catalog/);
}
fs.writeFileSync(outputPath,JSON.stringify({status:'PASS',mode,checks,...(mode==='parent'?{responses}:{}),initialization_metadata_equal:mode!=='parent',max_wasm_linear_memory_bytes:maximum,wasm_sha256:expectedWasmSha,payload_sha256:fixture.payload_sha256},null,2)+'\n',{flag:'wx'});
