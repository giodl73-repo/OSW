"""Protect every original thesis page while allowing a generated repository cover."""
import hashlib
import io
import json
import re
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import IndirectObject, DictionaryObject, ArrayObject
from melet_hal_source import encode, fingerprint

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'research/source-data/uhlhorn-loop-2008'
CONTRACT = ROOT / 'research/uhlhorn-loop-2008-thesis-integrity-contract.json'
SOURCE_URL = 'https://scholarship.miami.edu/view/pdfCoverPage?instCode=01UOML_INST&filePid=13355493060002976&download=true'
ORIGINAL_SHA = 'c86e4086c9d3242abe52e11e8702aba7af59fc76975ec3d1173b2d572accca84'
CONTRACT_SHA = '0ac16f5415f340304cfb72ec346935e3b72393c22da006272065cc1e059c4df7'
CURRENT_FILENAME = 'repository-current.pdf'


def describe(data):
    reader = PdfReader(io.BytesIO(data), strict=True)
    if reader.is_encrypted or len(reader.pages) != 177:
        raise ValueError('Changed Uhlhorn thesis page count or encryption')
    cover = reader.pages[0].extract_text()
    cover, count = re.subn(r'Downloaded On \d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}',
                          'Downloaded On [repository clock]', cover)
    if count != 1:
        raise ValueError('Unexpected Uhlhorn repository cover clock')
    selected = {}

    def visit(obj):
        if isinstance(obj, IndirectObject):
            key = f'{obj.idnum}:{obj.generation}'
            if key not in selected:
                selected[key] = encode(obj.get_object())
                visit(obj.get_object())
        elif isinstance(obj, DictionaryObject):
            for key, value in obj.items():
                if key == '/Parent' and obj.get('/Type') == '/Page':
                    continue
                visit(value)
        elif isinstance(obj, ArrayObject):
            for value in obj:
                visit(value)

    refs = [page.indirect_reference for page in reader.pages[1:]]
    for ref in refs:
        visit(ref)
    return {'thesis_page_count': 176, 'thesis_page_refs': [encode(ref) for ref in refs],
            'thesis_graph_sha256': fingerprint({'pages': [encode(ref) for ref in refs],
                                               'objects': selected}),
            'thesis_object_count': len(selected),
            'cover_identity_sha256': hashlib.sha256(cover.encode()).hexdigest()}


def verify_rendition(data, manifest):
    if (manifest.get('source_url'), manifest.get('sha256')) != (SOURCE_URL, ORIGINAL_SHA):
        raise ValueError('Changed reviewed Uhlhorn acquisition identity')
    if len(data) > 20_000_000 or not data.startswith(b'%PDF-') or not data.rstrip().endswith(b'%%EOF'):
        raise ValueError('Invalid bounded Uhlhorn PDF')
    raw = CONTRACT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CONTRACT_SHA:
        raise ValueError('Changed frozen Uhlhorn thesis integrity contract')
    expected = json.loads(raw)['protected_document']
    if describe(data) != expected:
        raise ValueError('Changed Uhlhorn thesis pages, resources or repository identity')
    return {'response_sha256': hashlib.sha256(data).hexdigest(), 'response_bytes': len(data),
            'thesis_graph_sha256': expected['thesis_graph_sha256']}


def resolve_source(directory=None):
    directory = DIRECTORY if directory is None else Path(directory)
    manifest = json.loads((directory / 'acquisition.json').read_bytes())
    original = directory / 'journal-article.pdf'
    if original.exists():
        data = original.read_bytes()
        if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA:
            raise ValueError('Changed retained Uhlhorn source; no rendition fallback')
    else:
        original = directory / CURRENT_FILENAME
        data = original.read_bytes()
    verify_rendition(data, manifest)
    return original
