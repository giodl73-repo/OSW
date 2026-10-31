"use strict";
window.renderRegionalModelLengths=function(parent,scene,inspect){
  if(scene?.kind!=='regional_model_core_length_series')return;
  const series=scene.series,collection=scene.selected_collection;
  if(!series)return;
  const selected=Array.isArray(scene.selected_records)?scene.selected_records:[];
  const readings=collection==='current_length_readings'?selected:collection?[]:scene.readings||[];
  const sensitivities=collection==='current_length_sensitivities'?selected:collection?[]:scene.sensitivities||[];
  const summary=!collection||collection==='current_length_series';
  const node=(tag,text,p)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;p.append(n);return n;};
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
  const table=(headings,p)=>{const wrap=node('div',undefined,p);wrap.style.cssText='max-width:100%;overflow-x:auto';const t=node('table',undefined,wrap);t.style.cssText='width:100%;font-size:.9rem;border-collapse:collapse';const head=node('tr',undefined,node('thead',undefined,t));for(const text of headings){const h=node('th',text,head);h.scope='col';h.style.cssText='text-align:left;padding:.4rem';}return node('tbody',undefined,t);};
  const cell=(text,row)=>{const c=node('td',text,row);c.style.cssText='padding:.4rem;border-top:1px solid #c9d8df';return c;};
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
      const x=lon=>55+(lon-60)/50*640,y=lat=>20+(-5-lat)/15*240;
      for(const lon of [60,70,80,90,100,110]){svgNode('line',{x1:x(lon),x2:x(lon),y1:20,y2:260,stroke:'#d0dee3'},map);svgNode('text',{x:x(lon),y:282,'text-anchor':'middle','font-size':12},map,`${lon}°E`);}
      for(const lat of [-5,-10,-15,-20]){svgNode('line',{x1:55,x2:695,y1:y(lat),y2:y(lat),stroke:'#d0dee3'},map);svgNode('text',{x:48,y:y(lat)+4,'text-anchor':'end','font-size':12},map,`${-lat}°S`);}
      for(const lon of series.geographic_gates_degrees_east||[])svgNode('line',{x1:x(lon),x2:x(lon),y1:20,y2:260,stroke:'#7a687c','stroke-dasharray':'4 4'},map);
      const paths=[];
      for(const row of qualified){
        const coords=row.geometry.coordinates;
        const path=svgNode('path',{d:coords.map(([lon,lat],i)=>`${i?'L':'M'}${x(lon).toFixed(2)},${y(lat).toFixed(2)}`).join(' '),fill:'none',stroke:'#087f8c','stroke-width':2,opacity:.45,tabindex:0,role:'button','aria-label':`${row.provider_year}, kernel ${row.kernel_cells}: ${km(row.length_km)}; inspect trace`,'data-model-reading-id':row.id},map);
        svgNode('title',{},path,`${row.provider_year} · kernel ${row.kernel_cells} · ${km(row.length_km)}`);
        const show=()=>{legend.textContent=`${row.provider_year} · kernel ${row.kernel_cells} · ${km(row.length_km)}. Regional model trace.`;for(const other of paths){other.path.setAttribute('opacity',other.id===row.id?'1':'.2');other.path.setAttribute('stroke-width',other.id===row.id?'4':'2');}};
        paths.push({path,id:row.id});path.addEventListener('mouseenter',show);path.addEventListener('focus',show);
        path.addEventListener('click',()=>inspect('current_length_readings',row.id));path.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspect('current_length_readings',row.id);}});
      }
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
