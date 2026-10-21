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
    node('h4','Kuroshio · 2024 regional model dimensions');
    node('p','908 resolved regional lengths and 4,976 fixed-latitude boundary spans at three depths. Every rejected case remains queryable.');
    node('p','First day of each month, not monthly means. These smoothed GLORYS12V1 model boundaries can include unflagged search-window fallbacks. Fixed-latitude spans are oblique to flow; they are not whole-current or perpendicular widths.');
    const controls=node('div');controls.style.cssText='display:flex;flex-wrap:wrap;gap:.6rem;align-items:end;max-width:100%';
    const label=node('label','Snapshot date ',controls),dates=node('select',undefined,label);dates.className='kuroshio-daily-date';dates.setAttribute('aria-label','Kuroshio snapshot date');
    const depthLabel=node('label','Nominal depth ',controls),depth=node('select',undefined,depthLabel);depth.className='kuroshio-daily-depth';depth.setAttribute('aria-label','Kuroshio nominal source depth');
    const dateValues=[...new Set(scene.frames.map(f=>f.date))].sort();for(const date of dateValues){const o=node('option',date,dates);o.value=date;}
    const levels=[...new Map(scene.frames.map(f=>[f.source_level,f.nominal_depth_m]))];for(const [level,value] of levels){const o=node('option',value+' m',depth);o.value=String(level);}
    for(const s of [dates,depth])s.style.cssText='display:block;max-width:100%;min-height:44px';
    const button=text=>{const b=node('button',text,controls);b.type='button';b.style.minHeight='44px';return b;};
    const previous=button('Previous snapshot'),next=button('Next snapshot'),play=button('Play dated snapshots');play.className='kuroshio-daily-play';
    const motionNote=node('p');motionNote.className='kuroshio-daily-motion';
    const status=node('p');status.className='kuroshio-daily-status';status.setAttribute('aria-live','polite');
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
    link('Inspect exact source report','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,pointer:'',limit:100})),node('p'));
    link('Open twelve-map figure at full size','../'+scene.figure_file,node('p'));
    link('Wang et al. (2026), dataset v1 · CC BY 4.0','https://doi.org/'+scene.source.doi,node('p'));
    node('p','Regional axis: fixed 18–30°N gates. Section spans: 18.5, 21.5, 24.5, 27.5 and 29.5°N. Source 30% axis-speed rule with farthest-valid-ocean fallback, 7 km sampling and 110 km smoothing. Fallback occurrence and numerical accuracy are unknown.');
    let timer=null;
    function stop(){if(timer!==null)clearInterval(timer);timer=null;play.textContent='Play dated snapshots';}
    function motion(){play.disabled=reduced.matches;motionNote.textContent=reduced.matches?'Reduced motion: use date, depth and previous/next controls.':'Playback steps through twelve dated snapshots without interpolation.';}
    function render(){
      const frame=scene.frames.find(f=>f.date===dates.value&&f.source_level===Number(depth.value));if(!frame)return;
      paths.replaceChildren();for(const p of frame.paths){const attrs={d:p.d,fill:'none',stroke:{axis:'#fff8de',left:'#ff9be4',right:'#78f1d3'}[p.role],'stroke-width':'.09'};if(p.role!=='axis')attrs['stroke-dasharray']=p.role==='left'?'.25 .11':'.08 .1';svgNode('path',attrs,paths);}
      title.textContent=`Kuroshio regional model curves · ${frame.date} · ${frame.nominal_depth_m} m`;
      status.textContent=`${frame.date} · nominal ${frame.nominal_depth_m} m · ${dateValues.indexOf(frame.date)+1} of 12 dated snapshots. Daily measurement coverage is shown below.`;
      const annual=scene.summaries.find(s=>s.source_level===frame.source_level&&s.month===null);body.replaceChildren();
      const measurements=[{label:'18–30°N regional axis',value:frame.axis.length_km,status:frame.axis.status,stats:annual.axis_length,id:frame.axis_sample_id},...frame.sections.map((s,i)=>({label:`${s.latitude}°N fixed-section span`,value:s.span_km,status:s.status,stats:annual.sections[i],id:s.sample_id}))];
      for(const m of measurements){const row=node('tr',undefined,body);node('th',m.label,row).scope='row';node('td',m.value===null?'Unresolved: '+m.status.replaceAll('_',' '):fmt(m.value),row);node('td',`${m.stats.valid_count} / ${annual.expected_days}`,row);node('td',m.stats.valid_count?fmt(m.stats.minimum_km)+' – '+fmt(m.stats.maximum_km):'Unresolved',row);const cell=node('td',undefined,row);if(inspect){const b=node('button','Inspect',cell);b.type='button';b.style.minHeight='44px';b.onclick=()=>inspect(scene.collection,m.id);}else link('Inspect',queryHref({collection:scene.collection,filters:[{field:'id',op:'eq',value:m.id}],limit:1}),cell);}
      for(const c of table.querySelectorAll('th,td'))c.style.cssText='padding:.45rem;text-align:left;border-bottom:1px solid #587681';
      for(const c of table.querySelectorAll('th:last-child,td:last-child'))c.style.whiteSpace='nowrap';
      previous.disabled=dates.selectedIndex===0;next.disabled=dates.selectedIndex===dateValues.length-1;
      const address=new URL(queryHref({collection:'diagnostics',filters:[{field:'id',op:'eq',value:scene.diagnostic_id}],limit:1}),location.href);address.searchParams.set('dimension-date',dates.value);address.searchParams.set('dimension-depth',depth.value);address.hash='query-chart-section';share.href=address.href;
      depthQuery.href=queryHref(query([{field:'source_level',op:'eq',value:Number(depth.value)}]));
      const mapReturn=container.querySelector('[data-kuroshio-map-return]');if(mapReturn){const address=new URL(mapReturn.href,location.href);address.searchParams.set('dimension-date',dates.value);address.searchParams.set('dimension-depth',depth.value);mapReturn.href=address.href;}
      document.dispatchEvent(new CustomEvent('osw:kuroshio-frame',{detail:{frame,host:section}}));
    }
    const params=new URL(location.href).searchParams;if(dateValues.includes(params.get('dimension-date')))dates.value=params.get('dimension-date');if(levels.some(([z])=>String(z)===params.get('dimension-depth')))depth.value=params.get('dimension-depth');
    for(const s of [dates,depth])s.addEventListener('change',()=>{stop();render();});
    previous.onclick=()=>{stop();dates.selectedIndex=Math.max(0,dates.selectedIndex-1);render();};next.onclick=()=>{stop();dates.selectedIndex=Math.min(dateValues.length-1,dates.selectedIndex+1);render();};
    play.onclick=()=>{if(timer!==null){stop();return;}if(reduced.matches)return;if(dates.selectedIndex===dateValues.length-1){dates.selectedIndex=0;render();}play.textContent='Pause snapshots';timer=setInterval(()=>{if(!section.isConnected||document.hidden||reduced.matches||dates.selectedIndex===dateValues.length-1){stop();return;}dates.selectedIndex++;render();},1200);};
    active.add({section,stop,motion});motion();render();
  };
})();
