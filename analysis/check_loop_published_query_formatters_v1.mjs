// Exercise the actual shipped scalar formatters without a DOM, browser or WASM.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../almanac/query.js', import.meta.url), 'utf8');
const start = source.indexOf('  function label(row)');
const end = source.indexOf('  function sampleFilters(', start);
assert(start >= 0 && end > start && end - start < 16000, 'Known shipped formatter section required');
const text = source.slice(start, end);
assert.equal((text.match(/  function /g) || []).length, 3, 'Only label/value/scope functions may run');
const format = vm.runInNewContext(text + '\n;({label,value,scope})', {window: {}}, {timeout: 1000});
const raw = process.argv.includes('--stdin') ? fs.readFileSync(0, 'utf8')
  : fs.readFileSync(new URL('../research/loop-published-metrics-query-contract-v1.json', import.meta.url), 'utf8');
assert(raw.length < 131072, 'Small scalar contract only');
const contract = JSON.parse(raw);
const summaries = contract.collections.current_reported_contour_length_summaries;
const events = contract.collections.current_reported_separation_events;
assert.equal(summaries.length, 2); assert.equal(events.length, 12);
for (const row of summaries) {
  assert.equal(format.label(row), row.label);
  assert.equal(format.value(row), `${row.mean_km} km`);
  assert(format.scope(row).includes(`Temporal SD ${row.temporal_standard_deviation_km} km`));
  assert(format.scope(row).includes('not measurement error'));
}
for (const row of events) {
  assert.equal(format.label(row), row.label);
  assert.equal(format.value(row).trim(), row.date);
  assert(format.scope(row).includes('final separation'));
  assert(format.scope(row).includes('identity, clock time, timezone and footprint unknown'));
  assert(!Object.hasOwn(row, 'timeline_file'));
  assert(!Object.hasOwn(row, 'map_features'));
}
console.log(JSON.stringify({status: 'PASS', shipped_formatter_records_checked: 14,
  browser_or_dom_started: false, wasm_loaded: false}));
