// Exact provenance navigation; rendering and source-worker execution need cloud QA.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.style={};this.attributes={};this.isConnected=true;this.clientWidth=800;}
  append(n){this.children.push(n);}
  setAttribute(key,value){this.attributes[key]=String(value);}
}
const document={createElement:t=>new Element(t),createElementNS:(_n,t)=>new Element(t)};
const observers=[];
class ResizeObserver{
  constructor(callback){this.callback=callback;observers.push(this);}
  observe(target){this.target=target;}
  disconnect(){this.disconnected=true;}
}
const context={window:{},document,location:{},ResizeObserver};
vm.runInNewContext(fs.readFileSync('almanac/published-current-speeds.js','utf8'),context);
const path='research/eacc-pemba-semba-2019-seasonal-speed-v1.json';
const doc=JSON.parse(fs.readFileSync(path));
const row={...doc.monthly_records[3],statistic_period:'monthly',source_pointer:'/monthly_records/3'};
const root=new Element('div');
context.window.renderPublishedCurrentSpeeds(root,{kind:'published_current_speed_statistics',title:'Pemba',scope:doc.scope,records:[row],source_file:path,source_conflicts:doc.source_conflicts,source_url:doc.source.url,monthly_figure:'monthly.svg',seasonal_figure:'seasonal.svg'},()=>{});
const all=n=>[n,...n.children.flatMap(all)];
const source=all(root).find(n=>n.tag==='a'&&n.href.includes('?source-q='));
assert(source);
const query=JSON.parse(decodeURIComponent(source.href.split('?source-q=')[1]));
assert.equal(query.document,path);
assert.equal(query.pointer,'/monthly_records/3');
const target=query.pointer.split('/').slice(1).reduce((value,key)=>value[key],doc);
assert.equal(target.id,row.id);
assert.equal(target.median,1.13);
const observer=observers[0];assert(observer);
observer.callback([{contentRect:{width:320}}]);
const chart=all(root).find(n=>n.tag==='svg');
assert.equal(chart.attributes.viewBox,'0 0 320 83');
const marker=all(root).find(n=>n.tag==='circle');
assert(Math.abs((Number(marker.attributes.cx)-112)/150*2-target.median)<1e-12);
observer.target.isConnected=false;observer.callback([{contentRect:{width:0}}]);
assert.equal(observer.disconnected,true);
console.log('PASS: exact source-table navigation, responsive median scale, and detached observer cleanup.');
