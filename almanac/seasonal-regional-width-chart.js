"use strict";
window.renderSeasonalRegionalWidth=function(container,row){
  const figure=document.createElement('figure');figure.className='seasonal-regional-width';figure.style.margin='0';container.append(figure);
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');figure.append(svg);svg.setAttribute('viewBox','0 0 500 135');svg.setAttribute('role','img');svg.setAttribute('aria-label','Somali northern coastal flow: March-May reported width scale 50 to 100 km. One seasonal synthesis; no separate monthly values, annual extrema or mapped edges.');svg.style.cssText='display:block;width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
  const x=v=>40+420*v/150,[low,high]=row.width_range_km;
  add('line',{x1:40,x2:460,y1:95,y2:95,stroke:'#526c77'});add('line',{x1:x(low),x2:x(high),y1:60,y2:60,stroke:'#176b82','stroke-width':5});
  for(const v of [low,high]){add('line',{x1:x(v),x2:x(v),y1:50,y2:70,stroke:'#176b82','stroke-width':3});add('text',{x:x(v),y:30,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`${v} km`);}
  for(const v of [0,150])add('text',{x:x(v),y:125,'text-anchor':v?'end':'start','font-size':26,fill:'#102f3b'},`${v} km`);
  const caption=document.createElement('figcaption');caption.textContent='March-May · one approximate regional span, no midpoint selected. The shallow northern coastal flow is distinct from its underlying southward current. No monthly widths, confidence interval, annual range or footprint inferred.';figure.append(caption);
  const calendar=document.createElement('div');calendar.className='seasonal-width-calendar';calendar.style.cssText='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.4rem;margin:1rem 0;font-size:14px';calendar.setAttribute('aria-label','Seasonal width evidence coverage');figure.append(calendar);
  ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].forEach((month,i)=>{const cell=document.createElement('div'),covered=row.calendar_months.includes(i+1);cell.dataset.widthEvidence=covered?'seasonal_statement':'unknown';cell.style.cssText='padding:.4rem;border:1px solid #69808a;overflow-wrap:anywhere';cell.textContent=`${month}: ${covered?'seasonal span':'width unknown'}`;calendar.append(cell);});
  const note=document.createElement('p');note.textContent='The three marked months identify the source season. They are not three measured values. Width evidence for the other nine months remains unknown; this does not imply zero width or absence of flow.';figure.append(note);
};
