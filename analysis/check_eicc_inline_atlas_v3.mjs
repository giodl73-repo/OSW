// Small checks of the shipped loader/label expressions. No DOM, browser or WASM.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const source = fs.readFileSync('almanac/reference-routes.js', 'utf8');
const loaderLine = source.split('\n').find(line => line.includes('const [reports, seasonalRoutes]'));
assert(loaderLine);
const begin = loaderLine.indexOf('Promise.all(catalog.candidates.map(');
const end = loaderLine.indexOf(', seasonalRoutesReady');
assert(begin >= 0 && end > begin);
const expression = loaderLine.slice(begin, end);
const first = {id: 'eicc-prose', rendering_role: 'derived_inline_source_reference_card_not_additional_observation'};
const second = {id: 'eicc-caption', rendering_role: first.rendering_role};
const requested = [];
const catalog = {candidates: [
  {candidate_file: 'research/eicc-source.json', report_inline: first},
  {candidate_file: 'research/eicc-source.json', report_inline: second},
  {candidate_file: 'research/legacy.json'},
]};
const reports = await vm.runInNewContext(expression, {catalog, load: async path => {
  requested.push(path); return {id: 'legacy'};
}});
assert.equal(reports.length, 3);
assert.equal(reports[0], first); assert.equal(reports[1], second);
assert.equal(reports[2].id, 'legacy');
assert.deepEqual(requested, ['../research/legacy.json']);

const atlas = fs.readFileSync('almanac/reference-route-atlas.js', 'utf8');
const line = atlas.split('\n').find(line => line.includes('editorial bend-probe span'));
assert(line);
const template = line.slice(line.indexOf('`'), line.lastIndexOf('`') + 1);
const row = {approximate_reference_path_km: 590, scenario_range_km: [590, 600], comparison_group: 'osw_source_anchor_connections'};
assert.match(vm.runInNewContext(template, {row}), /590–600 km editorial bend-probe span/);
row.comparison_group = 'osw_studied_reach_routes';
assert.match(vm.runInNewContext(template, {row}), /590–600 km scenario envelope/);
console.log(JSON.stringify({inline_reports_selected: 2, legacy_file_loads_preserved: 1,
  actual_loader_and_label_expressions_checked: true, browser_verified: false}));
