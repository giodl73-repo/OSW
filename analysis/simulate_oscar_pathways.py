"""Run a receipted deterministic pathway pilot through time-varying OSCAR fields.

Tracks are kinematic surface trajectories. They do not carry parcel mass or
heat and must not be interpreted as volume or heat transport.
"""

from __future__ import annotations

import argparse
import bisect
import datetime as dt
import json
import math
import pathlib


EARTH_RADIUS_M = 6_371_008.8
DEFAULT_RELEASE_TIMES = (
    "2017-12-16T00:00:00Z", "2018-03-18T00:00:00Z",
    "2018-06-17T00:00:00Z", "2018-09-16T00:00:00Z",
)
GATE_START = (-56.5, 293.0)
GATE_STOP = (-61.9, 299.3)


def parse_time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_assignment(path: pathlib.Path, variable: str = "OSW_OSCAR_TIMESERIES") -> dict:
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{variable}="
    if prefix not in text:
        raise ValueError(f"missing {prefix} assignment")
    return json.loads(text[text.index(prefix) + len(prefix):].rstrip().removesuffix(";"))


class VelocityField:
    def __init__(self, payload: dict):
        self.payload = payload
        self.latitudes = payload["latitude_values"]
        self.longitudes = payload["longitude_values"]
        self.times = [parse_time(frame["time"]) for frame in payload["frames"]]
        self.time_seconds = [(value - self.times[0]).total_seconds() for value in self.times]
        self.frames = payload["frames"]
        self.nlon = len(self.longitudes)
        if payload["shape"] != [len(self.times), len(self.latitudes), self.nlon]:
            raise ValueError("payload shape does not match coordinates")

    @staticmethod
    def _bracket(values: list[float], value: float) -> tuple[int, float] | None:
        index = bisect.bisect_right(values, value) - 1
        if index < 0 or index >= len(values) - 1:
            return None
        fraction = (value - values[index]) / (values[index + 1] - values[index])
        return index, fraction

    def sample(self, when: dt.datetime, latitude: float, longitude: float) -> tuple[float, float] | None:
        elapsed = (when - self.times[0]).total_seconds()
        time_bracket = self._bracket(self.time_seconds, elapsed)
        lat_bracket = self._bracket([-value for value in self.latitudes], -latitude)
        lon_bracket = self._bracket(self.longitudes, longitude)
        if time_bracket is None or lat_bracket is None or lon_bracket is None:
            return None
        ti, ft = time_bracket
        yi, fy = lat_bracket
        xi, fx = lon_bracket

        temporal = []
        for frame_index in (ti, ti + 1):
            frame = self.frames[frame_index]
            corners = []
            for row in (yi, yi + 1):
                for column in (xi, xi + 1):
                    flat = row * self.nlon + column
                    u, v = frame["u_mm_s"][flat], frame["v_mm_s"][flat]
                    if u is None or v is None:
                        return None
                    corners.append((u / 1000, v / 1000))
            south = tuple(corners[0][k] * (1 - fx) + corners[1][k] * fx for k in (0, 1))
            north = tuple(corners[2][k] * (1 - fx) + corners[3][k] * fx for k in (0, 1))
            temporal.append(tuple(south[k] * (1 - fy) + north[k] * fy for k in (0, 1)))
        return tuple(temporal[0][k] * (1 - ft) + temporal[1][k] * ft for k in (0, 1))


def coordinate_rates(field: VelocityField, when: dt.datetime, latitude: float, longitude: float) -> tuple[float, float] | None:
    velocity = field.sample(when, latitude, longitude)
    if velocity is None:
        return None
    u, v = velocity
    cosine = math.cos(math.radians(latitude))
    if abs(cosine) < 1e-8:
        return None
    radians_per_second = 1 / EARTH_RADIUS_M
    return math.degrees(v * radians_per_second), math.degrees(u * radians_per_second / cosine)


def rk4_step(field: VelocityField, when: dt.datetime, latitude: float, longitude: float, seconds: float) -> tuple[float, float] | None:
    half = dt.timedelta(seconds=seconds / 2)
    full = dt.timedelta(seconds=seconds)
    k1 = coordinate_rates(field, when, latitude, longitude)
    if k1 is None:
        return None
    k2 = coordinate_rates(field, when + half, latitude + k1[0] * seconds / 2, longitude + k1[1] * seconds / 2)
    if k2 is None:
        return None
    k3 = coordinate_rates(field, when + half, latitude + k2[0] * seconds / 2, longitude + k2[1] * seconds / 2)
    if k3 is None:
        return None
    k4 = coordinate_rates(field, when + full, latitude + k3[0] * seconds, longitude + k3[1] * seconds)
    if k4 is None:
        return None
    return (
        latitude + seconds * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6,
        longitude + seconds * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6,
    )


def great_circle_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a); lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(min(1, math.sqrt(h))) / 1000


