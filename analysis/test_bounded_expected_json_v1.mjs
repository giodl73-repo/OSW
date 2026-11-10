import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {readExpectedJson} from './bounded_expected_json_v1.mjs';
const directory=fs.mkdtempSync(path.join(os.tmpdir(),'osw-expected-json-'));
try{
  const value='{"text":"été 海 \\n","large_integer":9007199254740993}',raw=Buffer.from(value);
  const descriptor={file:'compare-main-1.expected.json',bytes:raw.length,sha256:crypto.createHash('sha256').update(raw).digest('hex')};
  fs.writeFileSync(path.join(directory,descriptor.file),raw);
  assert.equal(readExpectedJson(directory,descriptor,raw.length),value);
  assert.equal(readExpectedJson(directory,descriptor,raw.length),value);
  for(const change of [{file:'../compare-main-1.expected.json'},{bytes:raw.length+1},{sha256:'0'.repeat(64)}]){
    assert.throws(()=>readExpectedJson(directory,{...descriptor,...change},raw.length));
  }
  assert.throws(()=>readExpectedJson(directory,descriptor,raw.length-1));
  fs.writeFileSync(path.join(directory,descriptor.file),Buffer.from('changed'));
  assert.throws(()=>readExpectedJson(directory,descriptor,raw.length));
  console.log('PASS: exact UTF-8 and large-integer bytes, repeatability, size/hash guards and path confinement.');
}finally{
  const file=path.join(directory,'compare-main-1.expected.json');
  if(fs.existsSync(file))fs.unlinkSync(file);
  fs.rmdirSync(directory);
}
