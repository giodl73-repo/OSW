"use strict";

const decisionsData = window.OSW_DECISIONS;
let decisionEdge = "SANT--SSTC", decisionFilter = "all";

function selectedDecision() {
  return decisionsData.matrix.find(item => item.edge_id === decisionEdge);
}

function drawDecisionGeography(canvas, markTestedSegment) {
  const context = canvas.getContext("2d"), image = context.createImageData(canvas.width, canvas.height);
  for (let y = 0; y < canvas.height; y += 1) {
    for (let x = 0; x < canvas.width; x += 1) {
      const sample = mollweideSample(x, y, canvas.width, canvas.height), offset = (y * canvas.width + x) * 4;
      let rgb = hex("#f8f8f4");
      if (sample.index >= 0) {
        rgb = hex("#eef0ec");
        const east = x + 1 < canvas.width ? mollweideSample(x + 1, y, canvas.width, canvas.height).index : -2;
        const south = y + 1 < canvas.height ? mollweideSample(x, y + 1, canvas.width, canvas.height).index : -2;
        if (east !== sample.index || south !== sample.index) rgb = hex("#839694");
      }
      image.data.set([...rgb, 255], offset);
    }
  }
  context.putImageData(image, 0, 0);
  if (markTestedSegment) {
    const points = exchangeData.geometry.faces.map(face => mollweidePoint(face.longitude_deg, face.latitude_deg, canvas.width, canvas.height));
    context.beginPath(); points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y));
    context.strokeStyle = "#a63f55"; context.lineWidth = Math.max(4, canvas.width / 100); context.lineCap = "round"; context.stroke();
  }
  canvas.setAttribute("aria-label", markTestedSegment ? "Candidate physical-overlay map beside the unchanged source edition. One 16-face SANT to SSTC segment is demoted; all source edges remain." : "Unchanged Longhurst Version 4 source geography with all 128 reference edges retained.");
}

function renderDecisionsMap() {
  drawDecisionGeography(document.querySelector("#decisions-map"), true);
  drawDecisionGeography(document.querySelector("#source-revision-map"), false);
  drawDecisionGeography(document.querySelector("#candidate-revision-map"), true);
}

function renderDecisionScore() {
  const item = selectedDecision(), grid = document.querySelector("#decision-score-grid"); grid.replaceChildren();
  appendDefinition(grid, "Border", item.edge_id);
  appendDefinition(grid, "Disposition", item.disposition);
  appendDefinition(grid, "Global source edge", `${item.geometry.shared_boundary_length_km.toLocaleString()} km`);
  appendDefinition(grid, "Missing families", String(item.uncertainty.missing.length));
  document.querySelector("#decision-finding").textContent = `${item.rationale} Upgrade/falsification rule: ${item.falsification_or_upgrade}`;
}

function shortStatus(record) {
  return record.status === "unknown" ? "unknown" : record.status.replaceAll("_", " ");
}

function renderDecisionTable() {
  const body = document.querySelector("#decision-matrix-body"); body.replaceChildren();
  const rows = decisionsData.matrix.filter(item => decisionFilter === "all" || item.disposition === decisionFilter);
  rows.forEach(item => body.append(tableRow([
    item.edge_id, item.disposition, shortStatus(item.hydrographic_content), shortStatus(item.exchange), shortStatus(item.stability), shortStatus(item.event_route), item.uncertainty.missing.slice(0, 3).join("; "),
  ])));
  document.querySelector("#decision-table-count").textContent = `${rows.length} border${rows.length === 1 ? "" : "s"} shown`;
}

function updateDecisionUrl() {
  const params = new URLSearchParams(location.search); params.set("stage", "decisions"); params.set("edge", decisionEdge); params.set("filter", decisionFilter); history.replaceState(null, "", `?${params}`);
}

function renderDecisions() { renderDecisionsMap(); renderDecisionScore(); renderDecisionTable(); }

const decisionEdgeSelect = document.querySelector("#decision-edge-select"), decisionFilterSelect = document.querySelector("#decision-filter-select");
decisionsData.matrix.forEach(item => decisionEdgeSelect.append(option(item.edge_id, `${item.edge_id} · ${item.disposition}`)));
const decisionParams = new URLSearchParams(location.search);
if (decisionsData.matrix.some(item => item.edge_id === decisionParams.get("edge"))) decisionEdge = decisionParams.get("edge");
if (["all", "unknown", "demote"].includes(decisionParams.get("filter"))) decisionFilter = decisionParams.get("filter");
decisionEdgeSelect.value = decisionEdge; decisionFilterSelect.value = decisionFilter;
decisionEdgeSelect.addEventListener("change", () => { decisionEdge = decisionEdgeSelect.value; updateDecisionUrl(); renderDecisionScore(); });
decisionFilterSelect.addEventListener("change", () => { decisionFilter = decisionFilterSelect.value; updateDecisionUrl(); renderDecisionTable(); });
