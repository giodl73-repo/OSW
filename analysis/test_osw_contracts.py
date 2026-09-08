import json
from dataclasses import FrozenInstanceError
from pathlib import Path
import unittest

from analysis.osw_contracts import (
    ArtifactClass,
    ArtifactFamilyIdentity,
    ArtifactIdentity,
    ContractIdentityError,
    DataStatus,
    EvidenceOrigin,
    GeometrySupport,
    IntegrationOperator,
    LifecycleIdentity,
    LifecycleState,
    MethodClass,
    QuantityClass,
    QuantityIdentity,
    ReviewIdentity,
    SupportIdentity,
    SurfaceCondition,
    parse_closed,
    review_binding_diagnostic,
)
from analysis.osw_diagnostics import (
    DIAGNOSTICS,
    DiagnosticContractError,
    DiagnosticEnvelope,
    DiagnosticRegistry,
    DiagnosticSpec,
    make_diagnostic,
)


FIXTURES = Path(__file__).parent / "fixtures" / "osw-contracts"


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def build_quantity(record):
    return QuantityIdentity(
        quantity_id=record["quantity_id"],
        quantity_class=parse_closed(QuantityClass, record["quantity_class"], "quantity_class"),
        variable_ids=tuple(record["variable_ids"]),
        units=record["units"],
        dimensions=record["dimensions"],
        time_support=record["time_support"],
        vertical_support=record["vertical_support"],
        spatial_support=record["spatial_support"],
        reference_state=record["reference_state"],
        sign_orientation=record["sign_orientation"],
        integration_or_operator=parse_closed(
            IntegrationOperator,
            record["integration_or_operator"],
            "integration_or_operator",
        ),
        evidence_origin=parse_closed(EvidenceOrigin, record["evidence_origin"], "evidence_origin"),
        method_class=parse_closed(MethodClass, record["method_class"], "method_class"),
        supports=tuple(record["supports"]),
        does_not_support=tuple(record["does_not_support"]),
    )


