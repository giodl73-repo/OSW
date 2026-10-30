import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const window={};
vm.runInNewContext(fs.readFileSync('almanac/dashboard-evidence-schema.js','utf8'),{window});
const schema=window.oswDashboardEvidenceSchema;
const contract=JSON.parse(fs.readFileSync('research/richardson-walsh-1986-characteristic-velocity-query-contract-v1.json','utf8'));
const body=fs.readFileSync('almanac/dashboard.js','utf8');
const labels=vm.runInNewContext('('+body.match(/const labels = (\{[^;]+\});/)[1]+')');
for(const prior of Object.values(contract.prior_owners)) {
  assert(schema.validCapabilities(prior.objects[0].capabilities,labels,{}));
}
for(const row of Object.values(contract.final_objects)) {
  assert(schema.validCapabilities(row.capabilities,labels,{}));
}
const previous=structuredClone(Object.values(contract.prior_owners)[0].objects[0].capabilities);
for(const value of [undefined,null,'1',-1,1.5,NaN,Infinity]) {
  assert.equal(schema.validCapabilities({...previous,characteristic_velocity:value},labels,{}),false);
}
assert(schema.validCapabilities({...previous,characteristic_velocity:0},labels,{}));
delete previous.scoped_width;
assert.equal(schema.validCapabilities(previous,labels,{}),false);
const html=fs.readFileSync('almanac/dashboard.html','utf8');
assert(/dashboard-evidence-schema\.js\?v=[^"\s]+/.test(html));
assert(html.indexOf('dashboard-evidence-schema.js?')<html.indexOf('dashboard.js?'));
console.log('PASS all ten prior owners/families and eight updated owners; absent velocity allowed, malformed present velocity and missing required width refused.');
