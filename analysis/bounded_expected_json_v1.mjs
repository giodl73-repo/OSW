// Exact expected bytes are read one response at a time, outside escaped fixtures.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export function readExpectedJson(directory, descriptor, maximumBytes){
  assert(descriptor&&typeof descriptor==='object');
  assert.match(descriptor.file,/^compare-(?:main|index)-(?:metadata|[0-9]+)\.expected\.json$/);
  assert.match(descriptor.sha256,/^[0-9a-f]{64}$/);
  assert(Number.isSafeInteger(descriptor.bytes)&&descriptor.bytes>0&&descriptor.bytes<=maximumBytes);
  const base=path.resolve(directory),target=path.resolve(base,descriptor.file);
  assert.equal(path.dirname(target),base);
  const stat=fs.lstatSync(target);assert(stat.isFile()&&!stat.isSymbolicLink());
  assert.equal(stat.size,descriptor.bytes);
  const raw=fs.readFileSync(target);
  assert.equal(crypto.createHash('sha256').update(raw).digest('hex'),descriptor.sha256);
  return new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(raw);
}
