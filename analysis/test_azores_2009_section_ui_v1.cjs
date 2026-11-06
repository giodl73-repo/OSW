/* Source-only DOM behavior checks. These do not replace real browser QA. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.style={};this.dataset={};this.textContent='';}
  append(child){this.children.push(child);}
}
const window={};
vm.runInNewContext(fs.readFileSync('almanac/azores-2009-section.js','utf8'),{window,document:{createElement:tag=>new Element(tag)}});
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const review=read('research/azores-2009-section-original-review-v1.json');
const binding=read('research/azores-2009-section-record-bindings-v1.json');
const scene={kind:'azores_2009_section_review',title:'Azores / surveyed width sections',
  records:binding.records,enrichments:review.existing_measurement_enrichments,matching_ids:[],
  figure_file:'figures/azores-2009-section-card-v1.svg',source_file:'research/azores-2009-section-original-review-v1.json',
  bindings_file:'research/azores-2009-section-record-bindings-v1.json',source_url:review.source.publisher_url,scope:'Dated section spans'};
function nodes(element){return [element,...element.children.flatMap(nodes)];}
const root=new Element('main'),calls=[];
window.renderAzores2009Section(root,scene,'current:azores-countercurrent',(...args)=>calls.push(args));
const all=nodes(root);
assert.equal(all.filter(n=>n.tag==='h5'&&n.textContent.includes('selected record')).length,1);
assert(all.some(n=>n.textContent.includes('date conflict remains unresolved')));
assert(all.some(n=>n.textContent.includes('annual ranges remain unknown')));
assert.equal(all.find(n=>n.tag==='img').src,'../'+scene.figure_file);
for(const [i,record] of binding.records.entries()){
  const row=all.find(n=>n.dataset.widthId===record.id);assert(row);
  const descendants=nodes(row);
  descendants.find(n=>n.tag==='button').onclick();
  const anchor=descendants.find(n=>n.textContent==='Inspect exact source record');
  const query=JSON.parse(new URL(anchor.href,'https://osw.test/almanac/').searchParams.get('source-q'));
  assert.equal(query.document,scene.bindings_file);assert.equal(query.pointer,'/records/'+i);
}
assert.deepEqual(calls,binding.records.map(r=>['widths',r.id]));
const hidden=new Element('main');window.renderAzores2009Section(hidden,scene,'current:unrelated');
window.renderAzores2009Section(hidden,null);assert.equal(hidden.children.length,0);
const linkRoot=new Element('main');window.renderAzores2009Section(linkRoot,scene,binding.records[0].id);
const widthLink=nodes(linkRoot).find(n=>n.tag==='a'&&n.textContent==='Inspect width record');
assert.equal(new URL(widthLink.href,'https://osw.test/almanac/').searchParams.get('phase'),binding.records[0].id);
for(const html of ['query','seasons','reference-routes']){
  const raw=fs.readFileSync('almanac/'+html+'.html','utf8');assert(raw.includes('azores-2009-section.js?v=1'));
}
console.log('PASS: selected owner, record navigation, source pointers, inspect callbacks, unresolved scope and script inclusion');
