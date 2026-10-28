"use strict";
window.renderSatelliteCoreWidths = function(parent, scene, inspect) {
  if(!scene || scene.kind!=='published_satellite_core_widths' || !scene.records?.length)return;
  const node=(tag,text,into)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;into.append(el);return el;};
  const panel=node('section',undefined,parent);panel.className='satellite-core-widths';panel.style.cssText='min-width:0;overflow-wrap:anywhere';
  node('h3',scene.title,panel);node('p',scene.scope,panel);
  node('p','These are method-specific means, not seasonal limits, confidence intervals or full-current widths. Numerical width uncertainty is unreported.',panel);
  node('p','Each bar uses the same 0 to 100 km scale.',panel);
  inspect ||= (collection,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));};
  for(const row of scene.records){
    const card=node('section',undefined,panel);card.setAttribute('data-satellite-width-id',row.id);card.style.cssText='border-top:1px solid #b8ccd3;padding:.6rem 0;min-width:0';
    node('h4',row.label,card);node('strong',`${row.reported_mean_width_km} km mean`,card);
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 100 8');svg.setAttribute('role','img');svg.setAttribute('aria-label',`${row.label}: ${row.reported_mean_width_km} kilometres, author-reported regional mean. Common scale zero to 100 km. No uncertainty or annual range.`);svg.style.cssText='display:block;width:100%;max-width:600px;height:30px;margin:.3rem 0';card.append(svg);
    const line=document.createElementNS('http://www.w3.org/2000/svg','line');for(const [key,value] of Object.entries({x1:0,y1:4,x2:100,y2:4,stroke:'#d8e2e7','stroke-width':2}))line.setAttribute(key,value);svg.append(line);
    const bar=document.createElementNS('http://www.w3.org/2000/svg','rect');for(const [key,value] of Object.entries({x:0,y:1,width:row.reported_mean_width_km,height:6,fill:row.width_metric==='satellite_gaussian_core_mean'?'#246b77':'#527fb4'}))bar.setAttribute(key,value);svg.append(bar);
    node('p',row.time_convention,card);
    const method=node('details',undefined,card);node('summary','Method and support',method);node('p',row.boundary_rule,method);node('p',row.layer,method);
    if(row.operator_ambiguity_id){for(const issue of scene.source_ambiguities||[]){if(issue.id===row.operator_ambiguity_id){node('p',issue.source_issue,method);node('p',issue.handling,method);}}}
    const actions=node('p',undefined,card);actions.style.cssText='display:flex;flex-wrap:wrap;gap:.6rem';
    const button=node('button','Inspect',actions);button.type='button';button.onclick=()=>inspect('widths',row.id);
    const source=node('a','Source record',actions);source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:row.source_file,pointer:row.source_pointer,limit:100}));
  }
  node('p',scene.seasonality_finding.claim+' This is a non-detection in this regional analysis; width is not assumed constant.',panel);
  const context=node('a','Full context comparison (both methods)',node('p',undefined,panel));context.href='../'+scene.full_context_figure;
  return panel;
};
