// Complete native/WASM response equality with explicit finite payload/scene budgets.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {invoke} from './check_south_java_compiled_catalog_v1.mjs';
import {responseBudget} from './eicc_reference_response_budget_v1.mjs';

assert.equal(process.env.GITHUB_ACTIONS, 'true');
assert.equal(process.env.GITHUB_REPOSITORY, 'giodl73-repo/OSW');
assert.equal(process.env.GITHUB_REF, 'refs/heads/codex/current-measurement-gaps');
assert.equal(process.env.OSW_SPEED_DELIVERY_V1, '1');
const [mode, wasmPath, payloadPath, fixturePath, metadataPath, outputPath, expectedWasmSha] = process.argv.slice(2);
assert.equal(process.argv.slice(2).length, 7);
assert(['main', 'index'].includes(mode));
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
assert(fs.statSync(wasmPath).size <= 64000000);
const size = fs.statSync(payloadPath).size;
assert(size > 0 && size <= (mode === 'main' ? 210000000 : 536870912));
assert(fs.statSync(metadataPath).size <= size + 2097152);
assert(fs.statSync(fixturePath).size <= 16777216);
const fixture = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
assert.equal(fixture.queries.length, mode === 'main' ? 33 : 13);
let binary = fs.readFileSync(wasmPath); assert.equal(sha(binary), expectedWasmSha);
const {instance} = await WebAssembly.instantiate(binary, {}); binary = null;
const engine = instance.exports;
let payload = fs.readFileSync(payloadPath); assert.equal(sha(payload), fixture.payload_sha256);
let metadata = invoke(engine, mode === 'main' ? 'osw_load' : 'osw_index_load', payload, size + 2097152);
payload = null; assert.equal(metadata.ok, true, metadata.error);
assert.deepEqual(metadata, JSON.parse(fs.readFileSync(metadataPath, 'utf8'))); metadata = null;
const policy = JSON.parse(fs.readFileSync(new URL('../research/eicc-reference-response-budgets-v1.json', import.meta.url)));
let maximum = engine.memory.buffer.byteLength;
const checks = [];
for (const {request, expected} of fixture.queries) {
  const limit = responseBudget(policy, mode, request);
  const actual = invoke(engine, mode === 'main' ? 'osw_query' : 'osw_index_query',
    new TextEncoder().encode(JSON.stringify(request)), limit);
  assert.deepEqual(actual, expected, 'Complete response differs from native');
  maximum = Math.max(maximum, engine.memory.buffer.byteLength); assert(maximum <= 3221225472);
  checks.push({collection: request.collection ?? null, document: request.document ?? null,
    total: actual.total, entire_response_equal: true, response_limit_bytes: limit});
}
if (mode === 'index') {
  const refused = invoke(engine, 'osw_index_load',
    new TextEncoder().encode('{"schema":"osw.almanac-index-bundle.v1","documents":{}}'), 32768);
  assert.equal(refused.ok, false); assert.match(refused.error, /Changed index bundle or compiled catalog/);
}
fs.writeFileSync(outputPath, JSON.stringify({status: 'PASS', mode, checks,
  initialization_metadata_equal: true, max_wasm_linear_memory_bytes: maximum,
  mismatched_corpus_refused: mode === 'index', wasm_sha256: expectedWasmSha,
  payload_sha256: fixture.payload_sha256}, null, 2) + '\n', {flag: 'wx'});
