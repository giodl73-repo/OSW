const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const contract=JSON.parse(fs.readFileSync('research/chen-indian-sec-ridge-length-query-contract-v1.json','utf8'));
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.events={};this.style={};this.textContent='';}
  append(child){this.children.push(child);}
  setAttribute(k,v){this.attrs[k]=String(v);}
  addEventListener(k,v){this.events[k]=v;}
}
const context={window:{},document:{createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t)},location:{}};
vm.createContext(context);vm.runInContext(fs.readFileSync('almanac/regional-model-lengths.js','utf8'),context);
const flat=e=>[e,...e.children.flatMap(flat)];
const text=e=>flat(e).map(n=>n.textContent).join('\n');
const scene={kind:'regional_model_core_length_series',title:'Indian SEC regional lengths',scope:contract.series_record.scope,series:contract.series_record,entity_id:'current:indian-south-equatorial'};
function render(extra){const parent=new Element('root'),calls=[];context.window.renderRegionalModelLengths(parent,{...scene,...extra},(...a)=>calls.push(a));return {parent,calls,nodes:flat(parent)};}
// Full card retains failed cases and all scenarios, while mapping exactly eight qualified traces.
const full=render({readings:contract.reading_records,sensitivities:contract.sensitivity_records});
const paths=full.nodes.filter(n=>n.attrs['data-model-reading-id']);assert.equal(paths.length,8);
assert.match(text(full.parent),/75 trace cases · 8 matching mapped traces/);
assert.match(text(full.parent),/67 withheld/);assert.match(text(full.parent),/120 matching method/);
assert.equal(full.nodes.filter(n=>n.tag==='tr').length,25+75+120+3);
assert.ok(!text(full.parent).includes('undefined'));assert.equal(full.nodes.filter(n=>n.tag==='img').length,0);
paths[0].events.focus();assert.match(text(full.parent),/1995 · kernel 3/);
paths[0].events.keydown({key:'Enter',preventDefault(){}});assert.equal(full.calls[0][0],'current_length_readings');assert.equal(full.calls[0][1],paths[0].attrs['data-model-reading-id']);
// Filtered missing cases must not reintroduce global successes or static full-series imagery.
const failed=contract.reading_records.filter(r=>r.length_km===null);
const missing=render({selected_collection:'current_length_readings',selected_records:failed,readings:contract.reading_records});
assert.equal(missing.nodes.filter(n=>n.tag==='svg').length,0);
assert.match(text(missing.parent),/67 matching trace cases/);assert.match(text(missing.parent),/No qualified map geometry/);
assert.ok(!text(missing.parent).includes('Model-year coverage'));
// A single qualified query maps that one path and preserves its exact record selection.
const single=render({selected_collection:'current_length_readings',selected_records:[contract.reading_records.find(r=>r.length_km!==null)]});
assert.equal(single.nodes.filter(n=>n.attrs['data-model-reading-id']).length,1);
assert.ok(!text(single.parent).includes('120 matching'));
// Sensitivity-only queries expose only matched choices, never all parent paths or an envelope.
const choice=render({selected_collection:'current_length_sensitivities',selected_records:[contract.sensitivity_records[17]]});
assert.equal(choice.nodes.filter(n=>n.tag==='svg').length,0);assert.match(text(choice.parent),/1 matching method/);
const inspect=choice.nodes.find(n=>n.tag==='button'&&n.textContent==='Inspect');inspect.events.click();assert.equal(choice.calls[0][1],contract.sensitivity_records[17].id);
// Series queries have summaries but cannot fabricate geometry absent from their response.
const series=render({selected_collection:'current_length_series',selected_records:[contract.series_record]});
assert.match(text(series.parent),/Model-year coverage/);assert.equal(series.nodes.filter(n=>n.tag==='svg').length,0);
const paper=series.nodes.find(n=>n.tag==='button'&&n.textContent==='Paper');paper.events.click();assert.equal(series.calls[0][1],contract.series_record.source_id);
for(const page of ['query','object']){const html=fs.readFileSync(`almanac/${page}.html`,'utf8');assert.ok(html.indexOf('regional-model-lengths.js')<html.indexOf(`${page==='query'?'query-charts':'object'}.js`));}
const root=new Element('root');context.window.renderRegionalModelLengths(root,{kind:'other'});assert.equal(root.children.length,0);
console.log(JSON.stringify({status:'PASS_REGIONAL_MODEL_RENDERER_FUNCTIONAL_CHECKS',cases:7,qualified_paths:8,withheld_cases:67,sensitivity_records:120,browser_visual_review:false}));
