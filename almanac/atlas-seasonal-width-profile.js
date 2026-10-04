"use strict";
window.initAtlasSeasonalWidthProfile=function(panel,current,requestedSeason){
  if(current.id!=='current:kuroshio')return()=>{};
  let disposed=false,data=null,timer=null;
  const section=document.createElement('section');section.className='atlas-seasonal-width-profile';panel.append(section);
  function html(tag,text,parent=section){const node=document.createElement(tag);node.textContent=text;parent.append(node);return node;}
  html('h4','Seasonal width profiles · East China Sea · 1993–2008');
  html('p','Graph readings of regional seasonal mean section widths, normal to the diagnosed jet axis at a 0.1 m/s surface geostrophic cutoff. Longitude indexes the stream profile; it does not give geographic boundary coordinates.');
  const controls=html('div','');controls.className='route-atlas-controls';
  const label=html('label','Season ',controls),select=html('select','',label);select.className='atlas-width-season';select.disabled=true;
  function button(text,cls){const b=html('button',text,controls);b.className=cls;b.type='button';b.disabled=true;return b;}
  const previous=button('Previous','atlas-profile-previous'),next=button('Next','atlas-profile-next'),play=button('Play profiles','atlas-profile-play');
  const status=html('p','Loading extracted seasonal profiles…');status.className='atlas-profile-status';status.setAttribute('role','status');
  const ns='http://www.w3.org/2000/svg',chart=document.createElementNS(ns,'svg');chart.classList.add('atlas-monthly-chart');chart.setAttribute('viewBox','0 0 600 310');chart.setAttribute('role','img');section.append(chart);
  html('p','Bars show ±10 km editorial graph-reading allowances, not measurement uncertainty or confidence. Gray × markers below the plot are unreadable or ambiguous samples. Values are rounded to 5 km; missing samples stay missing.');
  html('p','Playback steps through the four plotted seasonal profiles and stops in autumn. It does not change map geometry. Exact seasonal month membership and averaging weights remain unresolved. The 122°E endpoint under the legend and the 130°E border are unsampled.');
  html('p','The source regional means (winter about 218 km, summer about 207 km, study mean about 210 km) remain separate records above. Sparse graph readings do not supply spring/autumn regional means or a physical annual range.');
  function link(text,href){const a=html('a',text,html('p',''));a.href=href;return a;}
  link('Extraction calibration and missing-value rules','../plans/kuroshio-seasonal-width-profile-extraction-protocol-v1.md');
  link('All profile readings and source hashes (JSON)','../research/kuroshio-ecs-seasonal-width-profile-extraction.json');
  const details=html('details','');html('summary','Selected profile readings',details);
  const table=html('table','',details);html('caption','Longitude, approximate width and graph-reading allowance; not boundary coordinates',table);
  const header=html('tr','',html('thead','',table));for(const title of ['Longitude °E','Width (km)','Reading allowance (km)']){const th=html('th',title,header);th.scope='col';}
  const body=html('tbody','',table);
  function stop(){if(timer!==null)clearInterval(timer);timer=null;play.textContent='Play profiles';play.setAttribute('aria-pressed','false');}
  function valid(doc){
    return doc?.schema==='osw.current-seasonal-width-profile-plot-extraction.v1'&&doc.current_id==='kuroshio'&&doc.status==='editorial_plot_extraction_scientific_review_pending'&&doc.velocity_threshold_m_s===.1&&doc.width_metric==='seasonal_mean_diagnosed_axis_normal_0.1m_s_threshold_span'&&JSON.stringify(doc.study_period_years)==='[1993,2008]'&&doc.reading_margin_km===10&&doc.rounding_km===5&&doc.reading_interval_kind==='editorial_plot_reading_allowance_not_measurement_uncertainty'&&doc.chart_playback_eligible===true&&['geographic_playback_eligible','whole_current_representative','width_rank_eligible','is_confidence_interval','annual_extrema_eligible','seasonal_playback_eligible','season_month_membership_resolved','averaging_weight_detail_resolved'].every(k=>doc[k]===false)&&['whole_current_width_km','annual_width_range_km','section_geometry','fixed_layer_bounds_m','observed_period'].every(k=>doc[k]===null)&&Array.isArray(doc.seasons)&&doc.seasons.length===4&&doc.seasons.every((s,i)=>s.label===['winter','spring','summer','autumn'][i]&&s.calendar_months===null&&s.regional_mean_width_km===null&&s.geographic_edge_coordinates===null&&Array.isArray(s.samples)&&s.samples.length===16&&s.samples.every((r,j)=>r.longitude_degrees_east===(j===15?129.9:122.5+j*.5)&&(r.approximate_width_km===null?r.status==='unresolved_color_occlusion_or_ambiguity'&&r.plot_reading_interval_km===null:r.status==='resolved_plot_reading'&&Number.isInteger(r.approximate_width_km)&&r.approximate_width_km>=140&&r.approximate_width_km<=275&&r.approximate_width_km%5===0&&r.plot_reading_interval_km?.length===2&&r.plot_reading_interval_km[0]===r.approximate_width_km-10&&r.plot_reading_interval_km[1]===r.approximate_width_km+10))&&s.resolved_samples===s.samples.filter(r=>r.approximate_width_km!==null).length);
  }
  function svg(tag,attrs,text){const node=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))node.setAttribute(k,v);if(text)node.textContent=text;chart.append(node);return node;}
  function render(){
    if(disposed||!data)return;
    const index=data.seasons.findIndex(s=>s.label===select.value),season=data.seasons[index];
    previous.disabled=index===0;next.disabled=index===3;play.disabled=index===3;if(index===3)stop();
    status.textContent=`${season.label}: ${season.resolved_samples} of 16 graph samples readable. Historical regional seasonal profile; unreadable samples are missing, not zero.`;
    chart.replaceChildren();chart.setAttribute('aria-label',status.textContent+' Width in km versus longitude along stream; selected values and reading allowances also appear in the table.');
    const x=lon=>50+(lon-122.5)/7.4*520,y=w=>230-(w-140)*1.4;
    for(const width of [140,180,220,260,280]){svg('line',{x1:45,x2:580,y1:y(width),y2:y(width),stroke:'#dbe7e7'});svg('text',{x:40,y:y(width)+4,'text-anchor':'end','font-size':13,fill:'#133c49'},String(width));}
    svg('text',{x:8,y:18,'font-size':13,fill:'#133c49'},'km');
    for(const longitude of [123,124,125,126,127,128,129])svg('text',{x:x(longitude),y:252,'text-anchor':'middle','font-size':13,fill:'#133c49'},String(longitude));
    svg('text',{x:8,y:272,'font-size':12,fill:'#45646e'},'missing');
    svg('text',{x:300,y:299,'text-anchor':'middle','font-size':14,fill:'#133c49'},'Longitude along stream (°E)');
    body.replaceChildren();
    for(const sample of season.samples){
      const row=html('tr','',body),th=html('th',String(sample.longitude_degrees_east),row);th.scope='row';
      if(sample.approximate_width_km===null){svg('text',{x:x(sample.longitude_degrees_east),y:272,'text-anchor':'middle','font-size':18,fill:'#45646e'},'×');html('td','missing',row);html('td','unreadable or ambiguous',row);continue;}
      const [lo,hi]=sample.plot_reading_interval_km;
      svg('line',{x1:x(sample.longitude_degrees_east),x2:x(sample.longitude_degrees_east),y1:y(lo),y2:y(hi),stroke:'#087e9a','stroke-width':2});
      for(const value of [lo,hi])svg('line',{x1:x(sample.longitude_degrees_east)-4,x2:x(sample.longitude_degrees_east)+4,y1:y(value),y2:y(value),stroke:'#087e9a','stroke-width':2});
      svg('circle',{cx:x(sample.longitude_degrees_east),cy:y(sample.approximate_width_km),r:3,fill:'#087e9a'});
      html('td',String(sample.approximate_width_km),row);html('td',sample.plot_reading_interval_km.join('–'),row);
    }
    const url=new URL(location.href);url.searchParams.set('atlas-width-season',season.label);history.replaceState(null,'',url);
    const share=panel.querySelector('[data-atlas-share]');if(share)share.href=url.href;
  }
  select.addEventListener('change',()=>{stop();render();});
  previous.addEventListener('click',()=>{stop();select.selectedIndex--;render();});next.addEventListener('click',()=>{stop();select.selectedIndex++;render();});
  play.addEventListener('click',()=>{if(timer!==null){stop();return;}play.textContent='Pause';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{select.selectedIndex++;render();},1800);});
  const visibility=()=>{if(document.hidden)stop();};document.addEventListener('visibilitychange',visibility);
  fetch('../research/kuroshio-ecs-seasonal-width-profile-extraction.json',{cache:'no-store'}).then(async r=>{if(!r.ok)throw Error('Missing seasonal profiles');return r.json();}).then(doc=>{
    if(disposed)return;if(!valid(doc))throw Error('Invalid seasonal profile scope');data=doc;
    for(const season of data.seasons){const option=html('option',season.label,select);option.value=season.label;}
    select.disabled=false;select.value=data.seasons.some(s=>s.label===requestedSeason)?requestedSeason:'winter';
    link('Published source · Figure 6a, page 30',data.source_url);render();
  }).catch(()=>{if(!disposed)status.textContent='Seasonal profile graph unavailable or invalid. The source prose width records remain available.';});
  return()=>{disposed=true;stop();document.removeEventListener('visibilitychange',visibility);};
};
