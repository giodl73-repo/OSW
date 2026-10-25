import test from 'node:test';
import assert from 'node:assert/strict';
import {requireCloud, invoke} from './check_south_java_saved_wasm_v1.mjs';

test('refuse local execution before file access', () => {
  assert.throws(() => requireCloud({}));
  assert.throws(() => requireCloud({GITHUB_ACTIONS: 'true',
    GITHUB_REPOSITORY: 'giodl73-repo/OSW', GITHUB_REF: 'refs/heads/main',
    OSW_SOUTH_JAVA_SAVED_WASM: '1'}));
});

test('ABI buffers are released when native JSON is invalid', () => {
  const memory = new WebAssembly.Memory({initial: 1});
  let released = false;
  const engine = {memory, osw_alloc: () => 4, osw_query: () => {},
    osw_result_ptr: () => 100, osw_result_len: () => 2,
    osw_dealloc: () => {released = true;}};
  assert.throws(() => invoke(engine, 'osw_query', new Uint8Array([1])));
  assert.equal(released, true);
});

test('initialization metadata has a separate bound from query responses', () => {
  const memory = new WebAssembly.Memory({initial: 4});
  const bytes = new TextEncoder().encode(JSON.stringify({ok: true, manifest: 'a'.repeat(140000)}));
  new Uint8Array(memory.buffer, 1000, bytes.length).set(bytes);
  let released = 0;
  const engine = {memory, osw_alloc: () => 4, osw_load: () => {}, osw_query: () => {},
    osw_result_ptr: () => 1000, osw_result_len: () => bytes.length,
    osw_dealloc: () => {released++;}};
  assert.equal(invoke(engine, 'osw_load', new Uint8Array([1])).ok, true);
  assert.throws(() => invoke(engine, 'osw_query', new Uint8Array([1])), /osw_query.*140025 bytes/);
  assert.equal(released, 2);
});

test('oversized initialization metadata is refused before reading the result', () => {
  let released = false;
  const engine = {memory: new WebAssembly.Memory({initial: 1}), osw_alloc: () => 4,
    osw_load: () => {}, osw_result_len: () => 4194305,
    osw_result_ptr: () => {throw Error('Must refuse before reading result');},
    osw_dealloc: () => {released = true;}};
  assert.throws(() => invoke(engine, 'osw_load', new Uint8Array([1])), /osw_load.*4194305 bytes/);
  assert.equal(released, true);
});
