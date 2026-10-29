import assert from 'node:assert/strict';
import {captureJson, invokeJson, readResponseJson, assertSameJsonBytes}
  from './current_gap_json_capture_v2.mjs';

const raw = '{"safe":1000.0,"float":1.8446744073709552e19,"integer":9007199254740993,"null":null,"bool":true}';
assert.notEqual(JSON.stringify(JSON.parse(raw)), raw);
assert.equal(JSON.parse(JSON.stringify(captureJson(raw))).raw_response_json, raw);
assertSameJsonBytes(raw, JSON.parse(JSON.stringify(captureJson(raw))).raw_response_json);
for (const changed of [raw.replace('9007199254740993','9007199254740992'),
  raw.replace('1000.0','1000'), raw.replace('null','0'), raw.replace('true','1')]) {
  assert.throws(() => assertSameJsonBytes(raw, changed));
}
assert.throws(() => captureJson('{broken'));
const memory = new WebAssembly.Memory({initial: 1});
let freed = 0;
const bytes = new TextEncoder().encode(raw);
const engine = {memory, osw_alloc: () => 0,
  osw_dealloc: () => freed++,
  osw_result_ptr: () => 128, osw_result_len: () => bytes.length,
  query: () => new Uint8Array(memory.buffer,128,bytes.length).set(bytes)};
assert.equal(invokeJson(engine,'query',new TextEncoder().encode('{}'),4096),raw);
assert.equal(freed,1);
assert.throws(() => readResponseJson(engine,1));
engine.query = () => { throw new Error('engine failure'); };
assert.throws(() => invokeJson(engine,'query',new Uint8Array(0),4096),/engine failure/);
assert.equal(freed,2);
new Uint8Array(memory.buffer,128,2).set([0xc3,0x28]);
engine.osw_result_len = () => 2;
assert.throws(() => readResponseJson(engine,4096));
console.log('PASS: exact numeric tokens, null/bool distinctions, ABI capture, limits, cleanup and UTF-8');
