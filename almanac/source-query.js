"use strict";
(() => {
  const $=id=>document.getElementById(id), panel=$("source-query-panel");
  let worker=null, loading=null, metadata=null, failed=null, serial=0, generation=0, last=null, requestValue=null;
  const pending=new Map(), saved=new URL(location.href).searchParams.get("source-q");
  function terminate(error){failed=error;for(const item of pending.values()){clearTimeout(item.timer);item.reject(error);}pending.clear();worker?.terminate();}
  function request(action,value){
    if(failed)return Promise.reject(failed);
    return new Promise((resolve,reject)=>{const id=++serial;const timer=setTimeout(()=>terminate(Error("Checked source request timed out")),90000);pending.set(id,{resolve,reject,timer});worker.postMessage({id,action,value});});
  }
  function controls(busy){
    $("source-query-fields").disabled=!metadata||busy||!!failed;
    $("source-query-json").disabled=$("source-query-run-json").disabled=!metadata||busy||!!failed;
    $("source-query-export").disabled=!last||busy;
    $("source-query-previous").disabled=!last||busy||last.offset===0;
    $("source-query-next").disabled=!last||busy||last.offset+last.rows.length>=last.total;
  }
  function clear(){last=null;window.oswSourceQueryResult=null;$("source-query-rows").replaceChildren();$("source-query-share").hidden=true;$("source-query-receipt").textContent="";$("source-query-page").textContent="";$("source-query-active").hidden=true;}
  function status(text,error=false){$("source-query-status").textContent=text;$("source-query-status").classList.toggle("error",error);}
  function download(value,name){const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)+"\n"],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function render(result){
    last=result;window.oswSourceQueryResult=result;
    const body=$("source-query-rows");body.replaceChildren();
    for(const row of result.rows){
      const tr=document.createElement("tr"), address=document.createElement("td"), preview=document.createElement("td"), pre=document.createElement("pre"), button=document.createElement("button");
      address.textContent=row.source_pointer||"/";tr.dataset.sourcePointer=row.source_pointer;
      const json=JSON.stringify(row.record,null,2);pre.textContent=json.slice(0,2000)+(json.length>2000?"\n… Preview limited to 2,000 characters. Download the complete record below.":"");
      pre.tabIndex=0;pre.setAttribute("aria-label",`Source record preview at ${row.source_pointer||"/"}`);
      button.type="button";button.textContent="Download this source record";button.addEventListener("click",()=>download({document:result.document,source_pointer:row.source_pointer,source_sha256:result.source_sha256,scope:result.scope,record:row.record},"osw-source-record.json"));
      preview.append(pre,button);tr.append(address,preview);body.append(tr);
    }
    const descriptor=metadata.catalog.documents.find(d=>d.path===result.document);
    $("source-query-receipt").textContent=`${result.document} · original source SHA-256 ${result.source_sha256} · ${descriptor.source_bytes.toLocaleString()} source bytes. ${result.scope}`;
    $("source-query-page").textContent=result.total?`${result.offset+1}–${result.offset+result.rows.length} of ${result.total} matching rows`:"0 matching rows";
    // An offset beyond the end is a valid empty page, not an invented row range.
    if(result.total&&result.rows.length===0)$("source-query-page").textContent=`No rows at offset ${result.offset}; ${result.total} matching rows`;
    status(`${result.rows.length} rows returned from ${metadata.source_count} checked source documents.`);
    const constraints={};if(requestValue.filters?.length)constraints.filters=requestValue.filters;if(requestValue.sort)constraints.sort=requestValue.sort;
    $("source-query-active").hidden=Object.keys(constraints).length===0;$("source-query-active").textContent=`Active structured constraints: ${JSON.stringify(constraints)}`;
    const url=new URL(location.href);url.searchParams.set("source-q",JSON.stringify(requestValue));history.replaceState(null,"",url);url.hash="source-query-title";$("source-query-share").href=url;$("source-query-share").hidden=false;
  }
  async function run(value){
    const token=++generation;clear();controls(true);status("Running checked source query…");$("source-query-status").dataset.pending="true";
    try{
      const result=await request("query",value);if(token!==generation)return;
      requestValue=value;$("source-query-json").value=JSON.stringify(value,null,2);
      $("source-query-document").value=result.document;$("source-query-pointer").value=result.pointer;
      $("source-query-text").value=value.text||"";$("source-query-limit").value=result.limit;
      render(result);
    }catch(error){if(token!==generation)return;clear();status(`Source query unavailable: ${error.message}`,true);}
    finally{if(token===generation){controls(false);$("source-query-status").dataset.pending="false";}}
  }
  async function load(){
    if(loading)return loading;
    loading=(async()=>{
      status("Loading checked source catalog…");worker=new Worker("index-worker.js?v=source-query-1");
      worker.onerror=()=>terminate(Error("Checked source worker failed"));
      worker.onmessage=({data})=>{const item=pending.get(data.id);if(!item)return;pending.delete(data.id);clearTimeout(item.timer);if(data.result.ok)item.resolve(data.result);else item.reject(Error(data.result.error));};
      try{
        metadata=await request("load");window.oswSourceQueryMetadata=metadata;
        for(const doc of metadata.catalog.documents){const option=document.createElement("option");option.value=option.textContent=doc.path;$("source-query-document").append(option);}
        controls(false);
        let initial;
        try{initial=saved?JSON.parse(saved):{document:"research/ocean-current-almanac.json",pointer:"/entries",limit:25,offset:0};}
        catch(error){clear();status(`Invalid shared source request JSON: ${error.message}`,true);return;}
        $("source-query-json").value=JSON.stringify(initial,null,2);await run(initial);
      }catch(error){clear();status(`Source catalog unavailable: ${error.message}`,true);controls(false);}
    })();return loading;
  }
  panel.addEventListener("toggle",()=>{if(panel.open)load();});
  $("source-query-document").addEventListener("change",()=>{$("source-query-pointer").value="";$("source-query-text").value="";});
  $("source-query-form").addEventListener("submit",event=>{
    event.preventDefault();const value={document:$("source-query-document").value,pointer:$("source-query-pointer").value,text:$("source-query-text").value,limit:Number($("source-query-limit").value),offset:0};
    // Preserve advanced constraints when using the basic controls on the same source.
    if(requestValue?.document===value.document){if(requestValue.filters)value.filters=requestValue.filters;if(requestValue.sort)value.sort=requestValue.sort;}
    run(value);
  });
  $("source-query-run-json").addEventListener("click",()=>{try{const value=JSON.parse($("source-query-json").value);run(value);}catch(error){clear();status(`Invalid source request JSON: ${error.message}`,true);controls(false);}});
  $("source-query-previous").addEventListener("click",()=>run({...requestValue,offset:Math.max(0,last.offset-last.limit)}));
  $("source-query-next").addEventListener("click",()=>run({...requestValue,offset:last.offset+last.limit}));
  $("source-query-export").addEventListener("click",()=>{if(last)download({query:requestValue,result:last},"osw-source-query-page.json");});
  if(saved){panel.open=true;load();}
})();
