// Exact record identity survives the query engine's default ID ordering.
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
const rows=source.records.map((r,i)=>({...r,label:r.id,current_scope:source.current_scopes.find(s=>s.current_id===r.current_id),source_file:path,source_pointer:`/records/${i}`,method_discrepancies:source.method_discrepancies.filter(d=>d.current_id===r.current_id)})).sort((a,b)=>a.id.localeCompare(b.id));
const threshold=rows.find(r=>r.estimate_kind==='reported_greater_than');
assert.notEqual(rows[5].id,threshold.id);
const scene={kind:'published_seasonal_core_velocities',title:'AX08',scope:'Regional seasonal fits',records:rows,source_file:path,source_url:source.source.url,full_context_figure:source.visualization.figure};
const all=n=>[n,...n.children.flatMap(all)];
const root=new Element('div'),inspected=[];
context.window.renderPublishedCurrentSpeeds(root,scene,(collection,id)=>inspected.push([collection,id]));
assert.equal(all(root).find(n=>n.tag==='table').style.minWidth,'780px');
const body=all(root).find(n=>n.tag==='tbody');assert.equal(body.children.length,6);
const target=body.children.find(n=>n.attributes['data-core-velocity-id']===threshold.id);assert(target);
const graphic=all(target).find(n=>n.tag==='svg');
assert.equal(all(graphic).filter(n=>n.tag==='polyline').length,1);
assert.equal(all(graphic).find(n=>n.tag==='circle').attributes.fill,'none');
assert.match(graphic.attributes['aria-label'],/greater than 0.30/);
all(target).find(n=>n.tag==='button').onclick();
assert.deepEqual(inspected,[['current_core_velocity_estimates',threshold.id]]);
const query=JSON.parse(decodeURIComponent(all(target).find(n=>n.tag==='a').href.split('?source-q=')[1]));
assert.equal(query.pointer,threshold.source_pointer);assert.equal(query.document,path);
assert.equal(source.records[Number(query.pointer.split('/').at(-1))].id,threshold.id);
for(const row of body.children){
  assert.equal(row.children[0].style.width,'4rem');
  assert.equal(row.children[4].style.whiteSpace,'nowrap');assert.equal(row.children[5].style.whiteSpace,'nowrap');
}
assert.deepEqual(all(root).find(n=>n.tag==='thead').children[0].children.map(n=>n.textContent),['Current','Estimate','Season','Layer','Record','Source']);
const filtered=new Element('div');context.window.renderPublishedCurrentSpeeds(filtered,{...scene,records:[threshold]});
all(filtered).find(n=>n.tag==='button').onclick();
const address=JSON.parse(decodeURIComponent(location.href.split('?q=')[1]));
assert.equal(address.collection,'current_core_velocity_estimates');assert.equal(address.filters[0].value,threshold.id);
for(const page of ['query.html','reference-routes.html','seasons.html'])assert.match(fs.readFileSync('almanac/'+page,'utf8'),/published-current-speeds\.js\?v=6/);
console.log('PASS: ID-sorted row selection, exact source/record navigation, compact Current column, unbroken actions and value-first columns. Browser layout untested.');
