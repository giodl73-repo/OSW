"use strict";

const eventsData = window.OSW_EVENTS;

function renderEventsMap() {
  const canvas = document.querySelector("#events-map"), context = canvas.getContext("2d");
  const bounds = {west: -55, east: -45, south: 38, north: 46};
  const image = context.createImageData(canvas.width, canvas.height);
  const at = (lon, lat) => {
    const column = Math.round((lon - footprints.grid.longitude_start) / footprints.grid.spacing_degrees);
    const row = Math.round((lat - footprints.grid.latitude_start) / footprints.grid.spacing_degrees);
    return row >= 0 && row < 720 && column >= 0 && column < 1440 ? assignments[row * 1440 + column] : -2;
  };
  for (let y = 0; y < canvas.height; y += 1) {
    const lat = bounds.north - (y + 0.5) / canvas.height * (bounds.north - bounds.south);
    for (let x = 0; x < canvas.width; x += 1) {
      const lon = bounds.west + (x + 0.5) / canvas.width * (bounds.east - bounds.west);
      const index = at(lon, lat), east = at(lon + 0.06, lat), south = at(lon, lat - 0.06);
      let rgb = index < 0 ? hex("#f8f8f4") : hex("#e6e7e2");
      if (index >= 0 && (east !== index || south !== index)) rgb = hex("#96a6a3");
      image.data.set([...rgb, 255], (y * canvas.width + x) * 4);
    }
  }
  context.putImageData(image, 0, 0);
  const point = centroid => ({x: (centroid.longitude_degrees_east - bounds.west) / (bounds.east - bounds.west) * canvas.width, y: (bounds.north - centroid.latitude_degrees_north) / (bounds.north - bounds.south) * canvas.height});
  const primary = eventsData.primary_route.days.map(day => point(day.centroid));
  context.beginPath(); primary.forEach((item, index) => index ? context.lineTo(item.x, item.y) : context.moveTo(item.x, item.y));
  context.strokeStyle = "#123c55"; context.lineWidth = 5; context.lineJoin = "round"; context.stroke();
  primary.forEach((item, index) => { context.beginPath(); context.arc(item.x, item.y, index === 0 || index === primary.length - 1 ? 7 : 3, 0, Math.PI * 2); context.fillStyle = index === 0 ? "#087f83" : index === primary.length - 1 ? "#ad7a16" : "#123c55"; context.fill(); });
  const branch = eventsData.lineage_family_route.nodes.find(node => node.node_id === "2026-07-29-C02");
  const source = eventsData.primary_route.days.find(day => day.date === "2026-07-28");
  const branchPoint = point(branch.centroid), sourcePoint = point(source.centroid);
  context.beginPath(); context.moveTo(sourcePoint.x, sourcePoint.y); context.lineTo(branchPoint.x, branchPoint.y); context.strokeStyle = "#a63f55"; context.lineWidth = 3; context.setLineDash([8, 5]); context.stroke(); context.setLineDash([]);
  context.fillStyle = "#132b32"; context.font = "700 17px Georgia"; context.fillText("NWCS", 32, 38); context.fillText("GFST", canvas.width - 78, canvas.height - 30);
  canvas.setAttribute("aria-label", `Regional state-address map of the 21-day primary surface heatwave footprint route, which remains dominantly in GFST, plus one small off-primary centroid branch into adjacent NWCS. The branch inherited 13 pixels, not a measured quantity of transported heat.`);
}

function renderEventsScore() {
  const grid = document.querySelector("#events-score-grid"); grid.replaceChildren();
  const days = eventsData.primary_route.days, maxArea = Math.max(...days.map(day => day.footprint_area_km2));
  appendDefinition(grid, "Primary duration", `${days.length} days`);
  appendDefinition(grid, "Primary states", eventsData.primary_route.province_sequence.join(" → "));
  appendDefinition(grid, "Maximum area", `${Math.round(maxArea).toLocaleString()} km²`);
  appendDefinition(grid, "Crossing candidates", String(eventsData.lineage_family_route.province_crossing_candidate_count));
  document.querySelector("#events-finding").textContent = "The primary event moves roughly 450 km while remaining dominantly inside GFST. One small side branch reaches NWCS in centroid address; neither movement establishes volume or heat transported across a border.";
}

function renderEventsSequence() {
  const body = document.querySelector("#events-sequence-body"); body.replaceChildren();
  eventsData.primary_route.days.forEach(day => {
    const other = day.province_overlap.slice(1).map(item => `${item.province} ${(item.area_fraction * 100).toFixed(2)}%`).join(", ") || "none";
    body.append(tableRow([day.date, day.dominant_province, `${Math.round(day.footprint_area_km2).toLocaleString()} km²`, other, "not available", "not available"]));
  });
}

function renderEventsEvidence() {
  const grid = document.querySelector("#events-evidence-grid"); grid.replaceChildren();
  const labels = {
    geometric_overlap: ["Geometric overlap", "supported"],
    observed_property_propagation: ["Surface property continuity", "partial"],
    model_pathway: ["Modeled pathway", ""],
    volume_exchange: ["Volume exchange", ""],
    heat_transport: ["Heat transport", ""],
  };
  Object.entries(eventsData.evidence_ladder).forEach(([key, value]) => {
    const article = document.createElement("article"), heading = document.createElement("h3"), paragraph = document.createElement("p");
    article.className = labels[key][1]; heading.textContent = labels[key][0]; paragraph.textContent = value.replaceAll("_", " "); article.append(heading, paragraph); grid.append(article);
  });
}

function renderEvents() { renderEventsMap(); renderEventsScore(); renderEventsSequence(); renderEventsEvidence(); }
