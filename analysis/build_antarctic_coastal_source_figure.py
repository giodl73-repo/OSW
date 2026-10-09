"""Reconstruct the credited Figure 3 raster from the pinned final original.

Optional dependency: pip install -r requirements-figures.txt.
No download, geographic digitization, recoloring or resampling is performed.
"""
import hashlib,json
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
def main():
    receipt=json.loads((ROOT/'research/source-data/schubert-aacc-2021/source-figure.json').read_bytes())
    original=(ROOT/receipt['source_document_file']).read_bytes()
    if hashlib.sha256(original).hexdigest()!=receipt['source_document_sha256']:
        raise ValueError('Original Antarctic coastal paper checksum mismatch')
    if pymupdf.VersionBind!=receipt['extraction_software']['version']:
        raise ValueError('Use the pinned PyMuPDF version from requirements-figures.txt')
    with pymupdf.open(stream=original,filetype='pdf') as paper:
        extracted=paper.extract_image(receipt['image_xref'])
    image=extracted['image']
    if extracted['ext']!='png' or [extracted['width'],extracted['height']]!=receipt['pixel_dimensions']:
        raise ValueError('Changed published figure dimensions or image type')
    if len(image)!=receipt['asset_bytes'] or hashlib.sha256(image).hexdigest()!=receipt['asset_sha256']:
        raise ValueError('Extracted source raster differs from reviewed figure')
    (ROOT/receipt['asset_file']).write_bytes(image)
    print('PASS: reconstructed original section-location map matches reviewed bytes')

if __name__=='__main__':main()
