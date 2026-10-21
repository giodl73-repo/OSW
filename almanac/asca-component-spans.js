"use strict";
window.renderAscaComponentSpans=function(container,scene,inspect,options={}){
  if(!scene||scene.kind!=='asca_dated_component_spans')return;
  const section=document.createElement('section');section.className='asca-component-spans';section.style.cssText='max-width:100%;min-width:0;border:1px solid #587681;padding:.8rem;margin:1rem 0;box-sizing:border-box';container.append(section);
  const node=(tag,text,parent=section)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  const link=(label,href,parent=section)=>{const n=node('a',label,parent);n.href=href;n.style.cssText='display:inline-flex;align-items:center;min-height:44px';return n;};
  const sourceLink=(label,document,pointer,parent=section)=>link(label,'query.html?source-q='+encodeURIComponent(JSON.stringify({document,pointer,limit:100})),parent);
  const fmt=x=>x===null?'Unresolved':Number(x).toLocaleString('en',{maximumFractionDigits:1});
  node('h4',scene.title);
  node('p','330 resolved / 931 dated profiles at the primary 50% threshold; 601 unresolved. Fixed-array southwestward component spans, not flow-normal current widths.');
  if(scene.measurement_query)link('Query all dated section measurements','query.html?q='+encodeURIComponent(JSON.stringify(scene.measurement_query)),node('p',''));
  const details=node('details',undefined);details.open=Boolean(options.open);const summary=node('summary','View dated spans, unresolved cases and source',details);summary.style.cssText='min-height:44px;padding:.35rem 0';
  const figure=node('figure',undefined,details);figure.style.margin='1rem 0';const image=node('img',undefined,figure);image.src='../'+scene.figure_file;image.alt=scene.figure_alt;image.loading='lazy';image.style.cssText='display:block;width:100%;height:auto;background:white';
  node('figcaption',scene.figure_alt,figure);link('Open component-span figure at full size','../'+scene.figure_file,figure);
  for(const caution of scene.cautions)node('p',caution,details);
  node('p','Local alignment is the angle between the velocity vector at the selected peak and the array normal. It is a local indicator, not a section-wide flow axis or a correction to the span. Missing along-array velocity leaves this angle unavailable.',details);
  const label=node('label','Recorded year and month ',details),select=node('select',undefined,label);select.style.cssText='min-height:44px;max-width:100%';
  for(const month of scene.months){const value=month.year+'-'+String(month.month).padStart(2,'0');const option=node('option',value+(month.complete_calendar_time_support?'':' / partial calendar month'),select);option.value=value;}
  const status=node('p','',details);status.setAttribute('aria-live','polite');
  const summaries=node('div',undefined,details),rows=node('div',undefined,details);
  function table(parent,caption,columns,minWidth){
    const scroll=node('div',undefined,parent);scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label',caption+'; scroll horizontally');scroll.style.cssText='max-width:100%;overflow-x:auto';
    const t=node('table',undefined,scroll);t.style.cssText='width:100%;min-width:'+minWidth+'px;border-collapse:collapse;font-size:.9rem';node('caption',caption,t).style.textAlign='left';
    const header=node('tr',undefined,node('thead',undefined,t));for(const title of columns){const th=node('th',title,header);th.scope='col';th.style.cssText='padding:.4rem;text-align:left';}
    return node('tbody',undefined,t);
  }
  const rowCells=(body,values)=>{const row=node('tr',undefined,body);for(const value of values){const cell=node('td',value,row);cell.style.cssText='padding:.4rem;border-bottom:1px solid #587681';}return row;};
  function draw(){
    const month=scene.months[select.selectedIndex];const selected=scene.profiles.filter(p=>p.year===month.year&&p.month===month.month);
    status.textContent=`${selected.length} original profiles; ${month.outcomes[1].resolved_profiles} primary spans resolve. ${month.complete_calendar_time_support?'Full nominal calendar schedule':'Partial calendar month'}; missing boundaries remain unresolved.`;
    summaries.replaceChildren();rows.replaceChildren();
    const body=table(summaries,'Threshold sensitivity: sampled summaries condition on resolved cases; not error bars or annual ranges.',['Peak fraction','Resolved / attempted','Minimum (km)','Median (km)','Maximum (km)'],580);
    for(const outcome of month.outcomes)rowCells(body,[Math.round(outcome.fraction*100)+'%'+(outcome.fraction===.5?' primary':''),outcome.resolved_profiles+' / '+outcome.attempted_profiles,fmt(outcome.resolved_span_min_km),fmt(outcome.resolved_span_median_km),fmt(outcome.resolved_span_max_km)]);
    const samples=table(rows,'Every source timestamp in this month, including unresolved primary outcomes. Grid brackets are interpolation support, not uncertainty.',['Source UTC time','50% span (rounded km)','Grid-bracket interval (km)','Peak −v (m/s)','Local alignment (°)','Boundary status','Exact sources'],1100);
    for(const profile of selected){
      const c=profile.cases[1],edges=[c.smaller_distance_edge?.status,c.larger_distance_edge?.status];
      const reason=edges.map((e,i)=>e==='unresolved_missing_barrier'?(i===0?'Smaller':'Larger')+' distance edge blocked by missing data':e==='unresolved_domain_truncation'?(i===0?'Smaller':'Larger')+' distance edge exceeds section support':null).filter(Boolean).join(' / ')||(c.span_km===null?'No usable peak above the declared minimum':'Both boundaries resolved');
      const row=rowCells(samples,[profile.observed_at,fmt(c.rounded_span_km),c.grid_bracket_separation_interval_km?.map(fmt).join('–')||'Unavailable',profile.peak_v_m_s===null?'Unavailable':fmt(-profile.peak_v_m_s),profile.peak_alignment_indicator_deg===null?'Unavailable':fmt(profile.peak_alignment_indicator_deg),reason]);
      const cell=node('td',undefined,row);cell.style.padding='.4rem';
      sourceLink('Inspect derived outcome '+profile.source_time_index,scene.source_file,'/profiles/'+profile.source_time_index,cell);
      sourceLink('Original velocity profile '+profile.source_time_index,scene.raw_source_file,profile.source_pointer,cell);
    }
  }
  select.addEventListener('change',draw);draw();
  sourceLink('Query all 931 dated outcomes',scene.source_file,'/profiles',node('p','',details));
  sourceLink('Inspect exact component-span source document',scene.source_file,'',node('p','',details));
  link('Provider dataset',scene.source_url,node('p','',details));node('p',scene.source_citation,details);
};
