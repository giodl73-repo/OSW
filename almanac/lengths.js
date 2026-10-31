"use strict";
(async()=>{
  const $=id=>document.getElementById(id),node=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;};
  const labels={reported:'Source-reported length',reference_estimate:'Calculated reference-route estimate',provisional_estimate:'Provisional geographic estimate',regional_only:'Full extent still to estimate',needs_route:'Route still to define'};
  try{
    const response=await fetch('../research/current-length-estimate-register-v1.json');if(!response.ok)throw Error('Length register unavailable');
    const data=await response.json();
    if(data.schema!=='osw.current-length-estimate-register.v1'||data.records.length!==111||new Set(data.records.map(r=>r.entity_id)).size!==111)throw Error('Incomplete current inventory');
    const counts=data.counts;
    $('length-summary').textContent=`${counts.with_length_estimate} of ${counts.currents} length entries available (${counts.provisional_estimate||0} provisional) · ${counts.remaining_full_extent_estimates} estimates to finish`;
    function render(){
      const text=$('length-search').value.trim().toLowerCase(),filter=$('length-filter').value;
      const rows=data.records.filter(r=>(!text||`${r.name} ${r.basin||''}`.toLowerCase().includes(text))&&(filter==='all'||filter==='estimated'&&r.length_estimate_km!==null||filter==='remaining'&&r.needs_full_extent_estimate||filter===r.status));
      rows.sort($('length-sort').value==='name'?(a,b)=>a.name.localeCompare(b.name):(a,b)=>(b.length_estimate_km??-1)-(a.length_estimate_km??-1)||a.name.localeCompare(b.name));
      $('length-results').textContent=`${rows.length} currents shown. Missing estimates stay visible at the end of length order.`;
      $('length-rows').replaceChildren();
      for(const row of rows){
        const tr=node('tr',undefined,$('length-rows'));tr.dataset.currentId=row.entity_id;
        const cell=label=>{const td=node('td',undefined,tr);td.dataset.label=label;return td;};
        const name=cell('Current'),link=node('a',row.name,name);link.href=row.current_card_url;
        node('span',`${row.basin||'Basin unspecified'} · ${row.identity_level}`,name).className='length-status';
        const value=cell('Length estimate');
        if(row.length_estimate_km!==null){node('span',`≈ ${row.length_estimate_km.toLocaleString()} km`,value).className='length-number';const bar=node('span',undefined,value);bar.className='length-bar';bar.style.width=Math.max(2,row.length_estimate_km/25000*150)+'px';bar.setAttribute('aria-hidden','true');}
        else{node('strong','To estimate',value).className='length-missing';if(row.available_regional_reach_km!==null)node('span',`Regional reach available: ≈ ${row.available_regional_reach_km.toLocaleString()} km`,value).className='length-status';}
        node('span',labels[row.status],cell('Basis'));
        const evidence=cell('Extent and evidence'),details=node('details',undefined,evidence);node('summary','Extent, method and source',details);
        node('p',row.scope||'The full reference extent still needs to be defined; a regional study boundary is not automatically a current endpoint.',details);
        if(row.route_choice_rule)node('p',row.route_choice_rule,details);
        if(row.reported_length_source_locator)node('p',row.reported_length_source_locator,details);
        if(row.source_locator)node('p',row.source_locator,details);
        if(row.route_sensitivity_km)node('p',`Route/gate sensitivity: ${row.route_sensitivity_km.map(n=>n.toLocaleString()).join('–')} km. Not physical uncertainty or annual variation.`,details);
        if(row.source_time_convention)node('p',row.source_time_convention,details);
        if(row.gate_rationale)node('p',row.gate_rationale,details);
        if(row.drawing_constraint)node('p',row.drawing_constraint,details);
        if(row.source_typography_note)node('p',row.source_typography_note,details);
        if(row.identity_interpretation)node('p',row.identity_interpretation,details);
        if(row.geographic_screening)node('p',row.geographic_screening,details);
        if(row.figure_file){const map=node('a','Map of the nominal reference extent',details);map.href='../'+row.figure_file;map.className='length-source';}
        if(row.source_url){const original=node('a','Original source',details);original.href=row.source_url;original.className='length-source';}
        if(row.record_file){const source=node('a','Retained source record',details);source.href='../'+row.record_file;source.className='length-source';}
        for(const route of row.route_options){const p=node('p',undefined,details),a=node('a',`≈ ${route.length_km.toLocaleString()} km · ${route.extent_class==='regional_reach'?'regional reach':'reference extent'}`,p);a.href=route.route_card_url;node('span',' — '+route.scope,p);}
      }
    }
    $('length-controls').addEventListener('submit',e=>e.preventDefault());for(const id of ['length-search','length-filter','length-sort'])$(id).addEventListener(id==='length-search'?'input':'change',render);
    window.oswCurrentLengthRegister=data;render();
  }catch(error){$('length-summary').textContent=error.message;}
})();
