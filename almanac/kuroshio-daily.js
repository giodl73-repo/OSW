"use strict";
(() => {
  const active=new Set(), reduced=matchMedia('(prefers-reduced-motion: reduce)');let sequence=0;
  const prune=()=>{for(const item of active)if(!item.section.isConnected){item.stop();active.delete(item);}};
  reduced.addEventListener('change',()=>{prune();for(const item of active){item.stop();item.motion();}});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)for(const item of active)item.stop();});
  new MutationObserver(prune).observe(document.documentElement,{childList:true,subtree:true});
  window.renderKuroshioDaily=function(container,scene,inspect){
    if(scene?.kind!=='kuroshio_daily_dimensions')return;
    prune();
    const section=document.createElement('section');section.className='kuroshio-daily';section.style.cssText='min-width:0;max-width:100%;box-sizing:border-box;border:1px solid #587681;padding:.8rem;margin:1rem 0;overflow-wrap:anywhere';container.append(section);
    const node=(tag,text,parent=section)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
    const link=(text,href,parent=section)=>{const a=node('a',text,parent);a.href=href;a.style.cssText='display:inline-flex;align-items:center;min-height:44px;max-width:100%';return a;};
    const svgNode=(tag,attrs,parent)=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));parent.append(n);return n;};
    const query=filters=>({collection:scene.collection,filters,sort:{field:'sample_date',direction:'asc'},limit:100});
    const queryHref=q=>'query.html?q='+encodeURIComponent(JSON.stringify(q));
    const fmt=value=>value===null?'Unresolved':'≈ '+(Math.round(value/10)*10).toLocaleString('en')+' km';
    const heading=node('h4','Kuroshio · 2024 regional model dimensions');
    const coverage=node('p','908 resolved regional lengths and 4,976 fixed-latitude boundary spans at three depths. Every rejected case remains queryable.');
    node('p','First day of each month, not monthly means. These smoothed GLORYS12V1 model boundaries can include unflagged search-window fallbacks. Fixed-latitude spans are oblique to flow; they are not whole-current or perpendicular widths.');
    const controls=node('div');controls.style.cssText='display:flex;flex-wrap:wrap;gap:.6rem;align-items:end;max-width:100%';
    const label=node('label','Snapshot date ',controls),dates=node('select',undefined,label);dates.className='kuroshio-daily-date';dates.setAttribute('aria-label','Kuroshio snapshot date');
    const depthLabel=node('label','Nominal depth ',controls),depth=node('select',undefined,depthLabel);depth.className='kuroshio-daily-depth';depth.setAttribute('aria-label','Kuroshio nominal source depth');
    const metricLabel=node('label','Measurement ',controls),metric=node('select',undefined,metricLabel);metric.className='kuroshio-daily-metric';metric.setAttribute('aria-label','Kuroshio model measurement');
    for(const [value,text] of [['regional','Regional axis / fixed-latitude spans'],...(scene.normal?[['axis_normal','Axis-normal model spans']]:[])]){const o=node('option',text,metric);o.value=value;}
    metric.value=scene.default_metric||'regional';
    const tangentLabel=node('label','Tangent half-window ',controls),tangent=node('select',undefined,tangentLabel);tangent.className='kuroshio-daily-tangent';tangent.setAttribute('aria-label','Kuroshio tangent half-window');
    for(const value of scene.normal?.tangent_half_windows_km||[14]){const o=node('option',value+' km',tangent);o.value=String(value);}tangent.value='14';
    const dateValues=[...new Set(scene.frames.map(f=>f.date))].sort();for(const date of dateValues){const o=node('option',date,dates);o.value=date;}
    const levels=[...new Map(scene.frames.map(f=>[f.source_level,f.nominal_depth_m]))];for(const [level,value] of levels){const o=node('option',value+' m',depth);o.value=String(level);}
    for(const s of [dates,depth,metric,tangent])s.style.cssText='display:block;max-width:100%;min-height:44px';
    const button=text=>{const b=node('button',text,controls);b.type='button';b.style.minHeight='44px';return b;};
    const previous=button('Previous snapshot'),next=button('Next snapshot'),play=button('Play dated snapshots');play.className='kuroshio-daily-play';
    const motionNote=node('p');motionNote.className='kuroshio-daily-motion';
    const status=node('p');status.className='kuroshio-daily-status';status.setAttribute('aria-live','polite');
    const normalNote=node('p');normalNote.className='kuroshio-normal-scope';
    node('p','East China Sea and Luzon Strait · solid cream: model axis · dashed pink: left boundary · dotted mint: right boundary. Gaps remain gaps.');
    const visuals=node('div');visuals.style.cssText='display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,430px),1fr));gap:1rem;align-items:start;min-width:0;max-width:100%';
    const map=svgNode('svg',{viewBox:scene.view_box.join(' '),role:'img',style:'display:block;width:100%;max-width:510px;height:auto;background:#e4f1f5'},visuals);
    const title=svgNode('title',{id:'kuroshio-daily-map-'+(++sequence)},map);map.setAttribute('aria-labelledby',title.id);
    const desc=svgNode('desc',{},map);desc.textContent='Dated publisher-identified model axis and two smoothed lateral boundaries, projected by Rust. The table provides dimensions and rejected cases. Equirectangular display with existing OSW geographic context; no occupied polygon or physical state passage.';
    svgNode('image',{href:'../figures/ocean-motion-closeup-ground.svg',x:0,y:0,width:360,height:180,preserveAspectRatio:'none',opacity:.75},map);
    for(const lat of [18,24.5,30])svgNode('path',{d:`M298 ${90-lat}H312`,fill:'none',stroke:'#677681','stroke-width':'.025','stroke-dasharray':'.13 .13'},map);
    const paths=svgNode('g',{},map);
    const wrap=node('div',undefined,visuals);wrap.style.cssText='min-width:0;max-width:100%;overflow-x:auto';wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Kuroshio regional dimensions table; scroll horizontally if needed');
    const table=node('table',undefined,wrap);table.style.cssText='border-collapse:collapse;width:100%;min-width:510px;font-size:.9rem';
    node('caption','2024 ranges condition on geometrically resolved model samples. They are not error bars, climatology or physical annual extrema.',table);
    const head=node('tr',undefined,node('thead',undefined,table));for(const text of ['Measurement','Selected day','Resolved in 2024','2024 sample range','Inspect']){const h=node('th',text,head);h.scope='col';}
    const body=node('tbody',undefined,table);
    const share=link('Share this dated model view','#',node('p'));
    const depthQuery=link('Query all daily attempts at this depth','#',node('p'));
    link('Query all 6,588 regional model attempts',queryHref(query([])),node('p'));
    if(scene.normal){link('Query all 16,470 axis-normal attempts',queryHref({collection:scene.normal.collection,limit:100}),node('p'));link('Inspect exact axis-normal source report','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.normal.source_file,pointer:'',limit:100})),node('p'));link('Open axis-normal ranges and mapped normals','../'+scene.normal.figure_file,node('p'));}
    link('Inspect exact source report','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,pointer:'',limit:100})),node('p'));
    link('Open twelve-map figure at full size','../'+scene.figure_file,node('p'));
    link('Wang et al. (2026), dataset v1 · CC BY 4.0','https://doi.org/'+scene.source.doi,node('p'));
    node('p','Regional axis: fixed 18–30°N gates. Section spans: 18.5, 21.5, 24.5, 27.5 and 29.5°N. Source 30% axis-speed rule with farthest-valid-ocean fallback, 7 km sampling and 110 km smoothing. Fallback occurrence and numerical accuracy are unknown.');
    let timer=null;
    function stop(){if(timer!==null)clearInterval(timer);timer=null;play.textContent='Play dated snapshots';}
    function motion(){play.disabled=reduced.matches;motionNote.textContent=reduced.matches?'Reduced motion: use date, depth and previous/next controls.':'Playback steps through twelve dated snapshots without interpolation.';}
    function render(){
      const frame=scene.frames.find(f=>f.date===dates.value&&f.source_level===Number(depth.value));if(!frame)return;
      const normal=metric.value==='axis_normal'&&!!scene.normal;tangentLabel.hidden=!normal;tangent.disabled=!normal;
      heading.textContent=normal?'Kuroshio · 2024 axis-normal model spans':'Kuroshio · 2024 regional model dimensions';
      coverage.textContent=normal?'4,680 of 5,490 primary model spans resolve across three depths and five gates in 2024. All 16,470 attempts, including alternate tangent windows and unresolved cases, remain queryable.':'908 resolved regional lengths and 4,976 fixed-latitude boundary spans at three depths. Every rejected case remains queryable.';
      table.style.minWidth=normal?'780px':'510px';wrap.setAttribute('aria-label',normal?'Kuroshio axis-normal dimensions table; scroll horizontally if needed':'Kuroshio regional dimensions table; scroll horizontally if needed');
      normalNote.hidden=!normal;normalNote.textContent='Gold lines: geometric axis-normal spans, not velocity-normal widths or occupied water corridors. Primary convention: 14 km tangent half-window; 7 and 28 km show method sensitivity, not confidence limits. Physical uncertainty, boundary fallback occurrence and speed-threshold attainment are unknown. Sample ranges use available resolved days only.';
      paths.replaceChildren();for(const p of frame.paths){const attrs={d:p.d,fill:'none',stroke:{axis:'#fff8de',left:'#ff9be4',right:'#78f1d3'}[p.role],'stroke-width':'.09'};if(p.role!=='axis')attrs['stroke-dasharray']=p.role==='left'?'.25 .11':'.08 .1';svgNode('path',attrs,paths);}
      const normalSections=normal?frame.normal_sections.filter(s=>s.tangent_half_window_km===Number(tangent.value)):[];
      const normalPaths=normalSections.filter(s=>s.d).map(s=>({role:'axis_normal',d:s.d,latitude:s.latitude}));for(const p of normalPaths)svgNode('path',{d:p.d,fill:'none',stroke:'#ffce5c','stroke-width':'.11','data-model-role':p.role},paths);
      title.textContent=`Kuroshio regional model curves · ${frame.date} · ${frame.nominal_depth_m} m`;
      if(normal)title.textContent+=` · axis-normal spans · ${tangent.value} km tangent half-window`;
      status.textContent=`${frame.date} · nominal ${frame.nominal_depth_m} m · ${dateValues.indexOf(frame.date)+1} of 12 dated snapshots. Daily measurement coverage is shown below.`;
      if(normal)status.textContent+=` Axis-normal model spans · ${tangent.value} km tangent half-window.`;
      const annual=scene.summaries.find(s=>s.source_level===frame.source_level&&s.month===null);body.replaceChildren();
      const measurements=normal?normalSections.map(s=>({label:`${s.latitude}°N axis-normal span`,value:s.span_km,status:s.status,stats:scene.normal.summaries.find(r=>r.source_level===frame.source_level&&r.latitude===s.latitude&&r.tangent_half_window_km===Number(tangent.value)&&r.month===null),id:s.sample_id,latitude:s.latitude,flag:s.exceeds_source_nominal_140km_transect})):[{label:'18–30°N regional axis',value:frame.axis.length_km,status:frame.axis.status,stats:annual.axis_length,id:frame.axis_sample_id},...frame.sections.map((s,i)=>({label:`${s.latitude}°N fixed-section span`,value:s.span_km,status:s.status,stats:annual.sections[i],id:s.sample_id}))];
      head.replaceChildren();for(const text of ['Measurement','Selected day','Resolved in 2024','2024 sample range',...(normal?['Selected month · available days','Same-day tangent sensitivity']:[]),'Inspect']){const h=node('th',text,head);h.scope='col';}
      const sampleCollection=normal?scene.normal.collection:scene.collection;
      for(const m of measurements){const row=node('tr',undefined,body);node('th',m.label,row).scope='row';node('td',(m.value===null?'Unresolved: '+m.status.replaceAll('_',' '):fmt(m.value))+(m.flag?' · exceeds nominal 140 km source transect':''),row);node('td',`${m.stats.valid_count} / ${normal?m.stats.attempted_count:annual.expected_days}`,row);node('td',m.stats.valid_count?fmt(m.stats.minimum_km)+' – '+fmt(m.stats.maximum_km):'Unresolved',row);
        if(normal){const monthly=scene.normal.summaries.find(r=>r.source_level===frame.source_level&&r.latitude===m.latitude&&r.tangent_half_window_km===Number(tangent.value)&&r.month===Number(frame.date.slice(5,7)));node('td',`${monthly.valid_count} / ${monthly.attempted_count} days · `+(monthly.valid_count?fmt(monthly.minimum_km)+' – '+fmt(monthly.maximum_km):'Unresolved'),row);const sensitivity=frame.normal_sensitivity.find(r=>r.latitude===m.latitude);const spread=sensitivity.complete?sensitivity.maximum_km-sensitivity.minimum_km:null;node('td',spread===null?`Unresolved · ${sensitivity.resolved_windows} / 3 windows`:spread<10?'<10 km across 3 windows':fmt(spread)+' across 3 windows',row);}
        const cell=node('td',undefined,row);if(inspect){const b=node('button','Inspect',cell);b.type='button';b.style.minHeight='44px';b.onclick=()=>inspect(sampleCollection,m.id);}else link('Inspect',queryHref({collection:sampleCollection,filters:[{field:'id',op:'eq',value:m.id}],limit:1}),cell);}
      for(const c of table.querySelectorAll('th,td'))c.style.cssText='padding:.45rem;text-align:left;border-bottom:1px solid #587681';
      for(const c of table.querySelectorAll('th:last-child,td:last-child'))c.style.whiteSpace='nowrap';
      previous.disabled=dates.selectedIndex===0;next.disabled=dates.selectedIndex===dateValues.length-1;
      const selectionParams=address=>{for(const [key,value] of [['date',dates.value],['depth',depth.value],['metric',metric.value],['tangent',tangent.value]])address.searchParams.set('dimension-'+key,value);};
      const address=new URL(queryHref({collection:'diagnostics',filters:[{field:'id',op:'eq',value:normal?scene.normal.diagnostic_id:scene.diagnostic_id}],limit:1}),location.href);selectionParams(address);address.hash='query-chart-section';share.href=address.href;
      depthQuery.href=queryHref({collection:sampleCollection,filters:[{field:'source_level',op:'eq',value:Number(depth.value)},...(normal?[{field:'tangent_half_window_km',op:'eq',value:Number(tangent.value)}]:[])],sort:{field:'sample_date',direction:'asc'},limit:100});
      const mapReturn=container.querySelector('[data-kuroshio-map-return]');if(mapReturn){const address=new URL(mapReturn.href,location.href);selectionParams(address);mapReturn.href=address.href;}
      document.dispatchEvent(new CustomEvent('osw:kuroshio-frame',{detail:{frame,host:section,metric:metric.value,tangent:Number(tangent.value),normalPaths}}));
    }
    const params=new URL(location.href).searchParams;if(dateValues.includes(params.get('dimension-date')))dates.value=params.get('dimension-date');if(levels.some(([z])=>String(z)===params.get('dimension-depth')))depth.value=params.get('dimension-depth');
    if(params.get('dimension-metric')==='regional'||(scene.normal&&params.get('dimension-metric')==='axis_normal'))metric.value=params.get('dimension-metric');if((scene.normal?.tangent_half_windows_km||[14]).map(String).includes(params.get('dimension-tangent')))tangent.value=params.get('dimension-tangent');
    for(const s of [dates,depth,metric,tangent])s.addEventListener('change',()=>{stop();render();});
    previous.onclick=()=>{stop();dates.selectedIndex=Math.max(0,dates.selectedIndex-1);render();};next.onclick=()=>{stop();dates.selectedIndex=Math.min(dateValues.length-1,dates.selectedIndex+1);render();};
    play.onclick=()=>{if(timer!==null){stop();return;}if(reduced.matches)return;if(dates.selectedIndex===dateValues.length-1){dates.selectedIndex=0;render();}play.textContent='Pause snapshots';timer=setInterval(()=>{if(!section.isConnected||document.hidden||reduced.matches||dates.selectedIndex===dateValues.length-1){stop();return;}dates.selectedIndex++;render();},1200);};
    active.add({section,stop,motion});motion();render();
  };
})();
