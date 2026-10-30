"""Verify confined complete-response captures without normalizing their JSON."""
import hashlib
import re
from pathlib import Path


def read_captured_json(directory, descriptor, maximum_bytes):
    if (set(descriptor) != {'file', 'bytes', 'sha256'}
        or not isinstance(descriptor['file'], str)
        or not re.fullmatch(r'capture-(main|index)-(metadata|[0-9]+)\.response\.json', descriptor['file'])
        or type(descriptor['bytes']) is not int
        or not 0 < descriptor['bytes'] <= maximum_bytes
        or not isinstance(descriptor['sha256'], str)
        or not re.fullmatch('[0-9a-f]{64}', descriptor['sha256'])):
        raise ValueError('Confined bounded complete-response descriptor required')
    target = Path(directory) / descriptor['file']
    if target.is_symlink() or not target.is_file() or target.stat().st_size != descriptor['bytes']:
        raise ValueError('Captured response file identity or size differs')
    raw = target.read_bytes()
    if len(raw) != descriptor['bytes'] or hashlib.sha256(raw).hexdigest() != descriptor['sha256']:
        raise ValueError('Captured response bytes differ')
    return raw.decode('utf-8', errors='strict')
