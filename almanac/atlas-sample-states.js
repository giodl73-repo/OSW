"use strict";
// Reverse navigation over pinned diagnostic relations; no physical-passage inference.
(() => {
  let pending;
  function read(year,path) {
    return fetch(path).then(async response=>{
      if(!response.ok)throw Error('Saved diagnostic relations unavailable');
      const value=await response.json();
      if(value.schema!=='osw.current-dated-timeline.v1'||value.current_id!=='gulf-stream-system'||!Array.isArray(value.frames)||value.frames.some(frame=>!Array.isArray(frame.state_relations)))throw Error('Invalid diagnostic sample set');
      return {year,data:value};
    });
  }
  window.renderAtlasDatedStateSamples=function(parent,code) {
    const section=document.createElement('details');section.className='state-dated-samples';parent.append(section);
    const summary=document.createElement('summary');summary.textContent='Saved Gulf Stream diagnostic samples · loading';section.append(summary);
    const status=document.createElement('p');status.setAttribute('role','status');section.append(status);
    if(!pending)pending=Promise.allSettled([
      read('2025','../research/ocean-current-dated-timeline-2025.json'),
      read('2026','../research/ocean-current-dated-timeline.json')
    ]);
    pending.then(results=>{
      if(!section.isConnected)return;
      const sets=results.filter(result=>result.status==='fulfilled').map(result=>result.value);
      const rows=sets.flatMap(set=>set.data.frames.flatMap(frame=>frame.state_relations.filter(relation=>relation.state_code===code).map(relation=>({year:set.year,frame,relation}))));
      summary.textContent=`Saved Gulf Stream diagnostic samples in ${code} · ${rows.length} dated line intersections`;
      status.textContent='Each dated relation clips a partial diagnostic line by approximate OSW state shapes. Dates and processing differ; these are not current footprints, containment, permanent passage or annual extrema.';
      const list=document.createElement('ul');section.append(list);
      const requested=new URLSearchParams(location.search);
      for(const {year,frame,relation} of rows) {
        const item=document.createElement('li');item.dataset.sampleDate=frame.date;item.dataset.stateCode=code;item.dataset.predicate=relation.predicate;list.append(item);
        const anchor=document.createElement('a');anchor.href=`reference-routes.html?atlas-feature=current%3Agulf-stream-system&atlas-series=${year}&atlas-date=${frame.date}#route-atlas`;
        anchor.textContent=`${frame.date} · about ${Math.round(relation.intersection_length_km).toLocaleString('en-US')} km of diagnostic line · view on atlas`;item.append(anchor);
        item.append(document.createTextNode(` · ${frame.source_algorithm} · ${frame.reaches_downstream_gate?'50 W gate reached':'truncated diagnostic'}`));
        if(requested.get('diagnostic-date')===frame.date&&requested.get('diagnostic-series')===year) {item.classList.add('requested-diagnostic-sample');item.append(document.createTextNode(' · requested sample'));section.open=true;}
      }
      if(!rows.length) {const item=document.createElement('li');item.textContent='No saved diagnostic line intersection recorded in the loaded sample sets; current absence is not established.';list.append(item);}
      if(sets.length<results.length) {const warning=document.createElement('p');warning.textContent='Some diagnostic sample sets are unavailable. Available relations are shown; counts do not cover the unavailable set.';section.append(warning);}
    });
  };
})();
