from dataclasses import FrozenInstanceError
import hashlib
import json
import logging
import os
from pathlib import Path
import socket
import unittest
import urllib.request
from unittest import mock

from analysis.osw_adapters import (
    ADAPTER_FAMILIES,
    AdaptedEvidenceCandidate,
    AdapterContractError,
    FrozenArray,
    FrozenObject,
    JsonNumber,
    adapt_historical_evidence,
    adapter_diagnostic,
    canonical_json,
    parse_strict_json,
    support_from_mapping,
)
from analysis.osw_contracts import (
    ArtifactIdentity,
    DataStatus,
    GeometrySupport,
    QuantityClass,
    SurfaceCondition,
)


ROOT = Path(__file__).parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "osw-adapters"


def fixture_bytes(name):
    return (FIXTURES / name).read_bytes()


def binding_fixture():
    return json.loads((FIXTURES / "family-bindings.json").read_text(encoding="utf-8"))


def family_bytes(definition):
    return (ROOT / definition.artifact.path).read_bytes()


def mutate_family(definition, mutation):
    record = json.loads(family_bytes(definition))
    mutation(record)
    return json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class StrictJsonTests(unittest.TestCase):
    def test_unknown_fields_null_order_and_number_lexemes_round_trip(self):
        source = fixture_bytes("strict-valid.json")
        parsed = parse_strict_json(source)
        reparsed = parse_strict_json(canonical_json(parsed))
        self.assertEqual(parsed, reparsed)
        unknown = parsed.require("unknown", "unknown")
        self.assertIsInstance(unknown, FrozenObject)
        self.assertEqual(
            ("explicit_null", "decimal", "large_integer", "ordered"),
            tuple(key for key, _ in unknown.items),
        )
        self.assertEqual("1.2300e+2", unknown.require("decimal", "unknown.decimal").lexeme)
        self.assertEqual("9007199254740993", unknown.require("large_integer", "unknown.large_integer").lexeme)

    def test_duplicate_and_nonfinite_values_fail_before_dispatch(self):
        for name in ("invalid-duplicate.json", "invalid-nonfinite.json"):
            with self.subTest(name=name):
                with self.assertRaises(AdapterContractError) as caught:
                    parse_strict_json(fixture_bytes(name))
                self.assertEqual("OSW-IF-CONTRACT-VERSION", caught.exception.diagnostic.code)

    def test_invalid_encoding_trailing_content_and_non_object_root_fail(self):
        candidates = (b"\xff", b'{"ok":true} trailing', b"[1,2,3]")
        for candidate in candidates:
            with self.subTest(candidate=candidate[:12]):
                with self.assertRaises(AdapterContractError):
                    parse_strict_json(candidate)

    def test_non_bytes_and_oversized_payload_fail(self):
        for candidate in ("{}", b" " * 1_000_001):
            with self.subTest(kind=type(candidate).__name__):
                with self.assertRaises(AdapterContractError):
                    parse_strict_json(candidate)

    def test_direct_frozen_constructors_reject_mutable_or_duplicate_content(self):
        with self.assertRaises(AdapterContractError):
            FrozenArray([JsonNumber("1")])
        with self.assertRaises(AdapterContractError):
            FrozenObject((("a", JsonNumber("1")), ("a", JsonNumber("2"))))
        with self.assertRaises(AdapterContractError):
            FrozenObject((("a", object()),))

    def test_canonical_serializer_rejects_arbitrary_objects(self):
        with self.assertRaises(AdapterContractError):
            canonical_json(object())


