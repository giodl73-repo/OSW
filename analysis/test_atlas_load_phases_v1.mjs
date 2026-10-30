import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync('almanac/reference-routes.js','utf8');
const block=source.slice(source.indexOf('  window.oswAtlasSourcesReady = new Promise('),source.indexOf('  async function load('));
assert(block.startsWith('  window.oswAtlasSourcesReady = new Promise('));
function fixture(cartography=async()=>({map:true})){
  let now=0,next=1,worker;const timers=new Map(),status={textContent:''},route={dataset:{}};
  const context={window:{createOswCartography:cartography},performance:{now:()=>now},byId:id=>id==='route-status'?route:status,
    Worker:class{constructor(url){this.url=url;this.messages=[];this.terminated=0;worker=this;}postMessage(m){this.messages.push(m);}terminate(){this.terminated++;}},
    setTimeout:(fn,ms)=>{const id=next++;timers.set(id,{fn,deadline:now+ms});return id;},clearTimeout:id=>timers.delete(id)};
  vm.runInNewContext(block,context);const promise=context.window.oswAtlasSourcesReady;promise.catch(()=>{});
  return {context,promise,worker:()=>worker,timers,status,advance:ms=>{now+=ms;for(const [id,t] of [...timers])if(t.deadline<=now){timers.delete(id);t.fn();}},message:async(id,result)=>worker.onmessage({data:{id,result}})};
}
{
 const f=fixture();assert.equal(f.timers.size,1);assert.equal([...f.timers.values()][0].deadline,90000);
 f.advance(80000);await f.message(1,{ok:true});assert.equal(f.context.window.oswAtlasLoadStatus.phase,'atlas');
 assert.equal([...f.timers.values()][0].deadline,170000);assert.equal(f.worker().messages.length,2);
 f.advance(80000);await f.message(2,{ok:true,engine:'rust',engine_binary:'verified binary',sources_json:{'a.json':'{"v":1}'}});
 assert.equal(JSON.stringify(await f.promise),'{"a.json":{"v":1}}');assert.equal(f.context.window.oswAtlasLoadStatus.elapsed_ms,160000);
 assert.equal(f.worker().terminated,1);assert.equal(f.timers.size,0);assert.equal(f.context.window.oswAtlasLoadStatus.phase,'ready');
}
{
 const f=fixture();f.advance(90000);await assert.rejects(f.promise,/Atlas data loading timed out/);
 await f.message(1,{ok:true});assert.equal(f.worker().messages.length,1);assert.equal(f.worker().terminated,1);
 assert.equal(f.context.window.oswAtlasSnapshot,undefined);
}
{
 const f=fixture();await f.message(1,{ok:true});f.advance(90000);await assert.rejects(f.promise,/Atlas map preparation timed out/);
 await f.message(2,{ok:true,engine:'late',sources_json:{}});assert.equal(f.context.window.oswAtlasSnapshot,undefined);
}
{
 let complete;const f=fixture(()=>new Promise(resolve=>{complete=resolve;}));await f.message(1,{ok:true});
 const pending=f.message(2,{ok:true,engine:'late',sources_json:{}});f.advance(90000);complete({map:true});await pending;
 await assert.rejects(f.promise,/Atlas map preparation timed out/);assert.equal(f.context.window.oswAtlasSnapshot,undefined);assert.equal(f.worker().terminated,1);
}
for(const mode of ['bad-id','bad-json','worker-error']){
 const f=fixture();await f.message(1,{ok:true});
 if(mode==='bad-id')await f.message(99,{ok:true});
 else if(mode==='bad-json')await f.message(2,{ok:true,sources_json:{'bad.json':'not json'}});
 else f.worker().onerror();
 await assert.rejects(f.promise);assert.equal(f.worker().terminated,1);assert.equal(f.timers.size,0);
}
console.log('PASS per-phase bounded deadlines, cold-path timing, late-response refusal, worker cleanup and malformed source handling');
