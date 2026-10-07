"use strict";
// Reverse navigation over pinned diagnostic relations; no physical-passage inference.
(() => {
  const pending = new Map();
  window.renderAtlasDatedStateSamples=function(parent,code) {
    const section=document.createElement('details');section.className='state-dated-samples';parent.append(section);
    const summary=document.createElement('summary');summary.textContent='Saved Gulf Stream diagnostic samples · loading';section.append(summary);
    const status=document.createElement('p');status.setAttribute('role','status');section.append(status);
    if(!pending.has(code)) pending.set(code,window.oswIndexSupport({section:"diagnostic_samples",state_code:code}));
    pending.get(code).then(view=>{
      if(!section.isConnected)return;
      const rows=view.rows;
      summary.textContent=`Saved Gulf Stream diagnostic samples in ${code} · ${rows.length} dated line intersections`;
      status.textContent='Each dated relation clips a partial diagnostic line by approximate OSW state shapes. Dates and processing differ; these are not current footprints, containment, permanent passage or annual extrema.';
      const list=document.createElement('ul');section.append(list);
      const requested=new URLSearchParams(location.search);
      for(const {year,frame,relation,atlas_url} of rows) {
        const item=document.createElement('li');item.dataset.sampleDate=frame.date;item.dataset.stateCode=code;item.dataset.predicate=relation.predicate;list.append(item);
        const anchor=document.createElement('a');anchor.href=atlas_url;
        anchor.textContent=`${frame.date} · about ${Math.round(relation.intersection_length_km).toLocaleString('en-US')} km of diagnostic line · view on atlas`;item.append(anchor);
        item.append(document.createTextNode(` · ${frame.source_algorithm} · ${frame.reaches_downstream_gate?'50 W gate reached':'truncated diagnostic'}`));
        if(requested.get('diagnostic-date')===frame.date&&requested.get('diagnostic-series')===year) {item.classList.add('requested-diagnostic-sample');item.append(document.createTextNode(' · requested sample'));section.open=true;}
      }
      if(!rows.length) {const item=document.createElement('li');item.textContent='No saved diagnostic line intersection recorded in the loaded sample sets; current absence is not established.';list.append(item);}
    }).catch(error=>{
      if(!section.isConnected)return;
      summary.textContent=`Saved Gulf Stream diagnostic samples in ${code} · unavailable`;
      status.textContent=`Diagnostic query unavailable: ${error.message}. Current absence is not established.`;
    });
  };
})();
