"use strict";
window.oswIndexPageReady = false;

function cell(row, value) {
  const td = document.createElement("td");
  td.textContent = value;
  row.append(td);
  return td;
}

function sourceCell(row, label, href) {
  const td = document.createElement("td");
  const link = document.createElement("a");
  link.href = href;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = label;
  td.append(link);
  row.append(td);
}

async function loadJson(path) {
  return window.oswIndexDocument(path);
}

function facetLabel(value) {
  return value.replaceAll("_", " ");
}

function locatorPosition([longitude, latitude]) {
  return window.oswIndexCartography({op: "project", coordinates: [longitude, latitude]}).point;
}

function renderGulfStreamFrontMap(view) {
  const layer = document.querySelector("#gulf-stream-fronts");
  const namespace = "http://www.w3.org/2000/svg";
  for (const {side, path: geometry} of view.fronts) {
    const path = document.createElementNS(namespace, "path");
    path.setAttribute("class", side);
    path.setAttribute("d", geometry);
    layer.append(path);
  }
  const toggle = document.querySelector("#show-gulf-stream-fronts");
  const update = () => { layer.style.display = toggle.checked ? "" : "none"; };
  toggle.addEventListener("change", update);
  update();
}

function renderGeostrophicPathMap(view) {
  const layer = document.querySelector("#geostrophic-streamline");
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", view.diagnosed_path);
  layer.append(path);
  document.querySelector("#geostrophic-reach-length").textContent = `≈${Math.round(view.diagnosed_length_km).toLocaleString()} km`;
  const toggle = document.querySelector("#show-geostrophic-streamline");
  const update = () => { layer.style.display = toggle.checked ? "" : "none"; };
  toggle.addEventListener("change", update);
  update();
}

function renderOperationalEddyMap(view) {
  const layer = document.querySelector("#operational-eddy-polygons");
  const namespace = "http://www.w3.org/2000/svg";
  for (const {record: feature, path: geometry} of view.operational_polygons) {
    const path = document.createElementNS(namespace, "path");
    path.setAttribute("class", feature.provider_type.toLowerCase());
    path.setAttribute("d", geometry);
    const title = document.createElementNS(namespace, "title");
    title.textContent = `${feature.provider_code}, ${feature.provider_type.toLowerCase()} operational eddy polygon, ${view.operational_date}`;
    path.append(title);
    const detectionLink = document.createElementNS(namespace, "a");
    detectionLink.setAttribute("href", "object.html?id=" + encodeURIComponent(feature.id));
    detectionLink.setAttribute("aria-label", `Open dated NAVO detection ${feature.provider_code}, ${view.operational_date}`);
    detectionLink.append(path);
    layer.append(detectionLink);
  }
  const toggle = document.querySelector("#show-operational-eddy-polygons");
  const update = () => { layer.style.display = toggle.checked ? "" : "none"; };
  toggle.addEventListener("change", update);
  update();
}

function mapLink(row, label, markerId, nasaSceneUrl = null, nasaTileUrl = null, verticalSetting = null, nasaTileContextTitle = null) {
  const td = document.createElement("td");
  const link = document.createElement("a");
  link.href = "#motion-map-section";
  link.textContent = label;
  link.addEventListener("click", () => {
    document.querySelectorAll("#motion-markers .selected").forEach(marker => marker.classList.remove("selected"));
    document.querySelectorAll(`#motion-markers [data-record="${markerId}"]`).forEach(marker => marker.classList.add("selected"));
  });
  td.append(link);
  if (nasaTileUrl) {
    const tile = document.createElement("a");
    tile.href = nasaTileUrl;
    tile.target = "_blank";
    tile.rel = "noopener noreferrer";
    tile.textContent = verticalSetting === "subsurface_core" || verticalSetting === "deep_flow"
      ? "NASA region (depth unverified) ↗"
      : "NASA region video ↗";
    tile.className = "nasa-scene-link";
    tile.title = nasaTileContextTitle || (verticalSetting === "subsurface_core" || verticalSetting === "deep_flow"
      ? "NASA 4K model movie; large file. Geographic coverage does not establish that this subsurface current is visible at the relevant depth."
      : "NASA 4K model movie; large file. Regional coverage does not establish a named current boundary.");
    td.append(tile);
  }
  if (nasaSceneUrl) {
    const nasa = document.createElement("a");
    nasa.href = nasaSceneUrl;
    nasa.target = "_blank";
    nasa.rel = "noopener noreferrer";
    nasa.textContent = "NASA film ↗";
    nasa.className = "nasa-scene-link";
    td.append(nasa);
  }
  row.append(td);
}

function renderMap(view) {
  const svg = document.querySelector("#motion-markers"), namespace = "http://www.w3.org/2000/svg";
  for (const marker of view.markers) {
    const link = document.createElementNS(namespace, "a");
    link.setAttribute("href", marker.href); link.setAttribute("class", marker.class);
    link.setAttribute("data-record", marker.id); link.setAttribute("aria-label", marker.label);
    link.setAttribute("tabindex", "0");
    if (marker.kind === "current") link.addEventListener("click", event => window.oswNavigateIndexCurrent(event, marker.id));
    else if (marker.kind === "loop" || marker.kind === "geography") link.addEventListener("click", event => window.oswNavigateIndexEddy(event, marker.kind, marker.href));
    const title = document.createElementNS(namespace, "title"); title.textContent = marker.title;
    const circle = document.createElementNS(namespace, "circle");
    circle.setAttribute("cx", marker.point[0]); circle.setAttribute("cy", marker.point[1]); circle.setAttribute("r", marker.radius);
    link.append(title, circle); svg.append(link);
  }
  const count = view.counts;
  document.querySelector("#map-count").textContent = `${count.currents} currents · ${count.nasa_markers} NASA structures · ${count.loop_names} Loop eddy names (${count.published_loop_positions} published center points) · ${count.geography_names} other eddy names`;
}

