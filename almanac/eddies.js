"use strict";
(async()=>{
  const $=id=>document.getElementById(id),add=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;};
  const units={'kJ/cm2':'kJ/cm²',km:'km',km2:'km²',day:'days',year:'years',month:'months',week:'weeks',percent:'%',degree_latitude:'degrees latitude','day/year':'days/year'},num=n=>n.toLocaleString(undefined,{maximumFractionDigits:3});
  function quantity(r){
    if(r.value_conflict)return 'Unresolved source values';
    if(r.lower_bound!==null)return `${r.lower_bound_exclusive?'>':'≥'} ${num(r.lower_bound)} ${units[r.unit]||r.unit}`;
    if(r.upper_bound!==undefined&&r.upper_bound!==null)return `${r.upper_bound_exclusive?'<':'≤'} ${num(r.upper_bound)} ${units[r.unit]||r.unit}`;
    if(r.range_value)return `${r.range_value.map(num).join('–')} ${units[r.unit]||r.unit} · ${r.source_plot_estimate?'graph estimate':r.source_map_estimate?.case.method==='source_visible_model_front_meridional_span_v1'?'visible model-front estimate':r.source_map_estimate?.case.method==='source_image_scale_bar_equivalent_spans_v1'?'chart-scale equivalent':r.source_map_estimate?'map estimate':r.calculation?.method==='spherical_sampled_station_separation_v1'?'coordinate estimate':'source range'}`;
    if(r.value===null)return 'Value unresolved';
    const elapsed=['source_track_elapsed_span','coherent_core_analysis_interval','source_dated_event_stage_interval'].includes(r.metric);
    return `${elapsed?'':'≈ '}${num(r.value)}${r.standard_deviation!==null?' ± '+num(r.standard_deviation)+' SD':''} ${units[r.unit]||r.unit}`;
  }
  function link(label,url,parent){const a=add('a',label,parent);a.href=url;return a;}
  function showRecord(r,parent){
    const box=add('section',undefined,parent);box.className='eddy-record';box.dataset.evidenceId=r.id;
    add('h3',quantity(r),box).className=r.value_conflict?'eddy-value eddy-conflict':'eddy-value';
    add('p',r.metric_label,box);
    if(r.component_label)add('strong','Source component: '+r.component_label+(r.component_label==='Northern post-split Quantum I source case'?' · no pre-split parent or Quantum II values inferred.':' · no post-merger radius inferred.'),add('p',undefined,box));
    if(r.case_label)add('strong','Source case: '+r.case_label,box);
    if(r.evidence_role==='qualified_indexed_reference')add('strong','Qualified indexed reference · full methods not independently reviewed.',add('p',undefined,box));
    if(r.case_alias_association){
      const a=r.case_alias_association;
      add('strong',`Published alias: ${a.published_alias} / ${a.source_label} · registry physical crosswalk unverified.`,add('p',undefined,box));
      add('p',`Registry initial separation: ${a.registry_initial_separation}; report context: ${a.report_separation_context}. Separation conventions remain unreconciled.`,box);
      if(a.method==='source_reported_1988_letter_case_reference'){
        add('strong',r.metric==='source_reported_sampled_drifter_axes_length_extrema'?'Sampled drifter-axis change · not a seasonal size range.':r.metric.includes('sampled_drifter_ellipse')?'Sampled ellipse dimension · the drifter need not follow the eddy front.':r.metric==='source_reported_baroclinic_radius_of_influence'?'Baroclinic radius of influence · 8°C temperature-surface diagnostic.':'Source-reported diameter · boundary and observation date unspecified.',add('p',undefined,box));
      }
    }
    if(r.profile_context){
      add('strong',(r.profile_context.method==='source_reported_multisensor_current_comparison'?'Multi-instrument current comparison':r.profile_context.method==='source_reported_operational_adcp_maximum'?'Operational ADCP current diagnostic':r.profile_context.method==='source_reported_mooring_current_diagnostic'?'Fixed-mooring current diagnostic':r.profile_context.method==='source_reported_airborne_temperature_diagnostic'?'Airborne temperature diagnostic':'Glider profile diagnostic')+' · sampling support is not whole-eddy depth.',add('p',undefined,box));
      const c=r.profile_context;
      if(c.method==='source_reported_multisensor_current_comparison'){
        add('p',`Instrument: ${c.instrument}; ${c.sample_depth_m===null?'effective near-surface weighting, no single assigned depth':`sample depth: ${c.sample_depth_m} m`}.`,box);
        add('p',c.shared_source_approximation?'The authors give one approximate speed for both remote instruments; this is not an arithmetic average or two independently resolved values.':'Approximate local buoy comparison value, not a mean or maximum.',box);
        add('p','Measurement times can differ by about an hour. No simultaneous vertical section or quantitative shear is calculated.',box);
      }
      if(c.method==='source_reported_operational_adcp_maximum')add('p','Provider-reported local maximum. Sample depth, exact dates and averaging interval unspecified; raw profiles unavailable. This does not establish the whole-eddy maximum.',box);
      if(c.method==='source_reported_mooring_current_diagnostic'){
        add('p',`${c.station} · instrument depth: ${c.instrument_depth_m} m · source direction: ${c.direction_as_reported}.`,box);
        add('p','Native cm/s site speeds; mean versus maximum is unspecified. Exact sample dates and raw time series unavailable; these readings do not establish a simultaneous vertical section, whole-eddy maximum or thickness.',box);
        if(c.source_small_anticyclone_coalescence_context)add('p','Kathleen coalesced with a smaller anticyclone; retain the post-coalescence context.',box);
      }
      if(c.vertical_averaging_interval_m)add('p',`Depth averaging: ${c.vertical_averaging_interval_m.join('–')} m; averaging axis: depth.`,box);
      if(c.thermal_reference_celsius!==undefined)add('p',`Thermal reference: ${c.thermal_reference_celsius}°C isotherm.`,box);
      if(c.related_circuit_window)add('p',`Related circuit: ${c.related_circuit_window.join(' to ')}; context only, not exact sample dates.`,box);
    }
    if(r.source_plot_estimate?.method==='source_height_profile_readings_v1'){
      const m=r.source_plot_estimate;
      add('strong','Satellite height-profile diagnostic · not whole-eddy dimensions.',add('p',undefined,box));
      add('p',m.component==='meridional_span'?'Selected bracketing crossings: OSW-chosen 0.30 m level; sensitivity 0.25 and 0.35 m. Meridional projection, not diameter or along-track distance. Local recrossings are not filled.':'Selected main-lobe peak dynamic topography, relative to the source mean-height reference; not eddy depth.',box);
      add('p',`Reading method: six-pixel allowance and ±2-pixel anchor shifts; ${m.calculation.total_scenarios} sensitivity cases. Rounded outward; these are reading/choice margins, not physical uncertainty or a confidence interval.`,box);
      add('p','Altimeter trace only, 20 June 1988. AXBT comparison was several days apart and is excluded; schematic inset is not an eddy boundary.',box);
    }else if(r.source_plot_estimate){
      add('strong','Graph-read estimate · selected plotted segment, not a seasonal range.',add('p',undefined,box));
      add('p',`Reading method: ${r.source_plot_estimate.reading_allowance_km} km allowance before rounding the lower end down and upper end up to ${r.source_plot_estimate.round_outward_to_km} km. Source measurement uncertainty is unspecified.`,box);
    }
    if(r.source_map_estimate){
      const m=r.source_map_estimate,c=m.case;
      if(c.method==='source_visible_model_front_meridional_span_v1'){
        add('strong','Visible model-inferred front · eastern side clipped.',add('p',undefined,box));
        add('p','Only the visible north–south plotted extent is measured. This does not establish the full front, observed eddy boundary, diameter or east–west width.',box);
        add('p',`Source date: ${c.date}; northern post-split Quantum I. Reading method: ${c.reading_allowance_pixels} pixels at each selected extremum, ±${c.axis_sensitivity_pixels} pixel latitude-anchor shifts, two ink gates and ${m.calculation.total_scenarios} sensitivity cases; rounded outward to ${c.round_outward_km} km. Model/front error is unspecified.`,box);
      }else if(c.method==='source_image_scale_bar_equivalent_spans_v1'){
        add('strong','Chart-scale equivalent · projection and contour threshold unspecified.',add('p',undefined,box));
        add('p',`Selected line: ${c.source_name}, ${c.date}; black date-legend entry. ${m.component} span at the displayed ${c.scale_bar_km} km scale bar, not a calibrated geodesic distance or eddy diameter.`,box);
        add('p',`Reading method: ${c.reading_allowance_pixels} pixels at each extent, ±${c.axis_sensitivity_pixels} pixel scale-anchor shifts and two ink gates; ${m.calculation.total_scenarios} sensitivity cases, rounded outward to ${c.round_outward_km} km. Geographic scale variation at the eddy remains unquantified.`,box);
      }else if(c.method==='source_native_pdf_frontal_line_spans_v1'){
        add('strong','Native PDF line span · contour observation date unspecified.',add('p',undefined,box));
        add('p',`Source legend: ${c.source_legend_speed_knots}-knot frontal-analysis contour. SSH background: ${c.background_ssh_date}; this does not date the frontal line.`,box);
        add('p',`Original native path: ${c.native_path.segments.toLocaleString()} continuous line segments, explicit endpoint closure, no reconstructed gaps. ${c.poster_overlay_qualification}`,box);
        add('p',`Reading method: ${m.component.replaceAll('_','–')} bounding arc on a ${c.earth_radius_km} km sphere; ${c.reading_allowance_pdf_points} PDF points at each extent (six 72 dpi pixels), rounded outward to ${c.round_outward_km} km. ${c.axis_method}`,box);
      }else{
        add('strong','Map-read span estimate · one published snapshot, not eddy diameter.',add('p',undefined,box));
        add('p',`Reading method: ${m.component.replaceAll('_','–')} bounding span on a ${c.earth_radius_km} km radius sphere; ${c.reading_allowance_pixels} pixels at each extent, rounded outward to ${c.round_outward_km} km. This is graph-reading allowance, not instrument uncertainty.`,box);
        add('p',`Selected outline: ${c.source_name}, ${c.date}, Figure ${c.figure}, ${c.panel}. ${c.boundary_description}`,box);
      }
      if(c.method==='retained_contour_audit_span_v1')add('p',`Sensitivity: four accepted stroke/threshold paths, ${m.calculation.accepted_scenarios} axis scenarios with ±${c.axis_sensitivity_pixels} pixel anchor shifts, plus the reading allowance above. Two non-simple paths stay excluded. These are editorial contour spans; physical ring attribution remains pending.`,box);
      if(c.method==='source_palette_level_patch_v1')add('p',`Colour patch: plotted level ${c.source_level}; source legend unit unspecified. OSW selection sensitivity uses plot levels ${m.calculation.plot_level_sensitivity.join(', ')}, with source-palette matching. No level in centimetres or metres is assigned. This patch is not the authors’ ring-edge definition or a full-ring boundary.`,box);
      if(c.method==='manual_ink_arrow_span_v1')add('p','Visible circulation-arrow extents · four manual source-ink readings. Closed-outline extraction rejected; no missing segment repaired and no footprint inferred. Source chart carries CONFIDENTIAL stamp and copyright despite public conference hosting. Research candidate only; excluded from rights-screened release.',box);
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
    if(r.calculation?.method==='spherical_sampled_station_separation_v1'){
      const c=r.calculation;
      add('strong','Sampled station separation · not whole-eddy radius or diameter.',add('p',undefined,box));
      add('p',`Station ${c.center_station.id} (sampled center): ${c.center_station.latitude}°, ${c.center_station.longitude}°. Station ${c.edge_station.id} (sampled edge): ${c.edge_station.latitude}°, ${c.edge_station.longitude}°. Coordinates are latitude, longitude.`,box);
      add('p',`Nominal coordinate separation: ${num(c.unrounded_nominal_km)} km on a ${num(c.earth_radius_km)} km sphere. OSW assumes ±${c.coordinate_allowance_degrees}° per coordinate; sensitivity allowance ${num(c.triangle_inequality_allowance_km)} km, rounded outward to ${c.round_outward_km} km. Source accuracy and simultaneity unverified.`,box);
    }else if(r.calculation)add('p',`Model calculation: ${r.calculation.multiplier} × ${r.calculation.deformation_radius_km} km = ${num(r.calculation.unrounded_km)} km, rounded to ${num(r.value)} km.`,box);
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
