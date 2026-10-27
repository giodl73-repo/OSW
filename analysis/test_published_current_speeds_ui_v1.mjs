// DOM behavior checks only. Actual layout and WASM execution require cloud QA.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

class Element {
  constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.style={};}
  append(child){this.children.push(child);}
  setAttribute(key,value){this.attributes[key]=value;}
}
const document={createElement:tag=>new Element(tag),createElementNS:(_ns,tag)=>new Element(tag)};
const location={href:''},context={document,window:{},location};
vm.runInNewContext(fs.readFileSync('almanac/published-current-speeds.js','utf8'),context);
const render=context.window.renderPublishedCurrentSpeeds;
const doc=JSON.parse(fs.readFileSync('research/eacc-pemba-semba-2019-seasonal-speed-v1.json','utf8'));
const monthly=doc.monthly_records.map(r=>({...r,statistic_period:'monthly'}));
const scene={kind:'published_current_speed_statistics',title:'Pemba Channel',scope:doc.scope,records:monthly,
  source_conflicts:doc.source_conflicts,source_url:doc.source.url,
  monthly_figure:'figures/eacc-pemba-monthly-speed-v1.svg',seasonal_figure:'figures/eacc-pemba-seasonal-speed-v1.svg'};
const descendants=root=>[root,...root.children.flatMap(descendants)];
const find=(root,tag)=>descendants(root).filter(n=>n.tag===tag);
const root=new Element('div'),inspected=[];
render(root,scene,(collection,id)=>inspected.push([collection,id]));
assert.equal(find(root,'line').length,12);
assert.equal(find(root,'circle').length,12);
assert.equal(find(root,'tbody')[0].children.length,12);
assert.equal(find(root,'caption').length,1);
assert.match(find(root,'svg')[0].attributes['aria-label'],/not confidence/);
find(root,'button')[3].onclick();
assert.deepEqual(inspected,[['current_speed_statistics',monthly[3].id]]);
const selected=new Element('div');
render(selected,{...scene,records:[monthly[0]]});
assert.equal(find(selected,'line').length,1);
assert.equal(find(selected,'tbody')[0].children.length,1);
find(selected,'button')[0].onclick();
const query=JSON.parse(decodeURIComponent(location.href.split('?q=')[1]));
assert.equal(query.collection,'current_speed_statistics');
assert.equal(query.filters[0].value,monthly[0].id);
const empty=new Element('div');render(empty,null);
assert.equal(empty.children.length,0);
console.log('PASS: monthly rows, filtered rows, accessible descriptions and exact record navigation. Layout untested.');
