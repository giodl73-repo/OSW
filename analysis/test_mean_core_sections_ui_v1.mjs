import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element{constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.style={};}append(el){this.children.push(el);}setAttribute(k,v){this.attributes[k]=String(v);}}
const document={createElement:t=>new Element(t),createElementNS:(_ns,t)=>new Element(t)};
const location={href:''},context={window:{},document,location};
vm.runInNewContext(fs.readFileSync('almanac/mean-core-sections.js','utf8'),context);
const contract=JSON.parse(fs.readFileSync('research/eac-mean-core-query-contract-v1.json','utf8'));
const scene={kind:'published_mean_core_sections',title:'EAC regional mean model core',scope:'1994–2016 model mean; spatial sections, not seasonal ranges.',
 records:contract.records,boundary:'−0.05 m/s contour in mean alongshore velocity',definition:'Geometry of mean velocity, not mean of daily dimensions.',
 labeling_note:'Forster Table1 uses32.3°S; Figure5(c) is labeled32.0°S.',source_url:contract.new_source.url,
 figure:'figures/eac-kerry-2020-mean-core-dimensions-v2.svg',compact_figure:'figures/eac-kerry-2020-mean-core-dimensions-compact-v2.svg'};
const all=n=>[n,...n.children.flatMap(all)],text=n=>all(n).map(n=>n.textContent||'').join(' ');
const root=new Element('div'),calls=[];
context.window.renderMeanCoreSections(root,scene,(collection,id)=>calls.push([collection,id]));
const cards=all(root).filter(n=>n.attributes['data-mean-core-id']);assert.equal(cards.length,5);
assert.match(text(root),/157.6 km/);assert.match(text(root),/1,250 m/);assert.match(text(root),/97.1 km²/);
assert.match(text(root),/southern extension/);assert.match(text(root),/Annual dimension ranges and numerical uncertainty are unknown/);
assert.match(text(root),/5 matching section records/);assert.match(text(root),/32.3°S.*32.0°S/);
const circles=all(cards[0]).filter(n=>n.tag==='circle');assert.equal(circles.length,2);
assert.equal(Number(circles[0].attributes.cx),12+157.6/240*276);assert.equal(Number(circles[1].attributes.cx),12+820/1400*276);
all(cards[0]).find(n=>n.tag==='button').onclick();assert.deepEqual(calls,[['current_mean_core_sections',contract.records[0].id]]);
const source=all(cards[0]).find(n=>n.textContent==='Source table record');
const sourceQuery=JSON.parse(decodeURIComponent(source.href.split('?source-q=')[1]));
assert.equal(sourceQuery.document,contract.records[0].source_file);assert.equal(sourceQuery.pointer,'/records/0');
const filtered=new Element('div');context.window.renderMeanCoreSections(filtered,{...scene,records:[scene.records[2]]});
assert.equal(all(filtered).filter(n=>n.attributes['data-mean-core-id']).length,1);assert.match(text(filtered),/1 matching section record\./);
assert.match(text(filtered),/178.7 km/);assert.ok(!text(filtered).includes('157.6 km'));
all(filtered).find(n=>n.tag==='button').onclick();const query=JSON.parse(decodeURIComponent(location.href.split('?q=')[1]));
assert.equal(query.collection,'current_mean_core_sections');assert.equal(query.filters[0].value,scene.records[2].id);
const unknown=new Element('div');context.window.renderMeanCoreSections(unknown,{...scene,records:[{...scene.records[0],offshore_extent_km:null,maximum_depth_m:null}]});
assert.equal(all(unknown).filter(n=>n.tag==='circle').length,0);
assert.ok(all(unknown).some(n=>n.tag==='dd'&&n.textContent==='Unknown km'));
assert.ok(all(unknown).some(n=>n.tag==='dd'&&n.textContent==='Unknown m'));
const empty=new Element('div');context.window.renderMeanCoreSections(empty,{...scene,records:[]});assert.equal(empty.children.length,0);
const compact=new Element('div');context.window.renderMeanCoreSections(compact,scene,undefined,{collapsed:true});
assert.equal(compact.children[0].tag,'details');assert.equal(compact.children[0].children[0].tag,'summary');
assert.ok(!('open' in compact.children[0].attributes));assert.match(text(compact.children[0].children[0]),/5 model mean-core sections/);
for(const page of ['query','reference-routes','seasons']){
 const html=fs.readFileSync(`almanac/${page}.html`,'utf8');
 assert.ok(html.includes('mean-core-sections.js?v=1'));
 const consumer=page==='query'?'query-charts.js?':`${page}.js?`;
 assert.ok(html.indexOf('mean-core-sections.js?v=1')<html.indexOf(consumer));
}
assert.ok(fs.readFileSync('almanac/reference-routes.js','utf8').indexOf('window.renderMeanCoreSections(card')>fs.readFileSync('almanac/reference-routes.js','utf8').indexOf('Open route map at full size'));
assert.ok(fs.readFileSync('almanac/dashboard.html','utf8').includes('value="reported_model_core_sections"'));
assert.ok(fs.readFileSync('almanac/dashboard.js','utf8').includes("mean_model_core_sections:'Mean model-core sections'"));
console.log('PASS: five/filtered section cards, source/Inspect links, unknowns, compact disclosure, separate scales, consumer ordering and dashboard labels; browser layout pending');