async function renderCurrents() {
  const initial = await window.oswIndexCurrents({});
  const input = document.querySelector("#current-search");
  const setting = document.querySelector("#current-setting");
  const lengthStatus = document.querySelector("#current-length-status");
  const nasaStatus = document.querySelector("#current-nasa-status");
  for (const [status, definition] of Object.entries(initial.length_definitions)) {
    const option = document.createElement("option");
    option.value = status;
    option.textContent = `${facetLabel(status)} (${initial.length_counts[status]})`;
    option.title = definition;
    lengthStatus.append(option);
  }
  for (const [status, definition] of Object.entries(initial.nasa_definitions)) {
    const option = document.createElement("option");
    option.value = status;
    option.textContent = `${facetLabel(status)} (${initial.nasa_counts[status]})`;
    option.title = definition;
    nasaStatus.append(option);
  }
  for (const key of initial.settings) {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = facetLabel(key);
    setting.append(option);
  }
  const body = document.querySelector("#current-rows");
  const count = document.querySelector("#current-count");
  let serial = 0;
  async function draw() {
    const ticket = ++serial;
    const view = await window.oswIndexCurrents({text: input.value, setting: setting.value,
      length_status: lengthStatus.value, nasa_status: nasaStatus.value});
    if (ticket !== serial) return;
    window.oswIndexCurrentView = view;
    body.replaceChildren();
    for (const joined of view.rows) {
      const item = joined.record, classification = joined.classification;
      const row = document.createElement("tr");
      row.id = `current-${item.id}`;
      cell(row, joined.rank == null ? "—" : String(joined.rank));
      cell(row, item.name);
      cell(row, item.basin);
      const verticalSetting = classification.vertical_setting;
      const typeCell = cell(row, `${facetLabel(classification.identity_level)} · ${facetLabel(classification.setting)}${verticalSetting ? ` · ${facetLabel(verticalSetting)}` : ""}`);
      typeCell.title = `${item.kind}; ${view.taxonomy_axes.time_behavior[classification.time_behavior]}${verticalSetting ? ` ${view.taxonomy_axes.vertical_setting[verticalSetting]}` : ""}`;
      cell(row, item.length_km != null
        ? `≈ ${item.length_km.toLocaleString()} km`
        : item.hypothesized_length_km != null
          ? `≈ ${item.hypothesized_length_km.toLocaleString()} km · hypothesis · unranked`
          : item.length_lower_bound_km != null
            ? `${item.length_bound_basis ? "≥" : ">"} ${item.length_lower_bound_km.toLocaleString()} km · unranked`
            : "unranked");
      cell(row, item.length_scope);
      const observation = document.createElement("td");
      if (item.section_observation) {
        const section = item.section_observation;
        const link = document.createElement("a");
        link.href = view.sources[section.source];
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        const place = section.reference_place
          ? `${section.distance_from_coast_nautical_miles.join("–")} nmi off ${section.reference_place}`
          : section.latitude_range
            ? `${Math.abs(section.longitude)}°W, ${section.latitude_range.join("–")}°N`
            : `${section.latitude}°N, ${section.longitude_range.map(Math.abs).sort((a, b) => a - b).join("–")}°W`;
        const values = [place];
        if (section.meridional_width_km) values.push(`~${section.meridional_width_km} km across`);
        if (section.reference_place) {
          values.push("coastal hydrographic stations");
        } else if (section.transport_layers_sv) {
          values.push(`${section.transport_layers_sv.map(layer => `${layer.layer} ${layer.value} ± ${layer.uncertainty} Sv`).join("; ")} ${section.direction}`);
        } else values.push(`${section.transport_sv}${section.transport_uncertainty_sv ? ` ± ${section.transport_uncertainty_sv}` : ""} Sv ${section.direction}`);
        link.textContent = `${values.join(" · ")} ↗`;
        link.title = `${section.observed_period ? `${section.observed_period}. ` : ""}${section.method_note || "Source-reported section measurement."} This location does not determine whole-current length.`;
        observation.append(link);
      } else if (item.survey_section) {
        const section = item.survey_section;
        const link = document.createElement("a");
        link.href = view.sources[section.source];
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        const latitudeLabel = value => value < 0 ? `${Math.abs(value)}°S` : value > 0 ? `${value}°N` : "0°";
        const longitudeLabel = section.longitude < 0 ? `${Math.abs(section.longitude)}°W` : `${section.longitude}°E`;
        link.textContent = `${longitudeLabel}, ${section.latitude_range.map(latitudeLabel).join("–")} · ~${section.transport_sv_approx} Sv ${section.direction} ↗`;
        link.title = `${section.period}. Survey transport across a latitude section, not whole-current length.`;
        observation.append(link);
      } else if (item.sampled_reach) {
        const reach = item.sampled_reach;
        const link = document.createElement("a");
        link.href = view.sources[reach.source];
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = `~${reach.alongflow_km_approx.toLocaleString()} km sampled reach ↗`;
        link.title = `${reach.scope} This is not the whole-current length.`;
        observation.append(link);
      } else if (item.section_review_source) {
        const link = document.createElement("a");
        link.href = view.sources[item.section_review_source];
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "Section review ↗";
        link.title = "Source evidence on current identity; no whole-current length established.";
        observation.append(link);
      } else observation.textContent = "—";
      for (const variant of item.source_reported_length_variants || []) {
        if (observation.textContent === "—") observation.textContent = "";
        else if (observation.childNodes.length) observation.append(document.createTextNode(" · "));
        const link = document.createElement("a");
        link.href = view.sources[variant.source];
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = `≈${variant.length_km_approx.toLocaleString()} km source-specific scope ↗`;
        link.title = `${variant.scope} Not in the comparable whole-current ranking.`;
        observation.append(link);
      }
      if (item.identity_scope_note && item.identity_scope_source) {
        if (observation.textContent === "—") observation.textContent = "";
        else if (observation.childNodes.length) observation.append(document.createTextNode(" · "));
        const link = document.createElement("a");
        link.href = view.sources[item.identity_scope_source];
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "Identity scope review ↗";
        link.title = item.identity_scope_note;
        observation.append(link);
      }
      row.append(observation);
      const relations = document.createElement("td");
      for (const {id, name} of joined.linked_currents) {
        const link = document.createElement("a");
        link.href = `#current-${id}`;
        link.textContent = name;
        link.addEventListener("click", event => navigateCurrent(event, id));
        if (relations.childNodes.length) relations.append(document.createTextNode(" · "));
        relations.append(link);
      }
      if (joined.identity_related) {
        const {id, name} = joined.identity_related;
        const link = document.createElement("a");
        link.href = `#current-${id}`;
        link.textContent = `Name overlap: ${name}`;
        link.title = item.identity_review.note;
        link.addEventListener("click", event => navigateCurrent(event, id));
        if (relations.childNodes.length) relations.append(document.createTextNode(" · "));
        relations.append(link);
      }
      for (const {id, name} of joined.related_currents) {
        const link = document.createElement("a");
        link.href = `#current-${id}`;
        link.textContent = `Related: ${name}`;
        link.title = "A source-associated current; this relation does not establish a continuous measured path.";
        link.addEventListener("click", event => navigateCurrent(event, id));
        if (relations.childNodes.length) relations.append(document.createTextNode(" · "));
        relations.append(link);
      }
      for (const {id, upstream_feeder: upstreamFeeder} of joined.nasa_links) {
        const link = document.createElement("a");
        link.href = `#nasa-${id}`;
        link.textContent = upstreamFeeder ? "NASA named receiving flow ↗" : "NASA described turn ↗";
        link.title = upstreamFeeder ? "An independent oceanographic study identifies this current as a feeder of the NASA-named flow. NASA does not identify this feeder by name." : "NASA describes this turn; the downstream current name comes from an independent oceanographic source.";
        link.addEventListener("click", () => {
          const nasaSearch = document.querySelector("#nasa-search");
          if (nasaSearch.value) {
            nasaSearch.value = "";
            nasaSearch.dispatchEvent(new Event("input"));
          }
        });
        if (relations.childNodes.length) relations.append(document.createTextNode(" · "));
        relations.append(link);
      }
      if (joined.scene_url) {
        const nasaLink = document.createElement("a");
        nasaLink.href = `#nasa-${item.id}`;
        nasaLink.textContent = "NASA object record ↗";
        nasaLink.addEventListener("click", () => {
          const nasaSearch = document.querySelector("#nasa-search");
          if (nasaSearch.value) {
            nasaSearch.value = "";
            nasaSearch.dispatchEvent(new Event("input"));
          }
        });
        if (relations.childNodes.length) relations.append(document.createTextNode(" · "));
        relations.append(nasaLink);
      }
      if (!relations.childNodes.length) relations.textContent = "—";
      row.append(relations);
      const nasaRelation = joined.nasa_relation;
      const nasaCell = cell(row, nasaRelation.status === "nasa_named_or_described" ? "NASA named or described" : nasaRelation.status === "independent_context" ? "Independently linked to NASA flow" : "Regional crop only");
      nasaCell.title = view.nasa_definitions[nasaRelation.status];
      const sourceKey = item.length_source || item.hypothesis_source;
      sourceCell(row, item.hypothesis_source ? "Published hypothesis" : item.length_bound_basis ? "Inferred lower bound" : item.length_lower_bound_km != null ? "Published lower bound" : item.length_source ? "Published estimate" : "Name source", sourceKey ? view.sources[sourceKey] : item.name_source_url || view.sources[item.name_source]);
      mapLink(row, "Locate ↗", item.id, joined.scene_url, joined.crop_url, verticalSetting);
      body.append(row);
    }
    count.textContent = `${body.children.length} of ${view.total} names · ${view.length_counts.published_estimate} ranked estimates · ${view.length_counts.derived_lower_bound + view.length_counts.published_lower_bound} unranked bounds`;
  }
  function report(error) {
    count.textContent = `Current query unavailable: ${error.message}`;
    console.error(error);
  }
  async function navigateCurrent(event, id) {
    event.preventDefault();
    input.value = ""; setting.value = "all";
    lengthStatus.value = "all"; nasaStatus.value = "all";
    try {
      await draw();
      const target = document.getElementById(`current-${id}`);
      if (target) { location.hash = target.id; target.scrollIntoView({block: "center"}); }
    } catch (error) { report(error); }
  }
  window.oswNavigateIndexCurrent = navigateCurrent;
  const redraw = () => { draw().catch(report); };
  input.addEventListener("input", redraw);
  setting.addEventListener("change", redraw);
  lengthStatus.addEventListener("change", redraw);
  nasaStatus.addEventListener("change", redraw);
  await draw();
}

async function renderIllustratedSpans() {
  const view = await window.oswIndexSupport({section: "illustrated_spans"});
  window.oswIndexIllustratedSpansView = view;
  const body = document.querySelector("#illustrated-span-rows");
  for (const joined of view.rows) {
    const item = joined.record;
    const row = document.createElement("tr");
    cell(row, String(item.illustrated_span_rank));
    const name = document.createElement("td");
    const link = document.createElement("a");
    link.href = `#current-${item.current_id}`;
    link.textContent = item.name;
    link.addEventListener("click", event => window.oswNavigateIndexCurrent(event, item.current_id));
    name.append(link);
    row.append(name);
    const span = cell(row, `≈ ${item.longest_arrow_span_km.toLocaleString()} km`);
    span.title = item.scope_note;
    cell(row, `${item.arrows[0].source_arrow_id} / ${item.source_arrow_count}`);
    const published = joined.current.length_km;
    cell(row, published == null ? "—" : `≈ ${published.toLocaleString()} km`);
    body.append(row);
  }
}

