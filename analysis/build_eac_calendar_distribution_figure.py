"""Independent comparison of EAC conditional spans and calendar support."""
import calendar
import json
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from build_eac_calendar_distributions import ROOT, REPORT, PROTOCOL, build, sha

OPERATOR = 'analysis/build_eac_calendar_distribution_figure.py'
MANIFEST = 'research/eac-section-calendar-distributions-figure.json'
STEM = 'figures/eac-section-calendar-distributions'


def figure(document):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.hashsalt': 'osw-eac-calendar-v1',
                         'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 1, figsize=(14, 8.8))
    fig.subplots_adjust(left=.075, right=.985, top=.87, bottom=.25, hspace=.62)
    fig.suptitle('East Australian Current · 100 m fixed-section diagnostics', x=.075,
                 y=.975, ha='left', fontsize=19, fontweight='bold')
    fig.text(.075, .93, 'Conditional distributions of resolved mapped dates; section spans, not physical current widths.', fontsize=12)
    rows_by_panel = [document['calendar_month_groups'], document['calendar_year_groups']]
    primary_rows = [[next(o for o in row['outcomes'] if o['primary']) for row in rows] for rows in rows_by_panel]
    maximum = max(o['conditional_max_km'] for rows in primary_rows for o in rows if o['conditional_max_km'] is not None)
    for panel, (ax, rows, outcomes) in enumerate(zip(axes, rows_by_panel, primary_rows)):
        labels = []
        for x, (row, outcome) in enumerate(zip(rows, outcomes)):
            label = calendar.month_abbr[row['month']] if panel == 0 else str(row['year'])+('*' if row['partial_calendar_year'] else '')
            labels.append(f"{label}\n{outcome['resolved_dates']}/{outcome['attempted_dates']}")
            if outcome['resolved_dates']:
                ax.vlines(x, outcome['conditional_min_km'], outcome['conditional_max_km'], color='#aac1c9', linewidth=2)
                ax.vlines(x, outcome['conditional_p10_km'], outcome['conditional_p90_km'], color='#137b91', linewidth=7)
                ax.scatter([x], [outcome['conditional_median_km']], color='#172e38', s=32, zorder=3)
            else:
                ax.text(x, 5, 'unresolved', rotation=90, ha='center', fontsize=8)
        ax.set_xticks(range(len(rows)), labels)
        ax.set_ylim(0, maximum*1.08)
        ax.set_xlim(-.6, len(rows)-.4)
        ax.set_ylabel('Section span (km)')
        ax.grid(axis='y', alpha=.22)
        ax.set_axisbelow(True)
        ax.set_title('Pooled by calendar month · resolved / attempted source dates' if panel == 0 else
                     'By calendar year · resolved / attempted source dates; * partial calendar year',
                     loc='left', fontsize=12, pad=12)
    fig.text(.075, .19, 'Thin: resolved minimum–maximum     Thick: 10th–90th percentile     Point: median', fontsize=11)
    caption = ('Primary case: central component, 50% of positive peak; all nine original scenario/threshold cases remain in the data. '
               'Filtered, SOM-filled mapped dates are correlated. Missing and failed cases are counted, never zero-filled. '
               'Pooled months weight resolved source dates equally, with unequal year support; percentiles are descriptive, not confidence intervals. '
               'No physical annual range, seasonal footprint or whole-current width is inferred.')
    fig.text(.075, .15, '\n'.join(textwrap.wrap(caption, 160)), fontsize=10, va='top', linespacing=1.45)
    fig.text(.075, .035, f"OSW derivation from pinned CSIRO v2.3 EAC section diagnostics · {document['source_first_date']} to {document['source_last_date']}", fontsize=9)
    return fig


def main():
    document = json.loads((ROOT/REPORT).read_bytes())
    if document != build():
        raise ValueError('Changed calendar distribution report')
    fig = figure(document)
    assets = {}
    for suffix in ['svg', 'png']:
        path = STEM+'.'+suffix
        metadata = {'Date': None, 'Creator': 'OSW'} if suffix == 'svg' else {'Software': 'OSW'}
        fig.savefig(ROOT/path, dpi=130, metadata=metadata, facecolor='white')
        assets[suffix] = {'file': path, 'sha256': sha(path), 'bytes': (ROOT/path).stat().st_size}
    plt.close(fig)
    manifest = {'schema': 'osw.eac-section-calendar-figure.v1', 'source_file': REPORT,
                'source_sha256': sha(REPORT), 'protocol_file': PROTOCOL, 'protocol_sha256': sha(PROTOCOL),
                'generator_file': OPERATOR, 'generator_sha256': sha(OPERATOR), 'figures': assets,
                'alt': 'Twelve pooled calendar-month and eleven separate year distributions of the primary EAC 100 m fixed-section component span. Each includes resolved/attempted counts. Thin min/max, thick 10th–90th percentiles and median points describe only resolved mapped dates; 2012 and 2022 are partial years. Not physical widths or confidence intervals.',
                'physical_width_admitted': False, 'source_image_redistributed': False}
    (ROOT/MANIFEST).write_bytes((json.dumps(manifest, indent=2)+'\n').encode())
    print(json.dumps({'figures': assets, 'manifest': MANIFEST}))


if __name__ == '__main__':
    main()
