"""Verify all parent pins with five explicit, byte-checked historical bindings."""
import hashlib
import json
from indian_coastal_card_presentation_v1 import local_path

ALLOWED = {
    '.github/workflows/baffin-bound-candidate.yml': 'historical_workflow_dependency',
    '.github/workflows/davidson-width-candidate.yml': 'historical_workflow_dependency',
    'almanac/dashboard.html': 'existing_navigation_presentation_revision',
    'almanac/query.html': 'existing_navigation_presentation_revision',
    'research/current-gap-delivery-phase.json': 'historical_delivery_phase_control',
}
ARCHIVE_ROOT = 'research/eacc-connection-presentation-history-v2/'
ARCHIVE_ROOTS = (ARCHIVE_ROOT, 'research/eacc-connection-presentation-history-v3/')


class ParentCustodyError(ValueError):
    def __init__(self, failures):
        self.failures = failures
        super().__init__('Parent custody failures: '+', '.join(f['path']+': '+f['reason'] for f in failures))


def digest_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_parent(site, archives, manifest, bindings):
    """Never skip a pin: validate current bytes, or both registered byte versions."""
    if (manifest.get('schema') != 'osw.query-engine-manifest.v1'
            or manifest.get('engine') != 'rust-osw-query-v1' or manifest.get('abi_version') != 1
            or not isinstance(manifest.get('sha256'), dict)):
        raise ValueError('Unsupported parent engine')
    paths = [row['manifest_path'] for row in bindings]
    if len(paths) != len(set(paths)) or set(paths) != set(ALLOWED):
        raise ValueError('Exactly the five reviewed historical source paths are required')
    production = set()
    for value in manifest.values():
        if isinstance(value, dict):
            production.update(value.get('dependency_proof', {}).get('production_dependencies', []))
    if production.intersection(paths):
        raise ValueError('Cannot rebind a compiled production dependency')
    by_path = {row['manifest_path']: row for row in bindings}
    for row in bindings:
        if (row['role'] != ALLOWED[row['manifest_path']]
                or not row['archive_path'].startswith(ARCHIVE_ROOTS)
                or row['historical_commit'] != '0c2f0dc67a9ba25cbf488f634702b05f30401f2f'
                or row['historical_sha256'] == row['installed_path_sha256']
                or manifest['sha256'].get(row['manifest_path']) != row['historical_sha256']):
            raise ValueError('Changed registered binding meaning or inherited source pin')
    failures = []; checked = []; historical = []
    for path, expected in manifest['sha256'].items():
        try:
            current = local_path(site, path)
            actual = digest_file(current)
            if path == 'research/current-gap-delivery-phase.json':
                phase = json.loads(current.read_bytes())
                if (phase.get('phase') != 'source-review-only-v1'
                        or phase.get('heavy_work_permitted') is not False
                        or type(phase.get('max_heavy_local_jobs')) is not int
                        or phase['max_heavy_local_jobs'] != 0
                        or type(phase.get('max_heavy_cloud_jobs')) is not int
                        or phase['max_heavy_cloud_jobs'] != 1):
                    raise ValueError('Live global delivery phase must remain disabled')
            if path not in by_path:
                if actual != expected:
                    failures.append({'path': path, 'reason': 'unregistered mismatch', 'expected': expected, 'actual': actual})
                else: checked.append(path)
                continue
            row = by_path[path]
            archive = local_path(archives, row['archive_path'])
            archived = digest_file(archive)
            if (archived != expected or archive.stat().st_size != row['historical_bytes']
                    or actual != row['installed_path_sha256'] or current.stat().st_size != row['installed_path_bytes']):
                failures.append({'path': path, 'reason': 'registered current or historical bytes differ',
                                 'expected': expected, 'actual': actual, 'archived': archived})
            else:
                historical.append({'path': path, 'historical_sha256': archived,
                                   'installed_sha256': actual, 'archive_path': row['archive_path']})
        except (OSError, ValueError) as error:
            failures.append({'path': path, 'reason': str(error)})
    if failures:
        raise ParentCustodyError(failures)
    return {'status': 'PASS', 'manifest_paths_verified': len(checked)+len(historical),
            'current_path_matches': len(checked), 'historical_bindings': historical,
            'production_dependencies_rebound': 0}
