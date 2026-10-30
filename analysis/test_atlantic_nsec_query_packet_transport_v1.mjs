// Synthetic bytes only: never open a local packet, index or WASM binary.
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import vm from 'node:vm';
const encoder=new TextEncoder(),sha=b=>crypto.createHash('sha256').update(new Uint8Array(b)).digest('hex');
const logical=encoder.encode(JSON.stringify({schema:'osw.query-bundle.v1',manifest:{},collections:{objects:[{id:'a',label:'é → Ω'}]}}));
let parses=0;
const context={TextDecoder,Uint8Array,Number,Array,Error,JSON:{parse:raw=>{
  parses++;assert.notEqual(raw,new TextDecoder().decode(logical),'The complete assembled payload must be parsed by Rust, not allocated again in JavaScript');
  return JSON.parse(raw);
}}};
vm.runInNewContext(fs.readFileSync('almanac/query-packet.js','utf8'),context);
function fixture(bytes=logical){
  const pin=sha(bytes),path=`query-parts/000000-${pin}.bin`;
  const packet={schema:'osw.query-packet.v1',logical_schema:'osw.query-bundle.v1',hash_algorithm:'sha256',part_byte_limit:16*1024*1024,
    logical_sha256:pin,logical_byte_length:bytes.length,parts:[{index:0,path,sha256:pin,byte_length:bytes.length}]};
  return {packet,pins:{['almanac/'+path]:pin},raw:()=>encoder.encode(JSON.stringify(packet)),fetch:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)};
}
let f=fixture();const result=await context.assembleQueryPacket(f.raw(),f.fetch,sha,f.pins);
assert.deepEqual(new Uint8Array(result),logical);assert.equal(parses,1);
for(const variant of ['pin','traversal','schema','length']){
  f=fixture();let fetches=0;
  if(variant==='pin')f.pins={};
  if(variant==='traversal')f.packet.parts[0].path='../outside.bin';
  if(variant==='schema')f.packet.logical_schema='wrong';
  if(variant==='length')f.packet.parts[0].byte_length++;
  await assert.rejects(()=>context.assembleQueryPacket(f.raw(),async()=>{fetches++;return f.fetch();},sha,f.pins));
  assert.equal(fetches,0);
}
f=fixture();await assert.rejects(()=>context.assembleQueryPacket(f.raw(),async()=>{throw Error('HTTP 404');},sha,f.pins),/HTTP 404/);
f=fixture();const changed=logical.slice();changed[0]^=1;
await assert.rejects(()=>context.assembleQueryPacket(f.raw(),async()=>changed,sha,f.pins),/Changed query packet part/);
f=fixture();f.packet.logical_sha256='0'.repeat(64);
await assert.rejects(()=>context.assembleQueryPacket(f.raw(),f.fetch,sha,f.pins),/Changed logical query bundle/);
// Payload content is deliberately deferred to the unchanged real Rust parser.
// Actual browser cases prove these bytes cannot produce successful engine loads.
for(const bytes of [encoder.encode('{"schema":"wrong"}'),encoder.encode('{malformed'),new Uint8Array([255,254])]){
  f=fixture(bytes);assert.deepEqual(new Uint8Array(await context.assembleQueryPacket(f.raw(),f.fetch,sha,f.pins)),bytes);
}
console.log('PASS exact bytes and hashes, pre-fetch refusal, no duplicate logical JSON tree; malformed payload acceptance remains guarded by actual Rust browser tests');