function formatTime(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

async function renderNasaObjects() {
  const body = document.querySelector("#nasa-rows");
  const input = document.querySelector("#nasa-search");
  const initial = await window.oswIndexNasa({});
  document.querySelector("#nasa-evidence-count").textContent = String(initial.release_evidence_count);
  let serial = 0;
  async function draw() {
    const ticket = ++serial;
    const view = await window.oswIndexNasa({text: input.value});
    if (ticket !== serial) return;
    window.oswIndexNasaView = view;
    body.replaceChildren();
    for (const joined of view.rows) {
      const item = joined.record, form = joined.form;
      const row = document.createElement("tr");
      row.id = `nasa-${item.id}`;
      const name = cell(row, item.name);
      name.title = item.description;
      const support = cell(row, facetLabel(item.support));
      const formLabel = document.createElement("small");
      formLabel.textContent = ` · ${form.replaceAll("_", " ")}`;
      formLabel.title = view.form_definitions[form];
      support.append(formLabel);
      const oswCell = document.createElement("td");
      if (item.almanac_current_id || item.atlas_feature_id) {
        const target = item.almanac_current_id ? `#current-${item.almanac_current_id}` : `../atlas/?feature=${item.atlas_feature_id}&lens=flows`;
        const link = document.createElement("a");
        link.href = target;
        link.textContent = item.almanac_current_id ? "Current ledger ↗" : "Atlas feature ↗";
        oswCell.append(link);
        if (item.almanac_current_id && item.atlas_feature_id) {
          const atlasLink = document.createElement("a");
          atlasLink.href = `../atlas/?feature=${item.atlas_feature_id}&lens=flows`;
          atlasLink.textContent = "Atlas feature ↗";
          oswCell.append(document.createTextNode(" · "), atlasLink);
        }
      } else if (item.parent_id) {
        const parent = joined.parent;
        const parentLink = document.createElement("a");
        parentLink.href = `#nasa-${item.parent_id}`;
        parentLink.textContent = `Parent: ${parent.name} ↗`;

        oswCell.append(parentLink);
        const parentCurrentId = joined.crosswalk.parent_current_id;
        if (parentCurrentId) {
          const currentLink = document.createElement("a");
          currentLink.href = `#current-${parentCurrentId}`;
          currentLink.textContent = "Parent current ↗";
          oswCell.append(document.createTextNode(" · "), currentLink);
        }
      } else oswCell.textContent = "Class / system";
      if (item.related_current_system_id) {
        const systemLink = document.createElement("a");
        systemLink.href = `#current-${item.related_current_system_id}`;
        systemLink.textContent = "Source-name system ↗";
        systemLink.title = item.name_scope_note;
        oswCell.append(document.createElement("br"), systemLink);
        const scopeNote = document.createElement("small");
        scopeNote.textContent = item.name_scope_note;
        oswCell.append(document.createElement("br"), scopeNote);
      }
      for (const {relation: context, record: current} of joined.external_currents) {
        const currentLink = document.createElement("a");
        currentLink.href = `#current-${context.current_id}`;
        currentLink.textContent = `Independently named: ${current.name} ↗`;
        currentLink.title = context.note;
        if (oswCell.childNodes.length) oswCell.append(document.createTextNode(" · "));
        oswCell.append(currentLink);
      }
      for (const example of joined.examples) {
        const exampleId = example.id;
        const exampleLink = document.createElement("a");
        exampleLink.href = `#nasa-${exampleId}`;
        exampleLink.textContent = `Example: ${example.name} ↗`;
        exampleLink.title = joined.crosswalk.example_relation;

        if (oswCell.childNodes.length) oswCell.append(document.createTextNode(" · "));
        oswCell.append(exampleLink);
      }
      for (const {relation: context, record: system} of joined.systems) {
        const systemLink = document.createElement("a");
        systemLink.href = `#nasa-${context.system_id}`;
        systemLink.textContent = `System: ${system.name} ↗`;
        systemLink.title = `${context.note} NASA narration cues ${context.cue_numbers.join("–")}.`;

        if (oswCell.childNodes.length) oswCell.append(document.createTextNode(" · "));
        oswCell.append(systemLink);
      }
      const classParent = joined.crosswalk.class_parent;
      if (classParent) {
        const classLink = document.createElement("a");
        classLink.href = `#nasa-${classParent.parent_id}`;
        classLink.textContent = `Class: ${joined.class_parent.name} ↗`;
        classLink.title = view.class_relation_rule;

        if (oswCell.childNodes.length) oswCell.append(document.createTextNode(" · "));
        oswCell.append(classLink);
      }
      for (const {relation: edge, record: child} of joined.class_children) {
        const childLink = document.createElement("a");
        childLink.href = `#nasa-${edge.child_id}`;
        childLink.textContent = `Subtype: ${child.name} ↗`;
        childLink.title = view.class_relation_rule;

        if (oswCell.childNodes.length) oswCell.append(document.createTextNode(" · "));
        oswCell.append(childLink);
      }
      const namedContext = joined.catalog.named_eddy_context;
      if (namedContext.length) {
        const details = document.createElement("details");
        const summary = document.createElement("summary");
        summary.textContent = `${namedContext.length} named eddy source records · context only`;
        summary.title = "These independently sourced names relate to a NASA-described class or flow. NASA does not identify any listed individual in its footage.";
        details.append(summary);
        const list = document.createElement("ul");
        for (const context of namedContext) {
          const listItem = document.createElement("li");
          const link = document.createElement("a");
          link.href = context.atlas_anchor;
          link.textContent = `${context.name} · ${context.source_event_date || context.event_year || facetLabel(context.identity_level)}`;
          link.title = `${context.relations.map(facetLabel).join(", ")}; ${facetLabel(context.locator_evidence_type || "unlocated")}; ${facetLabel(context.temporal_relation || "time_unresolved")}. Source: ${context.source_url}. No individual NASA identity claim.`;
          link.addEventListener("click", event => {
            if (context.source_collection === "published_loop_current") return;
            window.oswNavigateIndexEddy(event, context.source_collection === "horizon_loop_current" ? "loop" : "geography", link.hash);
          });
          listItem.append(link);
          list.append(listItem);
        }
        details.append(list);
        oswCell.append(details);
      }
      row.append(oswCell);
      const stateTd = document.createElement("td");
      const evidence = joined.crosswalk.state_evidence;
      for (const [kind, codes] of [
        ["mapped arrow", evidence.cartographic_current_crossings],
        ["map contact", evidence.width_sensitive_cartographic_contacts],
        ["atlas line", evidence.schematic_current_crossings],
        ["OSW gate", evidence.schematic_object_crossings],
        ["editorial line", evidence.editorial_current_line_crossings],
        ["locator", evidence.object_locator_candidates],
      ]) {
        for (const code of codes) {
          const stateLink = document.createElement("a");
          stateLink.href = `?state=${encodeURIComponent(code)}#state-title`;
          stateLink.textContent = `${code} ${kind} ↗`;
          stateLink.title = kind === "mapped arrow" ? "Independent cartographic current arrow crosses this OSW state at all four source widths; NASA did not segment this current's footprint." : kind === "locator" ? "Approximate object locator falls in this OSW state; this is not a footprint or containment claim." : "OSW map relation, not a NASA-segmented current footprint.";
          if (stateTd.childNodes.length) stateTd.append(document.createTextNode(", "));
          stateTd.append(stateLink);
        }
      }
      if (!stateTd.childNodes.length) stateTd.textContent = "No bounded state footprint";
      row.append(stateTd);
      const propertiesTd = document.createElement("td");
      for (const property of joined.crosswalk.reported_properties) {
        const link = document.createElement("a");
        link.href = property.source_url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = `${property.display} ↗`;
        link.title = property.scope_note;
        if (propertiesTd.childNodes.length) propertiesTd.append(document.createTextNode(" · "));
        propertiesTd.append(link);
        if (property.review_source_url) {
          const review = document.createElement("a");
          review.href = property.review_source_url;
          review.target = "_blank";
          review.rel = "noopener noreferrer";
          review.textContent = "Independent ring study ↗";
          review.title = property.review_note;
          propertiesTd.append(document.createTextNode(" · "), review);
        }
      }
      if (!propertiesTd.childNodes.length) propertiesTd.textContent = "—";
      row.append(propertiesTd);
      const sourceTd = document.createElement("td");
      for (const {record: source, evidence} of joined.releases) {
        const sourceLink = document.createElement("a");
        sourceLink.href = evidence.source_url;
        sourceLink.target = "_blank";
        sourceLink.rel = "noopener noreferrer";
        sourceLink.textContent = evidence.evidence_kind === "narration_cues" ? `${source.title} · cues ${evidence.cue_numbers[0]}–${evidence.cue_numbers.at(-1)}` : source.title;
        sourceLink.title = evidence.evidence_kind === "nasa_media_group" ? `NASA media group ${evidence.media_group_ids.join(", ")}` : "Exact cue numbers in NASA's published transcript.";
        if (sourceTd.childNodes.length) sourceTd.append(document.createTextNode(" · "));
        sourceTd.append(sourceLink);
        if (evidence.evidence_kind === "nasa_media_group") {
          for (let groupIndex = 1; groupIndex < evidence.media_group_urls.length; groupIndex += 1) {
            const groupLink = document.createElement("a");
            groupLink.href = evidence.media_group_urls[groupIndex];
            groupLink.target = "_blank";
            groupLink.rel = "noopener noreferrer";
            groupLink.textContent = ` source view ${groupIndex + 1} ↗`;
            groupLink.title = `NASA media group ${evidence.media_group_ids[groupIndex]} independently names or describes this object.`;
            sourceTd.append(document.createTextNode(" · "), groupLink);
          }
        }
      }
      if (item.nasa_still) {
        const still = document.createElement("a");
        still.href = item.nasa_still;
        still.target = "_blank";
        still.rel = "noopener noreferrer";
        still.textContent = " · 2011 still ↗";
        sourceTd.append(still);
      }
      if (item.narrated_start_s != null) {
        const time = document.createElement("a");
        time.href = joined.narrated_release.transcript;
        time.target = "_blank";
        time.rel = "noopener noreferrer";
        time.textContent = ` · transcript ${formatTime(item.narrated_start_s)}–${formatTime(item.narrated_end_s)} ↗`;
        sourceTd.append(time);
      }
      row.append(sourceTd);
      const movie = document.createElement("td");
      if (item.narrated_start_s != null) {
        const narrated = document.createElement("a");
        narrated.href = `${joined.narrated_release.timed_movie}#t=${item.narrated_start_s},${item.narrated_end_s}`;
        narrated.target = "_blank";
        narrated.rel = "noopener noreferrer";
        narrated.textContent = `Narrated ${formatTime(item.narrated_start_s)}–${formatTime(item.narrated_end_s)} ↗`;
        narrated.title = "Open NASA's narrated movie at this object or process; large video file.";
        movie.append(narrated);
      }
      const join = joined.crosswalk.regional_movie;
      if (join) {
        const link = document.createElement("a");
        link.href = join.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = `${join.tile_id} ↗`;
        link.title = "Large NASA regional 4K movie; the crop is a spatial match, not an object identification.";
        if (movie.childNodes.length) movie.append(document.createTextNode(" · "));
        movie.append(link);
      }
      for (const asset of joined.feature_media) {
        const mediaLink = document.createElement("a");
        mediaLink.href = asset.movie_url;
        mediaLink.target = "_blank";
        mediaLink.rel = "noopener noreferrer";
        mediaLink.textContent = `${asset.title} ↗`;
        mediaLink.title = asset.source_basis;
        if (movie.childNodes.length) movie.append(document.createTextNode(" · "));
        movie.append(mediaLink);
      }
      const overview = joined.crosswalk.source_overview_movie;
      if (overview) {
        const overviewLink = document.createElement("a");
        overviewLink.href = overview.url;
        overviewLink.target = "_blank";
        overviewLink.rel = "noopener noreferrer";
        overviewLink.textContent = "Source release overview ↗";
        overviewLink.title = "NASA discusses this class on the source release page. This full movie is context, not an identified individual ring or footprint.";
        if (movie.childNodes.length) movie.append(document.createTextNode(" · "));
        movie.append(overviewLink);
      }
      const cropEvidence = joined.cartographic_crops;
      if (cropEvidence?.cartographic_crop_contacts.length) {
        const details = document.createElement("details");
        const summary = document.createElement("summary");
        summary.textContent = `${cropEvidence.cartographic_crop_contacts.length} map-arrow crop regions`;
        summary.title = view.crop_claim_limit;
        details.append(summary);
        for (const contact of cropEvidence.cartographic_crop_contacts) {
          const link = document.createElement("a");
          link.href = contact.url;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          link.textContent = `${contact.tile_id}${contact.is_primary_locator_crop ? " (locator)" : ""} ↗`;
          link.title = `${contact.map_contact.replaceAll("_", " ")}; independent map arrows ${contact.source_arrow_ids.join(", ")}. ${view.crop_claim_limit}`;
          details.append(link, document.createElement("br"));
        }
        movie.append(details);
      }
      const variants = joined.variants;
      if (variants.length) {
        const details = document.createElement("details");
        const summary = document.createElement("summary");
        summary.textContent = `${variants.length} source-linked movie files`;
        summary.title = view.movie_variant_rule;
        details.append(summary);
        for (const {movie: variant, relation, release} of variants) {
          const link = document.createElement("a");
          link.href = relation.movie_url;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          link.textContent = `${release.title} · ${variant.width}×${variant.height} · ${variant.filename} ↗`;
          link.title = relation.relation === "narrated_bounded_clip" ? `NASA narrated cues ${relation.cue_numbers.join(", ")}; clip bounds are editorial navigation.` : `NASA media group ${variant.group_id} contains this object name or description.`;
          details.append(link, document.createElement("br"));
        }
        movie.append(details);
      }
      if (!movie.childNodes.length) movie.textContent = "No direct movie";
      row.append(movie);
      body.append(row);
    }
    document.querySelector("#nasa-count").textContent = `${body.children.length} of ${view.total} NASA motion records`;
  }
  const report = error => {document.querySelector("#nasa-count").textContent = `NASA query unavailable: ${error.message}`;};
  input.addEventListener("input", () => draw().catch(report));
  window.oswNavigateIndexNasa = async (event, hash) => {
    event.preventDefault(); input.value = "";
    try {
      await draw();
      const target = document.getElementById(hash.slice(1));
      if (target) {location.hash = hash; target.scrollIntoView({block: "center"});}
    } catch (error) {report(error);}
  };
  const targets = new Set(initial.rows.map(row => `#nasa-${row.record.id}`));
  document.addEventListener("click", event => {
    const link = event.target.closest("a");
    const hash = link?.getAttribute("href");
    if (!targets.has(hash)) return;
    event.stopPropagation();
    window.oswNavigateIndexNasa(event, hash);
  }, true);
  body.addEventListener("click", event => {
    const link = event.target.closest("a");
    const hash = link?.getAttribute("href");
    if (hash?.startsWith("#current-")) window.oswNavigateIndexCurrent(event, hash.slice(9));
  });
  await draw();
}

async function renderNasaReleaseMedia() {
  const view = await window.oswIndexReleaseMedia();
  window.oswIndexReleaseMediaView = view;
  const host = document.querySelector("#nasa-media-releases");
  host.replaceChildren();
  for (const joined of view.rows) {
    const release = joined.record;
    const details = document.createElement("details");
    details.className = "state-eddy-details";
    const summary = document.createElement("summary");
    summary.textContent = `${release.title} · ${joined.objects.length} identified records · ${release.movies.length} movie files`;
    details.append(summary);
    const source = document.createElement("p");
    const sourceLink = document.createElement("a");
    sourceLink.href = release.source_page;
    sourceLink.target = "_blank";
    sourceLink.rel = "noopener noreferrer";
    sourceLink.textContent = "NASA release page ↗";
    source.append(sourceLink);
    details.append(source);
    const sourceRecord = joined.source;
    const citation = document.createElement("p");
    citation.className = "source-review-note";
    citation.append(document.createTextNode(`Credit: ${sourceRecord.credit_text} · Citation: `));
    const citationText = document.createElement("cite");
    citationText.textContent = sourceRecord.preferred_citation;
    citation.append(citationText);
    details.append(citation);
    const objectHeading = document.createElement("h4");
    objectHeading.textContent = "Objects identified in this release";
    details.append(objectHeading);
    const objectList = document.createElement("ul");
    objectList.className = "nasa-release-objects";
    for (const {record: object, evidence} of joined.objects) {
      const objectId = object.id;
      const item = document.createElement("li");
      const objectLink = document.createElement("a");
      objectLink.href = `#nasa-${objectId}`;
      objectLink.textContent = `${object.name} ↗`;
      const evidenceLink = document.createElement("a");
      evidenceLink.href = evidence.source_url;
      evidenceLink.target = "_blank";
      evidenceLink.rel = "noopener noreferrer";
      evidenceLink.textContent = "NASA passage ↗";
      item.append(objectLink, document.createTextNode(" · "), evidenceLink);
      objectList.append(item);
    }
    if (!joined.objects.length) {
      const item = document.createElement("li");
      item.textContent = "No named or individually described motion object in this release's page text.";
      objectList.append(item);
    }
    details.append(objectList);
    const list = document.createElement("ul");
    for (const movie of release.movies) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = movie.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = `${movie.filename} ↗`;
      const context = movie.group_title || movie.group_description;
      if (context) link.title = context;
      item.append(link);
      if (movie.width && movie.height) item.append(document.createTextNode(` · ${movie.width}×${movie.height}`));
      list.append(item);
    }
    details.append(list);
    host.append(details);
  }
  document.querySelector("#nasa-media-count").textContent = `${view.release_count} releases · ${view.movie_listing_count} movie files`;
}

