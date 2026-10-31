import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const context={window:{}};
vm.runInNewContext(fs.readFileSync('almanac/reference-route-text.js','utf8'),context);
const text=context.window.OSWReferenceRouteText;
const row={approximate_reference_path_km:1500,scenario_count:3,scenario_range_km:null};
assert.match(text.summary(row),/1,500 km · range unknown/);
assert.match(text.summary(row,'atlas'),/range unknown/);
assert.match(text.seasonal(row),/range unknown/);
assert.equal(text.range(row),'Range unknown');
for(const bad of [null,[],[null,null],[0,0],[1600,1500],['1500','1600'],[NaN,1600]]) {
  assert.equal(text.hasRange({...row,scenario_range_km:bad}),false);
  assert.match(text.summary({...row,scenario_range_km:bad}),/range unknown/);
}
const old={...row,scenario_range_km:[1500,1600]};
assert.equal(text.summary(old),'≈ 1,500 km · 3 scenarios · 1,500–1,600 km scenario envelope');
assert.equal(text.summary({...old,comparison_group:'osw_source_anchor_connections'},'atlas'),'≈ 1,500 km · 1,500–1,600 km editorial bend-probe span');
assert.equal(text.summary({...old,comparison_group:'osw_offshore_coastal_reference_curves'}),'≈ 1,500 km · 3 scenarios · 1,500–1,600 km convention sensitivity');
assert.match(text.summary({approximate_reference_path_km:null,scenario_range_km:null}),/^Length unknown/);
assert.equal(text.compactFigure({figure:'figures/wicc-winter-regional-reference-route-v4-candidate.svg'},{}),'figures/wicc-winter-regional-reference-compact-v1.svg');
assert.equal(text.compactFigure({figure:'figures/atlantic-nsec-regional-reference-reaches-v1.svg'},{}),'figures/atlantic-nsec-regional-reference-reaches-compact-v1.svg');
for(const name of ['reference-routes','reference-route-atlas','seasons']) {
  const source=fs.readFileSync(`almanac/${name}.js`,'utf8');
  assert.ok(source.includes('window.OSWReferenceRouteText.'));
  assert.ok(!source.includes('scenario_range_km.map'));
}
for(const page of ['reference-routes','seasons']) {
  const source=fs.readFileSync(`almanac/${page}.html`,'utf8');
  const helper=source.match(/<script src="reference-route-text\.js\?v=[^"]+" defer><\/script>/g);
  assert.equal(helper?.length,1);
  assert.ok(source.indexOf(helper[0])<source.indexOf(`${page}.js?v=`));
}
assert.ok(fs.readFileSync('almanac/reference-route-atlas.js','utf8').includes("original?.closest('picture')"));
console.log('PASS: nullable ranges, unchanged finite labels, consumers, asset order and compact atlas picture selection');
