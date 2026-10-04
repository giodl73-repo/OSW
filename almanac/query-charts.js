"use strict";
window.oswCharts=(()=>{
  const ns='http://www.w3.org/2000/svg',root=()=>document.getElementById('query-chart-panels');
  function svgNode(tag,attrs,parent,text){const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.append(n);return n;}
  function html(tag,text,parent){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;}
  function render(scene,inspect){
    document.getElementById('query-chart-section').hidden=!scene;root().replaceChildren();if(!scene)return;
    document.getElementById('query-chart-scope').textContent=scene.scope;
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
      if(panel.x_field==='observation_date')html('p','Source processing versions: '+[...new Set(context.sample_value_spans.flatMap(s=>s.source_algorithms))].join(', ')+'. Processing changes and physical variation are not isolated by this chart.',article);
      if(panel.x_field==='observation_date')html('p','Closely dated samples can overlap visually. Each original sample remains selectable with Tab or from its table row.',article);
      html('p','Method: '+String(panel.metric).replaceAll('_',' ')+'. Measurement uncertainty remains unresolved.',article);
      if(context.study_period_years)html('p','Study-period years: '+context.study_period_years.join('–')+'. Season-to-month membership remains unresolved.',article);
      if(context.source_period_labels)html('p','Historical period labels differ; the combined averaging window remains unresolved.',article);
    }
  }
  return {render};
})();
