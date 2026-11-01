"use strict";
(async()=>{
  const $=id=>document.getElementById(id),add=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;};
  const units={'kJ/cm2':'kJ/cm²',km:'km',km2:'km²',day:'days',year:'years',month:'months',week:'weeks',percent:'%',degree_latitude:'degrees latitude','day/year':'days/year'},num=n=>n.toLocaleString(undefined,{maximumFractionDigits:3});
  function quantity(r){
    if(r.value_conflict)return 'Unresolved source values';
    if(r.lower_bound!==null)return `${r.lower_bound_exclusive?'>':'≥'} ${num(r.lower_bound)} ${units[r.unit]||r.unit}`;
    if(r.upper_bound!==undefined&&r.upper_bound!==null)return `${r.upper_bound_exclusive?'<':'≤'} ${num(r.upper_bound)} ${units[r.unit]||r.unit}`;
    if(r.calendar_support?.method==='source_narrative_nautilus_ii_calendar_span')return `${r.range_value.map(num).join('–')} days · calendar bounds`;
    if(r.range_value)return `${r.range_value.map(num).join('–')} ${units[r.unit]||r.unit} · ${r.source_plot_estimate?'graph estimate':r.source_map_estimate?.case.method==='source_operational_chart_visible_line_spans_v1'?'operational chart estimate':r.source_map_estimate?.case.method==='source_visible_model_front_meridional_span_v1'?'visible model-front estimate':r.source_map_estimate?.case.method==='source_image_scale_bar_equivalent_spans_v1'?'chart-scale equivalent':r.source_map_estimate?'map estimate':r.calculation?.method==='spherical_sampled_station_separation_v1'?'coordinate estimate':r.calculation?.method==='source_public_cardone_circulation_arrow_spans_v1'?'circulation arrow estimate':r.calculation?.method==='source_named_nelson_frontal_chart_spans_v1'?'frontal chart estimate':r.calculation?.method==='source_hot_core_pre_detachment_frontal_lobe_spans_v1'?'frontal-lobe estimate':r.calculation?.method==='osw_speed_contour_named_source_case_v1'?'speed-core estimate':r.calculation?.method==='gridded_adt_named_source_case_v1'?'gridded contour estimate':'source range'}`;
    if(r.value===null)return 'Value unresolved';
    if(r.metric==='source_model_counterfactual_shedding_date_difference')return `${num(r.value)} ${r.value===1?'day':'days'}`;
    const elapsed=['source_track_elapsed_span','coherent_core_analysis_interval','source_dated_event_stage_interval','source_model_counterfactual_shedding_date_difference'].includes(r.metric);
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
    if(r.profile_context?.method==='source_reported_laura_survey_ssh_anomaly'){
      add('strong','Laura sea-surface-height anomaly · not eddy depth.',add('p',undefined,box));
      add('p','Source reports about +40 cm maximum SSH anomaly at the time of MARE-1, March 2000. Exact altimeter acquisition/composite time and anomaly reference unspecified.',box);
      add('p','Hydrographic and SSH centers differ; Laura was not surveyed completely. This is not a full-life or annual maximum, vertical thickness, contour threshold or physical footprint.',box);
    }else if(r.profile_context){
      add('strong',(r.profile_context.method==='source_reported_nelson_1989_local_current_phases'?'Nelson local current phase':r.profile_context.method==='source_reported_quiet_sst_ellipse_axes'?'Source-reported SST ellipse axis':r.profile_context.method==='source_reported_k_2000_mooring_current'?'Interaction-site mooring current':r.profile_context.method==='source_reported_assimilative_analysis_parent_extent'?'Assimilative model-analysis extent':r.profile_context.method==='source_reported_yazoo_2022_case'?'Source-named Yazoo reference':r.profile_context.method==='source_reported_thermal_level_enclosed_area'?'Thermal-level enclosed area':r.profile_context.method==='source_reported_multisensor_current_comparison'?'Multi-instrument current comparison':r.profile_context.method==='source_reported_operational_adcp_maximum'?'Operational ADCP current diagnostic':r.profile_context.method==='source_reported_mooring_current_diagnostic'?'Fixed-mooring current diagnostic':r.profile_context.method==='source_reported_airborne_temperature_diagnostic'?'Airborne temperature diagnostic':'Glider profile diagnostic')+(r.profile_context.method==='source_reported_quiet_sst_ellipse_axes'?' · approximate surface expression.':' · sampling support is not whole-eddy depth.'),add('p',undefined,box));
      const c=r.profile_context;
      if(c.method==='source_reported_nelson_1989_local_current_phases'){
        add('strong',c.sample_depth_m===45?'Instrument depth: 45 m.':'Exact sampling depth unspecified.',add('p',undefined,box));
        add('p',c.support,box);
        if(c.bathymetry_contours_m)add('strong','500–1,000 m are seabed contours, not sampling depth or eddy thickness.',add('p',undefined,box));
        if(c.key==='post-severe-45m-bound')add('strong','Below 0.4 knots at most sampled sites in this phase; not an eddy-wide speed limit.',add('p',undefined,box));
        add('p','Separate local phases and sites: these values do not form a seasonal range, whole-eddy maximum or simultaneous vertical profile. No shear inferred.',box);
        add('p','Nelson 1989 source case; registry physical crosswalk unverified. Unknown sample depths are not filled from the 45 m observations.',box);
      }

      if(c.method==='source_reported_quiet_sst_ellipse_axes'){
        add('strong',c.axis==='major'?'Nearly 400 km · north-oriented major axis.':'About 250–300 km · east–west minor axis.',add('p',undefined,box));
        add('p','Quiet Eddy in NOAA-11 AVHRR imagery dated 12 and 19 August 1990. No separate axis pair supplied for each image; these dates do not establish continuous observations.',box);
        add('p','Source-described SST ellipse, with drifter context and about 0.5°C edge contrast. No mathematical ellipse fit or fixed outer-boundary operator verified.',box);
        add('p','Nearly is approximate source wording, not a strict upper bound. No ellipse area, diameter, seasonal range or physical footprint derived; registry physical crosswalk unverified.',box);
      }

      if(c.method==='source_reported_k_2000_mooring_current'){
        add('strong',c.sample_depth_m===null?'Near-surface reached value · exact depth unspecified.':'Local sampled maximum at 755 m · not whole-eddy maximum.',add('p',undefined,box));
        add('p','First two weeks of November 2000 at the LSU Sigsbee mooring, between WCE K and a cyclone. The 3 November map is context, not the exact current sample time.',box);
        add('p','The earlier field report explicitly names Kinetic / Eddy K. The cross-report event association and registry physical crosswalk remain unverified.',box);
        add('p','Interaction-site currents, not isolated eddy swirl. No simultaneous vertical profile, shear, eddy thickness or seasonal range inferred.',box);
      }

      if(c.method==='source_reported_assimilative_analysis_parent_extent'){
        add('strong','Approximate parent zonal extent · model analysis, not directly observed length.',add('p',undefined,box));
        add('p','Thor before near-splitting · analysis dated 24 February 2020. Weekly ensemble-mean verifying analysis from NCOM / NCODA / COAMPS, with 3 km model resolution and 32 members.',box);
        add('p','The source calls analysis truth for forecast verification. It remains an assimilative model product; this scalar is not a forecast-member result, principal width or diameter.',box);
        add('p','Boundary threshold and uncertainty for this scalar are unspecified. No values transferred to the March anticyclones or registry Thor; no annual envelope or physical footprint inferred.',box);
      }

      if(c.method==='source_reported_yazoo_2022_case'){
        add('strong',c.quantity==='radius'?'Approximate high-ADT-patch radius · not diameter.':'Eastern-flank cruise current · depth and statistic unspecified.',add('p',undefined,box));
        add('p',c.quantity==='radius'?'Source map averaged 7–17 November 2022; not a daily footprint. No area or principal width derived.':'WHOI cruise 1–5 October 2022; exact current sample times and mean/maximum definition unspecified. Nearby plotted depth averages are not assigned to this prose value.',box);
        add('p','Explicit source name: Yazoo. Registry initial separation: 2022-06-20; physical crosswalk unverified. No Yazoo II values inherited.',box);
        add('p','October current and November radius are separate observations; no simultaneous profile or annual range inferred.',box);
      }

      if(c.method==='source_reported_thermal_level_enclosed_area'){
        add('p',`Survey label: ${c.survey_label}; area within the ${c.temperature_surface_depth_contour_m} m depth contour of the 8°C temperature surface.`,box);
        add('p',`Source table: ${c.source_table_value} × 1,000 km². Planimeter measurement on hand-contoured hydrographic maps; uncertainty unspecified.`,box);
        add('strong','Thermal contour depth, not sampling depth or eddy thickness. This area is not the full outer boundary.',add('p',undefined,box));
        add('p','Survey labels can span month boundaries. Zero and unclosed table cells are not filled or interpolated; different levels do not form an annual size range.',box);
      }

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
      if(c.source_attribution?.method==='dated_2021_figure9_with_unresolved_duplicate_caption'){
        add('strong','Provisional Wilde illustration · duplicated caption unresolved.',add('p',undefined,box));
        add('p','Figure 9 names 2021 Wilde and the selected panel is dated 10-Nov-2021. The identical raster also appears under the Figure 10 Wilde II caption. This source defect remains unresolved.',box);
        add('p','These chart spans describe one provisional Figure 9 reading. Independent 2021 provider context does not authenticate the image. Pixel-reading margins do not cover attribution uncertainty.',box);
        add('p','No Wilde II measurement, later 2022-panel value or independent duplicate confirmation. Physical identity and boundary remain unverified; these are not seasonal width ranges.',box);
      }


      if(c.method==='source_cartographic_extent_circle_spans_v1'){
        add('strong','Laura cartographic extent-circle span · author illustration.',add('p',undefined,box));
        add('p','Figure 3 identifies Laura by the dashed track and Mar 00 marker. The caption says the circles indicate ring extension; the boundary operator and physical accuracy are unspecified.',box);
        add('p',`${m.component==='east_west'?'East–west parallel arc at illustrated-circle midlatitude':'North–south meridional arc'} on a 6371 km sphere. The drawn circle is not assumed geodesically circular; no physical diameter, principal width, radius, fitted circle or area inferred.`,box);
        add('p',`Reading margins: four native ink windows, two grayscale gates, ±2 pixel shifts of eight axis anchors and six-pixel extent allowance; ${m.calculation.total_scenarios} scenarios, rounded outward to 25 km. These margins describe image reading, not physical uncertainty or seasonal variation.`,box);
        add('p','March 2000 context only; exact survey instant unknown. The source warns that hydrographic and SSH centers differ and Laura was not surveyed completely. No synchronized boundary, footprint, state containment, ranking or animation inferred.',box);
      }else if(c.method==='source_author_animation_ssh_patch_v1'){
        add('strong','Qualified Atwater image-patch estimate · not whole-eddy dimensions.',add('p',undefined,box));
        add('p','Original author animation, 30 July 2023, first of four frames. The image has no Atwater label; the primary preprint names Atwater southwest of the transect. Candidate association and registry physical crosswalk remain unverified.',box);
        add('p','OSW-chosen 0.75 m level on the literal SSH (m) legend; 0.70/0.80 m selection sensitivity. Field datum and exact HYCOM product/export unverified: no absolute ADT or anomaly conversion.',box);
        add('p',`${m.component==='east_west'?'East–west parallel arc at bounding midlatitude':'North–south meridional arc'}; ${m.calculation.total_scenarios} scenarios across level choice, degree/Mercator latitude interpolation, ±2 pixel grid anchors and six-pixel extent allowance. Rounded outward to 25 km.`,box);
        add('p','Largest connected matching colour patch; no hole filling or gap repair. Image-reading sensitivity only, not physical uncertainty or a seasonal range. No diameter, principal width, area, footprint, ranking or state containment inferred.',box);
        add('p','2026 primary preprint, not peer-reviewed. Original paper PDF unavailable; original author GIF pixels verified at a pinned repository commit. Related code does not reproduce this exact export.',box);
      }else if(c.method==='source_bold_ssh_isoline_spans_v1'){
        add('strong','Source 17 cm SSH isoline span · not principal width or diameter.',add('p',undefined,box));
        add('p',`Zodiac · published map label ${c.date}. Bold closed line supplied by Robert Leben / CCAR; source SSH reference and exact composite/acquisition times unspecified.`,box);
        add('p',`${m.component==='east_west'?'East–west parallel arc at the bounding mid-latitude':'North–south meridional arc'} on a ${c.earth_radius_km} km sphere. This is not an SST warm-patch size or the OSW gridded contour operator.`,box);
        add('p',`Reading margins: ${c.reading_allowance_pixels} native pixels at each extent, ±${c.axis_sensitivity_pixels} pixel shifts of six labeled grid anchors, two neutral-ink gates and ${m.calculation.total_scenarios} scenarios. Rounded outward to ${c.round_outward_km} km; source uncertainty and seasonal extremes remain unquantified.`,box);
        add('p','Closed source ink verified without gap repair. No physical footprint, area or state containment inferred. Source detachment around 2022-12-28 and registry 2022-12-27 remain unreconciled; physical crosswalk unverified.',box);
        if(c.date==='2023-01-13')add('p','The source prose has a year typo; the linked original filename and map header both label 13 January 2023.',box);
      }else if(c.method==='source_operational_chart_visible_line_spans_v1'){

        add('strong','Visible operational frontal-line span · low-resolution chart.',add('p',undefined,box));
        add('p',`Printed map date: ${c.date}; ${c.source_name}. Native panel: 303 × 240 pixels. Selected visible segments only; no missing ink or closed boundary reconstructed.`,box);
        add('p',`Reading method: two neutral-ink gates, six-pixel extent allowance, ±2 pixel axis anchors and ${m.calculation.total_scenarios} sensitivity cases; rounded outward to 25 km. This is reading sensitivity, not measured uncertainty or a seasonal range.`,box);
        add('p','Chart threshold and physical-front error are unspecified. No area, diameter, principal axes or physical footprint inferred; the separate gridded comparison did not qualify.',box);
        if(c.source_name==='Hadal')add('p','The caption says shed by 30 July; this panel is dated 1 August 2011. These dates remain separate. Hadal II inherits no values.',box);
      }else if(c.method==='source_visible_model_front_meridional_span_v1'){
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
    if(r.calendar_support?.method==='source_narrative_nautilus_ii_calendar_span'){
      add('strong','Nautilus II source calendar span · not a measured lifespan.',add('p',undefined,box));
      add('p','The 2024 UABC thesis explicitly names Nautilus II: formation in May 2015 and dissipation between December 2015 and January 2016. It also describes repeated reconnections to Nautilus.',box);
      add('p','184–275 days covers month precision only. The lower end uses 31 May to 1 December; the upper end uses 1 May to 31 January. These are support boundaries, not observed event dates. No midpoint or 30-day-month conversion.',box);
      add('p','Figure 6 groups Nautilus/Nautilus II. Exact split history, continuous identity across reconnections and the registry physical association remain unverified. No individual child width or contour is established.',box);
      add('p','Own source narrative only: primary Nautilus registry separation on 2015-05-01 and dissipation in November 2015 are not inputs. No parent size/current values inherited; size gap retained.',box);
    }
    if(r.independent_named_case)add('strong','Independent named source case · no primary values inherited; physical crosswalk remains unverified.',add('p',undefined,box));
    if(r.evidence_role?.includes('model_case_reference')&&r.model_context?.method!=='source_reported_model_event_date_contrast')add('strong','Published model case · simulated quantity; not an observed regional constant.',add('p',undefined,box));
    if(r.model_context?.method==='source_reported_model_event_date_contrast'){
      const c=r.model_context;
      add('strong','Preprint model event-date contrast · not eddy lifetime.',add('p',undefined,box));
      add('p',`Control: ${c.control_event_date}; ${c.experiment}: ${c.counterfactual_event_date}. Counterfactual minus Control = ${c.calendar_day_difference} calendar ${c.calendar_day_difference===1?'day':'days'}. Removed forcing: ${c.removed_hurricanes}.`,box);
      add('p','Different simulated worlds, not observations of an eddy aging. The three contrasts are not additive and do not form an uncertainty range.',box);
      add('p','June 2026 preprint, not peer-reviewed. Indexed primary text only; original PDF, figure pixels and raw fields were not independently verified. Size and observed causal effect remain unestablished.',box);
    }
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
    }else if(r.calculation?.method==='gridded_adt_named_source_case_v1'){
      const c=r.calculation;
      add('strong','OSW gridded contour estimate · method sensitivity only.',add('p',undefined,box));
      add('p','Six scenarios: 0.15 / 0.17 / 0.19 m contours, with arithmetic and cosine-latitude Gulf demeaning. Nine primary-map interior probes uniquely select one candidate in each scenario.',box);
      add('p',`Native scenario extrema: ${c.unrounded_extrema.map(num).join('–')} ${units[r.unit]||r.unit}; outward rounding to ${c.round_outward_to} ${units[r.unit]||r.unit}. Mapping and physical-front errors remain unquantified.`,box);
      add('p','First March detachment; later reattachments and August departure remain separate. Registry initial separation: 2013-04-08. Registry physical crosswalk unverified; no other Kraken values inherited.',box);
      link('Primary dated Kraken map','https://www2.whoi.edu/site/bower-lab/wp-content/uploads/sites/12/2019/09/Hamilton_etal_LoopCurrentObs_2019_JPOx.pdf',box);
    }else if(r.calculation?.method==='source_public_cardone_circulation_arrow_spans_v1'){
      const c=r.calculation;
      add('strong','Cardone provider circulation arrows · physical boundary unverified.',add('p',undefined,box));
      add('p','The original Woods Hole Group / EddyWatch chart explicitly labels Cardone. Four isolated black-ink extrema define the plotted arrow spans. The coloured drifter tracks and speed legend do not define a threshold for the black arrows.',box);
      add('p','Observation date unspecified. The chart was reproduced in an article published 27 May 2024. That publication date and the screenshot filename are not sampling dates; no dated geometry or seasonal position is assigned.',box);
      add('p',`Reading sensitivity: ${c.reading_allowance_native_pixels} native pixels per extremum; ±${c.axis_allowance_native_pixels} pixels on six grid anchors across ${c.axis_shift_scenarios} scenarios; outward ${c.round_outward_km} km reporting. Physical extent, projection distortion and field/product uncertainty remain unquantified.`,box);
      add('p','Both closed-ink tests rejected the arrow loop. No gaps are repaired. These are illustration spans, not diameter, principal width, radius, area, a physical footprint or a verified closed eddy boundary.',box);
    }else if(r.calculation?.method==='source_named_nelson_frontal_chart_spans_v1'){
      const c=r.calculation;
      add('strong','Nelson historical frontal analysis · full physical boundary unverified.',add('p',undefined,box));
      add('p','The original chart explicitly labels Nelson Eddy. These manual bounding spans use the visible outer frontal-analysis envelope, including its original dashed western segment. Inner drifter tracks and the separate Loop Current front are excluded; no gaps are repaired and closed topology is not asserted.',box);
      add('p',`Chart-data week: ${c.source_week.join(' to ')}. Table 5.2-2 supplies this week; the report uses 1 September 1989 for separation. Registry initial separation remains 24 February 1989. The dates and definitions remain distinct.`,box);
      add('p',`Reading allowance: ${c.reading_allowance_native_pixels} original raster pixels at each extremum, rounded outward to ${c.round_outward_km} km. The interval is reading sensitivity only. Front interpretation, scan/axis distortion and physical uncertainty remain unquantified.`,box);
      add('p','These chart extents are not diameter, radius, area or principal width. Existing local ADCP current phases are separate evidence. No full physical boundary, footprint, state containment, ranking or seasonal cycle inferred.',box);
    }else if(r.calculation?.method==='source_hot_core_pre_detachment_frontal_lobe_spans_v1'){
      const c=r.calculation;
      add('strong','Hot Core pre-detachment frontal lobe · not a closed eddy boundary.',add('p',undefined,box));
      add('p','The original EddyWatch chart explicitly names Hot Core. Its western, northern and southern frontal extrema and the eastern lobe-neck junction define these manual landmark spans. Loop Current continuation is excluded; no missing line is reconstructed.',box);
      add('p',`Source chart week: ${c.source_week.join(' to ')}. The report uses 18 January 1986 for separation; the registry initial separation remains 8 November 1985. These definitions are unreconciled.`,box);
      add('p',`Reading allowance: ${c.reading_allowance_native_pixels} original raster pixels per extremum, with fixed outward ${c.round_outward_km} km reporting. This range describes reading sensitivity only; physical uncertainty, scan distortion and junction interpretation remain unquantified.`,box);
      add('p','Lobe bounding spans are not full detached-eddy dimensions, diameter, principal width, radius or area. No Eddy C alias, merged B/C diameter, Fast Eddy measurement, physical footprint, state join or seasonal cycle inferred.',box);
    }else if(r.calculation?.method==='osw_speed_contour_named_source_case_v1'){
      const c=r.calculation;
      add('strong','OSW gridded speed core · not the full outer eddy.',add('p',undefined,box));
      add('p','The selected contour maximizes average geostrophic speed around supported closed contours. Equivalent radius is a speed-core scale; bounding arcs are not principal width. The speed is a circum-averaged estimate, not a direct local current maximum.',box);
      add('p','Two peak-relative level steps: 0.005 and 0.0025 m. Their comparison plus outward rounding is numerical only, not physical uncertainty or a seasonal range. Mapping, MDT and gradient/interpolation errors remain unquantified.',box);
      add('p',`Source point (longitude, latitude): ${c.source_point_lon_lat.join(', ')}; grid peak: ${c.grid_peak_lon_lat.join(', ')}. About ${num(c.peak_distance_from_source_point_km)} km apart. Point role: ${c.source_point_role.replaceAll('_',' ')}. The source point may be an approximate center or a map proxy; the 150 km search rule is not position accuracy.`,box);
      add('p',`Selected interior support: ${c.selected_interior_gridpoints.join(' / ')} native gridpoints. A 0.125° grid and the 12-point support rule do not establish effective feature resolution.`,box);
      add('p',`${c.date} snapshot only. ${c.source_case_name} is explicitly named in the source context; the registry physical crosswalk and source-boundary equivalence remain unverified. No other eddy values, outer radius, physical footprint, state join or seasonal animation inferred.`,box);
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
