'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const contract = JSON.parse(fs.readFileSync('research/equatorial-basin-identity-query-contract-v2.json'));
const code = fs.readFileSync('almanac/equatorial-basin-identities.js', 'utf8');
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.style = {}; this.dataset = {}; this.attrs = {}; this.events = {}; }
  append(child) { this.children.push(child); }
  setAttribute(k, v) { this.attrs[k] = v; }
  addEventListener(k, v) { this.events[k] = v; }
}
function all(root) { return [root, ...root.children.flatMap(all)]; }
function setup() {
  const window = {};
  vm.runInNewContext(code, {window, document:{createElement:tag => new Element(tag)}});
  return {root:new Element('main'), render:window.renderEquatorialBasinIdentities};
}
function scene(rows, selected) {
  return {
    kind:'equatorial_basin_identity_context', title:'Basin-specific current identities',
    selected_entity_id:selected, scope:'Family relationships do not establish physical connections.',
    dimension_status:'Lengths, widths, observation dates and annual ranges remain unmeasured by this identity admission.',
    source_url:'https://www.tidesandcurrents.noaa.gov/glossary.html',
    figure:'figures/equatorial-basin-identity-members-v1.svg',
    members:rows.map(row => {
      const entity=contract.additions.entities.find(e => e.id===row.entity_id);
      const family=contract.prior_family_records[row.family_entity_id].entities[0];
      return {membership_record:row, entity_id:entity.id,label:entity.label,object_url:entity.almanac_url,
        family_entity_id:family.id,family_label:family.label,family_url:'object.html?id='+encodeURIComponent(family.id)};
    })
  };
}
test('all five identities link to their own current and family, with no invented map', () => {
  const {root,render}=setup(); const s=scene(contract.additions.current_basin_memberships);
  render(root,s);
  const nodes=all(root), cards=nodes.filter(n=>n.dataset.entityId);
  assert.equal(cards.length,5);
  for(const m of s.members) {
    const card=cards.find(n=>n.dataset.entityId===m.entity_id);
    assert.ok(all(card).some(n=>n.tag==='a'&&n.href===m.object_url&&n.textContent===m.label));
    assert.ok(all(card).some(n=>n.tag==='a'&&n.href===m.family_url&&n.textContent===m.family_label));
  }
  assert.equal(nodes.filter(n=>['svg','canvas','img'].includes(n.tag)).length,0);
  assert.ok(nodes.some(n=>n.textContent===s.dimension_status));
});
test('filtered query renders only its matched membership and inspects that exact record', () => {
  const {root,render}=setup(), row=contract.additions.current_basin_memberships[2], calls=[];
  render(root,scene([row]),(...args)=>calls.push(args));
  assert.equal(all(root).filter(n=>n.dataset.entityId).length,1);
  const buttons=all(root).filter(n=>n.tag==='button'); assert.equal(buttons.length,1);
  buttons[0].events.click();
  assert.deepEqual(calls,[['current_basin_memberships',row.id]]);
});
test('family views show their own two or three members and one selected current', () => {
  for(const [family,count] of [['north-equatorial',2],['south-equatorial',3]]) {
    const {root,render}=setup(), rows=contract.additions.current_basin_memberships.filter(r=>r.family_entity_id==='current:'+family);
    render(root,scene(rows,rows[0].entity_id));
    assert.equal(all(root).filter(n=>n.dataset.entityId).length,count);
    const current=all(root).filter(n=>n.attrs['aria-current']==='page'); assert.equal(current.length,1);
    assert.equal(current[0].textContent,contract.additions.entities.find(e=>e.id===rows[0].entity_id).label);
  }
});
test('unrelated or absent scene leaves its parent untouched', () => {
  const {root,render}=setup(); root.append(new Element('p'));
  for(const s of [null,undefined,{kind:'other'}])assert.equal(render(root,s),null);
  assert.equal(root.children.length,1);
});
test('source, complete diagram and canonical membership query remain reachable', () => {
  const {root,render}=setup(); render(root,scene(contract.additions.current_basin_memberships));
  const links=all(root).filter(n=>n.tag==='a');
  assert.ok(links.some(n=>n.href==='https://www.tidesandcurrents.noaa.gov/glossary.html'));
  assert.ok(links.some(n=>n.href==='../figures/equatorial-basin-identity-members-v1.svg'));
  const query=links.find(n=>n.textContent==='Query all basin memberships');
  assert.equal(JSON.parse(new URL(query.href,'https://osw.invalid/').searchParams.get('q')).collection,'current_basin_memberships');
});
test('labels are rendered as text, preserving literal source characters', () => {
  const {root,render}=setup(), s=scene([contract.additions.current_basin_memberships[0]]);
  s.members[0].label='<img src=x onerror=alert(1)>';
  render(root,s); const nodes=all(root);
  assert.ok(nodes.some(n=>n.tag==='a'&&n.textContent===s.members[0].label));
  assert.equal(nodes.filter(n=>n.tag==='img').length,0);
});
