"use strict";
(() => {
  const scope = "Hourly hindcast model section at 10 m. These samples are not observations, monthly means, a climatology, current boundaries or OSW state footprints. Current length, width and annual extrema remain unknown.";
  function node(tag, text, parent) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    parent.append(element);
    return element;
  }
  function link(text, href, parent) {
    const url = new URL(href, location.href);
    if (!["http:", "https:"].includes(url.protocol)) return;
    const anchor = node("a", text, parent);
    anchor.href = url.href;
    return anchor;
  }
  function queryLink(text, collection, field, value, sort, parent) {
    const query = {collection, filters: [{field, op: "eq", value}], sort: {field: sort}, limit: 100};
    return link(text, "query.html?q=" + encodeURIComponent(JSON.stringify(query)), parent);
  }
  function datum(parent, label, value) {
    node("dt", label, parent);
    node("dd", value === null || value === undefined ? "Unavailable" : String(value), parent);
  }
  function isLayerContext(row) {
    return ["model_analysis_layer_definition", "reported_model_mean_depth_context"].includes(row.record_type);
  }
  function contextScope(row) {
    const support = row.model_support;
    const study = support ? support.model + " model · " + support.analysis_start_year + "–" + support.analysis_end_year : "Published model study";
    return study + ". Analysis definitions and mean-flow context; physical width, thickness, annual ranges and uncertainty remain unknown.";
  }
  function contextValue(row) {
    if (row.record_type === "model_analysis_layer_definition") {
      const upper = row.upper_reference === "sea_surface" ? "Surface" : (row.upper_depth_m ?? "Unknown") + " m";
      return upper + " to " + (row.lower_depth_m ?? "unknown") + " m · study analysis layer";
    }
    if (row.depth_cap_m !== undefined) return "Mean flow > " + row.velocity_threshold_cm_s + " cm/s does not extend below " + row.depth_cap_m + " m";
    return (row.approximate ? "Approximately " : "Reported ") + (row.reported_depth_m ?? "unknown") + " m · mean-flow core depth";
  }
  function renderLayerContext(parent, row, inspect) {
    const section = node("section", undefined, parent);
    section.className = "model-section-card model-layer-context-card";
    node("h3", row.source_feature + " · " + (row.record_type === "model_analysis_layer_definition" ? "Study analysis layer" : "Mean-flow depth context"), section);
    node("p", contextValue(row), section);
    node("p", contextScope(row), section);
    node("p", row.entity_id === null
      ? "Separate undercurrent context. This record is related to South Java but is not assigned to the surface current or admitted as a new catalogue entity."
      : "Surface-current model context. This record is not an observed current boundary or a physical current thickness.", section);
    const values = node("dl", undefined, section);
    const support = row.model_support;
    if (support?.section_longitudes_degrees_east) datum(values, "Selected mean sections (degrees east)", support.section_longitudes_degrees_east.join(", "));
    if (row.reported_peak_speed_cm_s !== undefined) datum(values, "Reported mean-core peak eastward speed (cm/s)", row.reported_peak_speed_cm_s);
    if (row.depth_cap_m !== undefined) node("p", "The depth cap applies to the stated mean-flow threshold at the selected sections; the exact edge depth is unresolved.", section);
    datum(values, "Source location", row.source_locator);
    const links = node("div", undefined, section);
    links.className = "record-links";
    for (const [text, collection] of [["Related study analysis layers", "current_model_analysis_layers"], ["Related mean-flow depth context", "current_model_depth_context"]]) {
      queryLink(text, collection, "related_current_id", row.related_current_id, "id", links);
    }
    queryLink("South Java current record", "objects", "id", row.related_current_id, "id", links);
    const source = node("button", "Publication and source details", links);
    source.type = "button";
    source.addEventListener("click", () => inspect("sources", row.source_id));
    link("Reviewed source facts", "query.html?source-q=" + encodeURIComponent(JSON.stringify({document: row.source_file, pointer: "", limit: 100})), links);
    const figure = node("figure", undefined, section);
    figure.style.margin = "1rem 0";
    const image = node("img", undefined, figure);
    image.loading = "lazy";
    image.src = new URL("../" + row.figure_file, location.href).href;
    image.alt = "South Java model analysis layers, approximate mean-core depths and threshold cap; a depth schematic, not current thickness or a geographic footprint.";
    image.style.width = "100%";
    image.style.height = "auto";
    link("Open full-size depth schematic", "../" + row.figure_file, links);
    node("figcaption", "Source-qualified depth schematic. Analysis layers, approximate mean cores and the threshold cap are distinct quantities. No physical width or thickness is inferred.", figure);
    return true;
  }
  function render(parent, row, inspect) {
    if (isLayerContext(row)) return renderLayerContext(parent, row, inspect);
    if (!["model_section_frame", "model_section_sample"].includes(row.record_type)) return false;
    const section = node("section", undefined, parent);
    section.className = "model-section-card";
    node("h3", row.label, section);
    node("p", scope, section);
    const values = node("dl", undefined, section);
    datum(values, "Source time (UTC)", row.sample_time_utc);
    datum(values, "Depth (m)", row.depth_m);
    const links = node("div", undefined, section);
    links.className = "record-links";
    if (row.record_type === "model_section_frame") {
      datum(values, "Section longitude (degrees east)", row.section.longitude_degrees_east);
      datum(values, "Selected latitude limits (degrees north)", row.section.start_latitude + " to " + row.section.end_latitude);
      datum(values, "Samples with all three fields", row.available_sample_count + " of " + row.sample_count);
      node("p", row.sampling_rule, section);
      node("p", row.interpolation, section);
      node("p", row.limitations, section);
      const figure = node("figure", undefined, section);
      figure.style.margin = "1rem 0";
      const image = node("img", undefined, figure);
      image.loading = "lazy";
      image.src = new URL("../" + row.map_figure, location.href).href;
      image.alt = "NorKyst regional salinity and instantaneous velocity field for " + row.sample_time_utc + "; not a named-current boundary.";
      image.style.width = "100%";
      image.style.height = "auto";
      image.addEventListener("error", () => {
        image.hidden = true;
        node("p", "Regional field figure unavailable. The checked section records remain available below.", figure);
      }, {once: true});
      node("figcaption", "Regional model field, not a current footprint. " + row.credit + " · " + row.source_license, figure);
      queryLink("Query this frame’s 191 section samples", "model_samples", "model_frame_id", row.id, "sample_index", links);
      link("View recorded-date section page", row.url, links);
      link("Source model subset", row.source_url, links);
      link("Acquisition receipt", "../" + row.receipt_file, links);
    } else {
      datum(values, "Section sample index", row.sample_index);
      datum(values, "Longitude, latitude (degrees)", row.coordinates_lon_lat.join(", "));
      datum(values, "Distance from selected section start (km)", row.distance_from_section_start_km);
      datum(values, "Salinity (dimensionless source units)", row.salinity);
      datum(values, "Eastward velocity component (m/s)", row.u_eastward);
      datum(values, "Northward velocity component (m/s)", row.v_northward);
      node("p", row.field_values_available
        ? "All three interpolated fields have source support at this sampling site. Velocity components are not current speed or a boundary rule."
        : "At least one field has missing interpolation support. Nulls remain unavailable; the sampling position is still known.", section);
      const frame = node("button", "Inspect source frame, units and map", links);
      frame.type = "button";
      frame.addEventListener("click", () => inspect("model_frames", row.model_frame_id));
      queryLink("Query this source frame", "model_frames", "id", row.model_frame_id, "date", links);
    }
    queryLink("Query all NorKyst source frames", "model_frames", "current_id", row.current_id, "date", links);
    return true;
  }
  function value(row) {
    if (isLayerContext(row)) return contextValue(row);
    if (row.record_type === "model_section_frame") return row.sample_count + " sites · hourly model snapshot";
    if (row.record_type === "model_section_sample") {
      const shown = value => value === null ? "Unavailable" : String(value);
      return "S " + shown(row.salinity) + " · u " + shown(row.u_eastward) + " · v " + shown(row.v_northward) + " m/s";
    }
    return null;
  }
  function recordScope(row) {
    if (isLayerContext(row)) return contextScope(row);
    return ["model_section_frame", "model_section_sample"].includes(row.record_type) ? scope : null;
  }
  window.oswModelSectionCard = {render, value, scope: recordScope};
})();
