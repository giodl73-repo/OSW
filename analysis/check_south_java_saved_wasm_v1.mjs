// Cloud only: exercise the installed engine, without compiling or opening a browser.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';

const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export function requireCloud(env) {
  assert.equal(env.GITHUB_ACTIONS, 'true');
  assert.equal(env.GITHUB_REPOSITORY, 'giodl73-repo/OSW');
  assert.equal(env.GITHUB_REF, 'refs/heads/codex/current-measurement-gaps');
  assert.equal(env.OSW_SOUTH_JAVA_SAVED_WASM, '1');
}

export function invoke(engine, name, bytes) {
  const ptr = engine.osw_alloc(bytes.length);
  try {
    new Uint8Array(engine.memory.buffer, ptr, bytes.length).set(bytes);
    engine[name](ptr, bytes.length);
    const length = engine.osw_result_len();
    assert.ok(length > 0 && length <= 131072, 'Unexpected ABI result size');
    return JSON.parse(new TextDecoder().decode(
      new Uint8Array(engine.memory.buffer, engine.osw_result_ptr(), length)));
  } finally {
    engine.osw_dealloc(ptr, bytes.length);
  }
}

export async function main(env = process.env, argv = process.argv.slice(2)) {
  requireCloud(env); // Before opening any data or binary file.
  assert.equal(argv.length, 5);
  const [candidatePath, wasmPath, fixturesPath, receiptPath, expectedWasmSha] = argv;
  assert.ok(fs.statSync(candidatePath).size <= 210000000);
  assert.ok(fs.statSync(wasmPath).size <= 64000000);
  assert.ok(fs.statSync(fixturesPath).size <= 1572864);
  const fixtures = JSON.parse(fs.readFileSync(fixturesPath, 'utf8'));
  assert.equal(fixtures.queries.length, 11);
  let binary = fs.readFileSync(wasmPath);
  const wasmSha = sha(binary);
  assert.equal(wasmSha, expectedWasmSha);
  const {instance} = await WebAssembly.instantiate(binary, {});
  binary = null;
  const engine = instance.exports;
  let candidate = fs.readFileSync(candidatePath);
  assert.equal(sha(candidate), fixtures.candidate_sha256);
  const metadata = invoke(engine, 'osw_load', candidate);
  assert.equal(metadata.ok, true, JSON.stringify(metadata));
  candidate = null;
  let maxMemory = engine.memory.buffer.byteLength;
  const checks = [];
  for (const {query, expected} of fixtures.queries) {
    const actual = invoke(engine, 'osw_query', new TextEncoder().encode(JSON.stringify(query)));
    assert.deepEqual(actual, expected, `Native/WASM mismatch: ${JSON.stringify(query)}`);
    maxMemory = Math.max(maxMemory, engine.memory.buffer.byteLength);
    assert.ok(maxMemory <= 3221225472, 'WASM memory budget exceeded');
    checks.push({collection: query.collection, total: actual.total,
      row_ids: actual.rows.map(row => row.id), entire_response_equal: true});
  }
  const receipt = {schema: 'osw.south-java-saved-wasm-result.v1', status: 'PASS',
    source_commit: env.GITHUB_SHA, run_id: env.GITHUB_RUN_ID,
    run_attempt: env.GITHUB_RUN_ATTEMPT, candidate_sha256: fixtures.candidate_sha256,
    wasm_sha256: wasmSha, max_wasm_linear_memory_bytes: maxMemory,
    node_version: process.version,
    native_wasm_checks: checks, wasm_rebuilt: false, browser_verified: false,
    installed_assets_modified: false, new_physical_dimensions_admitted: 0};
  fs.writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + '\n', {flag: 'wx'});
  console.log(JSON.stringify({status: 'PASS', checks: checks.length, maxMemory}));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(error => { console.error(String(error).slice(0, 1500)); process.exitCode = 1; });
}
