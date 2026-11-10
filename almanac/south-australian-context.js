"use strict";
(()=>{
  let serial=0;
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)'),panels=new Set();
  function clean(){for(const panel of panels)if(!panel.section.isConnected){panel.stop();panels.delete(panel);}}
  document.addEventListener('visibilitychange',()=>{if(document.hidden)for(const panel of panels)panel.stop();clean();});
  reducedMotion.addEventListener('change',()=>{clean();for(const panel of panels){panel.button.disabled=reducedMotion.matches;if(reducedMotion.matches)panel.stop();}});
  window.renderSouthAustralianContext=function(container,scene,inspect,options={}){
    if(!scene||scene.kind!=='south_australian_flow_context')return;
    clean();
    const section=document.createElement('section');section.className='south-australian-context';section.style.cssText='min-width:0;max-width:100%;border:1px solid #587681;padding:.8rem;margin:1rem 0;box-sizing:border-box';container.append(section);
    const style=document.createElement('style');style.textContent='@media(max-width:500px){.south-australian-context .sac-map-tick{font-size:30px}.south-australian-context .sac-map-axis{font-size:28px}}';section.append(style);
    const node=(tag,text,parent=section)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
    const svgNode=(tag,attrs,parent,text)=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
    const link=(text,href,parent=section)=>{const a=node('a',text,parent);a.href=href;a.style.cssText='display:inline-flex;min-height:44px;align-items:center;max-width:100%;overflow-wrap:anywhere';return a;};
    const sourceUrl=pointer=>'query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.raw_context_file,pointer,limit:100}));
    const fmt=v=>Number(v).toLocaleString('en',{maximumFractionDigits:3});
    node('h4','South Australian investigation · surrounding flow');
    node('p','2012 HYCOM+NCODA model vectors at 100 m. The original monthly section spans remain unchanged; named-current identity and physical widths remain unresolved.');
    const details=node('details');details.open=Boolean(options.open);node('summary','Explore all 12 monthly flow contexts',details).style.cssText='min-height:44px;padding:.35rem 0';
    node('p','Colors mark connected native grid cells above a fraction of the original eastward peak. Missing cells stop connections. Box contact does not establish current continuity; monthly means do not establish instantaneous paths or annual extremes.',details);
    const controls=node('div',undefined,details);controls.style.cssText='display:flex;flex-wrap:wrap;gap:.7rem;align-items:center';
    const select=(label,name,choices)=>{const l=node('label',label+' ',controls),s=node('select',undefined,l);s.setAttribute('aria-label',label);s.dataset[name]='';s.style.cssText='min-height:44px;max-width:100%';for(const [value,text] of choices){const o=node('option',text,s);o.value=value;}return s;};
    const months=select('Recorded month','sacMonth',scene.months.map(m=>[m.month,new Date(Date.UTC(2012,m.month-1,1)).toLocaleDateString('en',{month:'long',year:'numeric',timeZone:'UTC'})]));
    const fraction=select('Peak threshold','sacThreshold',scene.fractions.map(f=>[f,Math.round(f*100)+'%']));
    const play=node('button','Play recorded 2012 months',controls);play.type='button';play.dataset.sacPlay='';play.style.cssText='min-height:44px;max-width:100%';play.disabled=reducedMotion.matches;play.setAttribute('aria-pressed','false');
    node('p','Playback steps through recorded monthly model means without interpolation. Automatic playback is disabled when reduced motion is requested.',details);
    let timer=null;
    function stop(){if(timer!==null)clearInterval(timer);timer=null;play.textContent='Play recorded 2012 months';play.setAttribute('aria-pressed','false');}
    panels.add({section,button:play,stop});
    details.addEventListener('toggle',()=>{if(!details.open)stop();});
    play.addEventListener('click',()=>{if(timer!==null){stop();return;}if(reducedMotion.matches)return;play.textContent='Stop playback';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{if(!section.isConnected||document.hidden){stop();return;}months.value=String(Number(months.value)%12+1);draw();},1300);});
    const params=new URLSearchParams(location.search);months.value=scene.months.some(m=>String(m.month)===params.get('sac-month'))?params.get('sac-month'):'1';fraction.value=scene.fractions.some(f=>String(f)===params.get('sac-threshold'))?params.get('sac-threshold'):'0.5';
    const reading=node('p','',details);reading.dataset.sacReading='';reading.setAttribute('role','status');reading.setAttribute('aria-live','polite');
    const figure=node('figure',undefined,details);figure.style.cssText='margin:.5rem 0;max-width:100%';
    const svg=svgNode('svg',{viewBox:'0 0 500 880',role:'img'},figure);svg.style.cssText='display:block;width:100%;max-width:520px;height:auto;background:#fff';svg.dataset.sacMap='';
    node('figcaption','Orange: selected seed-connected cells. White: supported outside that component. Gray: missing paired model values. Dashed line: original 132°E section; magenta: its unchanged half-peak span; star: original seed. Arrows show mean direction every fourth native cell. Longitude–latitude axes, local aspect at 35°S. No shoreline or physical current boundary inferred.',figure);
    const values=node('dl',undefined,details);values.style.cssText='display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:.4rem;overflow-wrap:anywhere';
    const exact=link('Inspect exact monthly membership and support',sourceUrl('/months/0'),node('p','',details));exact.dataset.sacExact='';
    const share=link('Share selected month',location.href,node('p','',details));share.dataset.sacShare='';
    link('All-month scientific map sheet','../'+scene.context_figure,node('p','',details));
    link('Daily source examples and all-date availability','../'+scene.source_figure,node('p','',details));
    link('Open original monthly section profiles','query.html?q='+encodeURIComponent(JSON.stringify({collection:'diagnostics',filters:[{field:'id',op:'eq',value:'diagnostic:basin-south-australian-132e-100m'}],limit:1})),node('p','',details));
    link('Inspect source scene and method pins','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,pointer:'',limit:100})),node('p','',details));
    const token='sac-map-'+(++serial),x=lon=>45+(lon-130)*100,y=lat=>40+(-32-lat)*100/Math.cos(35*Math.PI/180);
    function draw(){
      const month=scene.months.find(m=>String(m.month)===months.value),selected=month.threshold_cases.find(c=>String(c.fraction)===fraction.value);
      const seed=month.seed,angle=seed.angle_degrees_north_of_east;
      reading.textContent=`2012-${String(month.month).padStart(2,'0')}: ${selected.cell_count} seed-connected cells at ${Math.round(selected.fraction*100)}%. Box sides: ${selected.touched_box_sides.join(', ')||'none'}. Seed direction: ${fmt(angle)}° north of east. Physical width remains unresolved.`;
      svg.replaceChildren();svg.setAttribute('aria-label',reading.textContent+' Model-grid context; not a physical footprint.');
      svgNode('title',{},svg,'South Australian monthly model-grid flow context');svgNode('desc',{},svg,reading.textContent+' Missing source cells are not a coastline. Exact membership is available through the monthly source link.');
      const defs=svgNode('defs',{},svg),clip=svgNode('clipPath',{id:token},defs);svgNode('rect',{x:x(130),y:y(-32),width:400,height:y(-38)-y(-32)},clip);
      const grid=svgNode('g',{'clip-path':`url(#${token})`},svg);svgNode('rect',{x:45,y:40,width:400,height:y(-38)-40,fill:'#c5ccd3'},grid);
      function cell(iy,ix,color){const lo=scene.longitude[ix],la=scene.latitude[iy];const west=ix?(scene.longitude[ix-1]+lo)/2:lo-.04,east=ix+1<scene.longitude.length?(lo+scene.longitude[ix+1])/2:lo+.04;
        const south=iy?(scene.latitude[iy-1]+la)/2:la-.04,north=iy+1<scene.latitude.length?(la+scene.latitude[iy+1])/2:la+.04;
        return svgNode('rect',{x:x(west),y:y(north),width:x(east)-x(west)+.05,height:y(south)-y(north)+.05,fill:color},grid);}
      scene.source_paired_counts_by_cell.forEach((row,iy)=>row.forEach((count,ix)=>{if(count)cell(iy,ix,'#fff');}));
      for(const [iy,ix] of selected.cells)cell(iy,ix,'#e99132').setAttribute('data-sac-component-cell',iy+','+ix);
      svgNode('line',{x1:x(132),x2:x(132),y1:y(-32),y2:y(-38),stroke:'#526372','stroke-dasharray':'5 4'},grid);
      // Fixed source coordinates and uncorrected original section span endpoints.
      const old=month.original_section_boundaries;
      if(old)svgNode('line',{x1:x(132),x2:x(132),y1:y(old[0]),y2:y(old[1]),stroke:'#9d1976','stroke-width':3},grid);
      for(const [iy,ix,u,v] of month.direction_samples){if(u===null||v===null||Math.hypot(u,v)===0)continue;const speed=Math.hypot(u,v),cx=x(scene.longitude[ix]),cy=y(scene.latitude[iy]);
        const dx=7*u/speed/Math.cos(scene.latitude[iy]*Math.PI/180),dy=-7*v/speed/Math.cos(35*Math.PI/180),endX=cx+dx,endY=cy+dy,theta=Math.atan2(dy,dx),a=3;
        svgNode('path',{d:`M${cx-dx},${cy-dy}L${endX},${endY}M${endX-a*Math.cos(theta-.5)},${endY-a*Math.sin(theta-.5)}L${endX},${endY}L${endX-a*Math.cos(theta+.5)},${endY-a*Math.sin(theta+.5)}`,stroke:'#334553','stroke-width':1,fill:'none'},grid);}
      svgNode('text',{x:x(seed.longitude),y:y(seed.latitude)+5,'text-anchor':'middle','font-size':22,fill:'#fff',stroke:'#111','stroke-width':.7},grid,'★');
      svgNode('rect',{x:45,y:40,width:400,height:y(-38)-40,stroke:'#263e4b',fill:'none'},svg);
      for(let lon=130;lon<=134;lon++)svgNode('text',{class:'sac-map-tick',x:x(lon),y:y(-38)+35,'text-anchor':'middle',fill:'#223','font-size':14},svg,String(lon));
      for(let lat=-32;lat>=-38;lat--)svgNode('text',{class:'sac-map-tick',x:35,y:y(lat)+5,'text-anchor':'end',fill:'#223','font-size':14},svg,String(-lat));
      svgNode('text',{class:'sac-map-axis',x:245,y:y(-38)+75,'text-anchor':'middle',fill:'#223','font-size':15},svg,'Longitude °E · latitude °S');
      values.replaceChildren();for(const [label,value] of [['Source days / required paired days',month.source_days+' / '+month.minimum_required_pairs],['Supported native cells',month.supported_cells],['Seed eastward / northward (m/s)',fmt(seed.eastward_m_s)+' / '+fmt(seed.northward_m_s)],['Approximate original section span (km)','about '+Math.round(month.original_section_span_km/10)*10],['Threshold (m/s)',fmt(selected.threshold_m_s)],['Component native longitudes',selected.occupied_native_longitudes]]){node('dt',label,values);const dd=node('dd',String(value),values);dd.style.margin='0';}
      exact.href=sourceUrl('/months/'+(month.month-1));const url=new URL(location.href);url.searchParams.set('sac-month',month.month);url.searchParams.set('sac-threshold',selected.fraction);share.href=url.href;
      section.dataset.sacMonth=month.month;section.dataset.sacThreshold=selected.fraction;
    }
    months.addEventListener('change',()=>{stop();draw();});fraction.addEventListener('change',()=>{stop();draw();});draw();
  };
})();
