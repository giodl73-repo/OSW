"use strict";

const stabilityData = window.OSW_STABILITY;
let stabilityMonth = "201802", stabilityDepth = "0-200m";

function stabilityRecord() {
  return stabilityData.records.find(item => item.month === stabilityMonth && item.depth_support === stabilityDepth);
}

function renderStabilityMap() {
  const canvas = document.querySelector("#stability-map"), context = canvas.getContext("2d");
  const bounds = {west: -54, east: -48, south: -50.25, north: -45.5};
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
      const index = at(lon, lat), east = at(lon + 0.04, lat), south = at(lon, lat - 0.04);
      let rgb = index < 0 ? hex("#f8f8f4") : hex("#e6e7e2");
      if (index >= 0 && (east !== index || south !== index)) rgb = hex("#96a6a3");
      image.data.set([...rgb, 255], (y * canvas.width + x) * 4);
    }
  }
  context.putImageData(image, 0, 0);
  const record = stabilityRecord(), base = -51.375, pixelsPerFace = 0.25 / (bounds.east - bounds.west) * canvas.width;
  const xAt = offset => (base + offset * 0.25 - bounds.west) / (bounds.east - bounds.west) * canvas.width;
  const [envelopeLow, envelopeHigh] = record.front_envelope_offsets_native_faces;
  context.fillStyle = "rgba(166,63,85,.14)";
  context.fillRect(xAt(envelopeLow) - pixelsPerFace / 2, 54, (envelopeHigh - envelopeLow + 1) * pixelsPerFace, canvas.height - 100);
  const drawLine = (offset, color, width, dash = []) => {
    context.beginPath(); context.moveTo(xAt(offset), 54); context.lineTo(xAt(offset), canvas.height - 46);
    context.strokeStyle = color; context.lineWidth = width; context.setLineDash(dash); context.stroke(); context.setLineDash([]);
  };
  drawLine(0, "#ad7a16", 7); drawLine(1, "#087f83", 4); drawLine(record.diagnosed_peak_offset_native_faces, "#a63f55", 5, [10, 6]);
  context.fillStyle = "#132b32"; context.font = "700 17px Georgia"; context.fillText("SANT", 32, 38); context.fillText("SSTC", canvas.width - 78, 38);
  const detection = record.front_detected ? "passes the frozen front detector" : "does not pass the frozen front detector";
  canvas.setAttribute("aria-label", `${stabilityMonth}, ${stabilityDepth}: the strongest local temperature gradient is ${record.diagnosed_peak_offset_native_faces} native faces from the static SANT to SSTC edge and ${detection}. The static edge does not match.`);
}

function renderStabilityScore() {
  const record = stabilityRecord(), grid = document.querySelector("#stability-score-grid");
  grid.replaceChildren();
  appendDefinition(grid, "Peak offset", `${record.diagnosed_peak_offset_native_faces > 0 ? "+" : ""}${record.diagnosed_peak_offset_native_faces} faces`);
  appendDefinition(grid, "Displacement", `${record.diagnosed_peak_displacement_km.toFixed(1)} km`);
  appendDefinition(grid, "Peak gradient", `${record.peak_gradient_degC_per_km.toFixed(4)} °C/km`);
  appendDefinition(grid, "Prominence", `${record.peak_to_local_median_ratio.toFixed(2)}× local median`);
  document.querySelector("#stability-caption").textContent = `${stabilityMonth} · ${stabilityDepth}`;
  const detected = record.front_detected ? "passes" : "fails";
  document.querySelector("#stability-finding").textContent = `The local peak ${detected} the frozen detector but sits ${Math.abs(record.diagnosed_peak_offset_native_faces)} faces from the source edge. Static-edge match: no. This is a temperature-gradient result, not transport or a material barrier.`;
}

function renderStabilityMatrix() {
  const body = document.querySelector("#stability-matrix-body"); body.replaceChildren();
  const depths = [...new Set(stabilityData.records.map(item => item.depth_support))];
  const months = [...new Set(stabilityData.records.map(item => item.month))];
  depths.forEach(depth => {
    const values = [depth];
    months.forEach(month => {
      const record = stabilityData.records.find(item => item.month === month && item.depth_support === depth);
      const prefix = record.front_detected ? "detected" : "below floor";
      values.push(`${prefix} · ${record.diagnosed_peak_offset_native_faces > 0 ? "+" : ""}${record.diagnosed_peak_offset_native_faces}`);
    });
    body.append(tableRow(values));
  });
}

function renderStability() { renderStabilityMap(); renderStabilityScore(); renderStabilityMatrix(); }

const stabilityMonthSelect = document.querySelector("#stability-month-select"), stabilityDepthSelect = document.querySelector("#stability-depth-select");
[...new Set(stabilityData.records.map(item => item.month))].forEach(month => stabilityMonthSelect.append(option(month, `${month.slice(0, 4)}-${month.slice(4)}`)));
[...new Set(stabilityData.records.map(item => item.depth_support))].forEach(depth => stabilityDepthSelect.append(option(depth)));
stabilityMonthSelect.addEventListener("change", () => { stabilityMonth = stabilityMonthSelect.value; renderStability(); });
stabilityDepthSelect.addEventListener("change", () => { stabilityDepth = stabilityDepthSelect.value; renderStability(); });
