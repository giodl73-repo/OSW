"""Lossless cloud-only batch adapter; keeps the complete ordered case inventory."""
import json
import os
import subprocess


def encode_case(item):
    identity = {k: v for k, v in item.items() if k in ('kind', 'name')}
    if item['kind'] != 'snapshot':
        identity['request_json'] = json.dumps(item['request'], ensure_ascii=False, allow_nan=False)
    return identity


def case_key(item):
    return json.dumps(item, sort_keys=True, ensure_ascii=False, allow_nan=False)


def decode_batch(requests, batch):
    if batch.get('schema') != 'osw.delivery-native-probe.v2':
        raise ValueError('Wrong native probe schema')
    if len(requests) != len(batch['cases']):
        raise ValueError('Native probe dropped or added cases')
    results = {}
    for requested, response in zip(requests, batch['cases']):
        identity = {k: v for k, v in response.items() if k != 'raw_response_json'}
        if identity != requested:
            raise ValueError('Native probe reordered or changed case identity')
        raw = response['raw_response_json']
        if not isinstance(raw, str) or json.loads(raw).get('ok') is not True:
            raise ValueError('Invalid native response')
        key = case_key(requested)
        if key in results and results[key] != raw:
            raise ValueError('Repeated native request returned different bytes')
        results[key] = raw
    metadata = batch['metadata_json']
    if not isinstance(metadata, str) or json.loads(metadata).get('ok') is not True:
        raise ValueError('Invalid native metadata')
    return results


def run_batch(probe, mode, payload, cases):
    # Refuse before starting any native executable or opening a payload.
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('OSW_CHEN_INDIAN_SEC_DELIVERY_V2') != '1'):
        raise ValueError('Scoped cloud batch only')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One CPU and nice15 required')
    if mode not in ('main', 'index') or not 0 < len(cases) <= 1000:
        raise ValueError('Invalid batch inventory')
    requests = [encode_case(item) for item in cases]
    output = subprocess.run([str(probe), mode, str(payload)],
        input=json.dumps({'cases': requests}, ensure_ascii=False, allow_nan=False).encode(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600, check=True)
    batch = json.loads(output.stdout)
    return batch, decode_batch(requests, batch)
