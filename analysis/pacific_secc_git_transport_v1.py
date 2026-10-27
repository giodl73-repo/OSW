"""Git object transport for large, already verified cloud installation artifacts."""
import os
from pathlib import Path, PurePosixPath
import subprocess


def git(*args, raw=None, index=None):
    env = dict(os.environ)
    if index is not None:
        env['GIT_INDEX_FILE'] = str(Path(index).resolve())
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', '-c', 'maintenance.auto=0',
        '-c', 'gc.auto=0', '-c', 'user.name=OSW data delivery',
        '-c', 'user.email=actions@users.noreply.github.com', *args],
        input=raw, stdout=subprocess.PIPE, check=True, env=env, timeout=600).stdout.decode().strip()


def store(raw):
    return git('hash-object', '-w', '--stdin', raw=raw)


def objects(commit, paths):
    result = {}
    for path in paths:
        value = git('rev-parse', '--verify', commit + ':' + path)
        assert git('cat-file', '-t', value) == 'blob', path
        result[path] = {'oid': value, 'byteSize': int(git('cat-file', '-s', value))}
    return result


def candidate(source, entries, index):
    assert not Path(index).exists()
    assert len(entries) == len({row['path'] for row in entries})
    for row in entries:
        path = PurePosixPath(row['path'])
        assert not path.is_absolute() and '..' not in path.parts and '\\' not in row['path']
        assert row['mode'] == '100644' and row['type'] == 'blob'
        assert git('cat-file', '-t', row['sha']) == 'blob'
    git('read-tree', source, index=index)
    for row in entries:
        git('update-index', '--add', '--cacheinfo', '100644', row['sha'], row['path'], index=index)
    tree = git('write-tree', index=index)
    commit = git('commit-tree', tree, '-p', source, '-m',
                 'Install reviewed Pacific SECC reference reach and readable atlas cards')
    assert git('rev-parse', commit + '^') == source
    changes = [line.split('\t') for line in git('diff-tree', '--no-commit-id', '--name-status',
                                                '-r', source, commit).splitlines()]
    assert changes and all(status in ['A', 'M'] for status, path in changes)
    assert {path for status, path in changes} <= {row['path'] for row in entries}
    return commit


def publish(commit, branch, remote='origin'):
    # One nonforce update. No wildcard refspecs, tags, main or deletion.
    assert branch == 'codex/current-measurement-gaps'
    git('push', '--atomic', remote, commit + ':refs/heads/' + branch)
