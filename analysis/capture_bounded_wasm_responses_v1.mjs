// Cloud-only baseline capture: one full response per hash-bound file, no build.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {invokeJson,readResponseJson} from './current_gap_json_capture_v2.mjs';
import {writeCapturedJson} from './bounded_capture_json_v1.mjs';
assert.equal(process.env.GITHUB_ACTIONS,'true');
assert.equal(process.env.GITHUB_REPOSITORY,'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF,'refs/heads/codex/current-measurement-gaps');
assert.equal(['OSW_PACIFIC_SEC_JET_WIDTHS_DELIVERY_V1','OSW_CURRENT_CORE_DIMENSIONS_DELIVERY_V1','OSW_ATLANTIC_NSEC_REFERENCE_DELIVERY_V1'].some(key=>process.env[key]==='1'),true);
const [mode,wasmPath,payloadPath,fixturePath,outputPath,expectedWasmSha]=process.argv.slice(2);
assert.equal(process.argv.slice(2).length,6);
assert(['capture-main','capture-index'].includes(mode));
const index=mode==='capture-index',sha=raw=>crypto.createHash('sha256').update(raw).digest('hex');
assert(fs.statSync(wasmPath).size<=64000000);
const payloadBytes=fs.statSync(payloadPath).size;
assert(payloadBytes<=(index?536870912:210000000));
assert(fs.statSync(fixturePath).size<=67108864);
const fixture=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
assert(fixture.cases.length>0&&fixture.cases.length<=1000);
let binary=fs.readFileSync(wasmPath);assert.equal(sha(binary),expectedWasmSha);
const {instance}=await WebAssembly.instantiate(binary,{});binary=null;
const engine=instance.exports;
let payload=fs.readFileSync(payloadPath);assert.equal(sha(payload),fixture.payload_sha256);
const directory=path.dirname(outputPath);
let metadataJson=invokeJson(engine,index?'osw_index_load':'osw_load',payload,payloadBytes+2097152);
payload=null;
const metadata=writeCapturedJson(directory,mode+'-metadata.response.json',metadataJson,payloadBytes+2097152);
metadataJson=null;
const cases=[];let maximum=engine.memory.buffer.byteLength;
for(const [number,item] of fixture.cases.entries()){
  let raw,limit;
  if(item.kind==='snapshot'){
    assert(!index&&['atlas','seasons','dashboard'].includes(item.name));
    limit=134217728;engine['osw_'+item.name]();raw=readResponseJson(engine,limit);
  }else{
    assert(item.kind==='query'||item.kind==='object');assert(!index||item.kind==='query');
    assert.equal(typeof item.request_json,'string');limit=16777216;
    raw=invokeJson(engine,index?'osw_index_query':item.kind==='object'?'osw_object_view':'osw_query',new TextEncoder().encode(item.request_json),limit);
  }
  const response=writeCapturedJson(directory,mode+'-'+(number+1)+'.response.json',raw,limit);
  raw=null;cases.push({...item,response});
  maximum=Math.max(maximum,engine.memory.buffer.byteLength);assert(maximum<=3221225472);
}
const report={status:'PASS_COMPLETE_RESPONSE_FILES_CAPTURED',mode,payload_sha256:fixture.payload_sha256,
  wasm_sha256:expectedWasmSha,metadata,cases,max_wasm_linear_memory_bytes:maximum,
  transport:'one_complete_original_json_response_per_hash_checked_file'};
fs.writeFileSync(outputPath,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:report.status,mode,cases:cases.length,maximum_wasm_memory:maximum}));
