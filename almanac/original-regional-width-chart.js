"use strict";
window.renderOriginalRegionalWidth=function(container,row){
  if(!row?.original_regional_context)return;
  const figure=document.createElement("figure");figure.className="original-regional-width";figure.style.margin="0";container.append(figure);
  const ns="http://www.w3.org/2000/svg",svg=document.createElementNS(ns,"svg");figure.append(svg);
  const point=row.width_range_km===null;
  const [low,high]=point?[row.approximate_width_km,row.approximate_width_km]:row.width_range_km,maximum=Math.ceil(high/25)*25+25;
  svg.setAttribute("viewBox","0 0 500 135");svg.setAttribute("role","img");svg.setAttribute("aria-label",point?`${row.name}: approximate regional width ${low} km. Background synthesis, not dated width observations, annual extrema or mapped boundaries. No width range supplied; numerical uncertainty unknown.`:`${row.name}: reported regional width span ${low} to ${high} km. Background synthesis, not dated glider measurements, annual extrema or mapped boundaries. No midpoint selected; numerical uncertainty unknown.`);
  svg.style.cssText="display:block;width:100%;max-width:650px;background:#f6f5ef;color:#102f3b";
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
  const x=v=>40+420*v/maximum;
  add("line",{x1:40,x2:460,y1:95,y2:95,stroke:"#526c77"});
  if(point)add("circle",{cx:x(low),cy:60,r:6,fill:"#176b82"});
  else add("line",{x1:x(low),x2:x(high),y1:60,y2:60,stroke:"#176b82","stroke-width":5});
  for(const v of point?[low]:[low,high]){if(!point)add("line",{x1:x(v),x2:x(v),y1:50,y2:70,stroke:"#176b82","stroke-width":3});add("text",{x:x(v),y:30,"text-anchor":"middle","font-size":26,fill:"#102f3b"},`${point?'≈ ':''}${v} km`);}
  for(const v of [0,maximum])add("text",{x:x(v),y:125,"text-anchor":v?"end":"start","font-size":26,fill:"#102f3b"},`${v} km`);
  const caption=document.createElement("figcaption");caption.textContent=row.original_regional_context.display_caption||"Regional along-slope Atlantic Water flow · one 30–50 km background description, no midpoint selected. Numerical uncertainty unknown. The article's autumn 2014–2016 glider missions and 975 m sampling depth do not define this width's observation dates or layer. No annual range, monthly widths or mapped edges inferred.";figure.append(caption);
  const note=document.createElement("p");note.textContent=row.original_regional_context.display_method_note||"Original publisher text inspected; the width description cites Testor et al. (2005). The underlying width method remains unreviewed. Detached eddy diameters are separate quantities.";figure.append(note);
  const q={document:row.original_regional_context.audit_file,pointer:"/measurement",limit:50},a=document.createElement("a");a.href="query.html?source-q="+encodeURIComponent(JSON.stringify(q));a.textContent="Inspect regional width scope and source";figure.append(a);
};
