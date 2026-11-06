'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const contract=JSON.parse(fs.readFileSync('research/pacific-nec-nominal-width-query-contract-v1.json','utf8'));
const identities=JSON.parse(fs.readFileSync('research/equatorial-basin-identity-query-contract-v3.json','utf8'));
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.dataset={};this.style={};this.events={};}
  append(...items){this.children.push(...items);}
  setAttribute(k,v){this.attributes[k]=String(v);}
  addEventListener(k,v){this.events[k]=v;}
}
const all=root=>[root,...root.children.flatMap(all)];
const text=root=>all(root).map(n=>n.textContent||'').join(' ');
function setup(){
  const context={window:{},document:{createElement:t=>new Element(t),createElementNS:(_ns,t)=>new Element(t),createTextNode:t=>({tag:'#text',textContent:t,children:[]})},location:{href:''}};
  for(const file of ['current-dimension-evidence.js','equatorial-basin-identities.js'])vm.runInNewContext(fs.readFileSync('almanac/'+file,'utf8'),context);
  return context;
}
function scene(){return {kind:'published_current_dimension_evidence',title:'Pacific NEC nominal surface width',entity_id:contract.final_owner.id,
  width_records:[contract.width_record],event_records:[],scope:'Regional approximation; no annual range or physical edges.',
  definition:'WGS84 conversion of a nominal8-17N band. Separate JPO7-17N context.',source_url:contract.new_sources[0].url,
  source_label:'Reviewed original project synthesis',figure:contract.width_record.figure};}

test('derived nominal width is accessible and missing ranges stay explicit',()=>{
  const c=setup(),root=new Element('main');c.window.renderCurrentDimensionEvidence(root,scene());
  assert.match(text(root),/About 1,000 km/);
  assert.match(text(root),/Seasonal width range: Unknown. Numerical uncertainty: Unknown/);
  assert.match(text(root),/paired physical edges and annual variability remain unknown/);
  const svg=all(root).find(n=>n.tag==='svg');assert.match(svg.attributes['aria-label'],/Derived nominal regional latitude span/);
  assert.equal(all(root).filter(n=>n.tag==='circle').length,1);
  assert.equal(all(root).filter(n=>n.tag==='line'&&n.attributes['stroke-width']==='10').length,0);
  assert.equal(all(root).filter(n=>n.attributes['data-flow-event-id']).length,0);
});
test('inspection and source evidence point to the exact nominal width',()=>{
  const c=setup(),root=new Element('main'),calls=[];c.window.renderCurrentDimensionEvidence(root,scene(),(...args)=>calls.push(args));
  all(root).find(n=>n.tag==='button').onclick();assert.deepEqual(calls,[['widths',contract.width_record.id]]);
  const source=all(root).find(n=>n.tag==='a'&&n.textContent==='Source evidence record');
  const q=JSON.parse(new URL(source.href,'https://osw.invalid/').searchParams.get('source-q'));
  assert.equal(q.document,'research/qiu-pacific-nec-2015-source-facts-v1.json');assert.equal(q.pointer,'/nominal_surface_width');
  assert.equal(all(root).find(n=>n.textContent==='Reviewed original project synthesis').href,contract.new_sources[0].url);
});
test('rendering neither mutates the evidence nor invents a dated series',()=>{
  const c=setup(),root=new Element('main'),s=scene(),before=JSON.stringify(s);
  c.window.renderCurrentDimensionEvidence(root,s,()=>{},{collapsed:true});assert.equal(JSON.stringify(s),before);
  assert.equal(all(root).filter(n=>n.tag==='summary').length,1);assert(!text(root).includes('2014-06-01'));
  assert.equal(all(root).filter(n=>n.tag==='ol').length,0);
});
test('family context links width evidence only on the Pacific member',()=>{
  const c=setup(),root=new Element('main');
  const rows=identities.additions.current_basin_memberships.filter(r=>r.family_entity_id==='current:north-equatorial');
  const members=rows.map(r=>({membership_record:r,entity_id:r.entity_id,label:identities.additions.entities.find(e=>e.id===r.entity_id).label,
    object_url:'object.html?id='+encodeURIComponent(r.entity_id),family_label:'North Equatorial Current',family_url:'object.html?id=current%3Anorth-equatorial',
    ...(r.entity_id===contract.final_owner.id?{nominal_width_evidence:{label:'Nominal regional width: about 1,000 km',query_url:contract.width_query_after_installation,scope:'Annual range and physical edges unknown.'}}:{})}));
  c.window.renderEquatorialBasinIdentities(root,{kind:'equatorial_basin_identity_context',members,scope:'No measurement inheritance.',dimension_status:'Separately sourced nominal width; annual ranges unresolved.'});
  const cards=all(root).filter(n=>n.dataset.entityId);assert.equal(cards.length,2);
  assert(!text(cards.find(n=>n.dataset.entityId==='current:atlantic-north-equatorial')).includes('1,000'));
  const pacific=cards.find(n=>n.dataset.entityId===contract.final_owner.id);
  assert.equal(all(pacific).find(n=>n.textContent==='Nominal regional width: about 1,000 km').href,contract.width_query_after_installation);
});
test('atlas details use unknown labels rather than null or undefined',()=>{
  const c=setup(),code=fs.readFileSync('almanac/atlas-width-evidence.js','utf8');
  for(const name of [...code.matchAll(/window\.(render\w+)\(/g)].map(m=>m[1]))if(!c.window[name])c.window[name]=()=>{};
  vm.runInNewContext(code,c);const root=new Element('main');
  c.window.renderAtlasWidthEvidence(root,{id:contract.final_owner.id},{measurements:[contract.width_record],current_decisions:[]});
  assert.match(text(root),/sampling dates are unresolved/);
  assert.match(text(root),/No reproducible paired-edge rule is recorded/);
  assert(!text(root).includes('Definition: null'));assert(!text(root).includes('undefined'));
});
test('object page loads the evidence renderer before its current view',()=>{
  const html=fs.readFileSync('almanac/object.html','utf8'),js=fs.readFileSync('almanac/object.js','utf8');
  assert(html.includes('current-dimension-evidence.js?v=pacific-nec-1'));
  assert(js.includes('window.renderCurrentDimensionEvidence(identity,window.oswObjectView.current_dimension_evidence_scene)'));
  const c=setup(),root=new Element('main');c.window.renderCurrentDimensionEvidence(root,null);assert.equal(root.children.length,0);
});
