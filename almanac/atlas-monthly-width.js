"use strict";
// A historical crossing chart: playback never changes atlas geometry.
window.initAtlasMonthlyWidth = function(panel, current, requestedMonth) {
  if (current.id !== 'current:leeuwin') return () => {};
  let disposed=false, timer=null, data=null;
  const section=document.createElement('section');section.className='atlas-monthly-width';panel.append(section);
  function html(tag,text,parent=section){const el=document.createElement(tag);el.textContent=text;parent.append(el);return el;}
  html('h4','Historical monthly widths · Leeuwin crossing a101');
  html('p','Calendar-month means across 1993–2002 at one altimeter crossing near 26°S. Scientific review pending. The source gives July and August 2002 as differing end months; the combined period is unresolved.');
  const controls=html('div','');controls.className='route-atlas-controls';
  const label=html('label','Month ',controls),select=html('select','',label);select.className='atlas-width-month';select.disabled=true;
  function button(text,cls){const b=html('button',text,controls);b.type='button';b.className=cls;b.disabled=true;return b;}
  const previous=button('Previous','atlas-width-previous'),next=button('Next','atlas-width-next'),play=button('Play months','atlas-width-play');
  const status=html('p','Loading extracted graph…');status.className='atlas-width-month-status';status.setAttribute('role','status');
  const ns='http://www.w3.org/2000/svg',chart=document.createElementNS(ns,'svg');chart.classList.add('atlas-monthly-chart');chart.setAttribute('viewBox','0 0 600 270');chart.setAttribute('role','img');section.append(chart);
  html('p','Bars show ±3 km graph-reading allowances, not confidence intervals or physical variability. Playback steps through the twelve extracted months and stops in December; the map route stays unchanged.');
  html('p','Source width: w = 1.89 L cos(43.45°). Per-cycle widths were fitted first, then averaged by calendar month. These values do not measure the width of the entire current.');
  html('p','The paper reports April about 132 km and September about 89 km in prose. July and September graph-reading intervals overlap, so this extraction does not establish a uniquely narrowest month.');
  function link(text,href){const a=html('a',text,html('p',''));a.href=href;return a;}
  link('Extraction rules and calibration','../plans/leeuwin-monthly-plot-extraction-protocol-v1.md');
  link('All values and source hashes (JSON)','../research/leeuwin-a101-monthly-plot-extraction.json');
  function stop(){if(timer!==null)clearInterval(timer);timer=null;play.textContent='Play months';play.setAttribute('aria-pressed','false');}
  function valid(doc){
    return doc?.schema==='osw.current-monthly-width-plot-extraction.v1'&&doc.current_id==='leeuwin'&&doc.track_id==='a101'&&doc.status==='editorial_plot_extraction_scientific_review_pending'&&doc.width_equation==='w = 1.89 * L * cos(theta)'&&doc.track_angle_degrees===43.45&&doc.reading_interval_kind==='editorial_plot_reading_allowance_not_measurement_uncertainty'&&doc.chart_playback_eligible===true&&doc.complete_monthly_curve_extracted===true&&['is_confidence_interval','whole_current_representative','width_rank_eligible','annual_extrema_eligible','geographic_playback_eligible','seasonal_playback_eligible','exact_combined_averaging_period_resolved'].every(key=>doc[key]===false)&&['whole_current_width_km','annual_width_range_km','section_geometry','fixed_layer_bounds_m','observed_period'].every(key=>doc[key]===null)&&Array.isArray(doc.months)&&doc.months.length===12&&doc.months.every((m,i)=>m.month===i+1&&typeof m.label==='string'&&Number.isInteger(m.approximate_width_km)&&m.approximate_width_km>=70&&m.approximate_width_km<=140&&m.reading_margin_km===3&&m.plot_reading_interval_km?.length===2&&m.plot_reading_interval_km[0]===m.approximate_width_km-3&&m.plot_reading_interval_km[1]===m.approximate_width_km+3);
  }
  function svg(tag,attrs,text){const el=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);if(text)el.textContent=text;chart.append(el);return el;}
  function render(){
    if(disposed||!data)return;
    const month=data.months[Number(select.value)-1];previous.disabled=month.month===1;next.disabled=month.month===12;play.disabled=month.month===12;
    if(month.month===12)stop();
    status.textContent=`${month.label}: approximately ${month.approximate_width_km} km; graph-reading allowance ${month.plot_reading_interval_km.join('–')} km. Historical monthly composite at crossing a101.`;
    chart.replaceChildren();chart.setAttribute('aria-label',status.textContent+' All twelve monthly graph readings with reading allowances; values also available in the table.');
    const x=m=>50+(m-1)*47,y=w=>215-(w-70)*2.5;
    for(const w of [70,90,110,130,140]){svg('line',{x1:45,x2:580,y1:y(w),y2:y(w),stroke:'#dbe7e7'});svg('text',{x:39,y:y(w)+4,'text-anchor':'end','font-size':13,fill:'#133c49'},String(w));}
    svg('text',{x:10,y:18,'font-size':13,fill:'#133c49'},'km');
    for(const m of data.months){const [lo,hi]=m.plot_reading_interval_km,c=m.month===month.month?'#a76509':'#087e9a';
      svg('line',{x1:x(m.month),x2:x(m.month),y1:y(lo),y2:y(hi),stroke:c,'stroke-width':2});
      for(const v of [lo,hi])svg('line',{x1:x(m.month)-5,x2:x(m.month)+5,y1:y(v),y2:y(v),stroke:c,'stroke-width':2});
      svg('circle',{cx:x(m.month),cy:y(m.approximate_width_km),r:m.month===month.month?6:3,fill:c});
      svg('text',{x:x(m.month),y:242,'text-anchor':'middle','font-size':13,fill:'#133c49'},m.label.slice(0,3));
    }
    const url=new URL(location.href);url.searchParams.set('atlas-width-month',String(month.month));history.replaceState(null,'',url);
    const share=panel.querySelector('[data-atlas-share]');if(share)share.href=url.href;
  }
  select.addEventListener('change',()=>{stop();render();});
  previous.addEventListener('click',()=>{stop();select.value=String(Number(select.value)-1);render();});
  next.addEventListener('click',()=>{stop();select.value=String(Number(select.value)+1);render();});
  play.addEventListener('click',()=>{if(timer!==null){stop();return;}play.textContent='Pause';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{select.value=String(Number(select.value)+1);render();},1800);});
  const visibility=()=>{if(document.hidden)stop();};document.addEventListener('visibilitychange',visibility);
  window.oswAtlasSourcesReady.then(docs=>{const doc=docs['research/leeuwin-a101-monthly-plot-extraction.json'];if(!doc)throw Error('Missing checked extraction');return doc;}).then(doc=>{
    if(disposed)return;if(!valid(doc))throw Error('Invalid extraction scope');data=doc;
    for(const m of data.months){const option=html('option',m.label,select);option.value=String(m.month);}
    select.disabled=false;select.value=/^(?:[1-9]|1[0-2])$/.test(requestedMonth||'')?requestedMonth:'1';
    link('Published source · Figure 7d, page 144',data.source_url+'#page=10');
    const details=html('details','');html('summary','All twelve graph readings',details);const table=html('table','',details);
    html('caption','Approximate km and graph-reading allowance; not whole-current widths',table);
    const header=html('tr','',html('thead','',table));for(const title of ['Month','Width (km)','Reading allowance (km)']){const th=html('th',title,header);th.scope='col';}
    const body=html('tbody','',table);for(const m of data.months){const row=html('tr','',body);const th=html('th',m.label,row);th.scope='row';html('td',String(m.approximate_width_km),row);html('td',m.plot_reading_interval_km.join('–'),row);}
    render();
  }).catch(()=>{if(!disposed)status.textContent='Monthly graph unavailable or invalid. Published width records and the route remain available.';});
  return()=>{disposed=true;stop();document.removeEventListener('visibilitychange',visibility);};
};
