"use strict";

const data = window.OSW_COLUMN_DATA;
const bathy = window.OSW_BATHY_NEIGHBORHOODS;
const footprints = window.OSW_PROVINCE_FOOTPRINTS;
const fingerprints = window.OSW_PROVINCE_FINGERPRINTS;
const adjacency = window.OSW_PROVINCE_ADJACENCY;
const hypsometry = window.OSW_PROVINCE_HYPSOMETRY;
const svg = document.querySelector("#column-svg");
const NS = "http://www.w3.org/2000/svg";
const bandColors = ["#256f82", "#24576d", "#173f58", "#102f47", "#0a2338"];
let selectedProvince = "NADR";
let selectedBand = "OBJ113";
let scaleMode = "readable";
let neighborhoodMode = "depth";
let footprintProfileMode = "volume";
let footprintMapMode = "family";
const depthMapColors = {land:"#dad6c8",epipelagic:"#3b91a2",mesopelagic:"#2c7087",bathypelagic:"#1e506d",abyssopelagic:"#163a59",hadalpelagic:"#0a203b"};
const sourceMapColors = {land:"#dad6c8",direct_measurement:"#5bd8ce",indirect_or_interpolated:"#e8b960",mixed_or_unknown:"#b49ae8"};
const biomeMapColors = {Polar:"#638aa0",Westerlies:"#426d82",Trades:"#295668",Coastal:"#6d7a72"};
const quantityMapColors = ["#8de4d7", "#55b6b9", "#367c90", "#28566f", "#1a354c"];
const floorMapColors = {"shelf-led":"#86d7d1","upper-depth-floor-led":"#58a7b5","deep-floor-led":"#397a96","abyssal-floor-led":"#223f73","hadal-floor-led":"#121f48"};
const bandShareColors = ["#17364c", "#245a70", "#368497", "#59b7b5", "#91dfd2"];
const neighborMapColors = {selected:"#ffe078",neighbor:"#63e2d8",other:"#1b343c"};
const footprintCodes = [...new Set(footprints.footprint_runs.map(run => run[3]))];
const footprintCodeIndex = new Map(footprintCodes.map((code, index) => [code, index]));
const footprintAssignments = new Int16Array(footprints.grid.shape[0] * footprints.grid.shape[1]).fill(-1);
footprints.footprint_runs.forEach(([row, start, end, code]) => footprintAssignments.fill(footprintCodeIndex.get(code), row * footprints.grid.shape[1] + start, row * footprints.grid.shape[1] + end + 1));
let footprintMollweideAssignments;

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
  svg.replaceChildren(
    defs(),
    el("title", {id:"svg-title"}, "Ocean column address teaching section"),
    el("desc", {id:"svg-desc"}, "Five depth bands shown in shelf, basin, and trench example columns."),
  );
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
  renderFootprint();
  updateReadout();
}

function hexRgb(value) {
  return [parseInt(value.slice(1,3),16),parseInt(value.slice(3,5),16),parseInt(value.slice(5,7),16)];
}

function approximateVolume(value) {
  return `${(Math.round(value / 1000) * 1000).toLocaleString()} km³`;
}

function approximateBandVolume(value) {
  const rounded = value >= 1000 ? Math.round(value / 10) * 10 : (value >= 10 ? Math.round(value * 10) / 10 : Math.round(value * 100) / 100);
  return `${rounded.toLocaleString()} km³`;
}

function ranksFor(field) {
  return new Map(Object.values(footprints.provinces)
    .sort((left, right) => right[field] - left[field])
    .map((province, index) => [province.osw_code, index + 1]));
}

const provinceRanks = {
  area: ranksFor("sampled_wet_area_km2"),
  volume: ranksFor("sampled_water_volume_km3"),
  depth: ranksFor("area_weighted_mean_water_depth_m"),
};

function rankColor(rank, count = 54) {
  return quantityMapColors[Math.min(4, Math.floor((rank - 1) * 5 / count))];
}

