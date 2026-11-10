"use strict";
(() => {
  let shared=null;
  function client(){
    if(shared)return shared;
    shared=(async()=>{
      const worker=new Worker('index-worker.js?v=eac-source-1'),pending=new Map();let serial=0,failed=null;
      const fail=error=>{failed=error;for(const item of pending.values()){clearTimeout(item.timer);item.reject(error);}pending.clear();worker.terminate();};
      worker.onerror=()=>fail(Error('Checked EAC source worker failed'));
      worker.onmessage=({data})=>{const item=pending.get(data.id);if(!item)return;pending.delete(data.id);clearTimeout(item.timer);data.result.ok?item.resolve(data.result):item.reject(Error(data.result.error));};
      const request=(action,value)=>failed?Promise.reject(failed):new Promise((resolve,reject)=>{const id=++serial,timer=setTimeout(()=>fail(Error('Checked EAC source request timed out')),90000);pending.set(id,{resolve,reject,timer});worker.postMessage({id,action,value});});
      await request('load');const {binary}=await request('cartography_binary');
      return {request,project:await window.createOswCartography(binary)};
    })();return shared;
  }
  window.renderEacSourceFields=function(container,scene,inspect,options={}){
    if(!scene||scene.kind!=='eac_daily_source_fields')return;
    const section=document.createElement('section');section.className='eac-source-fields';section.style.cssText='max-width:100%;min-width:0;border:1px solid #587681;padding:.8rem;margin:1rem 0;box-sizing:border-box';container.append(section);
    const node=(tag,text,parent=section)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
    const svgNode=(tag,attrs,parent,text)=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.append(n);return n;};
    const link=(label,href,parent=section)=>{const n=node('a',label,parent);n.href=href;n.style.cssText='display:inline-flex;align-items:center;min-height:44px';return n;};
    const fmt=v=>v===null?'Unavailable':Number(v).toLocaleString('en',{maximumFractionDigits:3});
    const sourceUrl=query=>'query.html?source-q='+encodeURIComponent(JSON.stringify(query));
    node('h4',scene.title);node('p','3,770 daily source records at 100 m: 3,141 dates have data; 629 dates retain missing values. Processed, SOM-filled and spatially mapped fields; physical current widths remain unadmitted.');
    const details=node('details',undefined);details.open=Boolean(options.open);node('summary','Explore recorded days, source fields and uncertainty',details).style.cssText='min-height:44px;padding:.35rem 0';
    node('p','Five-day filtering and daily output make adjacent records dependent. Supplied uncertainty values are shown as source fields; no universal confidence level or lateral-width error is inferred. Zero uncertainty does not establish absence of error.',details);
    node('p','The fixed grid has roughly 1–2 km output spacing and much wider mooring separation. Two 100 m bottom cells prescribe zero velocity when data is present. These source boundary values are not independent observations of current absence.',details);
    const overview=node('details',undefined,details);node('summary','Whole-period source overview and method notes',overview).style.minHeight='44px';
    const figure=node('figure',undefined,overview);figure.style.margin='1rem 0';const image=node('img',undefined,figure);image.src='../'+scene.figure_file;image.alt=scene.figure_alt;image.loading='lazy';image.style.cssText='display:block;width:100%;height:auto;background:white';
    node('figcaption',scene.figure_alt,figure);link('Open full-size source overview','../'+scene.figure_file,figure);
    for(const note of scene.documentary_disagreements)node('p',note.topic+': '+(note.file_header||'Metadata version 23 and source data version 19 are distinct.')+' '+(note.descriptor||note.descriptor_and_collection_metadata||'')+' '+note.status.replaceAll('_',' '),overview);
    const controls=node('div',undefined,details);controls.style.cssText='display:flex;flex-wrap:wrap;gap:.5rem;max-width:100%';
    const monthLabel=node('label','Recorded year and month ',controls),month=node('select',undefined,monthLabel);
    const dayLabel=node('label','Source date (UTC) ',controls),day=node('select',undefined,dayLabel);
    for(const label of [monthLabel,dayLabel])label.style.cssText='display:grid;gap:.3rem;min-width:0;max-width:100%';
    for(const select of [month,day])select.style.cssText='min-height:44px;max-width:100%;min-width:0';
    for(const m of scene.months){const value=m.year+'-'+String(m.month).padStart(2,'0');const option=node('option',value+(m.complete_nominal_calendar_schedule?'':' / partial calendar schedule'),month);option.value=value;}
    const previous=node('button','Previous day',controls),next=node('button','Next day',controls),play=node('button','Play days in this month',controls);
    for(const button of [previous,next,play]){button.type='button';button.style.minHeight='44px';}
    const status=node('p','Source data loads when this section is opened.',details);status.setAttribute('role','status');status.dataset.eacSourceStatus='';
    node('p','On narrow screens, scroll each chart horizontally. Lines break at source missing values. Shading is plus/minus the supplied uncertainty field, not an assigned confidence interval.',details);
    const map=node('div',undefined,details),charts=node('div',undefined,details);
    const core=scene.core_spans;let coreRows=[];
    const corePanel=core?node('section',undefined,details):null;
    let scenario=null,threshold=null,coreChart=null,coreText=null,coreSummary=null;
    if(corePanel){
      corePanel.className='eac-section-core-spans';corePanel.style.cssText='max-width:100%;min-width:0;border-top:1px solid #81949d;margin-top:1rem';
      node('h4','Exploratory section-core spans at 100 m',corePanel);
      node('p','2,883 dates resolve both section edges at the central half-peak rule; 887 do not. These are distances along the sampling section, not flow-normal physical current widths or annual extrema. Bottom cells are excluded from this diagnostic while remaining unchanged in the original source fields.',corePanel);
      node('p','Green rings on the map mark approximate source-section intersections for the selected case. Their geographic positions interpolate within the source cells; they are not mapped current edges. The crossing cells and distances are also listed below.',corePanel);
      const choices=node('div',undefined,corePanel);choices.style.cssText='display:flex;flex-wrap:wrap;gap:.5rem;max-width:100%';
      const label=node('label','Component sensitivity ',choices);label.style.cssText='display:grid;min-width:0;max-width:100%';scenario=node('select',undefined,label);scenario.setAttribute('aria-label','Component sensitivity');
      for(const [value,title] of [['central','Central projected component'],['minus_supplied_component_magnitudes','Minus supplied component magnitudes'],['plus_supplied_component_magnitudes','Plus supplied component magnitudes']]){const option=node('option',title,scenario);option.value=value;}
      const fractionLabel=node('label','Peak fraction ',choices);fractionLabel.style.cssText='display:grid;min-width:0;max-width:100%';threshold=node('select',undefined,fractionLabel);threshold.setAttribute('aria-label','Peak fraction');
      for(const value of core.fractions){const option=node('option',Math.round(value*100)+'%'+(value===.5?' / primary':''),threshold);option.value=String(value);}threshold.value='0.5';
      for(const select of [scenario,threshold])select.style.cssText='min-height:44px;min-width:0;max-width:100%';
      coreSummary=node('p','',corePanel);coreSummary.dataset.eacCoreSupport='';coreChart=node('div',undefined,corePanel);coreText=node('div',undefined,corePanel);coreText.setAttribute('aria-live','polite');
      const overview=node('details',undefined,corePanel);node('summary','All-date outcomes, sensitivity and fixed source examples',overview).style.minHeight='44px';
      const img=node('img',undefined,overview);img.src='../'+core.figure_file;img.alt=core.figure_alt;img.loading='lazy';img.style.cssText='display:block;width:100%;height:auto;background:white';
      for(const note of core.limitations)node('p',note,overview);
      link('Query all 3,770 section-core outcomes',sourceUrl({document:core.raw_profile_file,pointer:'/profiles',limit:100}),node('p','',overview));
      const calendar=node('details',undefined,corePanel);calendar.className='eac-calendar-comparison';
      node('summary','Compare calendar months and years',calendar).style.minHeight='44px';
      node('p','The primary 50% case is pooled by calendar month and shown separately by year. Counts include unresolved dates. Thin segments show resolved min/max, thick segments show the 10th–90th percentiles, and points show medians. These are conditional distributions of mapped dates, not physical widths or confidence intervals.',calendar);
      const calendarImage=node('img',undefined,calendar);calendarImage.src='../figures/eac-section-calendar-distributions.svg';calendarImage.loading='lazy';
      calendarImage.alt='EAC 100 m section-span distributions for twelve calendar months and eleven years, with resolved and attempted date counts. 2014 has no resolved dates; 2012 and 2022 are partial calendar years.';
      calendarImage.style.cssText='display:block;width:100%;height:auto;background:white';
      link('Open full-size calendar comparison',calendarImage.src,node('p','',calendar));
      for(const [label,pointer] of [['Query calendar-month distributions','/calendar_month_groups'],['Query year distributions and missing-date counts','/calendar_year_groups']])link(label,sourceUrl({document:'research/eac-section-calendar-distributions.json',pointer,limit:25}),node('p','',calendar));
      scenario.addEventListener('change',()=>drawCore());threshold.addEventListener('change',()=>drawCore());
    }
    const cellLabel=node('label','Source position ',details),cell=node('select',undefined,cellLabel);cell.style.cssText='min-height:44px;max-width:100%';
    cell.setAttribute('aria-label','Source position');
    for(let i=0;i<scene.geometry.longitude_latitude_points.length;i++){const option=node('option',i+' · '+fmt(scene.geometry.distance_from_first_grid_point_m[i]/1000)+' km along source array',cell);option.value=String(i);}
    const reading=node('div',undefined,details);reading.setAttribute('aria-live','polite');reading.dataset.eacSourceReading='';const sources=node('p','',details);
    link('Query all 3,770 daily source records',sourceUrl({document:scene.raw_source_file,pointer:'/profiles',limit:100}),node('p','',details));
    link('Inspect source quality and methods',sourceUrl({document:scene.source_file,pointer:'',limit:100}),node('p','',details));
    link('Provider dataset',scene.source_url,node('p','',details));node('p',scene.source_citation,details);
    if(inspect){const button=node('button','Inspect source diagnostic',details);button.type='button';button.style.minHeight='44px';button.onclick=()=>inspect('diagnostics',scene.diagnostic_id);}
    const reduced=matchMedia('(prefers-reduced-motion: reduce)');let timer=null,rows=[],current=null,project=null,generation=0,loaded=false,busy=false;
    const stop=()=>{if(timer!==null)clearTimeout(timer);timer=null;play.textContent='Play days in this month';play.setAttribute('aria-pressed','false');};
    function buttons(){previous.disabled=busy||!rows.length||day.selectedIndex===0;next.disabled=busy||!rows.length||day.selectedIndex===rows.length-1;play.disabled=busy||!rows.length||reduced.matches;day.disabled=busy||!rows.length;}
    function showCell(){
      reading.replaceChildren();if(!current)return;const i=Number(cell.value),point=scene.geometry.longitude_latitude_points[i],bottom=scene.geometry.bottom_depth_m[i];
      node('p',`Position ${i}: ${fmt(point[0])}° E, ${fmt(point[1])}° N; source bottom ${fmt(bottom)} m. ${bottom<=100?'The selected 100 m level is at or below this source bottom.':'The selected level is above the source bottom.'}`,reading);
      for(const f of scene.fields)node('p',`${f.label}: ${fmt(current.fields[f.key][i])} ${f.unit}; supplied uncertainty ${fmt(current.fields[f.uncertainty_key][i])} ${f.unit}.`,reading);
      for(const circle of map.querySelectorAll('[data-eac-position]'))circle.setAttribute('stroke',Number(circle.dataset.eacPosition)===i?'#131c24':'none');
    }
    function drawCore(){
      if(!corePanel||!current)return;const row=coreRows[day.selectedIndex];coreChart.replaceChildren();coreText.replaceChildren();
      if(!row||row.source_time_index!==current.source_time_index){coreSummary.textContent='Section-core diagnostic unavailable for this date.';return;}
      const name=scenario.value,fraction=Number(threshold.value),variant=row.scenarios[name],c=variant.cases.find(c=>c.fraction===fraction),sign=name==='central'?0:name.startsWith('minus')?-1:1;
      corePanel.dataset.eacCoreIndex=String(row.source_time_index);window.oswEacCoreSelection={profile:row,scenario:name,fraction,case:c,source_sha256:core.raw_profile_sha256};
      const m=core.months[month.selectedIndex],support=m.outcomes.find(o=>o.scenario===name&&o.fraction===fraction),overall=core.overall_outcomes.find(o=>o.scenario===name&&o.fraction===fraction);
      coreSummary.textContent=`${current.source_time_utc} · selected month: ${support.resolved_dates} resolved / ${support.attempted_dates} attempted dates; whole source period: ${overall.resolved_dates} / ${overall.attempted_dates}. Missing and weak dates remain in these denominators. Sensitivity cases are not confidence limits or extra observations.`;
      const q=row.section_normal_velocity_m_s,a=row.projected_supplied_magnitudes_m_s,values=q.map((v,i)=>v===null||sign!==0&&a[i]===null?null:v+sign*(a[i]||0));
      const distances=core.geometry.distance_m,maxDistance=distances.at(-1),[low,high]=core.y_domain,x=d=>65+d/maxDistance*590,y=v=>220-(v-low)/(high-low)*190;
      const scroll=node('div',undefined,coreChart);scroll.style.cssText='max-width:100%;overflow-x:auto';scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Section-core component chart; scroll horizontally');
      const svg=svgNode('svg',{viewBox:'0 0 680 280',role:'img','aria-label':'Selected section-normal component and threshold. Sampling brackets mark interpolation support, not measurement uncertainty.'},scroll);svg.style.cssText='display:block;width:100%;min-width:600px';
      const bottom=core.geometry.bottom_depth_m.map((v,i)=>v<=100?distances[i]:null).filter(v=>v!==null);
      svgNode('rect',{x:65,y:30,width:x(bottom.at(-1))-65,height:190,fill:'#dfae8f',opacity:.5},svg);
      for(let i=0;i<=4;i++){const value=low+(high-low)*i/4;svgNode('line',{x1:65,x2:655,y1:y(value),y2:y(value),stroke:'#d0dce1'},svg);svgNode('text',{x:58,y:y(value)+4,'text-anchor':'end','font-size':12},svg,fmt(value));}
      for(const km of [0,50,100,150])svgNode('text',{x:x(km*1000),y:240,'text-anchor':'middle','font-size':12},svg,String(km));
      svgNode('text',{x:350,y:267,'text-anchor':'middle','font-size':12},svg,'Along fixed section (km); component m/s; not physical width');
      let run=[];const flush=()=>{if(run.length)svgNode('polyline',{points:run.map(i=>`${x(distances[i])},${y(values[i])}`).join(' '),fill:'none',stroke:'#155a73','stroke-width':2},svg);run=[];};
      values.forEach((v,i)=>{if(v===null)flush();else run.push(i);});flush();
      if(c.threshold_m_s!==null)svgNode('line',{x1:65,x2:655,y1:y(c.threshold_m_s),y2:y(c.threshold_m_s),stroke:'#744989','stroke-dasharray':'5 3'},svg);
      const reason=status=>({unresolved_section_domain:'source section ends before a crossing',unresolved_source_bottom_at_or_above_level:'excluded source bottom cell blocks the crossing',unresolved_missing_paired_velocity:'missing source velocity blocks the crossing',unresolved_missing_supplied_uncertainty:'missing supplied uncertainty blocks this sensitivity case'}[status]||status.replaceAll('_',' '));
      node('p',c.section_span_km===null?'Unresolved: '+(c.status==='unresolved_no_eligible_component'?'no eligible paired component data':c.status==='unresolved_peak_below_0_3_m_s'?'positive peak is below 0.3 m/s':'both section edges are not bracketed')+'.':`Resolved section span: ${c.rounded_section_span_km} km. Sampling-cell separation support: ${c.sampling_support_interval_km.map(fmt).join('–')} km; not measurement error.`,coreText);
      for(const [label,e] of [['Shoreward',c.shoreward_edge],['Offshore',c.offshore_edge]]){
        if(!e)continue;
        if(e.status==='resolved'){
          const [start,end]=e.distance_bracket_m;svgNode('rect',{x:x(start),y:30,width:x(end)-x(start),height:190,fill:'#9aad83',opacity:.45},svg);svgNode('line',{x1:x(e.distance_m),x2:x(e.distance_m),y1:30,y2:220,stroke:'#4b633a'},svg);
          node('p',`${label} crossing: ${fmt(e.distance_m/1000)} km along section, source cells ${e.indices_in_distance_order.join('–')}, support ${e.distance_bracket_m.map(v=>fmt(v/1000)).join('–')} km.`,coreText);
        }else node('p',label+': '+reason(e.status)+'.',coreText);
      }
      const peak=variant.peak_source_components;
      if(peak)node('p',`Peak source index ${variant.peak_index}; projected component ${fmt(variant.peak_component_m_s)} m/s; original eastward ${fmt(peak.UCUR)}, northward ${fmt(peak.VCUR)} m/s; section bearing ${fmt(peak.bearing_deg)}°. Tangent/normal ratio ${fmt(peak.tangent_to_normal_ratio_not_width_correction)} is local alignment context, not a width correction.`,coreText);
      node('p','Orange shading: excluded source bottom cells. Green brackets: crossing interpolation cells. Curves stop at missing values. The original mapped source remains available above and through the exact-record links.',coreText);
      link('Inspect this exact section-core outcome',sourceUrl({document:core.raw_profile_file,pointer:'/profiles',filters:[{field:'record.source_time_index',op:'eq',value:row.source_time_index}],limit:1}),node('p','',coreText));
      const ground=map.querySelector('svg');
      if(ground){
        ground.querySelectorAll('[data-eac-core-crossing]').forEach(n=>n.remove());
        const view=ground.getAttribute('viewBox').split(' ').map(Number);
        for(const [side,e] of [['shoreward',c.shoreward_edge],['offshore',c.offshore_edge]]){
          if(!e||e.status!=='resolved')continue;
          const inside=core.geometry.longitude_latitude_points[e.inside_index],outside=core.geometry.longitude_latitude_points[e.outside_index],f=e.fraction_inside_to_outside;
          const coordinate=inside.map((v,i)=>v+f*(outside[i]-v)),p=project({op:'project',coordinates:coordinate}).point;
          const mark=svgNode('circle',{cx:p[0],cy:p[1],r:view[2]/110,fill:'none',stroke:'#4b633a','stroke-width':view[2]/350,'data-eac-core-crossing':side},ground);
          svgNode('title',{},mark,side+' section crossing, interpolated within source cells; not a geographic current edge');
        }
      }
    }
    function draw(){
      current=rows[day.selectedIndex];if(!current)return;buttons();charts.replaceChildren();map.replaceChildren();sources.replaceChildren();
      const count=current.fields.UCUR.filter((v,i)=>v!==null&&current.fields.VCUR[i]!==null).length;
      status.textContent=`${current.source_time_utc} · ${count} of 124 source positions have paired velocity. ${count?'Mapped/filled source fields; supplied uncertainty retains its provider meaning.':'No velocity data on this date; current absence is not established.'}`;
      section.dataset.eacSourceIndex=String(current.source_time_index);window.oswEacSourceSelection={profile:current,source_sha256:scene.raw_source_sha256};
      const coords=scene.geometry.longitude_latitude_points,view=project({op:'fit',coordinates:coords}).view_box;
      const svg=svgNode('svg',{viewBox:view.join(' '),role:'img','aria-label':'Fixed EAC source sampling grid on the OSW reference basemap. Blue: source data, orange: supplied bottom boundary, grey: missing. These are sampling positions, not current edges.'},map);svg.style.cssText='display:block;width:100%;height:auto;background:#e7f0f2';
      svgNode('image',{href:'../figures/ocean-motion-dashboard-ground.svg',x:60,y:90,width:1480,height:740,opacity:.65},svg);
      svgNode('path',{d:project({op:'path',coordinates:coords}).d,fill:'none',stroke:'#49626d','stroke-width':view[2]/500},svg);
      for(let i=0;i<coords.length;i++){const point=project({op:'project',coordinates:coords[i]}).point,available=current.fields.VCUR[i]!==null;
        const circle=svgNode('circle',{cx:point[0],cy:point[1],r:view[2]/300,fill:available?(scene.geometry.bottom_depth_m[i]<=100?'#be582e':'#155a73'):'#6e7881','stroke-width':view[2]/450,'data-eac-position':i},svg);
        svgNode('title',{},circle,`Source position ${i}: ${fmt(coords[i][0])} E, ${fmt(coords[i][1])} N; northward velocity ${fmt(current.fields.VCUR[i])} m/s`);circle.onclick=()=>{cell.value=String(i);showCell();};
      }
      node('p','Fixed source sampling positions on the approximate OSW reference basemap. Source geometry is constant; plotted fields change with the selected date. The position selector provides keyboard access.',map);
      const distances=scene.geometry.distance_from_first_grid_point_m,maxDistance=distances.at(-1);
      for(const f of scene.fields){
        const panel=node('section',undefined,charts);panel.dataset.eacField=f.key;node('h5',`${f.label} (${f.unit})`,panel);
        const scroll=node('div',undefined,panel);scroll.style.cssText='max-width:100%;overflow-x:auto';scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label',f.label+' source chart; scroll horizontally');
        const svg=svgNode('svg',{viewBox:'0 0 680 280',role:'img','aria-label':`${current.source_time_utc}: ${f.label}; original mapped source values and supplied uncertainty; missing values break the line.`},scroll);svg.style.cssText='display:block;width:100%;min-width:600px';
        const [low,high]=f.y_domain,x=d=>65+d/maxDistance*590,y=v=>220-(v-low)/(high-low)*190;
        for(let i=0;i<=4;i++){const value=low+(high-low)*i/4;svgNode('line',{x1:65,x2:655,y1:y(value),y2:y(value),stroke:'#d0dce1'},svg);svgNode('text',{x:58,y:y(value)+4,'text-anchor':'end','font-size':12},svg,fmt(value));}
        for(const km of [0,50,100,150])svgNode('text',{x:x(km*1000),y:240,'text-anchor':'middle','font-size':12},svg,String(km));
        svgNode('text',{x:350,y:267,'text-anchor':'middle','font-size':12},svg,'Distance along fixed source array (km); not current length');
        const values=current.fields[f.key],errors=current.fields[f.uncertainty_key];let run=[];
        const flush=()=>{if(!run.length)return;let band=[];const shade=()=>{if(band.length>1){const upper=band.map(i=>`${x(distances[i])},${y(values[i]+errors[i])}`),lower=[...band].reverse().map(i=>`${x(distances[i])},${y(values[i]-errors[i])}`);svgNode('polygon',{points:[...upper,...lower].join(' '),fill:'#b3d2df','fill-opacity':.7},svg);}band=[];};
          for(const i of run){if(errors[i]===null)shade();else band.push(i);}shade();svgNode('polyline',{points:run.map(i=>`${x(distances[i])},${y(values[i])}`).join(' '),fill:'none',stroke:'#155a73','stroke-width':2},svg);run=[];};
        for(let i=0;i<values.length;i++){if(values[i]===null)flush();else run.push(i);}flush();
        for(const row of scene.source_bottom_support){const i=row.source_position_index;if(values[i]!==null)svgNode('circle',{cx:x(distances[i]),cy:y(values[i]),r:3,fill:'#be582e'},svg);}
        node('p',`${values.filter(v=>v!==null).length} of 124 values available. Orange marks show source cells at or below 100 m bottom depth.`,panel);
      }
      link('Inspect this exact daily source record',sourceUrl({document:scene.raw_source_file,pointer:'/profiles',filters:[{field:'record.source_time_index',op:'eq',value:current.source_time_index}],limit:1}),sources);showCell();drawCore();
    }
    async function loadMonth(){
      stop();const token=++generation;busy=true;buttons();status.textContent='Loading checked daily source records…';
      try{
        const service=await client();project=service.project;const m=scene.months[month.selectedIndex];
        const result=await service.request('query',{document:scene.raw_source_file,pointer:'/profiles',filters:[{field:'record.year',op:'eq',value:m.year},{field:'record.month',op:'eq',value:m.month}],sort:{field:'record.source_time_index',direction:'asc'},limit:40});
        if(token!==generation)return;
        if(result.source_sha256!==scene.raw_source_sha256||result.rows.length!==m.source_records||result.total!==m.source_records)throw Error('EAC source selection/hash mismatch');
        rows=result.rows.map(r=>r.record);
        if(rows.some((r,i)=>r.source_time_index!==m.source_time_indices[i]||scene.fields.some(f=>r.fields[f.key]?.length!==124||r.fields[f.uncertainty_key]?.length!==124)))throw Error('Incomplete EAC source fields/order');
        if(core){
          const derived=await service.request('query',{document:core.raw_profile_file,pointer:'/profiles',filters:[{field:'record.year',op:'eq',value:m.year},{field:'record.month',op:'eq',value:m.month}],sort:{field:'record.source_time_index',direction:'asc'},limit:40});
          if(token!==generation)return;
          if(derived.source_sha256!==core.raw_profile_sha256||derived.total!==m.source_records||derived.rows.length!==m.source_records)throw Error('EAC core source/hash mismatch');
          coreRows=derived.rows.map(r=>r.record);
          if(coreRows.some((r,i)=>r.source_time_index!==m.source_time_indices[i]))throw Error('Incomplete EAC core chronology');
        }
        day.replaceChildren();for(const row of rows){const option=node('option',row.source_time_utc,day);option.value=String(row.source_time_index);}day.selectedIndex=0;busy=false;draw();
      }catch(error){if(token!==generation)return;rows=[];coreRows=[];current=null;busy=false;charts.replaceChildren();map.replaceChildren();reading.replaceChildren();sources.replaceChildren();if(coreChart){coreChart.replaceChildren();coreText.replaceChildren();coreSummary.textContent='Section-core diagnostic unavailable.';}buttons();status.textContent='Source fields unavailable: '+error.message;}
    }
    month.addEventListener('change',()=>{if(loaded)loadMonth();});day.addEventListener('change',()=>{stop();draw();});cell.addEventListener('change',showCell);
    previous.onclick=()=>{stop();day.selectedIndex--;draw();};next.onclick=()=>{stop();day.selectedIndex++;draw();};
    play.onclick=()=>{if(timer!==null){stop();return;}if(reduced.matches||!rows.length)return;if(day.selectedIndex===rows.length-1)day.selectedIndex=0;draw();play.textContent='Pause recorded days';play.setAttribute('aria-pressed','true');const step=()=>{if(day.selectedIndex===rows.length-1){stop();return;}day.selectedIndex++;draw();timer=setTimeout(step,1000);};timer=setTimeout(step,1000);};
    reduced.addEventListener('change',()=>{stop();buttons();});details.addEventListener('toggle',()=>{if(!details.open){stop();return;}if(!loaded){loaded=true;loadMonth();}});
    buttons();if(details.open){loaded=true;loadMonth();}
  };
})();
