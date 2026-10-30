// Cloud-only complete native/WASM comparison with sequential expected-file reads.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {invokeJson,readResponseJson,assertSameJsonBytes} from './current_gap_json_capture_v2.mjs';
import {readExpectedJson} from './bounded_expected_json_v1.mjs';
assert.equal(process.env.GITHUB_ACTIONS,'true');
assert.equal(process.env.GITHUB_REPOSITORY,'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF,'refs/heads/codex/current-measurement-gaps');
assert.equal(['OSW_DIMOUNE_WIDTH_DELIVERY_V1','OSW_ATLANTIC_NEC_BANDS_DELIVERY_V1'].some(key=>process.env[key]==='1'),true);
const [mode,wasmPath,payloadPath,fixturePath,outputPath,expectedWasmSha]=process.argv.slice(2);
assert.equal(process.argv.slice(2).length,6);
assert(['compare-main','compare-index'].includes(mode));
const index=mode==='compare-index',sha=raw=>crypto.createHash('sha256').update(raw).digest('hex');
const payloadBytes=fs.statSync(payloadPath).size;
assert(fs.statSync(wasmPath).size<=64000000);
assert(payloadBytes<=(index?536870912:210000000));
assert(fs.statSync(fixturePath).size<=67108864);
const fixture=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
assert(fixture.cases.length>0&&fixture.cases.length<=1000);
assert.equal(fixture.schema,'osw.bounded-expected-response-fixture.v1');
let binary=fs.readFileSync(wasmPath);assert.equal(sha(binary),expectedWasmSha);
const {instance}=await WebAssembly.instantiate(binary,{});binary=null;
const engine=instance.exports;
let payload=fs.readFileSync(payloadPath);assert.equal(sha(payload),fixture.payload_sha256);
let metadataJson=invokeJson(engine,index?'osw_index_load':'osw_load',payload,payload.length+2097152);
payload=null;
assert.equal(JSON.parse(metadataJson).ok,true);
const directory=path.dirname(fixturePath);
assertSameJsonBytes(metadataJson,readExpectedJson(directory,fixture.expected_metadata,payloadBytes+2097152));
const metadataSha=sha(Buffer.from(metadataJson));metadataJson=null;
const checks=[];let maximum=engine.memory.buffer.byteLength;
for(const item of fixture.cases){
  let raw;
  if(item.kind==='snapshot'){
    assert(!index&&['atlas','seasons','dashboard'].includes(item.name));
    engine['osw_'+item.name]();raw=readResponseJson(engine,134217728);
  }else{
    assert(item.kind==='query'||item.kind==='object');assert(!index||item.kind==='query');
    assert.equal(typeof item.request_json,'string');
    raw=invokeJson(engine,index?'osw_index_query':item.kind==='object'?'osw_object_view':'osw_query',new TextEncoder().encode(item.request_json),16777216);
  }
  const actual=JSON.parse(raw);assert.equal(actual.ok,true,actual.error);
  assertSameJsonBytes(raw,readExpectedJson(directory,item.expected_response,item.kind==='snapshot'?134217728:16777216));
  const bytes=Buffer.from(raw);
  checks.push({kind:item.kind,name:item.name||null,request_json:item.request_json||null,total:actual.total??null,
    response_bytes:bytes.length,response_sha256:sha(bytes),entire_response_equal:true,comparison:'exact original JSON bytes'});
  maximum=Math.max(maximum,engine.memory.buffer.byteLength);assert(maximum<=3221225472);
}
let mismatchRefused=false;
if(index){
  const raw=invokeJson(engine,'osw_index_load',new TextEncoder().encode('{"schema":"osw.almanac-index-bundle.v1","documents":{}}'),32768);
  const refusal=JSON.parse(raw);assert.equal(refusal.ok,false);assert.match(refusal.error,/Changed index bundle or compiled catalog/);mismatchRefused=true;
}
fs.writeFileSync(outputPath,JSON.stringify({status:'PASS',mode,payload_sha256:fixture.payload_sha256,wasm_sha256:expectedWasmSha,
  complete_initialization_equal:true,initialization_response_sha256:metadataSha,checks,max_wasm_linear_memory_bytes:maximum,
  mismatched_corpus_refused:mismatchRefused,expected_transport:'hash_checked_one_complete_response_file_at_a_time'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'PASS',mode,checks:checks.length,maximum_wasm_memory:maximum,expected_transport:'sequential files'}));
