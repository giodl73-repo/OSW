"""Bind climatological diagnostics without promoting them to current widths."""
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
OWNER='indian-south-equatorial-countercurrent'
AUDIT='research/indian-secc-oscar-source-scope-audit.json'
DATA='research/indian-secc-oscar-1995-2016-monthly-sections.json'
DATA_PIN='c223e66c26c9a0a50af99978d6df26b723524ec87acc853b4e342a2a6d286ac7'
DOCUMENTS={
    'research/indian-secc-80p333e-1995-2016-climatological-component-spans.json':'4213a1f5530f6d37714b0c3dd2e878349c8410b6d7dd5c4552a7bd2afbf09051',
    'research/indian-secc-80p667e-1995-2016-climatological-component-spans.json':'f25b5c40e8af6ba40b176280e998130dd399bb6d60822bb7c4d277d2a9cab5d6',
}


def saved():
    result=[];inputs={DATA:DATA_PIN}
    for path,pin in DOCUMENTS.items():
        raw=(ROOT/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Changed frozen Indian SECC climatological diagnostic')
        doc=json.loads(raw);inputs.update(doc['input_sha256']);result.append(doc)
    for path,pin in inputs.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=pin:raise ValueError('Changed Indian SECC original, operator or source receipt')
    return result


def inventory_entry():
    return {'current_id':OWNER,'status':'local_component_section_diagnostic_requires_scientific_review',
        'metric':'fixed_orientation_half_peak_eastward_component_span',
        'whole_current_width_km':None,'annual_width_range_km':None,
        'width_rank_eligible':False,'annual_extrema_eligible':False,
        'visual_url':'query.html?q='+quote(json.dumps({'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':OWNER}],'sort':{'field':'month','direction':'asc'},'limit':100},separators=(',',':')),safe='')+'#query-chart-section',
        'scope_note':'Two separate native columns bracket80.5 E. 1995–2016 equal-year calendar-month component climatology; 528 yearly monthly profiles retained. No current identification, physical annual extrema or pooled longitude uncertainty.',
        'sources':[{'file':p,'sha256':pin} for p,pin in DOCUMENTS.items()]}


def validate_inventory(document):
    saved()
    found=[r for r in document.get('section_span_diagnostics',[]) if r.get('current_id')==OWNER]
    if found!=[inventory_entry()]:raise ValueError('Missing or promoted Indian SECC local-section inventory')
    if any(r.get('current_id')==OWNER for r in document['measurements']):raise ValueError('Indian SECC component diagnostic promoted to published width')
    if any(r.get('current_id')==OWNER for r in document.get('review_assessments',[])):raise ValueError('Old Indian SECC source assessment must remain in audit history')
