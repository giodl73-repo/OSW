"use strict";

const data = window.OSW_COLUMN_DATA;
const svg = document.querySelector("#column-svg");
const NS = "http://www.w3.org/2000/svg";
const bandColors = ["#256f82", "#24576d", "#173f58", "#102f47", "#0a2338"];
let selectedProvince = "NADR";
let selectedBand = "OBJ113";
let scaleMode = "readable";

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
  const columns = data.teaching_columns;
  const widths = 190;
  const xs = [190, 455, 720];

  svg.append(el("text", {x:28,y:58,class:"axis-title"}, "DECLARED DEPTH ↓"));
  const depthTicks = scaleMode === "linear" ? [0,1000,2000,3000,4000,5000,6000,7000,8000] : [0,200,1000,4000,6000,8000];
  depthTicks.forEach(depth => {
    const y = yForDepth(depth);
    svg.append(el("line", {x1:100,y1:y,x2:925,y2:y,class:"guide-line"}));
    svg.append(el("text", {x:88,y:y+4,class:"depth-label","text-anchor":"end"}, `${depth.toLocaleString()} m`));
  });

  columns.forEach((column, columnIndex) => {
    const x = xs[columnIndex];
    const floorY = yForDepth(column.bottom_m);
    svg.append(el("text", {x:x+widths/2,y:35,class:"column-title"}, column.name));
    svg.append(el("text", {x:x+widths/2,y:55,class:"column-note"}, `${column.bottom_m.toLocaleString()} m teaching depth`));
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
    drawOverlays(x, widths, column.bottom_m);
    svg.append(el("path", {d:`M${x-8} ${floorY}H${x+widths+8}V640H${x-8}Z`,class:"seabed"}));
  });
  updateReadout();
}

function drawOverlays(x, width, bottom) {
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
  const active = [...document.querySelectorAll("#overlay-controls input:checked")].map(input => overlayLabel(data.physical_overlays.find(item => item.id === input.value)));
  const overlaySentence = active.length ? ` Enabled hypothetical overlays: ${active.join(", ")}.` : " No physical teaching overlays enabled.";
  document.querySelector("#address-title").textContent = `${province.code} × ${band.name}`;
  document.querySelector("#address-readout").textContent = `${province.province} (${province.code}) · ${province.basin} / ${province.biome} reference · ${bandLabel(band)}. This composes an address class; occupancy at this depth is unverified until bathymetry and exact horizontal geometry are intersected. It is not a detected physical regime.${overlaySentence}`;
  document.querySelector("#svg-desc").textContent = `${band.name} is selected for ${province.province}. Shelf, basin, and trench teaching columns show bathymetric truncation. Enabled overlays are conceptual and are also reported by their checked controls.`;
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
  render();
}

init();
