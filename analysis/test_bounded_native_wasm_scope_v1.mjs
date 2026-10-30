import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
const clean={...process.env,GITHUB_ACTIONS:'true',GITHUB_REPOSITORY:'giodl73-repo/OSW',GITHUB_REF:'refs/heads/codex/current-measurement-gaps'};
delete clean.OSW_DIMOUNE_WIDTH_DELIVERY_V1;delete clean.OSW_ATLANTIC_NEC_BANDS_DELIVERY_V1;delete clean.OSW_CHARACTERISTIC_VELOCITIES_DELIVERY_V1;
for(const key of ['OSW_DIMOUNE_WIDTH_DELIVERY_V1','OSW_ATLANTIC_NEC_BANDS_DELIVERY_V1','OSW_CHARACTERISTIC_VELOCITIES_DELIVERY_V1']){
 const result=spawnSync(process.execPath,['analysis/check_bounded_native_wasm_v1.mjs'],{env:{...clean,[key]:'1'},encoding:'utf8'});
 assert.notEqual(result.status,0);assert(result.stderr.includes('0 !== 6'),'Allowed scope must reach argument validation without reading payloads');
}
for(const env of [clean,{...clean,OSW_ATLANTIC_NEC_BANDS_DELIVERY_V1:'1',GITHUB_REPOSITORY:'wrong/repo'}]){
 const result=spawnSync(process.execPath,['analysis/check_bounded_native_wasm_v1.mjs'],{env,encoding:'utf8'});
 assert.notEqual(result.status,0);assert(!result.stderr.includes('0 !== 6'),'Invalid scope must fail before argument/payload processing');
}
console.log('PASS all three explicit cloud scopes and missing/wrong-repository refusal before payload reads');
