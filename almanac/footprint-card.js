/* Canonical object-card presentation of Rust-projected figure digitizations. */
window.renderRustOceanFootprintCandidate = function ({ parent, candidate, entityLink, sourceLink, movieContexts = [], plotScene }) {
  const add = (tag, text, host = parent) => {
    const item = document.createElement(tag);
    if (text != null) item.textContent = text;
    host.append(item); return item;
  };
  parent.classList.add("footprint-candidate");
  parent.style.overflowWrap = "anywhere";
  add("h3", `${candidate.observation_date} · Figure-derived SSH contour candidate`);
  add("p", "This outline is an OSW digitization of the paper's instantaneous SSH contour. It is not the material coherent-core boundary or a verified whole-ring footprint. Scientific claim review: pending.");
  if (plotScene !== undefined) {
    if (plotScene.available) {
      const ns = "http://www.w3.org/2000/svg";
      const svg = document.createElementNS(ns, "svg");
      svg.setAttribute("viewBox", plotScene.view_box.join(" "));
      svg.setAttribute("role", "img"); svg.setAttribute("aria-label", plotScene.aria_label);
      svg.dataset.engine = "rust-osw-query-v1";
      svg.style.width = "100%"; svg.style.maxWidth = "600px"; svg.style.height = "auto";
      const group = document.createElementNS(ns, "g");
      group.setAttribute("transform", plotScene.display_transform);
      const path = document.createElementNS(ns, "path");
      path.setAttribute("d", plotScene.polygon_d);
      path.setAttribute("stroke", "currentColor"); path.setAttribute("stroke-width", "2");
      path.setAttribute("vector-effect", "non-scaling-stroke");
      path.setAttribute("stroke-dasharray", "6 3"); path.setAttribute("fill", "none");
      group.append(path); svg.append(group); parent.append(svg);
      add("p", plotScene.coordinate_label);
    } else add("p", plotScene.reason);
    if (plotScene.omitted_features?.length) add("p", `${plotScene.omitted_features.length} unsupported or invalid plot features omitted.`);
  } else add("p", "Contour plot unavailable from the checked Rust object view.");
  add("p", candidate.coordinate_reference_status);
  const list = add("ul", null);
  for (const assessment of candidate.state_assessments) {
    const entry = add("li", null, list);
    entityLink(assessment.state_id, entry);
    add("span", ` (${assessment.state_id.replace("state:", "")})`, entry);
    const range = assessment.display_area_fraction_range.map(value => (value * 100).toFixed(2));
    add("span", ` · ${assessment.intersection_assessment.replaceAll("_", " ")}; nominal display overlap ${(assessment.nominal_display_area_fraction * 100).toFixed(2)}%; tested range ${range.join("–")}%. Containment unresolved.`, entry);
  }
  add("p", "Overlap fractions refer to approximate OSW display geometry. Tested ranges are calibration/segmentation scenarios, not statistical confidence intervals.");
  add("p", candidate.physical_limit);
  add("p", `Source locator: ${candidate.source_locator}. Method: ${candidate.method}`);
  sourceLink(candidate.source_id, parent);
  add("p", "Adapted by OSW from Beron-Vera et al. (2018), Figure 2; original authors retain copyright. The source figure image is not packaged.");
  const license = add("a", "Source license: CC BY 4.0");
  license.href = "https://creativecommons.org/licenses/by/4.0/";
  if (movieContexts.length) {
    add("h4", "NASA views of this region");
    const first = movieContexts[0];
    add("p", `Contour date: ${candidate.observation_date}. NASA movie model period: ${first.movie_model_period}. ${first.temporal_alignment_status === "outside_declared_model_years" ? "The contour date is outside the declared movie years." : "The year is in range; event alignment remains unresolved."} These links show geographic overlap; Kraken has not been identified in the movie.`);
    const movieLink = (row, host) => {
      const anchor = add("a", `Open NASA crop ${row.tile_id}`, host);
      anchor.href = row.url; anchor.target = "_blank"; anchor.rel = "noopener noreferrer";
      add("span", ` · zoom ${row.zoom} · ${(row.nominal_angular_overlap_fraction * 100).toFixed(1)}% nominal contour overlap`, host);
    };
    const recommended = movieContexts.find(row => row.recommended);
    if (recommended) { add("p", "Recommended complete nominal view:"); movieLink(recommended, add("p", null)); }
    const crops = add("details", null); add("summary", `${movieContexts.length} overlapping NASA crops`, crops);
    const cropList = add("ul", null, crops);
    for (const row of movieContexts) movieLink(row, add("li", null, cropList));
    add("p", "Crop selection uses the nominal contour and approximate movie bounds. Calibration and segmentation uncertainty are not included in these navigation overlaps.");
  }
  const details = add("details", null); add("summary", "Source and geometry checksums", details);
  add("p", `PDF SHA-256: ${candidate.source_pdf_sha256}. Embedded figure SHA-256: ${candidate.embedded_figure_sha256}. Geometry SHA-256: ${candidate.geometry_sha256}.`, details);
};
