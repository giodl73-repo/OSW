"use strict";
// Sample positions are transverse section support, never current axes or edges.
window.initAtlasObservedSections = function(panel,current,api) {
 const source=current.series.find(row=>row.evidence_role==='observed_sections_with_unadmitted_one_sided_span');
 if(!source)return()=>{};
 let disposed=false,overlay=null,sections=null,bounds=null,view=null;
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
 function station(parent,sample,local=false){
  const {x,y}=sample,width=local?bounds[2]:Number(api.svg.getAttribute('viewBox').split(' ')[2]);
  const group=api.make('g',{class:'atlas-observed-station',tabindex:0,role:'button'},parent);
  const text=sample.label;
  group.dataset.currentId=current.id;group.dataset.atlasLabel=text;group.dataset.castId=sample.cast_id;
  group.setAttribute('aria-label',text);api.make('title',{},group).textContent=text;
  api.make('circle',{cx:x,cy:y,r:width/1480*8,fill:sample.color,'vector-effect':'non-scaling-stroke'},group);
  api.make('text',{x:x+width/1480*12,y:y-width/1480*12,'font-size':local?bounds[2]/360*12:width/1480*18},group).textContent=sample.cast_id;
  function activate(){
   if(disposed)return;
   section.querySelectorAll('.selected-cast').forEach(el=>el.classList.remove('selected-cast'));
   overlay?.querySelectorAll('.selected-cast').forEach(el=>el.classList.remove('selected-cast'));
   for(const container of [overlay,map])for(const mark of container?.querySelectorAll('[data-cast-id]')||[])if(mark.dataset.castId===sample.cast_id)mark.classList.add('selected-cast');
   castInfo.textContent=sample.activation_text;
  }
  group.addEventListener('click',()=>{if(!api.wasDragged())activate();});
  group.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();activate();}});
 }
 function render(){
  if(disposed||!sections)return;
  const row=sections.find(r=>r.id===select.value),diagnostic=view.sections[row.id];
  overlay?.remove();overlay=api.make('g',{class:'atlas-observed-overlay'},api.layer);
  api.svg.classList.add('has-observed-samples');
  map.replaceChildren();map.setAttribute('viewBox',bounds.join(' '));map.setAttribute('aria-label',`${current.label}: ${row.label} observed cast positions at 400 m; not current edges or an axis.`);
  api.make('image',{href:'../figures/ocean-motion-closeup-ground.svg',x:60,y:90,width:1480,height:740,opacity:.6},map);
  for(const sample of diagnostic.stations){station(overlay,sample);station(map,sample,true);}
  const message=diagnostic.status;
  status.textContent=message;document.getElementById('route-atlas-status').textContent=current.label+' · '+message;
  castInfo.textContent='Select an observed cast for its exact average time, quality and local velocity.';
  details.href=source.url+'?section='+encodeURIComponent(row.id);
  api.shareSelection(panel,current.id,null,null,row.id);
  api.refreshUpdates();
 }
 (async()=>{
  try{
   const docs=await window.oswAtlasSourcesReady,path=source.diagnostic_url.replace(/^\.\.\//,'');
   const data=docs[path];view=window.oswAtlasSnapshot.observed_section_views[path];
   if(disposed)return;if(!data||!view)throw Error('Observed-section data unavailable from checked atlas');
   sections=data.sections;
   for(const row of sections){const option=document.createElement('option');option.value=row.id;option.textContent=row.label;select.append(option);}
   bounds=view.view_box;
   if(api.svg.getAttribute('viewBox')===initialView)api.fitBounds(bounds);
   select.value=sections.some(r=>r.id===api.requestedSection)?api.requestedSection:sections[0].id;
   select.disabled=false;select.addEventListener('change',render);render();
  }catch(error){if(!disposed){status.textContent=error.message+'; the current record and standalone observed-section view remain available.';map.hidden=true;details.href=source.url;}}
 })();
 return()=>{disposed=true;overlay?.remove();overlay=null;api.svg.classList.remove('has-observed-samples');};
};
