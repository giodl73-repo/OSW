"use strict";
window.oswWorkspace=(()=>{
  let rpc,onChange,current,available=false;
  const $=id=>document.getElementById(id);
  function node(tag,text,parent){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;parent?.append(e);return e;}
  function checked(result){if(!result.ok)throw Error(result.error);return result;}
  function status(result){current=result;$('workspace-status').textContent=`Revision ${result.revision} · ${result.record_count} proposed records · saved locally.`;}
  function transaction(operations,revision){return {base_revision:revision,transaction_id:crypto.randomUUID(),created_at:new Date().toISOString(),operations};}
  let resolutions={},lastPlan=null;
  function rebaseView(plan){
    lastPlan=plan;const panel=$('workspace-rebase-plan');panel.hidden=false;panel.replaceChildren();node('h3','Rebase preview',panel);
    node('p',`${plan.records.length} proposed records · ${plan.unresolved} unresolved conflicts · ${plan.omitted_record_ids.length} omitted. ${plan.scope}`,panel);
    for(const conflict of plan.conflicts){
      const article=node('article',undefined,panel);node('h4',conflict.record_id+' · '+(conflict.path||conflict.kind.replaceAll('_',' ')),article);
      const details=node('details',undefined,article);node('summary','Compare source and proposed values',details);node('pre',JSON.stringify(conflict,null,2),details);
      const label=node('label','Conflict decision',article),select=node('select',undefined,label);select.dataset.conflict=conflict.id;
      for(const [value,text] of (conflict.kind==='missing_source_record'?[['','Choose a decision'],['omit','Keep this proposal in its old journal']]:[['','Choose a decision'],['proposed','Use proposed value'],['source',conflict.kind==='destination_working_record_conflict'?'Keep destination working copy':'Use updated source value']])){const option=node('option',text,select);option.value=value;}
      select.value=resolutions[conflict.id]||'';select.addEventListener('change',async()=>{if(select.value)resolutions[conflict.id]=select.value;else delete resolutions[conflict.id];select.disabled=true;try{rebaseView(checked(await rpc('workspace_rebase_resolve',resolutions)));}catch(e){$('workspace-status').textContent=e.message;select.disabled=false;}});
    }
    const records=node('details',undefined,panel);node('summary','Complete proposed records after merging',records);node('pre',JSON.stringify(plan.records,null,2),records);
    const save=node('button','Save rebased working records',panel);save.type='button';save.disabled=!plan.ready;
    save.addEventListener('click',async()=>{save.disabled=true;try{const result=checked(await rpc('workspace_rebase_save',resolutions));status(result);panel.hidden=true;lastPlan=null;onChange(result,true);}catch(e){$('workspace-status').textContent=e.message;save.disabled=false;}});
  }
  function download(journal,filename){const url=URL.createObjectURL(new Blob([JSON.stringify(journal,null,2)],{type:'application/json'}));const a=node('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  async function initialize(metadata,call,changed){
    rpc=call;onChange=changed;available=metadata.workspace_available;
    if(!available){$('workspace-status').textContent=metadata.workspace_error;return;}
    status(metadata.workspace);for(const id of ['workspace-query','workspace-refresh','workspace-export','workspace-import','workspace-list'])$(id).disabled=false;
    $('workspace-query').addEventListener('click',()=>onChange(current,true));
    $('workspace-refresh').addEventListener('click',async()=>{try{status(checked(await rpc('workspace_refresh')));onChange(current,false);}catch(e){$('workspace-status').textContent=e.message;}});
    $('workspace-export').addEventListener('click',async()=>{try{const result=checked(await rpc('workspace_export'));download(result.journal,'osw-workspace-revision-'+result.revision+'.json');}catch(e){$('workspace-status').textContent=e.message;}});
    $('workspace-list').addEventListener('click',async()=>{try{const result=checked(await rpc('workspace_snapshots'));$('workspace-snapshots').replaceChildren();for(const snapshot of result.snapshots){const option=node('option',snapshot.bundle_sha256.slice(0,12)+' · '+snapshot.revision+' revisions',$('workspace-snapshots'));option.value=snapshot.bundle_sha256;}for(const id of ['workspace-export-snapshot','workspace-export-source','workspace-rebase-preview'])$(id).disabled=!result.snapshots.length;}catch(e){$('workspace-status').textContent=e.message;}});
    $('workspace-snapshots').addEventListener('change',()=>{$('workspace-rebase-plan').hidden=true;lastPlan=null;resolutions={};});
    $('workspace-export-snapshot').addEventListener('click',async()=>{try{const result=checked(await rpc('workspace_export_snapshot',$('workspace-snapshots').value));download(result.journal,'osw-workspace-'+result.journal.bundle_sha256.slice(0,12)+'.json');}catch(e){$('workspace-status').textContent=e.message;}});
    $('workspace-export-source').addEventListener('click',async()=>{try{const result=checked(await rpc('workspace_export_source',$('workspace-snapshots').value));const url=URL.createObjectURL(new Blob([result.bytes],{type:'application/json'})),a=node('a');a.href=url;a.download='osw-source-'+$('workspace-snapshots').value.slice(0,12)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){$('workspace-status').textContent=e.message;}});
    $('workspace-rebase-preview').addEventListener('click',async()=>{const button=$('workspace-rebase-preview');button.disabled=true;lastPlan=null;resolutions={};$('workspace-rebase-plan').hidden=true;try{const file=$('workspace-rebase-source').files[0];if(file&&file.size>100000000)throw Error('Source snapshot exceeds 100 MB');const request={bundle_sha256:$('workspace-snapshots').value};if(file)request.old_bundle=await file.arrayBuffer();rebaseView(checked(await rpc('workspace_rebase_preview',request)));}catch(e){$('workspace-status').textContent=e.message;}finally{button.disabled=false;}});
    $('workspace-import').addEventListener('change',async()=>{try{const file=$('workspace-import').files[0];if(!file)return;if(file.size>8000000)throw Error('Journal exceeds 8 MB');const journal=JSON.parse(await file.text());status(checked(await rpc('workspace_import',journal)));onChange(current,true);}catch(e){$('workspace-status').textContent=e.message;}finally{$('workspace-import').value='';}});
  }
  function editor(parent,collection,record){
    if(!available)return;
    const working=collection==='working_records';const target=working?record.target:{collection,id:record.id};
    const draft=working?record:{id:'draft:'+collection+':'+record.id,label:record.label||record.name||record.title||record.id,summary:'',status:'proposed',target,proposed_data:record};
    // Revision captured when the editor opens; changes in another tab must conflict.
    const revision=current.revision,details=node('details',undefined,parent);details.className='working-editor';node('summary',working?'Edit proposed record':'Create proposed working copy',details);
    node('p','Full record copy, pending review. Describe the change and retain its source identity. Save creates a revision; the imported record remains the source reference.',details);
    const form=node('form',undefined,details),label=node('label','Working label',form),input=node('input',undefined,label);input.value=draft.label;input.required=true;input.maxLength=300;
    const reasonLabel=node('label','Change summary and evidence',form),reason=node('textarea',undefined,reasonLabel);reason.value=draft.summary;reason.required=true;reason.maxLength=4000;
    const dataLabel=node('label','Proposed record JSON',form),data=node('textarea',undefined,dataLabel);data.className='working-json';data.rows=12;data.spellcheck=false;data.value=JSON.stringify(draft.proposed_data,null,2);
    const save=node('button','Save proposed revision',form);save.type='submit';const message=node('p','',form);message.setAttribute('role','status');
    form.addEventListener('submit',async e=>{e.preventDefault();save.disabled=true;try{const proposed={...draft,label:input.value,summary:reason.value,proposed_data:JSON.parse(data.value)};const result=checked(await rpc('workspace_save',transaction([{op:'upsert',record:proposed}],revision)));status(result);message.textContent='Saved revision '+result.revision+'.';onChange(result,true);}catch(e){message.textContent=e.message;}finally{save.disabled=false;}});
    if(working){const archive=node('button','Archive working copy',details);archive.type='button';archive.addEventListener('click',async()=>{archive.disabled=true;try{const result=checked(await rpc('workspace_save',transaction([{op:'delete',id:record.id}],revision)));status(result);onChange(result,true);}catch(e){message.textContent=e.message;archive.disabled=false;}});}
  }
  return {initialize,editor};
})();
