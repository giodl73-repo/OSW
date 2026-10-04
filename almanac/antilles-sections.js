"use strict";
(async()=>{
 const byId=id=>document.getElementById(id),ns='http://www.w3.org/2000/svg';
 try {
  const response=await fetch('../research/antilles-ab0505-400m-section-diagnostic.json');if(!response.ok)throw new Error('Section data unavailable');
  const data=await response.json();
  if(data.schema!=='osw.ladcp-section-diagnostic.v1'||data.current_id!=='antilles'||data.status!=='derived_local_diagnostic_requires_review'||data.sections.length!==2)throw new Error('Unexpected section evidence');
  const select=byId('section-select');
  for(const section of data.sections){const option=document.createElement('option');option.value=section.id;option.textContent=section.label;select.append(option);}
  function render(){
   const section=data.sections.find(r=>r.id===select.value),result=section.half_peak_diagnostic;
   const address=new URL(location.href);address.searchParams.set('section',section.id);history.replaceState(null,'',address);
   const atlas=new URL('reference-routes.html',location.href);atlas.searchParams.set('atlas-feature','current:antilles');atlas.searchParams.set('atlas-section',section.id);atlas.hash='route-atlas';
   document.getElementById('section-atlas-return').href=atlas.href;
   byId('section-status').textContent=`${section.label}: ${section.samples.length} casts. ${result.offshore_span_km==null?'Offshore half-peak boundary unresolved: missing or caution samples block the calculation.':`About ${Math.round(result.offshore_span_km)} km sampled-peak-to-offshore-half-peak span; scientific review pending.`} Full width and annual ranges unknown.`;
   const rows=byId('section-samples'),layer=byId('section-station-layer');rows.replaceChildren();layer.replaceChildren();
   for(const sample of section.samples){
    const tr=document.createElement('tr');rows.append(tr);
    for(const value of [sample.cast_id,sample.average_cast_time_utc,...sample.coordinates_lon_lat,sample.northward_m_s,sample.error_velocity_m_s,sample.quality_class]){const td=document.createElement('td');td.textContent=value==null?'No sample':typeof value==='number'?value.toFixed(4):value;tr.append(td);}
    const [lon,lat]=sample.coordinates_lon_lat,x=60+(lon+180)/360*1480,y=90+(90-lat)/180*740;
    const group=document.createElementNS(ns,'g');group.classList.add('sample-station');group.setAttribute('tabindex','0');group.setAttribute('role','img');group.setAttribute('aria-label',`${sample.cast_id}, ${sample.average_cast_time_utc}, ${sample.quality_class}, ${sample.northward_m_s==null?'no sample at 400 m':sample.northward_m_s.toFixed(3)+' m/s northward'}`);layer.append(group);
    const circle=document.createElementNS(ns,'circle');for(const [k,v] of Object.entries({cx:x,cy:y,r:.5,fill:sample.northward_m_s==null?'#a6aeb1':sample.quality_class==='caution'?'#f1b15b':'#64dfce'}))circle.setAttribute(k,v);group.append(circle);
    const title=document.createElementNS(ns,'title');title.textContent=group.getAttribute('aria-label');group.append(title);
    const text=document.createElementNS(ns,'text');text.classList.add('station-name');text.setAttribute('x',x);text.setAttribute('y',y-2);text.textContent=sample.cast_id;group.append(text);
   }
  }
  const requested=new URL(location.href).searchParams.get('section');select.value=data.sections.some(r=>r.id===requested)?requested:data.sections[0].id;
  select.disabled=false;select.addEventListener('change',render);render();
 }catch(error){byId('section-status').textContent=error.message+'; source and static comparison remain available.';}
})();
