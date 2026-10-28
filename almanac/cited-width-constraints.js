"use strict";
window.renderCitedWidthConstraints = function(parent,scene,inspect) {
  if(!scene || scene.kind!=='published_cited_width_constraints' || !scene.records?.length)return;
  const node=(tag,text,into)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;into.append(el);return el;};
  const panel=node('section',undefined,parent);panel.className='cited-width-constraints';panel.style.cssText='min-width:0;overflow-wrap:anywhere';
  node('h3',scene.title,panel);node('p',scene.scope,panel);
  node('p','Historical cited constraint; not another independent width observation.',panel);
  inspect ||= (collection,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));};
  for(const row of scene.records){
    if(row.reported_operator!=='gt' || row.lower_bound_exclusive!==true || !Number.isFinite(row.reported_bound_km) || row.upper_bound_km!==null || row.reported_width_km!==null)throw new Error('Unsupported cited width constraint');
    const card=node('section',undefined,panel);card.setAttribute('data-cited-width-id',row.id);card.style.cssText='border-top:1px solid #b8ccd3;padding:.6rem 0;min-width:0';
    node('h4',row.width_metric_label,card);node('strong',`>${row.reported_bound_km} km`,card);
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 240 16');svg.setAttribute('role','img');
    svg.setAttribute('aria-label',`Cited exclusive width lower bound greater than ${row.reported_bound_km} kilometres. Open marker and right arrow; no central width, upper limit, annual range or uncertainty supplied.`);
    svg.style.cssText='display:block;width:100%;max-width:600px;height:40px;margin:.3rem 0';card.append(svg);
    for(const [tag,attrs] of [['line',{x1:0,y1:8,x2:240,y2:8,stroke:'#d8e2e7','stroke-width':1}],
      ['path',{d:`M${row.reported_bound_km+4} 8 H232 M224 3 L232 8 L224 13`,stroke:'#176f79','stroke-width':2,fill:'none'}],
      ['circle',{cx:row.reported_bound_km,cy:8,r:3,stroke:'#176f79','stroke-width':2,fill:'white'}]]){
      const mark=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,value] of Object.entries(attrs))mark.setAttribute(key,value);svg.append(mark);
    }
    node('p','Open marker excludes the bound. The arrow has no measured endpoint. No central width, upper limit or annual range is supplied.',card);
    const details=node('details',undefined,card);node('summary','Cited source and unresolved support',details);
    node('p',row.time_convention,details);node('p',row.layer,details);node('p',row.boundary_definition,details);
    node('p','The thesis cites Bell (1972). The original methods and edition remain unverified.',details);
    node('p',row.cited_width_constraint_context.lineage_note,details);
    const actions=node('p',undefined,card);actions.style.cssText='display:flex;flex-wrap:wrap;gap:.6rem';
    const button=node('button','Inspect',actions);button.type='button';button.onclick=()=>inspect('widths',row.id);
    const source=node('a','Source record',actions);source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:row.source_file,pointer:row.source_pointer,limit:100}));
    const original=node('a','Original thesis',actions);original.href=row.source_download_url;
  }
  node('a','Cited lower-bound plot',node('p',undefined,panel)).href='../'+scene.full_context_figure;
  return panel;
};
