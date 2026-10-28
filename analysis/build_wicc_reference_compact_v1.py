"""Geometry-preserving narrow-screen crop of the prepared editorial SVG."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SOURCE='figures/wicc-winter-regional-reference-route-v4-candidate.svg'
OUTPUT='figures/wicc-winter-regional-reference-compact-v1.svg'


def geometry(root):
    return [(e.tag,dict(e.attrib)) for e in root.iter() if e.tag.rsplit('}',1)[-1] in ['path','polyline','circle','polygon','line']]


def build():
    raw=(ROOT/SOURCE).read_bytes()
    tree=ET.ElementTree(ET.fromstring(raw));root=tree.getroot();before=geometry(root)
    root.set('viewBox','1070 360 63 70');root.set('width','800');root.set('height','889')
    for parent in root.iter():
        for e in list(parent):
            if e.tag.rsplit('}',1)[-1]=='text':parent.remove(e)
    next(e for e in root if e.tag.endswith('}title')).text='WICC winter regional reference: December1987-January1988'
    next(e for e in root if e.tag.endswith('}desc')).text='Compact editorial map between OSW bookkeeping gates at10N and22N. Approximately1500km; no observed axis, whole-current endpoints, uncertainty or annual range established. Brown nominal line and pale translated placements have equal length.'
    for x,y,label in [(1084.611111,368.555556,'22 N'),(1114.211111,417.888889,'10 N')]:
        ET.SubElement(root,'{http://www.w3.org/2000/svg}text',{'x':str(x),'y':str(y),'font-family':'sans-serif','font-size':'2.8','fill':'#152f3d'}).text=label
    assert geometry(root)==before,'Presentation must preserve all geometry'
    ET.register_namespace('','http://www.w3.org/2000/svg')
    target=ROOT/OUTPUT;assert not target.exists();tree.write(target,encoding='utf8',xml_declaration=True)
    import pymupdf
    doc=pymupdf.open(target)
    folder=ROOT/'.pytest_cache/wicc-reference-compact-v1';folder.mkdir(exist_ok=True)
    previews={}
    for width in [800,320]:
        image=doc[0].get_pixmap(matrix=pymupdf.Matrix(width/800,width/800))
        path=folder/f'{width}.png';image.save(path);previews[str(width)]={'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':image.width,'height':image.height}
    result={'schema':'osw.wicc-reference-compact-preparation.v1','status':'RENDERED_PENDING_VISUAL_REVIEW',
            'source_file':SOURCE,'source_sha256':hashlib.sha256(raw).hexdigest(),'figure_file':OUTPUT,
            'figure_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'geometry_unchanged':True,
            'only_crop_and_text_changed':True,'previews':previews,'browser_run':False,'installed':False}
    report=ROOT/'research/wicc-winter-reference-compact-preparation-v1.json';assert not report.exists();report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'geometry_unchanged':True,'previews':previews}))


if __name__=='__main__':build()
