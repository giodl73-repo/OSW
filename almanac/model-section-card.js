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
  function render(parent, row, inspect) {
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
    if (row.record_type === "model_section_frame") return row.sample_count + " sites · hourly model snapshot";
    if (row.record_type === "model_section_sample") {
      const shown = value => value === null ? "Unavailable" : String(value);
      return "S " + shown(row.salinity) + " · u " + shown(row.u_eastward) + " · v " + shown(row.v_northward) + " m/s";
    }
    return null;
  }
  function recordScope(row) {
    return ["model_section_frame", "model_section_sample"].includes(row.record_type) ? scope : null;
  }
  window.oswModelSectionCard = {render, value, scope: recordScope};
})();
