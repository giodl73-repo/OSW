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
const contract=JSON.parse(fs.readFileSync('research/pacific-sec-gourdeau-2008-query-contract-v1.json','utf8'));
const all=node=>[node,...node.children.flatMap(all)];
const text=node=>all(node).map(n=>n.textContent||'').join(' ');
const root=new Element('div'),calls=[];
const scene={kind:'published_current_dimension_evidence',title:'Pacific SEC regional jet widths',scope:'Regional component jets, nonsynoptic July-October 2005 campaign',definition:'Author-reported approximate widths; exact edge threshold unknown',width_records:contract.width_records,event_records:[],entity_id:'current:pacific-south-equatorial',source_url:contract.new_source.url,figure:'figures/pacific-sec-gourdeau-2008-regional-widths-v1.svg'};
context.window.renderCurrentDimensionEvidence(root,scene,(collection,id)=>calls.push([collection,id]));
const cards=all(root).filter(n=>n.attributes['data-dimension-width-id']);assert.equal(cards.length,2);
for(let i=0;i<2;i++){
 assert(text(cards[i]).includes('About '+contract.width_records[i].approximate_width_km+' km'));
 assert(text(cards[i]).includes(contract.width_records[i].component_label));
 assert(text(cards[i]).includes('July-October 2005 campaign'));
 assert(text(cards[i]).includes(contract.width_records[i].vertical_scope));
 assert(text(cards[i]).includes('not a fixed-depth width or current thickness.'));
 assert(text(cards[i]).includes('Seasonal width range: Unknown. Numerical uncertainty: Unknown.'));
 assert(!text(cards[i]).includes('undefined'));
}
assert.equal(all(root).filter(n=>n.tag==='line'&&n.attributes['stroke-width']==='10').length,0);
const points=all(root).filter(n=>n.tag==='circle');assert.equal(points.length,2);
for(let i=0;i<2;i++)assert.equal(Number(points[i].attributes.cx),12+contract.width_records[i].approximate_width_km/300*276);
for(const button of all(root).filter(n=>n.tag==='button'))button.onclick();
assert.deepEqual(calls,contract.width_records.map(r=>['widths',r.id]));
const pointers=all(root).filter(n=>n.tag==='a'&&n.textContent==='Source evidence record').map(n=>JSON.parse(new URL(n.href,'https://test.invalid').searchParams.get('source-q')));
assert.deepEqual(pointers.map(p=>p.pointer),contract.width_records.map(r=>r.source_pointer));
const filtered=new Element('div');context.window.renderCurrentDimensionEvidence(filtered,{...scene,width_records:[contract.width_records[0]]});
assert.equal(all(filtered).filter(n=>n.attributes['data-dimension-width-id']).length,1);
console.log('PASS two distinct jet widths, campaign/layer scope, unknown ranges, source pointers and filtered selection');
