"use strict";
(() => {
  const byId=id=>document.getElementById(id), owner=byId("branch-current"), series=byId("branch-series"), month=byId("branch-month");
  const previous=byId("branch-prev"), next=byId("branch-next"), play=byId("branch-play"), chart=byId("branch-chart");
  const labels=["January","February","March","April","May","June","July","August","September","October","November","December"];
  let timer=null, playing=false, serial=0, ready=false;
  const params=new URL(location.href).searchParams;
  if (["indian-south-equatorial","pacific-north-equatorial"].includes(params.get("branch-current"))) owner.value=params.get("branch-current");
  function layers(){const upper=series.querySelector('[value="wod_upper400"]');upper.disabled=owner.value==="pacific-north-equatorial";if(upper.disabled&&series.value==="wod_upper400")series.value="surface_ssh";}
  if (["surface_ssh","wod_upper400"].includes(params.get("branch-series"))) series.value=params.get("branch-series");
  layers();
  const saved=Number(params.get("branch-month")); if(Number.isInteger(saved)&&saved>=1&&saved<=12)month.value=saved;
  function stop(){clearTimeout(timer);timer=null;playing=false;play.textContent="Play months";}
  function controls(pending=false){owner.disabled=series.disabled=play.disabled=!ready||pending;month.disabled=!ready;previous.disabled=!ready||pending||Number(month.value)===1;next.disabled=!ready||pending||Number(month.value)===12;}
  function shape(tag,attrs,parent,text){const node=document.createElementNS("http://www.w3.org/2000/svg",tag);for(const [k,v] of Object.entries(attrs))node.setAttribute(k,v);if(text!==undefined)node.textContent=text;parent.append(node);return node;}
  function latitude(value){return `${Math.abs(value).toFixed(1)}°${value<0?"S":"N"}`;}
  function interval(values){const ordered=values[1]<0?[values[1],values[0]]:values;return `${Math.abs(ordered[0]).toFixed(1)}–${latitude(ordered[1])}`;}
  function paint(view){
    const pacific=view.current_id==="pacific-north-equatorial";
    const name=pacific?"Pacific North Equatorial":"Indian South Equatorial";
    byId("branching-title").textContent=`Where does the ${name} flow branch?`;
    month.setAttribute("aria-valuetext",labels[view.month-1]);
    chart.replaceChildren();const svg=shape("svg",{viewBox:view.chart.view_box,role:"img","aria-label":`${name} historical monthly branching latitudes; ${pacific?"surface SSH mean and source-labelled standard-deviation band":"separate surface SSH and upper-400-m cycles"}`},chart);
    shape("title",{},svg,pacific?"Monthly branching latitude off the Philippines":"Monthly branching latitude off Madagascar");
    for(const tick of view.chart.latitude_ticks){shape("line",{x1:56,x2:584,y1:tick.y,y2:tick.y,stroke:"#c5ccd2"},svg);shape("text",{x:48,y:tick.y,dy:".35em","text-anchor":"end","font-size":12,fill:"#243844"},svg,`${Math.abs(tick.latitude)}°${tick.latitude<0?"S":"N"}`);}
    for(const curve of view.curves){
      const color=curve.id==="surface_ssh"?"#3f4c5a":"#9d3f33";
      if(view.source_variability_envelope_extracted){
        const points=[...curve.points.map(p=>`${p.x},${p.source_band_y[0]}`),...curve.points.slice().reverse().map(p=>`${p.x},${p.source_band_y[1]}`)].join(" ");
        shape("polygon",{points,fill:"#899caa","fill-opacity":0.3,stroke:"#647886","stroke-width":1.5,"vector-effect":"non-scaling-stroke","data-source-band":"standard-deviation"},svg);
      }
      shape("polyline",{points:curve.points.map(p=>`${p.x},${p.y}`).join(" "),fill:"none",stroke:color,"stroke-width":2,"stroke-dasharray":curve.id==="surface_ssh"?"none":"5 3"},svg);
      for(const point of curve.points){shape("line",{x1:point.x,x2:point.x,y1:point.reading_y[0],y2:point.reading_y[1],stroke:color,"stroke-width":2},svg);shape("circle",{cx:point.x,cy:point.y,r:curve.id===view.series_id&&point.month===view.month?6:2.5,fill:color},svg);}
    }
    for(const point of view.curves[0].points)shape("text",{x:point.x,y:232,"text-anchor":"middle","font-size":10,fill:"#243844"},svg,labels[point.month-1].slice(0,3));
    chart.hidden=false;
    const rows=byId("branch-rows");rows.replaceChildren();
    for(const row of view.rows){const tr=document.createElement("tr");if(row.month===view.month)tr.setAttribute("aria-current","true");for(const text of [labels[row.month-1],latitude(row.approximate_latitude_degrees_north),interval(row.plot_reading_interval_degrees_north),row.approximate_source_standard_deviation_band_degrees_north?`${interval(row.approximate_source_standard_deviation_band_degrees_north)}; endpoint reading allowances ${row.band_endpoint_plot_reading_intervals_degrees_north.map(interval).join(" / ")}`:"Not extracted"]){const td=document.createElement("td");td.textContent=text;tr.append(td);}rows.append(tr);}
    const period=view.source_period?`${view.source_period.start} to ${view.source_period.end}`:view.period_note;
    byId("branch-scope").textContent=`${view.layer}. ${period}. ${view.scope}`;
    byId("branch-legend").textContent=`Solid gray: surface SSH.${pacific?" Shading shows the source-reported spread around the monthly mean, labelled a standard-deviation range; denominator and multiplier are not recovered. Shading is not a confidence interval, full observation envelope or annual extrema. Each band endpoint has its own ±0.1° graph-reading allowance in the table.":" Dashed red: upper 400 m. No source variability envelope extracted."} Bars show ±0.1° graph-reading allowances for the means, not measurement uncertainty or confidence intervals. Each series provides one historical monthly cycle; the repeated cycle in its figure is not a second observed year.`;
    byId("branch-status").textContent=`${labels[view.month-1]} · ${view.curves.find(c=>c.id===view.series_id).label} · ${latitude(view.selected.latitude)} · reading allowance ${interval(view.selected.reading_interval)}`;
    byId("branch-source").href=view.source_url;byId("branch-source").textContent=view.source_locator;
    byId("branch-card").href=`reference-routes.html#inventory-addition-${view.current_id}`;
    const url=new URL(location.href);url.searchParams.set("branch-current",view.current_id);url.searchParams.set("branch-series",view.series_id);url.searchParams.set("branch-month",view.month);history.replaceState(null,"",url);url.hash="branching-title";byId("branch-share").href=url;
    window.oswIndexBifurcationView=view;
  }
  async function draw(){
    const token=++serial;controls(true);byId("branch-status").dataset.pending="true";
    try{const view=await window.oswIndexSupport({section:"monthly_bifurcation",current_id:owner.value,filter:series.value,month:Number(month.value)});if(token!==serial)return;paint(view);ready=true;controls();byId("branch-status").dataset.pending="false";
      if(playing&&Number(month.value)<12)timer=setTimeout(()=>{month.value=Number(month.value)+1;draw();},1200);else if(playing)stop();
    }catch(error){if(token!==serial)return;stop();ready=false;window.oswIndexBifurcationView=null;chart.hidden=true;chart.replaceChildren();byId("branch-rows").replaceChildren();byId("branch-scope").textContent="";byId("branch-legend").textContent="";byId("branch-source").removeAttribute("href");byId("branch-card").removeAttribute("href");byId("branch-share").removeAttribute("href");byId("branch-status").textContent=`Seasonal evidence unavailable: ${error.message}`;byId("branch-status").dataset.pending="false";controls();}
  }
  owner.addEventListener("change",()=>{stop();layers();draw();});
  for(const element of [series,month])element.addEventListener("change",()=>{stop();draw();});
  previous.addEventListener("click",()=>{stop();month.value=Number(month.value)-1;draw();});next.addEventListener("click",()=>{stop();month.value=Number(month.value)+1;draw();});
  play.addEventListener("click",()=>{if(playing){stop();return;}playing=true;play.textContent="Pause months";if(Number(month.value)===12)month.value=1;draw();});
  document.addEventListener("visibilitychange",()=>{if(document.hidden)stop();});
  window.addEventListener("pagehide",stop);
  window.matchMedia("(prefers-reduced-motion: reduce)").addEventListener("change",stop);
  draw();
})();