function selectedBandInfo() {
  const band = data.column_address.bands.find(item => item.object_id === selectedBand);
  const ordered = Object.values(footprints.provinces)
    .filter(province => province.water_volume_km3_by_depth_band[band.name] > 0)
    .sort((left, right) => right.water_volume_km3_by_depth_band[band.name] - left.water_volume_km3_by_depth_band[band.name]);
  return {band, count:ordered.length, ranks:new Map(ordered.map((province, index) => [province.osw_code, index + 1]))};
}

function rankLegendEntries(count) {
  return quantityMapColors.map((color, index) => {
    const start = Math.ceil(index * count / 5) + 1;
    const end = Math.ceil((index + 1) * count / 5);
    return [color, start === end ? `rank ${start}` : `ranks ${start}–${end}`];
  });
}

function appendLegend(container, entries) {
  container.replaceChildren(...entries.map(([color, label]) => {
    const item = document.createElement("span"), swatch = document.createElement("i");
    swatch.style.background = color; item.append(swatch, document.createTextNode(label)); return item;
  }));
}

function bandShareColor(share) {
  if (share <= 0) return "#313a3d";
  if (share < .01) return bandShareColors[0];
  if (share < .02) return bandShareColors[1];
  if (share < .05) return bandShareColors[2];
  if (share < .10) return bandShareColors[3];
  return bandShareColors[4];
}

function renderDepthLadder() {
  const canvas = document.querySelector("#depth-ladder-canvas"), context = canvas.getContext("2d");
  const [rows, columns] = footprints.grid.shape;
  if (!footprintMollweideAssignments) footprintMollweideAssignments = buildMollweideAssignments(rows, columns);
  const narrow = window.matchMedia("(max-width: 700px)").matches;
  canvas.width = narrow ? 600 : 1440; canvas.height = narrow ? 1600 : 900;
  context.fillStyle = "#06181e"; context.fillRect(0, 0, canvas.width, canvas.height);
  const panels = narrow ? [[20,55],[20,365],[20,675],[20,985],[20,1295]] : [[20,70],[500,70],[980,70],[260,500],[740,500]];
  const panelWidth = narrow ? 560 : 440, panelHeight = narrow ? 280 : 220;
  const selectedIndex = footprintCodeIndex.get(selectedProvince), boundary = hexRgb("#71898d"), selectedEdge = hexRgb("#ffe078"), outside = hexRgb("#06181e");
  const summaryList = document.querySelector("#depth-ladder-summary"); summaryList.replaceChildren();
  const accessible = [];
  data.column_address.bands.forEach((band, bandIndex) => {
    const total = footprints.volume_summary.water_volume_km3_by_depth_band[band.name];
    const shares = new Map(footprintCodes.map(code => [code, (footprints.provinces[code]?.water_volume_km3_by_depth_band[band.name] ?? 0) / total]));
    const image = context.createImageData(panelWidth, panelHeight);
    for (let y = 0; y < panelHeight; y += 1) {
      const sourceRow = Math.min(rows - 1, Math.floor(y / panelHeight * rows));
      for (let x = 0; x < panelWidth; x += 1) {
        const sourceColumn = Math.min(columns - 1, Math.floor(x / panelWidth * columns));
        const codeIndex = footprintMollweideAssignments[sourceRow * columns + sourceColumn];
        const offset = (y * panelWidth + x) * 4;
        let rgb = outside;
        if (codeIndex >= 0) {
          const code = footprintCodes[codeIndex]; rgb = hexRgb(bandShareColor(shares.get(code)));
          const eastColumn = Math.min(columns - 1, Math.floor((x + 1) / panelWidth * columns));
          const southRow = Math.min(rows - 1, Math.floor((y + 1) / panelHeight * rows));
          const east = footprintMollweideAssignments[sourceRow * columns + eastColumn];
          const south = footprintMollweideAssignments[southRow * columns + sourceColumn];
          if (east !== codeIndex || south !== codeIndex) rgb = codeIndex === selectedIndex || east === selectedIndex || south === selectedIndex ? selectedEdge : boundary;
        }
        image.data[offset] = rgb[0]; image.data[offset + 1] = rgb[1]; image.data[offset + 2] = rgb[2]; image.data[offset + 3] = 255;
      }
    }
    const [panelX, panelY] = panels[bandIndex]; context.putImageData(image, panelX, panelY);
    context.strokeStyle = "#496b70"; context.lineWidth = 2; context.strokeRect(panelX, panelY, panelWidth, panelHeight);
    const positive = [...shares].filter(([, share]) => share > 0).sort((left, right) => right[1] - left[1]);
    const leader = positive[0], topFive = positive.slice(0, 5).reduce((sum, item) => sum + item[1], 0);
    context.fillStyle = "#eef9f7"; context.font = "900 22px ui-monospace, monospace"; context.fillText(band.name.toUpperCase(), panelX, panelY - 25);
    context.fillStyle = "#8fb4b6"; context.font = "700 16px ui-monospace, monospace"; context.fillText(`${(total / 1_000_000).toFixed(1)}M km³ · ${positive.length} states · ${leader[0]} leads`, panelX, panelY + panelHeight + 22);
    const sentence = `${band.name}: ${(total / 1_000_000).toFixed(1)} million km³ across ${positive.length} states; ${leader[0]} holds ${(leader[1] * 100).toFixed(2)}%, and the top five hold ${(topFive * 100).toFixed(2)}%.`;
    accessible.push(sentence); const item = document.createElement("li"); item.textContent = sentence; summaryList.append(item);
  });
  appendLegend(document.querySelector("#depth-ladder-legend"), [[bandShareColors[0],"<1% of global band"],[bandShareColors[1],"1–<2%"],[bandShareColors[2],"2–<5%"],[bandShareColors[3],"5–<10%"],[bandShareColors[4],"≥10%"],["#313a3d","no sampled band volume"],["#ffe078","gold edge = selected province"]]);
  canvas.setAttribute("aria-label", `Five Oceanic Mollweide maps using one global-band-share scale. ${accessible.join(" ")}`);
}

