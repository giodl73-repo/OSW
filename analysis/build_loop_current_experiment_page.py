"""Render the retained experiment, with failed paths and a text alternative."""
import html
import json
from build_loop_current_dated_streamline import ROOT, OUTPUT
from build_cartographic_current_state_join import project
from build_loop_current_adt_contours import OUTPUT as ADT_OUTPUT

def build():
    result=json.loads(OUTPUT.read_text(encoding='utf-8'))
    adt=json.loads(ADT_OUTPUT.read_text(encoding='utf-8'))
    adt_display=f"{adt['approximate_diagnostic_path_km']:,}" if adt['approximate_diagnostic_path_km'] is not None else 'unresolved'
    difference=adt['comparison']['signed_difference_duacs_minus_noaa_km']
    difference_display=f"{abs(difference):.1f} km" if difference is not None else 'unresolved'
    rows=[('Nominal',result['nominal'])]+[(s['variation'].replace('_',' '),s) for s in result['sensitivity_scenarios']]
    x,y=project(-91,31);right,bottom=project(-79,20)
    marks=[];table=[]
    # Failed traces first; successful step/threshold traces remain in the table
    # rather than obscuring the nominal line with nearly identical strokes.
    for index,(label,row) in enumerate(rows):
        path=' '.join(('M' if i==0 else 'L')+' %.5f %.5f'%project(*p) for i,p in enumerate(row['coordinates_lon_lat']))
        if index==0 or not row['gate_connected']:
            title=f"{label}: seed {row['seed_lon_lat'][0]:g}, {row['stop_reason'].replace('_',' ')}"
            marks.append(f'<path class="{"nominal" if index==0 else "failed"}" d="{path}"><title>{html.escape(title)}</title></path>')
        length=f"{row['open_path_length_km']:,.1f}" if row['gate_connected'] else 'unresolved'
        table.append('<tr>'+''.join(f'<td>{html.escape(str(v))}</td>' for v in [label,row['seed_lon_lat'][0],row['step_km'],row['minimum_speed_threshold_m_s'],row['stop_reason'].replace('_',' '),length,f"{row['travelled_distance_km']:,.1f}"] )+'</tr>')
    for d in [21.875]:
        a=project(-86.875,d);b=project(-85.125,d)
        marks.append(f'<path class="gate" d="M {a[0]} {a[1]} L {b[0]} {b[1]}"><title>Editorial Yucatan inflow gate</title></path>')
    a=project(-81.5,23);b=project(-81.5,25)
    marks.append(f'<path class="gate" d="M {a[0]} {a[1]} L {b[0]} {b[1]}"><title>Editorial Florida outflow gate</title></path>')
    if adt['selected']:
        path=' '.join(('M' if i==0 else 'L')+' %.5f %.5f'%project(*p) for i,p in enumerate(adt['selected']['coordinates_lon_lat']))
        marks.append(f'<path class="adt" d="{path}"><title>DUACS highest-mean-speed eligible ADT contour, {adt["selected"]["adt_level_m"]} m; local diagnostic</title></path>')
    ground='<image href="../figures/ocean-motion-closeup-ground.svg" x="60" y="90" width="1480" height="740"/>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loop Current dated path experiment · OSW</title><style>