def integrate(
    field: VelocityField, release_time: dt.datetime, latitude: float, longitude: float,
    duration_days: int, timestep_hours: int, output_hours: int,
) -> dict:
    steps = duration_days * 24 // timestep_hours
    output_every = output_hours // timestep_hours
    if duration_days <= 0 or timestep_hours <= 0 or output_hours % timestep_hours:
        raise ValueError("duration/timestep/output cadence must be positive and evenly nested")
    when = release_time
    points = [{"time": when.isoformat().replace("+00:00", "Z"), "latitude": latitude, "longitude": longitude}]
    travelled_km = 0.0
    status = "completed"
    for step in range(1, steps + 1):
        result = rk4_step(field, when, latitude, longitude, timestep_hours * 3600)
        if result is None:
            status = "terminated_invalid_wet_stencil_or_domain"
            break
        travelled_km += great_circle_km((latitude, longitude), result)
        latitude, longitude = result
        when += dt.timedelta(hours=timestep_hours)
        if step % output_every == 0:
            points.append({
                "time": when.isoformat().replace("+00:00", "Z"),
                "latitude": round(latitude, 6), "longitude": round(longitude, 6),
            })
    return {
        "status": status,
        "integrated_hours": round((when - release_time).total_seconds() / 3600),
        "travelled_km": round(travelled_km, 3),
        "points": points,
    }


def gate_releases(count: int) -> list[tuple[float, float]]:
    if count < 2:
        raise ValueError("release count must be at least two")
    return [
        (
            GATE_START[0] + index * (GATE_STOP[0] - GATE_START[0]) / (count - 1),
            GATE_START[1] + index * (GATE_STOP[1] - GATE_START[1]) / (count - 1),
        )
        for index in range(count)
    ]


def simulate(payload: dict, release_times: tuple[str, ...], release_count: int, duration_days: int, timestep_hours: int, output_hours: int) -> dict:
    field = VelocityField(payload)
    releases = gate_releases(release_count)
    tracks = []
    for release_time_text in release_times:
        release_time = parse_time(release_time_text)
        for index, (latitude, longitude) in enumerate(releases, 1):
            result = integrate(field, release_time, latitude, longitude, duration_days, timestep_hours, output_hours)
            tracks.append({
                "id": f"{release_time_text[:10]}-{index:02d}",
                "release_time": release_time_text,
                "release_index": index,
                "release_latitude": latitude,
                "release_longitude": longitude,
                **result,
            })
    completed = sum(track["status"] == "completed" for track in tracks)
    return {
        "schema": "oceanlines.osw.m2-pathway-pilot.v1",
        "status": "historical deterministic surface-pathway method pilot",
        "velocity_source": {
            "schema": payload["schema"], "dataset_id": payload["dataset_id"],
            "source_version": payload["source_version"], "source_sha256": payload["source_sha256"],
            "field_sha256": payload["field_sha256"], "nominal_depth_m": payload["nominal_depth_m"],
            "shape": payload["shape"], "sampled_extent": payload["sampled_extent"],
            "native_resolution_degrees": payload["native_resolution_degrees"],
            "space_stride": payload["display_stride"],
        },
        "solver_contract": {
            "integration": "forward fourth-order Runge-Kutta on spherical latitude/longitude rates",
            "duration_days": duration_days,
            "timestep_hours": timestep_hours,
            "output_interval_hours": output_hours,
            "spatial_interpolation": "bilinear; all four corners must have jointly finite u and v",
            "temporal_interpolation": "linear between adjacent OSCAR timestamps",
            "coastal_behavior": "terminate before any RK4 stage with an invalid wet stencil or outside domain",
            "diffusion": "none",
            "random_seed": None,
            "release_depth_m": payload["nominal_depth_m"],
            "integration_direction": "forward",
        },
        "release_contract": {
            "name": "wet interior of schematic Drake Passage surface section",
            "start": {"latitude": GATE_START[0], "longitude": GATE_START[1]},
            "stop": {"latitude": GATE_STOP[0], "longitude": GATE_STOP[1]},
            "count_per_time": release_count,
            "times": list(release_times),
            "weighting": "equal-count method ensemble; not area, volume, or transport weighted",
        },
        "summary": {
            "released": len(tracks), "completed": completed,
            "terminated": len(tracks) - completed,
            "completion_fraction": completed / len(tracks),
        },
        "tracks": tracks,
        "boundary": (
            "Kinematic surface tracks through one historical year of older OSCAR data. Track count "
            "and distance are not water-mass volume, residence, Lagrangian coherence, current "
            "boundary, temperature advection, full-depth circulation, or heat transport."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-drake-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-2018.json"))
    parser.add_argument("--release-time", action="append", dest="release_times")
    parser.add_argument("--release-count", type=int, default=10)
    parser.add_argument("--duration-days", type=int, default=30)
    parser.add_argument("--timestep-hours", type=int, default=6)
    parser.add_argument("--output-hours", type=int, default=24)
    args = parser.parse_args()
    payload = simulate(
        load_assignment(args.input), tuple(args.release_times or DEFAULT_RELEASE_TIMES),
        args.release_count, args.duration_days, args.timestep_hours, args.output_hours,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {payload['summary']}")


if __name__ == "__main__":
    main()
