"use strict";

const data = window.OSW_COLUMN_DATA;
const bathy = window.OSW_BATHY_NEIGHBORHOODS;
const svg = document.querySelector("#column-svg");
const NS = "http://www.w3.org/2000/svg";
const bandColors = ["#256f82", "#24576d", "#173f58", "#102f47", "#0a2338"];
let selectedProvince = "NADR";
let selectedBand = "OBJ113";
let scaleMode = "readable";
let neighborhoodMode = "depth";
const depthMapColors = {land:"#dad6c8",epipelagic:"#3b91a2",mesopelagic:"#2c7087",bathypelagic:"#1e506d",abyssopelagic:"#163a59",hadalpelagic:"#0a203b"};
const sourceMapColors = {land:"#dad6c8",direct_measurement:"#5bd8ce",indirect_or_interpolated:"#e8b960",mixed_or_unknown:"#b49ae8"};

function el(name, attrs = {}, text = "") {
  const node = document.createElementNS(NS, name);
  Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
  if (text) node.textContent = text;
  return node;
}

function bandLabel(band) {
  return band.upper_m === null
    ? `${band.name} · ≥${band.lower_m.toLocaleString()} m`
    : `${band.name} · ${band.lower_m.toLocaleString()}–<${band.upper_m.toLocaleString()} m`;
}

function overlayLabel(overlay) {
  if (overlay.range_m) return `${overlay.name} · hypothetical ${overlay.range_m[0].toLocaleString()}–${overlay.range_m[1].toLocaleString()} m`;
  return `${overlay.name} · hypothetical lowest ${overlay.height_above_bottom_m.toLocaleString()} m above seabed`;
}

function yForDepth(depth) {
  const top = 92, bottom = 615;
  if (scaleMode === "linear") return top + Math.min(depth, 8000) / 8000 * (bottom - top);
  const bounds = [0, 200, 1000, 4000, 6000, 8000];
  const segment = (bottom - top) / 5;
  let index = bounds.findIndex((value, i) => i < bounds.length - 1 && depth < bounds[i + 1]);
  if (index < 0) index = 4;
  const fraction = (depth - bounds[index]) / (bounds[index + 1] - bounds[index]);
  return top + (index + Math.max(0, Math.min(1, fraction))) * segment;
}

function seafloorBand(elevation) {
  if (elevation >= 0) return "land";
  const depth = -elevation;
  if (depth < 200) return "epipelagic";
  if (depth < 1000) return "mesopelagic";
  if (depth < 4000) return "bathypelagic";
  if (depth < 6000) return "abyssopelagic";
  return "hadalpelagic";
}

function sourceClass(tid) {
  if (tid === 0) return "land";
  if (tid >= 10 && tid <= 17) return "direct_measurement";
  if (tid >= 40 && tid <= 46) return "indirect_or_interpolated";
  return "mixed_or_unknown";
}

function defs() {
  const node = el("defs");
  const patterns = [
    ["mixed-pattern", "#ffd66f", "M0 8L8 0"],
    ["thermo-pattern", "#ff916f", "M0 0L8 8"],
    ["mass-pattern", "#68e0d5", "M4 0V8"],
    ["bottom-pattern", "#bdabef", "M0 4H8"],
  ];
  patterns.forEach(([id, color, path]) => {
    const pattern = el("pattern", {id, width:8, height:8, patternUnits:"userSpaceOnUse"});
    pattern.append(el("rect", {width:8, height:8, fill:color, opacity:.10}), el("path", {d:path, stroke:color, "stroke-width":1, opacity:.65}));
    node.append(pattern);
  });
  return node;
}

