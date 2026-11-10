"""Byte preserving, hash checked transport for the logical OSW query bundle.

The manifest is transport only. Workspace identity is the SHA of assembled bytes.
Legacy complete JSON bundles remain valid inputs.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'osw.query-packet.v1'
PART_LIMIT = 16 * 1024 * 1024


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptors(packet):
    if (packet.get('schema') != SCHEMA or packet.get('logical_schema') != 'osw.query-bundle.v1'
            or packet.get('hash_algorithm') != 'sha256' or packet.get('part_byte_limit') != PART_LIMIT
            or not isinstance(packet.get('logical_sha256'), str)
            or not re.fullmatch('[0-9a-f]{64}', packet['logical_sha256'])):
        raise ValueError('Unsupported query packet')
    length = packet.get('logical_byte_length')
    parts = packet.get('parts')
    if type(length) is not int or length <= 0 or not isinstance(parts, list) or len(parts) != (length + PART_LIMIT - 1) // PART_LIMIT:
        raise ValueError('Invalid query packet size')
    for i, part in enumerate(parts):
        pin = part.get('sha256', '')
        if (not isinstance(pin, str) or not re.fullmatch('[0-9a-f]{64}', pin)
                or type(part.get('index')) is not int or part['index'] != i
                or part.get('path') != f'query-parts/{i:06d}-{pin}.bin'
                or type(part.get('byte_length')) is not int
                or part['byte_length'] != min(PART_LIMIT, length - i * PART_LIMIT)):
            raise ValueError('Invalid query packet part')
    return parts


def assemble(raw, read_part):
    packet = json.loads(raw)
    if packet.get('schema') != SCHEMA:
        if packet.get('schema') != 'osw.query-bundle.v1':
            raise ValueError('Unsupported query bundle')
        return raw
    chunks = []
    for part in descriptors(packet):
        chunk = read_part(part['path'])
        if len(chunk) != part['byte_length'] or sha(chunk) != part['sha256']:
            raise ValueError('Changed query packet part: ' + part['path'])
        chunks.append(chunk)
    result = b''.join(chunks)
    if len(result) != packet['logical_byte_length'] or sha(result) != packet['logical_sha256']:
        raise ValueError('Changed logical query bundle')
    if json.loads(result).get('schema') != packet['logical_schema']:
        raise ValueError('Wrong logical query schema')
    return result


def read_bundle_bytes(path):
    path = Path(path)
    parent = path.parent.resolve()
    def read_part(relative):
        target = (parent / relative).resolve()
        if not target.is_relative_to(parent):
            raise ValueError('Query part leaves bundle directory')
        return target.read_bytes()
    return assemble(path.read_bytes(), read_part)


def load_bundle(path):
    return json.loads(read_bundle_bytes(path))


def read_bundle_at_revision(revision='HEAD', root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    def read(relative):
        return subprocess.check_output(['git', 'show', f'{revision}:almanac/{relative}'], cwd=root)
    return json.loads(assemble(read('query-data.json'), read))


def write_packet(path, raw):
    """Publish parts first, manifest last. Never remove prior parts or sources."""
    path = Path(path)
    if json.loads(raw).get('schema') != 'osw.query-bundle.v1':
        raise ValueError('Expected full logical query bundle')
    parts = []
    folder = path.parent / 'query-parts'
    folder.mkdir(exist_ok=True)
    if folder.is_symlink() or folder.resolve().parent != path.parent.resolve():
        raise ValueError('Query part directory must be local')
    for i, offset in enumerate(range(0, len(raw), PART_LIMIT)):
        chunk = raw[offset:offset + PART_LIMIT]
        pin = sha(chunk)
        relative = f'query-parts/{i:06d}-{pin}.bin'
        target = path.parent / relative
        if target.is_symlink():
            raise ValueError('Query part must not be a symbolic link')
        if target.exists():
            if target.read_bytes() != chunk:
                raise ValueError('Existing content-addressed part changed')
        else:
            temporary = target.with_suffix('.tmp')
            with temporary.open('xb') as stream:
                stream.write(chunk)
            temporary.replace(target)
        parts.append(dict(index=i, path=relative, byte_length=len(chunk), sha256=pin))
    packet = dict(schema=SCHEMA, logical_schema='osw.query-bundle.v1', hash_algorithm='sha256',
                  logical_sha256=sha(raw), logical_byte_length=len(raw), part_byte_limit=PART_LIMIT, parts=parts)
    descriptors(packet)
    temporary = path.with_suffix('.packet-tmp')
    with temporary.open('xb') as stream:
        stream.write((json.dumps(packet, indent=2) + '\n').encode('utf-8'))
    temporary.replace(path)
    return packet


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    parser.add_argument('--pack', action='store_true')
    args = parser.parse_args()
    raw = read_bundle_bytes(args.path)
    if args.pack:
        write_packet(args.path, raw)
    print(json.dumps({'logical_byte_length': len(raw), 'logical_sha256': sha(raw)}))
