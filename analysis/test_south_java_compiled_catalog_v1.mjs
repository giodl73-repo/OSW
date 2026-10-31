import test from 'node:test';
import assert from 'node:assert/strict';
import {requireCloud, invoke} from './check_south_java_compiled_catalog_v1.mjs';

test('local and wrong-branch invocation refuses before opening payloads', () => {
  assert.throws(() => requireCloud({}));
  assert.throws(() => requireCloud({GITHUB_ACTIONS: 'true', GITHUB_REPOSITORY: 'giodl73-repo/OSW',
    GITHUB_REF: 'refs/heads/main', OSW_SOUTH_JAVA_COMPILED_CATALOG: '1'}));
});

test('ABI output budget refuses before reading memory and releases its input', () => {
  let released = false;
  const engine = {memory: new WebAssembly.Memory({initial: 1}), osw_alloc: () => 4,
    osw_index_load: () => {}, osw_result_len: () => 101,
    osw_result_ptr: () => {throw Error('Must not read oversized result');},
    osw_dealloc: () => {released = true;}};
  assert.throws(() => invoke(engine, 'osw_index_load', new Uint8Array([1]), 100), /101 exceeds 100/);
  assert.equal(released, true);
});
