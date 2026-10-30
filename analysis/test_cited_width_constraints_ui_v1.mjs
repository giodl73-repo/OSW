import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element {constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.style={};}append(el){this.children.push(el);}setAttribute(k,v){this.attributes[k]=String(v);}}
const document={createElement:t=>new Element(t),createElementNS:(_ns,t)=>new Element(t)};
const location={href:''},context={document,window:{},location};vm.runInNewContext(fs.readFileSync('almanac/cited-width-constraints.js','utf8'),context);
const sourceFile='research/eacc-dekeyzer-2012-cited-width-lower-bound-source-facts-v1.json',facts=JSON.parse(fs.readFileSync(sourceFile,'utf8'));
const row={...facts.records[0],width_metric_label:'Thesis-cited exclusive width lower bound',source_file:sourceFile,source_pointer:'/records/0',
  source_download_url:facts.source.source_url+'#page=74',time_convention:facts.records[0].time_description,layer:facts.records[0].layer_description,
  cited_width_constraint_context:{lineage_note:facts.lineage_note}};
assert.equal(context.window.citedWidthConstraintLabel(row),'>160 km · cited exclusive lower bound; central width and upper limit unknown');
assert.equal(context.window.citedWidthConstraintLabel({approximate_width_km:160}),null);
for(const change of [{reported_operator:'gte'},{reported_width_km:160},{upper_bound_km:200}])assert.throws(()=>context.window.citedWidthConstraintLabel({...row,...change}),/Unsupported/);
const scene={kind:'published_cited_width_constraints',title:'EACC cited lower bound',scope:'Historical context',records:[row],full_context_figure:'figures/eacc-dekeyzer-2012-cited-width-lower-bound-v2.svg'};
const all=n=>[n,...n.children.flatMap(all)],text=n=>all(n).map(n=>n.textContent||'').join(' '),root=new Element('div'),inspected=[];
context.window.renderCitedWidthConstraints(root,scene,(collection,id)=>inspected.push([collection,id]));
assert.match(text(root),/>160 km/);assert.match(text(root),/not another independent width observation/);assert.match(text(root),/no measured endpoint/);
assert.match(text(root),/original methods and edition remain unverified/);assert.equal(all(root).find(n=>n.tag==='circle').attributes.fill,'white');
assert.equal(all(root).find(n=>n.tag==='circle').attributes.cx,'160');assert.match(all(root).find(n=>n.tag==='svg').attributes['aria-label'],/exclusive.*greater than 160/);
all(root).find(n=>n.tag==='button').onclick();assert.deepEqual(inspected,[['widths',row.id]]);
const query=JSON.parse(decodeURIComponent(all(root).find(n=>n.textContent==='Source record').href.split('?source-q=')[1]));assert.equal(query.document,sourceFile);assert.equal(query.pointer,'/records/0');
assert.equal(all(root).find(n=>n.textContent==='Original thesis').href,facts.source.source_url+'#page=74');
for(const change of [{reported_operator:'gte'},{reported_width_km:160},{upper_bound_km:200}])assert.throws(()=>context.window.renderCitedWidthConstraints(new Element('div'),{...scene,records:[{...row,...change}]}),/Unsupported/);
const empty=new Element('div');context.window.renderCitedWidthConstraints(empty,{...scene,records:[]});assert.equal(empty.children.length,0);
context.window.renderCitedWidthConstraints(empty,scene);all(empty).find(n=>n.tag==='button').onclick();assert.equal(JSON.parse(decodeURIComponent(location.href.split('?q=')[1])).filters[0].value,row.id);
for(const page of ['query.html','reference-routes.html','seasons.html'])assert.match(fs.readFileSync('almanac/'+page,'utf8'),/cited-width-constraints\.js\?v=[^"]+/);
console.log('PASS: exclusive lower-bound symbol, unknown upper/central width, provenance and exact navigation. Browser layout pending.');
