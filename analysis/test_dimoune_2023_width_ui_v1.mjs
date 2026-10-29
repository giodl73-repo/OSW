import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.style={};}
  append(child){this.children.push(child);}
  setAttribute(key,value){this.attributes[key]=String(value);}
}
const context={window:{},document:{createElement:tag=>new Element(tag),createElementNS:(_ns,tag)=>new Element(tag)},location:{href:''}};
vm.runInNewContext(fs.readFileSync('almanac/current-dimension-evidence.js','utf8'),context);
const contract=JSON.parse(fs.readFileSync('research/dimoune-2023-width-query-contract-v1.json','utf8'));
const all=node=>[node,...node.children.flatMap(all)];
const text=node=>all(node).map(n=>n.textContent||'').join(' ');
const root=new Element('div'),calls=[];
const scene={kind:'published_current_dimension_evidence',title:'Published mean section widths',scope:'Regional mean widths, not annual bounds.',
  definition:'Zero crossings after averaging velocity.',width_records:contract.width_records,event_records:[],
  entity_id:null,source_url:contract.new_source.url,figure:'figures/dimoune-2023-section-widths-source-review-v1.svg'};
context.window.renderCurrentDimensionEvidence(root,scene,(collection,id)=>calls.push([collection,id]));
const nodes=all(root),cards=nodes.filter(n=>n.attributes['data-dimension-width-id']);
assert.equal(cards.length,6);
assert.equal(nodes.filter(n=>n.attributes['data-flow-event-id']).length,0);
assert.equal(nodes.filter(n=>n.tag==='line'&&n.attributes['stroke-width']==='10').length,0);
assert.equal(nodes.filter(n=>n.tag==='a'&&n.textContent==='Open current atlas').length,0);
for(let i=0;i<cards.length;i++){
  assert(text(cards[i]).includes(`About ${contract.width_records[i].approximate_width_km} km`));
  assert(text(cards[i]).includes('Mean velocity profile, 1993-01 to 2017-12'));
  assert(text(cards[i]).includes('Seasonal width range: Unknown. Numerical uncertainty: Unknown.'));
}
assert.equal(cards.filter(n=>text(n).includes('Source discrepancy:')).length,3);
const pointers=nodes.filter(n=>n.tag==='a'&&n.textContent==='Source evidence record').map(n=>JSON.parse(new URL(n.href,'https://test.invalid').searchParams.get('source-q')));
assert.equal(pointers.length,6);assert.equal(new Set(pointers.map(p=>p.pointer)).size,6);
for(const button of nodes.filter(n=>n.tag==='button'))button.onclick();
assert.deepEqual(calls,contract.width_records.map(r=>['widths',r.id]));
const filtered=new Element('div');context.window.renderCurrentDimensionEvidence(filtered,{...scene,entity_id:'current:atlantic-south-equatorial',width_records:[contract.width_records[2]]});
assert.equal(all(filtered).filter(n=>n.attributes['data-dimension-width-id']).length,1);
assert.equal(all(filtered).find(n=>n.textContent==='Open current atlas').href,'reference-routes.html?atlas-feature=current%3Aatlantic-south-equatorial#route-atlas');
const historical=new Element('div');
context.window.renderCurrentDimensionEvidence(historical,{...scene,width_records:contract.prior_owners['current:atlantic-north-equatorial-countercurrent'].widths});
assert(!text(historical).includes('undefined'));
assert(text(historical).includes('HS5 mean section (42 W)'));
assert(text(historical).includes('Mean velocity profile, 1993-01 to 2017-12'));
console.log('PASS: six selected summaries, source pointers, three discrepancies, mean period, unknown bounds, no false playback or multi-owner atlas target. Actual browser layout pending.');
