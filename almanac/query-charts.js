"use strict";
window.oswCharts=(()=>{
  const ns='http://www.w3.org/2000/svg',root=()=>document.getElementById('query-chart-panels');
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');let stops=[];
  function stopAll(){for(const stop of stops)stop();}
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopAll();});
  reducedMotion.addEventListener('change',stopAll);
  function svgNode(tag,attrs,parent,text){const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.append(n);return n;}
  function html(tag,text,parent){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;}
  function render(scene,inspect){
    stopAll();stops=[];
    document.getElementById('query-chart-section').hidden=!scene;root().replaceChildren();if(!scene)return;
    document.getElementById('query-chart-scope').textContent=scene.scope;
    document.getElementById('query-chart-legend').hidden=scene.kind==='mooring_velocity';
    document.getElementById('chart-title').textContent=scene.kind==='mooring_velocity'?'Observed current velocity':'Width profiles';
    if(scene.kind==='dwbc_float_composite'||scene.kind==='scoped_width_comparisons'){document.getElementById('query-chart-legend').hidden=true;document.getElementById('chart-title').textContent='Scoped source comparisons';for(const s of scene.scenes||[scene]){if(s.kind==='coastal_composite_widths')window.renderCoastalCompositeWidths(root(),s,null,inspect);else window.renderDwbcFloatComposite(root(),s,inspect);}return;}
    if(scene.kind==='coastal_composite_widths'){document.getElementById('query-chart-legend').hidden=true;document.getElementById('chart-title').textContent='Composite section widths';window.renderCoastalCompositeWidths(root(),scene,null,inspect);return;}
    if(scene.kind==='published_section_transports'){document.getElementById('query-chart-legend').hidden=true;document.getElementById('chart-title').textContent='Published section transport';window.renderPublishedSectionTransports(root(),scene,inspect);return;}
    if(scene.kind==='mooring_velocity'){window.oswMooringVelocityCharts.render(scene,inspect,root(),stop=>stops.push(stop));return;}
    if(!scene.panels.length)html('p','No source samples match this query. Missing coverage does not mean zero width.',root());
    for(const [index,panel] of scene.panels.entries()){
      const article=html('article',undefined,root());article.className='query-chart-panel';article.dataset.panel=panel.id;
      html('h3',panel.title,article);html('p',panel.matching_samples+' matching samples · '+panel.missing_samples+' unresolved. Axes remain fixed to the original diagnostic.',article);
      const frame=html('div',undefined,article);frame.className='query-chart-frame';
      const svg=svgNode('svg',{viewBox:panel.view_box.join(' '),role:'group','aria-labelledby':'width-chart-title-'+index+' width-chart-desc-'+index},frame);
      svgNode('title',{id:'width-chart-title-'+index},svg,panel.title);
      svgNode('desc',{id:'width-chart-desc-'+index},svg,'Scoped source values in kilometres. Solid whiskers are plot-reading allowances; dashed whiskers are finite threshold sensitivity. Neither is a confidence interval. Dated points preserve elapsed-day gaps. Unresolved samples appear in a separate strip, never at zero. Select a point or missing mark for its original record.');
      for(const tick of panel.y_ticks){svgNode('line',{x1:58,x2:616,y1:tick.y,y2:tick.y,class:'chart-grid'},svg);svgNode('text',{x:49,y:tick.y+4,'text-anchor':'end'},svg,tick.value_km.toLocaleString('en',{maximumFractionDigits:1}));}
      svgNode('text',{x:58,y:18},svg,'Scoped width (km)');
      for(const tick of panel.x_ticks){const label=tick.label|| (panel.x_field==='month'?new Intl.DateTimeFormat('en',{month:'short',timeZone:'UTC'}).format(new Date(Date.UTC(2000,tick.value-1,1))):String(tick.value));svgNode('text',{x:tick.x,y:238,'text-anchor':panel.x_field==='observation_date'&&tick.x===58?'start':panel.x_field==='observation_date'&&tick.x===616?'end':'middle'},svg,label);}
      svgNode('text',{x:8,y:259},svg,'Missing');svgNode('text',{x:338,y:277,'text-anchor':'middle'},svg,panel.x_field==='month'?'Source calendar month':panel.x_field==='observation_date'?'Recorded observation day · elapsed Gregorian time':'Section longitude (degrees east)');
      for(const point of panel.points){
        const p=point.primitive,mark=svgNode('g',{tabindex:0,role:'button','data-sample':point.sample_id,class:'chart-sample'},svg);
        const label=point.label+' · '+(point.value_km===null?'unresolved':point.value_km.toLocaleString('en',{maximumFractionDigits:1})+' km')+(point.plot_reading_interval_km?' · plot-reading allowance '+point.plot_reading_interval_km.join('–')+' km':point.diagnostic_sensitivity_interval_km?' · finite threshold sensitivity '+point.diagnostic_sensitivity_interval_km.join('–')+' km; measurement uncertainty unresolved':' · measurement uncertainty unresolved')+(point.source_algorithm?' · '+point.source_algorithm:'');
        mark.setAttribute('aria-label',label);svgNode('title',{},mark,label);
        if(p.kind==='missing')svgNode('path',{d:`M${p.x-4},${p.missing_y-4}L${p.x+4},${p.missing_y+4}M${p.x-4},${p.missing_y+4}L${p.x+4},${p.missing_y-4}`,class:'chart-missing'},mark);
        else{if(p.interval_y){const [lo,hi]=p.interval_y;svgNode('path',{d:`M${p.x},${lo}V${hi}M${p.x-4},${lo}H${p.x+4}M${p.x-4},${hi}H${p.x+4}`,class:'chart-allowance'},mark);}if(p.sensitivity_y){const [lo,hi]=p.sensitivity_y;svgNode('path',{d:`M${p.x},${lo}V${hi}M${p.x-5},${lo}H${p.x+5}M${p.x-5},${hi}H${p.x+5}`,class:'chart-sensitivity'},mark);}svgNode('circle',{cx:p.x,cy:p.y,r:4,class:'chart-reading'},mark);}
        const select=()=>inspect('width_samples',point.sample_id);mark.addEventListener('click',select);mark.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select();}});
      }
      const context=panel.source_context;html('p',context.scope_note||(panel.x_field==='observation_date'?'Individual recorded-day fixed-meridian section spans. Rounded values, not monthly means or streamline widths. Dashed whiskers show finite 40–60% threshold sensitivity; grid brackets remain in the source card.':'One-year local monthly-mean diagnostic. Not climatology or a whole-current dimension.'),article);
      if(context.chart_playback_eligible&&panel.x_field==='month'&&panel.points.length){
        const controls=html('div',undefined,article);controls.className='record-links chart-playback';
        const label=html('label','Source month ',controls),select=html('select',undefined,label);
        for(const point of panel.points){const option=html('option',point.label,select);option.value=point.sample_id;}
        const previous=html('button','Previous month',controls),next=html('button','Next month',controls),play=html('button','Play monthly readings',controls),open=html('button','Inspect selected month',controls);
        for(const button of [previous,next,play,open])button.type='button';
        const reading=html('p',undefined,article);reading.className='chart-selected-reading';reading.setAttribute('aria-live','polite');
        html('p','Chart playback highlights the matching monthly readings only. One step per second; no interpolation or geographic animation. Manual month controls remain available with reduced motion.',article);
        let timer=null;
        const stop=()=>{clearInterval(timer);timer=null;play.textContent='Play monthly readings';play.setAttribute('aria-pressed','false');play.disabled=reducedMotion.matches||panel.points.length<2;};stops.push(stop);
        const show=()=>{const point=panel.points[select.selectedIndex];for(const mark of svg.querySelectorAll('.chart-sample')){const selected=mark.dataset.sample===point.sample_id;mark.setAttribute('aria-pressed',String(selected));const circle=mark.querySelector('circle');if(circle)circle.setAttribute('r',selected?'8':'4');}reading.textContent=point.label+': '+point.value_km+' km · graph-reading allowance '+point.plot_reading_interval_km.join('–')+' km; within-month variation and measurement uncertainty are separate.';previous.disabled=select.selectedIndex===0;next.disabled=select.selectedIndex===panel.points.length-1;};
        select.addEventListener('change',()=>{stop();show();});
        previous.addEventListener('click',()=>{stop();select.selectedIndex--;show();});next.addEventListener('click',()=>{stop();select.selectedIndex++;show();});
        open.addEventListener('click',()=>{stop();inspect('width_samples',select.value);});
        play.addEventListener('click',()=>{if(timer!==null){stop();return;}if(reducedMotion.matches)return;if(select.selectedIndex===panel.points.length-1)select.selectedIndex=0;show();play.textContent='Pause monthly readings';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{if(select.selectedIndex===panel.points.length-1){stop();return;}select.selectedIndex++;show();},1000);});
        stop();show();
      }
      if(panel.x_field==='observation_date')html('p','Source processing versions: '+[...new Set(context.sample_value_spans.flatMap(s=>s.source_algorithms))].join(', ')+'. Processing changes and physical variation are not isolated by this chart.',article);
      if(panel.x_field==='observation_date')html('p','Closely dated samples can overlap visually. Each original sample remains selectable with Tab or from its table row.',article);
      html('p','Method: '+String(panel.metric).replaceAll('_',' ')+'. Measurement uncertainty remains unresolved.',article);
      if(context.study_period_years)html('p','Study-period years: '+context.study_period_years.join('–')+'. Season-to-month membership remains unresolved.',article);
      if(context.source_period_labels)html('p','Historical period labels differ; the combined averaging window remains unresolved.',article);
    }
  }
  function selectSample(id){for(const select of root().querySelectorAll('.chart-playback select')){if([...select.options].some(option=>option.value===id)){select.value=id;select.dispatchEvent(new Event('change'));}}}
  return {render,selectSample};
})();