function render() {
  svg.replaceChildren(defs());
  const bands = data.column_address.bands;
  const province = data.provinces.find(item => item.code === selectedProvince);
  const measurement = province.seed_measurement;
  const columns = [{id:"seed",name:"Selected seed cell",bottom_m:measurement.water_depth_m,cell_state:measurement.cell_state,elevation_m:measurement.elevation_m,measured:true}, ...data.teaching_columns];
  const widths = 160;
  const xs = [120, 330, 540, 750];

  svg.append(el("text", {x:28,y:58,class:"axis-title"}, "DECLARED DEPTH ↓"));
  const depthTicks = scaleMode === "linear" ? [0,1000,2000,3000,4000,5000,6000,7000,8000] : [0,200,1000,4000,6000,8000];
  depthTicks.forEach(depth => {
    const y = yForDepth(depth);
    svg.append(el("line", {x1:100,y1:y,x2:925,y2:y,class:"guide-line"}));
    svg.append(el("text", {x:88,y:y+4,class:"depth-label","text-anchor":"end"}, `${depth.toLocaleString()} m`));
  });

  columns.forEach((column, columnIndex) => {
    const x = xs[columnIndex];
    const floorY = yForDepth(column.bottom_m ?? 0);
    svg.append(el("text", {x:x+widths/2,y:35,class:"column-title"}, column.name));
    const columnNote = column.measured
      ? (column.cell_state === "wet" ? `GEBCO 2026 · ${column.bottom_m.toLocaleString()} m` : `GEBCO 2026 · +${column.elevation_m.toLocaleString()} m`)
      : `${column.bottom_m.toLocaleString()} m teaching depth`;
    svg.append(el("text", {x:x+widths/2,y:55,class:"column-note"}, columnNote));
    if (column.cell_state === "non_wet_seed") {
      svg.append(el("rect", {x,y:92,width:widths,height:548,class:"nonwet"}));
      svg.append(el("text", {x:x+widths/2,y:340,class:"nonwet-label","text-anchor":"middle"}, "NON-WET SEED"));
      svg.append(el("text", {x:x+widths/2,y:360,class:"column-note"}, "retained · not moved"));
      return;
    }
    bands.forEach((band, index) => {
      if (band.lower_m >= column.bottom_m) return;
      const bandBottom = Math.min(band.upper_m ?? 8000, column.bottom_m);
      const y1 = yForDepth(band.lower_m), y2 = yForDepth(bandBottom);
      const rect = el("rect", {x,y:y1,width:widths,height:Math.max(1,y2-y1),fill:bandColors[index],class:`band${band.object_id===selectedBand?" selected":""}`,tabindex:"0",role:"button","data-band":band.object_id,"aria-label":`Select ${bandLabel(band)} in ${column.name}`});
      rect.addEventListener("click", () => selectBand(band.object_id));
      rect.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); selectBand(band.object_id); } });
      svg.append(rect);
      if (y2-y1 > 28) svg.append(el("text", {x:x+10,y:y1+20,class:"band-label"}, band.name.toUpperCase()));
    });
    drawOverlays(x, widths, column.bottom_m, column.measured);
    svg.append(el("path", {d:`M${x-8} ${floorY}H${x+widths+8}V640H${x-8}Z`,class:"seabed"}));
  });
  renderNeighborhood();
  updateReadout();
}

