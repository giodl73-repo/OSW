"use strict";
// Standalone pages consume the same receipt-checked Rust snapshot as the atlas.
window.oswCheckedAtlasReady = new Promise((resolve,reject)=>{
  const worker=new Worker('query-worker.js?v=standalone-source-1');
  let settled=false;
  const timer=setTimeout(()=>finish(Error('Checked source request timed out')),90000);
  function finish(error,result){
    if(settled)return;settled=true;clearTimeout(timer);worker.terminate();
    if(error){reject(error);return;}
    try{
      delete result.engine_binary;
      const documents=Object.fromEntries(Object.entries(result.sources_json).map(([path,raw])=>[path,JSON.parse(raw)]));
      window.oswCheckedAtlasSnapshot=result;
      resolve({snapshot:result,documents});
    }catch(error){reject(error);}
  }
  worker.onerror=()=>finish(Error('Checked source worker failed'));
  worker.onmessage=event=>{
    const {id,result}=event.data;
    if(!result.ok){finish(Error(result.error));return;}
    if(id===1)worker.postMessage({id:2,action:'atlas'});
    else if(id===2)finish(null,result);
  };
  worker.postMessage({id:1,action:'load'});
});