function renderPassport(summary, fingerprint, bandInfo) {
  const passport = document.querySelector("#footprint-passport");
  passport.replaceChildren();
  if (!summary) {
    const wrapper = document.createElement("div"), term = document.createElement("dt"), value = document.createElement("dd");
    term.textContent = "Version 4 passport"; value.textContent = "Unavailable for this older identity";
    wrapper.append(term, value); passport.append(wrapper); return;
  }
  const totalArea = Object.values(footprints.provinces).reduce((total, province) => total + province.sampled_wet_area_km2, 0);
  const bandName = bandInfo.band.name;
  const bandVolume = summary.water_volume_km3_by_depth_band[bandName];
  const bandRank = bandInfo.ranks.get(summary.osw_code);
  const globalBandVolume = footprints.volume_summary.water_volume_km3_by_depth_band[bandName];
  const entries = [
    ["Sampled wet area", `#${provinceRanks.area.get(summary.osw_code)} of 54 · ${(summary.sampled_wet_area_km2 / totalArea * 100).toFixed(2)}%`],
    ["Sampled water volume", `#${provinceRanks.volume.get(summary.osw_code)} of 54 · ${(summary.sampled_water_volume_km3 / footprints.volume_summary.sampled_source_aligned_water_volume_km3 * 100).toFixed(2)}%`],
    ["Mean water depth", `#${provinceRanks.depth.get(summary.osw_code)} deepest · ${summary.area_weighted_mean_water_depth_m.toLocaleString()} m`],
    ["Floor character", `${fingerprint.floor_character.replaceAll("-", " ")} · ${(fingerprint.dominant_seafloor_area_fraction * 100).toFixed(1)}%`],
    ["Vertical breadth", `${fingerprint.substantial_seafloor_band_count} of 5 bands ≥5% · hadal ${fingerprint.hadal_bearing ? "yes" : "no"}`],
    ["Area → volume rank", fingerprint.volume_rank_advantage_over_area === 0 ? "no rank change" : `${fingerprint.volume_rank_advantage_over_area > 0 ? "+" : ""}${fingerprint.volume_rank_advantage_over_area} places by volume`],
    [`${bandName} volume`, bandRank ? `#${bandRank} of ${bandInfo.count} · ${approximateBandVolume(bandVolume)}` : "no sampled volume"],
    ["Share of this state", `${(summary.water_volume_fraction_by_depth_band[bandName] * 100).toFixed(2)}% of sampled water`],
    ["Share of global band", `${(bandVolume / globalBandVolume * 100).toFixed(2)}% of sampled band`],
  ];
  const graphNode = adjacency.nodes.find(item => item.osw_code === summary.osw_code);
  entries.push(["Source-edge neighbors", `${graphNode.degree} · ${graphNode.shared_boundary_length_km.toLocaleString()} km shared total`]);
  entries.forEach(([label, text]) => {
    const wrapper = document.createElement("div"), term = document.createElement("dt"), value = document.createElement("dd");
    term.textContent = label; value.textContent = text; wrapper.append(term, value); passport.append(wrapper);
  });
}

