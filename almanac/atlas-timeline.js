"use strict";
// Display pinned diagnostic samples; never interpolate unsampled geometry.
window.initAtlasTimeline = function(panel,current,api) {
  const section=document.createElement('details');section.className='atlas-timeline';
  const savedSection=panel.querySelector('.route-atlas-dated-preview');if(savedSection)savedSection.after(section);else panel.append(section);
  const summary=document.createElement('summary');summary.textContent='Explore saved dates on the atlas';section.append(summary);
  const note=document.createElement('p');note.textContent='Step through sampled surface diagnostics. Playback advances by sample, not elapsed time; no interpolated seasonal paths or annual extrema.';section.append(note);
  const controls=document.createElement('div');controls.className='atlas-timeline-controls';section.append(controls);
  function selector(label,cls) {
    const wrapper=document.createElement('label');wrapper.append(document.createTextNode(label));controls.append(wrapper);
    const select=document.createElement('select');select.className=cls;wrapper.append(select);return select;
  }
  const seriesSelect=selector('Sample set','atlas-timeline-series');
  for(const [value,text] of [['2025','2025 · 12 daily snapshots'],['2026','September 2026 · 5 days']]) {const option=document.createElement('option');option.value=value;option.textContent=text;seriesSelect.append(option);}
  const dates=selector('Saved date','atlas-timeline-date');dates.disabled=true;
  const play=document.createElement('button');play.type='button';play.textContent='Play samples';play.disabled=true;controls.append(play);
  const status=document.createElement('p');status.className='atlas-timeline-status';status.setAttribute('role','status');section.append(status);
  const content=document.createElement('div');section.append(content);
  let timer=null,token=0,disposed=false,series=null,active=false,overlay=null,bounds=null;
  const cache=new Map();
  function stop() {if(timer!==null)clearInterval(timer);timer=null;play.textContent='Play samples';}
  function restoreLines() {api.layer.querySelectorAll('#route-atlas-dated-lines path').forEach(el=>el.style.removeProperty('visibility'));}
  function deactivate() {stop();active=false;overlay?.remove();overlay=null;restoreLines();status.textContent='Saved sample playback paused; select a date to display it.';}
  function paragraph(text) {const p=document.createElement('p');p.textContent=text;content.append(p);}
  function link(text,href) {const p=document.createElement('p'),a=document.createElement('a');a.textContent=text;a.href=href;p.append(a);content.append(p);}
  function render(fitView=false) {
    if(!series||disposed)return;
    const frame=series.frames[Number(dates.value)];if(!frame)return;
    active=true;api.layer.querySelectorAll('#route-atlas-dated-lines path').forEach(el=>el.style.visibility='hidden');const saved=panel.querySelector('.route-atlas-dated-content');if(saved)saved.hidden=true;if(fitView)api.fit(series.frames.flatMap(f=>f.coordinates_lon_lat));
    bounds=api.svg.getAttribute('viewBox');
    overlay?.remove();overlay=api.make('path',{d:api.pathData(frame.coordinates_lon_lat),class:'atlas-timeline-line','vector-effect':'non-scaling-stroke','aria-hidden':'true'},api.layer);
    api.layer.querySelectorAll('.route-atlas-dated-line.selected').forEach(el=>el.classList.remove('selected'));
    panel.querySelectorAll('.route-atlas-dated-preview button').forEach(el=>el.setAttribute('aria-pressed','false'));
    api.shareSelection(panel,current.id);
    const url=new URL(location.href);url.searchParams.set('atlas-series',seriesSelect.value);url.searchParams.set('atlas-date',frame.date);history.replaceState(null,'',url);panel.querySelector('[data-atlas-share]').href=url.href;
    content.replaceChildren();
    const image=document.createElementNS(api.ns,'svg');image.classList.add('atlas-timeline-map');image.setAttribute('viewBox',bounds);image.setAttribute('role','img');image.setAttribute('aria-label',`${current.label}: ${frame.date} partial surface geostrophic diagnostic, not a whole-current axis.`);content.append(image);
    api.make('image',{href:'../figures/ocean-motion-dashboard-ground.svg',x:60,y:90,width:1480,height:740,opacity:.45},image);
    api.make('path',{d:api.pathData(frame.coordinates_lon_lat),class:'atlas-timeline-line','vector-effect':'non-scaling-stroke'},image);    const states=document.createElement('section');states.className='atlas-timeline-states';content.append(states);    const stateHeading=document.createElement('h4');stateHeading.textContent=`OSW line intersections · ${frame.date}`;states.append(stateHeading);    const stateNote=document.createElement('p');stateNote.textContent='Saved diagnostic line clipped by approximate OSW state shapes. These are line-segment lengths, not current footprints, permanent passage or containment.';states.append(stateNote);    const stateList=document.createElement('ul');states.append(stateList);    for(const relation of frame.state_relations||[]) {      const item=document.createElement('li');item.dataset.stateCode=relation.state_code;item.dataset.predicate=relation.predicate;stateList.append(item);      const a=document.createElement('a');a.textContent=`${relation.state_code} · about ${Math.round(relation.intersection_length_km).toLocaleString('en-US')} km of diagnostic line`;      a.href=`index.html?state=${encodeURIComponent(relation.state_code)}&diagnostic-series=${seriesSelect.value}&diagnostic-date=${frame.date}#state-title`;item.append(a);    }    if(!stateList.children.length) {const item=document.createElement('li');item.textContent='No line intersection recorded for this sample; physical current passage remains unresolved.';stateList.append(item);}
    status.textContent=`${frame.date} · ${frame.reaches_downstream_gate?'50 W gate reached':'truncated diagnostic'} · ${frame.source_algorithm} · ${frame.source_product_status}`;
    document.getElementById('route-atlas-status').textContent=`${current.label} · saved surface diagnostic sample: ${frame.date} · ${frame.source_algorithm}; not a whole-current axis or annual extent.`;
    paragraph(`Trace stop: ${frame.stop_reason.replaceAll('_',' ')}. This is a diagnostic stop, not the current endpoint.${frame.stop_reason==='distance_cap'?' The trace can circulate until the integration cap; accumulated distance is not downstream current extent.':''}`);
    const previous=series.frames[Number(dates.value)-1];
    if(previous) {const gap=Math.round((Date.parse(frame.date)-Date.parse(previous.date))/86400000);paragraph(`${gap} calendar days since previous sample; ${gap-1} intervening days are unsampled here.`);}
    paragraph(series.sampling_note);
    if(new Set(series.frames.map(f=>f.source_algorithm)).size>1)paragraph('Source processing changes within this sample set. Differences cannot be assigned entirely to ocean change.');
    paragraph(series.limitations);
    link('NOAA source for this saved date',frame.source_url);link('Pinned source subset','../'+frame.source_subset);
    link('Diagnostic details and local width candidate',`dated-current.html?series=${seriesSelect.value}&date=${frame.date}`);
  }
  async function load(requestedDate) {
    deactivate();const request=++token;dates.disabled=true;play.disabled=true;status.textContent='Loading saved samples…';
    const year=seriesSelect.value,path=year==='2025'?'../research/ocean-current-dated-timeline-2025.json':'../research/ocean-current-dated-timeline.json';
    try {
      if(!cache.has(year))cache.set(year,fetch(path).then(async r=>{if(!r.ok)throw Error('Saved samples unavailable');return r.json();}).catch(e=>{cache.delete(year);throw e;}));
      const data=await cache.get(year);if(disposed||request!==token)return;
      if(data.schema!=='osw.current-dated-timeline.v1'||data.current_id!=='gulf-stream-system'||!Array.isArray(data.frames)||!data.frames.length||data.frames.some(f=>!Array.isArray(f.coordinates_lon_lat)||!f.coordinates_lon_lat.length))throw Error('Invalid saved sample set');
      series=data;dates.replaceChildren();
      for(const [index,frame] of series.frames.entries()) {const option=document.createElement('option');option.value=index;option.textContent=frame.date;dates.append(option);}
      const index=series.frames.findIndex(f=>f.date===requestedDate);dates.value=String(index<0?0:index);dates.disabled=false;play.disabled=series.frames.length<2;render(true);
    } catch(error) {if(!disposed&&request===token)status.textContent=error.message;}
  }
  seriesSelect.addEventListener('change',()=>load());
  dates.addEventListener('change',()=>{stop();render(!active);});
  play.addEventListener('click',()=>{if(timer!==null){stop();return;}if(!active)render(true);play.textContent='Pause';timer=setInterval(()=>{const next=Number(dates.value)+1;if(next>=series.frames.length){stop();return;}dates.value=String(next);render();},2200);});
  section.addEventListener('toggle',()=>{if(!section.open){stop();return;}if(!series)load(api.requestedDate);});
  const visibility=()=>{if(document.hidden)stop();};document.addEventListener('visibilitychange',visibility);
  panel.addEventListener('atlas-saved-view',deactivate);
  if(api.requestedDate) {seriesSelect.value=api.requestedSeries==='2026'?'2026':'2025';section.open=true;}
  return ()=>{disposed=true;++token;stop();overlay?.remove();restoreLines();document.removeEventListener('visibilitychange',visibility);panel.removeEventListener('atlas-saved-view',deactivate);};
};
