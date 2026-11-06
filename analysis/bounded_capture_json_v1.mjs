// Preserve one complete engine JSON response without retaining earlier responses.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
export function writeCapturedJson(directory,filename,raw,maximumBytes){
  assert.match(filename,/^capture-(main|index)-(metadata|[0-9]+)\.response\.json$/);
  assert.equal(typeof raw,'string');
  assert(Number.isSafeInteger(maximumBytes)&&maximumBytes>0);
  const bytes=Buffer.from(raw,'utf8');
  assert(bytes.length>0&&bytes.length<=maximumBytes);
  assert.equal(JSON.parse(raw).ok,true);
  fs.writeFileSync(path.join(directory,filename),bytes,{flag:'wx'});
  return {file:filename,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')};
}