function renderNeighborhood() {
  const neighborhood = bathy.neighborhoods[selectedProvince];
  const canvas = document.querySelector("#neighborhood-canvas");
  const context = canvas.getContext("2d");
  const size = bathy.shape[0], cell = canvas.width / size;
  context.clearRect(0, 0, canvas.width, canvas.height);
  for (let row = 0; row < size; row += 1) {
    for (let column = 0; column < size; column += 1) {
      const sourceIndex = row * size + column;
      const displayRow = size - 1 - row;
      const key = neighborhoodMode === "depth" ? seafloorBand(neighborhood.elevation_m[sourceIndex]) : sourceClass(neighborhood.tid[sourceIndex]);
      context.fillStyle = (neighborhoodMode === "depth" ? depthMapColors : sourceMapColors)[key];
      context.fillRect(column * cell, displayRow * cell, Math.ceil(cell), Math.ceil(cell));
    }
  }
  const center = Math.floor(size / 2);
  context.strokeStyle = "#fff0a0"; context.lineWidth = 5;
  context.strokeRect(center * cell + 2, center * cell + 2, cell - 4, cell - 4);
  context.fillStyle = "#eef9f7"; context.font = "900 22px ui-monospace, monospace";
  context.fillText("N", 14, 28); context.fillText("E", canvas.width - 30, canvas.height - 14);

  const legendEntries = neighborhoodMode === "depth"
    ? [["land","land/non-wet"],["epipelagic","bottom <200 m"],["mesopelagic","bottom 200–<1,000 m"],["bathypelagic","bottom 1,000–<4,000 m"],["abyssopelagic","bottom 4,000–<6,000 m"],["hadalpelagic","bottom ≥6,000 m"]]
    : [["land","land"],["direct_measurement","direct measurement"],["indirect_or_interpolated","indirect/interpolated"],["mixed_or_unknown","mixed/unknown"]];
  const legend = document.querySelector("#neighborhood-legend");
  legend.replaceChildren(...legendEntries.map(([key, label]) => {
    const span = document.createElement("span"), swatch = document.createElement("i");
    swatch.style.background = (neighborhoodMode === "depth" ? depthMapColors : sourceMapColors)[key];
    span.append(swatch, document.createTextNode(label)); return span;
  }));
  const summary = neighborhood.summary;
  const detail = neighborhoodMode === "depth"
    ? `Wet depths range from ${summary.minimum_wet_depth_m?.toLocaleString() ?? "none"} to ${summary.maximum_wet_depth_m?.toLocaleString() ?? "none"} m.`
    : `${summary.counts_by_tid_class.direct_measurement ?? 0} direct, ${summary.counts_by_tid_class.indirect_or_interpolated ?? 0} indirect/interpolated, ${summary.counts_by_tid_class.mixed_or_unknown ?? 0} mixed/unknown, and ${summary.counts_by_tid_class.land ?? 0} land source cells.`;
  document.querySelector("#neighborhood-summary").textContent = `${selectedProvince}: ${summary.wet_sample_count.toLocaleString()} wet and ${summary.land_sample_count.toLocaleString()} land samples among ${summary.sample_count.toLocaleString()} regular grid points from ${summary.latitude_bounds[0].toFixed(2)}° to ${summary.latitude_bounds[1].toFixed(2)}° latitude and ${summary.longitude_bounds[0].toFixed(2)}° to ${summary.longitude_bounds[1].toFixed(2)}° longitude. ${detail} These counts describe the seed neighborhood, not the province.`;
  canvas.setAttribute("aria-label", `${selectedProvince} GEBCO seed-neighborhood ${neighborhoodMode} map. ${document.querySelector("#neighborhood-summary").textContent}`);
}

function drawOverlays(x, width, bottom, measured = false) {
  if (measured) return;
  const active = new Set([...document.querySelectorAll("#overlay-controls input:checked")].map(input => input.value));
  data.physical_overlays.forEach((overlay, index) => {
    if (!active.has(overlay.id)) return;
    let upper = overlay.range_m?.[0] ?? Math.max(0, bottom - overlay.height_above_bottom_m);
    let lower = overlay.range_m?.[1] ?? bottom;
    if (upper >= bottom) return;
    lower = Math.min(lower, bottom);
    const inset = 9 + index * 8;
    svg.append(el("rect", {x:x+inset,y:yForDepth(upper),width:width-inset*2,height:Math.max(2,yForDepth(lower)-yForDepth(upper)),rx:5,class:`overlay overlay-${overlay.id}` }));
  });
}

function selectBand(id, announce = true) {
  selectedBand = id;
  document.querySelectorAll("#band-controls button").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.band === id)));
  updateUrl(); render();
  if (announce) document.querySelector("#address-readout").dataset.announced = "true";
}

