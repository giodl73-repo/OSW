"use strict";
window.renderPublishedSectionTransports = function(parent, scene, inspect) {
  if(!scene)return;
  const ns='http://www.w3.org/2000/svg';
  const el=(tag,text,p=parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;p.append(n);return n;};
  const svgEl=(tag,attrs,p,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;p.append(n);return n;};
  const section=el('section');section.className='published-section-transports';
  el('h3',scene.title,section);el('p',scene.scope,section);el('p',scene.spread_note,section);
  const scroll=(label)=>{el('p','Scroll horizontally for '+label+'. A table lists the same source values.',section);const n=el('div',undefined,section);n.style.cssText='overflow-x:auto;max-width:100%;';n.tabIndex=0;n.setAttribute('role','region');n.setAttribute('aria-label',label);return n;};
  const link=(text,href,p)=>{const a=el('a',text,p);a.href=href;a.style.cssText='display:inline-flex;align-items:center;min-height:44px;';return a;};
  const source=(r,p)=>link('Inspect source row','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,pointer:r.source_pointer,limit:50})),p);
  const table=(headers)=>{const frame=scroll('source table'),t=el('table',undefined,frame);t.style.cssText='min-width:900px;width:100%;border-collapse:collapse;';const head=el('tr',undefined,el('thead',undefined,t));for(const h of headers){const th=el('th',h,head);th.scope='col';}return el('tbody',undefined,t);};
  const cell=(text,tr)=>{const n=el('td',text,tr);n.style.cssText='padding:.5rem;border-bottom:1px solid #829ba6;';return n;};
  const open=(r,c,tr)=>{const td=cell('',tr);if(inspect){const b=el('button','Inspect record',td);b.type='button';b.style.minHeight='44px';b.onclick=()=>inspect(c,r.id);}source(r,td);};
  if(scene.model_records.length){
    const frame=scroll('mean transport chart'),svg=svgEl('svg',{viewBox:scene.view_box.join(' '),role:'img','aria-label':'Model mean transport magnitudes in Sv; directions and unresolved plus/minus notation are separate'},frame);
    svg.style.cssText='display:block;width:1000px;max-width:none;background:#f6f5ef;color:#102f3b;';
    const text=(x,y,s)=>{const n=svgEl('text',{x,y,fill:'#102f3b'},svg,s);n.style.font='16px Arial,sans-serif';};
    for(const p of scene.points){const r=p.record;text(8,p.y+5,r.section_id+' · '+r.layer_label+(r.transport_variant==='footnote_a'?' (a)':''));svgEl('line',{x1:p.x_start,x2:p.x_end,y1:p.y,y2:p.y,stroke:'#176b82','stroke-width':12},svg);text(770,p.y+5,r.value_sv+' ± '+r.source_reported_plus_minus_sv+' Sv '+r.direction);}
    for(const tick of scene.ticks)text(260+tick/scene.axis_max_sv*500,scene.view_box[3]-20,tick+' Sv');
    const rows=table(['Section / current','Mean ± source notation (Sv)','Direction','Integration scope','Identity','Source']);
    for(const r of scene.model_records){const tr=el('tr',undefined,rows);tr.dataset.transportId=r.id;cell(r.section_id+' · '+r.source_current_label+' · '+Math.abs(r.coordinate_degrees)+'° '+(r.coordinate_axis==='latitude'?(r.coordinate_degrees<0?'S':'N'):'E'),tr);cell(r.value_sv+' ± '+r.source_reported_plus_minus_sv,tr);cell(r.direction,tr);cell(({core:'Core',footnote_a:'Includes recirculation (source footnote a)',total_westward:'Total westward'}[r.transport_variant]||r.transport_variant)+' · '+r.layer_label+(r.fixed_layer_bounds_m?' · '+r.fixed_layer_bounds_m.join('–')+' m':''),tr);const owner=cell(r.current_id?'':'No canonical current assigned',tr);if(r.current_id)link('Open current card','seasons.html?current='+encodeURIComponent(r.current_id),owner);open(r,'section_transports',tr);}
  }
  if(scene.validation_records.length){
    el('h4','Observation / model comparisons',section);el('p','Each pair uses its published comparison period. The exact matched monthly mask is unavailable; these are not whole-run model means. SD is reported variability.',section);
    const rows=table(['Section / place','Period / source months','Observation mean / SD (Sv)','Model mean / SD (Sv)','RMSE (Sv)','Source']);
    for(const r of scene.validation_records){const tr=el('tr',undefined,rows);tr.dataset.validationId=r.id;cell(r.section_id+' · '+r.place_label,tr);cell(r.period.start+'–'+r.period.end+' · '+r.source_month_count+' months',tr);cell(r.observation.mean_sv+' '+r.observation.direction+' / '+r.observation.standard_deviation_sv,tr);cell(r.simulation.mean_sv+' '+r.simulation.direction+' / '+r.simulation.standard_deviation_sv,tr);cell(r.reported_rmse_sv,tr);open(r,'transport_validations',tr);if(r.source_direction_discrepancy||r.period_count_discrepancy){const warning=el('tr',undefined,rows);const td=cell(r.source_direction_discrepancy?'Source direction discrepancy retained: M1 reports W for the observation and S for the model.':'Source period discrepancy retained: M6 reports 18 months within a 17-calendar-month span.',warning);td.colSpan=6;}}
  }
  const geo=scene.geographic_view;
  if(geo.guides.length){
    el('h4','Source coordinate context',section);el('p',geo.caption,section);
    const frame=scroll('Australia coordinate context'),svg=svgEl('svg',{viewBox:geo.view_box.join(' '),role:'img','aria-label':geo.caption},frame);svg.style.cssText='display:block;width:800px;max-width:none;background:#102f3b;';
    svgEl('image',{href:'../figures/ocean-motion-dashboard-ground.svg',x:60,y:90,width:1480,height:740},svg);
    const [x,y,w,h]=geo.view_box;
    for(const g of geo.guides){const latitude=g.axis==='latitude',d=g.display_coordinate,label=g.section_id+' · '+g.coordinate_degrees+'° '+g.axis;const mark=svgEl('g',{tabindex:0,role:'img','aria-label':label},svg);svgEl('title',{},mark,label);svgEl('line',{x1:latitude?x:d,x2:latitude?x+w:d,y1:latitude?d:y,y2:latitude?d:y+h,stroke:'#ffd46c','stroke-width':.8,'stroke-dasharray':'2 2'},mark);const t=svgEl('text',{x:latitude?x+3:d+2,y:latitude?d-2:y+10,fill:'#fff',stroke:'#102f3b','stroke-width':1,'paint-order':'stroke',visibility:'hidden'},mark,label);t.style.font='6px Arial,sans-serif';const show=()=>t.setAttribute('visibility','visible'),hide=()=>{if(document.activeElement!==mark)t.setAttribute('visibility','hidden');};mark.addEventListener('mouseenter',show);mark.addEventListener('mouseleave',hide);mark.addEventListener('focus',show);mark.addEventListener('blur',()=>t.setAttribute('visibility','hidden'));}
  }
  for(const r of scene.seasonal_context)el('p',({'hiri-current':'Hiri Current','south-australian':'South Australian Current',zeehan:'Zeehan Current'}[r.current_id]||r.current_id)+': approximately '+r.approximate_seasonal_range_sv+' Sv seasonal range; '+r.source_peak_label+'. Source prose context; monthly values have not been extracted. This does not define width variation.',section);
  const notes=el('details',undefined,section);el('summary','Model method and scope notes',notes);const method=scene.model_description;el('p',method.model+' uses a '+method.horizontal_grid_km.join('–')+' km grid and '+method.vertical_levels+' vertical levels. The hindcast covers 2000–2014, without formal data assimilation.',notes);el('p',method.relaxation_note,notes);el('p',method.transect_method,notes);el('p',method.validation_interpolation,notes);el('p','The original model fields and observed monthly time series have not been reprocessed for this atlas.',notes);for(const note of scene.notes)el('p',note,notes);
  link('Original publication',scene.source_url,section);
};