function selectProvince(code) {
  selectedProvince = code;
  document.querySelector("#province-select").value = code;
  updateUrl(); render();
}

function renderNeighborTable() {
  const body = document.querySelector("#neighbor-table-body");
  const summary = document.querySelector("#neighbor-summary");
  body.replaceChildren();
  const node = adjacency.nodes.find(item => item.osw_code === selectedProvince);
  if (!node) {
    summary.textContent = `${selectedProvince} is an older directory identity without a separate Version 4 footprint, so no source-edge neighbors are assigned.`;
    const row = document.createElement("tr"), cell = document.createElement("td"); cell.colSpan = 4; cell.textContent = "No Version 4 border passports available."; row.append(cell); body.append(row);
    return;
  }
  const edges = adjacency.edges.filter(item => item.provinces.includes(selectedProvince)).sort((left, right) => right.shared_boundary_length_km - left.shared_boundary_length_km);
  edges.forEach(edge => {
    const neighbor = edge.provinces.find(code => code !== selectedProvince);
    const row = document.createElement("tr"), name = document.createElement("td"), button = document.createElement("button");
    button.type = "button"; button.textContent = neighbor; button.setAttribute("aria-label", `Select neighboring province ${neighbor}`); button.addEventListener("click", () => selectProvince(neighbor)); name.append(button);
    const length = document.createElement("td"); length.textContent = `${edge.shared_boundary_length_km.toLocaleString()} km`;
    const grid = document.createElement("td"); grid.textContent = edge.sampled_grid_support ? `${edge.sampled_grid_cross_edge_pair_count.toLocaleString()} neighboring cell pairs` : "not visible at 0.25°";
    const evidence = document.createElement("td"); evidence.textContent = "static shared source edge";
    row.append(name, length, grid, evidence); body.append(row);
  });
  const withoutGrid = edges.filter(edge => !edge.sampled_grid_support).length;
  summary.textContent = `${selectedProvince} has ${node.degree} shared-edge neighbors across ${node.shared_boundary_length_km.toLocaleString()} km of encoded Version 4 boundary. ${withoutGrid ? `${withoutGrid} source edge is too small to appear as neighboring cells at the 0.25° display resolution.` : "Every source edge has neighboring-cell support at the 0.25° display resolution."} These are geometric relationships, not measured exchanges.`;
}

