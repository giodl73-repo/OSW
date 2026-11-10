"""Prospective EACC seed selection only; no source IO or width admission.

Earth east/north components and geographic coordinates are never interchanged.
The field interface is the frozen regional-streamline Field interface. Caller
must establish model/depth/time/source identity before any original case.
"""
import math


PEAK_TOLERANCE_M_S = 1e-10
MINIMUM_NORTHWARD_M_S = 0.1
MAXIMUM_DIRECTION_DEGREES = 45.0


def northward_support(eastward, northward):
    """Evaluate a paired vector without replacing a failed winner by another."""
    if not all(math.isfinite(value) for value in (eastward, northward)):
        return {"status": "missing_paired_velocity", "direction_from_north_degrees": None}
    direction = math.degrees(math.atan2(abs(eastward), northward))
    status = "supported_northward_seed"
    if northward < MINIMUM_NORTHWARD_M_S:
        status = "weak_or_non_northward_seed"
    elif direction > MAXIMUM_DIRECTION_DEGREES:
        status = "seed_direction_exceeds_45degrees"
    return {"status": status, "direction_from_north_degrees": direction}


def select_anchor(field):
    """Select the unique strongest paired native V near 9 S, within 39--41 E.

    Maximality is only among finite paired cells in this editorial window.
    Missing cells and equal peaks remain explicit; no convenient fallback.
    Return native indices in the field's ascending-latitude coordinate system.
    """
    result = {
        "status": "missing_seed_window",
        "target_latitude_degrees_north": -9.0,
        "longitude_window_degrees_east": [39.0, 41.0],
        "selected_latitude_index": None,
        "selected_longitude_index": None,
        "selected_lon_lat": None,
        "paired_candidate_count": 0,
        "missing_paired_candidate_count": 0,
        "tied_longitude_indices": [],
        "maximum_northward_m_s": None,
        "vector_support": None,
        "current_association_verified": False,
    }
    if not len(field.y) or not field.y[0] <= -9 <= field.y[-1]:
        return {**result, "status": "target_latitude_outside_source"}
    distances = [abs(float(latitude) + 9) for latitude in field.y]
    nearest = min(distances)
    rows = [i for i, distance in enumerate(distances) if abs(distance - nearest) <= 1e-12]
    if len(rows) != 1:
        return {**result, "status": "tied_nearest_native_latitudes"}
    yi = rows[0]
    result["selected_latitude_index"] = yi
    columns = [i for i, longitude in enumerate(field.x) if 39 <= longitude <= 41]
    candidates = [i for i in columns if all(math.isfinite(float(a[yi, i])) for a in (field.u, field.v))]
    result.update(paired_candidate_count=len(candidates),
                  missing_paired_candidate_count=len(columns) - len(candidates))
    if not candidates:
        return result
    maximum = max(float(field.v[yi, i]) for i in candidates)
    ties = [i for i in candidates if maximum - float(field.v[yi, i]) <= PEAK_TOLERANCE_M_S]
    result.update(maximum_northward_m_s=maximum, tied_longitude_indices=ties)
    if maximum < MINIMUM_NORTHWARD_M_S:
        return {**result, "status": "weak_or_non_northward_seed"}
    if len(ties) != 1:
        return {**result, "status": "numerically_tied_northward_peaks"}
    xi = ties[0]
    origin = [float(field.x[xi]), float(field.y[yi])]
    result.update(selected_longitude_index=xi, selected_lon_lat=origin)
    velocity = field.sample(*origin)
    if velocity is None:
        return {**result, "status": "missing_seed_bilinear_corners"}
    support = northward_support(*velocity)
    return {**result, "status": support["status"], "vector_support": support}


def offset_seed(field, anchor, native_latitude_offset):
    """Keep the primary longitude; never reselect a more favorable peak.

    These are method perturbations, not additional independent observations.
    Even a supported seed is not a named-current association or width result.
    """
    if type(native_latitude_offset) is not int or native_latitude_offset not in (-1, 0, 1):
        raise ValueError("Native latitude offset must be -1, 0 or 1")
    result = {"status": "primary_seed_unsupported", "native_latitude_offset": native_latitude_offset,
              "origin_lon_lat": None, "vector_support": None,
              "current_association_verified": False}
    if anchor["status"] != "supported_northward_seed":
        return result
    yi = anchor["selected_latitude_index"] + native_latitude_offset
    xi = anchor["selected_longitude_index"]
    if not 0 <= yi < len(field.y):
        return {**result, "status": "seed_offset_outside_source"}
    origin = [float(field.x[xi]), float(field.y[yi])]
    result["origin_lon_lat"] = origin
    velocity = field.sample(*origin)
    if velocity is None:
        return {**result, "status": "missing_seed_bilinear_corners"}
    support = northward_support(*velocity)
    return {**result, "status": support["status"], "vector_support": support}
