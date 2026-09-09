"use strict";

const exchangeData = window.OSW_EXCHANGE;
let exchangeMonth = "201802";

function exchangeMonthRecord() {
  return exchangeData.months.find(item => item.month === exchangeMonth);
}

function mollweidePoint(longitude, latitude, width, height) {
  const phi = latitude * Math.PI / 180;
  let theta = phi;
  for (let iteration = 0; iteration < 12; iteration += 1) {
    const denominator = 2 + 2 * Math.cos(2 * theta);
    if (Math.abs(denominator) < 1e-10) break;
    theta -= (2 * theta + Math.sin(2 * theta) - Math.PI * Math.sin(phi)) / denominator;
  }
  return {x: ((longitude * Math.PI / 180) * Math.cos(theta) / Math.PI + 1) * width / 2, y: (1 - Math.sin(theta)) * height / 2};
}

function renderExchangeMap() {
  const canvas = document.querySelector("#exchange-map"), context = canvas.getContext("2d");
  const bounds = {west: -54, east: -48, south: -50.25, north: -45.5};
  const at = (lon, lat) => {
    const column = Math.round((lon - footprints.grid.longitude_start) / footprints.grid.spacing_degrees);
    const row = Math.round((lat - footprints.grid.latitude_start) / footprints.grid.spacing_degrees);
    return row >= 0 && row < 720 && column >= 0 && column < 1440 ? assignments[row * 1440 + column] : -2;
  };
  const image = context.createImageData(canvas.width, canvas.height);
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
  const point = (lon, lat) => ({x: (lon - bounds.west) / (bounds.east - bounds.west) * canvas.width, y: (bounds.north - lat) / (bounds.north - bounds.south) * canvas.height});
  const draw = (lonKey, latKey, color, width) => {
    const points = exchangeData.geometry.faces.map(face => point(face[lonKey], face[latKey]));
    context.beginPath();
    points.forEach((p, index) => index ? context.lineTo(p.x, p.y) : context.moveTo(p.x, p.y));
    context.strokeStyle = color; context.lineWidth = width; context.lineCap = "round"; context.lineJoin = "round"; context.stroke();
  };
  draw("control_longitude_deg", "control_latitude_deg", "#087f83", 4);
  draw("longitude_deg", "latitude_deg", "#ad7a16", 7);
  context.fillStyle = "#132b32"; context.font = "700 17px Georgia";
  context.fillText("SANT", 32, 42); context.fillText("SSTC", canvas.width - 78, 42);
  context.font = "12px Inter, sans-serif"; context.fillStyle = "#5f7478";
  context.fillText("54°W", 12, canvas.height - 12); context.fillText("48°W", canvas.width - 44, canvas.height - 12);
  const net = exchangeMonthRecord().boundary.all_depths.adjacent_mean["0.0"].net_first_to_second_Sv;
  canvas.setAttribute("aria-label", `Regional native-coordinate detail from 54 to 48 degrees west and 50.25 to 45.5 degrees south, showing 16 measured SANT to SSTC source-edge faces and paired one-cell controls. ${exchangeMonth} net volume is ${Math.abs(net).toFixed(2)} sverdrups ${net >= 0 ? "from SANT to SSTC" : "from SSTC to SANT"}.`);
}

function appendDefinition(grid, term, value) {
  const wrapper = document.createElement("div"), dt = document.createElement("dt"), dd = document.createElement("dd");
  dt.textContent = term; dd.textContent = value; wrapper.append(dt, dd); grid.append(wrapper);
}

