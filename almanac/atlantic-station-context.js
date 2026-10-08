"use strict";
(() => {
  const source = "research/atlantic-cruise-station-context.json";
  let loading;
  function load() {
    if (loading) return loading;
    loading = (async () => {
      const worker = new Worker("index-worker.js?v=station-context-1"), pending = new Map();
      let serial = 0;
      const fail = error => {
        for (const item of pending.values()) {clearTimeout(item.timer); item.reject(error);}
        pending.clear(); worker.terminate();
      };
      worker.onerror = () => fail(Error("Checked station source worker failed"));
      worker.onmessage = ({data}) => {
        const item = pending.get(data.id); if (!item) return;
        clearTimeout(item.timer); pending.delete(data.id);
        if (data.result.ok) item.resolve(data.result); else item.reject(Error(data.result.error));
      };
      const request = (action, value) => new Promise((resolve, reject) => {
        const id = ++serial, timer = setTimeout(() => fail(Error("Checked station source timed out")), 90000);
        pending.set(id, {resolve, reject, timer}); worker.postMessage({id, action, value});
      });
      try {
        await request("load");
        const [document, binary] = await Promise.all([
          request("document", {document: source}), request("cartography_binary")]);
        const audit = document.value;
        if (audit.schema !== "osw.atlantic-cruise-station-context.v1") throw Error("Unsupported station context schema");
        const project = await window.createOswCartography(binary.binary);
        return {audit, project};
      } finally {worker.terminate();}
    })();
    return loading;
  }
  window.renderAtlanticStationContext = function(container, records) {
    const node = (tag, text, parent) => {
      const element = document.createElement(tag); element.textContent = text; parent.append(element); return element;
    };
    const details = node("details", "", container);
    details.className = "cruise-station-context";
    node("summary", "Show cruise sampling locations", details);
    node("p", "Reported hydrographic station events within the paper’s sampling window. Points show sampling context; the paper’s current boundary station pairing remains unresolved.", details);
    node("p", "Yellow points mark selected ROS/CTD casts on the OSW equirectangular basemap. OSW state boundaries are background context. Casts can sample other flows and depths; this selection does not reconstruct the inverse model’s station subset.", details);
    const label = node("label", "Measurement cruise ", details), select = node("select", "", label);
    select.setAttribute("aria-label", "Cruise sampling map measurement");
    for (const record of records) {
      const option = node("option", `${record.hydrographic_section_context.cruise_id} · ${record.approximate_width_km} km`, select);
      option.value = record.id;
    }
    const initial = new URL(location.href).searchParams.get("phase");
    if (records.some(r => r.id === initial)) select.value = initial;
    const status = node("p", "", details); status.setAttribute("role", "status");
    const drawing = node("div", "", details), receipt = node("p", "", details);
    let generation = 0, started = false;
    async function render() {
      const token = ++generation;
      window.oswAtlanticStationContext = null;
      drawing.replaceChildren(); receipt.replaceChildren();
      status.textContent = "Loading checked cruise station context…";
      try {
        const {audit, project} = await load();
        if (token !== generation || !details.isConnected) return;
        const context = audit.measurement_contexts.find(row => row.measurement_id === select.value);
        if (!context || context.geometry_role !== "cruise_sampling_context_not_current_boundary" ||
            context.current_footprint_eligible !== false || context.state_intersection_eligible !== false ||
            context.boundary_station_mapping_status !== "unresolved") throw Error("Unsupported station context scope");
        window.oswAtlanticStationContext = context;
        if (!context.points.length) {
          status.textContent = context.status === "source_date_conflict"
            ? "Map unavailable: the source summary prints 2005 dates for this 2007 cruise. These dates need independent correction."
            : "Map unavailable: station coordinates for this cruise have not been recovered.";
        } else {
          const ns = "http://www.w3.org/2000/svg", svg = document.createElementNS(ns, "svg");
          const view = project({op: "fit", coordinates: context.points.map(p => p.coordinates)}).view_box;
          svg.setAttribute("viewBox", view.join(" ")); svg.setAttribute("role", "img");
          svg.setAttribute("class", "section-locator-map");
          svg.setAttribute("aria-label", `${context.paper_cruise_id}: ${context.point_count} reported hydrographic casts. Sampling points only; current edges unresolved.`);
          const ground = document.createElementNS(ns, "image");
          ground.setAttribute("href", "../figures/ocean-motion-dashboard-ground.svg");
          for (const [key, value] of Object.entries({x: 60, y: 90, width: 1480, height: 740, opacity: .65})) ground.setAttribute(key, value);
          svg.append(ground);
          for (const point of context.points) {
            const coordinates = project({op: "project", coordinates: point.coordinates}).point;
            const dot = document.createElementNS(ns, "circle"), title = document.createElementNS(ns, "title");
            dot.setAttribute("cx", coordinates[0]); dot.setAttribute("cy", coordinates[1]);
            dot.setAttribute("r", view[2] / 220); dot.setAttribute("fill", "#ffe090");
            dot.dataset.sourceLine = point.source_line;
            title.textContent = `Station ${point.station_label}, cast ${point.cast_label}, ${point.event_code}; ${point.sampling_date} UTC ${point.sampling_time_utc}; ${point.raw_latitude}, ${point.raw_longitude}; source line ${point.source_line}`;
            dot.append(title); svg.append(dot);
          }
          drawing.append(svg);
          const tableDetails = node("details", "", drawing);
          node("summary", "Station coordinates and source lines", tableDetails);
          const scroll = node("div", "", tableDetails); scroll.className = "cruise-span-scroll"; scroll.tabIndex = 0;
          scroll.setAttribute("role", "region"); scroll.setAttribute("aria-label", "Station coordinates; scroll horizontally for detail");
          const table = node("table", "", scroll); table.className = "cruise-span-table";
          node("caption", "Selected reported station events; source degrees and minutes retained", table);
          const header = node("tr", "", node("thead", "", table));
          for (const name of ["Station / cast / event", "Date / UTC time", "Latitude", "Longitude", "Source line"])
            node("th", name, header).scope = "col";
          const body = node("tbody", "", table);
          for (const point of context.points) {
            const row = node("tr", "", body);
            for (const value of [`${point.station_label} / ${point.cast_label} / ${point.event_code}`,
                                `${point.sampling_date} / ${point.sampling_time_utc}`, point.raw_latitude,
                                point.raw_longitude, point.source_line]) node("td", String(value), row);
          }
          status.textContent = `${context.point_count} reported casts · ${context.sampling_window.start} to ${context.sampling_window.end}. Sampling locations; no current boundary or width is drawn. Coordinate datum and uncertainty are unreported.`;
          if (context.date_reconciliation_file) {
            status.textContent += " Dates and times follow the corrected bottle archive; original summary timestamps remain in the source records.";
            const correction = node("a", "Inspect the original-to-corrected timestamp matches", node("p", "", drawing));
            correction.href = "query.html?source-q=" + encodeURIComponent(JSON.stringify({document: context.date_reconciliation_file, pointer: "/records", limit: 100})) + "#source-query-title";
          }
        }
        if (context.cruise_url) {
          const provider = node("a", "Original cruise archive", receipt); provider.href = context.cruise_url;
          node("span", ` · summary SHA-256 ${context.source_sha256.slice(0, 12)} · `, receipt);
        }
        const query = {document: source, pointer: "/measurement_contexts", filters: [{field: "record.measurement_id", op: "eq", value: context.measurement_id}], limit: 25};
        const inspect = node("a", "Inspect and download exact station records", receipt);
        inspect.href = "query.html?source-q=" + encodeURIComponent(JSON.stringify(query)) + "#source-query-title";
      } catch (error) {
        if (token !== generation || !details.isConnected) return;
        window.oswAtlanticStationContext = null; drawing.replaceChildren(); receipt.replaceChildren();
        status.textContent = `Station context unavailable: ${error.message}`;
      }
    }
    select.addEventListener("change", render);
    details.addEventListener("toggle", () => {if (details.open && !started) {started = true; render();}});
  };
})();
