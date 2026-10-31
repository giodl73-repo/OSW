// Small DOM fixture only; no browser, packet or WASM is loaded.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.style = {}; this.attributes = {}; }
  append(child) { this.children.push(child); }
  setAttribute(key, value) { this.attributes[key] = value; }
}
const context = {window: {}, document: {createElement: tag => new Element(tag)}};
vm.runInNewContext(fs.readFileSync('almanac/current-source-evidence-ui.js', 'utf8'), context);
const contract = JSON.parse(fs.readFileSync('research/indian-coastal-dimension-context-query-contract-v1.json'));
const original = contract.additions.current_regional_reaches[0];
const flatten = node => [node, ...node.children.flatMap(flatten)];
function render(row, id = original.entity_id) {
  const data = {current_regional_reaches: [structuredClone(row)]};
  const before = JSON.stringify(data);
  const root = new Element('main');
  context.window.renderCurrentSourceEvidence(root, data, id, () => {});
  assert.equal(JSON.stringify(data), before, 'render must not change scientific records');
  return flatten(root);
}
const nodes = render(original);
assert.equal(nodes.filter(n => n.tag === 'img').length, 1);
const image = nodes.find(n => n.tag === 'img');
assert.equal(image.src, '../figures/eacc-regional-connection-v1.svg');
assert.equal(image.loading, 'lazy');
assert.match(image.style.cssText, /width:100%.*height:auto/);
assert.match(image.alt, /not a measured current axis/);
assert.ok(fs.existsSync(image.src.replace('../', '')));
const queries = nodes.filter(n => n.tag === 'a' && n.href?.startsWith('query.html?q='));
assert.equal(queries.length, 1, 'reuse the existing exact query link');
const query = JSON.parse(decodeURIComponent(queries[0].href.split('?q=')[1]));
assert.equal(query.collection, 'current_regional_reaches');
assert.equal(query.filters[0].value, original.id);
assert.equal(query.limit, 1);
for (const change of [
  row => { row.id = 'different'; },
  row => { row.source_id = 'different'; },
  row => { row.schema = 'different'; },
  row => { row.constraint.reported_value_km = 900; },
  row => { row.constraint.relation = 'exact'; },
  row => { row.whole_current_length_admitted = true; },
  row => { row.constraint.whole_current_length_km = 1000; },
  row => { row.constraint.current_geometry = {type: 'LineString'}; },
]) {
  const row = structuredClone(original); change(row);
  assert.equal(render(row).filter(n => n.tag === 'img').length, 0, 'stale schematic must not attach to changed evidence');
}
assert.equal(render(original, 'current:unrelated').filter(n => n.tag === 'img').length, 0);
console.log('PASS EACC visual: canonical record reused, exact query preserved, eight changed-evidence guards, unrelated-owner exclusion, no data mutation');
