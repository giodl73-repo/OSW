// Sequential cloud-only native/WASM comparisons for the new scalar collections.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {invoke} from './check_south_java_compiled_catalog_v1.mjs';

assert.equal(process.env.GITHUB_ACTIONS, 'true');
assert.equal(process.env.GITHUB_REPOSITORY, 'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF, 'refs/heads/codex/current-measurement-gaps');
assert.equal(process.env.OSW_LOOP_PUBLISHED_METRICS_DELIVERY, '1');
const [mode, wasmPath, payloadPath, fixturePath, metadataPath, outputPath, expectedWasmSha] = process.argv.slice(2);
assert(['main', 'index'].includes(mode));
assert.equal(process.argv.slice(2).length, 7);
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
assert(fs.statSync(wasmPath).size <= 64000000);
const payloadBytes = fs.statSync(payloadPath).size;
assert(payloadBytes > 0 && payloadBytes <= (mode === 'main' ? 210000000 : 536870912));
assert(fs.statSync(metadataPath).size <= payloadBytes + 2097152);
assert(fs.statSync(fixturePath).size <= 6291456);
const fixtures = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
assert.equal(fixtures.queries.length, mode === 'main' ? 11 : 19);
let binary = fs.readFileSync(wasmPath); assert.equal(sha(binary), expectedWasmSha);
const {instance} = await WebAssembly.instantiate(binary, {}); binary = null;
const engine = instance.exports;
let payload = fs.readFileSync(payloadPath); assert.equal(sha(payload), fixtures.payload_sha256);
let metadata = invoke(engine, mode === 'main' ? 'osw_load' : 'osw_index_load', payload, payloadBytes + 2097152);
assert.equal(metadata.ok, true, metadata.error); payload = null;
assert.deepEqual(metadata, JSON.parse(fs.readFileSync(metadataPath, 'utf8'))); metadata = null;
let maxMemory = engine.memory.buffer.byteLength;
const checks = [];
for (const {request, expected} of fixtures.queries) {
  const actual = invoke(engine, mode === 'main' ? 'osw_query' : 'osw_index_query',
    new TextEncoder().encode(JSON.stringify(request)), mode === 'main' ? 131072 : 2097152);
  assert.deepEqual(actual, expected, 'Complete query response differs from native');
  maxMemory = Math.max(maxMemory, engine.memory.buffer.byteLength); assert(maxMemory <= 3221225472);
  checks.push({collection: request.collection ?? null, document: request.document ?? null,
    pointer: request.pointer ?? null, total: actual.total, entire_response_equal: true});
}
if (mode === 'index') {
  const wrong = new TextEncoder().encode('{"schema":"osw.almanac-index-bundle.v1","documents":{}}');
  const refused = invoke(engine, 'osw_index_load', wrong, 32768);
  assert.equal(refused.ok, false); assert.match(refused.error, /Changed index bundle or compiled catalog/);
}
fs.writeFileSync(outputPath, JSON.stringify({status: 'PASS', mode, checks,
  initialization_metadata_equal: true, max_wasm_linear_memory_bytes: maxMemory,
  mismatched_corpus_refused: mode === 'index', wasm_sha256: expectedWasmSha,
  payload_sha256: fixtures.payload_sha256}, null, 2) + '\n', {flag: 'wx'});
