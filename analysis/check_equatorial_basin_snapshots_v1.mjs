// Cloud-only parent capture or complete candidate native/WASM snapshot parity.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {invoke} from './check_south_java_compiled_catalog_v1.mjs';

assert.equal(process.env.GITHUB_ACTIONS, 'true');
assert.equal(process.env.GITHUB_REPOSITORY, 'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF, 'refs/heads/codex/current-measurement-gaps');
assert.equal(process.env.OSW_EQUATORIAL_BASIN_IDENTITY_DELIVERY_V1, '1');
const [mode, wasmPath, payloadPath, directory, expectedWasmSha, expectedPayloadSha] = process.argv.slice(2);
assert.equal(process.argv.slice(2).length, 6); assert(['parent', 'candidate'].includes(mode));
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
assert(fs.statSync(wasmPath).size <= 64000000);
assert(fs.statSync(payloadPath).size <= 210000000);
let binary = fs.readFileSync(wasmPath); assert.equal(sha(binary), expectedWasmSha);
const {instance} = await WebAssembly.instantiate(binary, {}); binary = null;
const engine = instance.exports;
let payload = fs.readFileSync(payloadPath); assert.equal(sha(payload), expectedPayloadSha);
let metadata = invoke(engine, 'osw_load', payload, 212097152); payload = null;
assert.equal(metadata.ok, true, metadata.error);
if (mode === 'candidate') assert.deepEqual(metadata, JSON.parse(fs.readFileSync(directory + '/main-metadata.json', 'utf8')));
metadata = null;
const limit = 134217728, checks = [];
let maximum = engine.memory.buffer.byteLength;
for (const name of ['atlas', 'seasons', 'dashboard']) {
  engine['osw_' + name]();
  const length = engine.osw_result_len(); assert(length > 0 && length <= limit);
  const bytes = new Uint8Array(engine.memory.buffer, engine.osw_result_ptr(), length);
  const actual = JSON.parse(new TextDecoder().decode(bytes));
  assert.equal(actual.ok, true, actual.error);
  if (mode === 'parent') fs.writeFileSync(directory + '/parent-' + name + '.json', Buffer.from(bytes), {flag: 'wx'});
  else {
    const path = directory + '/' + name + '-native.json'; assert(fs.statSync(path).size <= limit);
    assert.deepEqual(actual, JSON.parse(fs.readFileSync(path, 'utf8')), 'Complete ' + name + ' snapshot differs from native');
  }
  maximum = Math.max(maximum, engine.memory.buffer.byteLength); assert(maximum <= 3221225472);
  checks.push({view: name, response_bytes: length, response_sha256: sha(bytes),
    response_limit_bytes: limit, entire_response_equal: mode === 'candidate'});
}
fs.writeFileSync(directory + '/' + (mode === 'parent' ? 'parent-snapshots' : 'snapshots-parity') + '.json',
  JSON.stringify({status: 'PASS', mode, wasm_sha256: expectedWasmSha, payload_sha256: expectedPayloadSha,
    initialization_metadata_equal: mode === 'candidate', checks, max_wasm_linear_memory_bytes: maximum}, null, 2) + '\n', {flag: 'wx'});
