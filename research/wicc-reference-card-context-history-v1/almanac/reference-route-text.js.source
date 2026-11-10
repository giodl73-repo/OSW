/* Shared route labels: unknown support must never become a numeric interval. */
(() => {
  const format = value => value.toLocaleString('en-US');
  const hasRange = row => Array.isArray(row?.scenario_range_km) && row.scenario_range_km.length === 2 &&
    row.scenario_range_km.every(value => typeof value === 'number' && Number.isFinite(value) && value > 0) &&
    row.scenario_range_km[0] <= row.scenario_range_km[1];
  const length = row => Number.isFinite(row?.approximate_reference_path_km) && row.approximate_reference_path_km > 0 ?
    format(row.approximate_reference_path_km) : null;
  const range = row => hasRange(row) ? `${row.scenario_range_km.map(format).join('–')} km` : 'Range unknown';
  function summary(row, context = 'card') {
    const value = length(row), start = value ? `≈ ${value} km` : 'Length unknown';
    if (!hasRange(row)) return `${start} · range unknown. No annual range or uncertainty inferred.`;
    const count = context === 'card' ? ` · ${row.scenario_count} scenarios` : '';
    const kind = row.comparison_group === 'osw_source_anchor_connections' ?
      (context === 'card' ? 'bend-probe span' : 'editorial bend-probe span') :
      context === 'card' && row.comparison_group === 'osw_offshore_coastal_reference_curves' ? 'convention sensitivity' : 'scenario envelope';
    return `${start}${count} · ${range(row)} ${kind}`;
  }
  function seasonal(row) {
    const value = length(row);
    if (!value) return 'Scoped route length and range: unknown. No annual extrema or uncertainty margin inferred.';
    return hasRange(row) ? `Approximate scoped route length: ${value} km; ${range(row)} editorial sensitivity envelope. Different phase scopes cannot supply annual extrema.` :
      `Approximate scoped route length: ${value} km; range unknown. No annual extrema or uncertainty margin inferred.`;
  }
  function compactFigure(row, report) {
    if (row.compact_figure_file || report?.compact_figure_file) return row.compact_figure_file || report.compact_figure_file;
    return ({
      'figures/pacific-secc-western-mean-reference-path-v2-candidate.svg': 'figures/pacific-secc-western-reference-compact-v1.svg',
      'figures/wicc-winter-regional-reference-route-v4-candidate.svg': 'figures/wicc-winter-regional-reference-compact-v1.svg'
    })[row.figure] || null;
  }
  window.OSWReferenceRouteText = Object.freeze({hasRange, range, summary, seasonal, compactFigure});
})();
