import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element {constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.style={};}append(el){this.children.push(el);}setAttribute(key,value){this.attributes[key]=String(value);}}
const document={createElement:tag=>new Element(tag),createElementNS:(_ns,tag)=>new Element(tag)};
const location={href:''},context={document,window:{},location};vm.runInNewContext(fs.readFileSync('almanac/satellite-core-widths.js','utf8'),context);
const sourceFile='research/agulhas-krug-2012-core-widths-source-facts-v1.json',facts=JSON.parse(fs.readFileSync(sourceFile,'utf8'));
const rows=facts.records.map((r,i)=>({...r,width_metric:i===0?'satellite_gaussian_core_mean':'satellite_thermal_core_mean',time_convention:r.source_time_description,boundary_rule:r.operator,layer:'No fixed depth',source_file:sourceFile,source_pointer:`/records/${i}`}));
const scene={kind:'published_satellite_core_widths',title:'Agulhas satellite core widths',scope:'Track020',records:rows,seasonality_finding:facts.seasonality_finding,source_ambiguities:facts.source_ambiguities,full_context_figure:'figures/agulhas-krug-2012-core-widths-v1.svg'};
const all=n=>[n,...n.children.flatMap(all)],text=n=>all(n).map(n=>n.textContent||'').join(' ');
const root=new Element('div'),inspected=[];context.window.renderSatelliteCoreWidths(root,scene,(collection,id)=>inspected.push([collection,id]));
const cards=all(root).filter(n=>n.attributes['data-satellite-width-id']);assert.equal(cards.length,2);
for(const [i,card] of cards.entries()){
 assert.equal(all(card).find(n=>n.tag==='rect').attributes.width,String(rows[i].reported_mean_width_km));
 all(card).find(n=>n.tag==='button').onclick();assert.deepEqual(inspected[i],['widths',rows[i].id]);
 const q=JSON.parse(decodeURIComponent(all(card).find(n=>n.tag==='a').href.split('?source-q=')[1]));assert.equal(q.document,sourceFile);assert.equal(q.pointer,`/records/${i}`);
 assert.match(all(card).find(n=>n.tag==='svg').attributes['aria-label'],/regional mean/);
}
assert.match(text(root),/not seasonal limits/);assert.match(text(root),/not mathematically equivalent/);
assert.match(text(root),/width is not assumed constant/);
const filtered=new Element('div');context.window.renderSatelliteCoreWidths(filtered,{...scene,records:[rows[1]]});
assert.equal(all(filtered).filter(n=>n.attributes['data-satellite-width-id']).length,1);
assert.doesNotMatch(text(filtered),/64 km mean/);assert.match(text(filtered),/80 km mean/);
all(filtered).find(n=>n.tag==='button').onclick();const q=JSON.parse(decodeURIComponent(location.href.split('?q=')[1]));assert.equal(q.filters[0].value,rows[1].id);
assert.equal(all(filtered).find(n=>n.textContent==='Full context comparison (both methods)').href,'../'+scene.full_context_figure);
for(const page of ['query.html','reference-routes.html','seasons.html'])assert.match(fs.readFileSync('almanac/'+page,'utf8'),/satellite-core-widths\.js\?v=1/);
console.log('PASS: method-specific means, accessible bars, filtered records and exact Inspect/source navigation. Browser layout untested.');
