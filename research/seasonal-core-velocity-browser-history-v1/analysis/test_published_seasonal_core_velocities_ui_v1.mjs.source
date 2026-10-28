// DOM behavior only; cloud browser/native/WASM QA remains required.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.style={};}
  append(child){this.children.push(child);}
  setAttribute(key,value){this.attributes[key]=String(value);}
}
const document={createElement:tag=>new Element(tag),createElementNS:(_ns,tag)=>new Element(tag)};
const location={href:''},context={document,window:{},location};
vm.runInNewContext(fs.readFileSync('almanac/published-current-speeds.js','utf8'),context);
const path='research/atlantic-ax08-goes-2013-seasonal-core-speeds-v1.json';
const source=JSON.parse(fs.readFileSync(path,'utf8'));
const rows=source.records.map((r,i)=>({...r,label:r.id,current_scope:source.current_scopes.find(s=>s.current_id===r.current_id),source_file:path,source_pointer:`/records/${i}`,method_discrepancies:source.method_discrepancies.filter(d=>d.current_id===r.current_id)}));
const scene={kind:'published_seasonal_core_velocities',title:'AX08',scope:'Regional seasonal fits',records:rows,source_file:path,source_url:source.source.url,full_context_figure:source.visualization.figure};
const all=n=>[n,...n.children.flatMap(all)];
const root=new Element('div'),inspected=[];
context.window.renderPublishedCurrentSpeeds(root,scene,(collection,id)=>inspected.push([collection,id]));
assert.equal(all(root).filter(n=>n.tag==='tbody')[0].children.length,6);
assert.equal(all(root).filter(n=>n.tag==='svg').length,6);
const threshold=all(root).filter(n=>n.tag==='svg')[5];
assert.equal(all(threshold).filter(n=>n.tag==='polyline').length,1);
assert.equal(all(threshold).find(n=>n.tag==='circle').attributes.fill,'none');
assert.match(threshold.attributes['aria-label'],/greater than 0.30/);
const interval=all(root).filter(n=>n.tag==='svg')[1];
assert.equal(all(interval).filter(n=>n.tag==='circle').length,0);
assert.match(interval.attributes['aria-label'],/0.40–0.50/);
const links=all(root).filter(n=>n.tag==='a'&&n.href.includes('?source-q='));
assert.equal(links.length,6);
for(let i=0;i<links.length;i++){
  const q=JSON.parse(decodeURIComponent(links[i].href.split('?source-q=')[1]));
  assert.equal(q.document,path);assert.equal(q.pointer,`/records/${i}`);
  assert.equal(source.records[i].id,rows[i].id);
}
all(root).filter(n=>n.tag==='button')[5].onclick();
assert.deepEqual(inspected,[['current_core_velocity_estimates',rows[5].id]]);
const filtered=new Element('div');context.window.renderPublishedCurrentSpeeds(filtered,{...scene,records:[rows[5]]});
assert.equal(all(filtered).filter(n=>n.tag==='tbody')[0].children.length,1);
all(filtered).find(n=>n.tag==='button').onclick();
const q=JSON.parse(decodeURIComponent(location.href.split('?q=')[1]));
assert.equal(q.collection,'current_core_velocity_estimates');assert.equal(q.filters[0].value,rows[5].id);
const empty=new Element('div');context.window.renderPublishedCurrentSpeeds(empty,{...scene,records:[]});assert.equal(empty.children.length,0);
for(const page of ['query.html','reference-routes.html','seasons.html'])assert.match(fs.readFileSync('almanac/'+page,'utf8'),/published-current-speeds\.js\?v=4/);
assert.match(fs.readFileSync('almanac/query-charts.js','utf8'),/'published_seasonal_core_velocities'/);
console.log('PASS: six rows, filtered threshold, distinct interval/open-ended marks, exact source and record navigation, entry-page wiring. Layout untested.');
