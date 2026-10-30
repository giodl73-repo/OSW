import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {writeCapturedJson} from './bounded_capture_json_v1.mjs';
const directory=fs.mkdtempSync(path.join(os.tmpdir(),'osw-response-capture-'));
try{
  const raw=' {"ok":true,"integer":9007199254740993,"label":"é → Ω","nested":{"x":1.2300}}\n';
  const descriptor=writeCapturedJson(directory,'capture-main-1.response.json',raw,1024);
  assert.equal(fs.readFileSync(path.join(directory,descriptor.file),'utf8'),raw);
  assert.equal(descriptor.bytes,Buffer.byteLength(raw));
  assert.equal(descriptor.sha256,crypto.createHash('sha256').update(raw).digest('hex'));
  assert.throws(()=>writeCapturedJson(directory,descriptor.file,raw,1024));
  for(const name of ['../escape.json','capture-main-1.expected.json','/absolute.json'])
    assert.throws(()=>writeCapturedJson(directory,name,raw,1024));
  for(const value of ['{"ok":false}','not json',''])
    assert.throws(()=>writeCapturedJson(directory,'capture-main-2.response.json',value,1024));
  assert.throws(()=>writeCapturedJson(directory,'capture-main-2.response.json',raw,1));
  assert.equal(fs.readdirSync(directory).length,1);
}finally{
  assert(path.resolve(directory).startsWith(path.resolve(os.tmpdir())+path.sep));
  assert(path.basename(directory).startsWith('osw-response-capture-'));
  fs.rmSync(directory,{recursive:true});
}
const clean={...process.env,GITHUB_ACTIONS:'true',GITHUB_REPOSITORY:'giodl73-repo/OSW',GITHUB_REF:'refs/heads/codex/current-measurement-gaps'};
delete clean.OSW_PACIFIC_SEC_JET_WIDTHS_DELIVERY_V1;
for(const env of [clean,{...clean,OSW_PACIFIC_SEC_JET_WIDTHS_DELIVERY_V1:'1',GITHUB_REPOSITORY:'wrong/repo'}]){
  const result=spawnSync(process.execPath,['analysis/capture_bounded_wasm_responses_v1.mjs'],{env,encoding:'utf8'});
  assert.notEqual(result.status,0);assert(!result.stderr.includes('0 !== 6'));
}
const allowed=spawnSync(process.execPath,['analysis/capture_bounded_wasm_responses_v1.mjs'],{env:{...clean,OSW_PACIFIC_SEC_JET_WIDTHS_DELIVERY_V1:'1'},encoding:'utf8'});
assert.notEqual(allowed.status,0);assert(allowed.stderr.includes('0 !== 6'));
console.log('PASS exact original JSON bytes, bounded confined no-clobber capture and cloud-only scope refusal');
