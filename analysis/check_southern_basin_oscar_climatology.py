"""Bind three independent climatologies to existing unresolved section owners."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA='research/southern-basin-oscar-1995-2016-monthly-sections.json'
DATA_PIN='64886bab229872c4352b8b1786c9f40a95a05efa0ea123cd99a500dc75371065'
DOCUMENTS={
    'research/south-atlantic-30w-1995-2016-climatological-component-spans.json':'3825f8ff3a55218d2f6808aedb17394f411e14ccfa0f88c5d7713e30fdc9c112',
    'research/south-pacific-100w-1995-2016-climatological-component-spans.json':'708efa3c3bb40eaf503e99698e7b48e3445f24e75b27242641870e7251b70024',
    'research/south-indian-80e-1995-2016-climatological-component-spans.json':'f777b7689328f47a352a597dd30004a8e25c494aa083aeda24bb94ac31dc39e8',
}
BASE_SOURCES={
    'south-atlantic':('research/south-atlantic-30w-2013-monthly-component-spans.json','c576f4444d2b551ec46043861e464f8fc9e8ee06c80cfcd3158f0c69c9bcafc1'),
    'south-pacific':('research/south-pacific-100w-2013-monthly-component-spans.json','ea1f41ba0378aa7306f6de0e3c17d117a2f77b00f110d276e390a9479d97f44d'),
    'south-indian':('research/south-indian-80e-2013-monthly-component-spans.json','71242c8fe62379e4ed661dc2ad4a4ed4908aabc7558fe40ba715892883607346'),
}


def saved():
    docs=[];inputs={DATA:DATA_PIN}
    for path,pin in DOCUMENTS.items():
        raw=(ROOT/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Changed frozen southern-basin climatological diagnostic')
        doc=json.loads(raw);inputs.update(doc['input_sha256']);docs.append(doc)
    for path,pin in inputs.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=pin:raise ValueError('Changed southern-basin original, operator or receipt')
    return docs


def validate_inventory(inventory):
    for path,doc in zip(DOCUMENTS,saved()):
        owner=doc['current_id']
        entries=[r for r in inventory['section_span_diagnostics'] if r['current_id']==owner]
        original,original_pin=BASE_SOURCES[owner]
        expected=[{'file':original,'sha256':original_pin},{'file':path,'sha256':DOCUMENTS[path]}]
        if len(entries)!=1 or entries[0]['sources']!=expected:raise ValueError('Missing, pooled or rebound southern-basin evidence')
        if any(r['current_id']==owner for r in inventory['measurements']):raise ValueError('Southern-basin component promoted to published width')
        entry=entries[0]
        if entry['whole_current_width_km'] is not None or entry['annual_width_range_km'] is not None or entry['width_rank_eligible'] is not False or entry['annual_extrema_eligible'] is not False:
            raise ValueError('Southern-basin component promoted to physical dimension')
