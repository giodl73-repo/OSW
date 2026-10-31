// Cloud-only lossless JSON capture and complete native/WASM comparison.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {invokeJson, readResponseJson, captureJson, assertSameJsonBytes}
  from './current_gap_json_capture_v2.mjs';
assert.equal(process.env.GITHUB_ACTIONS,'true');
assert.equal(process.env.GITHUB_REPOSITORY,'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF,'refs/heads/codex/current-measurement-gaps');
assert.equal(process.env.OSW_CHEN_INDIAN_SEC_DELIVERY_V2,'1');
const [mode,wasmPath,payloadPath,fixturePath,outputPath,expectedWasmSha]=process.argv.slice(2);
assert.equal(process.argv.slice(2).length,6);
assert(['capture-main','capture-index','compare-main','compare-index'].includes(mode));
const capture=mode.startsWith('capture'),index=mode.endsWith('index');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert(fs.statSync(wasmPath).size<=64000000);
assert(fs.statSync(payloadPath).size<=(index?536870912:210000000));
assert(fs.statSync(fixturePath).size<=134217728);
const fixture=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
assert(fixture.cases.length>0&&fixture.cases.length<=1000);
let binary=fs.readFileSync(wasmPath);assert.equal(sha(binary),expectedWasmSha);
const {instance}=await WebAssembly.instantiate(binary,{});binary=null;
const engine=instance.exports;
let payload=fs.readFileSync(payloadPath);assert.equal(sha(payload),fixture.payload_sha256);
const metadataJson=invokeJson(engine,index?'osw_index_load':'osw_load',payload,payload.length+2097152);
payload=null;
const metadata=JSON.parse(metadataJson);assert.equal(metadata.ok,true,metadata.error);
if(!capture)assertSameJsonBytes(metadataJson,fixture.metadata_json);
const checks=[],responses=[];let maximum=engine.memory.buffer.byteLength;
for(const item of fixture.cases){
  let raw;
  if(item.kind==='snapshot'){
    assert(!index&&['atlas','seasons','dashboard'].includes(item.name));
    engine['osw_'+item.name]();raw=readResponseJson(engine,134217728);
  }else{
    assert(item.kind==='query'||item.kind==='object');assert(!index||item.kind==='query');
    assert.equal(typeof item.request_json,'string');
    raw=invokeJson(engine,index?'osw_index_query':item.kind==='object'?'osw_object_view':'osw_query',
      new TextEncoder().encode(item.request_json),16777216);
  }
  const actual=JSON.parse(raw);assert.equal(actual.ok,true,actual.error);
  if(capture)responses.push({...item,...captureJson(raw)});
  else assertSameJsonBytes(raw,item.raw_response_json);
  const bytes=Buffer.from(raw);
  checks.push({kind:item.kind,name:item.name||null,request_json:item.request_json||null,
    total:actual.total??null,response_bytes:bytes.length,response_sha256:sha(bytes),
    entire_response_equal:!capture,comparison:'exact original JSON bytes'});
  maximum=Math.max(maximum,engine.memory.buffer.byteLength);assert(maximum<=3221225472);
}
let mismatchRefused=false;
if(index&&!capture){
  const raw=invokeJson(engine,'osw_index_load',new TextEncoder().encode('{"schema":"osw.almanac-index-bundle.v1","documents":{}}'),32768);
  const refusal=JSON.parse(raw);assert.equal(refusal.ok,false);
  assert.match(refusal.error,/Changed index bundle or compiled catalog/);mismatchRefused=true;
}
fs.writeFileSync(outputPath,JSON.stringify(capture?
  {payload_sha256:fixture.payload_sha256,metadata_json:metadataJson,cases:responses}:
  {status:'PASS',mode,payload_sha256:fixture.payload_sha256,wasm_sha256:expectedWasmSha,
    complete_initialization_equal:true,checks,max_wasm_linear_memory_bytes:maximum,
    mismatched_corpus_refused:mismatchRefused},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'PASS',mode,checks:checks.length,maximum_wasm_memory:maximum}));
