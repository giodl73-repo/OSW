import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {webcrypto} from 'node:crypto';
import vm from 'node:vm';

const digest=async bytes=>Buffer.from(await webcrypto.subtle.digest('SHA-256',bytes)).toString('hex');
const bytes=text=>new TextEncoder().encode(text);
const binary=bytes('synthetic verified binary'),bundle=bytes('{"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":[]}}');
const binaryPin=await digest(binary),bundlePin=await digest(bundle);
const part='query-parts/000000-'+bundlePin+'.bin';
const packet=bytes(JSON.stringify({schema:'osw.query-packet.v1',logical_schema:'osw.query-bundle.v1',hash_algorithm:'sha256',part_byte_limit:16*1024*1024,logical_sha256:bundlePin,logical_byte_length:bundle.length,parts:[{index:0,path:part,sha256:bundlePin,byte_length:bundle.length}]}));
const manifest={schema:'osw.query-engine-manifest.v1',abi_version:1,sha256:{'almanac/query-engine.wasm':binaryPin,'almanac/query-data.json':await digest(packet),['almanac/'+part]:bundlePin}};

async function scenario({progress=false,badBinary=false,badPart=false,compileError=false,rustError=false}={}){
  const messages=[],events=[];let compiled=false,packetVerified=false,context;
  const memory={buffer:new ArrayBuffer(8192)};let responseLength=0;
  const output=value=>{const raw=bytes(JSON.stringify(value));new Uint8Array(memory.buffer,4096,raw.length).set(raw);responseLength=raw.length;};
  const exports={memory,osw_alloc:()=>0,osw_dealloc:()=>{},osw_result_ptr:()=>4096,osw_result_len:()=>responseLength,
    osw_load:(_ptr,length)=>{events.push('rust-load');assert.equal(length,bundle.length);assert.deepEqual(Buffer.from(memory.buffer,0,length),Buffer.from(bundle));output(rustError?{ok:false,error:'Invalid bundle JSON: synthetic Rust refusal'}:{ok:true,bundle_sha256:bundlePin});},
    osw_metadata:()=>output({ok:true,bundle_sha256:bundlePin}),osw_workspace_export:()=>output({ok:true,revision:0})};
  const fetch=async path=>({ok:true,json:async()=>manifest,arrayBuffer:async()=>{
    if(path==='query-engine.wasm')return (badBinary?bytes('changed'):binary).slice().buffer;
    if(path==='query-data.json')return packet.slice().buffer;
    assert.equal(path,part);events.push('part-bytes');assert.equal(compiled,true,'Compilation must start while the packet fetch is pending');
    return (badPart?bytes('changed'):bundle).slice().buffer;
  }});
  context=vm.createContext({TextEncoder,TextDecoder,Uint8Array,ArrayBuffer,performance,crypto:webcrypto,fetch,
    indexedDB:{open:()=>{const request={error:'synthetic storage unavailable'};queueMicrotask(()=>request.onerror());return request;}},
    self:{postMessage:value=>messages.push(value)},WebAssembly:{
      compile:async raw=>{events.push('compile');assert.deepEqual(Buffer.from(raw),Buffer.from(binary));compiled=true;if(compileError)throw Error('Synthetic compile failure');return {verifiedModule:true};},
      instantiate:async module=>{events.push('instantiate');assert.equal(module.verifiedModule,true);assert.equal(packetVerified,true,'Do not instantiate before complete packet verification');return {exports};}
    },importScripts:path=>{assert.equal(path,'query-packet.js');vm.runInContext(readFileSync('almanac/query-packet.js','utf8'),context);}});
  vm.runInContext(readFileSync('almanac/query-worker.js','utf8'),context);
  const assemble=context.assembleQueryPacket;
  context.assembleQueryPacket=async(...args)=>{const result=await assemble(...args);packetVerified=true;return result;};
  await context.self.onmessage({data:{id:7,action:'load',value:{report_progress:progress}}});
  // Allow the other Promise.all branch to settle after an intentional refusal.
  await new Promise(resolve=>setImmediate(resolve));
  return {messages,events};
}

const normal=await scenario();assert.equal(normal.messages.length,1);assert.equal(normal.messages[0].result.ok,true);assert.deepEqual(normal.events,['compile','part-bytes','instantiate','rust-load']);
const diagnostic=await scenario({progress:true});assert.equal(diagnostic.messages.at(-1).result.ok,true);
assert.deepEqual(diagnostic.messages.filter(r=>r.progress).map(r=>r.progress.phase),['runtime-files','packet-and-compile','instantiate','rust-load','workspace','metadata','ready']);
for(const row of diagnostic.messages.filter(r=>r.progress)){assert.equal(row.id,7);assert.ok(row.progress.elapsed_ms>=0);assert.ok(row.progress.completed_phases.every(p=>p.elapsed_ms>=0));assert.equal(row.result,undefined);}
for(const [options,error] of [[{badBinary:true},'Changed almanac/query-engine.wasm'],[{badPart:true},'Changed query packet part'],[{compileError:true},'Synthetic compile failure']]){
  const failed=await scenario(options);assert.equal(failed.messages.at(-1).result.ok,false);assert.ok(failed.messages.at(-1).result.error.includes(error));assert.ok(!failed.events.includes('instantiate'));assert.ok(!failed.events.includes('rust-load'));
}
const rust=await scenario({rustError:true});assert.equal(rust.messages.at(-1).result.ok,false);assert.match(rust.messages.at(-1).result.error,/Invalid bundle JSON/);
console.log('PASS concurrent verified compilation/packet assembly, opt-in phases, exact Rust input and fail-before-use guards; no real payload or WASM read');
