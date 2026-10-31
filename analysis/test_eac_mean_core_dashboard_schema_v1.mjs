import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const window={};vm.runInNewContext(fs.readFileSync('almanac/dashboard-evidence-schema.js','utf8'),{window});
const schema=window.oswDashboardEvidenceSchema;
const contract=JSON.parse(fs.readFileSync('research/eac-mean-core-query-contract-v1.json','utf8'));
const groups=Object.fromEntries(Object.keys(contract.dashboard_after.section_fingerprints).map(k=>[k,k]));
const labels=Object.fromEntries(Object.keys(contract.dashboard_after.capabilities).map(k=>[k,k]));
const before=contract.dashboard_before,after=contract.dashboard_after;
for(const row of [before,after]){
  assert(schema.validFingerprints(row.section_fingerprints,groups));
  assert(schema.validCapabilities(row.capabilities,labels,{}));
}
const unrelated=structuredClone(before);unrelated.id='current:unrelated';
assert(schema.validFingerprints(unrelated.section_fingerprints,groups));
assert(schema.validCapabilities(unrelated.capabilities,labels,{}));
for(const value of [undefined,null,5,{},false]){
  const changed={...before.section_fingerprints,mean_model_core_sections:value};
  assert.equal(schema.validFingerprints(changed,groups),false);
}
for(const value of [undefined,null,'5',-1,1.5,NaN]){
  assert.equal(schema.validCapabilities({...before.capabilities,reported_model_core_sections:value},labels,{}),false);
}
assert(schema.validCapabilities({...before.capabilities,reported_model_core_sections:0},labels,{}));
const missing=structuredClone(before.section_fingerprints);delete missing.identity;
assert.equal(schema.validFingerprints(missing,groups),false);
const missingCap=structuredClone(before.capabilities);delete missingCap.scoped_width;
assert.equal(schema.validCapabilities(missingCap,labels,{}),false);
const body=fs.readFileSync('almanac/dashboard.js','utf8');
assert(body.includes('!window.oswDashboardEvidenceSchema.validFingerprints(r.section_fingerprints,groupLabels)'));
assert(body.includes('!window.oswDashboardEvidenceSchema.validCapabilities(r.capabilities,labels,contextMetrics)'));
const html=fs.readFileSync('almanac/dashboard.html','utf8');
assert(html.indexOf('dashboard-evidence-schema.js?')>=0);
assert(html.indexOf('dashboard-evidence-schema.js?')<html.indexOf('dashboard.js?'));
assert.equal(Object.hasOwn(before.capabilities,'reported_model_core_sections'),false);
assert.equal(after.capabilities.reported_model_core_sections,5);
console.log('PASS: prior/unrelated/EAC dashboard entries accepted; absent optional fields allowed; malformed present values and missing required fields refused; helper loaded before consumer.');
