// No packet, engine or original observations are loaded by these checks.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {responseBudget} from './eicc_reference_response_budget_v1.mjs';

const policy = JSON.parse(fs.readFileSync(new URL('../research/eicc-reference-response-budgets-v1.json', import.meta.url)));
assert.equal(responseBudget(policy, 'main', {collection: 'widths', limit: 1}), 2097152);
assert(133699 <= responseBudget(policy, 'main', {collection: 'widths', limit: 1}));
for (const collection of ['objects', 'reference_routes']) {
  assert.equal(responseBudget(policy, 'main', {collection}), 2097152);
}
for (const collection of ['current_sampling_reference_points', 'current_spectral_cross_shore_scales', 'route_decisions']) {
  assert.equal(responseBudget(policy, 'main', {collection}), 131072);
}
assert.equal(responseBudget(policy, 'index', {document: 'source.json'}), 2097152);
assert.throws(() => responseBudget({...policy, scene_or_source_response_bytes: Infinity}, 'main', {collection: 'widths'}));
assert.throws(() => responseBudget(policy, 'unknown', {}));
process.stdout.write('Shared response budget checks passed; complete width chart fits, scalar and source bounds retained.\n');
