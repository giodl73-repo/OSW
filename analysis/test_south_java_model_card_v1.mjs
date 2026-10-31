import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const contract = JSON.parse(fs.readFileSync('research/south-java-model-layer-query-contract-v1.json'));
const rows = [...contract.collections.current_model_analysis_layers, ...contract.collections.current_model_depth_context];
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.style = {}; this.handlers = {}; }
  append(child) { this.children.push(child); }
  addEventListener(name, fn) { this.handlers[name] = fn; }
}
const context = {window: {}, document: {createElement: tag => new Element(tag)}, URL,
  location: {href: 'https://atlas.example/almanac/query.html'}};
vm.runInNewContext(fs.readFileSync('almanac/model-section-card.js', 'utf8'), context);
const card = context.window.oswModelSectionCard;
function elements(node) { return [node, ...node.children.flatMap(elements)]; }

test('five exact records retain distinct definitions, approximate cores and cap', () => {
  assert.match(card.value(rows[0]), /^Surface to 150 m.*analysis layer/);
  assert.match(card.value(rows[1]), /^150 m to 1000 m.*analysis layer/);
  assert.match(card.value(rows[2]), /^Approximately 50 m.*core depth/);
  assert.match(card.value(rows[3]), /^Mean flow > 5 cm\/s does not extend below 100 m$/);
  assert.match(card.value(rows[4]), /^Approximately 400 m.*core depth/);
});

test('unowned undercurrent stays separate and all navigation uses the related owner', () => {
  for (const row of rows.filter(row => row.entity_id === null)) {
    const parent = new Element('main');
    let selection;
    assert.equal(card.render(parent, row, (...args) => {selection = args;}), true);
    const nodes = elements(parent);
    assert.ok(nodes.some(node => node.textContent?.includes('Separate undercurrent context')));
    const owner = nodes.find(node => node.textContent === 'South Java current record');
    const query = JSON.parse(new URL(owner.href).searchParams.get('q'));
    assert.equal(query.filters[0].value, 'current:south-java');
    nodes.find(node => node.textContent === 'Publication and source details').handlers.click();
    assert.deepEqual(selection, ['sources', row.source_id]);
  }
});

test('all model cards carry the reviewed figure, source locator and physical unknowns', () => {
  for (const row of rows) {
    const parent = new Element('main');
    card.render(parent, row, () => {});
    const nodes = elements(parent);
    assert.ok(nodes.some(node => node.textContent?.includes('annual ranges and uncertainty remain unknown')));
    assert.ok(nodes.some(node => node.textContent === row.source_locator));
    const image = nodes.find(node => node.tag === 'img');
    assert.equal(image.src, 'https://atlas.example/' + row.figure_file);
    assert.match(image.alt, /not current thickness/);
    if ('depth_cap_m' in row) assert.ok(nodes.some(node => node.textContent?.includes('exact edge depth is unresolved')));
  }
});

test('existing model samples retain their values and unrelated rows are untouched', () => {
  assert.equal(card.value({record_type: 'model_section_sample', salinity: null, u_eastward: 0, v_northward: 1}), 'S Unavailable · u 0 · v 1 m/s');
  assert.equal(card.value({record_type: 'other'}), null);
  assert.equal(card.render(new Element('main'), {record_type: 'other'}, () => {}), false);
});
