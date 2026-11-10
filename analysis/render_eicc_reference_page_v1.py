"""A small static evidence page derived from the exact EICC query contract."""
from html import escape


def page(contract):
    from eicc_reference_query_v1 import POINTS, ROUTES, SCALES, query_url, route_record_query_url

    collections = contract['collections']
    routes = ''.join('''<article class="panel" id="{id}"><h3>{label}</h3>
<p class="number">About {value} km</p><p>{scope}</p>
<p>Nine ±10 km bend probes are retained for this source-coordinate convention. Their spread is editorial sensitivity.</p>
<p><a href="{query}">Open this reference and its query map</a> · <a href="{source}">Inspect this source candidate</a></p></article>'''.format(
        id=escape(r['id']), label=escape(r['label']), value=r['approximate_reference_path_km'],
        scope=escape(r['scope']), query=escape(route_record_query_url(r['id'])), source=escape(r['source_query_url'])) for r in collections[ROUTES])
    points = ''.join('''<article class="panel point"><h3>Point {label} · track {track}</h3>
<dl><dt>Source position</dt><dd>{lon:.1f}°E, {lat:.1f}°N</dd>
<dt>Nearest shore</dt><dd>{shore:g} km</dd><dt>Seafloor depth</dt><dd>{depth:g} m</dd></dl>
<p>{scope}</p><a href="{source}">Inspect source point</a></article>'''.format(
        label=r['source_point_label'], track=r['source_track'], lon=r['longitude_degrees_east'],
        lat=r['latitude_degrees_north'], shore=r['reported_nearest_shore_distance_km'],
        depth=r['reported_bathymetry_m'], scope=escape(r['scope']), source=escape(r['source_query_url'])) for r in collections[POINTS])
    scales = ''.join('''<tr><th scope="row">Track {track}</th>
<td data-label="Reported scale">{value} km</td><td data-label="Theoretical Ro/2">{theory} km</td></tr>'''.format(
        track=r['source_track'], value=r['reported_scale_km'], theory=r['reported_theoretical_ro_over_2_km']) for r in collections[SCALES])
    html = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EICC: regional references and published source support</title>
