"""Opt-in and seam fixtures only; no coast inventory or actual source routes."""
import os
import pytest
import check_south_java_reference_cloud_v1 as case


@pytest.mark.parametrize('cloud,ref',[(False,''),(True,'refs/heads/main'),(True,'refs/heads/codex/current-measurement-gaps')])
def test_refuses_before_source_files_without_exact_cloud_limits(monkeypatch,cloud,ref):
    monkeypatch.setenv('GITHUB_ACTIONS','true' if cloud else 'false')
    monkeypatch.setenv('RUNNER_OS','Linux' if cloud else 'Windows')
    monkeypatch.setenv('GITHUB_REPOSITORY','giodl73-repo/OSW');monkeypatch.setenv('GITHUB_REF',ref)
    monkeypatch.setattr(os,'sched_getaffinity',lambda p:{0,1},raising=False)
    def forbidden(*a,**k):pytest.fail('Read source before environment refusal')
    monkeypatch.setattr(case,'read',forbidden)
    with pytest.raises(ValueError):case.controls()


def test_one_km_samples_unwrap_an_eastward_dateline_leg():
    from pyproj import Geod
    pts=case.dense([[179,0],[-179,0]],Geod(ellps='WGS84'))
    assert pts[0]==[179,0] and pts[-1]==[181,0]
    assert len(pts)>200
    assert all(0<=b[0]-a[0]<.01 for a,b in zip(pts,pts[1:]))


def test_one_km_samples_preserve_a_westward_dateline_leg():
    from pyproj import Geod
    pts=case.dense([[-179,0],[179,0]],Geod(ellps='WGS84'))
    assert pts[-1]==[-181,0]
    assert all(-.01<b[0]-a[0]<=0 for a,b in zip(pts,pts[1:]))