function renderHypsometry() {
  const canvas = document.querySelector("#hypsometry-canvas"), context = canvas.getContext("2d");
  const buttons = document.querySelector("#hypsometry-buttons"), body = document.querySelector("#hypsometry-table-body"), summary = document.querySelector("#hypsometry-summary");
  buttons.replaceChildren(); body.replaceChildren();
  hypsometry.archetype_selection.codes.forEach(code => {
    const button = document.createElement("button"); button.type = "button"; button.textContent = code; button.setAttribute("aria-pressed", String(code === selectedProvince)); button.setAttribute("aria-label", `Show ${code} continuous depth prototype`); button.addEventListener("click", () => selectProvince(code)); buttons.append(button);
  });
  context.fillStyle = "#06181e"; context.fillRect(0, 0, canvas.width, canvas.height);
  const province = hypsometry.provinces[selectedProvince];
  if (!province) {
    context.fillStyle = "#8fb4b6"; context.font = "700 18px ui-monospace, monospace"; context.fillText("SELECT ONE OF THE SIX FROZEN PROTOTYPE STATES", 120, 175);
    summary.textContent = `${selectedProvince} is not in the six-state continuous-hypsometry prototype. Select a listed archetype; this absence is not estimated or filled.`;
    const row = document.createElement("tr"), cell = document.createElement("td"); cell.colSpan = 6; cell.textContent = "No prototype curve for this state."; row.append(cell); body.append(row);
    canvas.setAttribute("aria-label", summary.textContent); return;
  }
  const left = 70, right = 25, top = 25, bottom = 45, plotWidth = canvas.width - left - right, plotHeight = canvas.height - top - bottom;
  context.strokeStyle = "#29464d"; context.fillStyle = "#8fb4b6"; context.font = "700 12px ui-monospace, monospace"; context.lineWidth = 1;
  [0,2000,4000,6000,8000].forEach(depth => { const y = top + depth / 8000 * plotHeight; context.beginPath(); context.moveTo(left,y); context.lineTo(canvas.width-right,y); context.stroke(); context.fillText(`${depth.toLocaleString()} m`, 8, y+4); });
  [0,25,50,75,100].forEach(percent => { const x = left + percent / 100 * plotWidth; context.fillText(`${percent}%`, x-10, canvas.height-15); });
  const draw = (record, color, dashed) => { context.beginPath(); context.setLineDash(dashed ? [9,6] : []); record.depth_quantile_m.forEach((depth,index) => { const x=left+index/100*plotWidth, y=top+Math.min(depth,8000)/8000*plotHeight; if(index===0) context.moveTo(x,y); else context.lineTo(x,y); }); context.strokeStyle=color; context.lineWidth=4; context.stroke(); context.setLineDash([]); };
  draw(province.fine_0_25_degree,"#63e2d8",false); draw(province.coarse_0_5_degree_center_screen,"#ffe078",true);
  const rows = [["0.25°",province.fine_0_25_degree],["0.5°",province.coarse_0_5_degree_center_screen]];
  rows.forEach(([label,record]) => { const row=document.createElement("tr"); const values=[label,`${record.selected_depth_quantiles_m.p10.toLocaleString()} m`,`${record.selected_depth_quantiles_m.p50.toLocaleString()} m`,`${record.selected_depth_quantiles_m.p90.toLocaleString()} m`,`${record.area_weighted_mean_depth_m.toLocaleString()} m`,`${(record.shelf_area_fraction_lt_200m*100).toFixed(1)}%`]; values.forEach(value=>{const cell=document.createElement("td");cell.textContent=value;row.append(cell);}); body.append(row); });
  const fine=province.fine_0_25_degree, delta=province.sensitivity.coarse_minus_fine_mean_depth_m;
  summary.textContent = `${selectedProvince}, ${province.archetype_rationale}: the 0.25° area-weighted seafloor distribution runs from ${fine.minimum_depth_m.toLocaleString()} to ${fine.maximum_depth_m.toLocaleString()} m; its median is ${fine.selected_depth_quantiles_m.p50.toLocaleString()} m and ${(fine.shelf_area_fraction_lt_200m*100).toFixed(1)}% lies shallower than 200 m. The 0.5° mean-depth screen changes the mean by ${delta>=0?"+":""}${delta.toLocaleString()} m.`;
  canvas.setAttribute("aria-label", `${summary.textContent} Solid teal is the 0.25 degree curve; dashed gold is the 0.5 degree sensitivity curve.`);
}

