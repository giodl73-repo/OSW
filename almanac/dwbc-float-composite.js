"use strict";
window.renderDwbcFloatComposite=function(parent,scene,inspect=null){
  if(scene?.kind!=='dwbc_float_composite')return;
  const ns='http://www.w3.org/2000/svg';
  const node=(tag,text,owner=parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;owner.append(n);return n;};
  const link=(text,href,owner)=>{const n=node('a',text,owner);n.href=href;n.style.cssText='display:inline-flex;align-items:center;min-height:44px';return n;};
  const svgNode=(tag,attrs,owner,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;if(tag==='text')n.style.fontSize='16px';owner.append(n);return n;};
  const panel=node('section',undefined);panel.className='dwbc-float-composite';panel.style.cssText='min-width:0;max-width:100%';
  const scroll=owner=>{node('p','Scroll horizontally to see all chart values and table columns.',owner);const n=node('div',undefined,owner);n.className='dwbc-composite-scroll';n.style.cssText='max-width:100%;overflow-x:auto';n.tabIndex=0;n.setAttribute('aria-label','Scrollable study chart or table');n.addEventListener('focus',()=>{n.style.outline='3px solid #ad7406';});n.addEventListener('blur',()=>{n.style.outline='';});return n;};
  const chart=(box,label)=>{const frame=scroll(panel),svg=svgNode('svg',{viewBox:box.join(' '),role:'img','aria-label':label},frame);svg.style.cssText='display:block;width:760px;max-width:none;background:#f6f5ef;color:#102f3b';return svg;};
  node('h4',scene.title,panel);node('p',scene.scope,panel);node('p',scene.depth_note,panel);
  const geography=scene.geographic_view,view=geography.view_box,map=chart(view,geography.caption);map.classList.add('dwbc-study-geography');
  map.style.width='720px';
  svgNode('image',{href:'../figures/ocean-motion-dashboard-ground.svg',x:60,y:90,width:1480,height:740},map);
  for(const tick of geography.latitudes){
    svgNode('line',{x1:view[0],x2:view[0]+view[2],y1:tick.y,y2:tick.y,stroke:'#7297a0','stroke-width':.2},map);
    const label=svgNode('text',{x:view[0]+1.5,y:Math.max(view[1]+5,Math.min(view[1]+view[3]-6,tick.y-1)),fill:'#ffffff'},map,Math.abs(tick.latitude)+'°'+(tick.latitude<0?'S':tick.latitude>0?'N':''));label.style.cssText='font-size:4.3px;paint-order:stroke fill;stroke:#092b39;stroke-width:.8px';
  }
  for(const tick of geography.longitudes){
    svgNode('line',{x1:tick.x,x2:tick.x,y1:view[1],y2:view[1]+view[3],stroke:'#7297a0','stroke-width':.2},map);
    const label=svgNode('text',{x:tick.x,y:view[1]+view[3]-1,'text-anchor':tick.longitude===-55?'start':tick.longitude===-10?'end':'middle',fill:'#ffffff'},map,Math.abs(tick.longitude)+'°W');label.style.cssText='font-size:4.3px;paint-order:stroke fill;stroke:#092b39;stroke-width:.8px';
  }
  node('p',geography.caption+' Projection: '+geography.projection+'. Coarse coastlines provide context only.',panel);
  node('h5','Composite width ~100 km · numerical uncertainty unknown',panel);
  const width=chart(scene.width_view_box,'Approximate 100 km width between zero-velocity points. No numerical width error supplied.');
  svgNode('line',{x1:60,x2:700,y1:65,y2:65,stroke:'#526c77'},width);
  for(const tick of scene.width_ticks)svgNode('text',{x:60+640*tick/150,y:95,'text-anchor':'middle',fill:'#102f3b'},width,tick+' km');
  svgNode('circle',{cx:scene.width_point.x,cy:scene.width_point.y,r:7,fill:'#176b82','data-width-km':scene.width_point.value_km},width);
  svgNode('text',{x:scene.width_point.x,y:25,'text-anchor':'middle',fill:'#102f3b'},width,'~'+scene.width_point.value_km+' km');
  node('p',scene.width_caption,panel);
  node('h5','Published historical subset diagnostics',panel);node('p','These are published source estimates, not an ingested daily velocity series. Subsets are unequal and overlap the composite.',panel);node('p',scene.uncertainty_note,panel);
  for(const p of scene.panels){
    const unit=p.unit.replace('10^3 m2/s','10³ m²/s');node('h5',p.title+' ('+unit+')',panel);
    const svg=chart(p.view_box,p.title+'. Reported standard-error whiskers. Four source rows including the overlapping composite.');
    for(const tick of p.ticks){const x=270+420*tick/p.axis_max;svgNode('line',{x1:x,x2:x,y1:30,y2:238,stroke:'#d4dde0'},svg);svgNode('text',{x,y:265,'text-anchor':'middle',fill:'#102f3b'},svg,String(tick));}
    for(const point of p.points){
      const g=svgNode('g',{'data-source-row':point.source_row},svg);svgNode('text',{x:10,y:point.y+6,fill:'#102f3b'},g,point.label);
      svgNode('line',{x1:point.x_low,x2:point.x_high,y1:point.y,y2:point.y,stroke:'#176b82','stroke-width':3},g);
      for(const x of [point.x_low,point.x_high])svgNode('line',{x1:x,x2:x,y1:point.y-7,y2:point.y+7,stroke:'#176b82','stroke-width':2},g);
      svgNode('circle',{cx:point.x,cy:point.y,r:5,fill:'#176b82'},g);
      svgNode('text',{x:point.x_high+8,y:point.y-10,fill:'#102f3b'},g,point.value+' ±'+point.standard_error);
    }
  }
  const table=node('table',undefined,scroll(panel));table.style.cssText='min-width:1080px;font-size:14px';node('caption','Table 2 source values · approximate repeated widths are not tracked edges',table);
  const tr=node('tr',undefined,node('thead',undefined,table));for(const t of ['Period','Width km','Floats in current','Observations','Individual peak cm/s','Maximum bin average ±SE cm/s','Transport per depth ±SE (10³ m²/s)','Total transport Sv','Source']){const th=node('th',t,tr);th.scope='col';}
  const body=node('tbody',undefined,table);
  scene.table.forEach((row,i)=>{const r=node('tr',undefined,body);r.dataset.sourceRow=i;const th=node('th',row.period_label,r);th.scope='row';
    for(const value of [row.current_width_km,row.floats_in_current,row.observations_in_current,row.peak_individual_velocity_range_cm_s.join('–'),row.maximum_bin_average_velocity_cm_s+' ±'+row.maximum_bin_average_standard_error_cm_s,row.transport_per_unit_depth_10_3_m2_s+' ±'+row.transport_per_unit_depth_standard_error_10_3_m2_s,row.total_volume_transport_sv===null?'Not supplied':row.total_volume_transport_sv])node('td',String(value),r);
    link('Inspect source row','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.audit_file,pointer:'/measurement/original_regional_context/source_table_rows/'+i,limit:50})),node('td',undefined,r));
  });
  for(const note of scene.sampling_notes)node('p',note,panel);node('p',scene.transport_note,panel);
  const actions=node('p',undefined,panel);
  if(inspect){const button=node('button','Inspect width record',actions);button.type='button';button.addEventListener('click',()=>inspect('widths',scene.record.id));}
  else link('Inspect width record','seasons.html?current=deep-western-boundary&phase='+encodeURIComponent(scene.record.id),actions);
  actions.append(document.createTextNode(' · '));link('Published paper',scene.source_url,actions);node('p',scene.source_citation,panel);
};
