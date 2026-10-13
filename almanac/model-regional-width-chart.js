"use strict";
window.renderModelRegionalWidth=function(container,row){
  if(row?.phase_kind!=="model_regional_width_summary")return;
  const figure=document.createElement("figure");figure.className="model-regional-width";figure.style.margin="0";container.append(figure);
  const ns="http://www.w3.org/2000/svg",svg=document.createElementNS(ns,"svg");figure.append(svg);
  svg.setAttribute("viewBox","0 0 500 135");svg.setAttribute("role","img");svg.setAttribute("aria-label",`${row.name}: approximately ${row.approximate_width_km} km regional annual-mean reference-model width. Numerical uncertainty unknown; not monthly variation, annual extrema or mapped edges.`);
  svg.style.cssText="display:block;width:100%;max-width:650px;background:#f6f5ef;color:#102f3b";
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
  const x=v=>40+420*v/300;
  add("line",{x1:40,x2:460,y1:95,y2:95,stroke:"#526c77"});
  add("circle",{cx:x(row.approximate_width_km),cy:60,r:7,fill:"#176b82"});
  add("text",{x:x(row.approximate_width_km),y:30,"text-anchor":"middle","font-size":26,fill:"#102f3b"},`~${row.approximate_width_km} km`);
  for(const v of [0,300])add("text",{x:x(v),y:125,"text-anchor":v?"end":"start","font-size":26,fill:"#102f3b"},`${v} km`);
  const caption=document.createElement("figcaption");caption.textContent="Regional annual-mean reference ROMS surface flow. One approximate published model width; numerical uncertainty unknown. Model years 5–10 are not calendar dates. This mean supplies no monthly widths, annual extrema or mapped boundaries.";figure.append(caption);
  const note=document.createElement("p");note.textContent="The paper's 210 km theoretical inertial boundary-layer scale is a different quantity, not a second width or an error bound. The 30–40 m introductory thickness is not a fixed width layer. Figure-caption disagreement remains recorded; this point uses the explicit reference-experiment prose.";figure.append(note);
  const query={document:row.model_regional_context.audit_file,pointer:"/measurement",limit:50},link=document.createElement("a");link.href="query.html?source-q="+encodeURIComponent(JSON.stringify(query));link.textContent="Inspect source scope and model support";figure.append(link);
};
