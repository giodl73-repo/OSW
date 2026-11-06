"""Stack two source-bound editorial maps for narrow current cards."""
import hashlib
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT='research/atlantic-nsec-reference-query-contract-v2.json'
OUTPUT='figures/atlantic-nsec-regional-reference-reaches-compact-v1.svg'


def build():
    raw=(ROOT/CONTRACT).read_bytes();contract=json.loads(raw)
    rows=contract['routes']
    if [r['phase'] for r in rows]!=['northern_spring','northern_fall']:
        raise ValueError('The two reviewed source phases are required')
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="360" height="900" viewBox="0 0 360 900" role="img" aria-labelledby="title desc">',
        '<title id="title">Atlantic SEC northern branch: two regional references</title>',
        '<desc id="desc">Northern spring and fall editorial paths between selected interior gates at zero and thirty-five degrees west. Each is about 3900 kilometres. No whole-current length, annual range, observed axis or physical width is inferred.</desc>',
        '<metadata>Contract SHA256: '+hashlib.sha256(raw).hexdigest()+'</metadata>',
        '<rect width="360" height="900" fill="#f3f8fa"/><g font-family="Arial,sans-serif" fill="#153a49">']
    def text(x,y,value,size=17,bold=False,anchor=None):
        attrs=f' x="{x}" y="{y}" font-size="{size}"'
        if bold:attrs+=' font-weight="bold"'
        if anchor:attrs+=' text-anchor="'+anchor+'"'
        parts.append('<text'+attrs+'>'+html.escape(value)+'</text>')
    text(16,29,'Atlantic SEC · northern branch',21,True)
    text(16,57,'Two regional reference reaches',18)
    for row,top,title in zip(rows,[78,335],['Northern spring schematic','Northern fall schematic']):
        if row['rank_eligible'] is not False or row['annual_length_range_km'] is not None:
            raise ValueError('Regional editorial scope must remain explicit')
        if row['approximate_reference_path_km']!=3900:
            raise ValueError('The reviewed approximate distance is required')
        coords=row['coordinates_lon_lat']
        if coords[0]!=[0,2] or coords[-1][0]!=-35:
            raise ValueError('Reviewed interior gates required')
        parts.append(f'<rect x="12" y="{top}" width="336" height="245" rx="10" fill="white" stroke="#9bbac6"/>')
        text(25,top+30,title,21,True)
        project=lambda lon,lat:(48+(lon+37)*7,top+162-lat*20)
        for lon,label in [(-35,'35°W'),(-20,'20°W'),(0,'0°')]:
            x,_=project(lon,0)
            parts.append(f'<path d="M{x:g} {top+50}V{top+162}" stroke="#d8e5e9"/>')
            text(f'{x:g}',top+185,label,17,anchor='middle')
        for lat in [0,2,4]:
            _,y=project(0,lat)
            parts.append(f'<path d="M48 {y:g}H322" stroke="#d8e5e9"/>')
            text(42,f'{y+5:g}',str(lat)+'°N',17,anchor='end')
        points=' '.join(f'{x:.2f},{y:.2f}' for lon,lat in coords for x,y in [project(lon,lat)])
        parts.append('<polyline points="'+points+'" fill="none" stroke="#006e80" stroke-width="4"/>')
        for lon,lat in [coords[0],coords[-1]]:
            x,y=project(lon,lat);parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="5" fill="#955e22"/>')
        text(25,top+213,'About 3,900 km',21,True)
        text(25,top+236,'Selected 0°–35°W interior gates',17)
    for y,line in [(610,'Brown points: interior gates,'),(634,'not current origins or termini.'),
        (672,'Other SEC branches are excluded.'),(709,'Whole-current length, annual'),
        (733,'ranges and observed axis: unknown.'),(778,'Stramma & Schott (1999), Fig. 4'),
        (802,'Approximately 0–100 m context.'),(850,'WGS84 distances · 54 drawing/gate'),
        (874,'cases; not measurement uncertainty.')]:text(16,y,line)
    parts.append('</g></svg>')
    return ('\n'.join(parts)+'\n').encode()


if __name__=='__main__':
    (ROOT/OUTPUT).write_bytes(build())
