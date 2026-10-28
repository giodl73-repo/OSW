import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element{constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.style={};}append(el){this.children.push(el);}setAttribute(k,v){this.attributes[k]=String(v);}}
const document={createElement:t=>new Element(t),createElementNS:(_ns,t)=>new Element(t)};
const location={href:''},context={window:{},document,location};
vm.runInNewContext(fs.readFileSync('almanac/current-dimension-evidence.js','utf8'),context);
const contract=JSON.parse(fs.readFileSync('research/madagascar-dimensions-query-contract-v1.json','utf8'));
const scene={kind:'published_current_dimension_evidence',title:'Madagascar regional evidence',scope:'Separate studies; no seasonal range.',
 definition:'Width operators unspecified; no event widths extracted.',entity_id:contract.final_owner.id,
 width_records:[...contract.prior_records.widths,contract.width_record],event_records:[...contract.event_records].reverse(),
 source_url:contract.new_source.url,figure:'figures/ponsoni-emc-2016-dimensions-compact-v1.svg'};
const all=n=>[n,...n.children.flatMap(all)],text=n=>all(n).map(n=>n.textContent||'').join(' ');
const root=new Element('div'),calls=[];
context.window.renderCurrentDimensionEvidence(root,scene,(collection,id)=>calls.push([collection,id]));
const cards=all(root).filter(n=>n.attributes['data-dimension-width-id']);assert.equal(cards.length,2);
assert.match(text(cards[0]),/About 120 km/);assert.match(text(cards[1]),/About 60–100 km/);
assert.match(text(root),/Seasonal width range: Unknown. Numerical uncertainty: Unknown/);
assert.equal(all(cards[1]).filter(n=>n.tag==='line'&&n.attributes.stroke==='#087f8c').length,1);
all(cards[1]).find(n=>n.tag==='button').onclick();assert.deepEqual(calls,[['widths',contract.width_record.id]]);
const source=all(cards[1]).find(n=>n.textContent==='Source evidence record');
const sq=JSON.parse(decodeURIComponent(source.href.split('?source-q=')[1]));
assert.equal(sq.document,contract.width_record.source_file);assert.equal(sq.pointer,'/width_summary');
const events=all(root).filter(n=>n.attributes['data-flow-event-id']);assert.equal(events.length,8);
assert.equal(events[0].attributes['data-flow-event-id'],contract.event_records[0].id);
assert.match(text(events[0]),/2010-11-17/);assert.match(text(root),/No event widths were extracted/);
all(events[0]).find(n=>n.tag==='button').onclick();assert.deepEqual(calls[1],['current_reported_flow_events',contract.event_records[0].id]);
const filtered=new Element('div');context.window.renderCurrentDimensionEvidence(filtered,{...scene,width_records:[],event_records:[contract.event_records[2]]});
assert.equal(all(filtered).filter(n=>n.attributes['data-dimension-width-id']).length,0);
assert.equal(all(filtered).filter(n=>n.attributes['data-flow-event-id']).length,1);
all(filtered).find(n=>n.tag==='button').onclick();const q=JSON.parse(decodeURIComponent(location.href.split('?q=')[1]));
assert.equal(q.collection,'current_reported_flow_events');assert.equal(q.filters[0].value,contract.event_records[2].id);
const unknown=new Element('div');context.window.renderCurrentDimensionEvidence(unknown,{...scene,event_records:[],width_records:[{...contract.width_record,width_range_km:null}]});
assert.match(text(unknown),/Width: Unknown/);assert.equal(all(unknown).filter(n=>n.tag==='svg').length,0);
const collapsed=new Element('div');context.window.renderCurrentDimensionEvidence(collapsed,scene,undefined,{collapsed:true});
assert.equal(collapsed.children[0].tag,'details');assert.equal(collapsed.children[0].children[0].tag,'summary');
assert.ok(!Object.hasOwn(collapsed.children[0].attributes,'open'));
const empty=new Element('div');context.window.renderCurrentDimensionEvidence(empty,{...scene,width_records:[],event_records:[]});assert.equal(empty.children.length,0);
for(const page of ['query','reference-routes','seasons']){
 const html=fs.readFileSync(`almanac/${page}.html`,'utf8');
 assert.ok(html.includes('current-dimension-evidence.js?v=azcc-onken-1'));
 const consumer=page==='query'?'query-charts.js?':`${page}.js?`;
 assert.ok(html.indexOf('current-dimension-evidence.js?v=azcc-onken-1')<html.indexOf(consumer));
}
const schemaContext={window:{}};vm.runInNewContext(fs.readFileSync('almanac/dashboard-evidence-schema.js','utf8'),schemaContext);
const schema=schemaContext.window.oswDashboardEvidenceSchema;
const groups=Object.fromEntries(Object.keys(contract.dashboard_after.section_fingerprints).map(k=>[k,k]));
const labels=Object.fromEntries(Object.keys(contract.dashboard_after.capabilities).map(k=>[k,k]));
for(const row of [contract.dashboard_before,contract.dashboard_after]){
 assert(schema.validFingerprints(row.section_fingerprints,groups));assert(schema.validCapabilities(row.capabilities,labels,{}));
}
for(const value of [undefined,null,8,false,{}])assert.equal(schema.validFingerprints({...contract.dashboard_before.section_fingerprints,reported_flow_events:value},groups),false);
for(const value of [undefined,null,-1,1.5,'8',NaN])assert.equal(schema.validCapabilities({...contract.dashboard_before.capabilities,reported_flow_events:value},labels,{}),false);
const oldGroups=JSON.parse(fs.readFileSync('research/eac-mean-core-query-contract-v1.json','utf8')).dashboard_after;
assert(schema.validFingerprints(oldGroups.section_fingerprints,groups));assert(schema.validCapabilities(oldGroups.capabilities,labels,{}));
const html=fs.readFileSync('almanac/dashboard.html','utf8');
assert(html.indexOf('dashboard-evidence-schema.js?v=madagascar-dimensions-1')<html.indexOf('dashboard.js?v=madagascar-dimensions-1'));
console.log('PASS: width intervals, unknowns, filtered event cards, chronological order, source/Inspect links, collapsed atlas context, consumer order and optional dashboard fields. Actual browser layout remains pending.');