class HistoricalAdapterTests(unittest.TestCase):
    def test_registry_matches_exact_frozen_inventory(self):
        fixture = binding_fixture()["families"]
        found = [
            {
                "path": item.artifact.path,
                "sha256": item.artifact.sha256,
                "schema": item.schema,
                "quantity_class": item.quantity.quantity_class.value,
            }
            for item in ADAPTER_FAMILIES
        ]
        self.assertEqual(fixture, found)
        self.assertEqual(tuple(sorted(item["path"] for item in fixture)), tuple(item["path"] for item in found))

    def test_all_pinned_families_adapt_without_source_rewrite(self):
        before = {item.artifact.path: hashlib.sha256(family_bytes(item)).hexdigest() for item in ADAPTER_FAMILIES}
        for definition in ADAPTER_FAMILIES:
            with self.subTest(schema=definition.schema):
                raw = family_bytes(definition)
                candidate = adapt_historical_evidence(raw, definition.artifact)
                self.assertIsInstance(candidate, AdaptedEvidenceCandidate)
                self.assertFalse(candidate.admitted)
                self.assertEqual(definition.schema, candidate.source_schema)
                self.assertEqual(definition.detection_id, candidate.detection_id)
                self.assertEqual(definition.quantity, candidate.quantity)
                self.assertEqual(parse_strict_json(candidate.canonical_source_json()), candidate.source_snapshot)
                self.assertGreaterEqual(len(candidate.unavailable_fields), 7)
        after = {item.artifact.path: hashlib.sha256(family_bytes(item)).hexdigest() for item in ADAPTER_FAMILIES}
        self.assertEqual(before, after)

    def test_quantities_and_claim_ceilings_remain_distinct(self):
        by_detection = {item.detection_id: item.quantity for item in ADAPTER_FAMILIES}
        self.assertEqual(QuantityClass.SURFACE_HEAT_FLUX, by_detection["OSW-D12"].quantity_class)
        self.assertEqual(QuantityClass.STORAGE_TENDENCY, by_detection["OSW-D13"].quantity_class)
        self.assertEqual(QuantityClass.HORIZONTAL_ADVECTION, by_detection["OSW-D14"].quantity_class)
        self.assertIn("temperature_change.without_depth", by_detection["OSW-D12"].does_not_support)
        self.assertIn("cross_system.closure", by_detection["OSW-D13"].does_not_support)
        self.assertIn("conservative.convergence", by_detection["OSW-D14"].does_not_support)

    def test_source_references_are_opaque_and_not_recursively_opened(self):
        raw_by_path = {item.artifact.path: family_bytes(item) for item in ADAPTER_FAMILIES}
        def deny_open(*args, **kwargs):
            raise AssertionError(f"unexpected adapter I/O: {type(args[0]).__name__ if args else 'none'}")

        with (
            mock.patch("builtins.open", side_effect=deny_open),
            mock.patch.object(socket, "create_connection", side_effect=AssertionError("unexpected network")),
            mock.patch.object(urllib.request, "urlopen", side_effect=AssertionError("unexpected network")),
        ):
            candidates = [
                adapt_historical_evidence(raw_by_path[item.artifact.path], item.artifact)
                for item in ADAPTER_FAMILIES
            ]
        self.assertEqual((3, 2, 3), tuple(len(item.source_references) for item in candidates))

    def test_import_and_execution_have_no_ambient_state_effects(self):
        definition = ADAPTER_FAMILIES[0]
        raw = family_bytes(definition)
        environment = dict(os.environ)
        handlers = tuple(logging.getLogger().handlers)
        working_directory = os.getcwd()
        with mock.patch("builtins.open", side_effect=AssertionError("unexpected filesystem access")):
            candidate = adapt_historical_evidence(raw, definition.artifact)
        self.assertFalse(candidate.admitted)
        self.assertEqual(environment, dict(os.environ))
        self.assertEqual(handlers, tuple(logging.getLogger().handlers))
        self.assertEqual(working_directory, os.getcwd())

    def test_unknown_path_and_wrong_declared_hash_fail_without_echo(self):
        definition = ADAPTER_FAMILIES[0]
        sensitive_candidate = "private-machine-secret.json"
        cases = (
            ArtifactIdentity(sensitive_candidate, "a" * 64),
            ArtifactIdentity(definition.artifact.path, "a" * 64),
        )
        for artifact in cases:
            with self.subTest(path=artifact.path):
                with self.assertRaises(AdapterContractError) as caught:
                    adapt_historical_evidence(family_bytes(definition), artifact)
                self.assertEqual("OSW-ARTIFACT-INTEGRITY", adapter_diagnostic(caught.exception).code)
                self.assertNotIn(sensitive_candidate, str(caught.exception))

    def test_schema_detection_status_source_time_and_checksum_fail_distinctly(self):
        definition = ADAPTER_FAMILIES[0]
        cases = (
            (lambda item: item.__setitem__("schema", "invented.unknown.v1"), "OSW-IF-CONTRACT-VERSION"),
            (lambda item: item.__setitem__("detection_id", "OSW-D99"), "OSW-RECEIPT-BINDING"),
            (lambda item: item.__setitem__("status", "invented_status"), "OSW-CLAIM-CEILING"),
            (lambda item: item["source_artifacts"][0].__setitem__("role", "invented role"), "OSW-RECEIPT-BINDING"),
            (lambda item: item["intervals"][0].__setitem__("start", "2026-08-06"), "OSW-SUPPORT-MISMATCH"),
            (lambda item: item.__setitem__("boundary", item["boundary"] + " Invented."), "OSW-ARTIFACT-INTEGRITY"),
        )
        for mutation, expected in cases:
            with self.subTest(expected=expected):
                with self.assertRaises(AdapterContractError) as caught:
                    adapt_historical_evidence(mutate_family(definition, mutation), definition.artifact)
                self.assertEqual(expected, caught.exception.diagnostic.code)

    def test_family_semantic_anchors_detect_sign_reference_and_time_changes(self):
        paths = (
            (
                ADAPTER_FAMILIES[0],
                lambda item: item["method"].__setitem__("sign_convention", "positive upward"),
                "OSW-QUANTITY-IDENTITY",
            ),
            (
                ADAPTER_FAMILIES[1],
                lambda item: item["method"].__setitem__("reference_note", "invented reference"),
                "OSW-QUANTITY-IDENTITY",
            ),
            (
                ADAPTER_FAMILIES[2],
                lambda item: item["method"].__setitem__("temporal_support", "invented time"),
                "OSW-SUPPORT-MISMATCH",
            ),
        )
        for definition, mutation, expected in paths:
            with self.subTest(schema=definition.schema):
                with self.assertRaises(AdapterContractError) as caught:
                    adapt_historical_evidence(mutate_family(definition, mutation), definition.artifact)
                self.assertEqual(expected, caught.exception.diagnostic.code)

    def test_support_axes_are_explicit_and_subsurface_under_ice_survives(self):
        support = support_from_mapping(binding_fixture()["support"])
        self.assertEqual(
            (GeometrySupport.OCEAN, DataStatus.VALID, SurfaceCondition.SEA_ICE),
            (support.geometry_support, support.data_status, support.surface_condition),
        )
        for missing in ("geometry_support", "data_status", "surface_condition"):
            record = dict(binding_fixture()["support"])
            del record[missing]
            with self.subTest(missing=missing):
                with self.assertRaises(AdapterContractError):
                    support_from_mapping(record)
        invalid = dict(binding_fixture()["support"], data_status="invented")
        with self.assertRaises(AdapterContractError) as caught:
            support_from_mapping(invalid)
        self.assertEqual("OSW-SUPPORT-MISMATCH", caught.exception.diagnostic.code)

    def test_candidates_and_nested_records_are_immutable(self):
        definition = ADAPTER_FAMILIES[0]
        candidate = adapt_historical_evidence(family_bytes(definition), definition.artifact)
        with self.assertRaises(FrozenInstanceError):
            candidate.admitted = True
        with self.assertRaises(FrozenInstanceError):
            candidate.source_snapshot.items = ()
        with self.assertRaises(AdapterContractError):
            candidate.__class__(
                candidate.contract_version,
                candidate.source_artifact,
                candidate.family,
                candidate.lifecycle_state,
                candidate.source_schema,
                "OSW-D99",
                candidate.quantity,
                candidate.source_references,
                candidate.source_bytes,
                candidate.source_snapshot,
                candidate.unavailable_fields,
                candidate.claim_boundary,
            )


if __name__ == "__main__":
    unittest.main()
