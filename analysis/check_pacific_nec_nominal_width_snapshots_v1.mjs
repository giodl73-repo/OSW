// Cloud-only parent capture or complete candidate native/WASM snapshot parity.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {invoke} from './check_south_java_compiled_catalog_v1.mjs';

assert.equal(process.env.GITHUB_ACTIONS, 'true');
assert.equal(process.env.GITHUB_REPOSITORY, 'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF, 'refs/heads/codex/current-measurement-gaps');
assert.equal(process.env.OSW_PACIFIC_NEC_NOMINAL_WIDTH_DELIVERY_V1, '1');
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
// Capture complete installed object APIs as well as all candidate responses.
// This allows the Python preservation model to compare every historical field.
const owners = [
  'current:atlantic-north-equatorial', 'current:pacific-north-equatorial',
  'current:atlantic-south-equatorial', 'current:pacific-south-equatorial',
  'current:indian-south-equatorial', 'current:north-equatorial', 'current:south-equatorial'
];
const saved = mode === 'candidate'
  ? JSON.parse(fs.readFileSync(directory + '/objects-native.json', 'utf8')) : null;
if (saved) assert.deepEqual(Object.keys(saved).sort(), [...owners].sort(), 'Exact seven object IDs required');
const objects = {}, objectChecks = [];
for (const id of owners) {
  const actual = invoke(engine, 'osw_object_view', new TextEncoder().encode(JSON.stringify({id})), 2097152);
  assert.equal(actual.ok, true, actual.error);
  assert.equal(actual.bundle_sha256, expectedPayloadSha);
  if (saved) assert.deepEqual(actual, saved[id], 'Complete object API differs: ' + id);
  else objects[id] = actual;
  maximum = Math.max(maximum, engine.memory.buffer.byteLength); assert(maximum <= 3221225472);
  const encoded = Buffer.from(JSON.stringify(actual));
  objectChecks.push({id, response_bytes: encoded.length, response_sha256: sha(encoded),
    entire_response_equal: mode === 'candidate', complete_parent_response_saved: mode === 'parent'});
}
if (mode === 'parent') fs.writeFileSync(directory + '/parent-objects.json', JSON.stringify(objects), {flag: 'wx'});
fs.writeFileSync(directory + '/' + (mode === 'parent' ? 'parent-object-capture' : 'object-parity') + '.json',
  JSON.stringify({status: 'PASS', mode, checks: objectChecks, wasm_sha256: expectedWasmSha,
    payload_sha256: expectedPayloadSha, max_wasm_linear_memory_bytes: maximum}, null, 2) + '\n', {flag: 'wx'});
fs.writeFileSync(directory + '/' + (mode === 'parent' ? 'parent-snapshots' : 'snapshots-parity') + '.json',
  JSON.stringify({status: 'PASS', mode, wasm_sha256: expectedWasmSha, payload_sha256: expectedPayloadSha,
    initialization_metadata_equal: mode === 'candidate', checks, max_wasm_linear_memory_bytes: maximum}, null, 2) + '\n', {flag: 'wx'});
