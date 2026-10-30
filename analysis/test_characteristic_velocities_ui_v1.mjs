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
const contract=JSON.parse(fs.readFileSync('research/richardson-walsh-1986-characteristic-velocity-query-contract-v1.json','utf8'));
vm.runInNewContext(fs.readFileSync('almanac/published-current-speeds.js','utf8'),context);
const all=node=>[node,...node.children.flatMap(all)];const text=node=>all(node).map(n=>n.textContent||'').join(' ');
const scene={kind:'published_characteristic_current_velocities',title:'Characteristic velocities',scope:'Map values retain separate operators.',time_support:'1875–1976',operator_note:'Printed amplitude formula; no monthly phases.',unknowns:'Annual extrema and monthly series: unknown.',records:contract.records,source_file:'research/richardson-walsh-1986-characteristic-velocity-source-facts-v1.json',source_url:contract.new_source.url,figure:'figures/richardson-walsh-1986-characteristic-velocities-v1.svg'};
const root=new Element('div'),calls=[];context.window.renderPublishedCurrentSpeeds(root,scene,(collection,id)=>calls.push([collection,id]));
const cards=all(root).filter(n=>n.attributes['data-characteristic-velocity-id']);assert.equal(cards.length,10);
for(const card of cards){assert.equal(all(card).filter(n=>n.tag==='dt').length,4);assert(text(card).includes('annual extrema, confidence interval and monthly series remain unknown'));assert(!text(card).includes('undefined'));}
assert(text(cards[6]).includes('0.05–0.10 m/s'));assert(text(cards[2]).includes('0.75 m/s'));
for(const button of all(root).filter(n=>n.tag==='button'))button.onclick();assert.deepEqual(calls,contract.records.map(r=>['current_characteristic_velocities',r.id]));
const filtered=new Element('div');context.window.renderPublishedCurrentSpeeds(filtered,{...scene,records:[contract.records[6]]});assert.equal(all(filtered).filter(n=>n.attributes['data-characteristic-velocity-id']).length,1);
assert.equal(all(root).filter(n=>n.tag==='button'&&/play/i.test(n.textContent)).length,0);
const grouped=new Element('div');context.window.renderPublishedCurrentSpeeds(grouped,{kind:'published_velocity_evidence_groups',scenes:[{...scene,records:[contract.records[0]]},{...scene,records:[contract.records[1]]}]});assert.equal(all(grouped).filter(n=>n.attributes['data-characteristic-velocity-id']).length,2);
console.log('PASS four separate metrics, characteristic interval, source/Inspect links, selection, grouped evidence and no synthetic playback');
