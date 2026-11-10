"""All-date EAC exploratory section outcomes, denominators and fixed examples."""
from datetime import datetime
import json
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

from acquire_eac_100m_source import ROOT, sha
from build_eac_section_core_spans import REPORT, OPERATOR, PROTOCOL, verify

GENERATOR = 'analysis/build_eac_section_core_span_figure.py'
RECEIPT = 'research/eac-csiro-100m-section-core-spans-figure.json'
STEM = 'figures/eac-csiro-100m-section-core-spans'
EXAMPLES = (0, 1885, 3769)
ALT = ('Exploratory EAC100m section-normal component spans for all3770 source dates. '
       'The primary half-peak case resolves2883dates and leaves887unresolved, '
       'including629missing dates. Monthly denominators and fixed source examples '
       'retain domain failures, excluded bottom cells and supplied-magnitude sensitivity. '
       'These are section distances, not physical current widths or annual extrema.')


def case(row, scenario='central', fraction=.5):
    return next(c for c in row['scenarios'][scenario]['cases'] if c['fraction'] == fraction)


def build():
    doc = verify(); rows = doc['profiles']; dates = [datetime.fromisoformat(r['source_time_utc'].replace('Z', '+00:00')) for r in rows]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.hashsalt': 'osw-eac-section-core-v1'})
    fig = plt.figure(figsize=(14, 13), layout='constrained'); grid = fig.add_gridspec(4, 3, height_ratios=[2, 1.4, 1.6, .55])
    top = fig.add_subplot(grid[0, :]); primary = [case(r) for r in rows]
    values = np.array([np.nan if c['section_span_km'] is None else c['section_span_km'] for c in primary])
    top.plot(dates, values, '.', ms=1.8, color='#155a73', label='Resolved central half-peak section span')
    for status, color, marker, label, height in [
        ('unresolved_paired_boundaries', '#a24f25', 'x', 'Unresolved section edge', -8),
        ('unresolved_peak_below_0_3_m_s', '#744989', '+', 'Peak below 0.3 m/s', -16),
        ('unresolved_no_eligible_component', '#68737c', '|', 'No eligible paired source data', -24),
    ]:
        selected = [d for d, c in zip(dates, primary) if c['status'] == status]
        top.scatter(selected, [height]*len(selected), s=12, color=color, marker=marker, label=label)
    top.axvspan(dates[513], dates[1141], color='#d9dfe2', alpha=.5)
    top.set(title='All 3,770 dates: 2,883 resolved / 887 unresolved at the central half-peak rule',
            ylabel='Distance along fixed section (km)', ylim=(-31, 165))
    top.set_yticks(range(0, 151, 25))
    top.legend(loc='upper left', ncol=2, fontsize=9); top.grid(alpha=.2)
    top.xaxis.set_major_locator(mdates.YearLocator(2)); top.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    monthly = fig.add_subplot(grid[1, :]); bins = doc['monthly_summaries']
    months = [datetime(m['year'], m['month'], 1) for m in bins]
    choices = [('central', .4, '#457d46', '-', 'Central 40%'), ('central', .5, '#155a73', '-', 'Central 50%'),
               ('central', .6, '#9a6625', '-', 'Central 60%'),
               ('minus_supplied_component_magnitudes', .5, '#744989', '--', 'Minus supplied magnitudes: 50%'),
               ('plus_supplied_component_magnitudes', .5, '#b14d43', ':', 'Plus supplied magnitudes: 50%')]
    for scenario, fraction, color, style, label in choices:
        results = [next(o for o in m['outcomes'] if o['scenario'] == scenario and o['fraction'] == fraction) for m in bins]
        monthly.plot(months, [100*o['resolved_dates']/o['attempted_dates'] for o in results], color=color, ls=style, lw=1.2, label=label)
    monthly.set(title='Monthly resolved / all recorded dates (missing dates remain in the denominator)',
                ylabel='Resolved (%)', ylim=(-3, 103)); monthly.grid(alpha=.2)
    monthly.legend(ncol=3, fontsize=8, loc='lower right'); monthly.xaxis.set_major_locator(mdates.YearLocator(2)); monthly.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    distance = np.array(doc['geometry']['distance_m'])/1000
    excluded = [i for i, v in enumerate(doc['geometry']['bottom_depth_m']) if v <= 100]
    for slot, index in enumerate(EXAMPLES):
        ax = fig.add_subplot(grid[2, slot]); row = rows[index]; c = case(row)
        q = np.array(row['section_normal_velocity_m_s'], dtype=float)
        allowance = np.array(row['projected_supplied_magnitudes_m_s'], dtype=float)
        ax.fill_between(distance, q-allowance, q+allowance, color='#b3d2df', label='± supplied magnitudes')
        ax.plot(distance, q, color='#155a73', label='Projected central component')
        if excluded:
            ax.axvspan(distance[0], distance[max(excluded)], color='#dfae8f', alpha=.5, label='Excluded source bottom cells')
        if c['threshold_m_s'] is not None:
            ax.axhline(c['threshold_m_s'], color='#744989', ls='--', lw=1, label='Half-peak threshold')
        for edge in [c['shoreward_edge'], c['offshore_edge']]:
            if edge and edge['status'] == 'resolved':
                a, b = edge['distance_bracket_m']; ax.axvspan(a/1000, b/1000, color='#9aad83', alpha=.5)
                ax.axvline(edge['distance_m']/1000, color='#4b633a', lw=1)
        label = ('Resolved '+str(c['rounded_section_span_km'])+' km section span') if c['section_span_km'] is not None else {
            'unresolved_peak_below_0_3_m_s': 'Peak below 0.3 m/s; no span admitted',
            'unresolved_no_eligible_component': 'No eligible paired source data',
            'unresolved_paired_boundaries': 'At least one section edge unresolved'}[c['status']]
        ax.set(title=f"Source index {index} · {row['source_time_utc'][:10]}\n{label}",
               xlabel='Along fixed section (km)', ylim=(-.75, 1.6), xlim=(0, distance[-1]))
        ax.grid(alpha=.2)
        if slot == 0:
            ax.set_ylabel('Section-normal component (m/s)'); ax.legend(fontsize=7, loc='lower right')
    note = fig.add_subplot(grid[3, :]); note.axis('off')
    note.text(0, 1, 'Source: CSIRO DOI 10.25919/sfw7-hc46 · metadata v23 / data v19 · 100 m · 2012–2022 · CC BY 4.0\n'
              'Five-day-filtered, SOM-filled and spatially mapped output; days and mapped cells are not independent observations.\n'
              'Peak ≥0.3 m/s; 40/50/60% rules and supplied-magnitude cases are exploratory assumptions, not confidence bounds.\n'
              'Sampling brackets are not measurement error. No flow-normal physical width, whole-current width or annual extrema admitted.',
              va='top', fontsize=9)
    fig.suptitle('East Australian Current · exploratory 100 m section-core spans', fontsize=17)
    assets = {}
    for extension in ['.svg', '.png']:
        path = ROOT/(STEM+extension); fig.savefig(path, dpi=145, metadata={'Date': None} if extension == '.svg' else {})
        if extension == '.svg':
            ET.register_namespace('', 'http://www.w3.org/2000/svg'); tree = ET.parse(path); svg = tree.getroot()
            svg.set('role', 'img'); svg.set('aria-labelledby', 'eac-core-title eac-core-description')
            title = ET.Element('{http://www.w3.org/2000/svg}title', {'id': 'eac-core-title'}); title.text = 'EAC100m exploratory section-core spans'
            desc = ET.Element('{http://www.w3.org/2000/svg}desc', {'id': 'eac-core-description'}); desc.text = ALT
            svg.insert(0, title); svg.insert(1, desc); tree.write(path, encoding='utf-8', xml_declaration=True)
        assets[extension] = {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}
    plt.close(fig)
    receipt = {'schema': 'osw.eac-section-core-spans-figure.v1', 'source_file': REPORT, 'source_sha256': sha(ROOT/REPORT),
               'generator_file': GENERATOR, 'generator_sha256': sha(ROOT/GENERATOR),
               'input_sha256': {p: sha(ROOT/p) for p in [OPERATOR, PROTOCOL]}, 'figures': assets,
               'alt': ALT, 'fixed_source_indices': list(EXAMPLES), 'all_dates_included': 3770,
               'primary_resolved': 2883, 'primary_unresolved': 887,
               'physical_width_admitted': False, 'annual_range_admitted': False,
               'provider_uncertainty_assigned_confidence_convention': False}
    (ROOT/RECEIPT).write_bytes((json.dumps(receipt, indent=2)+'\n').encode())
    print(json.dumps(receipt))


if __name__ == '__main__':
    build()
