// Pure policy shared by the full WASM verifier and its small source checks.
import assert from 'node:assert/strict';

export function responseBudget(policy, mode, request) {
  assert.equal(policy.schema, 'osw.eicc-reference-response-budgets.v1');
  assert.equal(policy.scalar_response_bytes, 131072);
  assert.equal(policy.scene_or_source_response_bytes, 2097152);
  assert.deepEqual(policy.main_collections_with_scene_budget, ['objects', 'reference_routes', 'widths']);
  assert(['main', 'index'].includes(mode));
  return mode === 'index' || policy.main_collections_with_scene_budget.includes(request.collection)
    ? policy.scene_or_source_response_bytes : policy.scalar_response_bytes;
}
