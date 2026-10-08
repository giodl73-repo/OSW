const packageRoot = "release/v0.1.0/";
const collections = ["entities", "names", "measurements", "length_assessments", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context", "relations", "claims", "media", "geometries", "tiles", "tile_state_relations", "named_eddy_state_assessments", "named_eddy_source_observations", "named_current_source_observations", "operational_eddy_state_observations", "diagnosed_current_path_observations", "observation_sets", "sources"];
const evidenceText = {
  source_identified: "Source identified",
  source_associated: "Source associated",
  observed_geometry: "Observed geometry",
  derived_field: "Derived field",
  atlas_geometry: "Atlas geometry",
  unresolved: "Unresolved",
};
const relationText = {
  cartographic_arrow_crossing: "A published map arrow crosses this OSW state",
  osw_schematic_line_crossing: "An OSW schematic line crosses this state",
  osw_editorial_named_line_crossing: "An OSW editorial line crosses this state",
  width_sensitive_map_contact: "A source map arrow touches this state depending on drawing width",
  independently_named_downstream_flow: "An independent source names a downstream flow",
  independently_named_upstream_feeder: "An independent source names an upstream feeder",
  editorial_locator_candidate: "An editorial locator falls in this state",
  point_locator_only: "A locator point falls in this state",
  shared_source_region_gateway_only: "Shared regional gateway; individual eddy footprint unknown",
  nasa_named_or_described_current: "NASA names or describes this current",
  almanac_current_crosswalk: "Linked OSW current record",
  named_regional_segment_of: "Named regional segment relationship",
  dated_surface_front_intersection: "A dated analyzed surface front intersects this approximate OSW state",
  dated_geostrophic_streamline_segment_intersection: "A dated partial surface geostrophic streamline intersects this approximate OSW state",
  source_reported_local_current_presence: "A published local study observes this named current in the state's named region",
  unresolved: "Physical relation unresolved",
};

function element(tag, text, parent, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = String(text);
  if (className) node.className = className;
  parent.append(node);
  return node;
}

function link(label, url, parent) {
  const node = element("a", label, parent);
  node.href = url;
  if (/^https?:/.test(url)) {
    node.target = "_blank";
    node.rel = "noopener noreferrer";
  }
  return node;
}

function footprintPlot(scene,parent) {
  if(!scene?.available){element('p',scene?.reason||'Provider polygon display unavailable.',parent);return;}
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox',scene.view_box.join(' '));svg.setAttribute('role','img');svg.setAttribute('aria-label',scene.aria_label);svg.classList.add('detection-footprint');
  function child(tag,attributes,text,container=svg){const node=document.createElementNS(ns,tag);for(const [key,value]of Object.entries(attributes))node.setAttribute(key,value);if(text)node.textContent=text;container.append(node);return node;}
  const layer=child('g',{transform:scene.display_transform});
  child('path',{d:scene.polygon_d,fill:'#76d7e322',stroke:'#76d7e3','stroke-width':2,'vector-effect':'non-scaling-stroke','fill-rule':'evenodd'},null,layer);
  if(scene.center_d)child('path',{d:scene.center_d,stroke:'#ffe17c','stroke-width':2},null);
  child('text',{x:300,y:20,'text-anchor':'middle'},scene.title);
  child('text',{x:300,y:320,'text-anchor':'middle'},scene.longitude_label);
  child('text',{x:300,y:342,'text-anchor':'middle'},scene.latitude_label);
  parent.append(svg);element('p',scene.scope,parent);
  if(scene.omitted_features?.length)element('p',`${scene.omitted_features.length} invalid or unsupported plot features omitted.`,parent);
}

function loadObjectView() {
  return new Promise((resolve,reject)=>{
    const worker=new Worker('query-worker.js?v=object-view-7');
    const timer=setTimeout(()=>finish(Error('Object request timed out')),90000);
    const finish=(error,result)=>{clearTimeout(timer);worker.terminate();if(error)reject(error);else resolve(result);};
    worker.onerror=()=>finish(Error('Rust object worker failed'));
    worker.onmessage=event=>{const {id,result}=event.data;
      if(!result.ok){finish(Error(result.error));return;}
      if(id===1){worker.postMessage({id:2,action:'object_view',value:{id:new URL(location.href).searchParams.get('id')||'current:acc'}});return;}
      window.oswObjectView=result;
      document.querySelector('#object-summary').dataset.engine=result.engine;
      finish(null,result.collections);
    };
    worker.postMessage({id:1,action:'load'});
  });
}
loadObjectView().then(data => {
  const byId = Object.fromEntries(data.entities.map(item => [item.id, item]));
  const sources = Object.fromEntries(data.sources.map(item => [item.id, item]));
  let packetUrl;
  const input = document.querySelector("#object-search");
  const options = document.querySelector("#object-options");
  for (const item of [...data.entities].sort((a, b) => a.label.localeCompare(b.label))) {
    const option = element("option", undefined, options);
    option.value = `${item.label} [${item.id}]`;
  }
  function sourceLink(sourceId, parent) {
    const source = sources[sourceId];
    if (!source) return;
    const url = source.url || (packageRoot + source.path);
    link((source.label || (source.kind === "external" ? "External source" : "OSW source ledger")) + " ↗", url, parent);
  }
  function listOrEmpty(parent, rows, render, emptyText) {
    if (!rows.length) return element("p", emptyText, parent);
    const list = element("ul", undefined, parent);
    rows.forEach(item => render(item, element("li", undefined, list)));
  }
  function render(id) {
    const item = byId[id];
    if (!item) {
      document.querySelector("#search-result").textContent = "No object with that ID in this release candidate.";
      return;
    }
    document.querySelector("#search-result").textContent = "";
    document.title = `${item.label} — OSW Ocean Motion Atlas`;
    document.querySelector("#object-title").textContent = item.label;
    document.querySelector("#object-summary").textContent = `${item.type.replaceAll("_", " ")} · ${item.identity_level || "identity scope unresolved"} · ${item.basin || "basin unspecified"}`;
    const identity = document.querySelector("#identity");
    identity.replaceChildren();
    if (["named_current", "named_eddy", "operational_eddy_detection"].includes(item.type)) {
      link("Explore on the current atlas", `reference-routes.html?atlas-feature=${encodeURIComponent(item.id)}#route-atlas`, element("p", null, identity));
    }
    element("p", `Stable ID: ${item.id} · source record: ${item.source_record_id}`, identity);
    if (item.setting || item.time_behavior) {
      element("p", `OSW setting: ${(item.setting || "unresolved").replaceAll("_", " ")} · Time behavior: ${(item.time_behavior || "unresolved").replaceAll("_", " ")}`, identity);
    }
    if (item.motion_form) element("p", `OSW motion form: ${item.motion_form.replaceAll("_", " ")}`, identity);
    if (item.identity_limit) element("p", item.identity_limit, identity);
    if (item.identity_scope_note) element("p", item.identity_scope_note, identity);
    if (item.type === "operational_eddy_detection") {
      element("p", `Observation date: ${item.observation_date}. Provider labels: ${item.provider_type}, ${item.provider_rotation}. Source reuse decision: ${sources[item.source_id].rights_status.replaceAll("_", " ")}. Internal research candidate.`, identity);
    }
    sourceLink(item.source_id, identity);
    for(const record of (data.eddy_recurrence||[]).filter(row=>row.entity_id===item.id)) {
      const section=element('section',undefined,identity);section.id='eddy-recurrence-summary';
      element('h3','Published occurrence and event lifetime',section);
      const days=record.reported_occurrence_days_per_year_approx;
      const label=element('label',`About ${days} presence days per year (reported average)`,section);
      label.htmlFor='eddy-presence-meter';
      const meter=element('meter',undefined,section);meter.id='eddy-presence-meter';meter.min=0;meter.max=365;meter.value=days;
      meter.style.cssText='display:block;width:100%;max-width:36rem;height:1.5rem';
      element('p','Scale: 0–365 days in a descriptive average year. Presence may comprise several events; it is not the lifetime of one eddy.',section);
      const lifetime=record.reported_event_lifetime_approx;
      element('p',lifetime===null?'Event lifetime: not quantified in this summary.':`Event lifetime: about ${lifetime} ${record.event_lifetime_unit}${lifetime===1?'':'s'} (${record.event_lifetime_statistic}).`,section);
      element('p',record.seasonal_description,section);
      element('p',record.scope_note,section);
      element('p','No dated footprint, NASA identity match or seasonal map animation is established.',section);
      link('Read the primary source ↗',record.source_url,section);
      element('p',record.source_citation+' '+record.source_locator,section);
      const query={collection:'eddy_recurrence',sort:{field:'reported_occurrence_days_per_year_approx',direction:'desc'},limit:50};
      link('Compare all nine Black Sea recurrence summaries','query.html?q='+encodeURIComponent(JSON.stringify(query)),section);
    }
    if (item.almanac_url) {
      element("span", " · ", identity);
      link("Open almanac entry ↗", item.almanac_url, identity);
    }
    const aliases = data.names.filter(name => name.entity_id === id && !name.preferred);
    if (aliases.length) element("p", "Aliases: " + aliases.map(name => name.label).join(", "), identity);
    const locations = data.geometries.filter(row => row.entity_id === id);
    locations.forEach(row => {
      if (row.role === "dated_analyzed_surface_front") {
        const summary = element("p", `${row.observation_date} ${row.front_side.replaceAll("_", " ")}: ${row.geometry.coordinates.length} reported points, ≈${Math.round(row.observed_front_length_km).toLocaleString()} km of analyzed front. This is not a current axis or whole-current length. `, identity);
        sourceLink(row.source_id, summary);
      } else if (row.role === "dated_operational_eddy_polygon") {
        element("p", `Dated source polygon: ${row.geometry.coordinates[0].length.toLocaleString()} vertices; ${row.coordinate_reference_status}`, identity);
      } else if (row.geometry.type === "Point") {
        element("p", `Map geometry: ${row.role}; ${row.geometry.type} ${row.geometry.coordinates.join(", ")}. This is a locator, not a measured footprint.`, identity);
      } else if (row.geometry.type === "Polygon") {
        element("p", `Map geometry: ${row.role.replaceAll("_", " ")}; Polygon with ${row.geometry.coordinates.length} ring(s) and ${row.geometry.coordinates.reduce((total, ring) => total + ring.length, 0)} coordinate vertices. ${row.positional_uncertainty}`, identity);
      } else {
        element("p", `Map geometry: ${row.role.replaceAll("_", " ")}; ${row.geometry.type}, ${row.geometry.coordinates.length.toLocaleString()} points. ${row.positional_uncertainty}`, identity);
      }
    });

    const classifications = data.classification_vocabularies.filter(row => row.entity_id === id);
    const classificationArea = document.querySelector("#classifications");
    classificationArea.replaceChildren();
    document.querySelector("#classification-section").hidden = !classifications.length;
    for (const vocabulary of classifications) {
      element("h3", vocabulary.label, classificationArea);
      element("p", `${vocabulary.scope}. Source vocabulary only: no observed regime or OSW state assignment is admitted.`, classificationArea);
      const terms = element("dl", undefined, classificationArea);
      for (const term of vocabulary.terms) {
        element("dt", term.source_label, terms);
        element("dd", term.criterion_summary, terms);
      }
      element("p", vocabulary.density_variable_note, classificationArea);
      element("p", `Required for an assignment: ${vocabulary.assignment_requirements.join("; ")}.`, classificationArea);
      sourceLink(vocabulary.source_id, classificationArea);
      element("p", `Source locator: ${vocabulary.source_locator}. Scientific claim review: pending.`, classificationArea);
    }

    const footprints = data.named_eddy_footprint_candidates.filter(row => row.entity_id === id || row.state_assessments.some(item => item.state_id === id));
    document.querySelector("#footprint-section").hidden = !footprints.length;
    const footprintArea = document.querySelector("#footprints"); footprintArea.replaceChildren();
    for (const candidate of footprints) {
      const card = element("div", undefined, footprintArea);
      renderRustOceanFootprintCandidate({parent: card, candidate,
        plotScene: window.oswObjectView.footprint_plots[candidate.id],
        geometry: data.geometries.find(row => row.id === candidate.geometry_id),
        movieContexts: data.footprint_movie_context.filter(row => row.footprint_candidate_id === candidate.id),
        entityLink: (target, parent) => link(byId[target].label, "object.html?id=" + encodeURIComponent(target), parent),
        sourceLink});
    }
    if (footprints.length) link("Download footprint candidate records (JSON) ↗", packageRoot + "named_eddy_footprint_candidates.json", footprintArea);
    const measurement = document.querySelector("#measurements");
    measurement.replaceChildren();
    if (item.type === "named_current") {
      const assessment = data.length_assessments.find(row => row.entity_id === id);
      if (assessment) {
        const rankedCount = data.length_assessments.filter(row => row.rank_eligible).length;
        element("p", `Whole-current length status: ${assessment.evidence_status.replaceAll("_", " ")}. ${assessment.published_rank != null ? `Rank ${assessment.published_rank} within the ${rankedCount} published estimates in this source set.` : "No comparable published-estimate rank."}`, measurement);
        if (assessment.illustrated_span_km != null) {
          element("p", `Drawn map-arrow span: approximately ${Number(assessment.illustrated_span_km).toLocaleString("en-US")} km${assessment.illustrated_span_rank != null ? ` (illustration rank ${assessment.illustrated_span_rank})` : ""}. This is not a physical current length or lower bound.`, measurement);
        }
        link("Download this source-set length assessment ↗", packageRoot + "length_assessments.csv", measurement);
      }
    }
    listOrEmpty(measurement, data.measurements.filter(row => row.entity_id === id), (row, li) => {
      element("strong", `${Number(row.value).toLocaleString("en-US")} ${row.unit}`, li);
      element("span", ` · ${row.quantity.replaceAll("_", " ")} · ${row.evidence_status}; ${row.rank_eligible ? "eligible for published-estimate ranking" : "unranked"}. ${row.scope || "Scope not stated."} `, li);
      if (row.source_locator) element("span", `Source locator: ${row.source_locator}. `, li);
      sourceLink(row.source_id, li);
    }, "No comparable whole-object measurement has been admitted.");

    const relationArea = document.querySelector("#relations");
    relationArea.replaceChildren();
    const related = data.relations.filter(row => row.subject_id === id || row.object_id === id);
    const supported = related.filter(row => row.evidence_class !== "unresolved");
    const unresolved = related.filter(row => row.evidence_class === "unresolved");
    element("p", `${supported.length} linked relations; ${unresolved.length} unresolved relations in this source set.`, relationArea);
    listOrEmpty(relationArea, supported, (row, li) => {
      const other = row.subject_id === id ? row.object_id : row.subject_id;
      link(byId[other].label, "object.html?id=" + encodeURIComponent(other), li);
      element("span", ` · ${relationText[row.predicate] || row.predicate.replaceAll("_", " ")} · ${evidenceText[row.evidence_class] || row.evidence_class}`, li);
      if (row.observation_date) element("span", ` · ${row.observation_date}${row.front_side ? ` · ${row.front_side.replaceAll("_", " ")}` : ""}`, li);
      if (row.observation_start) element("span", ` · ${row.observation_start} to ${row.observation_end}`, li);
      if (row.physical_relation) element("span", ` · physical relation: ${row.physical_relation.replaceAll("_", " ")}`, li);
      element("span", " · ", li);
      sourceLink(row.source_id, li);
    }, "No linked relations yet.");
    if (unresolved.length) {
      const details = element("details", undefined, relationArea);
      element("summary", `Show ${unresolved.length} unresolved relations`, details);
      listOrEmpty(details, unresolved, (row, li) => {
        const other = row.subject_id === id ? row.object_id : row.subject_id;
        link(byId[other].label, "object.html?id=" + encodeURIComponent(other), li);
        element("span", " · physical relation unresolved", li);
      }, "");
    }

    const claimArea = document.querySelector("#claim-audit");
    claimArea.replaceChildren();
    const objectClaims = data.claims.filter(row => row.subject_id === id || row.object_id === id);
    const internalLocators = objectClaims.filter(row => row.source_locator_status === "internal_ledger_row").length;
    const internalRecords = objectClaims.filter(row => row.source_locator_status === "internal_ledger_record").length;
    const specificLocators = objectClaims.filter(row => row.source_locator_status === "specific").length;
    const missingLocators = objectClaims.filter(row => row.source_locator_status === "source_only_no_precise_locator");
    element("p", `${objectClaims.length} linked claim records: ${internalLocators} point to exact OSW ledger rows, ${internalRecords} point to source eddy or NASA records, ${specificLocators} have specific source locators, and ${missingLocators.length} have only a source-level link. Individual claim review is pending.`, claimArea);
    if (missingLocators.length) {
      const details = element("details", undefined, claimArea);
      element("summary", `Show ${missingLocators.length} claims needing a precise source locator`, details);
      listOrEmpty(details, missingLocators, (row, li) => {
        element("span", `${row.predicate.replaceAll("_", " ")} · ${row.target_id} · `, li);
        sourceLink(row.source_id, li);
      }, "");
    }
    link("Download all claim records ↗", packageRoot + "claims.csv", claimArea);

    const publishedCurrentSection = document.querySelector("#published-current-section");
    const publishedCurrentArea = document.querySelector("#published-current-observations");
    const publishedCurrentRows = data.named_current_source_observations.filter(row =>
      row.entity_id === id || row.state_id === id);
    publishedCurrentSection.hidden = !publishedCurrentRows.length;
    publishedCurrentArea.replaceChildren();
    for (const row of publishedCurrentRows) {
      const other = row.entity_id === id ? row.state_id : row.entity_id;
      const paragraph = element("p", undefined, publishedCurrentArea);
      link(byId[other].label, "object.html?id=" + encodeURIComponent(other), paragraph);
      element("span", ` · ${row.observation_start} to ${row.observation_end} · ${row.reported_locality}. ${row.time_detail} ${row.state_boundary_limit} This local observation does not establish a whole-current path, length, or permanent state passage. `, paragraph);
      if (row.observation_depth_note) element("span", `${row.observation_depth_note} `, paragraph);
      if (row.reported_observation_points_lon_lat) element("span", `Instrument positions (longitude, latitude): ${row.reported_observation_points_lon_lat.map(point => point.join(", ")).join("; ")}. `, paragraph);
      sourceLink(row.source_id, paragraph);
      if (row.reported_observation_points_lon_lat) {
        const source = sources[row.source_id];
        element("p", source.credit_text, publishedCurrentArea);
        if (source.license_url) link("Source license: CC BY 4.0 ↗", source.license_url, publishedCurrentArea);
      }
    }
    if (publishedCurrentRows.length) link("Download dated named-current observations ↗", packageRoot + "named_current_source_observations.csv", publishedCurrentArea);

    const diagnosedRelations = data.relations.filter(row => row.predicate === "dated_geostrophic_streamline_segment_intersection" && row.object_id === id);
    const diagnosedRows = data.diagnosed_current_path_observations.filter(row =>
      row.entity_id === id || diagnosedRelations.some(relation => relation.subject_id === row.entity_id));
    const diagnosedSection = document.querySelector("#diagnosed-current-section");
    const diagnosedArea = document.querySelector("#diagnosed-current-observations");
    diagnosedSection.hidden = !diagnosedRows.length;
    diagnosedArea.replaceChildren();
    for (const row of diagnosedRows) {
      const local = diagnosedRelations.find(relation => relation.subject_id === row.entity_id);
      const paragraph = element("p", `${row.observation_date} · ${Number(row.reach_length_km).toLocaleString("en-US")} km from the declared seed gate to 50°W${local ? `; approximately ${Number(local.diagnosed_segment_length_km).toLocaleString("en-US")} km of that line intersects this state` : ""}. NOAA labels the source analysis ${row.source_product_status.toLowerCase()}. This is an unranked, frozen-time surface geostrophic streamline reach. ${row.physical_limit} `, diagnosedArea);
      sourceLink(row.source_id, paragraph);
      const sensitivity = element("p", `Adjacent seeds: ${row.adjacent_seed_sensitivity.map(item => `${item.seed_lon_lat[1]}°N ${item.stop_reason.replaceAll("_", " ")} after ${Number(item.segment_length_km).toLocaleString("en-US")} km`).join("; ")}. Numerical step tests: ${row.step_size_sensitivity.map(item => `${item.step_km} km step → ${Number(item.segment_length_km).toLocaleString("en-US")} km`).join("; ")}.`, diagnosedArea);
      sensitivity.className = "footnote";
    }
    if (diagnosedRows.length) link("Download dated diagnostic path observation ↗", packageRoot + "diagnosed_current_path_observations.csv", diagnosedArea);

    const operationalEddyRows = data.operational_eddy_state_observations.filter(row => row.state_id === id || row.operational_eddy_id === id);
    const operationalEddySection = document.querySelector("#operational-eddy-section");
    const operationalEddyArea = document.querySelector("#operational-eddy-observations");
    operationalEddySection.hidden = !operationalEddyRows.length;
    operationalEddyArea.replaceChildren();
    for (const row of operationalEddyRows) {
      const paragraph = element("p", `${row.observation_date} · ${row.provider_code} · ${row.provider_type.toLowerCase()}, ${row.provider_rotation.toLowerCase()} · ${row.relation.replaceAll("_", " ")}. The source shapefile lacks a declared coordinate reference system; state shapes are approximate. `, operationalEddyArea);
      const other = row.operational_eddy_id === id ? row.state_id : row.operational_eddy_id;
      link(byId[other].label, "object.html?id=" + encodeURIComponent(other), paragraph);
      element("span", " · ", paragraph);
      sourceLink(row.source_id, paragraph);
    }
    if (operationalEddyRows.length) link("Download dated operational eddy/state observations ↗", packageRoot + "operational_eddy_state_observations.csv", operationalEddyArea);
    const detectionSection = document.querySelector("#detection-section");
    const detectionArea = document.querySelector("#detection-detail");
    detectionSection.hidden = item.type !== "operational_eddy_detection";
    detectionArea.replaceChildren();
    if (packetUrl) { URL.revokeObjectURL(packetUrl); packetUrl = undefined; }
    if (!detectionSection.hidden) {
      const geometry = locations.find(row => row.role === "dated_operational_eddy_polygon");
      footprintPlot(window.oswObjectView.detection_plot, detectionArea);
      element("h3", "OSW state footprint relation", detectionArea);
      for (const row of operationalEddyRows) {
        const paragraph = element("p", undefined, detectionArea);
        link(byId[row.state_id].label, "object.html?id=" + encodeURIComponent(row.state_id), paragraph);
        element("span", ` · ${row.relation.replaceAll("_", " ")} · ${(100 * row.display_projection_polygon_area_fraction).toFixed(1)}% of this polygon's display-projected area. ${row.relation_limit}`, paragraph);
      }
      element("p", `Source ZIP SHA-256: ${geometry.source_zip_sha256}`, detectionArea, "source-digest");
      const claims = data.claims.filter(row => operationalEddyRows.some(observation => observation.claim_id === row.id));
      const claimDetails = element("details", undefined, detectionArea);
      element("summary", "State-intersection evidence and method", claimDetails);
      for (const claim of claims) element("p", `${claim.id}: ${claim.method}. Source locator: ${claim.source_locator}. Scientific review: ${claim.review_status.replaceAll("_", " ")}.`, claimDetails);
      const stateIds = new Set(operationalEddyRows.map(row => row.state_id));
      const contextRelations = data.tile_state_relations.filter(row => stateIds.has(row.state_id));
      const tileIds = new Set(contextRelations.map(row => row.tile_id));
      const contextTiles = data.tiles.filter(row => tileIds.has(row.tile_id));
      element("h3", "NASA regional context", detectionArea);
      element("p", "These crops overlap the associated state's approximate display area. They are regional navigation links, not a match to this polygon or the 2026-09-25 observation. NASA does not identify this provider detection here.", detectionArea);
      const movieDetails = element("details", undefined, detectionArea);
      element("summary", `${contextTiles.length} NASA regional movie crops`, movieDetails);
      listOrEmpty(movieDetails, contextTiles, (tile, li) => {
        link(`Crop ${tile.tile_id} · zoom ${tile.zoom}`, tile.url, li);
      }, "No regional crop address in this source set.");
      const packet = {schema: "osw.ocean-motion-detection-review-packet.v1", status: "full_research_candidate_pending_source_use_not_published",
        entity: item, geometries: locations, state_observations: operationalEddyRows, claims,
        states: [...stateIds].map(stateId => byId[stateId]),
        regional_movie_context: {limit: "State display overlap only; no dated detection identification or temporal match", tiles: contextTiles, state_tile_relations: contextRelations,
          claims: data.claims.filter(claim => contextRelations.some(row => row.claim_id === claim.id))}};
      const packetSourceIds = new Set();
      function collectSources(value) {
        if (typeof value === "string" && sources[value]) packetSourceIds.add(value);
        else if (Array.isArray(value)) value.forEach(collectSources);
        else if (value && typeof value === "object") Object.values(value).forEach(collectSources);
      }
      collectSources(packet);
      packet.sources = [...packetSourceIds].sort().map(sourceId => sources[sourceId]);
      packetUrl = URL.createObjectURL(new Blob([JSON.stringify(packet, null, 2) + "\n"], {type: "application/json"}));
      const download = link("Download this detection's evidence packet", packetUrl, detectionArea);
      download.download = `${id.replaceAll(":", "-")}.json`;
    }

    const eddyStateSection = document.querySelector("#named-eddy-state-section");
    eddyStateSection.hidden = !["named_eddy", "osw_state"].includes(item.type);
    const eddyStateArea = document.querySelector("#named-eddy-state-assessments");
    eddyStateArea.replaceChildren();
    if (!eddyStateSection.hidden) {
      const assessments = data.named_eddy_state_assessments.filter(row =>
        item.type === "named_eddy" ? row.eddy_id === id : row.state_id === id);
      const candidates = assessments.filter(row => row.evidence_status !== "unresolved");
      const scope = item.type === "named_eddy" ? "56 OSW states" :
        `${data.entities.filter(row => row.type === "named_eddy").length} named eddy records`;
      element("p", `${assessments.length} assessments across ${scope}; ${candidates.length} ${candidates.length === 1 ? "has" : "have"} source-specific location evidence. Verified whole-eddy containment or intersection: 0. Whole-ring physical relations remain unknown without a dated footprint.`, eddyStateArea);
      if (candidates.length) {
        const details = element("details", undefined, eddyStateArea);
        element("summary", `Show ${candidates.length} candidate addresses`, details);
        const list = element("ul", undefined, details);
        for (const row of candidates) {
          const other = item.type === "named_eddy" ? row.state_id : row.eddy_id;
          const li = element("li", undefined, list);
          link(byId[other].label, "object.html?id=" + encodeURIComponent(other), li);
          element("span", ` · ${row.evidence_status.replaceAll("_", " ")}${row.point_evidence_types.length ? ` · ${row.point_evidence_types.join(", ").replaceAll("_", " ")}` : ""}; footprint unresolved`, li);
        }
      }
      const unresolvedCount = assessments.length - candidates.length;
      element("p", `${unresolvedCount} pairs have no candidate address in this source set. `, eddyStateArea);
      link("Download the complete named-eddy/state table ↗", packageRoot + "named_eddy_state_assessments.csv", eddyStateArea);
    }

    const publishedEddySection = document.querySelector("#published-eddy-section");
    const publishedEddyArea = document.querySelector("#published-eddy-observations");
    const publishedEddyRows = data.named_eddy_source_observations.filter(row => row.entity_id === id);
    publishedEddySection.hidden = item.type !== "named_eddy" || !publishedEddyRows.length;
    publishedEddyArea.replaceChildren();
    for (const row of publishedEddyRows) {
      const geometryNote = row.geometry_status === "figure_red_pixels_georeferenced_no_closed_boundary" ?
        "Figure red pixels support a location candidate; whole-ring state containment remains unresolved." :
        row.observed_center ?
        "The source-reported center is a dated point candidate; whole-ring state containment remains unresolved." :
        "Dated figure geometry is not digitized; state containment remains unresolved.";
      const centerNote = row.observed_center ? `Reported center on ${row.observed_center.date}: ${row.observed_center.coordinate_lon_lat[1]}°N, ${Math.abs(row.observed_center.coordinate_lon_lat[0])}°W; approximate point only. ` : "";
      const paragraph = element("p", `${row.observation_start} to ${row.observation_end} · ${row.evidence_type.replaceAll("_", " ")}. ${row.interpretation} ${row.reported_measure || ""} ${centerNote}${row.name_origin ? `Name origin: ${row.name_origin}.` : ""} ${geometryNote} `, publishedEddyArea);
      sourceLink(row.source_id, paragraph);
      element("span", ` · ${row.source_locator}`, paragraph);
    }

    const observationSection = document.querySelector("#observation-section");
    observationSection.hidden = item.type !== "osw_state";
    if (item.type === "osw_state") {
      const body = document.querySelector("#observation-rows");
      body.replaceChildren();
      for (const set of data.observation_sets) {
        const counts = set.state_counts[item.source_record_id];
        const tr = element("tr", undefined, body);
        element("td", set.date, tr);
        element("td", counts.contained.toLocaleString("en-US"), tr);
        element("td", counts.intersected.toLocaleString("en-US"), tr);
        const recordCell = element("td", undefined, tr);
        link("Dated detection table ↗", packageRoot + set.observation_file, recordCell);
      }
    }

    const mediaArea = document.querySelector("#media");
    mediaArea.replaceChildren();
    listOrEmpty(mediaArea, data.media.filter(row => row.entity_id === id), (row, li) => {
      link("Open NASA movie ↗", row.url, li);
      element("span", ` · ${row.relation.replaceAll("_", " ")}${row.tile_id ? ` · crop ${row.tile_id}` : ""}`, li);
    }, "No NASA movie address is linked to this object.");
  }
  document.querySelector("#object-search-form").addEventListener("submit", event => {
    event.preventDefault();
    const match = input.value.match(/\[([^\]]+)\]$/);
    const id = match ? match[1] : input.value.trim();
    if (byId[id]) window.location.href = "object.html?id=" + encodeURIComponent(id);
    else document.querySelector("#search-result").textContent = "Select a listed object or enter a stable ID.";
  });
  render(new URLSearchParams(window.location.search).get("id") || "current:acc");
}).catch(error => {
  document.querySelector("#object-summary").textContent = "Release data unavailable. Return to the motion almanac or try reloading this page.";
  console.error(error);
});
