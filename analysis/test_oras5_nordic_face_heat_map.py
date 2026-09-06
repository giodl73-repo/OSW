import pathlib

from analyze_oras5_nordic_face_heat_map import analyze


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_face_heat_map_closes_to_section_anatomy() -> None:
    result = analyze(ROOT)
    assert result["checks"] == {"face_count_matches_control": True, "all_section_sums_match_anatomy": True, "driver_identity_closes": True}
    assert result["summary"]["positive_face_count"] + result["summary"]["negative_face_count"] == 284
    assert result["summary"]["maximum_positive_face"]["net_heat_convergence_TW_at_0C"] > 0
    assert result["summary"]["maximum_negative_face"]["net_heat_convergence_TW_at_0C"] < 0
    assert result["summary"]["top_absolute_face_share"]["20"] > 0.5
    assert result["summary"]["opposing_face_cancellation_fraction"] > 0.85
    assert 0 <= result["summary"]["top_20_total_and_density_overlap_count"] <= 20
    assert all(face["wet_cross_sectional_area_m2"] > 0 for section in result["sections"] for face in section["faces"])
    assert all(abs(face["net_heat_flux_density_MW_m2_at_0C"]) < 100 for section in result["sections"] for face in section["faces"])
    assert all(face["gross_volume_exchange_Sv"] > 0 for section in result["sections"] for face in section["faces"])
    assert all(face["gross_exchange_speed_m_s"] > 0 for section in result["sections"] for face in section["faces"])
    assert result["summary"]["maximum_driver_identity_error_TW"] < 1e-12
    assert set(result["summary"]["driver_p90_to_p10_spread"]) == {"wet_cross_sectional_area", "gross_exchange_speed", "absolute_net_thermal_transport_factor", "absolute_net_heat_convergence"}
    assert "cross-section-average transport intensity" in result["boundary"]
    assert "not a water-mass temperature" in result["boundary"]
    persistence = result["summary"]["monthly_persistence"]
    assert 0 <= persistence["same_nonzero_sign_all_12_months_face_count"] <= 284
    assert 0 <= persistence["annual_top_20_same_nonzero_sign_all_12_months_count"] <= 20
    assert set(persistence["annual_top_20_monthly_top_20_overlap"]) == {f"2018{month:02d}" for month in range(1, 13)}
    assert 1 <= persistence["annual_leader_monthly_absolute_rank_min"] <= persistence["annual_leader_monthly_absolute_rank_max"] <= 284
