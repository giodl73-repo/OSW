"use strict";
window.renderOriginalRegionalWidth=function(container,row){
  if(!row?.original_regional_context||['aacc_composite_threshold_section','dwbc_upper_core_float_composite'].includes(row.original_regional_context.description_kind))return;
  if(row.reported_width_constraint){window.renderReportedWidthConstraint(container,row);return;}
  const figure=document.createElement("figure");figure.className="original-regional-width";figure.style.margin="0";container.append(figure);
  const ns="http://www.w3.org/2000/svg",svg=document.createElementNS(ns,"svg");figure.append(svg);
  const point=row.width_range_km===null;
  const [low,high]=point?[row.approximate_width_km,row.approximate_width_km]:row.width_range_km,maximum=Math.ceil(high/25)*25+25;
  svg.setAttribute("viewBox","0 0 500 135");svg.setAttribute("role","img");svg.setAttribute("aria-label",point?`${row.name}: approximate regional width ${low} km. Background synthesis, not dated width observations, annual extrema or mapped boundaries. No width range supplied; numerical uncertainty unknown.`:`${row.name}: reported regional width span ${low} to ${high} km. Background synthesis, not dated glider measurements, annual extrema or mapped boundaries. No midpoint selected; numerical uncertainty unknown.`);
  svg.style.cssText="display:block;width:100%;max-width:650px;background:#f6f5ef;color:#102f3b";
  if(row.original_regional_context.temporal_operator==="monthly_mean")svg.setAttribute("aria-label",`${row.name}: approximate meridional jet width ${low} km in monthly mean fields. No dated width series extracted; numerical uncertainty unknown. Separate 200 km climatological meridional scale is contextual, not a width range endpoint.`);
  const scopedDescription=!!row.original_regional_context.description_kind;
  const labelSize=scopedDescription?36:26;
  if(scopedDescription)svg.setAttribute("aria-label",row.original_regional_context.display_aria_label||`${row.phase_label}: reported regional description ${low} km. Primary publisher HTML text; core/jet relationship unresolved. No combined seasonal range or mapped width edges.`);
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
  const x=v=>40+420*v/maximum;
  add("line",{x1:40,x2:460,y1:95,y2:95,stroke:"#526c77"});
  if(point)add("circle",{cx:x(low),cy:60,r:6,fill:"#176b82"});
  else add("line",{x1:x(low),x2:x(high),y1:60,y2:60,stroke:"#176b82","stroke-width":5});
  const closeLabels=!point&&x(high)-x(low)<labelSize*(`${low} km`.length+`${high} km`.length)*.3+8;
  for(const v of point?[low]:[low,high]){if(!point)add("line",{x1:x(v),x2:x(v),y1:50,y2:70,stroke:"#176b82","stroke-width":3});add("text",{x:x(v),y:30,"text-anchor":closeLabels?(v===low?"end":"start"):point&&v/maximum>.8?"end":"middle","font-size":labelSize,fill:"#102f3b"},`${point?'≈ ':''}${v} km`);}
  for(const v of [0,maximum])add("text",{x:x(v),y:125,"text-anchor":v?"end":"start","font-size":labelSize,fill:"#102f3b"},`${v} km`);
  const caption=document.createElement("figcaption");caption.textContent=row.original_regional_context.display_caption||"Regional along-slope Atlantic Water flow · one 30–50 km background description, no midpoint selected. Numerical uncertainty unknown. The article's autumn 2014–2016 glider missions and 975 m sampling depth do not define this width's observation dates or layer. No annual range, monthly widths or mapped edges inferred.";figure.append(caption);
  const note=document.createElement("p");note.textContent=row.original_regional_context.display_method_note||"Original publisher text inspected; the width description cites Testor et al. (2005). The underlying width method remains unreviewed. Detached eddy diameters are separate quantities.";figure.append(note);
  const q={document:row.original_regional_context.audit_file,pointer:row.original_regional_context.audit_pointer||"/measurement",limit:50},a=document.createElement("a");a.href="query.html?source-q="+encodeURIComponent(JSON.stringify(q));a.textContent="Inspect regional width scope and source";figure.append(a);
  if(row.original_regional_context.section_comparison)window.renderQualitativeSectionComparison(figure,row);
};

