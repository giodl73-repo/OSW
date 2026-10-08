"use strict";
(() => {
  const byId=id=>document.getElementById(id), series=byId("branch-series"), month=byId("branch-month");
  const previous=byId("branch-prev"), next=byId("branch-next"), play=byId("branch-play"), chart=byId("branch-chart");
  const labels=["January","February","March","April","May","June","July","August","September","October","November","December"];
  let timer=null, playing=false, serial=0, ready=false;
  const params=new URL(location.href).searchParams;
  if (["surface_ssh","wod_upper400"].includes(params.get("branch-series"))) series.value=params.get("branch-series");
  const saved=Number(params.get("branch-month")); if(Number.isInteger(saved)&&saved>=1&&saved<=12)month.value=saved;
  function stop(){clearTimeout(timer);timer=null;playing=false;play.textContent="Play months";}
  function controls(pending=false){series.disabled=month.disabled=play.disabled=!ready||pending;previous.disabled=!ready||pending||Number(month.value)===1;next.disabled=!ready||pending||Number(month.value)===12;}
  function shape(tag,attrs,parent,text){const node=document.createElementNS("http://www.w3.org/2000/svg",tag);for(const [k,v] of Object.entries(attrs))node.setAttribute(k,v);if(text!==undefined)node.textContent=text;parent.append(node);return node;}
  function south(value){return `${Math.abs(value).toFixed(1)}°S`;}
  function interval(values){return `${Math.abs(values[1]).toFixed(1)}–${Math.abs(values[0]).toFixed(1)}°S`;}
  function paint(view){
    month.setAttribute("aria-valuetext",labels[view.month-1]);
    chart.replaceChildren();const svg=shape("svg",{viewBox:view.chart.view_box,role:"img","aria-label":"Historical monthly branching latitudes: separate surface SSH and upper-400-m cycles"},chart);
    shape("title",{},svg,"Monthly branching latitude off Madagascar");
    for(const tick of view.chart.latitude_ticks){shape("line",{x1:56,x2:584,y1:tick.y,y2:tick.y,stroke:"#c5ccd2"},svg);shape("text",{x:48,y:tick.y+4,"text-anchor":"end","font-size":12,fill:"#243844"},svg,`${Math.abs(tick.latitude)}°S`);}
    for(const curve of view.curves){
      const color=curve.id==="surface_ssh"?"#3f4c5a":"#9d3f33";
      shape("polyline",{points:curve.points.map(p=>`${p.x},${p.y}`).join(" "),fill:"none",stroke:color,"stroke-width":2,"stroke-dasharray":curve.id==="surface_ssh"?"none":"5 3"},svg);
      for(const point of curve.points){shape("line",{x1:point.x,x2:point.x,y1:point.reading_y[0],y2:point.reading_y[1],stroke:color,"stroke-width":2},svg);shape("circle",{cx:point.x,cy:point.y,r:curve.id===view.series_id&&point.month===view.month?6:2.5,fill:color},svg);}
    }
    for(const point of view.curves[0].points)shape("text",{x:point.x,y:232,"text-anchor":"middle","font-size":10,fill:"#243844"},svg,labels[point.month-1].slice(0,3));
    chart.hidden=false;
    const rows=byId("branch-rows");rows.replaceChildren();
    for(const row of view.rows){const tr=document.createElement("tr");if(row.month===view.month)tr.setAttribute("aria-current","true");for(const text of [labels[row.month-1],south(row.approximate_latitude_degrees_north),interval(row.plot_reading_interval_degrees_north)]){const td=document.createElement("td");td.textContent=text;tr.append(td);}rows.append(tr);}
    const period=view.source_period?`${view.source_period.start} to ${view.source_period.end}`:view.period_note;
    byId("branch-scope").textContent=`${view.layer}. ${period}. No source variability envelope extracted.`;
    byId("branch-status").textContent=`${labels[view.month-1]} · ${view.curves.find(c=>c.id===view.series_id).label} · ${south(view.selected.latitude)} · reading allowance ${interval(view.selected.reading_interval)}`;
    byId("branch-source").href=view.source_url;
    const url=new URL(location.href);url.searchParams.set("branch-series",view.series_id);url.searchParams.set("branch-month",view.month);history.replaceState(null,"",url);url.hash="branching-title";byId("branch-share").href=url;
    window.oswIndexBifurcationView=view;
  }
  async function draw(){
    const token=++serial;controls(true);byId("branch-status").dataset.pending="true";
    try{const view=await window.oswIndexSupport({section:"monthly_bifurcation",filter:series.value,month:Number(month.value)});if(token!==serial)return;paint(view);ready=true;controls();byId("branch-status").dataset.pending="false";
      if(playing&&Number(month.value)<12)timer=setTimeout(()=>{month.value=Number(month.value)+1;draw();},1200);else if(playing)stop();
    }catch(error){if(token!==serial)return;stop();ready=false;window.oswIndexBifurcationView=null;chart.hidden=true;chart.replaceChildren();byId("branch-rows").replaceChildren();byId("branch-scope").textContent="";byId("branch-status").textContent=`Seasonal evidence unavailable: ${error.message}`;byId("branch-status").dataset.pending="false";controls();}
  }
  for(const element of [series,month])element.addEventListener("change",()=>{stop();draw();});
  previous.addEventListener("click",()=>{stop();month.value=Number(month.value)-1;draw();});next.addEventListener("click",()=>{stop();month.value=Number(month.value)+1;draw();});
  play.addEventListener("click",()=>{if(playing){stop();return;}playing=true;play.textContent="Pause months";if(Number(month.value)===12)month.value=1;draw();});
  document.addEventListener("visibilitychange",()=>{if(document.hidden)stop();});
  window.addEventListener("pagehide",stop);
  window.matchMedia("(prefers-reduced-motion: reduce)").addEventListener("change",stop);
  draw();
})();
