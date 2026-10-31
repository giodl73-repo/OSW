"use strict";
(async()=>{
  const $=id=>document.getElementById(id),add=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;};
  const units={km:'km',km2:'km²',day:'days',year:'years',month:'months',week:'weeks',percent:'%',degree_latitude:'degrees latitude','day/year':'days/year'},num=n=>n.toLocaleString(undefined,{maximumFractionDigits:3});
  function quantity(r){
    if(r.value_conflict)return 'Unresolved source values';
    if(r.lower_bound!==null)return `${r.lower_bound_exclusive?'>':'≥'} ${num(r.lower_bound)} ${units[r.unit]||r.unit}`;
    if(r.upper_bound!==undefined&&r.upper_bound!==null)return `${r.upper_bound_exclusive?'<':'≤'} ${num(r.upper_bound)} ${units[r.unit]||r.unit}`;
    if(r.range_value)return `${r.range_value.map(num).join('–')} ${units[r.unit]||r.unit} · ${r.source_plot_estimate?'graph estimate':r.source_map_estimate?'map estimate':'source range'}`;
    if(r.value===null)return 'Value unresolved';
    const elapsed=['source_track_elapsed_span','coherent_core_analysis_interval','source_dated_event_stage_interval'].includes(r.metric);
    return `${elapsed?'':'≈ '}${num(r.value)}${r.standard_deviation!==null?' ± '+num(r.standard_deviation)+' SD':''} ${units[r.unit]||r.unit}`;
  }
  function link(label,url,parent){const a=add('a',label,parent);a.href=url;return a;}
  function showRecord(r,parent){
    const box=add('section',undefined,parent);box.className='eddy-record';box.dataset.evidenceId=r.id;
    add('h3',quantity(r),box).className=r.value_conflict?'eddy-value eddy-conflict':'eddy-value';
    add('p',r.metric_label,box);
    if(r.component_label)add('strong','Source component: '+r.component_label+' · no post-merger radius inferred.',box);
    if(r.case_label)add('strong','Source case: '+r.case_label,box);
    if(r.evidence_role==='qualified_indexed_reference')add('strong','Qualified indexed reference · full methods not independently reviewed.',add('p',undefined,box));
    if(r.source_plot_estimate){
      add('strong','Graph-read estimate · selected plotted segment, not a seasonal range.',add('p',undefined,box));
      add('p',`Reading method: ${r.source_plot_estimate.reading_allowance_km} km allowance before rounding the lower end down and upper end up to ${r.source_plot_estimate.round_outward_to_km} km. Source measurement uncertainty is unspecified.`,box);
    }
    if(r.source_map_estimate){
      const m=r.source_map_estimate,c=m.case;
      add('strong','Map-read span estimate · one published snapshot, not eddy diameter.',add('p',undefined,box));
      add('p',`Reading method: ${m.component.replaceAll('_','–')} bounding span on a ${c.earth_radius_km} km radius sphere; ${c.reading_allowance_pixels} pixels at each extent, rounded outward to ${c.round_outward_km} km. This is graph-reading allowance, not instrument uncertainty.`,box);
      add('p',`Selected outline: ${c.source_name}, ${c.date}, Figure ${c.figure}, ${c.panel}. ${c.boundary_description}`,box);
      if(c.method==='retained_contour_audit_span_v1')add('p',`Sensitivity: four accepted stroke/threshold paths, ${m.calculation.accepted_scenarios} axis scenarios with ±${c.axis_sensitivity_pixels} pixel anchor shifts, plus the reading allowance above. Two non-simple paths stay excluded. These are editorial contour spans; physical ring attribution remains pending.`,box);
      if(c.method==='source_palette_level_patch_v1')add('p',`Colour patch: plotted level ${c.source_level}; source legend unit unspecified. OSW selection sensitivity uses plot levels ${m.calculation.plot_level_sensitivity.join(', ')}, with source-palette matching. No level in centimetres or metres is assigned. This patch is not the authors’ ring-edge definition or a full-ring boundary.`,box);
    }
    if(r.independent_named_case)add('strong','Independent named source case · no primary values inherited; physical crosswalk remains unverified.',add('p',undefined,box));
    if(r.evidence_role?.includes('model_case_reference'))add('strong','Published model case · simulated quantity; not an observed regional constant.',add('p',undefined,box));
    if(r.evidence_role==='qualified_indexed_model_case_reference')add('strong','Qualified indexed model reference · original PDF not retrieved in this pass.',add('p',undefined,box));
    if(r.detection_context){
      const c=r.detection_context;
      add('p','Detection method: '+c.area_operator,box);
      add('p',`Input: ${c.product}, ${c.spatial_grid_degrees.join('° × ')}° grid, every ${c.cadence_days} days. Regional weekly mean removed: ${c.regional_weekly_mean_removed}.`,box);
      add('p','Track convention: '+c.source_case_label+'. Physical name crosswalk unverified.',box);
    }
    for(const [label,value] of [['Definition',r.definition],['Scope',r.scope],['Period',r.period_label||(r.period_start?`${r.period_start} to ${r.period_end}`:null)],['Qualification',r.qualification]])if(value)add('p',`${label}: ${value}`,box);
    if(r.sample_count!==null)add('p',`Table sample count: ${r.sample_count}. Standard deviation describes population spread; measurement uncertainty is unspecified.`,box);
    if(r.right_censored)add('strong','Track still present at the final study snapshot; disappearance date unknown.',box);
    if(r.period_precision)add('p','Date precision: '+r.period_precision.replaceAll('_',' '),box);
    if(r.source_access)add('p','Source access: '+r.source_access,box);
    if(r.range_kind)add('p','Range meaning: '+r.range_kind.replaceAll('_',' ')+'. No representative midpoint inferred.',box);
    if(r.calculation)add('p',`Model calculation: ${r.calculation.multiplier} × ${r.calculation.deformation_radius_km} km = ${num(r.calculation.unrounded_km)} km, rounded to ${num(r.value)} km.`,box);
    if(r.calendar_support){
      const c=r.calendar_support;
      add('p',`Calendar support: start ${c.start_date_min} to ${c.start_date_max} (${c.start_precision}); end ${c.end_date_min} to ${c.end_date_max} (${c.end_precision}).`,box);
      if(c.chronology_conditioned)add('strong','Chronology-conditioned range: the source month overlaps dates before separation. Zero is an allowed calendar-day difference, not missing data or a measured zero lifespan.',box);
    }
    for(const claim of r.source_claims)add('p',`Separate source claim: ${num(claim.value_km)} km · ${claim.reported_period} · ${claim.source_locator}`,box);
    if(r.date_conflict)add('strong','Source year conflict unresolved; no normalized observation month assigned.',box);
    add('p',r.source_locator,box);link('Original source',r.source_url,box);link('Retained source record','../'+r.source_file,box);
    add('span','Source location: '+r.source_pointer,box).className='eddy-note';
  }
  try{
    const response=await fetch('../research/eddy-measurement-register-v1.json');if(!response.ok)throw Error('Eddy register unavailable');const data=await response.json();
    if(data.schema!=='osw.eddy-measurement-register.v1'||data.records.length!==136||new Set(data.records.map(r=>r.entity_id)).size!==136)throw Error('Incomplete eddy identity inventory');
    const byId=new Map(data.evidence.map(r=>[r.id,r])),classById=new Map(data.size_classifications.map(r=>[r.id,r])),c=data.counts;
    $('eddy-summary').textContent=`${c.identities} source identities · ${c.evidence_records} evidence records across ${c.identities_with_measurements} entries · ${c.identities_without_measurements} entries still without numeric measurements`;
    const requested=new URLSearchParams(location.search).get('id');
    const requestedRow=data.records.find(r=>r.entity_id===requested);if(requestedRow)$('eddy-search').value=requestedRow.name;
    function render(){
      const search=$('eddy-search').value.trim().toLowerCase(),identity=$('eddy-identity').value,filter=$('eddy-filter').value,category=$('eddy-category').value;
      const selected=r=>r.evidence_ids.map(id=>byId.get(id)).filter(e=>category==='all'||e.category===category);
      const rows=data.records.filter(r=>(!search||`${r.name} ${r.basin}`.toLowerCase().includes(search))&&(identity==='all'||r.identity_level===identity)&&(filter==='all'||filter==='measured'&&r.evidence_ids.length>0||filter==='gap'&&!r.evidence_ids.length||filter==='linked'&&r.linked_primary_context&&!r.evidence_ids.length||filter==='unlinked-gap'&&!r.evidence_ids.length&&!r.linked_primary_context||filter==='size-gap'&&r.size_gap||filter==='size-class'&&r.size_classification_ids.length>0||filter==='duration-gap'&&r.duration_gap)&&(category==='all'||selected(r).length)).sort((a,b)=>a.name.localeCompare(b.name)||a.entity_id.localeCompare(b.entity_id));
      $('eddy-results').textContent=`${rows.length} source ${rows.length===1?'identity':'identities'} shown · ${c.size_owners} entries have size references; ${c.duration_owners} have duration references; ${c.recurrence_owners} have regional recurrence. No pooled size or lifetime ranking.`;
      $('eddy-class-summary').textContent=`${data.size_classification_counts.owners} entries also have qualitative source size classes. Thresholds are unspecified; ${data.size_classification_counts.owners_with_numeric_size_gap} of these still need numeric sizes.`;
      $('eddy-rows').replaceChildren();
      for(const row of rows){
        const tr=add('tr',undefined,$('eddy-rows'));tr.dataset.eddyId=row.entity_id;
        const cell=label=>{const td=add('td',undefined,tr);td.dataset.label=label;return td;};
        const owner=cell('Eddy');link(row.name,row.current_card_url,owner);add('span',`${row.basin} · ${row.identity_level.replaceAll('_',' ')}`,owner).className='eddy-note';add('span',row.entity_id,owner).className='eddy-note';
        const evidence=selected(row),size=cell('Size'),time=cell('Time, movement and structure'),body=cell('Details');
        const classes=(category==='all'||category==='size')?row.size_classification_ids.map(id=>classById.get(id)):[];
        for(const entry of classes){add('strong',entry.label+' · source size class',size);add('span','Numeric thresholds unspecified',size).className='eddy-note';}
        for(const [target,items,empty] of [[size,evidence.filter(e=>e.category==='size'),'Size reference needed'],[time,evidence.filter(e=>e.category!=='size'),'Duration / movement reference needed']]){
          if(!items.length)add('span',empty,target).className='eddy-note';
          for(const r of items){add('strong',quantity(r),target);add('span',(r.component_label||r.case_label?(r.component_label||r.case_label)+' · ':'')+r.metric_label+(r.period_label?' · '+r.period_label:''),target).className='eddy-note';}
        }
        const details=add('details',undefined,body);add('summary',evidence.length?`Inspect ${evidence.length} numeric source ${evidence.length===1?'record':'records'}${classes.length?' + size class':''}`:classes.length?'Inspect source size class and identity context':'Inspect identity and date context',details);
        if(row.event_date)add('p',`Registry separation date: ${row.event_date}. This supplies no lifespan or age.`,details);
        if(row.registry_context){const c=row.registry_context;
          add('p',`Registry dissipation label: ${c.dissipation_label||'Not supplied'}.`,details);
          if(c.dissipation_label==='Active')add('strong','Undated source label; current status and age have not been established.',details);
          if(c.lc_separation_count!==null)add('p',`Registry number of LC separations: ${c.lc_separation_count}. Count method and dates unspecified.`,details);
        }
        if(row.linked_primary_context){const c=row.linked_primary_context,p=add('p',c.relation+' ',details);link('Inspect primary '+c.name,c.url,p);add('span',` · ${c.evidence_ids.length} primary source records; no values inherited by this secondary.`,p);}
        if(row.paper_window_context){const w=row.paper_window_context;add('p',`Paper window: ${w.start} to ${w.end}. ${w.interpretation}`,details);}
        if(row.identity_note)add('p',row.identity_note,details);
        if(row.possible_same_ring_as){const p=add('p','Possible name crosswalk · identity unverified: ',details);link(row.possible_same_ring_as,'eddies.html?id='+encodeURIComponent('eddy:'+row.possible_same_ring_as),p);}
        for(const r of evidence)showRecord(r,details);
        for(const entry of classes){
          const box=add('section',undefined,details);box.className='eddy-record';box.dataset.classificationId=entry.id;
          add('h3',entry.label+' · qualitative source size class',box);
          add('p',`Source row: ${entry.source_name}, ${entry.source_year}. Source year is not assumed to be separation year.`,box);
          add('p',row.entity_id.endsWith('-secondary')?`Associated primary registry row: ${entry.registry_primary_name}, separation ${entry.registry_primary_initial_separation}. This supplies no secondary separation date. Physical name crosswalk unverified.`:`Registry context: ${entry.registry_name}, separation ${entry.registry_primary_initial_separation}. Physical name crosswalk unverified.`,box);
          add('p',entry.definition,box);add('p',entry.qualification,box);add('p',entry.source_access,box);
          link('Classification source',entry.source_url,box);link('Retained classification row','../'+entry.source_file,box);
          add('span','Source location: '+entry.source_pointer,box).className='eddy-note';
        }
        if(!evidence.length)add('p',row.next_action,details);
        link('Identity source',row.source_url,details);link('Atlas context',row.atlas_url,body);
        if(row.entity_id===requested)details.open=true;
      }
    }
    $('eddy-controls').addEventListener('submit',e=>e.preventDefault());
    for(const id of ['eddy-search','eddy-identity','eddy-filter','eddy-category'])$(id).addEventListener(id==='eddy-search'?'input':'change',render);
    window.oswEddyMeasurementRegister=data;render();
  }catch(error){$('eddy-summary').textContent=error.message;}
})();
