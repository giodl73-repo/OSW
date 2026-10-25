// Cloud-only parity checks for the matching main-store and compiled index APIs.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';

const sha = value => crypto.createHash('sha256').update(value).digest('hex');
export function requireCloud(env) {
  assert.equal(env.GITHUB_ACTIONS, 'true');
  assert.equal(env.GITHUB_REPOSITORY, 'giodl73-repo/OSW');
  assert.equal(env.GITHUB_REF, 'refs/heads/codex/current-measurement-gaps');
  assert.equal(env.OSW_SOUTH_JAVA_COMPILED_CATALOG, '1');
}

export function invoke(engine, name, bytes, limit) {
  const pointer = engine.osw_alloc(bytes.length);
  try {
    new Uint8Array(engine.memory.buffer, pointer, bytes.length).set(bytes);
    engine[name](pointer, bytes.length);
    const length = engine.osw_result_len();
    assert.ok(length > 0 && length <= limit, `${name}: result ${length} exceeds ${limit} bytes`);
    return JSON.parse(new TextDecoder().decode(
      new Uint8Array(engine.memory.buffer, engine.osw_result_ptr(), length)));
  } finally { engine.osw_dealloc(pointer, bytes.length); }
}

export async function main(env = process.env, argv = process.argv.slice(2)) {
  requireCloud(env); // Before opening any payload, metadata or binary file.
  assert.equal(argv.length, 7);
  const [mode, wasmPath, payloadPath, fixturePath, metadataPath, outputPath, expectedWasmSha] = argv;
  assert.ok(['main', 'index'].includes(mode));
  assert.ok(fs.statSync(wasmPath).size <= 64000000);
  const payloadBytes = fs.statSync(payloadPath).size;
  assert.ok(payloadBytes > 0 && payloadBytes <= (mode === 'main' ? 210000000 : 536870912));
  const metadataBudget = payloadBytes + 2097152;
  assert.ok(fs.statSync(metadataPath).size <= metadataBudget);
  assert.ok(fs.statSync(fixturePath).size <= 6291456);
  const fixtures = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
  assert.equal(fixtures.queries.length, mode === 'main' ? 11 : 3);
  let binary = fs.readFileSync(wasmPath);
  assert.equal(sha(binary), expectedWasmSha);
  const {instance} = await WebAssembly.instantiate(binary, {});
  binary = null;
  const engine = instance.exports;
  let payload = fs.readFileSync(payloadPath);
  assert.equal(sha(payload), fixtures.payload_sha256);
  let metadata = invoke(engine, mode === 'main' ? 'osw_load' : 'osw_index_load', payload, metadataBudget);
  assert.equal(metadata.ok, true, metadata.error || 'Matching-engine initialization failed');
  payload = null;
  assert.deepEqual(metadata, JSON.parse(fs.readFileSync(metadataPath, 'utf8')), `${mode} metadata differs from native`);
  metadata = null;
  let maxMemory = engine.memory.buffer.byteLength;
  assert.ok(maxMemory <= 3221225472, 'WASM memory budget exceeded at initialization');
  const checks = [];
  for (const {request, expected} of fixtures.queries) {
    const actual = invoke(engine, mode === 'main' ? 'osw_query' : 'osw_index_query',
      new TextEncoder().encode(JSON.stringify(request)), mode === 'main' ? 131072 : 2097152);
    assert.deepEqual(actual, expected, `${mode} response differs from native`);
    maxMemory = Math.max(maxMemory, engine.memory.buffer.byteLength);
    assert.ok(maxMemory <= 3221225472, 'WASM memory budget exceeded');
    checks.push({collection: request.collection ?? null, document: request.document ?? null,
      total: actual.total, entire_response_equal: true});
  }
  let mismatchRefused = null;
  if (mode === 'index') {
    const wrong = new TextEncoder().encode('{"schema":"osw.almanac-index-bundle.v1","documents":{}}');
    const refusal = invoke(engine, 'osw_index_load', wrong, 32768);
    assert.equal(refusal.ok, false);
    assert.match(refusal.error, /Changed index bundle or compiled catalog/);
    mismatchRefused = true;
  }
  const result = {schema: 'osw.south-java-compiled-catalog-parity.v1', status: 'PASS', mode,
    source_commit: env.GITHUB_SHA, run_id: env.GITHUB_RUN_ID, run_attempt: env.GITHUB_RUN_ATTEMPT,
    wasm_sha256: expectedWasmSha, payload_sha256: fixtures.payload_sha256,
    payload_bytes: payloadBytes, initialization_metadata_equal: true, checks,
    max_wasm_linear_memory_bytes: maxMemory, mismatched_corpus_refused: mismatchRefused,
    wasm_rebuilt: true, scientific_source_processing: false,
    browser_verified: false, working_branch_installed: false, node_version: process.version};
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + '\n', {flag: 'wx'});
  console.log(JSON.stringify({status: 'PASS', mode, checks: checks.length, mismatchRefused}));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(error => { console.error(String(error).slice(0, 1500)); process.exitCode = 1; });
}
