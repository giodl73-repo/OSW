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
const contract=JSON.parse(fs.readFileSync('research/atlantic-nec-stramma-2005-query-contract-v1.json','utf8'));
const all=node=>[node,...node.children.flatMap(all)];
const text=node=>all(node).map(n=>n.textContent||'').join(' ');
const root=new Element('div'),calls=[];
const scene={kind:'published_current_dimension_evidence',title:'Atlantic NEC regional spans',scope:'Regional southern band',definition:'Nominal meridional separation',width_records:contract.width_records,event_records:[],entity_id:'current:atlantic-north-equatorial',source_url:contract.new_source.url,figure:'figures/atlantic-nec-stramma-2005-band-spans-prepared-v2.svg'};
context.window.renderCurrentDimensionEvidence(root,scene,(collection,id)=>calls.push([collection,id]));
const cards=all(root).filter(n=>n.attributes['data-dimension-width-id']);assert.equal(cards.length,2);
for(let i=0;i<2;i++){
 assert(text(cards[i]).includes('About 700 km'));
 assert(text(cards[i]).includes(i===0?'16–22°N':'14–20°N'));
 assert(text(cards[i]).includes('Sampling depth is not current thickness.'));
 assert(text(cards[i]).includes('Seasonal width range: Unknown. Numerical uncertainty: Unknown.'));
 assert(!text(cards[i]).includes('undefined'));
}
assert.equal(all(root).filter(n=>n.tag==='line'&&n.attributes['stroke-width']==='10').length,0);
for(const button of all(root).filter(n=>n.tag==='button'))button.onclick();
assert.deepEqual(calls,contract.width_records.map(r=>['widths',r.id]));
const pointers=all(root).filter(n=>n.tag==='a'&&n.textContent==='Source evidence record').map(n=>JSON.parse(new URL(n.href,'https://test.invalid').searchParams.get('source-q')));
assert.deepEqual(pointers.map(p=>p.pointer),contract.width_records.map(r=>r.source_pointer));
const filtered=new Element('div');context.window.renderCurrentDimensionEvidence(filtered,{...scene,width_records:[contract.width_records[0]]});
assert.equal(all(filtered).filter(n=>n.attributes['data-dimension-width-id']).length,1);
console.log('PASS two distinct spans, scope, source pointers and filtered selection');
