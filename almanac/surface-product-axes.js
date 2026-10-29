"use strict";
window.oswSurfaceProductAxes=(()=>{
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const km=x=>finite(x)?`${x.toLocaleString('en-US',{maximumFractionDigits:1})} km`:'Withheld';
  const date=r=>`${r.year}-${String(r.month).padStart(2,'0')}`;
  const windowLabel=r=>`${r.window_deg_north.join('–')}°N`;
  const scene=(snapshot,id)=>snapshot?.surface_product_axis_scenes?.[id.replace(/^current:/,'')]||null;
  const paths=s=>(s?.readings||[]).filter(r=>finite(r.length_km)&&r.geometry?.type==='MultiLineString');
  const selection=(s,id)=>paths(s).find(r=>r.id===id)||paths(s).find(r=>r.month===1&&r.window_deg_north.join(',')==='8,18')||paths(s)[0]||null;
  const segments=row=>row?.geometry?.type==='MultiLineString'?row.geometry.coordinates:[];
  const queryUrl=(collection,id)=>'query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));
  const atlasUrl=r=>'reference-routes.html?atlas-feature='+encodeURIComponent(r.entity_id)+'&atlas-product-reading='+encodeURIComponent(r.id)+'#route-atlas';
  function draw({scene:s,currentId,parent,make,pathData,interactive,onSelect}){
    return paths(s).map(row=>{
      const line=make('path',{d:segments(row).map(part=>pathData(part)).join(' '),class:'route-atlas-product-axis','vector-effect':'non-scaling-stroke'},parent);
      line.dataset.currentId=currentId;line.dataset.productReadingId=row.id;
      line.dataset.productDefault=String(row.month===1&&row.window_deg_north.join(',')==='8,18');
      line.hidden=!(row.month===1&&row.window_deg_north.join(',')==='8,18');
      line.style.display=line.hidden?'none':'';
      interactive(line,`Pacific NEC · ${date(row)} · ${windowLabel(row)} · experimental regional product path · ${km(row.length_km)}`,()=>onSelect(row));
      return {row,line};
    });
  }
  return {finite,km,date,windowLabel,scene,paths,selection,segments,queryUrl,atlasUrl,draw};
})();
window.renderSurfaceProductAxes=function(parent,scene,inspect,options={}){
  if(scene?.kind!=='surface_product_axis_diagnostics')return ()=>{};
  const H=window.oswSurfaceProductAxes,{finite,km,date,windowLabel}=H;
  inspect||=((collection,id)=>{location.href=H.queryUrl(collection,id);});
  const node=(tag,text,p)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;p.append(n);return n;};
  const svgNode=(tag,attrs,p,text)=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;p.append(n);return n;};
  const panel=node('section',undefined,parent);panel.className='surface-product-axes';
  node('h3',scene.title,panel);node('p',scene.scope,panel);
  node('p','OSCAR2017.0 near-surface product, nominal 15 m coordinate. Equal-sample monthly means from dated 2013 archive frames; these are product estimates, not direct instrument sections.',panel);
  node('p',scene.playback_scope,panel);node('p',scene.method_span_scope,panel);
  const records=scene.selected_records||[],collection=scene.selected_collection;
  if(collection)node('p',`${records.length} matching ${collection} records. Charts use all matches, independently of table pagination.`,panel);
  const action=(label,name,id,p)=>{const b=node('button',label,p);b.type='button';b.addEventListener('click',()=>inspect(name,id));return b;};
  const link=(label,href,p)=>{const a=node('a',label,p);a.href=href;return a;};
  const readings=H.paths(scene),series=scene.series||[];
  let timer=null,observer=null,active=null;
  const stop=()=>{if(timer!==null)clearInterval(timer);timer=null;if(play)play.textContent='Play dated months';};
  let play=null;
  const reduced=typeof matchMedia==='function'?matchMedia('(prefers-reduced-motion: reduce)'):null;
  const onVisibility=()=>{if(document.hidden)stop();};
  document.addEventListener('visibilitychange',onVisibility);reduced?.addEventListener('change',stop);
  const cleanup=()=>{stop();observer?.disconnect();document.removeEventListener('visibilitychange',onVisibility);reduced?.removeEventListener('change',stop);};
  if(readings.length){
    const controls=node('div',undefined,panel);controls.className='product-axis-controls';
    const windowSelect=node('select',undefined,node('label','Analysis window ',controls));
    const monthSelect=node('select',undefined,node('label','Dated month ',controls));
    const windows=[...new Set(readings.map(r=>r.series_id))];
    for(const id of windows){const r=readings.find(r=>r.series_id===id),o=node('option',windowLabel(r),windowSelect);o.value=id;}
    play=node('button','Play dated months',controls);play.type='button';
    const status=node('p',undefined,panel);status.setAttribute('aria-live','polite');
    const map=svgNode('svg',{role:'img','aria-label':'Experimental monthly Pacific product path on a longitude–latitude reference grid'},panel);
    map.classList.add('product-axis-chart');
    const chart=svgNode('svg',{role:'img','aria-label':'Matching monthly regional product-path lengths, not annual physical bounds'},panel);
    chart.classList.add('product-axis-chart');
    const detail=node('p',undefined,panel),links=node('p',undefined,panel);links.className='product-axis-links';
    const months=()=>readings.filter(r=>r.series_id===windowSelect.value).sort((a,b)=>a.month-b.month);
    const initial=H.selection(scene,options.readingId);windowSelect.value=initial.series_id;
    function fillMonths(wanted){monthSelect.replaceChildren();for(const r of months()){const o=node('option',date(r),monthSelect);o.value=r.id;}monthSelect.value=months().some(r=>r.id===wanted)?wanted:months()[0].id;}
    function render(){
      active=readings.find(r=>r.id===monthSelect.value);if(!active)return;
      const width=Math.max(220,panel.getBoundingClientRect?.().width||720),height=Math.max(220,width*.38),left=48,right=width-20,top=20,bottom=height-38;
      const x=lon=>left+(lon-130)/110*(right-left),y=lat=>top+(26-lat)/22*(bottom-top);
      map.replaceChildren();map.setAttribute('viewBox',`0 0 ${width} ${height}`);
      for(const lon of (width<420?[130,180,240]:[130,150,180,210,240])){svgNode('line',{x1:x(lon),x2:x(lon),y1:top,y2:bottom,stroke:'#b8ccd4'},map);svgNode('text',{x:x(lon),y:height-12,'text-anchor':'middle','font-size':13},map,lon<=180?`${lon}°E`:`${360-lon}°W`);}
      for(const lat of [4,8,18,26]){svgNode('line',{x1:left,x2:right,y1:y(lat),y2:y(lat),stroke:'#b8ccd4'},map);svgNode('text',{x:left-6,y:y(lat)+4,'text-anchor':'end','font-size':13},map,`${lat}°N`);}
      for(const lat of active.window_deg_north)svgNode('line',{x1:left,x2:right,y1:y(lat),y2:y(lat),stroke:'#9c5073','stroke-dasharray':'4 4'},map);
      const path=svgNode('path',{d:active.native_vector_points.map(([lon,lat],i)=>`${i?'L':'M'}${x(lon)},${y(lat)}`).join(' '),fill:'none',stroke:'#087f8c','stroke-width':3,'vector-effect':'non-scaling-stroke',tabindex:0,role:'button','aria-label':`${date(active)} · ${windowLabel(active)} · inspect product path`},map);
      svgNode('title',{},path,`${date(active)} · ${windowLabel(active)} · ${km(active.length_km)}`);
      const open=()=>inspect('current_axis_readings',active.id);path.addEventListener('click',open);path.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}});
      status.textContent=`${date(active)} · ${windowLabel(active)} · regional path about ${active.approximate_length_km.toLocaleString()} km · ${active.sample_count} archive frames · ${active.boundary_contact_native_cells} window-boundary contacts.`;
      detail.textContent=`First/last archive timestamps: ${active.sample_times_utc[0]} / ${active.sample_times_utc.at(-1)}. Threshold ${active.threshold_m_s} m/s; penalty ${active.penalty_m_s} m/s; maximum vector angle ${active.maximum_angle_deg}°. Dashed lines are analysis limits; 130°E–120°W are fixed comparison gates, not current endpoints. This reference grid uses unwrapped Pacific longitude.`;
      links.replaceChildren();action('Inspect path, vectors and timestamps','current_axis_readings',active.id,links);link('Open this path in the global atlas',H.atlasUrl(active),links);
      chart.replaceChildren();const h=210;chart.setAttribute('viewBox',`0 0 ${width} ${h}`);
      const group=months(),values=group.map(r=>r.length_km),lo=Math.floor(Math.min(...values)/100)*100-100,hi=Math.ceil(Math.max(...values)/100)*100+100;
      const cx=m=>left+(m-1)/11*(right-left),cy=v=>20+(hi-v)/(hi-lo)*150;
      for(const v of [lo,(lo+hi)/2,hi]){svgNode('line',{x1:left,x2:right,y1:cy(v),y2:cy(v),stroke:'#b8ccd4'},chart);svgNode('text',{x:left-5,y:cy(v)+4,'text-anchor':'end','font-size':13},chart,Math.round(v).toLocaleString());}
      for(const m of [1,4,7,10,12])svgNode('text',{x:cx(m),y:195,'text-anchor':'middle','font-size':13},chart,String(m));
      for(const r of group){const c=svgNode('circle',{cx:cx(r.month),cy:cy(r.length_km),r:r.id===active.id?6:4,fill:r.boundary_contact_native_cells?'#a74862':'#087f8c',tabindex:0,role:'button','aria-label':`${date(r)} · ${km(r.length_km)} · ${r.boundary_contact_native_cells} boundary contacts`},chart);svgNode('title',{},c,`${date(r)} · ${km(r.length_km)}`);const select=()=>{stop();monthSelect.value=r.id;render();};c.addEventListener('click',select);c.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select();}});}
      options.onSelect?.(active);
    }
    fillMonths(initial.id);render();
    windowSelect.addEventListener('change',()=>{stop();const month=active.month;fillMonths(months().find(r=>r.month===month)?.id);render();});
    monthSelect.addEventListener('change',()=>{stop();render();});
    play.addEventListener('click',()=>{if(timer!==null){stop();return;}if(reduced?.matches)return;play.textContent='Pause dated months';timer=setInterval(()=>{if(!panel.isConnected||document.hidden){stop();return;}const group=months(),i=group.findIndex(r=>r.id===monthSelect.value);monthSelect.value=group[(i+1)%group.length].id;render();},1200);});
    play.disabled=Boolean(reduced?.matches);
    node('p','Length chart: month number on the horizontal axis, regional product-path km on the vertical axis. Rose points touch an analysis-window boundary. Playback steps through available dated months without interpolation; this is not a seasonal climatology.',panel);
    if(typeof ResizeObserver==='function'){let previous=0;observer=new ResizeObserver(()=>{const width=panel.getBoundingClientRect().width;if(Math.abs(width-previous)>.5){previous=width;render();}});observer.observe(panel);}
  }else if(collection)node('p','No native path geometry in these matching records. Scenario calculations and section spans are not substituted with nominal map paths.',panel);
  function table(title,headings,rows,cells){
    if(!rows.length)return;const details=node('details',undefined,panel);node('summary',`${title} (${rows.length})`,details);
    const wrap=node('div',undefined,details);wrap.className='product-axis-table-wrap';
    details.addEventListener('toggle',()=>{if(!details.open||wrap.children.length)return;const t=node('table',undefined,wrap);t.setAttribute('role','table');const hr=node('tr',undefined,node('thead',undefined,t));for(const h of headings){const th=node('th',h,hr);th.scope='col';}const body=node('tbody',undefined,t);for(const r of rows){const tr=node('tr',undefined,body);tr.setAttribute('role','row');cells(r).forEach((value,i)=>{const td=node('td',undefined,tr);td.setAttribute('role','cell');td.dataset.label=headings[i];if(typeof value==='function')value(td);else td.textContent=value;});}},{once:false});
  }
  table('Monthly native paths',['Month / window','Regional path','Method parameters','Boundary / archive support','Record'],readings,r=>[`${date(r)} · ${windowLabel(r)}`,km(r.length_km),`u < −${r.threshold_m_s} m/s; penalty ${r.penalty_m_s}; angle ${r.maximum_angle_deg}°`,`${r.boundary_contact_native_cells} contacts; ${r.sample_count} frames`,td=>action('Inspect','current_axis_readings',r.id,td)]);
  const scenarios=collection==='current_axis_scenarios'?records:[];
  table('Matching operator scenarios',['Month / window','Quantity / result','Parameters','Outcome','Record'],scenarios,r=>[`${date(r)} · ${windowLabel(r)}`,`${r.quantity}: ${km(r.length_km)}`,JSON.stringify(Object.fromEntries(Object.entries(r).filter(([k])=>/threshold|penalty|angle|stride|phase|anchor|representation|native_witness/.test(k)))),r.reason||r.status,td=>action('Inspect','current_axis_scenarios',r.id,td)]);
  const spans=scene.section_spans||[];
  table('Fixed-meridian numerical spans',['Month / section','Span','Edges','Tracking / outcome','Record'],spans,r=>[`${date(r)} · ${r.longitude_east}°E`,km(r.width_km),finite(r.south_latitude)&&finite(r.north_latitude)?`${r.south_latitude.toFixed(3)}–${r.north_latitude.toFixed(3)}°N`:'Edges withheld',r.reason||'No qualified full-year physical-width tracking',td=>action('Inspect','current_axis_section_spans',r.id,td)]);
  for(const s of series){const p=node('p',undefined,panel);action(`Inspect ${windowLabel(s)} series`,'current_axis_series',s.id,p);const a=node('a','Query related operator scenarios',p);a.href='query.html?q='+encodeURIComponent(JSON.stringify({collection:'current_axis_scenarios',filters:[{field:'series_id',op:'eq',value:s.id}],limit:100}));}
  const sources=node('details',undefined,panel);node('summary','Product, context paper and measurement method',sources);
  for(const s of scene.sources||[])action(s.title||s.id,'sources',s.id,node('p',undefined,sources));
  node('p','The paper supplies context and window choices; the numerical paths are derived from the OSCAR archive by the OSW method. Whole-current length, physical paired-edge width, annual physical ranges and numerical physical uncertainty remain unresolved.',sources);
  link('Open current card','object.html?id='+encodeURIComponent(scene.entity_id),node('p',undefined,panel));
  return cleanup;
};
