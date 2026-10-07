"use strict";
// Monthly product samples are transverse support, never a full current axis.
window.initAtlasMonthlySection=function(panel,current,api){
 const source=current.series.find(row=>row.evidence_role==='monthly_mean_section_width_candidate');
 if(!source)return()=>{};
 let disposed=false,data=null,overlay=null,timer=null;
 const initialView=api.svg.getAttribute('viewBox');
 const section=document.createElement('section');section.className='atlas-monthly-section';
 panel.querySelector('.route-atlas-classification')?.after(section);if(!section.isConnected)panel.append(section);
 const heading=document.createElement('h4');heading.textContent='Monthly surface section · 140°W · 2013';section.append(heading);
 const controls=document.createElement('div');controls.className='route-atlas-controls';section.append(controls);
 const label=document.createElement('label');label.textContent='Saved month ';controls.append(label);
 const select=document.createElement('select');select.className='atlas-monthly-select';select.disabled=true;label.append(select);
 function button(text,cls){const b=document.createElement('button');b.type='button';b.textContent=text;b.className=cls;b.disabled=true;controls.append(b);return b;}
 const previous=button('Previous','atlas-monthly-previous'),next=button('Next','atlas-monthly-next'),play=button('Play monthly profiles','atlas-monthly-play');
 const status=document.createElement('p');status.className='atlas-monthly-status';status.setAttribute('role','status');status.textContent='Loading saved monthly section…';section.append(status);
 const chart=document.createElementNS(api.ns,'svg');chart.classList.add('atlas-monthly-chart');chart.setAttribute('viewBox','0 0 600 310');chart.setAttribute('role','img');section.append(chart);
 const map=document.createElementNS(api.ns,'svg');map.classList.add('atlas-observed-section-map','atlas-monthly-map');map.setAttribute('role','group');section.append(map);
 const note=document.createElement('p');note.textContent='Points are satellite-product grid samples: teal eastward, purple westward, gray missing. Activate a sample for its value. Dashed boundaries enclose the selected positive-flow component of each monthly mean. Nominal 15 m surface product; scientific review pending. These are not current axes, instrument casts or annual whole-current dimensions. Playback steps through saved months without interpolation.';section.append(note);
 const sampleInfo=document.createElement('p');sampleInfo.className='atlas-monthly-sample-info';sampleInfo.setAttribute('role','status');section.append(sampleInfo);
 const details=document.createElement('a');details.className='atlas-monthly-details';details.textContent='All monthly profiles, brackets and calculation rules →';details.href=source.url;section.append(details);
 function stop(){if(timer!==null)clearInterval(timer);timer=null;play.textContent='Play monthly profiles';}
 function valid(doc){
  return doc?.schema==='osw.current-monthly-section-diagnostic.v1'&&'current:'+doc.current_id===current.id&&doc.status==='derived_width_candidate_requires_scientific_review'&&doc.year===2013&&doc.width_metric==='connected_positive_zonal_component_of_equal_sample_monthly_mean'&&doc.boundary_rule==='first_zero_crossing_on_each_side_of_largest_eligible_peak_in_2_to_10N'&&doc.peak_eligibility_m_s===.1&&doc.section_longitude_degrees_east===-140&&doc.nominal_depth_coordinate_m===15&&doc.is_climatology===false&&doc.whole_current_representative===false&&doc.width_rank_eligible===false&&doc.is_confidence_interval===false&&doc.monthly_width_is_mean_of_instantaneous_widths===false&&doc.seasonal_playback_eligible===false&&['whole_current_width_km','whole_current_length_km','annual_width_range_km','annual_length_range_km'].every(key=>doc[key]===null)&&Array.isArray(doc.months)&&doc.months.length===12&&doc.months.every((m,i)=>m.month===i+1&&m.id===`oscar-necc-140w-2013-${String(i+1).padStart(2,'0')}`&&m.label===`2013-${String(i+1).padStart(2,'0')}`&&Number.isInteger(m.sample_count)&&m.sample_count>=5&&Array.isArray(m.sample_times)&&m.sample_times.length===m.sample_count&&m.sample_times.every(t=>/^2013-\d{2}-\d{2}T00:00:00Z$/.test(t)&&Number.isFinite(Date.parse(t))&&Number(t.slice(5,7))===m.month)&&Array.isArray(m.profile)&&m.profile.length===37&&m.profile.every((s,j)=>Number.isFinite(s.latitude)&&Math.abs(s.latitude-j/3)<1e-8&&(s.eastward_m_s===null||Number.isFinite(s.eastward_m_s)&&Math.abs(s.eastward_m_s)<=1))&&m.zero_crossing?.threshold_m_s===0&&(m.zero_crossing.span_km===null||Number.isFinite(m.zero_crossing.span_km)&&m.zero_crossing.span_km>0&&m.zero_crossing.status==='resolved_connected_component'&&Number.isFinite(m.zero_crossing.peak_latitude)&&m.zero_crossing.peak_latitude>=2&&m.zero_crossing.peak_latitude<=10&&m.zero_crossing.boundaries?.south?.status==='resolved'&&m.zero_crossing.boundaries?.north?.status==='resolved'&&m.zero_crossing.boundaries.south.latitude<m.zero_crossing.peak_latitude&&m.zero_crossing.boundaries.north.latitude>m.zero_crossing.peak_latitude)&&['south','north'].every(side=>{const b=m.zero_crossing.boundaries?.[side];return !b||b.latitude===null||Number.isFinite(b.latitude)&&b.latitude>=0&&b.latitude<=12;}));
 }
 const [cx,cy]=api.project([-140,6]),bounds=[cx-70,cy-35,140,70];
 function point(parent,sample,month,local){
  const [x,y]=api.project([-140,sample.latitude]);const width=local?bounds[2]:Number(api.svg.getAttribute('viewBox').split(' ')[2]);
  const text=`${month.label} · ${sample.latitude.toFixed(2)}° N, 140° W · ${sample.eastward_m_s===null?'missing velocity':sample.eastward_m_s.toFixed(3)+' m/s zonal velocity ('+(sample.eastward_m_s>0?'eastward':sample.eastward_m_s<0?'westward':'zero')+')'} · ${month.sample_count} archived samples`;
  const group=api.make('g',{class:'atlas-observed-station atlas-monthly-station',tabindex:0,role:'button','aria-label':text},parent);group.dataset.currentId=current.id;group.dataset.atlasLabel=text;
  api.make('title',{},group).textContent=text;
  api.make('circle',{cx:x,cy:y,r:width/1480*5,fill:sample.eastward_m_s===null?'#a6aeb1':sample.eastward_m_s>=0?'#64dfce':'#d7a6e6','vector-effect':'non-scaling-stroke'},group);
  api.make('text',{x:x+width/1480*10,y:y-width/1480*8,'font-size':width/1480*16},group).textContent=`${sample.latitude.toFixed(2)}° N`;
  function activate(){if(!disposed)sampleInfo.textContent=text+'. This is a monthly surface-product mean, not an instrument observation.';}
  group.addEventListener('click',()=>{if(!api.wasDragged())activate();});group.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();activate();}});
 }
 function render(){
  if(disposed||!data)return;
  const month=data.months.find(m=>m.id===select.value),index=month.month-1,result=month.zero_crossing;
  previous.disabled=index===0;next.disabled=index===11;play.disabled=index===11;
  if(index===11)stop();
  const span=result.span_km===null?'span unresolved':`about ${Math.round(result.span_km/10)*10} km connected-component span`;
  status.textContent=`${month.label} · ${month.sample_count} archived samples · ${span}. Width of monthly mean zonal flow; not mean instantaneous width or climatology.`;
  document.getElementById('route-atlas-status').textContent=current.label+' · '+status.textContent;
  overlay?.remove();overlay=api.make('g',{class:'atlas-monthly-overlay'},api.layer);api.svg.classList.add('has-observed-samples');
  map.replaceChildren();map.setAttribute('viewBox',bounds.join(' '));map.setAttribute('aria-label',`${current.label}: ${month.label}, surface-product sample section at 140 W, 0–12 N; not current axis.`);
  api.make('image',{href:'../figures/ocean-motion-closeup-ground.svg',x:60,y:90,width:1480,height:740,opacity:.6},map);
  for(const sample of month.profile){point(overlay,sample,month,false);point(map,sample,month,true);}
  chart.replaceChildren();chart.setAttribute('aria-label',`${month.label}: monthly zonal velocity by latitude, 0–12 N and -1 to 1 m/s; ${span}.`);
  const px=lat=>45+lat*45,py=u=>140-u*120;
  for(let lat=0;lat<=12;lat+=2){api.make('line',{x1:px(lat),x2:px(lat),y1:20,y2:260,stroke:'#dbe7e7'},chart);api.make('text',{x:px(lat),y:279,'text-anchor':'middle','font-size':14,fill:'#133c49'},chart).textContent=lat;}
  for(const u of [-1,0,1]){api.make('line',{x1:45,x2:585,y1:py(u),y2:py(u),stroke:u===0?'#465f6c':'#dbe7e7'},chart);api.make('text',{x:38,y:py(u)+5,'text-anchor':'end','font-size':14,fill:'#133c49'},chart).textContent=u;}
  let path='',gap=true;for(const s of month.profile){if(s.eastward_m_s===null){gap=true;continue;}path+=`${gap?'M':'L'}${px(s.latitude)} ${py(s.eastward_m_s)} `;gap=false;}
  api.make('path',{d:path,fill:'none',stroke:'#087f88','stroke-width':3},chart);
  for(const b of Object.values(result.boundaries)){if(b.latitude===null)continue;api.make('line',{x1:px(b.latitude),x2:px(b.latitude),y1:20,y2:260,stroke:'#a76509','stroke-width':2,'stroke-dasharray':'5 5'},chart);for(const parent of [overlay,map]){const [x,y]=api.project([-140,b.latitude]);api.make('path',{d:`M${x-2} ${y}L${x+2} ${y}`,stroke:'#ffc663','stroke-width':3,'vector-effect':'non-scaling-stroke',class:'atlas-monthly-boundary'},parent);}}
  api.make('text',{x:310,y:301,'text-anchor':'middle','font-size':14,fill:'#133c49'},chart).textContent='Latitude (°N)';
  api.make('text',{x:13,y:140,transform:'rotate(-90 13 140)','text-anchor':'middle','font-size':13,fill:'#133c49'},chart).textContent='Zonal velocity (m/s)';
  sampleInfo.textContent='Hover or focus for latitude; activate a sample for its signed zonal velocity.';
  details.href=source.url+'?month='+encodeURIComponent(month.label)+'#'+month.id;
  api.shareSelection(panel,current.id,null,null,month.id);api.refreshUpdates();
 }
 select.addEventListener('change',()=>{stop();render();});previous.addEventListener('click',()=>{stop();select.selectedIndex--;render();});next.addEventListener('click',()=>{stop();select.selectedIndex++;render();});
 play.addEventListener('click',()=>{if(timer!==null){stop();return;}play.textContent='Pause monthly profiles';timer=setInterval(()=>{if(disposed){stop();return;}select.selectedIndex++;render();},2200);});
 function onVisibility(){if(document.hidden)stop();}document.addEventListener('visibilitychange',onVisibility);
 (async()=>{try{const docs=await window.oswAtlasSourcesReady;const doc=docs['research/pacific-necc-oscar-2013-section-diagnostic.json'];if(!doc)throw Error('Checked monthly diagnostic unavailable');if(disposed)return;if(!valid(doc))throw Error('Unsupported monthly section evidence');data=doc;for(const m of data.months){const option=document.createElement('option');option.value=m.id;option.textContent=m.label;select.append(option);}select.value=data.months.some(m=>m.id===api.requestedSection)?api.requestedSection:data.months[0].id;select.disabled=false;
  if(api.svg.getAttribute('viewBox')===initialView)api.fit(data.months[0].profile.map(s=>[-140,s.latitude]));render();
 }catch(error){if(!disposed){status.textContent=error.message+'; the standalone review page remains available.';chart.style.display='none';map.style.display='none';}}})();
 return()=>{disposed=true;stop();document.removeEventListener('visibilitychange',onVisibility);overlay?.remove();api.svg.classList.remove('has-observed-samples');};
};
