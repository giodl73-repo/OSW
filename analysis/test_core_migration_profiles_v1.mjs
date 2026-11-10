import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Node {
  constructor(tag){this.tagName=tag;this.children=[];this.attrs={};this.events={};this.textContent='';this.classList={add:()=>{}};}
  append(child){this.children.push(child);}
  setAttribute(key,value){this.attrs[key]=String(value);}
  addEventListener(event,handler){this.events[event]=handler;}
}
const document={createElement:tag=>new Node(tag),createElementNS:(_,tag)=>new Node(tag)};
const context={document,window:{},location:{}};
vm.runInNewContext(fs.readFileSync('almanac/core-migration-profiles.js','utf8'),context);
const contract=JSON.parse(fs.readFileSync('research/current-reference-profile-batch-query-contract-v1.json','utf8'));
vm.runInNewContext(fs.readFileSync('almanac/dashboard-evidence-schema.js','utf8'),context);
const dashboard=fs.readFileSync('almanac/dashboard.js','utf8');
const labels=vm.runInNewContext('('+dashboard.match(/const labels = (\{[^;]+\});/)[1]+')');
const schema=context.window.oswDashboardEvidenceSchema;
for(const prior of Object.values(contract.prior_owners))assert(schema.validCapabilities(prior.objects[0].capabilities,labels,{}));
for(const final of Object.values(contract.final_objects))assert(schema.validCapabilities(final.capabilities,labels,{}));
const capabilities=contract.final_objects['current:pacific-south-equatorial'].capabilities;
for(const bad of [null,undefined,-1,1.5,'24'])assert.equal(schema.validCapabilities({...capabilities,core_migration_profile:bad},labels,{}),false);
assert.match(dashboard,/\[\.\.\.Object\.keys\(contextMetrics\),'core_migration_profile'\]/);
const row=contract.records.find(r=>r.section_longitude_degrees_east===-160&&r.sampling_depth_m===500);
const root=new Node('div'),calls=[];
context.window.renderCoreMigrationProfiles(root,{kind:'published_core_migration_profiles',records:[row],scope:row.scope,source_url:row.source_url},(...args)=>calls.push(args));
function all(node){return [node,...node.children.flatMap(all)];}
const marks=all(root).filter(n=>n.attrs['data-core-profile-id']);
assert.equal(marks.length,1,'a filtered scene must not invent other depth readings');
assert.equal(marks[0].attrs['data-core-profile-id'],row.id);
let prevented=false;marks[0].events.keydown({key:'Enter',preventDefault(){prevented=true;}});
assert.equal(prevented,true);assert.deepEqual(calls,[['current_core_migration_profiles',row.id]]);
const text=all(root).map(n=>n.textContent).join(' ');
assert.match(text,/includes zero/);assert.match(text,/not a confidence interval/);assert.match(text,/0\.00–0\.04/);
const empty=new Node('div');assert.equal(context.window.renderCoreMigrationProfiles(empty,null),null);assert.equal(empty.children.length,0);
console.log('PASS filtered source-profile marks, keyboard Inspect, zero-touching allowance and no-data rendering');
