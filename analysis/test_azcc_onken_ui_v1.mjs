import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element{constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.style={};}append(el){this.children.push(el);}setAttribute(k,v){this.attributes[k]=String(v);}}
const document={createElement:t=>new Element(t),createElementNS:(_ns,t)=>new Element(t)};
const context={window:{},document,location:{href:''}};
vm.runInNewContext(fs.readFileSync('almanac/current-dimension-evidence.js','utf8'),context);
const contract=JSON.parse(fs.readFileSync('research/azcc-onken-query-contract-v1.json','utf8'));
const scene={kind:'published_current_dimension_evidence',title:'Azores Countercurrent: separately scoped width evidence',
  scope:'Distinct110km2009 section and200km historical regional interpretation; not a seasonal range.',
  definition:'Historical dates, fixed layer and edges unknown. No alongflow length.',entity_id:contract.final_owner.id,
  width_records:[...contract.prior_records.widths,contract.width_record],event_records:[],source_url:contract.new_source.url,
  source_label:'Original historical study',figure:'figures/onken-azcc-1993-evidence-compact-v1.svg',
  width_source_links:{'azores-countercurrent-2009-section-width':{source_file:'research/azores-2009-section-record-bindings-v1.json',source_pointer:'/records/1'}}};
const all=n=>[n,...n.children.flatMap(all)],text=n=>all(n).map(n=>n.textContent||'').join(' ');
const root=new Element('div'),calls=[];
context.window.renderCurrentDimensionEvidence(root,scene,(collection,id)=>calls.push([collection,id]),{collapsed:true});
const nodes=all(root),cards=nodes.filter(n=>n.attributes['data-dimension-width-id']);assert.equal(cards.length,2);
assert.match(text(cards[0]),/About 110 km/);assert.match(text(cards[1]),/About 200 km/);
for(const card of cards){assert.match(text(card),/Width scale: 0–200 km/);assert.match(text(card),/Seasonal width range: Unknown. Numerical uncertainty: Unknown/);}
const marks=cards.map(card=>all(card).find(n=>n.tag==='circle'));
assert(Math.abs(Number(marks[0].attributes.cx)-163.8)<1e-10);assert.equal(Number(marks[1].attributes.cx),288);
assert.equal(nodes.filter(n=>n.tag==='line'&&n.attributes['stroke-width']==='10').length,0);
assert.equal(nodes.filter(n=>n.attributes['data-flow-event-id']).length,0);
const summary=nodes.find(n=>n.tag==='summary');assert.equal(summary.textContent,'2 regional width summaries');
assert.equal(nodes.find(n=>n.tag==='details').attributes.open,undefined);
const sources=nodes.filter(n=>n.tag==='a'&&n.textContent==='Source evidence record');assert.equal(sources.length,2);
const requests=sources.map(n=>JSON.parse(new URL(n.href,'https://example.test/almanac/').searchParams.get('source-q')));
assert.equal(requests[0].document,'research/azores-2009-section-record-bindings-v1.json');assert.equal(requests[0].pointer,'/records/1');
assert.equal(requests[1].document,'research/onken-azcc-1993-source-facts-v1.json');assert.equal(requests[1].pointer,'/cited_width_summary');
assert.equal(nodes.find(n=>n.tag==='a'&&n.textContent==='Original historical study').href,contract.new_source.url);
for(const button of nodes.filter(n=>n.tag==='button'))button.onclick();
assert.deepEqual(calls,scene.width_records.map(r=>['widths',r.id]));
const filtered=new Element('div');context.window.renderCurrentDimensionEvidence(filtered,{...scene,width_records:[contract.width_record]},()=>{});
assert.equal(all(filtered).filter(n=>n.attributes['data-dimension-width-id']).length,1);
assert(!text(filtered).includes('About 110 km'));
for(const path of ['almanac/query.html','almanac/reference-routes.html','almanac/seasons.html']){
  assert(/<script[^>]+src="current-dimension-evidence\.js\?v=[^"]+"/.test(fs.readFileSync(path,'utf8')));
}
assert.deepEqual(scene.width_records,[...contract.prior_records.widths,contract.width_record]);
console.log('PASS: two separate widths on a common scale, original source pointers, filtered cards, unknown ranges, no event promotion and explicit historical-study link. Actual browser layout pending.');
