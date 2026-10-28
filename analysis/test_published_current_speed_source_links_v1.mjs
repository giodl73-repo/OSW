// Exact provenance navigation; rendering and source-worker execution need cloud QA.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.style={};}
  append(n){this.children.push(n);}
  setAttribute(){}
}
const document={createElement:t=>new Element(t),createElementNS:(_n,t)=>new Element(t)};
const context={window:{},document,location:{}};
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
console.log('PASS: exact April source-table navigation resolves to the matching original summary.');
