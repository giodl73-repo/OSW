"""Reuse the guarded binary transport with a current-neutral commit message."""
from pathlib import Path, PurePosixPath
from south_java_reference_git_transport_v1 import git, store, objects, publish


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
    commit = git('commit-tree', tree, '-p', source, '-m', 'Install verified OSW artifacts and reviewed current cards')
    assert git('rev-parse', commit + '^') == source
    changes = [line.split('\t') for line in git('diff-tree', '--no-commit-id', '--name-status', '-r', source, commit).splitlines()]
    assert changes and all(status in ['A', 'M'] for status, path in changes)
    assert {path for status, path in changes} <= {row['path'] for row in entries}
    return commit