function buildMollweideAssignments(rows, columns) {
  const projected = new Int16Array(rows * columns).fill(-2);
  const rootTwo = Math.SQRT2;
  for (let displayRow = 0; displayRow < rows; displayRow += 1) {
    const y = (1 - (displayRow + 0.5) / rows * 2) * rootTwo;
    const theta = Math.asin(Math.max(-1, Math.min(1, y / rootTwo)));
    const cosine = Math.cos(theta);
    for (let column = 0; column < columns; column += 1) {
      const x = ((column + 0.5) / columns * 2 - 1) * 2 * rootTwo;
      const longitudeRadians = cosine < 1e-10 ? 0 : Math.PI * x / (2 * rootTwo * cosine);
      if (Math.abs(longitudeRadians) > Math.PI) continue;
      const latitudeRadians = Math.asin(Math.max(-1, Math.min(1, (2 * theta + Math.sin(2 * theta)) / Math.PI)));
      const longitude = longitudeRadians * 180 / Math.PI;
      const latitude = latitudeRadians * 180 / Math.PI;
      const sourceColumn = Math.round((longitude - footprints.grid.longitude_start) / footprints.grid.spacing_degrees);
      const sourceRow = Math.round((latitude - footprints.grid.latitude_start) / footprints.grid.spacing_degrees);
      if (sourceRow >= 0 && sourceRow < rows && sourceColumn >= 0 && sourceColumn < columns) projected[displayRow * columns + column] = footprintAssignments[sourceRow * columns + sourceColumn];
    }
  }
  return projected;
}

