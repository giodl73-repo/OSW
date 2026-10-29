// Scoped cloud parent capture or complete native/WASM response comparison.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {invoke} from './check_south_java_compiled_catalog_v1.mjs';
assert.equal(process.env.GITHUB_ACTIONS,'true');
assert.equal(process.env.GITHUB_REPOSITORY,'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF,'refs/heads/codex/current-measurement-gaps');
assert.equal(process.env.OSW_CHEN_INDIAN_SEC_DELIVERY_V1,'1');
const [mode,wasmPath,payloadPath,fixturePath,outputPath,expectedWasmSha]=process.argv.slice(2);
assert.equal(process.argv.slice(2).length,6);assert(['capture-main','capture-index','compare-main','compare-index'].includes(mode));
const capture=mode.startsWith('capture'),index=mode.endsWith('index');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert(fs.statSync(wasmPath).size<=64000000);assert(fs.statSync(payloadPath).size<=(index?536870912:210000000));
assert(fs.statSync(fixturePath).size<=134217728);
const fixture=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
assert(fixture.cases.length>0&&fixture.cases.length<=1000);
let binary=fs.readFileSync(wasmPath);assert.equal(sha(binary),expectedWasmSha);
const {instance}=await WebAssembly.instantiate(binary,{});binary=null;const engine=instance.exports;
let payload=fs.readFileSync(payloadPath);assert.equal(sha(payload),fixture.payload_sha256);
const metadata=invoke(engine,index?'osw_index_load':'osw_load',payload,payload.length+2097152);payload=null;
assert.equal(metadata.ok,true,metadata.error);if(!capture)assert.deepEqual(metadata,fixture.metadata,'Complete initialization metadata differs');
const checks=[],responses=[];let maximum=engine.memory.buffer.byteLength;
for(const item of fixture.cases){
  let actual;
  if(item.kind==='snapshot'){
    assert(!index&&['atlas','seasons','dashboard'].includes(item.name));engine['osw_'+item.name]();
    const length=engine.osw_result_len();assert(length>0&&length<=134217728);
    actual=JSON.parse(new TextDecoder().decode(new Uint8Array(engine.memory.buffer,engine.osw_result_ptr(),length)));
  }else{
    assert(item.kind==='query'||item.kind==='object');assert(!index||item.kind==='query');
    actual=invoke(engine,index?'osw_index_query':item.kind==='object'?'osw_object_view':'osw_query',new TextEncoder().encode(JSON.stringify(item.request)),16777216);
  }
  assert.equal(actual.ok,true,actual.error);
  if(capture)responses.push({...item,expected:actual});else assert.deepEqual(actual,item.expected,'Entire response differs: '+JSON.stringify({...item,expected:undefined}));
  const encoded=Buffer.from(JSON.stringify(actual));checks.push({kind:item.kind,name:item.name||null,request:item.request||null,total:actual.total??null,response_bytes:encoded.length,response_sha256:sha(encoded),entire_response_equal:!capture});
  maximum=Math.max(maximum,engine.memory.buffer.byteLength);assert(maximum<=3221225472);
}
let mismatchRefused=false;
if(index&&!capture){const refusal=invoke(engine,'osw_index_load',new TextEncoder().encode('{"schema":"osw.almanac-index-bundle.v1","documents":{}}'),32768);assert.equal(refusal.ok,false);assert.match(refusal.error,/Changed index bundle or compiled catalog/);mismatchRefused=true;}
fs.writeFileSync(outputPath,JSON.stringify(capture?{payload_sha256:fixture.payload_sha256,metadata,cases:responses}:{status:'PASS',mode,payload_sha256:fixture.payload_sha256,wasm_sha256:expectedWasmSha,complete_initialization_equal:true,checks,max_wasm_linear_memory_bytes:maximum,mismatched_corpus_refused:mismatchRefused},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'PASS',mode,checks:checks.length,maximum_wasm_memory:maximum}));
