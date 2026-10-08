"use strict";
window.renderAtlasWidthEvidence = function(panel, current, inventory) {
  const id=current.id.replace(/^current:/,'');
  const section=document.createElement('section');section.className='atlas-width-evidence';panel.append(section);
  const node=(tag,text,parent=section)=>{const element=document.createElement(tag);element.textContent=text;parent.append(element);return element;};
  const link=(text,href,parent)=>{const anchor=node('a',text,parent);anchor.href=href;return anchor;};
  node('h4','Published width evidence');
  if(!inventory) {node('p','Width inventory unavailable. The detailed evidence page may have additional records.');link('Open width evidence','seasons.html?current='+encodeURIComponent(id),section);return;}
  const records=inventory.measurements.filter(row=>row.current_id===id);
  const decision=inventory.current_decisions.find(row=>row.current_id===id);
  if(!records.length) {
    const review=inventory.review_assessments?.find(row=>row.current_id===id);
    node('p',review?'Reviewed sources have not supplied a comparable numeric current width.':decision?.width_decision==='derived_width_candidate_requires_review'?'A derived section-width candidate is available; no published width record is stored here.':'No published width record is stored yet; width remains unresolved.');
    if(review) {node('p',review.reason);for(const evidence of review.evidence)link(evidence.citation,evidence.url,node('p',''));}
    node('p','Missing evidence does not mean zero width or physical absence.');return;
  }
  node('p',`${records.length} local or regional source record${records.length===1?'':'s'}. Definitions differ; these do not establish a uniform whole-current width or annual extrema.`);
  const format=value=>Number(value).toLocaleString('en-US');
  for(const row of records) {
    const details=document.createElement('details');details.className='atlas-width-record';details.dataset.measurementId=row.id;section.append(details);
    const angular=row.ensemble_angular_context;
    const value=angular?`${format(angular.source_reported_latitude_span_degrees)}° latitude (~${format(row.approximate_width_km)} km conversion)`
      :row.phase_kind==='width_time_series_statistics'?`${format(row.approximate_width_km)} km mean (${row.width_range_km.map(format).join('–')} km observed)`
      :row.phase_kind==='survey_layer_median_threshold_width'?`${format(row.approximate_width_km)} ±${format(row.reported_total_error_km)} km source width and total error`
      :row.phase_kind==='mean_offshore_extent_range'?`${row.width_range_km.map(format).join('–')} km mean surface offshore extent (not full width)`
      :row.approximate_width_km===null?`${row.width_range_km.map(format).join('–')} km reported span`:`about ${format(row.approximate_width_km)} km`;
    node('summary',`${value} · ${row.width_metric_label||row.width_metric.replaceAll('_',' ')} · ${row.phase_label}`,details);
    node('p',row.time_convention,details);
    node('p',`${row.geographic_scope} ${row.layer}`,details);
    node('p',`Definition: ${row.boundary_rule}${row.boundary_sides?' Boundary support: '+row.boundary_sides.replaceAll('_',' ')+'.':''}`,details);
    node('p',row.range_interpretation,details);
    if(row.source_quality_note)node('p',row.source_quality_note,details);
    const links=node('p','',details);
    link('Inspect this width record',`seasons.html?current=${encodeURIComponent(id)}&phase=${encodeURIComponent(row.id)}`,links);
    links.append(document.createTextNode(' · '));link('Published source',row.source_url,links);
    if(row.phase_kind==='width_time_series_statistics'&&id==='florida'){
      const query={collection:'width_samples',filters:[{field:'current_id',op:'eq',value:'florida'}],sort:{field:'month',direction:'asc'},limit:100};
      links.append(document.createTextNode(' · '));link('Monthly width chart','query.html?q='+encodeURIComponent(JSON.stringify(query)),links);
    }
    node('p',`${row.source_citation} ${row.source_locator}`,details);
  }
  node('p','Editorial source extractions; independent scientific admission pending.');
};