window.renderQualitativeSectionComparison=function(container,row){
  const comparison=row.original_regional_context.section_comparison;
  const add=(tag,text,parent)=>{const el=document.createElement(tag);if(text!=null)el.textContent=text;parent?.append(el);return el;};
  const panel=add('section',null,container);panel.className='qualitative-section-comparison';
  add('h4','Strahan · two 1997 occupations',panel);
  add('p',comparison.width_relation+'. '+comparison.strength_relation+'. Numerical section widths and width ratio remain unknown.',panel);
  const grid=add('div',null,panel);grid.style.cssText='display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.5rem';
  for(const record of comparison.records){const item=add('div',null,grid);item.style.cssText='border:1px solid #68818a;padding:.6rem;min-width:0';add('strong',record.observed_month,item);add('p',record.width_description,item);add('p','Numerical width: unknown',item);add('small','Stations '+record.station_label+' · exact occupation day unknown',item);}
  add('p','Relative comparison from the source; the historical 40 km value is not assigned to either section. Two occupations do not establish annual extrema, a seasonal range or monthly evolution.',panel);
  add('small',comparison.source_locator,panel);
  const link=add('a','Query both occupation contexts',add('p',null,panel));link.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:row.original_regional_context.audit_file,pointer:'/measurement/original_regional_context/section_comparison/records',limit:50}));
};

window.renderReportedWidthConstraint=function(container,row){
  const figure=document.createElement('figure');figure.className='original-regional-width reported-width-constraint';figure.style.margin='0';container.append(figure);
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');figure.append(svg);
  svg.setAttribute('viewBox','0 0 500 100');svg.setAttribute('role','img');
  const breadth=row.reported_width_constraint.kind==='issuer_reported_greater_than_geographic_breadth';
  const confinement=row.reported_width_constraint.kind==='author_reported_one_sided_coastal_confinement';
  const broadBand=row.reported_width_constraint.kind==='author_reported_greater_than_broad_flow_band';
  svg.setAttribute('aria-label',breadth?`${row.name}: source reports offshore geographic breadth ${row.reported_width_constraint.source_notation}. Government synthesis, not a measured velocity-core width, finite interval or seasonal range. Representative width and numerical uncertainty unknown.`:`${row.name}: source reports ${row.reported_width_constraint.source_notation}. Approximate less-than size description, not a measured 20 km width, rigorous hard bound or zero-to-20 km interval. Representative width and numerical uncertainty unknown.`);
  svg.style.cssText='display:block;width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';
  if(confinement||broadBand)svg.setAttribute('aria-label',row.original_regional_context.display_aria_label);
  for(const [label,y,size] of [[row.reported_width_constraint.source_notation,40,36],[broadBand?row.original_regional_context.display_constraint_label:confinement?'Coastal confinement':breadth?'Reported offshore breadth':'Reported size constraint',80,breadth?32:28]]){
    const text=document.createElementNS(ns,'text');text.setAttribute('x',25);text.setAttribute('y',y);text.setAttribute('font-size',size);text.setAttribute('fill','#102f3b');text.textContent=label;svg.append(text);
  }
  const caption=document.createElement('figcaption');caption.textContent=row.original_regional_context.display_caption;figure.append(caption);
  const note=document.createElement('p');note.textContent=row.original_regional_context.display_method_note;figure.append(note);
  const a=document.createElement('a');a.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:row.original_regional_context.audit_file,pointer:row.original_regional_context.audit_pointer||'/measurement',limit:50}));a.textContent=broadBand?'Inspect broad flow definition and source':confinement?'Inspect coastal confinement and source':'Inspect size constraint and source';figure.append(a);
};
