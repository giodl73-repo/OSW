/* Source descriptions keep their own dates, regions and measurement scope. */
(() => {
  const own = (data, name, id) => (data[name] || []).filter(row => row.entity_id === id);
  function node(tag, text, parent) {
    const result = document.createElement(tag);
    if (text != null) result.textContent = text;
    parent.append(result);
    return result;
  }
  function recordLink(parent, collection, id) {
    const query = {collection, filters:[{field:'id',op:'eq',value:id}],limit:1};
    const a = node('a', 'Evidence and source details', parent);
    a.href = 'query.html?q=' + encodeURIComponent(JSON.stringify(query));
  }
  function heading(parent, id, text) {
    const section = node('section', null, parent);
    section.id = id;
    section.setAttribute('aria-labelledby', id + '-title');
    node('h3', text, section).id = id + '-title';
    return section;
  }
  function windowLabel(window) {
    return Array.isArray(window) && window.length === 2 ? window.join(' to ') : 'Observation dates unspecified';
  }
  function contextText(row, text) {
    if (row.schema !== 'osw.source-reported-regional-connection.v1'
        && row.quantity !== 'sst_associated_coastal_confinement_scale') return text;
    return String(text)
      .replace(/\bnear(\d+(?:\.\d+)?)degrees([NS])\b/g, 'near $1°$2')
      .replace(/\bdescribes(\d+)years\b/g, 'describes $1 years')
      .replace(/\b(page|section|Section|printed|PDF|Figure)(\d+)\b/g, '$1 $2');
  }
  function source(row, parent, sourceLink) {
    sourceLink(row.source_id, node('p', null, parent));
    if (row.source_locator || row.locator) node('p', contextText(row, row.source_locator || row.locator), parent);
  }
  window.renderCurrentSourceEvidence = function(parent, data, id, sourceLink) {
    const lengthBounds = own(data, 'current_length_bound_admissions', id).filter(row =>
      row.schema === 'osw.baffin-latitude-bound-working-admission.v1');
    for (const bound of lengthBounds) {
      const measurement = own(data, 'measurements', id).find(row =>
        row.id === bound.measurement_id && row.length_bound_admission_id === bound.id);
      if (!measurement) continue;
      const section = heading(parent, 'current-geographic-length-bound', 'Regional geographic length evidence');
      node('h4', `${measurement.value.toLocaleString()} km · conditional geographic floor · unranked`, section);
      node('p', bound.scope, section);
      node('p', bound.naming_scope, section);
      node('p', `Study context: summer ${bound.study_years.join(' and ')}. Exact gate dates and a common fixed layer are unknown.`, section);
      node('p', 'The nominal floor is rounded down to 100 km. It is not below every editorial scenario and does not establish a guaranteed physical minimum for a connected current.', section);
      const figure = node('figure', null, section);
      const image = node('img', null, figure);
      image.src = '../' + bound.figure_file;
      image.alt = `${measurement.value.toLocaleString()} km conditional geographic floor from nominal 67°N and 76°N source gates. Summer-study geographic support, unranked; no measured centerline or seasonal length range.`;
      image.loading = 'lazy'; image.style.cssText = 'width:100%;max-width:960px;height:auto';
      node('figcaption', 'Scalar latitude separation. The calculation longitude is abstract; no current route or physical endpoints are mapped by this diagram.', figure);
      const scenarios = own(data, 'current_length_bound_scenarios', id)
        .filter(row => row.admission_id === bound.id).sort((a,b) => a.scenario_index-b.scenario_index);
      node('p', 'Nine ±0.5° editorial gate scenarios test the chosen latitude support. They are not observations, source position errors, confidence intervals or seasonal variability.', section);
      const wrap = node('div', null, section); wrap.className = 'table-wrap';
      const table = node('table', null, wrap);
      node('caption', 'Editorial latitude sensitivity · WGS84 meridional separation', table);
      const head = node('tr', null, node('thead', null, table));
      for (const label of ['Case', 'South °N', 'North °N', 'Separation km']) node('th', label, head).scope = 'col';
      const body = node('tbody', null, table);
      for (const row of scenarios) {
        const tr = node('tr', null, body); tr.dataset.scenarioIndex = row.scenario_index;
        node('th', row.scenario_index, tr).scope = 'row';
        for (const value of row.nominal_latitudes_degrees_north) node('td', value.toFixed(1), tr);
        node('td', row.geographic_separation_km.toFixed(1), tr);
      }
      if (scenarios.length !== 9) node('p', 'The complete nine-case scenario table is unavailable in this view; inspect the admission query before using this evidence.', section);
      source(bound, section, sourceLink);
      const method = node('p', null, section); sourceLink(bound.method_source_id, method);
      recordLink(section, 'measurements', measurement.id);
      const admission = node('p', null, section); recordLink(admission, 'current_length_bound_admissions', bound.id);
      admission.firstChild.textContent = 'Admission, source support and limitations';
      const link = node('a', 'Query all nine editorial scenarios', section);
      link.href = 'query.html?q=' + encodeURIComponent(JSON.stringify({collection:'current_length_bound_scenarios',filters:[{field:'entity_id',op:'eq',value:id}],sort:{field:'scenario_index',direction:'asc'},limit:9}));
    }
    const campaignSpans = own(data, 'widths', id).filter(row =>
      row.measurement_type === 'source_reported_regional_transect_summary' &&
      row.source_evidence_kind === 'primary_course_cruise_report' &&
      own(data, 'current_measurement_admissions', id).some(admission =>
        admission.id === row.width_admission_id && admission.width_id === row.id));
    if (campaignSpans.length) {
      const section = heading(parent, 'current-campaign-widths', 'Reported regional transect spans');
      node('p', 'Each record keeps its own region, depth and campaign. Separate historical summaries do not establish a trend or seasonal range.', section);
      for (const row of campaignSpans) {
        const article = node('article', null, section); article.dataset.recordId = row.id;
        node('h4', `About ${row.approximate_width_km} km · ${row.phase_label}`, article);
        node('p', row.geographic_scope, article);
        node('p', row.layer, article);
        node('p', `Campaign: ${windowLabel(row.observation_window)}. Exact occupation date unknown.`, article);
        node('p', `Source reports about ${row.source_reported_value} ${row.source_unit_label}. Unit conversion: ${row.normalized_width_km_decimal} km; the source remains approximate.`, article);
        node('p', 'Primary course cruise report. Peer review and publication date unverified. Paired current edges, numerical velocity cutoff and uncertainty are unspecified. Flow-normal orientation is unverified.', article);
        node('p', 'No whole-current width, annual range or seasonal animation is established.', article);
        const figure = node('figure', null, article);
        const image = node('img', null, figure);
        image.src = '../' + row.figure_file;
        image.alt = `About ${row.approximate_width_km} km, one reported regional transect span. ${row.layer}. ${row.phase_label}. Numerical marker only, with unknown edges and uncertainty.`;
        image.loading = 'lazy'; image.style.cssText = 'width:100%;max-width:600px;height:auto';
        node('figcaption', 'One source-reported scalar. The diagram does not locate current boundaries on a map.', figure);
        const open = node('a', 'Open the source-scope diagram', article);
        open.href = image.getAttribute('src');
        source(row, article, sourceLink);
        const widthLink = node('p', null, article);
        recordLink(widthLink, 'widths', row.id);
        const admissionLink = node('p', null, article);
        recordLink(admissionLink, 'current_measurement_admissions', row.width_admission_id);
        admissionLink.firstChild.textContent = 'Admission and limitations';
      }
    }
    const calendars = own(data, 'current_direction_calendars', id);
    for (const calendar of calendars) {
      const section = heading(parent, 'current-direction-calendar', 'Typical direction through the year');
      node('p', 'A source-described annual pattern. These months are qualitative descriptions, not monthly observations or a moving current boundary.', section);
      const wrap = node('div', null, section); wrap.className = 'table-wrap';
      const table = node('table', null, wrap);
      node('caption', calendar.display_name + ' · ' + calendar.figure_source_label, table);
      const head = node('tr', null, node('thead', null, table));
      for (const label of ['Month', 'Source-described direction']) node('th', label, head).scope = 'col';
      const body = node('tbody', null, table);
      const months = own(data, 'current_direction_descriptions', id)
        .filter(row => row.calendar_id === calendar.id).sort((a,b) => a.month-b.month);
      for (const month of months) {
        const tr = node('tr', null, body); tr.dataset.month = month.month;
        node('th', month.month_label, tr).scope = 'row';
        const label = month.direction === 'northward' ? '↑ Northward'
          : month.direction === 'southward' ? '↓ Southward' : 'Not specified by this source';
        node('td', label, tr);
      }
      if (id === 'current:west-india-coastal') node('p', 'Strong intraseasonal variability can produce either direction at a particular time. Unspecified months do not mean zero flow or a measured transition.', section);
      if (id === 'current:east-african-coastal') node('p', 'Northward prevailing orientation throughout the year does not guarantee the direction of every observation.', section);
      source(calendar, section, sourceLink);
      recordLink(section, 'current_direction_calendars', calendar.id);
    }

    const statements = own(data, 'current_reported_width_evidence', id);
    if (statements.length) {
      const section = heading(parent, 'current-reported-widths', 'Published widths and their scope');
      node('p', 'Keep these three source statements separate. Their different regions and support do not establish an annual minimum, maximum or uncertainty range.', section);
      for (const row of statements) {
        const admitted = row.canonical_width_admitted === true && own(data,'widths',id)
          .some(width => width.id === row.width_id && width.width_admission_id === row.width_admission_id);
        const article = node('article', null, section); article.dataset.recordId = row.id;
        node('h4', `About ${row.reported_width_km} km · ${row.label}`, article);
        node('p', admitted ? 'Admitted as a scoped published width summary.' : 'Reported source context; no separate canonical width admitted.', article);
        node('p', row.geographic_scope, article);
        node('p', windowLabel(row.reported_time_window), article);
        if (row.vertical_support) node('p', row.vertical_support, article);
        if (admitted) node('p', 'Source-associated 21 m level. Paired edges, a finite depth interval, numerical boundary cutoff and error bounds are unspecified. No whole-current width or annual range is established.', article);
        source(row, article, sourceLink);
        recordLink(article, 'current_reported_width_evidence', row.id);
      }
      const figure = node('figure', null, section);
      const image = node('img', null, figure);
      image.src = '../figures/eicc-wijesekera-2015-width-evidence-v1.svg';
      image.alt = 'Three separately scoped EICC source statements: about 100, 200 and 250 kilometres.';
      image.loading = 'lazy'; image.style.cssText = 'width:100%;height:auto';
      node('figcaption', 'The source-evidence diagram preserves the earlier extraction status. The T24 summary has a separate later scoped admission shown above.', figure);
    }

    const crossShore = own(data, 'current_cross_shore_context', id);
    if (crossShore.length) {
      const section = heading(parent, 'current-cross-shore-context', 'Offshore position and extent');
      node('p', 'Distances from the coast describe different features. They do not define a width between two current edges.', section);
      node('p', 'Read the region, time support and boundary meaning with each description. These ranges are not annual extrema or error bounds.', section);
      const labels = {
        reported_recognisable_current_offshore_extent:'Recognisable offshore extent',
        reported_current_core_offshore_position:'Position of the fastest core',
        reported_eastern_boundary_offshore_distance:'Outer-boundary distance',
        reported_typical_transport_concentration_offshore_extent:'Typical transport concentration',
        sst_associated_coastal_confinement_scale:'SST-associated coastal confinement',
      };
      const list = node('dl', null, section);
      for (const row of crossShore) {
        const value = Array.isArray(row.reported_range_km) ? row.reported_range_km.join('–') : row.reported_value_km;
        node('dt', `${labels[row.quantity] || row.quantity.replaceAll('_',' ')} · ${value} km`, list);
        const description = node('dd', null, list);
        if (row.geographic_scope) node('p', row.geographic_scope, description);
        node('p', `${row.source_precision}. Reference: ${row.reference}.`, description);
        if (row.range_meaning || row.criterion_context) node('p', row.range_meaning || row.criterion_context, description);
        if (row.time_support_note) node('p', contextText(row, row.time_support_note), description);
        if (row.proxy_note) node('p', row.proxy_note, description);
        source(row, description, sourceLink);
        recordLink(description, 'current_cross_shore_context', row.id);
      }
    }

    for (const row of own(data, 'current_regime_context', id)) {
      const section = heading(parent, 'current-survey-regime', 'A dated survey in context');
      node('p', windowLabel(row.reported_hydrographic_survey_window), section);
      node('p', row.source_reported_regime, section);
      node('p', row.relation_to_direction_calendar, section);
      node('p', 'This does not establish zero current or identify individual named eddies.', section);
      source(row, section, sourceLink);
      recordLink(section, 'current_regime_context', row.id);
    }
    for (const row of own(data, 'current_regional_reaches', id)) {
      const section = heading(parent, 'current-regional-reach', 'Reported regional reach');
      node('p', row.constraint.display, section);
      node('p', contextText(row, row.scope_note || row.constraint.numeric_precision), section);
      node('p', 'This regional reach is unranked. A whole-current length, physical length lower bound and annual range have not been established.', section);
      if (row.id === 'regional-reach:east-african-coastal:painter-2020-connection'
          && row.schema === 'osw.source-reported-regional-connection.v1'
          && row.source_id === 'source:painter-eacc-2020-regional-reach'
          && row.constraint.reported_value_km === 1000
          && row.constraint.relation === 'source_reported_approximate_value'
          && row.whole_current_length_admitted === false
          && row.constraint.whole_current_length_km === null
          && row.constraint.current_geometry === null) {
        const figure = node('figure', null, section);
        const image = node('img', null, figure);
        image.src = '../figures/eacc-regional-connection-v1.svg';
        image.alt = 'Approximately 1000 km regional connection from coastal contact near 11°S to the Somali Current confluence near 3°S. Schematic, not a measured current axis; observation dates, layer, uncertainty and annual ranges unknown.';
        image.loading = 'lazy'; image.style.cssText = 'width:100%;max-width:860px;height:auto';
        node('figcaption', 'Published regional connection in a theoretical-transit discussion. This diagram adds no measurement or geographic route.', figure);
        const open = node('a', 'Open the regional-connection diagram', section);
        open.href = image.src;
      }
      if (row.source?.source_title) node('p', [row.schema === 'osw.source-reported-regional-connection.v1' ? null : row.source.source_title,
        (row.source.authors || []).join(', '), row.source.chapter].filter(Boolean).join(' · '), section);
      source(row, section, sourceLink);
      recordLink(section, 'current_regional_reaches', row.id);
    }
  };
})();
