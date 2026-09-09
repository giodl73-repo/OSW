"""Stable, side-effect-free diagnostics for OSW contract boundaries.

The registry describes dispositions; it does not decide scientific validity,
repair candidates, log messages, or grant release authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Final, Iterable


_CODE_PATTERN: Final = re.compile(r"^OSW-[A-Z]+(?:-[A-Z]+)*$")
_INTERFACE_PATTERN: Final = re.compile(r"^(?:all|[0-9]{3})$")
_KEY_PATTERN: Final = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_SENSITIVE_KEYS: Final = frozenset(
    {
        "access_key",
        "api_key",
        "authorization",
        "cookie",
        "credential",
        "password",
        "secret",
        "signature",
        "signed_url",
        "token",
    }
)
_SENSITIVE_VALUE: Final = re.compile(
    r"(?i)(?:\b(?:bearer|basic)\s+\S+|"
    r"(?:token|key|secret|signature|credential|password)=|"
    r"https?://\S+\?)"
)
_MAX_CONTEXT_FIELDS: Final = 16
_MAX_CONTEXT_TEXT: Final = 256
_MAX_CONTEXT_TOTAL: Final = 2_048
_MAX_INTEGER: Final = (1 << 63) - 1


class DiagnosticContractError(ValueError):
    """A stable diagnostic-contract failure that never echoes rejected input."""

    code = "OSW-IF-CONTRACT-VERSION"

    def __init__(self, reason: str) -> None:
        super().__init__(f"{self.code}: {reason}")


@dataclass(frozen=True, slots=True)
class DiagnosticSpec:
    code: str
    interfaces: tuple[str, ...]
    meaning: str
    required_behavior: str

    def __post_init__(self) -> None:
        if type(self.code) is not str or not _CODE_PATTERN.fullmatch(self.code):
            raise DiagnosticContractError("invalid diagnostic-code grammar")
        if (
            type(self.interfaces) is not tuple
            or not self.interfaces
            or any(type(item) is not str or not _INTERFACE_PATTERN.fullmatch(item) for item in self.interfaces)
            or len(set(self.interfaces)) != len(self.interfaces)
        ):
            raise DiagnosticContractError("diagnostic interface ownership missing")
        if any(
            type(text) is not str
            or not text
            or len(text) > _MAX_CONTEXT_TEXT
            or any(ord(character) < 32 for character in text)
            or _SENSITIVE_VALUE.search(text)
            for text in (self.meaning, self.required_behavior)
        ):
            raise DiagnosticContractError("diagnostic description missing")


class DiagnosticRegistry:
    """Immutable exact-match registry with deterministic code ordering."""

    __slots__ = ("_by_code", "_specs")

    def __init__(self, specs: Iterable[DiagnosticSpec]) -> None:
        by_code: dict[str, DiagnosticSpec] = {}
        for spec in specs:
            if not isinstance(spec, DiagnosticSpec):
                raise DiagnosticContractError("registry member has invalid type")
            if spec.code in by_code:
                raise DiagnosticContractError("duplicate diagnostic code")
            by_code[spec.code] = spec
        if not by_code:
            raise DiagnosticContractError("diagnostic registry is empty")
        self._specs = tuple(by_code[code] for code in sorted(by_code))
        self._by_code = MappingProxyType({spec.code: spec for spec in self._specs})

    def __iter__(self):
        return iter(self._specs)

    def __len__(self) -> int:
        return len(self._specs)

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(spec.code for spec in self._specs)

    def require(self, code: str) -> DiagnosticSpec:
        if type(code) is not str or code not in self._by_code:
            raise DiagnosticContractError("unknown diagnostic code")
        return self._by_code[code]


ContextValue = str | int | bool | None


def _safe_context_value(value: object) -> ContextValue:
    if value is None or type(value) is bool:
        return value
    if type(value) is int:
        if abs(value) > _MAX_INTEGER:
            raise DiagnosticContractError("diagnostic integer exceeds bound")
        return value
    if type(value) is str:
        if len(value) > _MAX_CONTEXT_TEXT:
            raise DiagnosticContractError("diagnostic text exceeds bound")
        if any(ord(character) < 32 for character in value):
            raise DiagnosticContractError("diagnostic text contains control character")
        if _SENSITIVE_VALUE.search(value):
            raise DiagnosticContractError("diagnostic text resembles sensitive input")
        return value
    raise DiagnosticContractError("diagnostic context type is not permitted")


def _freeze_context(context: dict[str, object] | None) -> tuple[tuple[str, ContextValue], ...]:
    if context is None:
        return ()
    if type(context) is not dict:
        raise DiagnosticContractError("diagnostic context must be a plain mapping")
    if len(context) > _MAX_CONTEXT_FIELDS:
        raise DiagnosticContractError("diagnostic context has too many fields")
    frozen: list[tuple[str, ContextValue]] = []
    for key, value in context.items():
        if type(key) is not str or not _KEY_PATTERN.fullmatch(key):
            raise DiagnosticContractError("diagnostic context key is invalid")
        if key in _SENSITIVE_KEYS or any(part in _SENSITIVE_KEYS for part in key.split("_")):
            raise DiagnosticContractError("diagnostic context key is sensitive")
        frozen.append((key, _safe_context_value(value)))
    frozen.sort(key=lambda item: item[0])
    if sum(len(key) + len(str(value)) for key, value in frozen) > _MAX_CONTEXT_TOTAL:
        raise DiagnosticContractError("diagnostic context exceeds total bound")
    return tuple(frozen)


@dataclass(frozen=True, slots=True)
class DiagnosticEnvelope:
    """A stable code plus bounded, sorted, non-secret context."""

    spec: DiagnosticSpec
    context: tuple[tuple[str, ContextValue], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.spec, DiagnosticSpec) or type(self.context) is not tuple:
            raise DiagnosticContractError("diagnostic envelope shape is invalid")
        if DIAGNOSTICS.require(self.spec.code) != self.spec:
            raise DiagnosticContractError("diagnostic envelope code is not allocated")
        try:
            context_map = dict(self.context)
        except (TypeError, ValueError) as error:
            raise DiagnosticContractError("diagnostic envelope context is invalid") from error
        if len(context_map) != len(self.context) or _freeze_context(context_map) != self.context:
            raise DiagnosticContractError("diagnostic envelope context is not canonical")

    @property
    def code(self) -> str:
        return self.spec.code

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.spec.code,
            "meaning": self.spec.meaning,
            "required_behavior": self.spec.required_behavior,
            "context": dict(self.context),
        }


def make_diagnostic(
    code: str,
    context: dict[str, object] | None = None,
) -> DiagnosticEnvelope:
    return DiagnosticEnvelope(DIAGNOSTICS.require(code), _freeze_context(context))


_DIAGNOSTIC_SPECS: Final = (
    DiagnosticSpec(
        "OSW-IF-CONTRACT-VERSION",
        ("all",),
        "Unsupported or missing required contract version.",
        "Block affected record; preserve prior accepted state or artifact.",
    ),
    DiagnosticSpec(
        "OSW-IF-REQUIRED-FIELD",
        ("all",),
        "Required or applicable field absent.",
        "Block affected admission and name the field.",
    ),
    DiagnosticSpec(
        "OSW-STATE-UNKNOWN",
        ("002",),
        "Unknown key, value, or unsupported version.",
        "Use field-local safe fallback plus visible and announced diagnostic.",
    ),
    DiagnosticSpec(
        "OSW-STATE-CONFLICT",
        ("002",),
        "Values or aliases conflict.",
        "Reject least-authoritative fragment and preserve compatible state.",
    ),
    DiagnosticSpec(
        "OSW-STATE-INCOMPATIBLE",
        ("002",),
        "Individually valid fields form an invalid combination.",
        "Use transactional fallback; never split visual and semantic state.",
    ),
    DiagnosticSpec(
        "OSW-CLAIM-CEILING",
        ("003", "007", "008", "014"),
        "Claim exceeds admitted quantity or evidence.",
        "Block scene or comparison admission.",
    ),
    DiagnosticSpec(
        "OSW-RECEIPT-BINDING",
        ("003", "005"),
        "Receipt path is missing, stale, ambiguous, or checksum-inconsistent.",
        "Block dependent scene or release.",
    ),
    DiagnosticSpec(
        "OSW-MAP-CONTRACT",
        ("004", "009"),
        "Projection, support, boundary, comparison, or text/visual mismatch.",
        "Block affected map family.",
    ),
    DiagnosticSpec(
        "OSW-PRIVACY-BOUNDARY",
        ("006",),
        "Undeclared request, storage, upload, account, cookie, telemetry, or collection.",
        "Block release.",
    ),
    DiagnosticSpec(
        "OSW-QUANTITY-IDENTITY",
        ("007",),
        "Unknown or incompatible quantity identity.",
        "Block affected result and claim.",
    ),
    DiagnosticSpec(
        "OSW-SUPPORT-MISMATCH",
        ("009",),
        "Declared support, mask, or numerical boundary mismatch.",
        "Block affected result; never coerce valid ocean.",
    ),
    DiagnosticSpec(
        "OSW-ADMISSION-INCOMPLETE",
        ("010",),
        "Required domain is missing, failed, unknown, or unjustifiably not applicable.",
        "Keep overall admission false and preserve domain decisions.",
    ),
    DiagnosticSpec(
        "OSW-ACQUISITION-FAILED",
        ("011",),
        "Provider, request, response, rights, or checksum validation failed.",
        "Preserve the prior accepted custody artifact.",
    ),
    DiagnosticSpec(
        "OSW-ARTIFACT-INTEGRITY",
        ("012",),
        "Generator, input, output, comparison, or family contract drift.",
        "Block admission or release for the affected family.",
    ),
    DiagnosticSpec(
        "OSW-REVIEW-STALE",
        ("013",),
        "Reviewed bytes differ or a required review field is absent.",
        "Do not transfer review credit to admission or release.",
    ),
    DiagnosticSpec(
        "OSW-ZONE-EVIDENCE",
        ("015",),
        "Zoning diagnostic is missing, coerced, or insufficient for promotion.",
        "Keep or demote provisional class and block diagnosed promotion.",
    ),
    DiagnosticSpec(
        "OSW-RELEASE-DRIFT",
        ("005",),
        "Candidate, lifecycle, status, citation, artifact, or owner decision disagree.",
        "Hold release without changing current claims.",
    ),
    DiagnosticSpec(
        "OSW-DEPLOY-UNVERIFIED",
        ("005",),
        "Hosted commit or journey proof is absent or failed.",
        "Retain or restore prior release and metadata.",
    ),
)

DIAGNOSTICS: Final = DiagnosticRegistry(_DIAGNOSTIC_SPECS)
