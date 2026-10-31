const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const c=JSON.parse(fs.readFileSync('research/chen-indian-sec-ridge-length-query-contract-v1.json','utf8'));
const scene={kind:'regional_model_core_length_series',series:c.series_record,readings:c.reading_records,sensitivities:c.sensitivity_records};
const context={window:{}};vm.createContext(context);vm.runInContext(fs.readFileSync('almanac/regional-model-atlas.js','utf8'),context);
const api=context.window.oswRegionalModelAtlas,snapshot={regional_model_length_scenes:{'indian-south-equatorial':scene}};
assert.equal(api.scene(snapshot,'current:indian-south-equatorial'),scene);
assert.equal(api.scene(snapshot,'current:south-equatorial'),null);assert.equal(api.scene({},'current:indian-south-equatorial'),null);
assert.equal(api.qualified(scene).length,8);assert.equal(api.nominal(scene).length,3);assert.equal(api.qualified(null).length,0);
const nominal=api.nominal(scene);assert.deepEqual(Array.from(nominal,r=>r.provider_year),[1995,2010,2011]);
assert.equal(api.selection(scene,'missing').id,nominal[0].id);
const alternative=c.reading_records.find(r=>r.kernel_cells===5&&r.length_km!==null);
assert.equal(api.selection(scene,alternative.id),alternative);
assert.equal(api.selection(scene,c.reading_records.find(r=>r.length_km===null).id).id,nominal[0].id);
assert.equal(api.selection(null,null),null);
const calls=[],paths=[];
const marks=api.draw({scene,currentId:'current:indian-south-equatorial',parent:'layer',
  make:(tag,attrs,parent)=>{assert.equal(tag,'path');assert.equal(parent,'layer');const node={attrs,dataset:{}};paths.push(node);return node;},
  pathData:coords=>{assert.ok(coords.length>100);assert.ok(coords.every(p=>p.length===2&&p.every(Number.isFinite)));return 'checked-path';},
  interactive:(node,label,activate)=>{assert.match(label,/regional model-grid trace/);assert.match(label,/Whole-current length unknown/);node.activate=activate;},
  onSelect:row=>calls.push(row)});
assert.equal(marks.length,8);assert.equal(marks.filter(m=>m.dataset.modelNominal==='true').length,3);
assert.equal(new Set(marks.map(m=>m.dataset.modelReadingId)).size,8);
assert.equal(paths.filter(p=>p.attrs.class==='route-atlas-regional-model-line').length,8);
marks[0].activate();assert.equal(calls[0].id,marks[0].dataset.modelReadingId);
assert.ok(marks.every(m=>m.dataset.currentId==='current:indian-south-equatorial'));
assert.equal(api.draw({scene:null}).length,0);
const html=fs.readFileSync('almanac/reference-routes.html','utf8'),atlas=fs.readFileSync('almanac/reference-route-atlas.js','utf8');
assert.ok(html.indexOf('regional-model-atlas.js')<html.indexOf('reference-route-atlas.js'));
assert.ok(html.indexOf('regional-model-lengths.js')<html.indexOf('reference-route-atlas.js'));
assert.match(html,/data-model-nominal="false"\]:not\(\.selected\)/);
assert.match(atlas,/url.searchParams.set\('atlas-model-reading',selectedModelReadingId\)/);
assert.match(atlas,/url.searchParams.delete\('atlas-model-reading'\)/);
assert.match(atlas,/const requestedModelReading=modelReadingId\|\|new URL\(location.href\).searchParams.get\('atlas-model-reading'\)/);
console.log(JSON.stringify({status:'PASS_REGIONAL_MODEL_ATLAS_HELPER_AND_WIRING',qualified_paths:8,default_nominal_paths:3,withheld_paths:67,alternative_trace_selection:true,family_inheritance:false,browser_visual_review:false}));
