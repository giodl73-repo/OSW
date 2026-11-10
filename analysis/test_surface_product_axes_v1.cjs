// Pure renderer tests: compact derived contract only; no browser or engine packet.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const contract=JSON.parse(fs.readFileSync(path.join(root,'research/pacific-nec-product-axis-query-contract-v1.json'),'utf8'));
class Element {
  constructor(tag){this.tagName=tag;this.children=[];this.dataset={};this.attributes={};this.style={};this.events={};this.value='';this.isConnected=true;this.classList={add(){},toggle(){}};}
  append(...nodes){this.children.push(...nodes);for(const n of nodes)n.parentElement=this;}
  replaceChildren(...nodes){this.children=[];this.append(...nodes);}
  setAttribute(k,v){this.attributes[k]=String(v);}
  getBoundingClientRect(){return {width:320};}
  addEventListener(k,fn){(this.events[k]||=[]).push(fn);}
  fire(k,event={}){for(const fn of this.events[k]||[])fn(event);}
}
function setup(){
  const listeners=new Map(),intervals=new Map();let seq=0;
  const document={createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t),hidden:false,addEventListener:(k,f)=>listeners.set(f,k),removeEventListener:(k,f)=>listeners.delete(f)};
  const window={};const context=vm.createContext({window,document,location:{href:''},setInterval:f=>{intervals.set(++seq,f);return seq;},clearInterval:i=>intervals.delete(i),matchMedia:()=>({matches:false,addEventListener(){},removeEventListener(){}})});
  vm.runInContext(fs.readFileSync(path.join(root,'almanac/surface-product-axes.js'),'utf8'),context);
  return {window,document,listeners,intervals,parent:new Element('main')};
}
function scene(){return {kind:'surface_product_axis_diagnostics',title:'Pacific NEC',entity_id:'current:pacific-north-equatorial',scope:'Experimental',series:contract.collections_added.current_axis_series,readings:contract.collections_added.current_axis_readings,section_spans:contract.collections_added.current_axis_section_spans,sources:contract.new_sources};}
function all(node,tag){return node.children.flatMap(c=>[...(c.tagName===tag?[c]:[]),...all(c,tag)]);}
test('all 36 native paths retain real dateline splits and distinct analysis windows',()=>{
  const {window}=setup(),H=window.oswSurfaceProductAxes,s=scene();
  assert.equal(H.paths(s).length,36);
  assert.equal(H.selection(s).month,1);
  assert.equal(H.windowLabel(H.selection(s)),'8–18°N');
  for(const r of H.paths(s)){
    assert.equal(H.segments(r).length,2);
    for(const segment of H.segments(r))for(let i=1;i<segment.length;i++)assert.ok(Math.abs(segment[i][0]-segment[i-1][0])<1);
    const url=new URL(H.atlasUrl(r),'https://osw.test/');assert.equal(url.searchParams.get('atlas-product-reading'),r.id);
  }
  assert.equal(H.km(null),'Withheld');assert.equal(H.km(0),'0 km');
});
test('global paths use independent move commands across the seam and select the exact record',()=>{
  const {window}=setup(),H=window.oswSurfaceProductAxes;let selected;
  const drawn=H.draw({scene:scene(),currentId:'current:pacific-north-equatorial',parent:new Element('g'),make:(tag,attrs,p)=>{const el=new Element(tag);Object.assign(el.attributes,attrs);p.append(el);return el;},pathData:coordinates=>'M'+coordinates.map(p=>p.join(',')).join('L'),interactive:(el,label,fn)=>{el.activate=fn;el.label=label;},onSelect:r=>selected=r});
  assert.equal(drawn.length,36);assert.equal(drawn.filter(x=>x.line.style.display==='').length,1);
  for(const {line} of drawn)assert.equal((line.attributes.d.match(/M/g)||[]).length,2);
  drawn[23].line.activate();assert.equal(selected.id,drawn[23].row.id);
});
test('monthly controls, exact selected initial path, stepping and cleanup work without synthesizing months',()=>{
  const {window,parent,intervals,listeners,document}=setup(),s=scene(),changes=[];
  const chosen=s.readings.find(r=>r.month===7&&r.window_deg_north.join(',')==='7,19');
  const cleanup=window.renderSurfaceProductAxes(parent,s,()=>{},{readingId:chosen.id,onSelect:r=>changes.push(r.id)});
  const [windows,months]=all(parent,'select');assert.equal(windows.value,chosen.series_id);assert.equal(months.value,chosen.id);
  const play=all(parent,'button').find(x=>x.textContent==='Play dated months');play.fire('click');assert.equal(intervals.size,1);
  [...intervals.values()][0]();assert.equal(changes.at(-1),s.readings.find(r=>r.month===8&&r.series_id===chosen.series_id).id);
  document.hidden=true;for(const [fn,event]of listeners)if(event==='visibilitychange')fn();assert.equal(intervals.size,0);
  cleanup();assert.equal(listeners.size,0);
});
test('a filtered reading scene cannot leak other months or windows',()=>{
  const {window,parent}=setup(),s=scene(),chosen=s.readings[5];s.readings=[chosen];s.series=s.series.filter(r=>r.id===chosen.series_id);s.section_spans=[];s.selected_collection='current_axis_readings';s.selected_records=[chosen];
  const cleanup=window.renderSurfaceProductAxes(parent,s,()=>{});const selects=all(parent,'select');assert.equal(selects[0].children.length,1);assert.equal(selects[1].children.length,1);assert.equal(selects[1].value,chosen.id);
  for(const svg of all(parent,'svg'))assert.ok(!svg.children.some(x=>String(x.attributes?.cy)==='NaN'));
  cleanup();
});
test('scenario failures retain nulls and all matching rows without invented nominal geometry',()=>{
  const {window,parent}=setup(),s=scene();s.readings=[];s.section_spans=[];s.selected_collection='current_axis_scenarios';s.selected_records=contract.collections_added.current_axis_scenarios;
  const cleanup=window.renderSurfaceProductAxes(parent,s,()=>{});assert.equal(all(parent,'svg').length,0);
  const detail=all(parent,'details').find(d=>d.children[0].textContent.startsWith('Matching operator scenarios'));detail.open=true;detail.fire('toggle');
  assert.equal(all(detail,'tr').length,1333);const values=all(detail,'td').map(td=>td.textContent||'');assert.equal(values.filter(v=>v.endsWith(': Withheld')).length,85);
  assert.ok(values.some(v=>v.includes('fixed_path_thinned_geodesic_representation_length')));
  cleanup();
});
test('section-only scenes keep the censored span withheld and do not supply map paths',()=>{
  const {window,parent}=setup(),s=scene();s.readings=[];s.selected_collection='current_axis_section_spans';s.selected_records=s.section_spans;
  const cleanup=window.renderSurfaceProductAxes(parent,s,()=>{});assert.equal(all(parent,'svg').length,0);
  const detail=all(parent,'details').find(d=>d.children[0].textContent.startsWith('Fixed-meridian'));detail.open=true;detail.fire('toggle');
  assert.equal(all(detail,'tr').length,37);assert.equal(all(detail,'td').filter(td=>td.textContent==='Withheld').length,1);
  cleanup();
});
