"use strict";
window.renderAbstractRegionalWidth=function(container,row){
  if(!row?.source_scope_context)return;
  const figure=document.createElement('figure');figure.className='abstract-regional-width';figure.style.margin='0';container.append(figure);
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');figure.append(svg);
  const span=row.width_range_km,scalar=row.approximate_width_km,maximum=span?1000:150;
  const description=span?`${span[0]} to ${span[1]} km regional width span; no midpoint selected`:`approximately ${scalar} km regional width; numerical uncertainty unknown`;
  svg.setAttribute('viewBox','0 0 500 140');svg.setAttribute('role','img');svg.setAttribute('aria-label',`${row.name}: ${description}. Abstract summary, not annual variation or mapped boundaries.`);
  svg.style.cssText='display:block;width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
  const x=v=>45+410*v/maximum;
  add('line',{x1:45,x2:455,y1:100,y2:100,stroke:'#526c77'});
  if(span){add('line',{x1:x(span[0]),x2:x(span[1]),y1:65,y2:65,stroke:'#176b82','stroke-width':5});for(const v of span){add('line',{x1:x(v),x2:x(v),y1:55,y2:75,stroke:'#176b82','stroke-width':3});add('text',{x:x(v),y:35,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`${v} km`);}}
  else{add('circle',{cx:x(scalar),cy:65,r:7,fill:'#176b82'});add('text',{x:x(scalar),y:35,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`~${scalar} km`);}
  for(const v of [0,maximum])add('text',{x:x(v),y:130,'text-anchor':v===0?'start':'end','font-size':26,fill:'#102f3b'},`${v} km`);
  const caption=document.createElement('figcaption');caption.textContent=`${description}. Publisher abstract only; original boundary methods and figures remain unreviewed. This schematic scale establishes no occupied footprint, seasonal cycle or confidence interval.`;figure.append(caption);
};
