"use strict";
window.renderRegionalModelLengths=(()=>{
  const redraws=new WeakMap();
  const observer=typeof ResizeObserver==='function'?new ResizeObserver(entries=>{
    for(const {target} of entries){
      if(!target.isConnected){observer.unobserve(target);redraws.delete(target);}
      else redraws.get(target)?.();
    }
  }):null;
  return function(parent,scene,inspect){
  if(scene?.kind!=='regional_model_core_length_series')return;
  const series=scene.series,collection=scene.selected_collection;
  if(!series)return;
  const selected=Array.isArray(scene.selected_records)?scene.selected_records:[];
  const readings=collection==='current_length_readings'?selected:collection?[]:scene.readings||[];
  const sensitivities=collection==='current_length_sensitivities'?selected:collection?[]:scene.sensitivities||[];
  const summary=!collection||collection==='current_length_series';
  const node=(tag,text,p)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(tag==='tr'){n.setAttribute('role','row');n._regionalHeadings=p._regionalHeadings;}p.append(n);return n;};
  const svgNode=(tag,attrs,p,text)=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;p.append(n);return n;};
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const km=x=>finite(x)?`about ${(Math.round(x/100)*100).toLocaleString('en-US')} km`:'Withheld';
  inspect||=((name,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection:name,filters:[{field:'id',op:'eq',value:id}],limit:100}));});
  const panel=node('section',undefined,parent);panel.className='regional-model-lengths';panel.style.cssText='min-width:0;overflow-wrap:anywhere';
  node('h3',scene.title,panel);node('p',scene.scope,panel);
  node('p',`${series.layer_scope} · ${series.time_support?.season||'Season unspecified'} · provider model years ${series.time_support?.provider_start_year}–${series.time_support?.provider_end_year}. Calendar encoding is inferred; exact observation dates are unknown.`,panel);
  node('p','Whole-current length, physical width, annual dimension ranges and physical uncertainty: Unknown.',panel);
  if(collection)node('p',`${selected.length} matching ${collection==='current_length_sensitivities'?'sensitivity scenarios':collection==='current_length_readings'?'trace cases':'series records'}. This view uses only these matches.`,panel);
  const action=(label,name,id,p)=>{const b=node('button',label,p);b.type='button';b.addEventListener('click',()=>inspect(name,id));return b;};
  const table=(headings,p)=>{const wrap=node('div',undefined,p);wrap.className='regional-model-table-wrap';wrap.style.cssText='max-width:100%;overflow-x:auto';const t=node('table',undefined,wrap);t.className='regional-model-table';t.setAttribute('role','table');t.setAttribute('data-columns',String(headings.length));t.style.cssText='width:100%;font-size:.9rem;border-collapse:collapse';const head=node('tr',undefined,node('thead',undefined,t));for(const text of headings){const h=node('th',text,head);h.scope='col';h.style.cssText='text-align:left;padding:.4rem';}const body=node('tbody',undefined,t);body.setAttribute('role','rowgroup');body._regionalHeadings=headings;return body;};
  const cell=(text,row)=>{const c=node('td',text,row);c.setAttribute('role','cell');c.setAttribute('data-label',row._regionalHeadings[row.children.length-1]);c.style.cssText='padding:.4rem;border-top:1px solid #c9d8df';return c;};
  if(summary){
    const coverage=node('details',undefined,panel);node('summary','Model-year coverage',coverage);
    node('p',`${series.qualified_grid_length_count} qualified method traces / ${series.reading_count} evaluated cases; ${series.withheld_reading_count} withheld. Nominal kernel: ${series.nominal_kernel_cells} cells.`,coverage);
    const body=table(['Model case','Nominal regional length','Method / resolution span'],coverage);
    for(const row of series.case_summaries||[]){const tr=node('tr',undefined,body);cell(row.case.replace('provider-year-',''),tr);cell(km(row.approximate_nominal_km),tr);const span=row.rounded_method_resolution_span_km;cell(Array.isArray(span)?`${span.map(x=>x.toLocaleString('en-US')).join('–')} km`:'Unknown',tr);}
    node('p','Spans describe smoothing and vertex-sampling choices. They are not physical error bars or annual minima and maxima. Withheld cases stay missing; they are never plotted at zero.',coverage);
    action('Inspect series record','current_length_series',series.id,coverage);
  }
  if(readings.length){
    const qualified=readings.filter(r=>finite(r.length_km)&&r.geometry?.type==='LineString');
    node('h4',`${readings.length} trace cases · ${qualified.length} matching mapped traces`,panel);
    const legend=node('p',undefined,panel);legend.setAttribute('aria-live','polite');
    if(qualified.length){
      const map=svgNode('svg',{viewBox:'0 0 720 300',role:'img','aria-label':'Regional model-grid traces in longitude and latitude. Editorial gates, not whole-current endpoints.'},panel);
      map.style.cssText='display:block;width:100%;height:auto;background:#eef6f9;border-radius:.5rem';
      const longitudeTicks=[60,70,80,90,100,110].map(lon=>({lon,
        line:svgNode('line',{stroke:'#d0dee3'},map),
        label:svgNode('text',{'text-anchor':'middle','font-size':13,'data-model-axis-label':'longitude'},map,`${lon}°E`)}));
      const latitudeTicks=[-5,-10,-15,-20].map(lat=>({lat,
        line:svgNode('line',{stroke:'#d0dee3'},map),
        label:svgNode('text',{'text-anchor':'end','font-size':13,'data-model-axis-label':'latitude'},map,`${-lat}°S`)}));
      const gates=(series.geographic_gates_degrees_east||[]).map(lon=>({lon,
        line:svgNode('line',{stroke:'#7a687c','stroke-dasharray':'4 4'},map)}));
      const paths=[];
      for(const row of qualified){
        const coords=row.geometry.coordinates;
        const path=svgNode('path',{d:'',fill:'none',stroke:'#087f8c','stroke-width':2,'vector-effect':'non-scaling-stroke',opacity:.45,tabindex:0,role:'button','aria-label':`${row.provider_year}, kernel ${row.kernel_cells}: ${km(row.length_km)}; inspect trace`,'data-model-reading-id':row.id},map);
        svgNode('title',{},path,`${row.provider_year} · kernel ${row.kernel_cells} · ${km(row.length_km)}`);
        const show=()=>{legend.textContent=`${row.provider_year} · kernel ${row.kernel_cells} · ${km(row.length_km)}. Regional model trace.`;for(const other of paths){other.path.setAttribute('opacity',other.id===row.id?'1':'.2');other.path.setAttribute('stroke-width',other.id===row.id?'4':'2');}};
        paths.push({path,id:row.id,coordinates:coords});path.addEventListener('mouseenter',show);path.addEventListener('focus',show);
        path.addEventListener('click',()=>inspect('current_length_readings',row.id));path.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspect('current_length_readings',row.id);}});
      }
      let lastWidth=-1;
      const layout=()=>{
        const width=Math.max(180,map.getBoundingClientRect?.()?.width||panel.clientWidth||720);
        if(Math.abs(width-lastWidth)<.5)return;lastWidth=width;
        const height=Math.max(230,width*300/720),left=44,right=width-18,top=20,bottom=height-38;
        map.setAttribute('viewBox',`0 0 ${width} ${height}`);
        const x=lon=>left+(lon-60)/50*(right-left),y=lat=>top+(-5-lat)/15*(bottom-top);
        const attributes=(node,values)=>{for(const [key,value] of Object.entries(values))node.setAttribute(key,String(value));};
        for(const tick of longitudeTicks){
          attributes(tick.line,{x1:x(tick.lon),x2:x(tick.lon),y1:top,y2:bottom});
          attributes(tick.label,{x:x(tick.lon),y:height-14,display:width<360&&[70,90,110].includes(tick.lon)?'none':'inline'});
        }
        for(const tick of latitudeTicks){
          attributes(tick.line,{x1:left,x2:right,y1:y(tick.lat),y2:y(tick.lat)});
          attributes(tick.label,{x:left-8,y:y(tick.lat)+4});
        }
        for(const gate of gates)attributes(gate.line,{x1:x(gate.lon),x2:x(gate.lon),y1:top,y2:bottom});
        for(const item of paths)item.path.setAttribute('d',item.coordinates.map(([lon,lat],i)=>`${i?'L':'M'}${x(lon).toFixed(2)},${y(lat).toFixed(2)}`).join(' '));
      };
      layout();
      if(observer){redraws.set(map,layout);observer.observe(map);}
      legend.textContent='Hover or focus a trace for its model year, kernel and length. Select it to inspect the record.';
      node('p','Longitude–latitude reference grid. Dashed lines are editorial comparison gates. Display interpolation adds no observations; these paths are not diagnosed whole-current axes.',panel);
    }else legend.textContent='No qualified map geometry among the matching cases. Failed paths are withheld.';
    const details=node('details',undefined,panel);node('summary',`Inspect ${readings.length} matching trace cases`,details);
    const body=table(['Model case','Kernel','Regional length','Trace status'],details);
    for(const row of readings){const tr=node('tr',undefined,body);const c=cell(undefined,tr);action(row.provider_year===null?'Mean field':String(row.provider_year),'current_length_readings',row.id,c);cell(String(row.kernel_cells),tr);cell(km(row.length_km),tr);cell(finite(row.length_km)?'Qualified':`Withheld · ${(row.flags||[]).map(f=>f.reason.replaceAll('_',' ').toLowerCase()).join('; ')||'failed trace'}`,tr);}
  }
  if(sensitivities.length){
    const details=node('details',undefined,panel);node('summary',`${sensitivities.length} matching method / resolution scenarios`,details);
    node('p','These computed choices describe grid-path sensitivity. They do not supply seasonal variation, physical bounds or independent observations.',details);
    const body=table(['Model year','Kernel','Stride / phase','Regional length','Record'],details);
    for(const row of sensitivities){const tr=node('tr',undefined,body);cell(String(row.provider_year),tr);cell(String(row.kernel_cells),tr);cell(`${row.stride} / ${row.phase}`,tr);cell(km(row.length_km),tr);action('Inspect','current_length_sensitivities',row.id,cell(undefined,tr));}
  }
  const links=node('p',undefined,panel);
  for(const [label,key]of [['Paper','source_id'],['Model deposit','dataset_source_id'],['Measurement method','method_source_id']])if(series[key])action(label,'sources',series[key],links);
  const a=node('a','Open current card',node('p',undefined,panel));a.href='object.html?id='+encodeURIComponent(scene.entity_id);
};
})();