function renderExchangeScore() {
  const month = exchangeMonthRecord();
  const result = month.boundary.all_depths.adjacent_mean["0.0"];
  const control = month.matched_displaced_control.all_depths.adjacent_mean["0.0"];
  const grid = document.querySelector("#exchange-score-grid");
  grid.replaceChildren();
  appendDefinition(grid, "Net volume", `${result.net_first_to_second_Sv.toFixed(2)} Sv`);
  appendDefinition(grid, "Gross exchange", `${result.gross_exchange_Sv.toFixed(2)} Sv`);
  appendDefinition(grid, "Net thermal", `${result.net_first_to_second_PW.toFixed(3)} PW`);
  appendDefinition(grid, "Control net", `${control.net_first_to_second_Sv.toFixed(2)} Sv`);
  const direction = result.net_first_to_second_Sv >= 0 ? "SANT → SSTC" : "SSTC → SANT";
  document.querySelector("#exchange-finding").textContent = `${exchangeMonth}: net volume points ${direction}. Gross opposing exchange is ${result.gross_exchange_Sv.toFixed(2)} Sv. The parallel displaced control is ${control.net_first_to_second_Sv.toFixed(2)} Sv, so this month alone cannot make the source edge a unique physical barrier.`;
}

function tableRow(values) {
  const row = document.createElement("tr");
  values.forEach(value => { const cell = document.createElement("td"); cell.textContent = value; row.append(cell); });
  return row;
}

function renderExchangeTables() {
  const month = exchangeMonthRecord();
  const depthBody = document.querySelector("#depth-body");
  depthBody.replaceChildren();
  month.boundary.by_depth.forEach(item => {
    const result = item.reference_and_collocation_cases.adjacent_mean["0.0"];
    depthBody.append(tableRow([item.depth_support, item.wet_face_level_count.toLocaleString(), `${result.positive_first_to_second_Sv.toFixed(2)} Sv`, `${Math.abs(result.negative_second_to_first_Sv).toFixed(2)} Sv`, `${result.gross_exchange_Sv.toFixed(2)} Sv`, `${result.net_first_to_second_Sv.toFixed(2)} Sv`, `${result.net_first_to_second_PW.toFixed(3)} PW`]));
  });
  const seasonBody = document.querySelector("#season-body");
  seasonBody.replaceChildren();
  exchangeData.months.forEach(item => {
    const result = item.boundary.all_depths.adjacent_mean["0.0"];
    const control = item.matched_displaced_control.all_depths.adjacent_mean["0.0"];
    seasonBody.append(tableRow([`${item.month.slice(0, 4)}-${item.month.slice(4)}`, `${result.net_first_to_second_Sv.toFixed(2)} Sv`, `${control.net_first_to_second_Sv.toFixed(2)} Sv`, `${result.net_first_to_second_PW.toFixed(3)} PW`, result.net_first_to_second_Sv >= 0 ? "SANT → SSTC" : "SSTC → SANT"]));
  });
}

function renderExchange() { renderExchangeMap(); renderExchangeScore(); renderExchangeTables(); }

function setStage(stage, updateUrl = true) {
  const showInventory = stage === "inventory", showExchange = stage === "exchange", showStability = stage === "stability", showEvents = stage === "events", showDecisions = stage === "decisions";
  document.querySelectorAll(".inventory-panel").forEach(item => { item.hidden = !showInventory; });
  document.querySelector("#exchange-panel").hidden = !showExchange;
  document.querySelector("#stability-panel").hidden = !showStability;
  document.querySelector("#events-panel").hidden = !showEvents;
  document.querySelector("#decisions-panel").hidden = !showDecisions;
  document.querySelectorAll(".stage-nav button").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.stage === stage)));
  if (updateUrl) { const params = new URLSearchParams(location.search); params.set("stage", stage); history.replaceState(null, "", `?${params}`); }
  if (showExchange) renderExchange(); else if (showStability) renderStability(); else if (showEvents) renderEvents(); else if (showDecisions) renderDecisions(); else render();
}

const exchangeMonthSelect = document.querySelector("#exchange-month-select");
exchangeData.months.forEach(item => exchangeMonthSelect.append(option(item.month, `${item.month.slice(0, 4)}-${item.month.slice(4)}`)));
exchangeMonthSelect.addEventListener("change", () => { exchangeMonth = exchangeMonthSelect.value; renderExchange(); });
document.querySelectorAll(".stage-nav button:not(:disabled)").forEach(button => button.addEventListener("click", () => setStage(button.dataset.stage)));
const requestedStage = new URLSearchParams(location.search).get("stage");
setStage(["exchange", "stability", "events", "decisions"].includes(requestedStage) ? requestedStage : "inventory", false);
