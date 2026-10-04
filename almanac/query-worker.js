"use strict";
// All record selection and joins run in Rust WASM, off the rendering thread.
let engine=null;
let database=null,bundleHash=null,workspaceError=null;
let sourceSnapshotBytes=null,rebaseRequest=null;
const encoder=new TextEncoder(),decoder=new TextDecoder();
function invoke(name,value){
  const bytes=value instanceof Uint8Array?value:encoder.encode(JSON.stringify(value));
  const ptr=engine.osw_alloc(bytes.length);
  try{
    new Uint8Array(engine.memory.buffer,ptr,bytes.length).set(bytes);
    engine[name](ptr,bytes.length);
    return JSON.parse(decoder.decode(new Uint8Array(engine.memory.buffer,engine.osw_result_ptr(),engine.osw_result_len())));
  }finally{engine.osw_dealloc(ptr,bytes.length);}
}
async function digest(buffer){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',buffer))].map(b=>b.toString(16).padStart(2,'0')).join('');}
function openDatabase(){return new Promise((resolve,reject)=>{const request=indexedDB.open('osw-query-workspaces',1);request.onupgradeneeded=()=>request.result.createObjectStore('journals');request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(Error('Workspace storage unavailable: '+request.error));request.onblocked=()=>reject(Error('Workspace storage upgrade is blocked by another tab'));});}
function readJournal(){return new Promise((resolve,reject)=>{const tx=database.transaction('journals','readonly');const request=tx.objectStore('journals').get(bundleHash);request.onsuccess=()=>resolve(request.result||{schema:'osw.workspace-journal.v1',bundle_sha256:bundleHash,events:[]});request.onerror=()=>reject(request.error);});}
function readStored(key){return new Promise((resolve,reject)=>{const tx=database.transaction('journals','readonly'),request=tx.objectStore('journals').get(key);request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);});}
function savedJournals(){return new Promise((resolve,reject)=>{const tx=database.transaction('journals','readonly'),request=tx.objectStore('journals').getAll(IDBKeyRange.bound('0'.repeat(64),'f'.repeat(64)));request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);});}
function commitJournal(journal,revision){return new Promise((resolve,reject)=>{
  const tx=database.transaction('journals','readwrite'),store=tx.objectStore('journals'),request=store.get(bundleHash);let reason;
  const abort=message=>{reason=reason||message;try{tx.abort();}catch(_){}};
  request.onsuccess=()=>{const existing=request.result||{events:[]};
    if(existing.events.length!==revision){reason='Workspace revision conflict; reload working records';tx.abort();return;}
    if(JSON.stringify(journal.events.slice(0,revision))!==JSON.stringify(existing.events)){reason='Imported workspace would rewrite existing revision history';tx.abort();return;}
    try{store.put(journal,bundleHash);const snapshot=store.get('~snapshot:'+bundleHash);snapshot.onsuccess=()=>{if(!snapshot.result){try{store.put({kind:'source_snapshot',bundle_sha256:bundleHash,bytes:sourceSnapshotBytes},'~snapshot:'+bundleHash);}catch(e){abort('Source snapshot was not saved: '+e.message);}}};}catch(e){abort('Journal was not saved: '+e.message);}
  };
  tx.oncomplete=()=>resolve();tx.onabort=()=>reject(Error(reason||'Workspace transaction was not saved: '+tx.error));tx.onerror=()=>{};
});}
function exported(name='osw_workspace_export'){engine[name]();return JSON.parse(decoder.decode(new Uint8Array(engine.memory.buffer,engine.osw_result_ptr(),engine.osw_result_len())));}
async function refreshWorkspace(){if(!database)throw Error(workspaceError||'Workspace storage is unavailable');const result=invoke('osw_workspace_import',await readJournal());if(!result.ok)throw Error(result.error);return result;}
async function load(){
  const fetchFile=async path=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw Error(`${path}: HTTP ${r.status}`);return r;};
  const manifest=await (await fetchFile('query-engine.manifest.json')).json();
  if(manifest.schema!=='osw.query-engine-manifest.v1'||manifest.abi_version!==1)throw Error('Unsupported query engine manifest');
  const [wasm,bundle]=await Promise.all(['query-engine.wasm','query-data.json'].map(async p=>(await fetchFile(p)).arrayBuffer()));
  for(const [path,bytes] of [['almanac/query-engine.wasm',wasm],['almanac/query-data.json',bundle]]){
    if(await digest(bytes)!==manifest.sha256[path])throw Error(`Changed ${path}; rebuild the query snapshot and engine manifest`);
  }
  const result=await WebAssembly.instantiate(wasm,{});engine=result.instance.exports;
  let metadata=invoke('osw_load',new Uint8Array(bundle));
  if(!metadata.ok)throw Error(metadata.error);
  bundleHash=metadata.bundle_sha256;
  sourceSnapshotBytes=bundle;
  try{database=await openDatabase();await refreshWorkspace();}catch(error){workspaceError=error.message;database=null;}
  metadata=exported('osw_metadata');
  return {...metadata,workspace:exported(),workspace_available:!!database,workspace_error:workspaceError,wasm_sha256:manifest.sha256['almanac/query-engine.wasm'],bundle_sha256:bundleHash};
}
self.onmessage=async event=>{
  const {id,action,value}=event.data;
  try{
    let result;
    if(action==='load')result=await load();
    else if(!engine)throw Error('Rust engine is not loaded');
    else if(action==='query')result=invoke('osw_query',value);
    else if(action==='query_svg')result=invoke('osw_query_svg',value);
    else if(action==='record')result=invoke('osw_record',value);
    else if(action==='workspace_refresh')result=await refreshWorkspace();
    else if(action==='workspace_export')result=exported();
    else if(action==='workspace_snapshots'){
      if(!database)throw Error(workspaceError||'Workspace storage unavailable');
      result={ok:true,snapshots:(await savedJournals()).map(j=>({bundle_sha256:j.bundle_sha256,revision:j.events.length}))};
    }
    else if(action==='workspace_export_snapshot'){
      if(!database)throw Error(workspaceError||'Workspace storage unavailable');
      const journal=(await savedJournals()).find(j=>j.bundle_sha256===value);
      if(!journal)throw Error('Saved snapshot journal not found');result={ok:true,journal};
    }
    else if(action==='workspace_export_source'){
      if(!database)throw Error(workspaceError||'Workspace storage unavailable');
      const snapshot=await readStored('~snapshot:'+value);if(!snapshot)throw Error('Matching source snapshot is not stored locally');
      result={ok:true,bytes:snapshot.bytes};
    }
    else if(action==='workspace_rebase_preview'){
      if(!database)throw Error(workspaceError||'Workspace storage unavailable');
      const journal=await readStored(value.bundle_sha256);if(!journal)throw Error('Saved journal not found');
      const snapshot=value.old_bundle?{bytes:value.old_bundle}:await readStored('~snapshot:'+value.bundle_sha256);
      if(!snapshot?.bytes)throw Error('Matching old source snapshot is unavailable. Attach its query-data.json to preview a rebase.');
      const loaded=invoke('osw_rebase_source',new Uint8Array(snapshot.bytes));if(!loaded.ok)throw Error(loaded.error);
      if(loaded.bundle_sha256!==journal.bundle_sha256)throw Error('Attached source snapshot does not match the saved journal');
      rebaseRequest={journal,base_revision:exported().revision,transaction_id:crypto.randomUUID(),created_at:new Date().toISOString(),resolutions:{}};
      result=invoke('osw_workspace_rebase',{request:rebaseRequest,prepare:false});
    }
    else if(action==='workspace_rebase_resolve'||action==='workspace_rebase_save'){
      if(!rebaseRequest)throw Error('Preview a rebase before choosing resolutions');
      rebaseRequest={...rebaseRequest,resolutions:value||{}};
      result=invoke('osw_workspace_rebase',{request:rebaseRequest,prepare:action==='workspace_rebase_save'});
      if(action==='workspace_rebase_save'&&result.ok){await commitJournal(result.journal,rebaseRequest.base_revision);result=invoke('osw_workspace_import',result.journal);rebaseRequest=null;}
    }
    else if(action==='workspace_save'||action==='workspace_import'){
      if(!database)throw Error(workspaceError||'Workspace storage unavailable');
      const prepared=invoke(action==='workspace_save'?'osw_workspace_prepare':'osw_workspace_check',value);
      if(!prepared.ok)throw Error(prepared.error);
      const revision=action==='workspace_save'?value.base_revision:exported().revision;
      await commitJournal(prepared.journal,revision);
      result=invoke('osw_workspace_import',prepared.journal);if(!result.ok)throw Error('Saved journal requires reload: '+result.error);
    }
    else throw Error('Unknown query worker action');
    self.postMessage({id,result});
  }catch(error){self.postMessage({id,result:{ok:false,error:String(error.message||error)}});}
};
