// Check both shared tools reach argument validation only for explicit cloud scopes.
// No packet, index or WASM paths are supplied by these fixtures.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
const keys=['OSW_DIMOUNE_WIDTH_DELIVERY_V1','OSW_ATLANTIC_NEC_BANDS_DELIVERY_V1','OSW_CHARACTERISTIC_VELOCITIES_DELIVERY_V1','OSW_PACIFIC_SEC_JET_WIDTHS_DELIVERY_V1','OSW_CURRENT_CORE_DIMENSIONS_DELIVERY_V1'];
const clean={...process.env,GITHUB_ACTIONS:'true',GITHUB_REPOSITORY:'giodl73-repo/OSW',GITHUB_REF:'refs/heads/codex/current-measurement-gaps'};
for(const key of keys)delete clean[key];
for(const script of ['analysis/capture_bounded_wasm_responses_v1.mjs','analysis/check_bounded_native_wasm_v1.mjs']){
  for(const key of ['OSW_PACIFIC_SEC_JET_WIDTHS_DELIVERY_V1','OSW_CURRENT_CORE_DIMENSIONS_DELIVERY_V1']){
    const result=spawnSync(process.execPath,[script],{env:{...clean,[key]:'1'},encoding:'utf8'});
    assert.notEqual(result.status,0);assert(result.stderr.includes('0 !== 6'),`${script}/${key}: must reach argument-count gate before any file access`);
  }
  for(const bad of [clean,{...clean,OSW_CURRENT_CORE_DIMENSIONS_DELIVERY_V1:'0'},{...clean,OSW_CURRENT_CORE_DIMENSIONS_DELIVERY_V1:'1',GITHUB_REPOSITORY:'wrong/repo'},{...clean,OSW_CURRENT_CORE_DIMENSIONS_DELIVERY_V1:'1',GITHUB_REF:'refs/heads/main'},{...clean,OSW_CURRENT_CORE_DIMENSIONS_DELIVERY_V1:'1',GITHUB_ACTIONS:'false'}]){
    const result=spawnSync(process.execPath,[script],{env:bad,encoding:'utf8'});
    assert.notEqual(result.status,0);assert(!result.stderr.includes('0 !== 6'),`${script}: invalid cloud identity must refuse before argument or file reads`);
  }
}
const workflow=fs.readFileSync('.github/workflows/current-core-dimensions-delivery-v1.yml','utf8');
assert(workflow.includes('OSW_CURRENT_CORE_DIMENSIONS_DELIVERY_V1: "1"'));
assert(workflow.includes('node analysis/test_current_core_dimensions_capture_scope_v1.mjs'));
console.log('PASS both explicit delivery scopes reach pre-I/O argument gate; unscoped/wrong cloud identities refuse; workflow matches tools');
