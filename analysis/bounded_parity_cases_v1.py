"""Partition comparison fixtures by exact UTF-8 bytes, retaining order and repeats."""
import json
import hashlib
import re

def expected_descriptor(filename,raw):
    if not re.fullmatch(r'compare-(main|index)-(metadata|[0-9]+)\.expected\.json',filename):
        raise ValueError('Confined expected JSON filename required')
    if not isinstance(raw,str) or not raw:raise ValueError('Nonempty exact JSON bytes required')
    body=raw.encode('utf-8')
    return {'file':filename,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()},body

def encoded(value):
    return (json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def partition(header,cases,*,maximum_bytes=64*1024*1024):
    if 'cases' in header or type(maximum_bytes) is not int or maximum_bytes<=0:
        raise ValueError('Explicit header and positive fixture bound required')
    if not isinstance(cases,list) or not cases:raise ValueError('Nonempty ordered case list required')
    base=len(encoded({**header,'cases':[]}))
    groups=[];current=[];size=base
    for row in cases:
        # One row's trailing newline is not part of its array representation.
        length=len(encoded(row))-1
        if base+length>maximum_bytes:raise ValueError('One complete response exceeds the bounded fixture size')
        addition=length+(1 if current else 0)
        if current and size+addition>maximum_bytes:
            groups.append({**header,'cases':current});current=[];size=base;addition=length
        current.append(row);size+=addition
    groups.append({**header,'cases':current})
    if [row for group in groups for row in group['cases']]!=cases:raise ValueError('Partition altered case order or repeats')
    if any(len(encoded(group))>maximum_bytes for group in groups):raise ValueError('Fixture exceeds exact encoded-byte bound')
    return groups
