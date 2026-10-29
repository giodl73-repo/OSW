"use strict";
window.renderCurrentDimensionEvidence=function(parent,scene,inspect,options={}){
  if(scene?.kind!=='published_current_dimension_evidence')return;
  const widths=Array.isArray(scene.width_records)?scene.width_records:[],events=Array.isArray(scene.event_records)?scene.event_records:[];
  if(!widths.length&&!events.length)return;
  const node=(tag,text,container)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;container.append(n);return n;};
  const link=(label,url,container)=>{const n=node('a',label,container);n.href=url;return n;};
  const svgNode=(tag,attrs,container)=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));container.append(n);return n;};
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const number=value=>finite(value)?value.toLocaleString('en-US'):'Unknown';
  inspect||=((collection,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));});
  const wrapper=node(options.collapsed?'details':'section',undefined,parent);wrapper.className='current-dimension-evidence';wrapper.style.cssText='min-width:0;overflow-wrap:anywhere';
  if(options.collapsed)node('summary',`${widths.length} regional width summaries${events.length?` · ${events.length} dated flow examples`:''}`,wrapper);
  const panel=options.collapsed?node('div',undefined,wrapper):wrapper;
  node('h3',scene.title,panel);node('p',scene.scope,panel);node('p',scene.definition,panel);
  const sourceLink=(row,container)=>{
    const source=row.source_file||row.source_report_file?row:scene.width_source_links?.[row.id]||row;
    const file=source.source_file||source.source_report_file;
    if(file)link('Source evidence record','query.html?source-q='+encodeURIComponent(JSON.stringify({document:file,pointer:source.source_pointer||'',limit:100})),node('p',undefined,container));
  };
  const widthMaximum=Math.max(140,...widths.flatMap(row=>Array.isArray(row.width_range_km)?row.width_range_km.filter(finite):finite(row.approximate_width_km)?[row.approximate_width_km]:[]));
  for(const row of widths){
    const card=node('article',undefined,panel);card.setAttribute('data-dimension-width-id',row.id);
    card.style.cssText='min-width:0;border:1px solid #b7ced2;border-radius:.5rem;padding:.8rem;margin:.8rem 0';
    node('h4',row.phase_label||row.width_metric||'Regional width summary',card);
    const nominal=row.measurement_type==='published_nominal_regional_angular_width';
    const range=row.width_range_km,hasRange=Array.isArray(range)&&range.length===2&&range.every(finite)&&range[0]<=range[1];
    const central=finite(row.approximate_width_km)?row.approximate_width_km:null;
    node('p',hasRange?`About ${number(range[0])}–${number(range[1])} km`:central===null?'Width: Unknown':`About ${number(central)} km`,card);
    if(hasRange||central!==null){
      const maximum=widthMaximum;
      const chart=svgNode('svg',{viewBox:'0 0 300 56',role:'img','aria-label':hasRange?`Reported regional width range ${number(range[0])} to ${number(range[1])} km. Study summary, not annual extrema or error bars.`:nominal?`Derived nominal regional latitude span about ${number(central)} km. No physical edge coordinates or annual range.`:`Reported regional width about ${number(central)} km.`,},card);
      chart.style.cssText='display:block;width:100%;max-width:600px;height:auto';
      const x=value=>12+value/maximum*276;
      svgNode('line',{x1:12,x2:288,y1:20,y2:20,stroke:'#cadbdf','stroke-width':2},chart);
      if(hasRange)svgNode('line',{x1:x(range[0]),x2:x(range[1]),y1:20,y2:20,stroke:'#087f8c','stroke-width':10},chart);
      else svgNode('circle',{cx:x(central),cy:20,r:5,fill:'#98632b'},chart);
      node('p',`Width scale: 0–${number(maximum)} km. Studies retain separate definitions and periods.`,card);
    }
    node('p',row.range_interpretation||(nominal?'Nominal latitude-band conversion; paired physical edges and annual variability remain unknown.':'Regional survey summary; variability range unspecified.'),card);
    node('p',row.vertical_scope||row.layer||'Fixed width layer: Unknown',card);
    if(row.mean_section_context){
      const context=row.mean_section_context,period=context.averaging_period_months;
      node('p',`${context.section_id} / ${context.source_flow_label}${period?` · Mean velocity profile, ${period.start} to ${period.end}`:''}`,card);
      if(row.boundary_rule)node('p',row.boundary_rule,card);
    }
    if(row.source_discrepancy_note)node('p',`Source discrepancy: ${row.source_discrepancy_note}`,card);
    if(row.source_quality_note)node('p',row.source_quality_note,card);
    node('p','Seasonal width range: Unknown. Numerical uncertainty: Unknown.',card);
    const action=node('button','Inspect width record',card);action.type='button';action.onclick=()=>inspect('widths',row.id);sourceLink(row,card);
  }
  if(events.length){
    node('h4',`${events.length} matching dated flow example${events.length===1?'':'s'}`,panel);
    node('p','Selected source snapshots in date order. No event widths were extracted; missing dates are not interpolated.',panel);
    const list=node('ol',undefined,panel);list.style.cssText='padding-left:1.4rem';
    const sorted=[...events].sort((a,b)=>String(a.date).localeCompare(String(b.date)));
    for(const row of sorted){
      const item=node('li',undefined,list);item.setAttribute('data-flow-event-id',row.id);item.style.cssText='margin:.7rem 0;min-width:0';
      node('strong',`${row.date} · ${row.source_panel}`,item);node('p',row.description,item);
      const action=node('button','Inspect dated event',item);action.type='button';action.onclick=()=>inspect('current_reported_flow_events',row.id);sourceLink(row,item);
    }
  }
  link(scene.source_label||'Original mooring study',scene.source_url,node('p',undefined,panel));
  link('Full evidence context chart','../'+scene.figure,node('p',undefined,panel));
  if(scene.entity_id)link('Open current atlas','reference-routes.html?atlas-feature='+encodeURIComponent(scene.entity_id)+'#route-atlas',node('p',undefined,panel));
};
