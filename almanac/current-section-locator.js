"use strict";
// Reported latitude limits locate a section; computed limits do not locate edges.
window.currentSectionLocator = (() => {
  const ns = "http://www.w3.org/2000/svg";
  const project = ([lon, lat]) => [60 + (lon + 180) / 360 * 1480, 90 + (90 - lat) / 180 * 740];
  const latitude = lat => `${Math.abs(lat)}° ${lat < 0 ? 'S' : 'N'}`;
  const timeLabel = row => row.time_precision === 'month' ? `${row.observed_month} (month precision; exact days unresolved)` : `${row.observed_period.start} to ${row.observed_period.end}`;
  function coordinates(row) {
    const monthBand = row?.phase_kind === 'month_dated_section';
    const band = monthBand ? row.angular_span_conversion : row?.subsurface_band_context;
    const limits = band?.source_reported_latitude_limits_degrees;
    const lon = monthBand ? band?.source_section_longitude_degrees_east : band?.section_longitude_degrees_east;
    const period = row?.observed_period;
    const depths = band?.source_reported_depth_range_m;
    if (row?.full_width_inference_eligible !== false || row.section_geometry !== null ||
        !Array.isArray(limits) || limits.length !== 2 || !limits.every(Number.isFinite) ||
        !Number.isFinite(lon) || Math.abs(lon) > 180 || limits[0] < -90 || limits[1] > 90 || limits[0] >= limits[1]) return null;
    if (monthBand) {
      if (row.width_metric !== 'author_reported_meridional_angular_span' || row.time_precision !== 'month' ||
          typeof row.observed_month !== 'string' || !/^\d{4}-(0[1-9]|1[0-2])$/.test(row.observed_month) ||
          period !== null || row.calendar_months !== null || row.fixed_layer_bounds_m !== null ||
          row.boundary_sides !== 'author_reported_section_span' ||
          band.source_reported_center_latitude_degrees !== null ||
          band.center_role !== 'computed_from_reported_limits_for_unit_conversion_only' ||
          band.normalization_center_latitude_degrees !== (limits[0]+limits[1])/2 ||
          band.source_reported_latitude_span_degrees !== limits[1]-limits[0] ||
          band.normalization_limits_are_observed_edges !== false) return null;
    } else if (row.phase_kind !== "dated_band_section" ||
        row.width_metric !== "author_described_subsurface_meridional_band_span" || row.time_precision !== 'day' ||
        !period || ![period.start,period.end].every(value => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) && Number.isFinite(Date.parse(value))) || period.start > period.end ||
        !Array.isArray(depths) || depths.length !== 2 || !depths.every(Number.isFinite) || depths[0] < 0 || depths[0] >= depths[1] ||
        band?.paired_velocity_edges_diagnosed !== false) return null;
    return limits.map(lat => [lon, lat]);
  }
  function render(parent, row) {
    const coords = coordinates(row);
    if (!coords) return null;
    const section = document.createElement("section"); section.className = "current-section-locator";
    const heading = document.createElement("h4"); heading.textContent = row.time_precision === 'month' ? 'Reported section location · month precision' : "Dated section location"; section.append(heading);
    const svg = document.createElementNS(ns, "svg");
    svg.classList.add("section-locator-map"); svg.setAttribute("role", "img");
    const points = coords.map(project), centerY = (points[0][1] + points[1][1]) / 2;
    svg.setAttribute("viewBox", `${points[0][0] - 60} ${centerY - 30} 120 60`);
    const summary = `${timeLabel(row)}: ${Math.abs(coords[0][0])}° ${coords[0][0] < 0 ? 'W' : 'E'} section, ${latitude(coords[0][1])} to ${latitude(coords[1][1])}. Blue bracket locates the reported latitude span; it is not a current axis, paired velocity edges or occupied footprint.`;
    svg.setAttribute("aria-label", summary);
    const make = (tag, attrs) => { const el = document.createElementNS(ns, tag); for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value); svg.append(el); return el; };
    make("image", {href:"../figures/ocean-motion-closeup-ground.svg", x:60,y:90,width:1480,height:740,opacity:.6});
    const [x,y0] = points[0], y1 = points[1][1];
    make("path", {d:`M ${x} ${y0} L ${x} ${y1} M ${x-1} ${y0} H ${x+1} M ${x-1} ${y1} H ${x+1}`, fill:"none",stroke:"#82d6ff","stroke-width":2,"vector-effect":"non-scaling-stroke"});
    for (const [i, [px, py]] of points.entries()) {
      const text=make("text",{x:px+3,y:py+.7,fill:"white","font-size":2.5});
      text.textContent=latitude(coords[i][1]);
    }
    section.append(svg);
    const text = document.createElement("p"); text.textContent = summary; section.append(text);
    const scope = document.createElement("p"); scope.textContent = `About ${row.approximate_width_km} km described meridional band span. ${row.layer} ${row.boundary_rule} Equirectangular OSW display geography; coarse coastline. Whole-current length, full width and annual ranges remain unresolved.`; section.append(scope);
    const source = document.createElement("a"); source.href=row.source_url; source.textContent="Section source and measurement definition"; section.append(source);
    parent.append(section); return section;
  }
  return {coordinates, render, timeLabel};
})();