function updateReadout() {
  const province = data.provinces.find(item => item.code === selectedProvince);
  const band = data.column_address.bands.find(item => item.object_id === selectedBand);
  const measurement = province.seed_measurement;
  const active = [...document.querySelectorAll("#overlay-controls input:checked")].map(input => overlayLabel(data.physical_overlays.find(item => item.id === input.value)));
  const overlaySentence = active.length ? ` Enabled hypothetical overlays: ${active.join(", ")}.` : " No physical teaching overlays enabled.";
  let measuredSentence;
  if (measurement.cell_state !== "wet") {
    measuredSentence = ` The nearest GEBCO seed cell is non-wet at +${measurement.elevation_m.toLocaleString()} m; it supplies no water-column occupancy and was not moved offshore.`;
  } else if (band.lower_m >= measurement.water_depth_m) {
    measuredSentence = ` The nearest GEBCO seed cell is ${measurement.water_depth_m.toLocaleString()} m deep and does not reach this band.`;
  } else if (band.upper_m === null || band.upper_m > measurement.water_depth_m) {
    measuredSentence = ` The nearest GEBCO seed cell is ${measurement.water_depth_m.toLocaleString()} m deep and contains only the upper, bathymetry-truncated part of this band.`;
  } else {
    measuredSentence = ` The nearest GEBCO seed cell is ${measurement.water_depth_m.toLocaleString()} m deep and spans this complete reference band.`;
  }
  document.querySelector("#address-title").textContent = `${province.code} × ${band.name}`;
  document.querySelector("#seed-status").textContent = measurement.cell_state === "wet"
    ? `ONE GEBCO SEED CELL · ${measurement.sampled_latitude.toFixed(4)}°, ${measurement.sampled_longitude.toFixed(4)}° · ${measurement.water_depth_m.toLocaleString()} M DEEP · TID ${measurement.tid_code} ${measurement.tid_class.replaceAll("_", " ").toUpperCase()}`
    : `NON-WET SEED CELL · ${measurement.sampled_latitude.toFixed(4)}°, ${measurement.sampled_longitude.toFixed(4)}° · +${measurement.elevation_m.toLocaleString()} M · TID ${measurement.tid_code} LAND`;
  document.querySelector("#address-readout").textContent = `${province.province} (${province.code}) · ${province.basin} / ${province.biome} reference · ${bandLabel(band)}.${measuredSentence} GEBCO source type: TID ${measurement.tid_code}, ${measurement.tid_definition}. This single-cell result is not province-wide and is not a detected physical regime.${overlaySentence}`;
  document.querySelector("#svg-desc").textContent = `${band.name} is selected for ${province.province}. One GEBCO seed cell and three conceptual shelf, basin, and trench columns show bathymetric truncation. Enabled overlays apply only to teaching columns.`;
}

function updateUrl() {
  const url = new URL(window.location.href);
  url.searchParams.set("province", selectedProvince);
  url.searchParams.set("band", selectedBand);
  history.replaceState(null, "", url);
}

function init() {
  const params = new URLSearchParams(location.search);
  if (data.provinces.some(item => item.code === params.get("province"))) selectedProvince = params.get("province");
  if (data.column_address.bands.some(item => item.object_id === params.get("band"))) selectedBand = params.get("band");
  if (["depth", "source"].includes(params.get("neighborhood"))) neighborhoodMode = params.get("neighborhood");

  const provinceSelect = document.querySelector("#province-select");
  data.provinces.forEach(province => {
    const option = document.createElement("option");
    option.value = province.code;
    option.textContent = `${province.code} — ${province.province}`;
    provinceSelect.append(option);
  });
  provinceSelect.value = selectedProvince;
  provinceSelect.addEventListener("change", event => { selectedProvince = event.target.value; updateUrl(); render(); });

  const bandControls = document.querySelector("#band-controls");
  data.column_address.bands.forEach(band => {
    const button = document.createElement("button");
    button.type = "button"; button.dataset.band = band.object_id;
    button.setAttribute("aria-pressed", String(band.object_id === selectedBand));
    button.textContent = bandLabel(band);
    button.addEventListener("click", () => selectBand(band.object_id));
    bandControls.append(button);
  });

  const overlayControls = document.querySelector("#overlay-controls");
  data.physical_overlays.forEach(overlay => {
    const label = document.createElement("label"), input = document.createElement("input");
    input.type = "checkbox"; input.value = overlay.id;
    input.addEventListener("change", render);
    label.append(input, document.createTextNode(overlayLabel(overlay))); overlayControls.append(label);
  });

  document.querySelectorAll("[data-scale]").forEach(button => button.addEventListener("click", () => {
    scaleMode = button.dataset.scale;
    document.querySelectorAll("[data-scale]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    document.querySelector("#scale-badge").textContent = scaleMode === "linear" ? "LINEAR DEPTH · 0–8,000 M" : "EQUAL-BAND DISPLAY · NOT TO SCALE";
    render();
  }));
  document.querySelectorAll("[data-neighborhood-mode]").forEach(button => {
    button.setAttribute("aria-pressed", String(button.dataset.neighborhoodMode === neighborhoodMode));
    button.addEventListener("click", () => {
      neighborhoodMode = button.dataset.neighborhoodMode;
      document.querySelectorAll("[data-neighborhood-mode]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
      const url = new URL(window.location.href); url.searchParams.set("neighborhood", neighborhoodMode); history.replaceState(null, "", url);
      renderNeighborhood();
    });
  });
  render();
}

init();
