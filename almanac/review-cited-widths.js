"use strict";
window.renderReviewCitedWidths = function(parent,scene,inspect) {
  if(!scene || scene.kind!=='published_review_cited_widths' || !scene.records?.length)return;
  const node=(tag,text,into)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;into.append(el);return el;};
  const panel=node('section',undefined,parent);panel.className='review-cited-widths';panel.style.cssText='min-width:0;overflow-wrap:anywhere';
  node('h3',scene.title,panel);node('p',scene.scope,panel);
  node('p','Reported in a review citing earlier observations. This is not a new independent width sample.',panel);
  inspect ||= (collection,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));};
  for(const row of scene.records){
    const card=node('section',undefined,panel);card.setAttribute('data-review-width-id',row.id);card.style.cssText='border-top:1px solid #b8ccd3;padding:.6rem 0;min-width:0';
    node('h4',row.label,card);node('strong',`about ${row.reported_width_km} km`,card);
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 200 16');svg.setAttribute('role','img');svg.setAttribute('aria-label',`Approximately ${row.reported_width_km} kilometres, review-cited regional surface width. Scale zero to 200 kilometres. Width error and annual range unreported.`);svg.style.cssText='display:block;width:100%;max-width:600px;height:40px;margin:.3rem 0';card.append(svg);
    for(const [tag,attrs] of [['line',{x1:0,y1:8,x2:200,y2:8,stroke:'#d8e2e7','stroke-width':2}],['circle',{cx:row.reported_width_km,cy:8,r:3,fill:'#176f79'}]]){
      const mark=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,value] of Object.entries(attrs))mark.setAttribute(key,value);svg.append(mark);
    }
    node('p','Width scale: 0–200 km. Numerical width uncertainty and annual range are unreported.',card);
    node('p',row.time_convention,card);node('p',row.layer,card);
    const details=node('details',undefined,card);node('summary','Review evidence and limitations',details);
    node('p',row.boundary_rule,details);node('p','The review cites Shetye et al. (1990). The cited original methods have not been reviewed.',details);
    node('p',row.review_width_context.observational_independence_note,details);
    const actions=node('p',undefined,card);actions.style.cssText='display:flex;flex-wrap:wrap;gap:.6rem';
    const button=node('button','Inspect',actions);button.type='button';button.onclick=()=>inspect('widths',row.id);
    const source=node('a','Source record',actions);source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:row.source_file,pointer:row.source_pointer,limit:100}));
    const original=node('a','Original review',actions);original.href=row.source_url;
  }
  const figure=node('a','Review-cited width plot',node('p',undefined,panel));figure.href='../'+scene.full_context_figure;
  return panel;
};