body{{margin:0;background:#092b39;color:#e3f1f4;font:16px/1.5 system-ui,sans-serif}}main{{max-width:1000px;margin:auto;padding:24px}}a{{color:#8be9da}}a:focus-visible{{outline:3px solid #ffd36e}}h1{{line-height:1.15}}.status{{color:#ffd36e}}svg{{display:block;width:100%;max-height:650px;background:#092b39}}.nominal{{fill:none;stroke:#ffbb71;stroke-width:.5}}.failed{{fill:none;stroke:#b4c4cf;stroke-width:.25;stroke-dasharray:.7 .5}}.gate{{fill:none;stroke:#8be9da;stroke-width:.65}}.adt{{fill:none;stroke:#82e8fa;stroke-width:.3;stroke-dasharray:2 .4}}.table-wrap{{overflow:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:9px;text-align:left;border-bottom:1px solid #37606c}}p{{max-width:85ch}}code{{overflow-wrap:anywhere}}
</style></head><body><main><a href="query.html">Return to query atlas</a><p class="status">LOCAL EXPERIMENT · UNRANKED · REVIEW REQUIRED</p><h1>Loop Current · 25 September 2026</h1><p>The nominal surface velocity trace connects two editorial regional gateways over about <strong>{result['approximate_diagnostic_path_km']:,} km</strong>. All four neighboring seed tests fail to connect them. This does not establish a robust current length, uncertainty interval, width, annual range or particle trajectory.</p>
<figure><svg viewBox="{x} {y} {right-x} {bottom-y}" role="img" aria-labelledby="map-title map-desc"><title id="map-title">Dated Loop Current product and method comparison</title><desc id="map-desc">Orange solid NOAA velocity trace; cyan long-dashed DUACS ADT contour; gray short-dashed failed neighboring traces stop early. Teal short lines are editorial gateways. The table and comparison text provide outcomes. Equirectangular display on coarse OSW coastline; geographic lengths use WGS84 geodesics.</desc>{ground}{''.join(marks)}</svg><figcaption>Solid orange: NOAA nominal trace. Long-dashed cyan: DUACS ADT contour. Short-dashed gray: failed neighboring traces. Teal: editorial gateways. Equirectangular display; 91–79 W, 20–31 N. Hover paths for their test identity.</figcaption></figure>
<h2>Same-day product and method comparison</h2><p>DUACS ADT contour search: <strong>{adt_display} km</strong>; NOAA velocity integration: <strong>{result['approximate_diagnostic_path_km']:,} km</strong>. The raw difference is {difference_display}. These products can share satellite inputs; this is not independent observational confirmation or an uncertainty interval.</p><p>The finite search scans 146 ADT levels from 0.05 to 1.50 m, retains {adt['eligible_count']} eligible connected contours, and selects the greatest length-weighted mean speed. Missing velocity anywhere rejects a candidate. Scanned contours are not a physical width or annual range. Gates, effective resolution and original method details remain under review.</p><p><a href="{html.escape(adt['dataset_page'])}">GCOOS / Copernicus DUACS dataset</a> · <a href="../plans/loop-current-adt-contour-protocol-v1.md">Contour search rules</a> · <a href="../research/loop-current-adt-contours-20260925.json">All contour candidates and receipts</a></p>
<h2>Retained scenario outcomes</h2><p>“Travelled” includes the portion traced before a failure. It is not an open-path length. Successful integration-step tests stay within 12 km of the nominal result; that numerical agreement does not remove the seed failures.</p><div class="table-wrap"><table><caption>Frozen-time surface geostrophic diagnostic; km values at 0.1 km are calculation readback, not measurement accuracy.</caption><thead><tr><th scope="col">Test</th><th scope="col">Seed longitude</th><th scope="col">Step km</th><th scope="col">Stop speed m/s</th><th scope="col">Outcome</th><th scope="col">Connected km</th><th scope="col">Travelled km</th></tr></thead><tbody>{''.join(table)}</tbody></table></div>
<h2>Source and method</h2><p>NOAA LSA / CoastWatch, RADS 4.8.1, Experimental daily absolute surface geostrophic velocity, 0.25-degree analysis grid. UTC interval: 25 September to 26 September 2026, end excluded. Missing cells stop tracing. Effective resolution, endpoint conventions and source-use review remain open.</p><p><a href="{html.escape(result['source_url'])}">NOAA source file</a> · <a href="../plans/loop-current-dated-streamline-protocol-v1.md">Measurement protocol</a> · <a href="../research/loop-current-dated-streamline-20260925.json">Complete diagnostic and provenance</a> · <a href="https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2023.1156159/full">Published method comparison</a></p><p>The source sea-level anomaly field is not absolute dynamic topography. This velocity integration is an OSW experiment, distinct from the published maximum-velocity contour algorithm. The existing ranked inventory and canonical release are unchanged.</p></main></body></html>'''

if __name__=='__main__':
    path=ROOT/'almanac/loop-current-experiment.html';path.write_text(build(),encoding='utf-8');print(path)
