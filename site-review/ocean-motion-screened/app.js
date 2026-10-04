(() => {
  const collections = ["entities", "names", "length_assessments", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context", "measurements", "relations", "claims", "geometries", "media", "tiles", "tile_state_relations", "named_eddy_state_assessments", "named_eddy_source_observations", "named_current_source_observations", "sources", "ranked-length-editorial-reviews", "entity-packets-index"];
  const byId = id => document.getElementById(id);
  const node = (tag, value, parent) => { const item = document.createElement(tag); if (value != null) item.textContent = value; if (parent) parent.append(item); return item; };
  const labelKind = { named_current: "Named current", named_eddy: "Named eddy", nasa_described_motion: "NASA motion", osw_state: "OSW state" };
  const formatNumber = value => Number(value).toLocaleString("en-US", { maximumFractionDigits: 1 });
  const objectHref = id => `?id=${encodeURIComponent(id)}#record`;
  const stateHref = id => `?state=${encodeURIComponent(id)}#states`;
  function link(label, href, parent, external = false) {
    const item = node("a", label, parent);
    item.href = href;
    if (external) { item.target = "_blank"; item.rel = "noopener noreferrer"; }
    return item;
  }
  async function load(name) {
    const response = await fetch(`data/${name}.json`);
    if (!response.ok) throw new Error(`Could not load ${name}: HTTP ${response.status}`);
    return response.json();
  }
  function sourceLink(sourceId, lookup, parent) {
    const source = lookup.get(sourceId);
    if (!source) return node("span", sourceId || "Source unresolved", parent);
    if (source.url) return link(source.title || source.label, source.url, parent, true);
    return node("span", source.title || source.label, parent);
  }
  function renderEditorial(editorial, parent) {
    const note = node("p", `Editorial passage check: ${editorial.editorial_note} Scientific claim review: pending.`, parent);
    note.className = editorial.emphasis === "scope_warning" || editorial.source_passage_assessment === "quoted_number_supported_with_source_warning" ? "warning" : "small";
    for (const source of editorial.corroborating_sources || []) {
      const citation = node("p", "Corroborating source: ", parent);
      link(source.locator, source.url, citation, true);
      node("span", ` · ${source.role.replaceAll("_", " ")}`, citation);
    }
  }
  function attachObjectLink(id, lookup, parent, text) {
    const entity = lookup.get(id);
    const anchor = link(text || entity?.label || id, objectHref(id), parent);
    anchor.addEventListener("click", event => {
      event.preventDefault();
      history.pushState({ id }, "", anchor.href);
      renderRecord(id);
      byId("record").scrollIntoView({ block: "start" });
      byId("record-title").focus();
    });
    return anchor;
  }
  let data, entityById, sourceById, lengthByEntity, mediaByEntity, rankedMeasurementByEntity, editorialByClaim;

  const project = ([longitude, latitude]) => [60 + (longitude + 180) / 360 * 1480, 90 + (90 - latitude) / 180 * 740];
  function renderMarkers(visible) {
    const svgNS = "http://www.w3.org/2000/svg";
    const layer = byId("markers"); layer.replaceChildren();
    const allowed = new Set(visible.map(item => item.id));
    for (const geometry of data.geometries) {
      if (!allowed.has(geometry.entity_id) || geometry.geometry.type !== "Point") continue;
      const entity = entityById.get(geometry.entity_id);
      const [longitude, latitude] = geometry.geometry.coordinates;
      const anchor = document.createElementNS(svgNS, "a");
      anchor.setAttribute("href", objectHref(entity.id));
      anchor.setAttribute("aria-label", `Open ${entity.label}; approximate editorial locator at ${latitude} degrees latitude, ${longitude} degrees longitude`);
      const circle = document.createElementNS(svgNS, "circle");
      const [x, y] = project([longitude, latitude]);
      circle.setAttribute("cx", x); circle.setAttribute("cy", y);
      circle.setAttribute("r", 7); circle.setAttribute("class", `marker${new URLSearchParams(location.search).get("id") === entity.id ? " selected" : ""}`);
      const title = document.createElementNS(svgNS, "title"); title.textContent = `${entity.label} · editorial locator`; circle.append(title);
      anchor.append(circle);
      anchor.addEventListener("click", event => {
        event.preventDefault(); history.pushState({ id: entity.id }, "", anchor.getAttribute("href"));
        renderRecord(entity.id); byId("record").scrollIntoView({ block: "start" }); byId("record-title").focus();
      });
      layer.append(anchor);
    }
  }
  function renderDirectory() {
    const query = byId("search").value.trim().toLocaleLowerCase();
    const kind = byId("kind").value;
    const visible = data.entities.filter(item => (kind === "all" || item.type === kind) &&
      (!query || `${item.label} ${item.basin || ""} ${item.id} ${item.setting || ""}`.toLocaleLowerCase().includes(query)));
    const body = byId("object-rows"); body.replaceChildren();
    for (const item of visible) {
      const row = node("tr", null, body);
      attachObjectLink(item.id, entityById, node("td", null, row));
      node("td", labelKind[item.type] || item.type, row);
      node("td", item.basin || "—", row);
      node("td", [item.identity_level, item.setting, item.time_behavior].filter(Boolean).join(" · ") || "Source-scoped record", row);
    }
    byId("object-count").textContent = `${visible.length} of ${data.entities.length} records`;
    renderMarkers(visible);
  }
  function renderRecord(id) {
    const item = entityById.get(id);
    const body = byId("record-body"); body.replaceChildren();
    if (!item) { byId("record-title").textContent = "Record unavailable in this screened source set"; byId("selection-status").textContent = "This object ID is unavailable in the screened source set."; node("p", "The ID may belong to an excluded source record. Search the directory for a retained object.", body); return; }
    byId("record-title").textContent = item.label;
    if (item.identity_scope_note) node("p", item.identity_scope_note, body);
    const vocabularies = data.classification_vocabularies.filter(row => row.entity_id === id);
    for (const vocabulary of vocabularies) {
      const card = node("section", null, body); card.className = "classification-card";
      node("h3", "Published regional classification", card);
      node("p", `${vocabulary.scope}. Source vocabulary only: no observed regime or OSW state assignment is admitted.`, card);
      const terms = node("dl", null, card);
      for (const term of vocabulary.terms) { node("dt", term.source_label, terms); node("dd", term.criterion_summary, terms); }
      node("p", vocabulary.density_variable_note, card);
      node("p", `Required for an assignment: ${vocabulary.assignment_requirements.join("; ")}.`, card);
      sourceLink(vocabulary.source_id, sourceById, card);
      node("p", `Source locator: ${vocabulary.source_locator}. Scientific claim review: pending.`, card);
    }

    for (const candidate of data.named_eddy_footprint_candidates.filter(row => row.entity_id === id || row.state_assessments.some(item => item.state_id === id))) {
      renderOceanFootprintCandidate({parent: node("section", null, body), candidate,
        geometry: data.geometries.find(row => row.id === candidate.geometry_id),
        movieContexts: data.footprint_movie_context.filter(row => row.footprint_candidate_id === candidate.id),
        entityLink: (target, parent) => link(entityById.get(target).label, target.startsWith("state:") ? stateHref(target) : objectHref(target), parent),
        sourceLink: (source, parent) => sourceLink(source, sourceById, parent)});
    }
    byId("selection-status").textContent = `Opened ${item.label}. Details follow below.`;
    const introduction = node("p", null, body);
    node("span", `${labelKind[item.type]} · ${item.basin || "basin not assigned"} · ${item.identity_level || "source-scoped identity"}`, introduction);
    introduction.append(document.createTextNode(" · Source: ")); sourceLink(item.source_id, sourceById, introduction);
    const cards = node("div", null, body); cards.className = "record-grid";
    const identities = node("div", null, cards); node("h3", "Identity and names", identities);
    node("p", `Stable ID: ${item.id}`, identities);
    const packetPath = data["entity-packets-index"][item.id];
    if (packetPath) {
      const packet = link("Download this record and its evidence (JSON review copy)", `data/${packetPath}`, identities);
      packet.download = packetPath.split("/").pop();
    }
    if (item.type === "osw_state") link("Open state passport", stateHref(item.id), identities);
    const aliases = data.names.filter(row => row.entity_id === id && row.label !== item.label);
    node("p", aliases.length ? `Other source names: ${[...new Set(aliases.map(row => row.label))].join("; ")}` : "No alternate source name recorded.", identities);
    node("p", `Identity: ${item.identity_level || "—"}; setting: ${item.setting || "—"}; time behavior: ${item.time_behavior || "—"}.`, identities);

    const locations = node("div", null, cards); node("h3", "Map address", locations);
    const points = data.geometries.filter(row => row.entity_id === id && row.geometry.type === "Point");
    node("p", points.length ? `${points.length} approximate editorial locator point${points.length === 1 ? "" : "s"}; not an observed path, core, or footprint.` : "No map point admitted for this record.", locations);
    for (const point of points) node("p", `${point.geometry.coordinates[1]}° latitude, ${point.geometry.coordinates[0]}° longitude · ${point.coordinate_reference_system}`, locations);

    const currentObservations = data.named_current_source_observations.filter(row => row.entity_id === id || row.state_id === id);
    if (currentObservations.length) {
      const observations = node("div", null, cards); node("h3", "Published local current observations", observations);
      for (const row of currentObservations) {
        node("p", `${row.observation_start} to ${row.observation_end} · ${row.reported_locality}. ${row.time_detail}`, observations);
        if (row.observation_depth_note) node("p", row.observation_depth_note, observations);
        if (row.reported_observation_points_lon_lat) node("p", `Instrument positions (longitude, latitude): ${row.reported_observation_points_lon_lat.map(point => point.join(", ")).join("; ")}.`, observations);
        node("p", `${row.state_boundary_limit} A local observation does not establish a whole-current path, length, or permanent state passage.`, observations);
        const related = node("p", "Related atlas record: ", observations);
        if (row.entity_id === id) link(entityById.get(row.state_id).label, stateHref(row.state_id), related);
        else link(entityById.get(row.entity_id).label, objectHref(row.entity_id), related);
        const citation = node("p", "Paper: ", observations); sourceLink(row.source_id, sourceById, citation);
        if (row.reported_observation_points_lon_lat) {
          const source = sourceById.get(row.source_id);
          node("p", source.credit_text, observations);
          if (source.license_url) link("Source license: CC BY 4.0", source.license_url, node("p", null, observations), true);
        }
        const publicationCopy = sourceById.get(row.source_id)?.source_file_url;
        if (publicationCopy) link("Read cited publication copy (PDF)", publicationCopy, node("p", null, observations), true);
      }
    }
    const eddyObservations = data.named_eddy_source_observations.filter(row => row.entity_id === id);
    if (eddyObservations.length) {
      const observations = node("div", null, cards); node("h3", "Published ring observations", observations);
      for (const row of eddyObservations) {
        node("p", row.event_stage
          ? `${row.observation_start} · ${row.event_stage.replaceAll("_", " ")} · ${row.source_locator}. This is a source-reported event stage, not an OSW-derived footprint or complete eddy lifetime.`
          : `${row.observation_start} to ${row.observation_end} · ${row.source_locator}. This is the paper's observation window, not a complete eddy lifetime.`, observations);
        node("p", row.interpretation, observations);
        if (row.name_origin) node("p", `Name origin: ${row.name_origin}.`, observations);
        const citation = node("p", "Paper: ", observations); sourceLink(row.source_id, sourceById, citation);
      }
      node("p", id === "eddy:published:kraken-2013"
        ? "OSW traces Kraken's 29 May closed SSH contour from Figure 2 as a dated image-derived footprint proxy. It is not the authors' numeric boundary or a whole-ring lifetime footprint. Whole-eddy state containment remains unresolved."
        : "The authors' closed boundary has not been reconstructed as a coordinate polygon. Whole-eddy state containment and intersection remain unresolved.", observations);
    }
    const figureCandidates = data.named_eddy_state_assessments.filter(row =>
      row.eddy_id === id && ["figure_derived_red_curve_candidate", "figure_derived_dated_ssh_contour_candidate"].includes(row.evidence_status));
    if (figureCandidates.length) {
      const figure = node("div", null, cards); node("h3", "Dated figure location", figure);
      for (const row of figureCandidates) {
        const description = row.evidence_status === "figure_derived_red_curve_candidate"
          ? `Figure 2 red coherent-core and shielding-curve pixels on ${row.figure_observation_dates.join(", ")} fall in or near the approximate ${entityById.get(row.state_id)?.label || row.state_id} state. The minimum red-pixel fraction inside CAMR across axis calibration checks is ${formatNumber(row.figure_axis_sensitivity_fraction * 100)}%. The 29 May closed blue SSH footprint proxy also robustly intersects CAMR; nominal overlap is about ${formatNumber(row.dated_ssh_contour_nominal_area_fraction * 100)}%, and the lowest tested overlap is ${formatNumber(row.dated_ssh_contour_area_fraction_range[0] * 100)}%. Whole-ring containment remains unresolved. `
          : `Figure 2's closed blue instantaneous SSH contour on ${row.dated_ssh_contour_observation_date} nominally overlaps the approximate ${entityById.get(row.state_id)?.label || row.state_id} state by about ${formatNumber(row.dated_ssh_contour_nominal_area_fraction * 100)}% of its image-derived footprint. Axis calibration checks range from ${formatNumber(row.dated_ssh_contour_area_fraction_range[0] * 100)}% to ${formatNumber(row.dated_ssh_contour_area_fraction_range[1] * 100)}%, so this is an axis-sensitive intersection candidate. It is not a whole-ring lifetime footprint. `;
        const p = node("p", description, figure);
        link("Open state passport", stateHref(row.state_id), p);
        const audit = node("p", "Inspect source-image hashes, pixel envelopes, threshold tests, and calibration method: ", figure);
        link("Screened Figure 2 audit JSON", "data/source-ledgers/kraken-2013-figure2-state-audit.json", audit);
      }
    }
    const centerCandidates = data.named_eddy_state_assessments.filter(row =>
      row.eddy_id === id && row.evidence_status === "published_observed_center_point_candidate");
    if (centerCandidates.length) {
      const centers = node("div", null, cards); node("h3", "Dated observed center point", centers);
      for (const row of centerCandidates) {
        const p = node("p", `The paper places the center near ${row.reported_center_lon_lat[1]}°N, ${Math.abs(row.reported_center_lon_lat[0])}°W on ${row.observed_center_date}. OSW projects this approximate point into ${entityById.get(row.state_id)?.label || row.state_id}. The point does not establish whole-ring containment or intersection. `, centers);
        link("Open state passport", stateHref(row.state_id), p);
        const citation = node("p", `Source: ${row.source_locator}. `, centers);
        sourceLink(row.source_id, sourceById, citation);
      }
    }

    const measure = node("div", null, cards); node("h3", "Length and measurement", measure);
    const assessment = lengthByEntity.get(id);
    if (assessment) {
      const value = assessment.published_length_km != null ? `≈${formatNumber(assessment.published_length_km)} km${assessment.rank_eligible ? ` · source-set rank ${assessment.published_rank}` : ""}` :
        assessment.lower_bound_km != null ? `≥${formatNumber(assessment.lower_bound_km)} km · unranked lower bound` : "No comparable numeric length admitted.";
      node("p", value, measure);
      node("p", `${assessment.evidence_status.replaceAll("_", " ")} · ${assessment.scope || "Scope not recorded"}`, measure);
      if (assessment.length_source_id) { const p = node("p", "Length source: ", measure); sourceLink(assessment.length_source_id, sourceById, p); }
      const editorial = editorialByClaim.get(rankedMeasurementByEntity.get(id)?.claim_id);
      if (editorial) renderEditorial(editorial, measure);
    } else node("p", "No whole-current length assessment for this kind of object.", measure);
    for (const row of data.measurements.filter(row => row.entity_id === id)) node("p", `${row.quantity.replaceAll("_", " ")}: ${formatNumber(row.value)} ${row.unit || ""} · ${row.scope || ""}`, measure);

    const relations = node("div", null, cards); node("h3", "Linked atlas evidence", relations);
    const allRelations = data.relations.filter(row => row.subject_id === id || row.object_id === id);
    const supported = allRelations.filter(row => row.evidence_class !== "unresolved");
    node("p", `${supported.length} source-linked or editorial relations; ${allRelations.length - supported.length} unresolved assessments. Each relation below names its evidence class. A missing relation is not observed absence.`, relations);
    if (supported.length) {
      const list = node("ul", null, relations);
      for (const row of supported.slice(0, 24)) {
        const other = row.subject_id === id ? row.object_id : row.subject_id;
        const entry = node("li", `${row.predicate.replaceAll("_", " ")} (${row.evidence_class.replaceAll("_", " ")}) · `, list);
        attachObjectLink(other, entityById, entry);
      }
      if (supported.length > 24) node("p", `${supported.length - 24} more links remain in the downloadable relations table.`, relations);
    }

    const films = node("div", null, cards); node("h3", "NASA geographic views", films);
    const filmRows = mediaByEntity.get(id) || [];
    if (!filmRows.length) node("p", "No movie view linked in this screened source set.", films);
    else {
      node("p", `${filmRows.length} movie link${filmRows.length === 1 ? "" : "s"}. A geographic crop is not NASA identification of this named object.`, films);
      const list = node("ul", null, films);
      for (const row of filmRows.slice(0, 12)) link(`${row.tile_id || "NASA release"} · watch at NASA`, row.url, node("li", null, list), true);
      if (filmRows.length > 12) node("p", `${filmRows.length - 12} additional links are in the media download.`, films);
    }
    const provenance = node("div", null, body); node("h3", "Claim provenance", provenance);
    const objectClaims = data.claims.filter(row => row.subject_id === id || row.object_id === id);
    node("p", `${objectClaims.length} linked claims; individual scientific review remains pending.`, provenance);
    const specific = objectClaims.filter(row => row.source_locator_status === "specific");
    if (specific.length) {
      const list = node("ul", null, provenance);
      for (const claim of specific.slice(0, 10)) {
        const entry = node("li", `${claim.predicate.replaceAll("_", " ")} · ${claim.source_locator || "source locator unavailable"} · `, list);
        sourceLink(claim.source_id, sourceById, entry);
      }
      if (specific.length > 10) node("p", `${specific.length - 10} more source-specific claims are in the claims table.`, provenance);
    }
    link("Download all claims (JSON)", "data/claims.json", provenance);
    renderMarkers(data.entities.filter(row => (byId("kind").value === "all" || row.type === byId("kind").value) &&
      (!byId("search").value || `${row.label} ${row.basin || ""} ${row.id} ${row.setting || ""}`.toLocaleLowerCase().includes(byId("search").value.trim().toLocaleLowerCase()))));
  }
  function renderLengths() {
    const body = byId("length-rows"); body.replaceChildren();
    const ranked = data.length_assessments.filter(row => row.rank_eligible).sort((a, b) => a.published_rank - b.published_rank || a.entity_id.localeCompare(b.entity_id));
    for (const row of ranked) {
      const tr = node("tr", null, body); node("td", String(row.published_rank), tr);
      attachObjectLink(row.entity_id, entityById, node("td", null, tr));
      node("td", `≈${formatNumber(row.published_length_km)} km`, tr);
      const scope = node("td", row.scope || "Scope not recorded", tr);
      scope.append(document.createTextNode(" · ")); sourceLink(row.length_source_id, sourceById, scope);
      const editorial = editorialByClaim.get(rankedMeasurementByEntity.get(row.entity_id)?.claim_id);
      if (editorial) renderEditorial(editorial, scope);
    }
  }
  function renderLengthInventory() {
    const query = byId("length-search").value.trim().toLocaleLowerCase();
    const statusLabel = {
      published_estimate: "Published estimate",
      derived_lower_bound: "OSW geographic floor",
      published_lower_bound: "Published lower bound",
      proposed_system_length: "Proposed system length",
      sampled_reach_only: "Sampled reach only",
      section_only: "Cross-stream section only",
      no_numeric_length: "No numeric length admitted",
    };
    const statusOrder = ["published_estimate", "derived_lower_bound", "published_lower_bound", "proposed_system_length", "sampled_reach_only", "section_only", "no_numeric_length"];
    const numericValue = row => row.published_length_km ?? row.lower_bound_km ?? row.proposed_system_length_km ?? -1;
    const rows = data.length_assessments.filter(row => {
      const label = entityById.get(row.entity_id)?.label || row.entity_id;
      return !query || `${label} ${row.entity_id} ${statusLabel[row.evidence_status] || row.evidence_status}`.toLocaleLowerCase().includes(query);
    }).sort((a, b) => statusOrder.indexOf(a.evidence_status) - statusOrder.indexOf(b.evidence_status) ||
      numericValue(b) - numericValue(a) ||
      (entityById.get(a.entity_id)?.label || a.entity_id).localeCompare(entityById.get(b.entity_id)?.label || b.entity_id));
    const body = byId("length-inventory-rows"); body.replaceChildren();
    for (const row of rows) {
      const tr = node("tr", null, body);
      attachObjectLink(row.entity_id, entityById, node("td", null, tr));
      node("td", statusLabel[row.evidence_status] || row.evidence_status.replaceAll("_", " "), tr);
      const amount = row.published_length_km != null ? `≈${formatNumber(row.published_length_km)} km · ranked ${row.published_rank}` :
        row.lower_bound_km != null ? `≥${formatNumber(row.lower_bound_km)} km · unranked` :
        row.proposed_system_length_km != null ? `≈${formatNumber(row.proposed_system_length_km)} km · hypothesis, unranked` : "No whole-current number admitted";
      node("td", amount, tr);
      const scope = node("td", row.scope || "Scope not recorded", tr);
      const scenario = row.gate_distance_sensitivity;
      if (scenario) {
        const rank = scenario.geographic_span_rank_best === scenario.geographic_span_rank_worst ?
          String(scenario.geographic_span_rank_best) :
          `${scenario.geographic_span_rank_best}–${scenario.geographic_span_rank_worst}`;
        node("p", `Geographic span sensitivity: ${formatNumber(scenario.scenario_min_km)}–${formatNumber(scenario.scenario_max_km)} km in ±${scenario.perturbation_degrees}° gate scenarios. Possible position ${rank} of ${scenario.geographic_span_rank_count} geographic spans. This is an editorial scenario, not a current-length rank or confidence interval.`, scope);
      }
      if (row.length_source_id) { scope.append(document.createTextNode(" · ")); sourceLink(row.length_source_id, sourceById, scope); }
      const editorial = editorialByClaim.get(rankedMeasurementByEntity.get(row.entity_id)?.claim_id);
      if (editorial) renderEditorial(editorial, scope);
    }
    byId("length-inventory-count").textContent = `${rows.length} of ${data.length_assessments.length} named-current records`;
  }
  function renderState() {
    const id = byId("state-select").value;
    const body = byId("state-body"); body.replaceChildren();
    if (!id) { byId("state-status").textContent = "No state selected."; node("p", "Choose a state to see its source-set relations and movie views.", body); return; }
    const state = entityById.get(id); node("h3", state.label, body);
    byId("state-status").textContent = `Opened ${state.label} state passport. Evidence groups follow below.`;
    node("p", `${state.id} · approximate atlas region. These relations do not establish a whole-current path through the state.`, body);
    const packetPath = data["entity-packets-index"][id];
    if (packetPath) {
      const packet = link("Download this state's records and evidence (JSON review copy)", `data/${packetPath}`, body);
      packet.download = packetPath.split("/").pop();
    }
    const currents = data.entities.filter(row => row.type === "named_current");
    const currentRows = data.relations.filter(row => row.object_id === id && row.subject_id.startsWith("current:"));
    const associated = currentRows.filter(row => row.evidence_class !== "unresolved");
    const unresolvedCurrents = currentRows.filter(row => row.evidence_class === "unresolved");
    const missing = currents.length - new Set(currentRows.map(row => row.subject_id)).size;
    const eddyRows = data.named_eddy_state_assessments.filter(row => row.state_id === id);
    const candidates = eddyRows.filter(row => row.evidence_status !== "unresolved");
    const footprintCandidates = data.named_eddy_footprint_candidates.filter(row => row.state_assessments.some(item => item.state_id === id));
    const cropRows = data.tile_state_relations.filter(row => row.state_id === id).sort((a, b) => b.display_coverage_fraction - a.display_coverage_fraction);
    const distinct = (rows, key) => new Set(rows.map(row => row[key])).size;
    const datedEddies = candidates.filter(row => row.observed_center_date || row.figure_observation_dates?.length || row.dated_ssh_contour_observation_date);
    const overview = node("section", null, body); overview.className = "state-evidence-overview";
    node("h4", "Evidence available for this state", overview);
    node("p", "Counts are distinct objects within each group; an object can appear in more than one group. Zero means no retained evidence in this screened source set, not physical absence.", overview);
    const table = node("table", null, overview);
    node("caption", "State evidence overview", table);
    const head = node("tr", null, node("thead", null, table));
    for (const label of ["Evidence", "Objects", "What it establishes"]) { const th = node("th", label, head); th.scope = "col"; }
    const rowsBody = node("tbody", null, table);
    const summaries = [
      ["Source-reported local current presence", distinct(associated.filter(row => row.evidence_class === "source_associated"), "subject_id"), "Presence at the reported locality and dates; whole-current passage unresolved."],
      ["Schematic or cartographic current crossings", distinct(associated.filter(row => row.evidence_class === "atlas_geometry" && row.predicate !== "editorial_locator_candidate"), "subject_id"), "A drawn path crosses the atlas region; physical passage unresolved."],
      ["Editorial current locators", distinct(associated.filter(row => row.predicate === "editorial_locator_candidate"), "subject_id"), "An approximate atlas location; physical passage unresolved."],
      ["Dated named-eddy evidence", distinct(datedEddies, "eddy_id"), "A reported center or dated figure candidate; whole-eddy containment unresolved."],
      ["Undated named-eddy locators", distinct(candidates.filter(row => !datedEddies.includes(row)), "eddy_id"), "A point or region associated with the name; dated intersection unresolved."],
      ["Dated figure-footprint candidates", distinct(footprintCandidates, "entity_id"), "A figure-derived contour proxy; inspect its intersection sensitivity and limits below."],
      ["NASA regional movie crops", distinct(cropRows, "tile_id"), "Display overlap for navigation; event identity unresolved."],
    ];
    for (const [label, count, meaning] of summaries) {
      const tr = node("tr", null, rowsBody);
      const th = node("th", label, tr); th.scope = "row";
      node("td", String(count), tr); node("td", meaning, tr);
    }
    node("p", `${associated.length} source-linked or atlas-geometry current relation rows; ${currentRows.length - associated.length} unresolved rows; ${missing} current records excluded or unassessed for this state. Atlas geometry includes editorial locators and does not prove physical passage.`, body);
    const claimById = new Map(data.claims.map(row => [row.id, row]));
    const currentGroups = [
      ["Source-reported local presence", associated.filter(row => row.evidence_class === "source_associated")],
      ["Schematic or cartographic crossings", associated.filter(row => row.evidence_class === "atlas_geometry" && row.predicate !== "editorial_locator_candidate")],
      ["Editorial locator candidates", associated.filter(row => row.predicate === "editorial_locator_candidate")],
      ["Unresolved physical crossings", unresolvedCurrents],
    ];
    for (const [heading, rows] of currentGroups) {
      const details = node("details", null, body);
      node("summary", `${heading}: ${rows.length}`, details);
      if (!rows.length) { node("p", "No rows in this evidence group.", details); continue; }
      const list = node("ul", null, details);
      for (const row of rows.sort((a, b) => (entityById.get(a.subject_id)?.label || a.subject_id).localeCompare(entityById.get(b.subject_id)?.label || b.subject_id))) {
        const entry = node("li", `${row.predicate.replaceAll("_", " ")} · `, list);
        attachObjectLink(row.subject_id, entityById, entry);
        if (row.evidence_class === "source_associated") {
          const date = row.observation_start === row.observation_end ? row.observation_start : `${row.observation_start} to ${row.observation_end}`;
          node("span", ` · ${date} · ${row.reported_locality || "reported locality"} · local observation; whole-current path unresolved · `, entry);
          sourceLink(row.source_id, sourceById, entry);
        }
        const claim = claimById.get(row.claim_id);
        const evidence = node("details", null, entry); evidence.className = "state-relation-evidence";
        node("summary", "Source and method", evidence);
        const citation = node("p", "Source: ", evidence); sourceLink(row.source_id, sourceById, citation);
        node("p", `Evidence: ${row.evidence_class.replaceAll("_", " ")} · ${row.predicate.replaceAll("_", " ")}`, evidence);
        if (claim?.source_locator) node("p", `Source locator: ${claim.source_locator}`, evidence);
        node("p", `Method: ${claim?.method || "Method not supplied; inspect the downloaded evidence records."}`, evidence);
        node("p", `Scientific claim review: ${(claim?.review_status || "unresolved").replaceAll("_", " ")}.`, evidence);
      }
    }
    for (const candidate of footprintCandidates) {
      const card = node("section", null, body);
      attachObjectLink(candidate.entity_id, entityById, card);
      renderOceanFootprintCandidate({parent: card, candidate,
        geometry: data.geometries.find(row => row.id === candidate.geometry_id),
        movieContexts: data.footprint_movie_context.filter(row => row.footprint_candidate_id === candidate.id),
        entityLink: (target, parent) => link(entityById.get(target).label, stateHref(target), parent),
        sourceLink: (source, parent) => sourceLink(source, sourceById, parent)});
    }
    node("p", `${eddyRows.length} named-eddy/state assessments; ${candidates.length} have source-specific location evidence. Verified whole-eddy footprint intersections: 0.`, body);
    if (candidates.length) {
      const details = node("details", null, body); node("summary", "Inspect named-eddy locator candidates", details);
      const list = node("ul", null, details);
      for (const row of candidates) {
        const entry = node("li", `${row.evidence_status.replaceAll("_", " ")} · `, list);
        attachObjectLink(row.eddy_id, entityById, entry);
        if (row.observed_center_date) node("span", ` · reported center ${row.observed_center_date}; point only, whole eddy unresolved`, entry);
        else if (row.figure_observation_dates?.length) node("span", ` · dated figure ${row.figure_observation_dates.join(", ")}; whole eddy unresolved`, entry);
        if (row.source_locator) { node("span", " · ", entry); sourceLink(row.source_id, sourceById, entry); }
      }
    }
    const unresolvedEddies = eddyRows.filter(row => row.evidence_status === "unresolved");
    const unresolvedDetails = node("details", null, body);
    node("summary", `Named eddies with unresolved state intersection: ${unresolvedEddies.length}`, unresolvedDetails);
    const unresolvedList = node("ul", null, unresolvedDetails);
    for (const row of unresolvedEddies.sort((a, b) => (entityById.get(a.eddy_id)?.label || a.eddy_id).localeCompare(entityById.get(b.eddy_id)?.label || b.eddy_id))) attachObjectLink(row.eddy_id, entityById, node("li", null, unresolvedList));
    node("p", `${cropRows.length} NASA regional crop display overlaps. Overlap is a map-navigation result, not a physical state crossing.`, body);
    if (cropRows.length) {
      const details = node("details", null, body); node("summary", "Open NASA crops for this state", details);
      const list = node("ul", null, details);
      const tileById = new Map(data.tiles.map(row => [row.tile_id, row]));
      for (const row of cropRows) {
        const tile = tileById.get(row.tile_id);
        if (!tile) continue;
        const entry = node("li", `${row.tile_id} · ${formatNumber(row.display_coverage_fraction * 100)}% display overlap · `, list);
        link("Watch at NASA", tile.url, entry, true);
      }
    }
    link("Download relation table (CSV)", "data/relations.csv", body);
  }
  function renderMovies() {
    const query = byId("movie-search").value.trim().toLocaleLowerCase();
    const body = byId("movie-rows"); body.replaceChildren();
    const byTile = new Map(data.tiles.map(row => [row.tile_id, []]));
    for (const row of data.media) if (row.tile_id && byTile.has(row.tile_id)) byTile.get(row.tile_id).push(row);
    for (const row of data.footprint_movie_context) if (byTile.has(row.tile_id)) byTile.get(row.tile_id).push(row);
    const visible = data.tiles.filter(tile => !query || tile.tile_id.toLocaleLowerCase().includes(query) ||
      byTile.get(tile.tile_id).some(row => entityById.get(row.entity_id)?.label.toLocaleLowerCase().includes(query)));
    for (const tile of visible) {
      const tr = node("tr", null, body); node("td", `${tile.tile_id} · level ${tile.zoom}`, tr);
      link("Watch at NASA", tile.url, node("td", null, tr), true);
      const cell = node("td", null, tr);
      const ids = [...new Set(byTile.get(tile.tile_id).map(row => row.entity_id))];
      if (!ids.length) node("span", "No linked object in screened set", cell);
      else {
        const details = node("details", null, cell); node("summary", `${ids.length} geographic links`, details);
        const list = node("ul", null, details);
        for (const id of ids.sort((a, b) => (entityById.get(a)?.label || a).localeCompare(entityById.get(b)?.label || b))) {
          const entry = node("li", null, list); attachObjectLink(id, entityById, entry);
          const context = byTile.get(tile.tile_id).find(row => row.entity_id === id && row.footprint_candidate_id);
          if (context) node("span", ` · figure-footprint geographic context · ${context.observation_date} · movie ${context.movie_model_period} · ${context.temporal_alignment_status.replaceAll("_", " ")} · event identity not established`, entry);
        }
      }
    }
    byId("movie-count").textContent = `${visible.length} of ${data.tiles.length} NASA crops`;
  }
  Promise.all(collections.map(load)).then(values => {
    data = Object.fromEntries(collections.map((name, index) => [name, values[index]]));
    entityById = new Map(data.entities.map(row => [row.id, row]));
    sourceById = new Map(data.sources.map(row => [row.id, row]));
    lengthByEntity = new Map(data.length_assessments.map(row => [row.entity_id, row]));
    rankedMeasurementByEntity = new Map(data.measurements.filter(row => row.rank_eligible).map(row => [row.entity_id, row]));
    editorialByClaim = new Map(data["ranked-length-editorial-reviews"].entries.map(row => [row.claim_id, row]));
    mediaByEntity = new Map();
    for (const row of data.media) { if (!mediaByEntity.has(row.entity_id)) mediaByEntity.set(row.entity_id, []); mediaByEntity.get(row.entity_id).push(row); }
    const counts = Object.fromEntries(["named_current", "named_eddy", "nasa_described_motion", "osw_state"].map(type => [type, data.entities.filter(row => row.type === type).length]));
    byId("coverage").textContent = `${counts.named_current} named currents · ${counts.named_eddy} named eddies · ${counts.nasa_described_motion} NASA-described motion records · ${counts.osw_state} OSW states · ${data.tiles.length} NASA crop links.`;
    renderDirectory(); renderLengths(); renderLengthInventory(); renderMovies();
    for (const state of data.entities.filter(row => row.type === "osw_state").sort((a, b) => a.label.localeCompare(b.label))) {
      const option = node("option", state.label, byId("state-select")); option.value = state.id;
    }
    byId("search").addEventListener("input", renderDirectory);
    byId("kind").addEventListener("change", renderDirectory);
    byId("length-search").addEventListener("input", renderLengthInventory);
    byId("movie-search").addEventListener("input", renderMovies);
    byId("state-select").addEventListener("change", () => { const state = byId("state-select").value; history.pushState({ state }, "", state ? stateHref(state) : location.pathname + "#states"); renderState(); });
    const params = new URLSearchParams(location.search);
    const initial = params.get("id"); if (initial) renderRecord(initial);
    const initialState = params.get("state"); if (initialState) { byId("state-select").value = initialState; renderState(); }
    addEventListener("popstate", () => { const params = new URLSearchParams(location.search); const id = params.get("id"); if (id) renderRecord(id); byId("state-select").value = params.get("state") || ""; renderState(); });
  }).catch(error => {
    byId("coverage").textContent = "Data unavailable";
    byId("object-count").textContent = "Unavailable";
    byId("movie-count").textContent = "Unavailable";
    node("p", `Could not load the atlas data: ${error.message}`, byId("record-body"));
    console.error(error);
  });
})();
