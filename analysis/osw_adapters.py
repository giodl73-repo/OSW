"""Pure lossless adapters for the three WP-OSW-001B historical families.

Adapters preserve pinned source meaning in an immutable candidate envelope.
They do not read files, fetch URLs, calculate science, compose admission,
render maps, rewrite receipts, or grant publication authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from types import MappingProxyType
from typing import Final

from analysis.osw_contracts import (
    ArtifactClass,
    ArtifactFamilyIdentity,
    ArtifactIdentity,
    ContractIdentityError,
    DataStatus,
    EvidenceOrigin,
    GeometrySupport,
    IntegrationOperator,
    LifecycleState,
    MethodClass,
    QuantityClass,
    QuantityIdentity,
    SupportIdentity,
    SurfaceCondition,
    parse_closed,
)
from analysis.osw_diagnostics import DiagnosticEnvelope, make_diagnostic


_NUMBER_PATTERN: Final = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$")
_FIELD_PATTERN: Final = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)*$")
_CONTRACT_VERSION: Final = "osw.evidence-receipt-adapter.v1"
_MAX_SOURCE_BYTES: Final = 1_000_000


class AdapterContractError(ValueError):
    """A fail-closed adapter error carrying only bounded diagnostic context."""

    def __init__(self, code: str, field: str) -> None:
        safe_field = (
            field
            if type(field) is str and len(field) <= 96 and _FIELD_PATTERN.fullmatch(field)
            else "unknown_field"
        )
        self.diagnostic = make_diagnostic(code, {"field": safe_field})
        super().__init__(f"{code}: {safe_field}")


@dataclass(frozen=True, slots=True)
class JsonNumber:
    lexeme: str

    def __post_init__(self) -> None:
        if type(self.lexeme) is not str or not _NUMBER_PATTERN.fullmatch(self.lexeme):
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.number")
        try:
            if not Decimal(self.lexeme).is_finite():
                raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.number")
        except InvalidOperation as error:
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.number") from error


@dataclass(frozen=True, slots=True)
class FrozenArray:
    items: tuple[object, ...]

    def __post_init__(self) -> None:
        if type(self.items) is not tuple or any(not _is_frozen_json(item) for item in self.items):
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.array")


@dataclass(frozen=True, slots=True)
class FrozenObject:
    items: tuple[tuple[str, object], ...]

    def __post_init__(self) -> None:
        if type(self.items) is not tuple:
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.object")
        keys: list[str] = []
        for item in self.items:
            if type(item) is not tuple or len(item) != 2 or type(item[0]) is not str:
                raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.object")
            if not _is_frozen_json(item[1]):
                raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.object")
            keys.append(item[0])
        if len(set(keys)) != len(keys):
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.duplicate_name")

    def require(self, key: str, field: str) -> object:
        for candidate, value in self.items:
            if candidate == key:
                return value
        raise AdapterContractError("OSW-IF-REQUIRED-FIELD", field)


def _is_frozen_json(value: object) -> bool:
    return (
        value is None
        or type(value) in (str, bool)
        or type(value) in (JsonNumber, FrozenArray, FrozenObject)
    )


@dataclass(frozen=True, slots=True)
class _RawObject:
    items: tuple[tuple[str, object], ...]


def _object_pairs(pairs: list[tuple[str, object]]) -> _RawObject:
    keys = tuple(key for key, _ in pairs)
    if len(set(keys)) != len(keys):
        raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.duplicate_name")
    return _RawObject(tuple(pairs))


def _reject_constant(_: str) -> object:
    raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.number")


def _freeze_json(value: object) -> object:
    if isinstance(value, _RawObject):
        return FrozenObject(tuple((key, _freeze_json(item)) for key, item in value.items))
    if type(value) is list:
        return FrozenArray(tuple(_freeze_json(item) for item in value))
    if value is None or type(value) in (str, bool) or isinstance(value, JsonNumber):
        return value
    raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.value")


def parse_strict_json(raw: bytes) -> FrozenObject:
    """Parse UTF-8 JSON without duplicate-name, non-finite, or repair behavior."""

    if type(raw) is not bytes:
        raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "source.bytes")
    if len(raw) > _MAX_SOURCE_BYTES:
        raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", "source.size")
    try:
        text = raw.decode("utf-8")
        decoded = json.loads(
            text,
            object_pairs_hook=_object_pairs,
            parse_int=JsonNumber,
            parse_float=JsonNumber,
            parse_constant=_reject_constant,
        )
    except AdapterContractError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "source.json") from error
    try:
        value = _freeze_json(decoded)
    except RecursionError as error:
        raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "source.json") from error
    if not isinstance(value, FrozenObject):
        raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "source.root")
    return value


def canonical_json(value: object) -> bytes:
    """Serialize a frozen tree deterministically while retaining number lexemes."""

    if value is None:
        return b"null"
    if type(value) is bool:
        return b"true" if value else b"false"
    if type(value) is str:
        return json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    if isinstance(value, JsonNumber):
        return value.lexeme.encode("ascii")
    if isinstance(value, FrozenArray):
        return b"[" + b",".join(canonical_json(item) for item in value.items) + b"]"
    if isinstance(value, FrozenObject):
        fields = (
            canonical_json(key) + b":" + canonical_json(item)
            for key, item in value.items
        )
        return b"{" + b",".join(fields) + b"}"
    raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "json.value")


@dataclass(frozen=True, slots=True)
class UnavailableField:
    field_path: str
    reason_id: str
    claim_restriction: str

    def __post_init__(self) -> None:
        for name in ("field_path", "reason_id", "claim_restriction"):
            value = getattr(self, name)
            if type(value) is not str or len(value) > 96 or not _FIELD_PATTERN.fullmatch(value):
                raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "unavailable_field")


@dataclass(frozen=True, slots=True)
class SourceReference:
    artifact: ArtifactIdentity
    role: str

    def __post_init__(self) -> None:
        if type(self.artifact) is not ArtifactIdentity:
            raise AdapterContractError("OSW-RECEIPT-BINDING", "source_reference.artifact")
        invalid_role = (
            type(self.role) is not str
            or not self.role
            or self.role != self.role.strip()
            or len(self.role) > 160
            or any(ord(character) < 32 for character in self.role)
        )
        if invalid_role:
            raise AdapterContractError("OSW-RECEIPT-BINDING", "source_reference.role")


@dataclass(frozen=True, slots=True)
class AdaptedEvidenceCandidate:
    contract_version: str
    source_artifact: ArtifactIdentity
    family: ArtifactFamilyIdentity
    lifecycle_state: LifecycleState
    source_schema: str
    detection_id: str
    quantity: QuantityIdentity
    source_references: tuple[SourceReference, ...]
    source_bytes: bytes = field(repr=False)
    source_snapshot: FrozenObject
    unavailable_fields: tuple[UnavailableField, ...]
    claim_boundary: str
    admitted: bool = False

    def __post_init__(self) -> None:
        if self.contract_version != _CONTRACT_VERSION or self.admitted is not False:
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "adapter.contract")
        required_types = (
            type(self.source_artifact) is ArtifactIdentity,
            type(self.family) is ArtifactFamilyIdentity,
            self.lifecycle_state is LifecycleState.RESEARCH_INTAKE,
            type(self.quantity) is QuantityIdentity,
            type(self.source_bytes) is bytes,
            type(self.source_snapshot) is FrozenObject,
        )
        if not all(required_types):
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "adapter.candidate")
        if hashlib.sha256(self.source_bytes).hexdigest() != self.source_artifact.sha256:
            raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", "artifact.sha256")
        if parse_strict_json(self.source_bytes) != self.source_snapshot:
            raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", "source.snapshot")
        if type(self.source_references) is not tuple or not all(
            type(item) is SourceReference for item in self.source_references
        ):
            raise AdapterContractError("OSW-RECEIPT-BINDING", "source_references")
        if type(self.unavailable_fields) is not tuple or not all(
            type(item) is UnavailableField for item in self.unavailable_fields
        ):
            raise AdapterContractError("OSW-IF-REQUIRED-FIELD", "unavailable_fields")
        if len({item.field_path for item in self.unavailable_fields}) != len(self.unavailable_fields):
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "unavailable_fields")
        unavailable_paths = tuple(item.field_path for item in self.unavailable_fields)
        if not set(self.family.unavailable_fields).issubset(unavailable_paths):
            raise AdapterContractError("OSW-IF-REQUIRED-FIELD", "unavailable_fields")
        snapshot_schema = self.source_snapshot.require("schema", "schema")
        snapshot_detection = self.source_snapshot.require("detection_id", "detection_id")
        snapshot_boundary = self.source_snapshot.require("boundary", "boundary")
        if self.source_schema != snapshot_schema:
            raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "schema")
        if self.detection_id != snapshot_detection:
            raise AdapterContractError("OSW-RECEIPT-BINDING", "detection_id")
        invalid_boundary = (
            type(self.claim_boundary) is not str
            or not self.claim_boundary
            or len(self.claim_boundary) > 2_048
            or any(ord(character) < 32 and character not in "\n\t" for character in self.claim_boundary)
        )
        if invalid_boundary:
            raise AdapterContractError("OSW-CLAIM-CEILING", "claim_boundary")
        if self.claim_boundary != snapshot_boundary:
            raise AdapterContractError("OSW-CLAIM-CEILING", "claim_boundary")
        _validate_candidate_binding(self)

    def canonical_source_json(self) -> bytes:
        return canonical_json(self.source_snapshot)


@dataclass(frozen=True, slots=True)
class FamilyDefinition:
    artifact: ArtifactIdentity
    schema: str
    detection_id: str
    status: str
    family: ArtifactFamilyIdentity
    quantity: QuantityIdentity
    source_references: tuple[tuple[str, str, str], ...]
    semantic_anchors: tuple[tuple[tuple[str, ...], str, str], ...]
    intervals: tuple[tuple[str, str], ...]
    unavailable_fields: tuple[UnavailableField, ...]


def _quantity(
    quantity_id: str,
    quantity_class: QuantityClass,
    variables: tuple[str, ...],
    vertical: str,
    sign: str,
    operator: IntegrationOperator,
    origin: EvidenceOrigin,
    supports: tuple[str, ...],
    excludes: tuple[str, ...],
) -> QuantityIdentity:
    return QuantityIdentity(
        quantity_id,
        quantity_class,
        variables,
        "W m-2",
        "energy area^-1 time^-1",
        "five daily intervals from 2026-08-07 through 2026-08-12",
        vertical,
        "fixed North Atlantic box; latitude-weighted grid-center summary",
        "not_applicable",
        sign,
        operator,
        origin,
        MethodClass.DERIVED_DIAGNOSTIC,
        supports,
        excludes,
    )


_COMMON_UNAVAILABLE: Final = (
    UnavailableField("source.provider", "not_recorded_upstream", "provenance_incomplete"),
    UnavailableField("source.product", "not_recorded_upstream", "provenance_incomplete"),
    UnavailableField("source.product_version", "not_recorded_upstream", "provenance_incomplete"),
    UnavailableField("source.source_url", "not_recorded_upstream", "provenance_incomplete"),
    UnavailableField("source.citation", "not_recorded_upstream", "citation_requires_source_review"),
    UnavailableField("source.license", "not_recorded_upstream", "rights_require_source_review"),
    UnavailableField("source.redistribution", "not_recorded_upstream", "rights_require_source_review"),
    UnavailableField("acquisition.query", "not_recorded_upstream", "request_not_reconstructable_here"),
    UnavailableField("acquisition.retrieved_at", "not_recorded_upstream", "custody_incomplete"),
    UnavailableField("support.geometry_support", "not_recorded_upstream", "cell_support_not_admitted"),
    UnavailableField("support.data_status", "not_recorded_upstream", "cell_support_not_admitted"),
    UnavailableField("support.mask_mapping", "not_recorded_upstream", "cell_support_not_admitted"),
    UnavailableField("support.surface_condition", "not_recorded_upstream", "ice_state_not_admitted"),
    UnavailableField("support.spatial_bounds", "not_recorded_upstream", "exact_extent_not_admitted"),
    UnavailableField("support.coordinate_order", "not_recorded_upstream", "grid_identity_incomplete"),
    UnavailableField("support.longitude_convention", "not_recorded_upstream", "grid_identity_incomplete"),
    UnavailableField("support.uncertainty", "not_recorded_upstream", "uncertainty_not_quantified"),
)

_INTERVALS: Final = tuple(
    (f"2026-08-{day:02d}", f"2026-08-{day + 1:02d}") for day in range(7, 12)
)


def _family_identity(
    family_id: str,
    unavailable: tuple[UnavailableField, ...],
) -> ArtifactFamilyIdentity:
    return ArtifactFamilyIdentity(
        family_id,
        "v1",
        "osw",
        ArtifactClass.SCIENTIFIC_RESULT,
        tuple(item.field_path for item in unavailable),
    )


def _d12_definition() -> FamilyDefinition:
    unavailable = _COMMON_UNAVAILABLE + (
        UnavailableField(
            "quantities.temperature_conversion",
            "not_mapped_in_pulse",
            "depth_conversion_not_admitted",
        ),
    )
    references = (
        (
            "atlas/data/gfs-mhw-surface-flux-north-atlantic-20260807-20260812.json",
            "75b4a7bdd85970fb1f7895ef14e0f615aeb83743f6e7830fac7ad8cb7036b5ec",
            "forecast-derived surface forcing",
        ),
        (
            "atlas/data/rtofs-mhw-bridge-north-atlantic-20260807-20260812.json",
            "af211d027f87ea14846a61e79ab3c1ec7048f0360842a48154a23a3ab76edcbd",
            "operational assimilative ocean state and mixed-layer thickness",
        ),
        (
            "research/osw-d11-rtofs-mhw-horizontal-advection-2026.json",
            "9da71c6bb00a8d9a641163fcb2a0f9bd7a42d4ea63cbb16a5247535cd6b7bd8f",
            "offline surface horizontal-advection screen",
        ),
    )
    return FamilyDefinition(
        ArtifactIdentity(
            "research/osw-d12-gfs-surface-flux-screen-2026.json",
            "d3d9627319179eb1d6cd5a2d3bbee1da03fe431a04c96c31a71740c027df7666",
        ),
        "osw.ocean-object-gfs-surface-flux-screen.v1",
        "OSW-D12",
        "cross_system_surface_energy_plausibility_screen",
        _family_identity("osw.d12.gfs_surface_flux_screen", unavailable),
        _quantity(
            "osw.d12.net_downward_surface_heat_flux",
            QuantityClass.SURFACE_HEAT_FLUX,
            ("gfs.dswrf", "gfs.dlwrf", "gfs.uswrf", "gfs.ulwrf", "gfs.lhtfl", "gfs.shtfl"),
            "air-sea surface boundary",
            "positive downward into the ocean surface",
            IntegrationOperator.POINT_OR_SAMPLE,
            EvidenceOrigin.OPERATIONAL_FORECAST_MODEL,
            ("surface_energy_flux.magnitude", "surface_energy_flux.sign"),
            ("native_ocean_model.closure", "temperature_change.without_depth", "causal_attribution"),
        ),
        references,
        ((
            ("method", "sign_convention"),
            "positive net flux is downward into the surface; GFS LHTFL and SHTFL are treated as positive upward losses",
            "OSW-QUANTITY-IDENTITY",
        ),),
        _INTERVALS,
        unavailable,
    )


def _d13_definition() -> FamilyDefinition:
    unavailable = _COMMON_UNAVAILABLE + (
        UnavailableField(
            "quantities.surface_flux_comparison",
            "cross_system_comparison",
            "native_closure_not_admitted",
        ),
    )
    references = (
        (
            "atlas/data/rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json",
            "5838e98bbd419050289f8b775a42c8f5e8376150d12de26133ad289068040ed4",
            "operational assimilative upper-ocean temperature",
        ),
        (
            "research/osw-d12-gfs-surface-flux-screen-2026.json",
            "d3d9627319179eb1d6cd5a2d3bbee1da03fe431a04c96c31a71740c027df7666",
            "cross-system forecast-derived surface-flux comparison",
        ),
    )
    return FamilyDefinition(
        ArtifactIdentity(
            "research/osw-d13-rtofs-mhw-upper-ocean-storage-2026.json",
            "e418b2b5bcccbb5afd8cc4cce29ef504652dbe38cb04c85b0805d0dbf9afbc27",
        ),
        "osw.ocean-object-rtofs-upper-ocean-storage-screen.v1",
        "OSW-D13",
        "fixed_depth_upper_ocean_storage_screen",
        _family_identity("osw.d13.rtofs_upper_ocean_storage", unavailable),
        _quantity(
            "osw.d13.fixed_column_storage_tendency",
            QuantityClass.STORAGE_TENDENCY,
            ("rtofs.temperature",),
            "fixed 0-50 m column sampled at 15 standard depths",
            "positive fixed-column heat gain",
            IntegrationOperator.DEPTH,
            EvidenceOrigin.OPERATIONAL_ASSIMILATIVE_MODEL,
            ("fixed_column.storage_tendency", "surface_to_column.contrast"),
            ("native_layer.heat_content", "cross_system.closure", "causal_attribution"),
        ),
        references,
        ((
            ("method", "reference_note"),
            "a constant temperature reference cancels in fixed-depth day-to-day "
            "storage differences under constant rho and cp",
            "OSW-QUANTITY-IDENTITY",
        ),),
        _INTERVALS,
        unavailable,
    )


def _d14_definition() -> FamilyDefinition:
    unavailable = _COMMON_UNAVAILABLE + (
        UnavailableField(
            "quantities.cross_system_residual",
            "mixed_evidence_origin",
            "closure_and_causation_not_admitted",
        ),
    )
    references = (
        (
            "atlas/data/rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json",
            "5838e98bbd419050289f8b775a42c8f5e8376150d12de26133ad289068040ed4",
            "RTOFS standard-depth temperature and horizontal velocity",
        ),
        (
            "research/osw-d13-rtofs-mhw-upper-ocean-storage-2026.json",
            "e418b2b5bcccbb5afd8cc4cce29ef504652dbe38cb04c85b0805d0dbf9afbc27",
            "RTOFS fixed-column storage proxy",
        ),
        (
            "research/osw-d12-gfs-surface-flux-screen-2026.json",
            "d3d9627319179eb1d6cd5a2d3bbee1da03fe431a04c96c31a71740c027df7666",
            "GFS forecast-derived surface flux",
        ),
    )
    return FamilyDefinition(
        ArtifactIdentity(
            "research/osw-d14-rtofs-mhw-upper-ocean-advection-2026.json",
            "9de6e342cea1630767e04b1620debe643b64e9e3c9f8a1fc70582caa30290672",
        ),
        "osw.ocean-object-rtofs-upper-ocean-advection-screen.v1",
        "OSW-D14",
        "cross_system_partial_fixed_column_budget_screen",
        _family_identity("osw.d14.rtofs_upper_ocean_advection", unavailable),
        _quantity(
            "osw.d14.depth_integrated_horizontal_advection",
            QuantityClass.HORIZONTAL_ADVECTION,
            ("rtofs.temperature", "rtofs.u", "rtofs.v"),
            "fixed 0-50 m column sampled at 15 standard depths",
            "positive contribution warms the fixed column",
            IntegrationOperator.DEPTH,
            EvidenceOrigin.OPERATIONAL_ASSIMILATIVE_MODEL,
            ("horizontal_advection.magnitude", "gradient_stencil.sensitivity"),
            ("native_tracer.flux", "conservative.convergence", "cross_system.closure", "causal_attribution"),
        ),
        references,
        ((
            ("method", "temporal_support"),
            "daily 00 UTC snapshots with endpoint advection averaged across each interval",
            "OSW-SUPPORT-MISMATCH",
        ),),
        _INTERVALS,
        unavailable,
    )


def _build_registry() -> tuple[tuple[FamilyDefinition, ...], MappingProxyType]:
    definitions = (_d12_definition(), _d13_definition(), _d14_definition())
    for field, values in (
        ("artifact.path", tuple(item.artifact.path for item in definitions)),
        ("schema", tuple(item.schema for item in definitions)),
        ("detection_id", tuple(item.detection_id for item in definitions)),
    ):
        if len(set(values)) != len(values):
            raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", field)
    ordered = tuple(sorted(definitions, key=lambda item: item.artifact.path))
    return ordered, MappingProxyType({item.artifact.path: item for item in ordered})


ADAPTER_FAMILIES, _BY_PATH = _build_registry()


def _validate_candidate_binding(candidate: AdaptedEvidenceCandidate) -> None:
    definition = _BY_PATH.get(candidate.source_artifact.path)
    if definition is None or candidate.source_artifact != definition.artifact:
        raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", "artifact")
    expected_references = tuple(
        SourceReference(ArtifactIdentity(path, digest), role)
        for path, digest, role in definition.source_references
    )
    expected = (
        candidate.family == definition.family,
        candidate.source_schema == definition.schema,
        candidate.detection_id == definition.detection_id,
        candidate.quantity == definition.quantity,
        candidate.source_references == expected_references,
        candidate.unavailable_fields == definition.unavailable_fields,
    )
    if not all(expected):
        raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", "adapter.binding")


def _text(value: object, field: str) -> str:
    invalid = (
        type(value) is not str
        or not value
        or value != value.strip()
        or any(ord(character) < 32 and character not in "\n\t" for character in value)
    )
    if invalid:
        raise AdapterContractError("OSW-IF-REQUIRED-FIELD", field)
    return value


def _at_path(root: FrozenObject, path: tuple[str, ...]) -> object:
    value: object = root
    for index, key in enumerate(path):
        if type(value) is not FrozenObject:
            raise AdapterContractError("OSW-IF-REQUIRED-FIELD", ".".join(path[: index + 1]))
        value = value.require(key, ".".join(path[: index + 1]))
    return value


def _validate_identity(root: FrozenObject, definition: FamilyDefinition) -> None:
    if _text(root.require("schema", "schema"), "schema") != definition.schema:
        raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "schema")
    if _text(root.require("detection_id", "detection_id"), "detection_id") != definition.detection_id:
        raise AdapterContractError("OSW-RECEIPT-BINDING", "detection_id")
    if _text(root.require("status", "status"), "status") != definition.status:
        raise AdapterContractError("OSW-CLAIM-CEILING", "status")
    _text(root.require("boundary", "boundary"), "boundary")
    for path, expected, code in definition.semantic_anchors:
        if _text(_at_path(root, path), ".".join(path)) != expected:
            raise AdapterContractError(code, ".".join(path))


def _source_references(root: FrozenObject, definition: FamilyDefinition) -> tuple[SourceReference, ...]:
    value = root.require("source_artifacts", "source_artifacts")
    if type(value) is not FrozenArray:
        raise AdapterContractError("OSW-RECEIPT-BINDING", "source_artifacts")
    found: list[tuple[str, str, str]] = []
    for item in value.items:
        if type(item) is not FrozenObject:
            raise AdapterContractError("OSW-RECEIPT-BINDING", "source_artifacts")
        found.append((
            _text(item.require("path", "source_artifacts.path"), "source_artifacts.path"),
            _text(item.require("sha256", "source_artifacts.sha256"), "source_artifacts.sha256"),
            _text(item.require("role", "source_artifacts.role"), "source_artifacts.role"),
        ))
    if tuple(found) != definition.source_references:
        raise AdapterContractError("OSW-RECEIPT-BINDING", "source_artifacts")
    return tuple(SourceReference(ArtifactIdentity(path, digest), role) for path, digest, role in found)


def _validate_intervals(root: FrozenObject, definition: FamilyDefinition) -> None:
    value = root.require("intervals", "intervals")
    if type(value) is not FrozenArray:
        raise AdapterContractError("OSW-SUPPORT-MISMATCH", "intervals")
    found: list[tuple[str, str]] = []
    for item in value.items:
        if type(item) is not FrozenObject:
            raise AdapterContractError("OSW-SUPPORT-MISMATCH", "intervals")
        found.append((
            _text(item.require("start", "intervals.start"), "intervals.start"),
            _text(item.require("end", "intervals.end"), "intervals.end"),
        ))
    if tuple(found) != definition.intervals:
        raise AdapterContractError("OSW-SUPPORT-MISMATCH", "intervals")


def adapt_historical_evidence(raw: bytes, artifact: ArtifactIdentity) -> AdaptedEvidenceCandidate:
    """Adapt one pinned family from caller-provided bytes without ambient I/O."""

    if type(artifact) is not ArtifactIdentity or artifact.path not in _BY_PATH:
        raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", "artifact.path")
    definition = _BY_PATH[artifact.path]
    if artifact != definition.artifact:
        raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", "artifact.sha256")
    root = parse_strict_json(raw)
    _validate_identity(root, definition)
    references = _source_references(root, definition)
    _validate_intervals(root, definition)
    if hashlib.sha256(raw).hexdigest() != artifact.sha256:
        raise AdapterContractError("OSW-ARTIFACT-INTEGRITY", "artifact.sha256")
    return AdaptedEvidenceCandidate(
        _CONTRACT_VERSION,
        artifact,
        definition.family,
        LifecycleState.RESEARCH_INTAKE,
        definition.schema,
        definition.detection_id,
        definition.quantity,
        references,
        raw,
        root,
        definition.unavailable_fields,
        _text(root.require("boundary", "boundary"), "boundary"),
    )


def support_from_mapping(record: dict[str, object]) -> SupportIdentity:
    """Build orthogonal support only from explicit caller-provided axes."""

    if type(record) is not dict:
        raise AdapterContractError("OSW-SUPPORT-MISMATCH", "support")
    try:
        return SupportIdentity(
            parse_closed(GeometrySupport, record["geometry_support"], "geometry_support"),
            parse_closed(DataStatus, record["data_status"], "data_status"),
            parse_closed(SurfaceCondition, record["surface_condition"], "surface_condition"),
        )
    except KeyError as error:
        raise AdapterContractError("OSW-IF-REQUIRED-FIELD", "support") from error
    except ContractIdentityError as error:
        raise AdapterContractError("OSW-SUPPORT-MISMATCH", "support") from error


def adapter_diagnostic(error: AdapterContractError) -> DiagnosticEnvelope:
    if type(error) is not AdapterContractError:
        raise AdapterContractError("OSW-IF-CONTRACT-VERSION", "adapter.error")
    return error.diagnostic
