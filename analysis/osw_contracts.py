"""Immutable identity vocabulary for the WP-OSW-001A contract pulse.

These records identify evidence. They do not calculate science, adapt legacy
receipts, compose admission, render maps, or grant review/release authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import PurePosixPath
import re
from typing import Final, TypeVar

from analysis.osw_diagnostics import DiagnosticEnvelope, make_diagnostic


_ID_PATTERN: Final = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_VERSION_PATTERN: Final = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_GIT_COMMIT_PATTERN: Final = re.compile(r"^[0-9a-f]{40}$")
_MAX_ID_LENGTH: Final = 96
_MAX_TEXT_LENGTH: Final = 256


class ContractIdentityError(ValueError):
    """A field-local contract failure that does not echo rejected content."""

    def __init__(self, diagnostic_code: str, field: str, reason: str) -> None:
        self.diagnostic_code = diagnostic_code
        self.field = field if isinstance(field, str) and _ID_PATTERN.fullmatch(field) else "unknown_field"
        super().__init__(f"{diagnostic_code}: {self.field}: {reason}")


class ClosedValue(str, Enum):
    """An exact, non-normalizing controlled string value."""


class QuantityClass(ClosedValue):
    TEMPERATURE = "temperature"
    TEMPERATURE_ANOMALY = "temperature_anomaly"
    HEAT_CONTENT = "heat_content"
    SURFACE_HEAT_FLUX = "surface_heat_flux"
    STORAGE_TENDENCY = "storage_tendency"
    VELOCITY = "velocity"
    VOLUME_TRANSPORT = "volume_transport"
    REFERENCE_RELATIVE_HEAT_TRANSPORT = "reference_relative_heat_transport"
    HORIZONTAL_ADVECTION = "horizontal_advection"
    CONVERGENCE = "convergence"
    TRANSFORMATION = "transformation"
    RESIDUAL = "residual"


class IntegrationOperator(ClosedValue):
    NONE = "none"
    POINT_OR_SAMPLE = "point/sample"
    AREA = "area"
    DEPTH = "depth"
    SECTION = "section"
    VOLUME = "volume"
    DERIVATIVE = "derivative"
    CONVERGENCE = "convergence"
    TRANSFORMATION = "transformation"
    RESIDUAL = "residual"


class EvidenceOrigin(ClosedValue):
    OBSERVATIONAL_ANALYSIS = "observational_analysis"
    DERIVED_OBSERVATION_PRODUCT = "derived_observation_product"
    ASSIMILATIVE_REANALYSIS = "assimilative_reanalysis"
    OPERATIONAL_ASSIMILATIVE_MODEL = "operational_assimilative_model"
    OPERATIONAL_FORECAST_MODEL = "operational_forecast_model"
    SIMULATION = "simulation"
    CONCEPTUAL_SYNTHESIS = "conceptual_synthesis"


class MethodClass(ClosedValue):
    SOURCE_FIELD = "source_field"
    DERIVED_DIAGNOSTIC = "derived_diagnostic"
    SENSITIVITY = "sensitivity"
    COMPARISON = "comparison"
    UNRESOLVED_REMAINDER = "unresolved_remainder"


class GeometrySupport(ClosedValue):
    OCEAN = "ocean"
    LAND = "land"
    OUT_OF_DOMAIN = "out_of_domain"


class DataStatus(ClosedValue):
    VALID = "valid"
    SOURCE_MISSING = "source_missing"
    QUALITY_REJECTED = "quality_rejected"
    ANALYSIS_INVALID = "analysis_invalid"


class SurfaceCondition(ClosedValue):
    OPEN_WATER = "open_water"
    SEA_ICE = "sea_ice"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class LifecycleState(ClosedValue):
    RELEASED = "released"
    REVIEW_PREVIEW = "review_preview"
    EXPERIMENT = "experiment"
    RESEARCH_INTAKE = "research_intake"
    DEGRADED = "degraded"


class ArtifactClass(ClosedValue):
    SCIENTIFIC_RESULT = "scientific_result"
    DISPLAY_FIELD = "display_field"
    FIGURE_MAP = "figure_map"
    REGISTRY_TABLE = "registry_table"
    PUBLIC_PROSE_STATUS = "public_prose_status"
    REVIEW_GOVERNANCE = "review_governance"


_EnumT = TypeVar("_EnumT", bound=ClosedValue)


def parse_closed(enum_type: type[_EnumT], value: object, field: str) -> _EnumT:
    if isinstance(value, enum_type):
        return value
    if type(value) is not str:
        raise ContractIdentityError("OSW-IF-REQUIRED-FIELD", field, "expected exact string")
    try:
        return enum_type(value)
    except ValueError as error:
        raise ContractIdentityError("OSW-IF-CONTRACT-VERSION", field, "unknown controlled value") from error


def _bounded_text(value: object, field: str, *, maximum: int = _MAX_TEXT_LENGTH) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise ContractIdentityError("OSW-IF-REQUIRED-FIELD", field, "missing or non-canonical text")
    if len(value) > maximum or any(ord(character) < 32 for character in value):
        raise ContractIdentityError("OSW-IF-CONTRACT-VERSION", field, "text exceeds contract bound")
    return value


def _stable_id(value: object, field: str) -> str:
    text = _bounded_text(value, field, maximum=_MAX_ID_LENGTH)
    if not _ID_PATTERN.fullmatch(text):
        raise ContractIdentityError("OSW-IF-CONTRACT-VERSION", field, "invalid stable identity")
    return text


def _stable_version(value: object, field: str) -> str:
    text = _bounded_text(value, field, maximum=_MAX_ID_LENGTH)
    if not _VERSION_PATTERN.fullmatch(text):
        raise ContractIdentityError("OSW-IF-CONTRACT-VERSION", field, "invalid version identity")
    return text


def _exact_tuple(values: object, field: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if type(values) is not tuple or (not values and not allow_empty):
        raise ContractIdentityError("OSW-IF-REQUIRED-FIELD", field, "expected immutable identity tuple")
    checked = tuple(_stable_id(item, field) for item in values)
    if len(set(checked)) != len(checked):
        raise ContractIdentityError("OSW-IF-CONTRACT-VERSION", field, "duplicate identity")
    return checked


@dataclass(frozen=True, slots=True)
class ArtifactIdentity:
    path: str
    sha256: str

    def __post_init__(self) -> None:
        path = _bounded_text(self.path, "artifact.path")
        parsed = PurePosixPath(path)
        invalid_path = (
            not parsed.parts
            or parsed.is_absolute()
            or ".." in parsed.parts
            or "\\" in path
            or ":" in path
            or path.endswith("/")
            or str(parsed) != path
        )
        if invalid_path:
            raise ContractIdentityError(
                "OSW-ARTIFACT-INTEGRITY",
                "artifact.path",
                "path is not repository-relative POSIX",
            )
        if not _SHA256_PATTERN.fullmatch(self.sha256):
            raise ContractIdentityError("OSW-ARTIFACT-INTEGRITY", "artifact.sha256", "expected lowercase SHA-256")


@dataclass(frozen=True, slots=True)
class QuantityIdentity:
    quantity_id: str
    quantity_class: QuantityClass
    variable_ids: tuple[str, ...]
    units: str
    dimensions: str
    time_support: str
    vertical_support: str
    spatial_support: str
    reference_state: str
    sign_orientation: str
    integration_or_operator: IntegrationOperator
    evidence_origin: EvidenceOrigin
    method_class: MethodClass
    supports: tuple[str, ...]
    does_not_support: tuple[str, ...]

    def __post_init__(self) -> None:
        _stable_id(self.quantity_id, "quantity_id")
        if not isinstance(self.quantity_class, QuantityClass):
            raise ContractIdentityError("OSW-QUANTITY-IDENTITY", "quantity_class", "unknown controlled value")
        _exact_tuple(self.variable_ids, "variable_ids")
        text_fields = (
            "units",
            "dimensions",
            "time_support",
            "vertical_support",
            "spatial_support",
            "reference_state",
            "sign_orientation",
        )
        for field in text_fields:
            _bounded_text(getattr(self, field), field)
        if not isinstance(self.integration_or_operator, IntegrationOperator):
            raise ContractIdentityError("OSW-QUANTITY-IDENTITY", "integration_or_operator", "unknown controlled value")
        if not isinstance(self.evidence_origin, EvidenceOrigin):
            raise ContractIdentityError("OSW-QUANTITY-IDENTITY", "evidence_origin", "unknown controlled value")
        if not isinstance(self.method_class, MethodClass):
            raise ContractIdentityError("OSW-QUANTITY-IDENTITY", "method_class", "unknown controlled value")
        _exact_tuple(self.supports, "supports", allow_empty=True)
        _exact_tuple(self.does_not_support, "does_not_support")


@dataclass(frozen=True, slots=True)
class SupportIdentity:
    geometry_support: GeometrySupport
    data_status: DataStatus
    surface_condition: SurfaceCondition

    def __post_init__(self) -> None:
        if not isinstance(self.geometry_support, GeometrySupport):
            raise ContractIdentityError("OSW-SUPPORT-MISMATCH", "geometry_support", "unknown controlled value")
        if not isinstance(self.data_status, DataStatus):
            raise ContractIdentityError("OSW-SUPPORT-MISMATCH", "data_status", "unknown controlled value")
        if not isinstance(self.surface_condition, SurfaceCondition):
            raise ContractIdentityError("OSW-SUPPORT-MISMATCH", "surface_condition", "unknown controlled value")


@dataclass(frozen=True, slots=True)
class LifecycleIdentity:
    artifact: ArtifactIdentity
    state: LifecycleState

    def __post_init__(self) -> None:
        if not isinstance(self.artifact, ArtifactIdentity):
            raise ContractIdentityError("OSW-RELEASE-DRIFT", "artifact", "artifact identity required")
        if not isinstance(self.state, LifecycleState):
            raise ContractIdentityError("OSW-RELEASE-DRIFT", "state", "exactly one controlled state required")


@dataclass(frozen=True, slots=True)
class ReviewIdentity:
    review_id: str
    artifact: ArtifactIdentity
    source_commit: str
    reviewer_id: str
    role_lens: str
    review_date: str
    disposition: str
    scientific_endorsement: bool = False
    release_authority: bool = False

    def __post_init__(self) -> None:
        _stable_id(self.review_id, "review_id")
        if not isinstance(self.artifact, ArtifactIdentity):
            raise ContractIdentityError("OSW-REVIEW-STALE", "artifact", "artifact identity required")
        if not _GIT_COMMIT_PATTERN.fullmatch(self.source_commit):
            raise ContractIdentityError("OSW-REVIEW-STALE", "source_commit", "expected lowercase full commit")
        _stable_id(self.reviewer_id, "reviewer_id")
        _stable_id(self.role_lens, "role_lens")
        _stable_id(self.disposition, "disposition")
        try:
            date.fromisoformat(self.review_date)
        except (TypeError, ValueError) as error:
            raise ContractIdentityError("OSW-REVIEW-STALE", "review_date", "expected ISO date") from error
        if self.scientific_endorsement is not False or self.release_authority is not False:
            raise ContractIdentityError("OSW-REVIEW-STALE", "authority", "review cannot grant endorsement or release")


@dataclass(frozen=True, slots=True)
class ArtifactFamilyIdentity:
    family_id: str
    family_version: str
    owner: str
    artifact_class: ArtifactClass
    unavailable_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _stable_id(self.family_id, "family_id")
        _stable_version(self.family_version, "family_version")
        _stable_id(self.owner, "owner")
        if not isinstance(self.artifact_class, ArtifactClass):
            raise ContractIdentityError("OSW-ARTIFACT-INTEGRITY", "artifact_class", "unknown controlled value")
        _exact_tuple(self.unavailable_fields, "unavailable_fields", allow_empty=True)


def review_binding_diagnostic(review: ReviewIdentity, candidate: ArtifactIdentity) -> DiagnosticEnvelope | None:
    if not isinstance(review, ReviewIdentity) or not isinstance(candidate, ArtifactIdentity):
        return make_diagnostic("OSW-REVIEW-STALE", {"field": "artifact_identity"})
    if review.artifact != candidate:
        return make_diagnostic("OSW-REVIEW-STALE", {"field": "artifact_sha256"})
    return None