function renderFootprint() {
  const canvas = document.querySelector("#footprint-canvas");
  const context = canvas.getContext("2d");
  const [rows, columns] = footprints.grid.shape;
  if (!footprintMollweideAssignments) footprintMollweideAssignments = buildMollweideAssignments(rows, columns);
  const image = context.createImageData(columns, rows);
  const selectedIndex = footprintCodeIndex.get(selectedProvince);
  const provinceByCode = new Map(data.provinces.map(province => [province.code, province]));
  const background = hexRgb("#06181e"), boundary = hexRgb("#8aa3a5"), selected = hexRgb("#63e2d8"), selectedEdge = hexRgb("#ffe078");
  const biomeRgb = new Map(footprintCodes.map(code => [code, hexRgb(biomeMapColors[provinceByCode.get(code)?.biome] ?? "#38545b")]));
  const quantityRgb = new Map(footprintCodes.map(code => [code, hexRgb(rankColor(provinceRanks[footprintMapMode]?.get(code) ?? 54))]));
  const floorRgb = new Map(footprintCodes.map(code => [code, hexRgb(floorMapColors[fingerprints.provinces[code]?.floor_character] ?? "#38545b")]));
  const bandInfo = selectedBandInfo();
  const bandRgb = new Map(footprintCodes.map(code => {
    const rank = bandInfo.ranks.get(code);
    return [code, hexRgb(rank ? rankColor(rank, bandInfo.count) : "#313a3d")];
  }));
  const graphNode = adjacency.nodes.find(item => item.osw_code === selectedProvince);
  const selectedNeighbors = new Set(graphNode?.neighbors ?? []);
  for (let displayRow = 0; displayRow < rows; displayRow += 1) {
    for (let column = 0; column < columns; column += 1) {
      const sourceOffset = displayRow * columns + column;
      const displayOffset = sourceOffset * 4;
      const codeIndex = footprintMollweideAssignments[sourceOffset];
      let rgb = background;
      if (codeIndex >= 0) {
        const code = footprintCodes[codeIndex];
        rgb = footprintMapMode === "neighbors"
          ? hexRgb(code === selectedProvince ? neighborMapColors.selected : (selectedNeighbors.has(code) ? neighborMapColors.neighbor : neighborMapColors.other))
          : (footprintMapMode === "family" && codeIndex === selectedIndex ? selected : (footprintMapMode === "family" ? biomeRgb.get(code) : (footprintMapMode === "floor" ? floorRgb.get(code) : (footprintMapMode === "band" ? bandRgb.get(code) : quantityRgb.get(code)))));
        const east = column + 1 < columns ? footprintMollweideAssignments[sourceOffset + 1] : -2;
        const north = displayRow + 1 < rows ? footprintMollweideAssignments[sourceOffset + columns] : -2;
        if (east !== codeIndex || north !== codeIndex) rgb = codeIndex === selectedIndex || east === selectedIndex || north === selectedIndex ? selectedEdge : boundary;
      }
      image.data[displayOffset] = rgb[0]; image.data[displayOffset + 1] = rgb[1]; image.data[displayOffset + 2] = rgb[2]; image.data[displayOffset + 3] = 255;
    }
  }
  context.putImageData(image, 0, 0);

  const crosswalk = footprints.crosswalk.find(item => item.osw_code === selectedProvince);
  const summary = footprints.provinces[selectedProvince];
  const profile = document.querySelector("#footprint-depth-profile");
  const legend = document.querySelector("#footprint-legend");
  const mapLegend = document.querySelector("#footprint-map-legend");
  const bands = [["epipelagic","<200 m"],["mesopelagic","200–<1,000 m"],["bathypelagic","1,000–<4,000 m"],["abyssopelagic","4,000–<6,000 m"],["hadalpelagic","≥6,000 m"]];
  profile.replaceChildren();
  legend.replaceChildren();
  const mapLabels = {family:"ecological families",area:"sampled wet-area rank · largest first",volume:"sampled water-volume rank · largest first",depth:"area-weighted mean-depth rank · deepest first",floor:"dominant seafloor-depth character",band:`${bandInfo.band.name} water-volume rank · largest first`,neighbors:"source-edge neighbors · geometry only"};
  document.querySelector("#footprint-map-label").textContent = `MAP FIELD · ${mapLabels[footprintMapMode].toUpperCase()}`;
  if (footprintMapMode === "neighbors") {
    appendLegend(mapLegend, [[neighborMapColors.selected,"selected state"],[neighborMapColors.neighbor,"shared-edge neighbor"],[neighborMapColors.other,"not an immediate neighbor"],["#8aa3a5","hairline = rasterized province edge"]]);
  } else if (footprintMapMode === "family") {
    appendLegend(mapLegend, [...Object.entries(biomeMapColors).map(([label, color]) => [color, label]), ["#63e2d8", "selected province"]]);
  } else if (footprintMapMode === "floor") {
    appendLegend(mapLegend, [[floorMapColors["shelf-led"],"shelf-led · bottom <200 m dominant"],[floorMapColors["deep-floor-led"],"deep-floor-led · bottom 1,000–<4,000 m dominant"],[floorMapColors["abyssal-floor-led"],"abyssal-floor-led · bottom 4,000–<6,000 m dominant"],["#ffe078","gold edge = selected province"]]);
  } else if (footprintMapMode === "band") {
    appendLegend(mapLegend, [...rankLegendEntries(bandInfo.count), ["#313a3d",`no sampled ${bandInfo.band.name} volume`], ["#ffe078","gold edge = selected province"]]);
  } else {
    appendLegend(mapLegend, [...quantityMapColors.map((color, index) => [color, index === 4 ? "ranks 45–54" : `ranks ${index * 11 + 1}–${index * 11 + 11}`]), ["#ffe078", "gold edge = selected province"]]);
  }
  renderPassport(summary, fingerprints.provinces[selectedProvince], bandInfo);
  if (!summary) {
    document.querySelector("#footprint-profile-label").textContent = "DEPTH PROFILE UNAVAILABLE IN VERSION 4";
    document.querySelector("#footprint-status").textContent = "OLDER 1995 IDENTITY · NO SEPARATE V4 FOOTPRINT";
    document.querySelector("#footprint-summary").textContent = `${selectedProvince}: ${crosswalk.note} The map retains all 54 Version 4 territories but highlights none; OSW will not invent a boundary for this older identity.`;
    profile.setAttribute("aria-label", `${selectedProvince} has no separate Longhurst Version 4 footprint or depth distribution.`);
  } else {
    const fractions = footprintProfileMode === "volume" ? summary.water_volume_fraction_by_depth_band : summary.wet_area_fraction_by_seafloor_band;
    const profileNoun = footprintProfileMode === "volume" ? "water volume" : "seafloor-reaching area";
    document.querySelector("#footprint-profile-label").textContent = `${profileNoun.toUpperCase()} BY DEPTH BAND`;
    bands.forEach(([key, label]) => {
      const fraction = fractions[key] ?? 0;
      const segment = document.createElement("span"); segment.style.width = `${fraction * 100}%`; segment.style.background = depthMapColors[key]; segment.title = `${label}: ${(fraction * 100).toFixed(1)}%`;
      profile.append(segment);
      const item = document.createElement("span"), swatch = document.createElement("i"); swatch.style.background = depthMapColors[key]; item.append(swatch, document.createTextNode(`${label} · ${(fraction * 100).toFixed(1)}%`)); legend.append(item);
    });
    const direct = (summary.wet_area_fraction_by_tid_class.direct_measurement ?? 0) * 100;
    const indirect = (summary.wet_area_fraction_by_tid_class.indirect_or_interpolated ?? 0) * 100;
    const alias = crosswalk.source_code === selectedProvince ? "direct code match" : `${crosswalk.source_code} source-code alias`;
    document.querySelector("#footprint-status").textContent = `54-PROVINCE VERSION 4 · ${alias.toUpperCase()}`;
    document.querySelector("#footprint-summary").textContent = `${selectedProvince} / ${crosswalk.source_code}: the bar shows ${profileNoun} by depth band. ${summary.wet_sample_count.toLocaleString()} wet 0.25° samples represent approximately ${summary.sampled_wet_area_km2.toLocaleString()} km² and ${approximateVolume(summary.sampled_water_volume_km3)} of water under sampled prismatic integration. Area-weighted mean water depth is ${summary.area_weighted_mean_water_depth_m.toLocaleString()} m; wet seabed depths span ${summary.minimum_wet_depth_m.toLocaleString()}–${summary.maximum_wet_depth_m.toLocaleString()} m. Source-type area is ${direct.toFixed(1)}% direct measurement and ${indirect.toFixed(1)}% indirect/interpolated; remaining area is mixed/unknown. The source polygon also contains ${summary.non_wet_geometry_sample_count.toLocaleString()} GEBCO non-wet centers from coastline/grid disagreement.`;
    profile.setAttribute("aria-label", `${selectedProvince} ${profileNoun} distribution: ${bands.map(([key,label]) => `${label} ${((fractions[key] ?? 0) * 100).toFixed(1)}%`).join(", ")}.`);
  }
  canvas.setAttribute("aria-label", `Oceanic Mollweide world map of the 54 source-aligned Longhurst Version 4 province footprints, filled by ${mapLabels[footprintMapMode]}. ${document.querySelector("#footprint-summary").textContent}`);
  renderNeighborTable();
  renderHypsometry();
  renderDepthLadder();
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
  if (["volume", "seafloor"].includes(params.get("profile"))) footprintProfileMode = params.get("profile");
  if (["family", "area", "volume", "depth", "floor", "band", "neighbors"].includes(params.get("map"))) footprintMapMode = params.get("map");

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
  document.querySelectorAll("[data-footprint-profile]").forEach(button => {
    button.setAttribute("aria-pressed", String(button.dataset.footprintProfile === footprintProfileMode));
    button.addEventListener("click", () => {
      footprintProfileMode = button.dataset.footprintProfile;
      document.querySelectorAll("[data-footprint-profile]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
      const url = new URL(window.location.href); url.searchParams.set("profile", footprintProfileMode); history.replaceState(null, "", url);
      renderFootprint();
    });
  });
  document.querySelectorAll("[data-footprint-map]").forEach(button => {
    button.setAttribute("aria-pressed", String(button.dataset.footprintMap === footprintMapMode));
    button.addEventListener("click", () => {
      footprintMapMode = button.dataset.footprintMap;
      document.querySelectorAll("[data-footprint-map]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
      const url = new URL(window.location.href); url.searchParams.set("map", footprintMapMode); history.replaceState(null, "", url);
      renderFootprint();
    });
  });
  window.matchMedia("(max-width: 700px)").addEventListener("change", renderDepthLadder);
  render();
}

init();
