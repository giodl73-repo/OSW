// Run actual shipped label/value/scope functions; no DOM, browser or WASM.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../almanac/query.js', import.meta.url), 'utf8');
const start = source.indexOf('  function label(row)');
const end = source.indexOf('  function sampleFilters(', start);
assert(start >= 0 && end > start && end - start < 16000);
const text = source.slice(start, end);
assert.equal((text.match(/  function /g) || []).length, 3);
const format = vm.runInNewContext(text + '\n;({label,value,scope})', {window: {}}, {timeout: 1000});
const raw = fs.readFileSync(new URL('../research/eicc-reference-query-contract-v1.json', import.meta.url), 'utf8');
assert(raw.length < 262144, 'Source contract only; never open a real packet');
const c = JSON.parse(raw).collections;
assert.equal(c.reference_routes.length, 2);
assert.equal(c.current_sampling_reference_points.length, 7);
assert.equal(c.current_spectral_cross_shore_scales.length, 6);
for (const row of c.reference_routes) {
  assert.equal(format.label(row), row.label);
  assert.equal(format.value(row), `≈ ${row.approximate_reference_path_km} km · reference route`);
  assert(format.scope(row).includes('not physical uncertainty'));
  assert(format.scope(row).includes('no whole-current EICC length'));
}
for (const row of c.current_sampling_reference_points) {
  assert.equal(format.label(row), row.label);
  assert.equal(format.value(row).trim(), row.value);
  assert(format.scope(row).includes('bathymetry is not current depth'));
}
for (const row of c.current_spectral_cross_shore_scales) {
  assert.equal(format.value(row), `${row.reported_scale_km} km`);
  assert(format.scope(row).includes('not paired current width'));
}
console.log(JSON.stringify({status: 'PASS', shipped_formatter_records_checked: 15,
  dom_or_browser_started: false, wasm_loaded: false}));