function stateLinks(ids, lookup, prefix, fallback) {
  const list = document.createElement("ul");
  for (const id of ids) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = `#${prefix}-${id}`;
    link.textContent = lookup[id]?.name || id.replaceAll("-", " ");
    if (prefix === "current") link.addEventListener("click", event => window.oswNavigateIndexCurrent(event, id));
    if (prefix === "nasa") link.addEventListener("click", () => {
      const search = document.querySelector("#nasa-search");
      search.value = "";
      search.dispatchEvent(new Event("input"));
    });
    if (prefix === "eddy-geography") link.addEventListener("click", event => window.oswNavigateIndexEddy(event, "geography", link.hash));
    if (prefix === "eddy") link.addEventListener("click", event => window.oswNavigateIndexEddy(event, "loop", link.hash));
    item.append(link);
    list.append(item);
  }
  if (!ids.length) {
    const item = document.createElement("li");
    item.textContent = fallback;
    list.append(item);
  }
  return list;
}

function stateMembershipLinks(members, prefix, fallback) {
  const list = document.createElement("ul");
  for (const member of members) {
    const item = document.createElement("li"), link = document.createElement("a");
    link.href = `#${prefix}-${member.id}`; link.textContent = member.name;
    if (prefix === "current") link.addEventListener("click", event => window.oswNavigateIndexCurrent(event, member.id));
    if (prefix === "eddy-geography") link.addEventListener("click", event => window.oswNavigateIndexEddy(event, "geography", link.hash));
    if (prefix === "eddy") link.addEventListener("click", event => window.oswNavigateIndexEddy(event, "loop", link.hash));
    item.append(link); list.append(item);
  }
  if (!members.length) {const item = document.createElement("li"); item.textContent = fallback; list.append(item);}
  return list;
}

