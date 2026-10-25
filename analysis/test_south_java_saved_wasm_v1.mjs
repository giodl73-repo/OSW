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
