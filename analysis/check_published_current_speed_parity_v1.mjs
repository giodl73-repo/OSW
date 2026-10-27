import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {invoke} from './check_south_java_compiled_catalog_v1.mjs';
assert.equal(process.env.GITHUB_ACTIONS,'true');
assert.equal(process.env.GITHUB_REPOSITORY,'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF,'refs/heads/codex/current-measurement-gaps');
assert.equal(process.env.OSW_SPEED_VERIFICATION_V1,'1');
const [wasmPath,payloadPath,fixturePath,metadataPath,outputPath,wasmSha]=process.argv.slice(2);
assert.equal(process.argv.slice(2).length,6);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert(fs.statSync(wasmPath).size<=64000000);
assert(fs.statSync(payloadPath).size<=210000000);
assert(fs.statSync(fixturePath).size<=16777216);
const fixtures=JSON.parse(fs.readFileSync(fixturePath));assert.equal(fixtures.queries.length,7);
let binary=fs.readFileSync(wasmPath);assert.equal(sha(binary),wasmSha);
const {instance}=await WebAssembly.instantiate(binary,{});binary=null;
let payload=fs.readFileSync(payloadPath);assert.equal(sha(payload),fixtures.payload_sha256);
const engine=instance.exports;
let metadata=invoke(engine,'osw_load',payload,212097152);payload=null;
assert.equal(metadata.ok,true,metadata.error);
assert.deepEqual(metadata,JSON.parse(fs.readFileSync(metadataPath)));metadata=null;
let maximum=engine.memory.buffer.byteLength;
for(const {request,expected} of fixtures.queries){
  const actual=invoke(engine,'osw_query',new TextEncoder().encode(JSON.stringify(request)),1048576);
  assert.deepEqual(actual,expected,'Entire query response differs');
  maximum=Math.max(maximum,engine.memory.buffer.byteLength);assert(maximum<=3221225472);
}
fs.writeFileSync(outputPath,JSON.stringify({status:'PASS',query_cases:7,entire_responses_equal:true,initialization_equal:true,max_wasm_memory_bytes:maximum,wasm_sha256:wasmSha},null,2)+'\n',{flag:'wx'});