async function renderStates(seasonalManifest) {
  const select = document.querySelector("#state-select");
  const dateSelect = document.querySelector("#eddy-date-select");
  const result = document.querySelector("#state-result");
  const showEddies = document.querySelector("#show-state-eddies");
  const eddyLayer = document.querySelector("#detected-eddy-markers");
  const trackLayer = document.querySelector("#selected-eddy-track");
  const trackSummary = document.querySelector("#selected-track-summary");
  for (const snapshot of [...seasonalManifest.snapshots].reverse()) {
    const option = document.createElement("option");
    option.value = snapshot.date;
    option.textContent = `${snapshot.date} · ${snapshot.detection_count.toLocaleString()} detections${snapshot.weekly_track_join ? " · 7-day tracks" : ""}`;
    dateSelect.append(option);
  }
  dateSelect.value = "2023-06-01";
  let selectedDate = dateSelect.value;
  let paintedNoaa = null, trackSerial = 0;
  async function showTrack(id, focusDate, sourceDate, stateCode) {
    const ticket = ++trackSerial;
    try {
      const view = await window.oswIndexNoaaTrack({date: sourceDate, state_code: stateCode, detection_id: id, focus_date: focusDate});
      if (ticket !== trackSerial || paintedNoaa?.date !== sourceDate || paintedNoaa?.state_code !== stateCode) return;
      window.oswIndexNoaaTrackView = view;
      trackLayer.replaceChildren();
      const namespace = "http://www.w3.org/2000/svg";
      const path = document.createElementNS(namespace, "path");
      path.setAttribute("d", view.path); trackLayer.append(path);
      for (const [x, y] of [view.points[0], view.points.at(-1)]) {
        const marker = document.createElementNS(namespace, "circle");
        marker.setAttribute("cx", x); marker.setAttribute("cy", y); marker.setAttribute("r", "7"); trackLayer.append(marker);
      }
      const record = view.record;
      trackSummary.textContent = `${id}: ${record.positions.length} NOAA daily centers, ${record.positions[0].date} to ${record.positions.at(-1).date}. ${record.file_scoped_track_ref} is only an address within this seven-day file; it is not a NASA or named-ring identity.`;
      if (view.movie_context) {
        const movie = view.movie_context, link = document.createElement("a");
        link.href = `${movie.tile.url}#t=${movie.seek.estimated_crop_seconds}`;
        link.target = "_blank"; link.rel = "noopener noreferrer";
        link.textContent = `NASA regional view near ${movie.date} ↗`; link.title = movie.scope;
        trackSummary.append(document.createTextNode(" "), link);
      }
      document.querySelector("#motion-map-section").scrollIntoView({behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start"});
    } catch (error) { if (ticket === trackSerial) trackSummary.textContent = `Weekly path unavailable: ${error.message}`; }
  }
  function drawEddyMap() {
    eddyLayer.replaceChildren();
    if (!paintedNoaa || !showEddies.checked) return;
    const namespace = "http://www.w3.org/2000/svg";
    for (const group of paintedNoaa.groups) for (const row of group.rows) {
      if (!row.point) continue;
      const [x,y] = row.point, status = group.status === "intersected" ? "intersecting" : group.status;
      const circle = document.createElementNS(namespace, "circle");
      circle.setAttribute("cx", x); circle.setAttribute("cy", y); circle.setAttribute("r", "3.7");
      circle.setAttribute("class", `${row.record.polarity} ${status}`);
      const title = document.createElementNS(namespace, "title");
      title.textContent = `${row.id} · ${row.record.polarity} · ${status} in ${paintedNoaa.state_code} on ${paintedNoaa.date}`;
      circle.append(title); eddyLayer.append(circle);
    }
  }
  const metadata = await window.oswIndexStateMemberships({});
  const memberships = new Map(), contexts = new Map(), noaaViews = new Map();
  let serial = 0;
  for (const {code, name} of metadata.states) {
    const option = document.createElement("option");
    option.value = code; option.textContent = `${code} · ${name}`; select.append(option);
  }
  async function draw() {
    const code = select.value, date = selectedDate, ticket = ++serial;
    let membership = null, contextResult = null, context = null, noaa = null;
    if (code) {
      if (!memberships.has(code)) memberships.set(code, (await window.oswIndexStateMemberships({state_code: code})).views[0]);
      membership = memberships.get(code);
      const key = `${code}:${date}`;
      if (!contexts.has(key)) contexts.set(key, await window.oswIndexStateContext({state_code: code, date}));
      contextResult = contexts.get(key); context = contextResult.views[0];
      if (!noaaViews.has(key)) noaaViews.set(key, await window.oswIndexNoaaState({state_code: code, date}));
      noaa = noaaViews.get(key);
    }
    if (ticket !== serial) return;
    window.oswIndexStateMembershipView = membership;
    window.oswIndexStateContextView = contextResult;
    window.oswIndexNoaaStateView = paintedNoaa = noaa;
    ++trackSerial;
    trackLayer.replaceChildren();
    trackSummary.textContent = noaa?.weekly ? "Choose a state's detected eddy to see its NOAA weekly center path." : "Seven-day NOAA tracks are available for the June sample dates only.";
    drawEddyMap();
    result.replaceChildren();
    if (!code) {
      const message = document.createElement("p");
      message.textContent = "Choose a state to inspect its motion evidence.";
      result.append(message);
      document.querySelector("#state-count").textContent = `${metadata.state_count} states`;
      const url = new URL(window.location.href); url.searchParams.delete("state"); history.replaceState(null, "", url);
      return;
    }
    const state = membership.state;
    const heading = document.createElement("h3");
    heading.textContent = `${code} · ${state.name}`;
    const atlas = document.createElement("a");
    atlas.href = `../atlas/?province=${code}&lens=flows`;
    atlas.textContent = "Open this state in Atlas 10 ↗";
    result.append(heading, atlas);
    const currentSummary = document.createElement("p");
    currentSummary.className = "state-warning";
    currentSummary.textContent = `${membership.atlas_linked_current_count} of ${membership.current_count} named currents have atlas evidence here. The remaining current/state pairs are unresolved; map arrows, sketches, and locators do not establish observed flow footprints.`;
    result.append(currentSummary);
    const routeSection = document.createElement("section");
    routeSection.className = "state-reference-routes";
    const routeHeading = document.createElement("h4");
    routeHeading.textContent = "Reference routes through this diagram state";
    routeSection.append(routeHeading);
    const routeState = context.reference_routes;
    const routeSummary = document.createElement("p");
    routeSummary.textContent = routeState
      ? `${routeState.current_count} named currents have a crossing in at least one declared route scenario; ${routeState.nominal_current_count} cross in a nominal route. These are editorial line crossings, not observed current passage or eddy containment. Scenario counts are sensitivity cases, not probabilities or seasonal frequency.`
      : "Reference-route state inventory unavailable. Existing state evidence remains available below.";
    routeSection.append(routeSummary);
    if (routeState) {
      const list = document.createElement("ul");
      for (const row of routeState.route_candidates) {
        const item = document.createElement("li");
        item.dataset.candidateId = row.candidate_id;
        const routeLink = document.createElement("a");
        routeLink.href = row.route_url;
        routeLink.textContent = row.name;
        item.append(routeLink, document.createTextNode(` · ${row.route_extent_kind} · ${row.nominal_crossing ? "nominal crossing" : "scenario-only crossing"} · ${row.crossing_scenario_count}/${row.scenario_count} declared scenarios`));
        const details = document.createElement("details");
        const summary = document.createElement("summary");
        summary.textContent = "Route scope, layer and time";
        details.append(summary);
        for (const text of [row.scope, row.layer, row.time_convention]) {
          const paragraph = document.createElement("p"); paragraph.textContent = text; details.append(paragraph);
        }
        const source = document.createElement("a"); source.href = row.source_url; source.textContent = "Read the source";
        source.target = "_blank"; source.rel = "noopener noreferrer"; details.append(source);
        item.append(details); list.append(item);
      }
      if (!routeState.route_candidates.length) {
        const empty = document.createElement("li"); empty.textContent = "No reference-route crossing recorded. Current passage remains unresolved."; list.append(empty);
      }
      routeSection.append(list);
    }
    result.append(routeSection);

    const observedFronts = context.front.front_observations;
    const observedFrontLengths = context.front.front_intersection_lengths_km;
    if (Object.keys(observedFronts).length) {
      const front = document.createElement("p");
      front.className = "state-warning";
      const current = document.createElement("a");
      current.href = "object.html?id=current%3Agulf-stream-system";
      current.textContent = "Gulf Stream System";
      front.append(document.createTextNode(`${context.front_date} analyzed surface front: `), current,
        document.createTextNode(` ${Object.entries(observedFronts).map(([side, kind]) => `${side.replaceAll("_", " ")} (${kind.replaceAll("_", " ")}, ≈${Math.round(observedFrontLengths[side]).toLocaleString()} km of analyzed front in this atlas state)`).join("; ")}. These lengths measure dated front segments clipped by approximate state shapes, not a whole current or perpetual passage. `));
      const source = document.createElement("a");
      source.href = context.front_source_url;
      source.target = "_blank";
      source.rel = "noopener noreferrer";
      source.textContent = "NOAA source ↗";
      front.append(source);
      result.append(front);
    }
    const diagnosedPathHere = context.diagnosed_relation;
    if (diagnosedPathHere) {
      const paragraph = document.createElement("p");
      paragraph.className = "state-warning state-diagnosed-current-path";
      const current = document.createElement("a");
      current.href = "object.html?id=current%3Agulf-stream-system";
      current.textContent = "Gulf Stream System";
      paragraph.append(document.createTextNode(`${context.diagnosed_date} partial surface geostrophic streamline: `), current,
        document.createTextNode(` · ≈${Math.round(diagnosedPathHere.intersection_length_km).toLocaleString()} km of this dated diagnostic line in ${code}. The entire seed-to-50°W reach is ≈${Math.round(context.diagnosed_length_km).toLocaleString()} km; a seed 0.25° north stopped before the gate. NOAA labels the source analysis experimental. This is neither a whole-current length nor permanent state passage. `));
      const source = document.createElement("a");
      source.href = context.diagnosed_product_page;
      source.target = "_blank";
      source.rel = "noopener noreferrer";
      source.textContent = "NOAA velocity product ↗";
      paragraph.append(source);
      result.append(paragraph);
    }
    if(window.renderAtlasDatedStateSamples)window.renderAtlasDatedStateSamples(result,code);
    for (const {record: observation, current: observedCurrent} of context.current_observations) {
      const paragraph = document.createElement("p");
      paragraph.className = "state-warning state-source-observation";
      const current = document.createElement("a");
      current.href = `object.html?id=${encodeURIComponent(observation.entity_id)}`;
      current.textContent = observedCurrent.name;
      paragraph.append(document.createTextNode(`${observation.observation_start} to ${observation.observation_end} published local observation: `), current,
        document.createTextNode(` · ${observation.reported_locality}. ${observation.time_detail} ${observation.state_boundary_limit} This source-reported local section or locality does not establish a whole-current path, length, or permanent state crossing. `));
      const source = document.createElement("a");
      source.href = observation.source_url;
      source.target = "_blank";
      source.rel = "noopener noreferrer";
      source.textContent = "Published study ↗";
      paragraph.append(source);
      result.append(paragraph);
    }
    const operationalEddiesHere = context.operational_eddy_observations;
    if (operationalEddiesHere.length) {
      const details = document.createElement("details");
      details.className = "state-eddy-details operational-eddy-details";
      const summary = document.createElement("summary");
      summary.textContent = `${operationalEddiesHere.length} dated NAVO operational eddy ${operationalEddiesHere.length === 1 ? "polygon" : "polygons"} · 2026-09-25`;
      details.append(summary);
      const list = document.createElement("ul");
      for (const row of operationalEddiesHere) {
        const item = document.createElement("li");
        const detection = document.createElement("a");
        detection.href = "object.html?id=" + encodeURIComponent(row.operational_eddy_id);
        detection.textContent = row.provider_code + " detection details";
        item.append(detection, document.createTextNode(` · ${row.provider_type.toLowerCase()}, ${row.provider_rotation.toLowerCase()} · ${row.relation.replaceAll("_", " ")}. `));
        const source = document.createElement("a");
        source.href = "https://www.ncei.noaa.gov/jag/navy/data/satellite_analysis/nafreddy.zip";
        source.target = "_blank";
        source.rel = "noopener noreferrer";
        source.textContent = "NAVO/NCEI source ZIP ↗";
        const receipt = document.createElement("a");
        receipt.href = "release/v0.1.0/source-ledgers/navo-freddies-eddy-snapshot-20260925.json";
        receipt.textContent = "Pinned observation receipt";
        item.append(source, document.createTextNode(" · "), receipt);
        list.append(item);
      }
      details.append(list);
      const limit = document.createElement("p");
      limit.textContent = "These are provider codes for one dated polygon release, not persistent named-eddy identities or events shown in NASA's movie. State containment uses approximate OSW display boundaries; the shapefile has no declared coordinate reference system.";
      details.append(limit);
      result.append(details);
    }
    const groups = document.createElement("div");
    groups.className = "state-groups";
    for (const groupView of membership.groups) {
      const group = document.createElement("div");
      group.dataset.membershipKind = `${groupView.prefix}:${groupView.kind}`;
      const h4 = document.createElement("h4"); h4.textContent = groupView.title;
      const links = stateMembershipLinks(groupView.members, groupView.prefix, groupView.fallback);
      for (const [index, member] of groupView.members.entries()) {
        if (member.source_arrow_ids.length) links.children[index].append(document.createTextNode(` · source arrow ${member.source_arrow_ids.join(", ")}`));
      }
      group.append(h4, links); groups.append(group);
    }
    result.append(groups);
    const contextualClasses = membership.contextual_classes;
    if (contextualClasses.length) {
      const details = document.createElement("details");
      details.className = "state-eddy-details";
      const summary = document.createElement("summary");
      summary.textContent = `${contextualClasses.length} NASA classes or systems with indexed examples here`;
      details.append(summary);
      const list = document.createElement("ul");
      for (const context of contextualClasses) {
        const classId = context.object.id;
        const item = document.createElement("li");
        const classLink = document.createElement("a");
        classLink.href = `#nasa-${classId}`;
        classLink.textContent = context.object.name;
        item.append(classLink, document.createTextNode(": "));
        for (const [index, member] of context.members.entries()) {
          if (index) item.append(document.createTextNode(", "));
          const memberLink = document.createElement("a");
          memberLink.href = `#nasa-${member.id}`;
          memberLink.textContent = member.name;
          memberLink.title = `${facetLabel(member.relation.relation)}; atlas evidence: ${member.relation.evidence_kinds.map(facetLabel).join(", ")}.`;
          item.append(memberLink);
        }
        item.append(document.createTextNode(" · example context only; no class footprint or containment claim."));
        list.append(item);
      }
      details.append(list);
      result.append(details);
    }
    const namedEddyPositions = context.named_eddy_positions;
    if (namedEddyPositions.length) {
      const details = document.createElement("details");
      details.className = "state-eddy-details";
      const summary = document.createElement("summary");
      summary.textContent = `${namedEddyPositions.length} source-reported named-eddy point${namedEddyPositions.length === 1 ? "" : "s"} inside`;
      details.append(summary);
      const list = document.createElement("ul");
      for (const {record: visit, eddy: observedEddy} of namedEddyPositions) {
        const item = document.createElement("li");
        const link = document.createElement("a");
        link.href = `#eddy-geography-${visit.eddy_id}`;
        link.textContent = `${observedEddy.name} · ${visit.date || visit.period}`;
        item.append(link, document.createTextNode(` · ${facetLabel(visit.evidence_type)}; point only, no footprint or containment claim.`));
        list.append(item);
      }
      details.append(list);
      result.append(details);
    }
    if (context.loop_region_names.length) {
      const details = document.createElement("details");
      details.className = "state-eddy-details";
      const summary = document.createElement("summary");
      summary.textContent = `${context.loop_region_names.length} Horizon Loop eddy names · shared Gulf source-region gateway`;
      details.append(summary, stateMembershipLinks(context.loop_region_names, "eddy", "No names in this source region."));
      const caveat = document.createElement("p");
      caveat.textContent = "These names share a regional locator. Horizon's table does not supply individual positions, so this list does not establish containment or intersection with the state.";
      details.append(caveat);
      result.append(details);
    }
    const publishedLoopPositions = context.published_loop_positions;
    if (publishedLoopPositions.length) {
      const details = document.createElement("details");
      details.className = "state-eddy-details";
      const summary = document.createElement("summary");
      summary.textContent = `${publishedLoopPositions.length} published Loop eddy center point${publishedLoopPositions.length === 1 ? "" : "s"} inside`;
      details.append(summary);
      const list = document.createElement("ul");
      for (const observedEddy of publishedLoopPositions) {
        const eddyId = observedEddy.id, position = observedEddy.published_observed_position;
        const item = document.createElement("li");
        const link = document.createElement("a");
        link.href = `#eddy-${eddyId}`;
        link.textContent = `${observedEddy.name} · ${position.period}`;
        item.append(link, document.createTextNode(" · approximate center point; no footprint or NASA identity claim."));
        list.append(item);
      }
      details.append(list);
      result.append(details);
    }
    const movieJoin = context.movie_selection;
    const movieHeading = document.createElement("h4");
    movieHeading.textContent = "NASA regional movie views";
    result.append(movieHeading);
    const movieList = document.createElement("ul");
    movieList.className = "state-movie-list";
    function appendDateSeek(item, url) {
      const seek = contextResult.movie_seek;
      if (!seek) return;
      const link = document.createElement("a");
      link.href = `${url}#t=${seek.estimated_crop_seconds}`;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = `~${selectedDate} model date ↗`;
      link.title = "Approximate cross-release date alignment; NASA did not publish crop frame timestamps or identify the NOAA eddy in this movie.";
      item.append(document.createTextNode(" · "), link);
    }
    for (const [index, match] of context.recommended_movies.entries()) {
      const tileId = match.tile_id;
      const entry = document.createElement("li");
      const link = document.createElement("a");
      link.href = match.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = `Regional view ${index + 1} · ${Math.round(match.display_coverage_fraction * 100)}% display overlap ↗`;
      link.title = `${tileId}: NASA 4K movie; large file. State boundaries and object names are OSW indexes, not NASA labels.`;
      entry.append(link);
      appendDateSeek(entry, match.url);
      movieList.append(entry);
    }
    const overview = context.overview_movie;
    const overviewItem = document.createElement("li");
    const overviewLink = document.createElement("a");
    overviewLink.href = overview.url;
    overviewLink.target = "_blank";
    overviewLink.rel = "noopener noreferrer";
    overviewLink.textContent = `Broader view · ${Math.round(overview.display_coverage_fraction * 100)}% display overlap ↗`;
    overviewItem.append(overviewLink);
    appendDateSeek(overviewItem, overview.url);
    movieList.append(overviewItem);
    if (movieJoin.polar_perspective) {
      const polar = movieJoin.polar_perspective;
      const polarItem = document.createElement("li");
      const polarLink = document.createElement("a");
      polarLink.href = polar.url;
      polarLink.target = "_blank";
      polarLink.rel = "noopener noreferrer";
      polarLink.textContent = `${polar.hemisphere === "north" ? "North" : "South"} polar perspective ↗`;
      polarLink.title = "NASA polar movie; selected from the OSW state's display centroid, without a claimed state footprint in the movie.";
      polarItem.append(polarLink);
      movieList.append(polarItem);
    }
    result.append(movieList);
    const movieNote = document.createElement("p");
    movieNote.className = "state-warning";
    movieNote.textContent = "The rectangular NASA crops geographically cover the approximate state. Polar perspectives are selected by the OSW state display centroid and have no measured state coverage. Where a model-date seek is available, it is an inference from NASA's separate date list and sampled crop frame counts, not a verified crop timestamp. Display overlap or matching model date does not establish a named current path, eddy identity, or observed state boundary.";
    result.append(movieNote);
    if (state.schematic_nasa_object_crossings.length) {
      const gate = document.createElement("p");
      gate.textContent = `Schematic NASA-linked gate line crossing: ${state.schematic_nasa_object_crossings.join(", ").replaceAll("-", " ")}.`;
      result.append(gate);
    }
    const detected = Object.fromEntries(noaa.groups.map(group => [group.status, group.rows]));
    const eddyHeading = document.createElement("h4");
    eddyHeading.textContent = `NOAA detected eddies · ${selectedDate}`;
    result.append(eddyHeading);
    for (const [label, ids] of [["Fully contained contours", detected.contained], ["Contours intersecting this state", detected.intersected]]) {
      const details = document.createElement("details");
      details.className = "state-eddy-details";
      const summary = document.createElement("summary");
      summary.textContent = `${label}: ${ids.length}`;
      details.append(summary);
      const list = document.createElement("ul");
      for (const row of ids) {
        const id = row.id, eddy = row.record;
        const item = document.createElement("li");
        const [longitude, latitude] = eddy.center;
        const description = `${id} · ${eddy.polarity} · center ${latitude?.toFixed(2)}°, ${longitude?.toFixed(2)}° · radius ${eddy.radius_km?.toFixed(1) ?? "?"} km`;
        if (row.track_available) {
          const button = document.createElement("button");
          button.type = "button";
          button.textContent = `${description} · show weekly path`;
          button.addEventListener("click", () => showTrack(id, date, date, code));
          item.append(button);
        } else {
          item.textContent = description;
        }
        const datedCrop = row.crop;
        const tileId = datedCrop?.tile.id;
        if (tileId) {
          const movie = document.createElement("a");
          movie.href = `${datedCrop.tile.url}#t=${datedCrop.estimated_crop_seconds}`;
          movie.target = "_blank";
          movie.rel = "noopener noreferrer";
          movie.textContent = `NASA crop ${tileId} near this center/date ↗`;
          movie.title = "Geographic and approximate model-date navigation only; NASA ECCO2 does not identify this NOAA detected eddy.";
          item.append(document.createTextNode(" · "), movie);
        }
        list.append(item);
      }
      if (!ids.length) {
        const item = document.createElement("li");
        item.textContent = "No detection in this state for the selected date and product coverage.";
        list.append(item);
      }
      details.append(list);
      result.append(details);
    }
    if (noaa.weekly) {
    const weeklyDates = noaa.weekly.center_relations.track_dates;
    const weeklyDetails = document.createElement("details");
    weeklyDetails.className = "state-eddy-details";
    const weeklySummary = document.createElement("summary");
    weeklySummary.textContent = `NOAA weekly center visits · ${Object.keys(weeklyDates).length} day-one tracks · ${noaa.weekly.start_date} to ${noaa.weekly.end_date}`;
    weeklyDetails.append(weeklySummary);
    const weeklyList = document.createElement("ul");
    for (const [id, dates] of Object.entries(weeklyDates)) {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `${id} · center in state ${dates.join(", ")} · show weekly path`;
      button.addEventListener("click", () => showTrack(id, dates[0], date, code));
      item.append(button);
      weeklyList.append(item);
    }
    if (!weeklyList.children.length) {
      const item = document.createElement("li");
      item.textContent = "No NOAA trajectory center visited this state during this seven-day file.";
      weeklyList.append(item);
    }
    weeklyDetails.append(weeklyList);
    result.append(weeklyDetails);
    for (const [status, label] of [["contained", "Fully contained weekly contours"], ["intersected", "Weekly contours intersecting this state"]]) {
      const trackDates = noaa.weekly.contour_relations[status];
      const details = document.createElement("details");
      details.className = "state-eddy-details";
      const summary = document.createElement("summary");
      summary.textContent = `${label}: ${Object.keys(trackDates).length} day-one tracks · ${noaa.weekly.start_date} to ${noaa.weekly.end_date}`;
      details.append(summary);
      const list = document.createElement("ul");
      for (const [id, dates] of Object.entries(trackDates)) {
        const item = document.createElement("li");
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = `${id} · ${dates.join(", ")} · show weekly path`;
        button.addEventListener("click", () => showTrack(id, dates[0], date, code));
        item.append(button);
        list.append(item);
      }
      if (!list.children.length) {
        const item = document.createElement("li");
        item.textContent = "No contour relation in this seven-day file.";
        list.append(item);
      }
      details.append(list);
      result.append(details);
    }
    }
    const unresolved = membership.unresolved_nasa;
    const nasaStatus = document.createElement("p");
    nasaStatus.className = "state-warning";
    nasaStatus.textContent = `${membership.atlas_linked_object_count} of ${membership.nasa_object_count} NASA-identified records have atlas map evidence in ${code}; ${unresolved.length} object–state pairs remain unresolved. Map evidence does not establish a physical crossing or containment.`;
    result.append(nasaStatus);
    const unknownDetails = document.createElement("details");
    unknownDetails.className = "state-eddy-details nasa-unresolved-details";
    const unknownSummary = document.createElement("summary");
    unknownSummary.textContent = `NASA object relations unresolved here · ${unresolved.length}`;
    unknownDetails.append(unknownSummary, stateMembershipLinks(unresolved, "nasa", "Every NASA object has atlas evidence in this state."));
    result.append(unknownDetails);
    const warning = document.createElement("p");
    warning.className = "state-warning";
    warning.textContent = `These NOAA detections sample ${selectedDate} only, within the product's approximate 60°S–60°N latitude range. IDs are local to daily files; none is matched to a Horizon ring name or a NASA model eddy. Where present, NASA crop links use NOAA center position and an inferred same-model-date seek, not an identity match. ${noaa.weekly ? `The ${noaa.weekly.start_date} to ${noaa.weekly.end_date} center visits and dated contour relations are separate tests. ` : "Seven-day tracks are available for June sample dates only. "}Named-ring containment/intersection remains unknown. Editorial current sketches are approximate routes, not observed cores or verified passage; locator points are candidates only.`;
    result.append(warning);
    document.querySelector("#state-count").textContent = `${metadata.state_count} states · ${code} selected`;
    const url = new URL(window.location.href);
    url.searchParams.set("state", code);
    history.replaceState(null, "", url);
  }
  select.addEventListener("change", () => draw().catch(error => {trackSummary.textContent = `State query unavailable: ${error.message}`;}));
  dateSelect.addEventListener("change", async () => {
    const previousDate = selectedDate;
    const nextDate = dateSelect.value;
    dateSelect.disabled = true;
    try {
      selectedDate = nextDate;
      trackLayer.replaceChildren();
      await draw();
    } catch (error) {
      dateSelect.value = previousDate;
      selectedDate = previousDate;
      trackSummary.textContent = `Could not load ${nextDate}: ${error.message}`;
      console.error(error);
    } finally {
      dateSelect.disabled = false;
    }
  });
  showEddies.addEventListener("change", drawEddyMap);
  const requested = new URLSearchParams(window.location.search).get("state");
  if (requested && metadata.states.some(state => state.code === requested)) select.value = requested;
  document.querySelector("#state-count").textContent = `${metadata.state_count} states`;
  await draw();
}

async function renderMarineRegionsCurrentCrosswalk() {
  const input = document.querySelector("#source-current-search");
  const filter = document.querySelector("#source-current-filter");
  const body = document.querySelector("#source-current-rows");
  let serial = 0;
  async function draw() {
    const ticket = ++serial;
    const view = await window.oswIndexSupport({section: "reconciliation", text: input.value, filter: filter.value});
    if (ticket !== serial) return;
    window.oswIndexReconciliationView = view;
    body.replaceChildren();
    for (const joined of view.rows) {
      const record = joined.record;
      const row = document.createElement("tr");
      row.id = `mr-current-${record.mrgid}`;
      cell(row, record.name);
      const status = cell(row, joined.status_label);
      status.title = record.join_note;
      const osw = document.createElement("td");
      if (record.osw_current_id) {
        const link = document.createElement("a");
        link.href = `#current-${record.osw_current_id}`;
        link.textContent = `${joined.current.name} ↗`;
        link.addEventListener("click", event => window.oswNavigateIndexCurrent(event, record.osw_current_id));
        osw.append(link);
      } else osw.textContent = "Unresolved";
      row.append(osw);
      cell(row, record.source_point ? `${record.source_point[1].toFixed(2)}°, ${record.source_point[0].toFixed(2)}°` : "Not supplied");
      const source = cell(row, record.source ? record.source.length > 90 ? `${record.source.slice(0, 87)}…` : record.source : "Not stated");
      source.title = record.source || "No gazetteer source named in this record.";
      const recordCell = document.createElement("td");
      const recordLink = document.createElement("a");
      recordLink.href = record.record_url;
      recordLink.target = "_blank";
      recordLink.rel = "noopener noreferrer";
      recordLink.textContent = `MRGID ${record.mrgid} ↗`;
      recordCell.append(recordLink);
      if (record.review_note) {
        const review = document.createElement("p");
        review.className = "source-review-note";
        review.textContent = record.review_note;
        recordCell.append(review);
        if (record.review_source_url) {
          const evidence = document.createElement("a");
          evidence.href = record.review_source_url;
          evidence.target = "_blank";
          evidence.rel = "noopener noreferrer";
          evidence.textContent = "Review evidence ↗";
          recordCell.append(evidence);
        }
      }
      row.append(recordCell);
      body.append(row);
    }
    document.querySelector("#source-current-count").textContent = `${body.children.length} of ${view.total} source records`;
  }
  const refresh = () => draw().catch(error => {document.querySelector("#source-current-count").textContent = `Source query unavailable: ${error.message}`;});
  input.addEventListener("input", refresh);
  filter.addEventListener("change", refresh);
  await draw();
}

window.oswNavigateIndexEddy = async function(event, section, hash) {
  event.preventDefault();
  const controller = window.oswIndexEddyControllers?.[section];
  if (!controller) return;
  controller.input.value = "";
  try {
    await controller.draw();
    const target = document.getElementById(hash.slice(1));
    if (target) {location.hash = hash; target.scrollIntoView({block: "center"});}
  } catch (error) {
    document.querySelector(section === "loop" ? "#eddy-count" : "#eddy-geography-count").textContent = `Eddy query unavailable: ${error.message}`;
  }
};

async function renderEddies() {
  const initial = await window.oswIndexEddies({section: "loop"});
  const input = document.querySelector("#eddy-search");
  const body = document.querySelector("#eddy-rows");
  const count = document.querySelector("#eddy-count");
  document.querySelector("#eddy-date").textContent = initial.retrieved_date;
  let serial = 0;
  async function draw() {
    const ticket = ++serial;
    const view = await window.oswIndexEddies({section: "loop", text: input.value});
    if (ticket !== serial) return;
    (window.oswIndexEddyViews ||= {}).loop = view;
    body.replaceChildren();
    for (const joined of view.rows) {
      const item = joined.record;
      const row = document.createElement("tr");
      row.id = `eddy-${item.id}`;
      const relation = joined.relation;
      cell(row, String(item.source_number));
      cell(row, item.name);
      cell(row, item.role === "primary" ? "Primary" : "Secondary eddy");
      const separation = cell(row, item.initial_separation || "Not reported for secondary name");
      if (relation.temporal_relation === "separation_in_model_years_identity_unverified") {
        const dateNote = document.createElement("small");
        dateNote.textContent = " · NASA model years overlap; identity unverified";
        separation.append(dateNote);
      } else if (relation.temporal_relation === "related_event_in_model_years_secondary_undated") {
        const dateNote = document.createElement("small");
        dateNote.textContent = " · linked event began in NASA model years";
        separation.append(dateNote);
      }
      const parent = cell(row, item.related_primary_id ? `Linked to ${joined.parent.name}` : "—");
      const nasaClass = document.createElement("a");
      nasaClass.href = `#nasa-${relation.nasa_object_id}`;
      nasaClass.textContent = "NASA-described class ↗";
      nasaClass.title = "NASA describes Gulf of Mexico loop eddies as a class, but does not identify this Horizon-named ring.";
      nasaClass.addEventListener("click", () => {
        const nasaSearch = document.querySelector("#nasa-search");
        if (nasaSearch.value) {
          nasaSearch.value = "";
          nasaSearch.dispatchEvent(new Event("input"));
        }
      });
      parent.append(document.createElement("br"), nasaClass);
      if (item.external_evidence) {
        const independent = document.createElement("a");
        independent.href = item.external_evidence.source_url;
        independent.target = "_blank";
        independent.rel = "noopener noreferrer";
        independent.textContent = "Independent ring study ↗";
        independent.title = item.external_evidence.note;
        parent.append(document.createElement("br"), independent);
      }
      if (relation.published_observed_position) {
        const position = relation.published_observed_position;
        const source = document.createElement("a");
        source.href = position.source_url;
        source.target = "_blank";
        source.rel = "noopener noreferrer";
        source.textContent = `Published center near ${Math.abs(position.coordinate[1])}°N, ${Math.abs(position.coordinate[0])}°W ↗`;
        source.title = `${position.period}. ${position.note}`;
        parent.append(document.createElement("br"), source, document.createTextNode(` · ${position.period} · OSW point-in-state ${position.state_point_candidates.join(", ") || "none"}`));
      }
      if (relation.published_dated_map_presence) {
        const presence = relation.published_dated_map_presence;
        const source = document.createElement("a");
        source.href = presence.source_url;
        source.target = "_blank";
        source.rel = "noopener noreferrer";
        source.textContent = `Source-labeled map · ${presence.date} ↗`;
        source.title = presence.note;
        parent.append(document.createElement("br"), source);
        if (presence.nasa_crop_seek) {
          const seek = document.createElement("a");
          seek.href = presence.nasa_crop_seek.url;
          seek.target = "_blank";
          seek.rel = "noopener noreferrer";
          seek.textContent = " · NASA model-date view ↗";
          seek.title = "Approximate cross-release date alignment in a regional movie. The source-labeled observed ring is not identified in NASA's ECCO model.";
          parent.append(seek);
        }
      }
      mapLink(row, relation.published_observed_position ? "Published center point ↗" : "Gulf region ↗", relation.published_observed_position ? item.id : "loop-rings", null, relation.published_observed_position?.nasa_region_movie.url || relation.nasa_region_movie.url, null, relation.published_observed_position ? "NASA regional model view of the approximate published eddy center, from a different period. NASA does not identify this ring or provide its footprint." : null);
      body.append(row);
    }
    count.textContent = `${body.children.length} of ${view.total} names · ${view.numbered_event_count} numbered events`;
  }
  input.addEventListener("input", () => draw().catch(error => {count.textContent = `Eddy query unavailable: ${error.message}`;}));
  (window.oswIndexEddyControllers ||= {}).loop = {input, draw};
  await draw();
}

async function renderNamedEddyGeography() {
  let serial = 0;
  const input = document.querySelector("#eddy-geography-search");
  const body = document.querySelector("#eddy-geography-rows");
  async function draw() {
    const ticket = ++serial;
    const view = await window.oswIndexEddies({section: "geography", text: input.value});
    if (ticket !== serial) return;
    (window.oswIndexEddyViews ||= {}).geography = view;
    body.replaceChildren();
    for (const joined of view.rows) {
      const item = joined.record, relation = joined.relation;
      const row = document.createElement("tr");
      row.id = `eddy-geography-${item.id}`;
      const name = cell(row, item.name);
      name.title = item.locator_basis;
      const identity = cell(row, item.identity_level === "individual_eddy"
        ? `Individual · ${item.formation ? `formed ${item.event_year}` : item.event_year}`
        : item.identity_level === "eddy_family" ? `Named ${item.object_type === "ring" ? "ring" : "eddy"} class` : "Recurring regional name");
      if (item.sample_site) identity.append(document.createTextNode(` · CTD cast ${item.sample_site.cast_id}, ${item.sample_site.depth_db.toLocaleString()} dbar`));
      if (item.observed_center) identity.append(document.createTextNode(` · center reported ${item.observed_center.period}`));
      for (const observation of relation.additional_observed_position_joins || []) {
        const note = document.createElement("span");
        const [longitude, latitude] = observation.coordinate;
        note.textContent = `${facetLabel(observation.evidence_type)} ${observation.date || observation.period} at ${Math.abs(latitude)}°${latitude < 0 ? "S" : "N"}, ${Math.abs(longitude)}°${longitude < 0 ? "W" : "E"} · point-in-state candidates: ${observation.state_center_candidates.join(", ") || "none"}`;
        note.title = observation.note;
        const movie = document.createElement("a");
        movie.href = observation.nasa_region_movie.url;
        movie.textContent = " · NASA regional crop ↗";
        movie.title = "Regional model context only; this historical ring is not identified in the NASA animation.";
        movie.target = "_blank";
        movie.rel = "noopener noreferrer";
        identity.append(document.createElement("br"), note, movie);
      }
      if(item.published_ring_radius_evidence)window.renderPublishedRingRadii(identity,{name:item.name,measurements:item.published_ring_radius_evidence},item.ring_radius_audit_file,item.id);
      if(item.radial_scale_evidence) window.renderEddyRadialScales(identity,{measurements:item.radial_scale_evidence});
      if (item.reported_radius_km && !item.radial_scale_evidence) identity.append(document.createTextNode(` · ~${item.reported_radius_km} km radius`));
      if (item.reported_track_period) identity.append(document.createTextNode(` · source track ${item.reported_track_period.start} to ${item.reported_track_period.end}`));
      if (item.external_track_identifier) identity.append(document.createTextNode(` · ${item.external_track_identifier.product} #${item.external_track_identifier.track_label} (source identification, track not rejoined)`));
      if (item.reported_lifetime_years_approx) identity.append(document.createTextNode(` · ~${item.reported_lifetime_years_approx} year source-reported lifetime`));
      if (item.reported_travel_km_lower_bound) identity.append(document.createTextNode(` · >${item.reported_travel_km_lower_bound.toLocaleString()} km source-reported ring travel`));
      if (item.reported_encounter) identity.append(document.createTextNode(` · ${item.reported_encounter.place}, ${item.reported_encounter.period}`));
      if (item.identity_note) {
        const identityNote = document.createElement("span");
        identityNote.textContent = item.identity_note;
        identity.append(document.createElement("br"), identityNote);
      }
      if (item.activity_region) {
        const box = item.activity_region;
        const regionSource = document.createElement("a");
        regionSource.href = view.sources[box.source];
        regionSource.target = "_blank";
        regionSource.rel = "noopener noreferrer";
        regionSource.textContent = `Study activity box ${box.west}–${box.east}°E, ${box.south}–${box.north}°N ↗`;
        regionSource.title = "Study-defined region of recurring eddy activity, not an individual eddy footprint or a state-containment claim.";
        identity.append(document.createElement("br"), regionSource);
      }
      if (item.source_observed_months) identity.append(document.createTextNode(` · source observations ${item.source_observed_months.join(", ")}`));
      if (item.vertical_evidence) {
        const depthNote = document.createElement("span");
        depthNote.textContent = item.vertical_evidence;
        identity.append(document.createElement("br"), depthNote);
      }
      for (const key of item.supporting_sources || []) {
        const support = document.createElement("a");
        support.href = view.sources[key];
        support.target = "_blank";
        support.rel = "noopener noreferrer";
        support.textContent = `${facetLabel(key)} ↗`;
        identity.append(document.createElement("br"), support);
      }
      if (item.related_current_id) {
        const currentLink = document.createElement("a");
        currentLink.href = `#current-${item.related_current_id}`;
        currentLink.textContent = `Related source current: ${joined.related_current.name} ↗`;
        currentLink.title = "A source-described current relationship; the exact relation depends on the eddy record. This does not establish NASA identification or an observed whole-eddy path.";
        currentLink.addEventListener("click", event => window.oswNavigateIndexCurrent(event, item.related_current_id));
        identity.append(document.createElement("br"), currentLink);
      }
      if (item.nasa_object_id) {
        const nasaLink = document.createElement("a");
        nasaLink.href = `#nasa-${item.nasa_object_id}`;
        nasaLink.textContent = "NASA named class ↗";
        nasaLink.addEventListener("click", () => {
          const nasaSearch = document.querySelector("#nasa-search");
          if (nasaSearch.value) { nasaSearch.value = ""; nasaSearch.dispatchEvent(new Event("input")); }
        });
        identity.append(document.createElement("br"), nasaLink);
      }
      const classContext = relation.nasa_class_context;
      const classLinks = [[classContext.generic_class_id, "NASA ocean-eddy class ↗"]];
      if (classContext.specific_class_id && !item.nasa_object_id) classLinks.push([classContext.specific_class_id, "NASA Agulhas Rings class ↗"]);
      for (const [classId, label] of classLinks) {
        const classLink = document.createElement("a");
        classLink.href = `#nasa-${classId}`;
        classLink.textContent = label;
        classLink.title = "OSW taxonomic context only. NASA did not identify this named individual in its footage.";
        classLink.addEventListener("click", () => {
          const nasaSearch = document.querySelector("#nasa-search");
          if (nasaSearch.value) { nasaSearch.value = ""; nasaSearch.dispatchEvent(new Event("input")); }
        });
        identity.append(document.createElement("br"), classLink);
      }
      if (item.related_nasa_object_id) {
        const nasaLink = document.createElement("a");
        nasaLink.href = `#nasa-${item.related_nasa_object_id}`;
        nasaLink.textContent = "Related NASA-described flow ↗";
        nasaLink.title = "NASA describes the parent overflow, but does not identify this eddy class or an individual eddy.";
        nasaLink.addEventListener("click", () => {
          const nasaSearch = document.querySelector("#nasa-search");
          if (nasaSearch.value) {
            nasaSearch.value = "";
            nasaSearch.dispatchEvent(new Event("input"));
          }
        });
        identity.append(document.createElement("br"), nasaLink);
      }
      if (item.reported_fate) {
        const fate = item.reported_fate.type === "last_confirmed_alive"
          ? `Observed through ${item.reported_fate.date}`
          : `Dissipated ${item.reported_fate.period}`;
        const note = document.createElement("span");
        note.textContent = fate;
        note.title = item.reported_fate.note;
        identity.append(document.createElement("br"), note);
      }
      if (item.source_census_count) identity.append(document.createTextNode(` · ${item.source_census_count} source-detected in ${item.source_census_period}`));
      if (item.independent_source_census) {
        const census = item.independent_source_census;
        const link = document.createElement("a");
        link.href = view.sources[census.source];
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = `${census.initial_shed_rings} shed rings; ${census.long_lived_walvis_crossing_tracks} long-lived Walvis-crossing tracks (${census.period}) ↗`;
        link.title = census.definition_note;
        identity.append(document.createElement("br"), link);
      }
      if (item.source_activity_periods) identity.append(document.createTextNode(` · ${item.source_activity_periods} reported activity periods in ${item.source_activity_year}`));
      if (item.member_of) {
        const parent = joined.parent;
        const link = document.createElement("a");
        link.href = `#eddy-geography-${item.member_of}`;
        link.textContent = `Family: ${parent.name} ↗`;
        link.addEventListener("click", event => window.oswNavigateIndexEddy(event, "geography", link.hash));
        identity.append(document.createElement("br"), link);
      }
      cell(row, item.basin);
      const [longitude, latitude] = item.locator;
      const locator = cell(row, `${Math.abs(latitude)}°${latitude < 0 ? "S" : "N"}, ${Math.abs(longitude)}°${longitude < 0 ? "W" : "E"} · ${item.sample_site ? "sample site" : item.observed_center ? "reported center" : item.formation ? "reported event point" : "region point"}`);
      locator.title = item.locator_basis;
      cell(row, facetLabel(item.polarity));
      const state = document.createElement("td");
      for (const code of relation.state_locator_candidates) {
        const link = document.createElement("a");
        link.href = `?state=${encodeURIComponent(code)}#state-title`;
        link.textContent = `${code} locator ↗`;
        link.title = "Regional point inside an approximate OSW state; no dated eddy containment or intersection claim.";
        if (state.childNodes.length) state.append(document.createTextNode(" · "));
        state.append(link);
      }
      if (!state.childNodes.length) state.textContent = "No suitable OSW state";
      row.append(state);
      sourceCell(row, "Research source ↗", view.sources[item.source]);
      const movie = document.createElement("td");
      const map = document.createElement("a");
      map.href = "#motion-map-section";
      map.textContent = "Map point ↗";
      map.title = item.locator_basis;
      map.addEventListener("click", () => {
        document.querySelectorAll("#motion-markers .selected").forEach(marker => marker.classList.remove("selected"));
        document.querySelectorAll(`#motion-markers [data-record="${item.id}"]`).forEach(marker => marker.classList.add("selected"));
      });
      const crop = document.createElement("a");
      crop.href = relation.nasa_region_movie.url;
      crop.target = "_blank";
      crop.rel = "noopener noreferrer";
      crop.textContent = relation.nasa_region_movie.temporal_relation === "outside_model_period"
        ? `${relation.nasa_region_movie.tile_id} · different era ↗`
        : relation.nasa_region_movie.temporal_relation === "source_observations_before_inferred_crop_window"
          ? `${relation.nasa_region_movie.tile_id} · before inferred crop dates ↗`
        : relation.nasa_region_movie.depth_relation === "subsurface_visibility_unverified"
          ? `${relation.nasa_region_movie.tile_id} · depth unverified ↗`
        : `${relation.nasa_region_movie.tile_id} · region only ↗`;
      crop.title = relation.nasa_region_movie.temporal_relation === "outside_model_period"
        ? `NASA regional crop covers ${relation.nasa_region_movie.model_period}; it cannot depict the ${item.event_year} individual eddy.`
        : relation.nasa_region_movie.temporal_relation === "source_observations_before_inferred_crop_window"
          ? `A related NASA date list suggests ${relation.nasa_region_movie.crop_date_start} to ${relation.nasa_region_movie.crop_date_end} for this crop; alignment is unverified. The cited observations are from ${item.source_observed_months.join(", ")}. NASA did not identify these peddies.`
        : `NASA regional crop covers ${relation.nasa_region_movie.model_period}; NASA did not identify a generation of this named eddy or provide its dated footprint.`;
      if (relation.nasa_region_movie.depth_relation === "subsurface_visibility_unverified") crop.title += " The named subsurface lens is not verified as visible in this crop.";
      movie.append(map, document.createTextNode(" · "), crop);
      row.append(movie);
      body.append(row);
    }
    document.querySelector("#eddy-geography-count").textContent = `${body.children.length} of ${view.total} names`;
  }
  input.addEventListener("input", () => draw().catch(error => {document.querySelector("#eddy-geography-count").textContent = `Eddy query unavailable: ${error.message}`;}));
  (window.oswIndexEddyControllers ||= {}).geography = {input, draw};
  await draw();
}

async function renderUnifiedEddyIndex() {
  const initial = await window.oswIndexEddies({section: "inventory"});
  let serial = 0;
  const input = document.querySelector("#all-eddy-search");
  const results = document.querySelector("#all-eddy-results");
  const count = document.querySelector("#all-eddy-count");
  count.textContent = `${initial.total} source records · ${initial.horizon_numbered_event_count} numbered Loop events`;
  async function draw() {
    const ticket = ++serial;
    const view = await window.oswIndexEddies({section: "inventory", text: input.value});
    if (ticket !== serial) return;
    (window.oswIndexEddyViews ||= {}).inventory = view;
    results.replaceChildren();
    for (const joined of view.rows) {
      const item = joined.record;
      const row = document.createElement("li");
      const link = document.createElement("a");
      link.href = item.atlas_anchor;
      link.textContent = item.name;
      link.addEventListener("click", event => {
        if (item.source_collection === "published_loop_current") return;
        window.oswNavigateIndexEddy(event, item.source_collection === "horizon_loop_current" ? "loop" : "geography", link.hash);
      });
      const sourceLabel = joined.source_label, dateLabel = joined.date_label;
      row.append(link, document.createTextNode(` · ${sourceLabel} · ${dateLabel}`));
      results.append(row);
    }
    if (view.text.trim() && !view.rows.length) {
      const row = document.createElement("li");
      row.textContent = "No name in the current source set matches this search.";
      results.append(row);
    }
  }
  input.addEventListener("input", () => draw().catch(error => {results.textContent = `Eddy query unavailable: ${error.message}`;}));
  await draw();
}

Promise.all([
  window.oswIndexMap(),
  loadJson("../research/noaa-munster-eddy-seasonal-manifest-2021-2023.json"),
]).then(async ([map, seasonalManifest]) => {
  window.oswIndexMapView = map;
  renderGeostrophicPathMap(map);
  renderOperationalEddyMap(map);
  await renderCurrents();
  await renderIllustratedSpans();
  await renderMarineRegionsCurrentCrosswalk();
  await renderEddies();
  await renderNamedEddyGeography();
  await renderUnifiedEddyIndex();
  renderMap(map);
  renderGulfStreamFrontMap(map);
  document.querySelector("#north-front-length").textContent = `≈${Math.round(map.front_lengths_km.north_wall).toLocaleString()} km`;
  document.querySelector("#south-front-length").textContent = `≈${Math.round(map.front_lengths_km.south_wall).toLocaleString()} km`;
  await renderNasaObjects();
  await renderNasaReleaseMedia();
  await renderStates(seasonalManifest);
  window.oswIndexPageReady = true;
}).catch(error => {
  document.querySelector("#current-count").textContent = "Data unavailable";
  document.querySelector("#eddy-count").textContent = "Data unavailable";
  document.querySelector("#eddy-geography-count").textContent = "Data unavailable";
  document.querySelector("#map-count").textContent = "Map unavailable";
  document.querySelector("#nasa-count").textContent = "Data unavailable";
  document.querySelector("#state-count").textContent = "Data unavailable";
  console.error(error);
});

loadJson("release/v0.1.0/coverage.json").then(coverage => {
  const levels = coverage.identity_levels;
  document.querySelector("#taxonomy-counts").textContent =
    `In this declared source set: ${levels.family} current families, ${levels.system} systems, ` +
    `${levels.current} current-level records, ${levels.segment} named segments, ` +
    `${levels.eddy_family} eddy families, ${levels.recurrent_eddy_region} recurrent eddy regions, ` +
    `and ${levels.individual_eddy} individual named eddy records. ` +
    `These are classification counts, not a global census.`;
}).catch(() => {
  document.querySelector("#taxonomy-counts").textContent = "Classified source-set counts unavailable.";
});