<style>
body{margin:0;background:#f5f8fa;color:#183343;font:16px/1.55 system-ui,sans-serif}main{max-width:980px;margin:auto;padding:24px 16px 50px}a{color:#08677d;overflow-wrap:anywhere}h1{font-size:clamp(1.5rem,5vw,2.2rem);line-height:1.2}h2{font-size:1.3rem;margin-top:2rem}h3{font-size:1.05rem;margin-top:0}.panel{background:white;border:1px solid #d5e0e5;border-radius:10px;padding:16px;margin-top:16px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px}.number{font-size:1.5rem;font-weight:700;margin:.5rem 0}figure{margin:20px 0}img{display:block;width:100%;height:auto}figcaption,.note{font-size:.92rem;color:#425466}table{width:100%;border-collapse:collapse;table-layout:fixed}th,td{text-align:left;vertical-align:top;padding:9px 6px;border-bottom:1px solid #dfe7eb;overflow-wrap:anywhere}caption{text-align:left;font-weight:650;margin-bottom:8px}dl{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:6px 12px}dt,dd{margin:0;overflow-wrap:anywhere}a:focus-visible{outline:3px solid #147d92;outline-offset:4px}
@media(max-width:480px){.scales thead{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}.scales tbody{display:block}.scales tbody tr{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0 12px;padding:12px 0;border-bottom:1px solid #dfe7eb}.scales tbody th{grid-column:1/-1;padding:0 0 10px;border:0;overflow-wrap:normal}.scales tbody td{padding:0;border:0;overflow-wrap:normal}.scales tbody td::before{content:attr(data-label);display:block;font-size:.85em;color:#425466}}
</style><main>
<nav aria-label="Almanac"><a href="dashboard.html">Dashboard</a> · <a href="query.html">Query</a> · <a href="object.html?id=current%3Aeast-india-coastal">EICC current card</a></nav>
<h1>East India Coastal Current: regional references and source support</h1>
<p>Two regional reference estimates and thirteen published source-table records. The reference estimates connect approximate source locations; the table records describe sampling and spectral diagnostics. None supplies a whole-current length or seasonal dimension range.</p>
<section aria-labelledby="references"><h2 id="references">Springtime regional reference connections</h2>
<p>Gangopadhyay et al. (2013) distinguish the northward springtime western boundary current (WBC) from the southward phase they call EICC. OSW associates this source-specific spring regime with its broader EICC entry. The 50 m analysis uses survey-wide support from 22 March to 28 April 1987; exact simultaneous axis occupation dates are unknown.</p>
<p>The prose places an eastern section core near 18°N, while its caption describes about 18.5°N. Both coordinate conventions are retained separately. They are not minimum and maximum physical current lengths.</p>
<figure id="reference-map"><img src="../figures/eicc-spring-regional-reference-v1.svg" alt="Two regional geodesic reference connections from 84 degrees east,14 degrees north through83 degrees east,16 degrees north to85.5 degrees east at18 or18.5 degrees north. Approximate reference lengths590 and630 kilometres; all18 bend probes retained."><figcaption><a href="../figures/eicc-spring-regional-reference-v1.svg">Open full-size reference map</a>. All eighteen probes clear both retained land masks. Cartographic checks do not establish a measured current axis or navigational clearance.</figcaption></figure>
<div class="cards">ROUTE_CARDS</div></section>
<section aria-labelledby="sampling"><h2 id="sampling">Seven published sampling reference locations</h2>
<p>Durand et al. (2009), Table 1: each location selects maximal cross-track current variability on an altimeter track. These points are not connecting route vertices. Coordinates retain the source's 0.1° precision; its datum is unspecified.</p>
<p>Point G / track 142 supplies monsoon-current outlet context and is not strictly on the EICC path. Nearest-shore distance is not current width, and reported bathymetry is seafloor depth, not current depth or thickness.</p>
<p><a href="POINT_QUERY">Query all sampling locations</a></p><div class="cards">POINT_CARDS</div></section>
<section aria-labelledby="spectral"><h2 id="spectral">Six cross-shore spectral scales</h2>
<p>Durand et al. (2009), Table 3: e-folding scales of annual spectral power, with a theoretical Ro/2 comparison. These are not paired current widths, independent width samples or annual width extrema.</p>
<figure><img src="../figures/eicc-durand-2009-published-support-v1.svg" alt="Seven source reference points with point G marked as outlet context, and six reported annual-power scales compared with the source theoretical Ro over2 values. Exact values appear in the records and table."><figcaption><a href="../figures/eicc-durand-2009-published-support-v1.svg">Open full-size source-support chart</a>. Source coverage November 1992–July 2002; no source figures digitized.</figcaption></figure>
<div class="panel"><table class="scales"><caption>Published annual-power scales and source theoretical comparison</caption><thead><tr><th scope="col">Track</th><th scope="col">Reported scale</th><th scope="col">Theoretical Ro/2</th></tr></thead><tbody>SCALE_ROWS</tbody></table></div>
<p><a href="SCALE_QUERY">Query all spectral-scale records</a></p></section>
<section aria-labelledby="sources"><h2 id="sources">Sources and reproducible data</h2>
<p><a href="https://agupubs.onlinelibrary.wiley.com/doi/10.1002/grl.50412">Gangopadhyay et al. (2013)</a>, paragraphs 3,5,7,8 and Figure 2 caption. <a href="https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008JC004807">Durand et al. (2009)</a>, sections 2–3 and Tables 1,3.</p>
<p><a href="../research/eicc-spring-regional-reference-calculation-v1.json" download>All eighteen reference calculations and coastline checks</a> · <a href="../research/eicc-durand-2009-sampling-spectral-source-facts-v1.json" download>Published sampling and spectral facts</a> · <a href="../research/eicc-spring-regional-reference-protocol-v1.json">Declared reference measurement protocol</a></p>
<p class="note">The separate 900 km length lead remains unverified in the full primary source and is excluded from these estimates. No source-coordinate discrepancy is silently repaired. No physical edges, annual dimension ranges or named eddies are inferred here.</p></section>
</main></html>
'''
    for marker, replacement in [('ROUTE_CARDS', routes), ('POINT_CARDS', points), ('SCALE_ROWS', scales),
                                ('POINT_QUERY', escape(query_url(POINTS))), ('SCALE_QUERY', escape(query_url(SCALES)))]:
        html = html.replace(marker, replacement)
    return html.encode('utf-8')
