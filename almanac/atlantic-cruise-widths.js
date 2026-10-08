"use strict";
window.renderAtlanticCruiseWidths = function(container, current, inventory) {
  container.replaceChildren();
  const records = inventory.measurements.filter(row => row.current_id === current && row.phase_kind === "inverse_hydrographic_section_span");
  container.hidden = records.length === 0;
  if (!records.length) return;
  const node = (tag, text, parent = container) => {
    const element = document.createElement(tag); element.textContent = text; parent.append(element); return element;
  };
  const heading = node("h2", "Cruise-section spans"); heading.id = "cruise-span-title";
  node("p", "Separate transport-selected section snapshots. Sections and depth support differ. These values do not form an annual range or a seasonal time series.");
  const scroll = node("div", ""); scroll.className = "cruise-span-scroll"; scroll.tabIndex = 0;
  scroll.setAttribute("role", "region"); scroll.setAttribute("aria-label", "Cruise-section span chart and source table; scroll horizontally for detail");
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg"); scroll.append(svg);
  svg.setAttribute("viewBox", `0 0 700 ${records.length * 48 + 62}`);
  svg.setAttribute("class", "cruise-span-chart"); svg.setAttribute("role", "img"); svg.setAttribute("aria-labelledby", "cruise-span-title cruise-span-description");
  const shape = (tag, attributes, text) => {
    const element = document.createElementNS(ns, tag);
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, String(value));
    if (text !== undefined) element.textContent = text;
    svg.append(element); return element;
  };
  shape("desc", {id: "cruise-span-description"}, records.map(row => `${row.hydrographic_section_context.cruise_id}, nominal ${row.hydrographic_section_context.nominal_section_latitude_degrees_north} degrees north: ${row.approximate_width_km} kilometres.`).join(" ") + " Bars encode reported scalar distances, not map edges. Width uncertainty is unreported.");
  const maximum = Math.ceil(Math.max(...records.map(row => row.approximate_width_km)) / 50) * 50;
  for (let tick = 0; tick <= 4; tick++) {
    const x = 300 + tick * 80;
    shape("line", {x1: x, x2: x, y1: 32, y2: records.length * 48 + 24, stroke: "#c5cdd1"});
    shape("text", {x, y: 19, "text-anchor": "middle", fill: "#203642"}, `${maximum * tick / 4} km`);
  }
  records.forEach((row, index) => {
    const context = row.hydrographic_section_context;
    const latitude = context.nominal_section_latitude_degrees_north;
    const y = 40 + index * 48;
    shape("text", {x: 0, y: y + 17, fill: "#203642"}, `${context.cruise_id} · ${Math.abs(latitude)}° ${latitude < 0 ? "S" : "N"}`);
    const bar = shape("rect", {x: 300, y, width: row.approximate_width_km / maximum * 320, height: 24, fill: "#176b82", "data-measurement-id": row.id, "data-value-km": row.approximate_width_km});
    const title = document.createElementNS(ns, "title"); title.textContent = `${row.approximate_width_km} km. ${row.time_convention} ${row.layer}`; bar.append(title);
    shape("text", {x: 630, y: y + 17, fill: "#203642"}, `${row.approximate_width_km} km`);
  });
  const table = node("table", "", scroll); table.className = "cruise-span-table";
  node("caption", "Publisher Table 2 distances with Table 1 cruise sampling windows", table);
  const header = node("tr", "", node("thead", "", table));
  for (const label of ["Cruise / nominal section", "Section sampling window", "Span (km)", "Reported depth extent (m)", "Station label / source row"]) {
    const cell = node("th", label, header); cell.scope = "col";
  }
  const body = node("tbody", "", table);
  for (const row of records) {
    const context = row.hydrographic_section_context;
    const record = node("tr", "", body); record.dataset.measurementId = row.id;
    const cell = node("td", "", record);
    const address = new URL(location.href); address.searchParams.set("current", current); address.searchParams.set("phase", row.id);
    const anchor = node("a", `${context.cruise_id} / ${context.nominal_section_latitude_degrees_north}° north`, cell); anchor.href = address.href;
    node("td", `${context.cruise_sampling_window.start} to ${context.cruise_sampling_window.end}`, record);
    node("td", String(row.approximate_width_km), record);
    node("td", context.source_depth_extent_m.join("–"), record);
    node("td", `${context.source_station_range_label} / Table 2 row ${context.table_2_row}`, record);
  }
  node("p", "Sampling windows cover the whole cruise section. Selected station-pair occupation dates and actual endpoint latitudes are unresolved. Reported density-layer depth extents are not uniform fixed-depth slices. Width uncertainty is unreported.");
  const source = node("a", "Published source and original tables", node("p", "")); source.href = records[0].source_url;
  const query = {collection: "widths", filters: [{field: "current_id", op: "eq", value: current}, {field: "phase_kind", op: "eq", value: "inverse_hydrographic_section_span"}], limit: 100};
  const inspect = node("a", "Query these exact source records", node("p", "")); inspect.href = "query.html?q=" + encodeURIComponent(JSON.stringify(query));
};
