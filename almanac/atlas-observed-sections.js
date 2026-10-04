"use strict";
// Sample positions are transverse section support, never current axes or edges.
window.initAtlasObservedSections = function(panel,current,api) {
 const source=current.series.find(row=>row.evidence_role==='observed_sections_with_unadmitted_one_sided_span');
 if(!source)return()=>{};
 let disposed=false,overlay=null,sections=null,bounds=null;
 const initialView=api.svg.getAttribute('viewBox');
 const section=document.createElement('section');section.className='atlas-observed-sections';
 panel.querySelector('.route-atlas-classification')?.after(section);
 if(!section.isConnected)panel.append(section);
 const heading=document.createElement('h4');heading.textContent='Observed sections · May 2005';section.append(heading);
 const controls=document.createElement('div');controls.className='route-atlas-controls';section.append(controls);
 const label=document.createElement('label');label.textContent='Occupation ';controls.append(label);
 const select=document.createElement('select');select.className='atlas-observed-section-select';select.disabled=true;label.append(select);
 const status=document.createElement('p');status.className='atlas-observed-section-status';status.setAttribute('role','status');status.textContent='Loading pinned observed sections…';section.append(status);
 const map=document.createElementNS(api.ns,'svg');map.classList.add('atlas-observed-section-map');map.setAttribute('role','group');section.append(map);
 const note=document.createElement('p');note.textContent='Points are instrument locations, not a current axis or footprint. Teal: provider usable; orange: caution; gray: no sample at 400 m. Hover or focus a cast for its name; activate it for date and velocity. Several days compose each survey; tides were not removed.';section.append(note);
 const castInfo=document.createElement('p');castInfo.className='atlas-observed-cast-info';castInfo.setAttribute('role','status');section.append(castInfo);
 const details=document.createElement('a');details.textContent='Compare profiles, cast table and measurement rule →';details.className='atlas-observed-details-link';section.append(details);
 const sourceLink=document.createElement('a');sourceLink.textContent='Pinned observations and calculation';sourceLink.href=source.diagnostic_url;
 const paragraph=document.createElement('p');paragraph.append(sourceLink);section.append(paragraph);
 function valid(data){
  return data?.schema==='osw.ladcp-section-diagnostic.v1'&&'current:'+data.current_id===current.id&&data.status==='derived_local_diagnostic_requires_review'&&
   data.depth_m===400&&data.geographic_role==='transverse_observation_section_not_current_axis'&&data.tides_removed===false&&data.width_rank_eligible===false&&data.seasonal_playback_eligible===false&&
   ['whole_current_length_km','whole_current_width_km','annual_length_range_km','annual_width_range_km'].every(key=>data[key]===null)&&
   Array.isArray(data.sections)&&data.sections.length===2&&new Set(data.sections.map(r=>r.id)).size===2&&data.sections.every(r=>
    typeof r.id==='string'&&typeof r.label==='string'&&r.half_peak_diagnostic?.full_width_km===null&&
    Array.isArray(r.samples)&&r.samples.length>0&&r.samples.every(s=>typeof s.cast_id==='string'&&
     ['usable','caution'].includes(s.quality_class)&&Array.isArray(s.coordinates_lon_lat)&&s.coordinates_lon_lat.length===2&&s.coordinates_lon_lat.every(Number.isFinite)&&Math.abs(s.coordinates_lon_lat[0])<=180&&Math.abs(s.coordinates_lon_lat[1])<=90&&
     typeof s.average_cast_time_utc==='string'&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(s.average_cast_time_utc)&&Number.isFinite(Date.parse(s.average_cast_time_utc))&&
     ['northward_m_s','error_velocity_m_s'].every(key=>s[key]===null||typeof s[key]==='number'&&Number.isFinite(s[key]))));
 }
 function station(parent,sample,local=false){
  const [x,y]=api.project(sample.coordinates_lon_lat),width=local?bounds[2]:Number(api.svg.getAttribute('viewBox').split(' ')[2]);
  const group=api.make('g',{class:'atlas-observed-station',tabindex:0,role:'button'},parent);
  const text=`${sample.cast_id} · ${sample.average_cast_time_utc} · ${sample.quality_class} · ${sample.northward_m_s==null?'no sample at 400 m':sample.northward_m_s.toFixed(3)+' m/s northward at 400 m'}`;
  group.dataset.currentId=current.id;group.dataset.atlasLabel=text;group.dataset.castId=sample.cast_id;
  group.setAttribute('aria-label',text);api.make('title',{},group).textContent=text;
  api.make('circle',{cx:x,cy:y,r:width/1480*8,fill:sample.northward_m_s==null?'#a6aeb1':sample.quality_class==='caution'?'#f1b15b':'#64dfce','vector-effect':'non-scaling-stroke'},group);
  api.make('text',{x:x+width/1480*12,y:y-width/1480*12,'font-size':local?bounds[2]/360*12:width/1480*18},group).textContent=sample.cast_id;
  function activate(){
   if(disposed)return;
   section.querySelectorAll('.selected-cast').forEach(el=>el.classList.remove('selected-cast'));
   overlay?.querySelectorAll('.selected-cast').forEach(el=>el.classList.remove('selected-cast'));
   for(const container of [overlay,map])for(const mark of container?.querySelectorAll('[data-cast-id]')||[])if(mark.dataset.castId===sample.cast_id)mark.classList.add('selected-cast');
   castInfo.textContent=text+` · error velocity: ${sample.error_velocity_m_s==null?'no sample':sample.error_velocity_m_s.toFixed(3)+' m/s'}. Error velocity is not a confidence interval.`;
  }
  group.addEventListener('click',()=>{if(!api.wasDragged())activate();});
  group.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();activate();}});
 }
 function render(){
  if(disposed||!sections)return;
  const row=sections.find(r=>r.id===select.value),diagnostic=row.half_peak_diagnostic;
  overlay?.remove();overlay=api.make('g',{class:'atlas-observed-overlay'},api.layer);
  api.svg.classList.add('has-observed-samples');
  map.replaceChildren();map.setAttribute('viewBox',bounds.join(' '));map.setAttribute('aria-label',`${current.label}: ${row.label} observed cast positions at 400 m; not current edges or an axis.`);
  api.make('image',{href:'../figures/ocean-motion-closeup-ground.svg',x:60,y:90,width:1480,height:740,opacity:.6},map);
  for(const sample of row.samples){station(overlay,sample);station(map,sample,true);}
  const message=`${row.label} · ${row.samples.length} observed casts · 400 m instrument depth. ${diagnostic.offshore_span_km==null?'Offshore half-peak boundary unresolved under quality rules.':`About ${Math.round(diagnostic.offshore_span_km)} km one-sided sampled-peak-to-offshore-half-peak span; review pending.`} Full width, current length and annual ranges remain unresolved.`;
  status.textContent=message;document.getElementById('route-atlas-status').textContent=current.label+' · '+message;
  castInfo.textContent='Select an observed cast for its exact average time, quality and local velocity.';
  details.href=source.url+'?section='+encodeURIComponent(row.id);
  api.shareSelection(panel,current.id,null,null,row.id);
  api.refreshUpdates();
 }
 (async()=>{
  try{
   const response=await fetch(source.diagnostic_url,{cache:'no-store'});if(!response.ok)throw Error('Observed-section data unavailable');
   const data=await response.json();if(disposed)return;if(!valid(data))throw Error('Invalid observed-section evidence');
   sections=data.sections;
   for(const row of sections){const option=document.createElement('option');option.value=row.id;option.textContent=row.label;select.append(option);}
   const points=sections.flatMap(r=>r.samples.map(s=>api.project(s.coordinates_lon_lat))),xs=points.map(r=>r[0]),ys=points.map(r=>r[1]);
   const width=Math.min(1480,Math.max(16,(Math.max(...xs)-Math.min(...xs))*1.4,(Math.max(...ys)-Math.min(...ys))*2.8));
   bounds=[Math.max(60,Math.min(1540-width,(Math.min(...xs)+Math.max(...xs))/2-width/2)),Math.max(90,Math.min(830-width/2,(Math.min(...ys)+Math.max(...ys))/2-width/4)),width,width/2];
   if(api.svg.getAttribute('viewBox')===initialView)api.fit(sections.flatMap(r=>r.samples.map(s=>s.coordinates_lon_lat)));
   select.value=sections.some(r=>r.id===api.requestedSection)?api.requestedSection:sections[0].id;
   select.disabled=false;select.addEventListener('change',render);render();
  }catch(error){if(!disposed){status.textContent=error.message+'; the current record and standalone observed-section view remain available.';map.hidden=true;details.href=source.url;}}
 })();
 return()=>{disposed=true;overlay?.remove();overlay=null;api.svg.classList.remove('has-observed-samples');};
};
