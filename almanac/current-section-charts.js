"use strict";
window.oswCurrentSectionCharts = {render(scene, inspect, root, registerStop) {
  const html = (tag, text, parent) => {const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  const svgNode = (tag, attrs, parent, text) => {const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  const fmt = x => x===null?'unavailable':Number(x).toLocaleString('en',{maximumFractionDigits:3});
  const frames=scene.frames;
  if(!frames.length){html('p','No recorded sections match this query.',root);return;}
  const article=html('article',undefined,root);article.className='current-section-chart';article.style.minWidth='0';
  html('h3',scene.title,article);
  const controls=html('div',undefined,article);controls.className='section-controls';controls.style.cssText='display:flex;flex-wrap:wrap;gap:.5rem;max-width:100%';
  const label=html('label','Recorded month ',controls),select=html('select',undefined,label);
  label.style.cssText='display:grid;gap:.3rem;width:100%;min-width:0';select.style.cssText='width:100%;min-width:0;max-width:100%';
  select.dataset.sectionMonth='';
  for(const frame of frames){const option=html('option',frame.label,select);option.value=frame.id;}
  const previous=html('button','Previous month',controls),next=html('button','Next month',controls),play=html('button','Play months',controls);
  for(const button of [previous,next,play])button.type='button';
  const status=html('p',undefined,article);status.setAttribute('aria-live','polite');status.dataset.sectionStatus='';
  html('p','On small screens, scroll each chart horizontally to see the complete array.',article);
  const charts=html('div',undefined,article);charts.dataset.sectionPanels='';
  const sourceLine=html('p',undefined,article),source=html('a','Inspect original timestamped profiles',sourceLine);
  const open=html('button','Inspect selected monthly section',article);open.type='button';
  open.addEventListener('click',()=>inspect('current_sections',select.value));
  html('p','Shading: plus or minus one sample standard deviation of available records. This is descriptive spread, not measurement error or a confidence interval. Counts use each field’s own availability. Paired-component counts require both velocity components at the same original time and cell.',article);
  html('p','Playback steps through the selected recorded months and stops at the end. It does not interpolate, fill gaps or repeat an annual cycle. Manual controls remain available with reduced motion.',article);
  const credit=html('a',scene.credit,article);credit.href=scene.source_url;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');let timer=null;
  const stop=()=>{clearInterval(timer);timer=null;play.textContent='Play months';play.setAttribute('aria-pressed','false');play.disabled=reduced.matches||frames.length<2;};
  // The query host owns visibility/reduced-motion listeners and stops every renderer.
  registerStop(stop);
  function draw(){
    const frame=frames[select.selectedIndex];charts.replaceChildren();
    previous.disabled=select.selectedIndex===0;next.disabled=select.selectedIndex===frames.length-1;
    status.textContent=`${frame.label} / ${frame.sample_count} source records / ${frame.first_observed_at} to ${frame.last_observed_at}. ${frame.complete_calendar_time_support?'Complete nominal calendar-time schedule; cell coverage varies.':'Partial calendar month; cell coverage varies.'}`;
    source.href='query.html?source-q='+encodeURIComponent(JSON.stringify(frame.source_query));
    for(const field of scene.fields){
      const panel=html('section',undefined,charts);panel.dataset.sectionField=field.key;
      html('h4',`${field.label} (${field.unit})`,panel);
      const scroll=html('div',undefined,panel);scroll.style.cssText='overflow-x:auto;max-width:100%';
      const svg=svgNode('svg',{viewBox:'0 0 680 300',role:'img','aria-label':`${frame.label}: ${field.label}. Missing cells break the line. Shading is sample spread.`},scroll);
      svg.style.cssText='display:block;width:100%;min-width:600px';
      const [lo,hi]=field.y_domain,x=d=>65+d/300000*590,y=v=>235-(v-lo)/(hi-lo)*205;
      for(let i=0;i<=4;i++){const value=lo+(hi-lo)*i/4;svgNode('line',{x1:65,x2:655,y1:y(value),y2:y(value),stroke:'#cfdae0'},svg);svgNode('text',{x:58,y:y(value)+4,'text-anchor':'end','font-size':12},svg,fmt(value));}
      if(lo<0&&hi>0)svgNode('line',{x1:65,x2:655,y1:y(0),y2:y(0),stroke:'#566e7c'},svg);
      for(const km of [0,50,100,150,200,250,300])svgNode('text',{x:x(km*1000),y:255,'text-anchor':'middle','font-size':12},svg,String(km));
      svgNode('text',{x:355,y:278,'text-anchor':'middle','font-size':13},svg,'Distance along array (km); not geographic current edges');
      const stats=frame.field_statistics[field.key];
      // Each finite run is separate: no line or shaded polygon crosses missing cells.
      let run=[];
      const flush=()=>{if(!run.length)return;let band=[];const shade=()=>{if(band.length>1){const upper=band.map(i=>`${x(frame.distance_m[i])},${y(stats.mean[i]+stats.sample_sd[i])}`),lower=[...band].reverse().map(i=>`${x(frame.distance_m[i])},${y(stats.mean[i]-stats.sample_sd[i])}`);svgNode('polygon',{points:[...upper,...lower].join(' '),fill:'#b4d2df','fill-opacity':.65},svg);}band=[];};for(const i of run){if(stats.sample_sd[i]===null)shade();else band.push(i);}shade();svgNode('polyline',{points:run.map(i=>`${x(frame.distance_m[i])},${y(stats.mean[i])}`).join(' '),fill:'none',stroke:'#155a73','stroke-width':2},svg);if(run.length===1)svgNode('circle',{cx:x(frame.distance_m[run[0]]),cy:y(stats.mean[run[0]]),r:2,fill:'#155a73'},svg);run=[];};
      for(let i=0;i<stats.mean.length;i++){if(stats.mean[i]===null)flush();else run.push(i);}flush();
      const counts=stats.valid_count,paired=frame.paired_vector_statistics.v.valid_count;
      html('p',`${counts.filter(n=>n>0).length} of ${counts.length} cells have data. Available records per cell: ${Math.min(...counts)}–${Math.max(...counts)} of ${frame.sample_count}.`,panel);
      const details=html('details',undefined,panel);html('summary','Exact cell values and support',details);
      const cellLabel=html('label','Distance cell ',details),cell=html('select',undefined,cellLabel);
      for(const [i,d] of frame.distance_m.entries()){const option=html('option',`${fmt(d/1000)} km`,cell);option.value=String(i);}
      const reading=html('p',undefined,details);reading.setAttribute('aria-live','polite');
      const show=()=>{const i=Number(cell.value);reading.textContent=`${fmt(frame.distance_m[i]/1000)} km: mean ${fmt(stats.mean[i])} ${field.unit}; sample SD ${fmt(stats.sample_sd[i])}; n=${counts[i]} of ${frame.sample_count}${field.unit==='m/s'?`; paired-component n=${paired[i]}`:''}.`;};
      cell.addEventListener('change',show);show();
    }
  }
  select.addEventListener('change',()=>{stop();draw();});
  previous.addEventListener('click',()=>{stop();select.selectedIndex--;draw();});
  next.addEventListener('click',()=>{stop();select.selectedIndex++;draw();});
  play.addEventListener('click',()=>{if(timer!==null){stop();return;}if(reduced.matches)return;if(select.selectedIndex===frames.length-1)select.selectedIndex=0;draw();play.textContent='Pause months';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{if(select.selectedIndex===frames.length-1){stop();return;}select.selectedIndex++;draw();},1200);});
  stop();draw();
}};