class DiagnosticRegistryTests(unittest.TestCase):
    def test_registry_has_exact_allocated_codes_in_deterministic_order(self):
        expected = {
            "OSW-ACQUISITION-FAILED", "OSW-ADMISSION-INCOMPLETE", "OSW-ARTIFACT-INTEGRITY",
            "OSW-CLAIM-CEILING", "OSW-DEPLOY-UNVERIFIED", "OSW-IF-CONTRACT-VERSION",
            "OSW-IF-REQUIRED-FIELD", "OSW-MAP-CONTRACT", "OSW-PRIVACY-BOUNDARY",
            "OSW-QUANTITY-IDENTITY", "OSW-RECEIPT-BINDING", "OSW-RELEASE-DRIFT",
            "OSW-REVIEW-STALE", "OSW-STATE-CONFLICT", "OSW-STATE-INCOMPATIBLE",
            "OSW-STATE-UNKNOWN", "OSW-SUPPORT-MISMATCH", "OSW-ZONE-EVIDENCE",
        }
        self.assertEqual(expected, set(DIAGNOSTICS.codes))
        self.assertEqual(tuple(sorted(expected)), DIAGNOSTICS.codes)

    def test_duplicate_code_fails_without_partial_registry(self):
        spec = DiagnosticSpec("OSW-TEST-CODE", ("007",), "Invented meaning.", "Fail safely.")
        with self.assertRaisesRegex(DiagnosticContractError, "duplicate diagnostic code"):
            DiagnosticRegistry((spec, spec))

    def test_spec_rejects_duplicate_or_unowned_interfaces(self):
        for interfaces in (("007", "007"), ("quantity",), ["007"]):
            with self.subTest(interfaces=interfaces):
                with self.assertRaises(DiagnosticContractError):
                    DiagnosticSpec("OSW-TEST-CODE", interfaces, "Invented meaning.", "Fail safely.")

    def test_unknown_code_failure_does_not_echo_candidate(self):
        candidate = "OSW-UNKNOWN-INVENTED-SENSITIVE-CANDIDATE"
        with self.assertRaises(DiagnosticContractError) as caught:
            DIAGNOSTICS.require(candidate)
        self.assertNotIn(candidate, str(caught.exception))

    def test_envelope_sorts_bounded_context(self):
        envelope = make_diagnostic("OSW-ARTIFACT-INTEGRITY", {"view_id": "invented", "attempt": 2})
        self.assertEqual(("attempt", "view_id"), tuple(key for key, _ in envelope.context))
        self.assertEqual("OSW-ARTIFACT-INTEGRITY", envelope.as_dict()["code"])

    def test_sensitive_key_fixture_fails_without_echo(self):
        fixture = load_fixture("invalid-secret-context.json")
        with self.assertRaises(DiagnosticContractError) as caught:
            make_diagnostic(fixture["code"], fixture["context"])
        self.assertNotIn(fixture["context"]["api_token"], str(caught.exception))
        self.assertNotIn(fixture["context"]["artifact_id"], str(caught.exception))

    def test_sensitive_or_unbounded_values_fail(self):
        rejected = ("Bearer INVENTED", "https://example.invalid/path?sig=INVENTED", "x" * 257)
        for value in rejected:
            with self.subTest(value=value[:20]):
                with self.assertRaises(DiagnosticContractError):
                    make_diagnostic("OSW-IF-REQUIRED-FIELD", {"detail": value})

    def test_arbitrary_context_object_fails(self):
        with self.assertRaises(DiagnosticContractError):
            make_diagnostic("OSW-IF-REQUIRED-FIELD", {"detail": object()})

    def test_direct_envelope_cannot_bypass_safe_canonical_context(self):
        spec = DIAGNOSTICS.require("OSW-IF-REQUIRED-FIELD")
        invalid_contexts = ([('field', 'value')], (("token", "INVENTED"),), (("z", 1), ("a", 2)))
        for context in invalid_contexts:
            with self.subTest(context=context):
                with self.assertRaises(DiagnosticContractError):
                    DiagnosticEnvelope(spec, context)
        unallocated = DiagnosticSpec("OSW-TEST-CODE", ("007",), "Invented meaning.", "Fail safely.")
        with self.assertRaises(DiagnosticContractError):
            DiagnosticEnvelope(unallocated, ())


class ClosedIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = load_fixture("valid-contract-identities.json")

    def test_valid_fixture_builds_immutable_identities(self):
        artifact = ArtifactIdentity(**self.fixture["artifact"])
        quantity = build_quantity(self.fixture["quantity"])
        support = SupportIdentity(
            parse_closed(GeometrySupport, self.fixture["support"]["geometry_support"], "geometry_support"),
            parse_closed(DataStatus, self.fixture["support"]["data_status"], "data_status"),
            parse_closed(SurfaceCondition, self.fixture["support"]["surface_condition"], "surface_condition"),
        )
        self.assertEqual(QuantityClass.TEMPERATURE, quantity.quantity_class)
        self.assertEqual(
            (GeometrySupport.OCEAN, DataStatus.VALID, SurfaceCondition.SEA_ICE),
            (support.geometry_support, support.data_status, support.surface_condition),
        )
        with self.assertRaises(FrozenInstanceError):
            artifact.path = "changed"

    def test_closed_value_is_exact_and_non_normalizing(self):
        for candidate in ("Temperature", " temperature", "temperature ", "TEMPERATURE"):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ContractIdentityError):
                    parse_closed(QuantityClass, candidate, "quantity_class")
        with self.assertRaises(ContractIdentityError):
            parse_closed(QuantityClass, MethodClass.SOURCE_FIELD, "quantity_class")

    def test_exact_identity_rejects_case_whitespace_and_confusable_shape(self):
        base = self.fixture["quantity"].copy()
        candidates = (
            "Invented.temperature.surface",
            " invented.temperature.surface",
            "invented_temperature_ѕurface",
        )
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                base["quantity_id"] = candidate
                with self.assertRaises(ContractIdentityError):
                    build_quantity(base)

    def test_rejected_field_label_is_not_echoed(self):
        sensitive_field = "Bearer INVENTED"
        with self.assertRaises(ContractIdentityError) as caught:
            parse_closed(QuantityClass, "not-a-quantity", sensitive_field)
        self.assertNotIn(sensitive_field, str(caught.exception))

    def test_artifact_path_is_repo_relative_posix_and_hash_lowercase(self):
        digest = self.fixture["artifact"]["sha256"]
        invalid_paths = (
            "C:/private/result.json",
            "research/C:/result.json",
            "../result.json",
            "research\\result.json",
            "./research/result.json",
            "research//result.json",
            ".",
            "research/",
        )
        for path in invalid_paths:
            with self.subTest(path=path):
                with self.assertRaises(ContractIdentityError):
                    ArtifactIdentity(path, digest)
        with self.assertRaises(ContractIdentityError):
            ArtifactIdentity("research/result.json", digest.upper())

    def test_support_axes_are_independent(self):
        cases = {
            SupportIdentity(GeometrySupport.OCEAN, DataStatus.VALID, SurfaceCondition.SEA_ICE),
            SupportIdentity(GeometrySupport.OCEAN, DataStatus.SOURCE_MISSING, SurfaceCondition.SEA_ICE),
            SupportIdentity(GeometrySupport.LAND, DataStatus.SOURCE_MISSING, SurfaceCondition.NOT_APPLICABLE),
        }
        self.assertEqual(3, len(cases))

    def test_lifecycle_requires_one_enum_value(self):
        artifact = ArtifactIdentity(**self.fixture["artifact"])
        identity = LifecycleIdentity(artifact, LifecycleState.RESEARCH_INTAKE)
        self.assertEqual(LifecycleState.RESEARCH_INTAKE, identity.state)
        with self.assertRaises(ContractIdentityError):
            LifecycleIdentity(artifact, "research_intake")

    def test_review_binding_is_exact_and_never_grants_authority(self):
        artifact = ArtifactIdentity(**self.fixture["artifact"])
        review = ReviewIdentity(
            "invented.review",
            artifact,
            "a" * 40,
            "bounded.reviewer",
            "sounder",
            "2026-09-08",
            "approved-with-conditions",
        )
        self.assertIsNone(review_binding_diagnostic(review, artifact))
        changed = ArtifactIdentity(artifact.path, "f" * 64)
        self.assertEqual("OSW-REVIEW-STALE", review_binding_diagnostic(review, changed).code)
        for authority in ("scientific_endorsement", "release_authority"):
            with self.subTest(authority=authority):
                with self.assertRaises(ContractIdentityError):
                    ReviewIdentity(
                        "invented.review",
                        artifact,
                        "a" * 40,
                        "bounded.reviewer",
                        "sounder",
                        "2026-09-08",
                        "approved",
                        **{authority: True},
                    )

    def test_family_identity_preserves_explicit_unavailable_fields(self):
        record = self.fixture["family"]
        identity = ArtifactFamilyIdentity(
            record["family_id"],
            record["family_version"],
            record["owner"],
            parse_closed(ArtifactClass, record["artifact_class"], "artifact_class"),
            tuple(record["unavailable_fields"]),
        )
        self.assertEqual(("native-budget-term",), identity.unavailable_fields)

    def test_mutable_or_duplicate_identity_collections_fail(self):
        record = self.fixture["quantity"]
        quantity = build_quantity(record)
        with self.assertRaises(ContractIdentityError):
            QuantityIdentity(
                quantity.quantity_id,
                quantity.quantity_class,
                ["invented.variable.temperature"],
                quantity.units,
                quantity.dimensions,
                quantity.time_support,
                quantity.vertical_support,
                quantity.spatial_support,
                quantity.reference_state,
                quantity.sign_orientation,
                quantity.integration_or_operator,
                quantity.evidence_origin,
                quantity.method_class,
                quantity.supports,
                quantity.does_not_support,
            )
        duplicate = dict(record, variable_ids=["invented.variable.temperature", "invented.variable.temperature"])
        with self.assertRaises(ContractIdentityError):
            build_quantity(duplicate)


if __name__ == "__main__":
    unittest.main()
