"""Exercise the claim-review gate without assigning a real dataset review."""

from copy import deepcopy

from build_ocean_motion_claims import apply_claim_reviews, review_fingerprint


def decision_for(claim):
    return {"claim_id": claim["id"], "review_fingerprint": claim["review_fingerprint"],
            "reviewer": "synthetic-test-reviewer", "review_date": "2026-09-30",
            "review_status": "verified", "review_note": "Synthetic validation only"}


def fails(claims, decisions):
    try:
        apply_claim_reviews(deepcopy(claims),
                            {"schema": "osw.ocean-motion-claim-reviews.v1", "decisions": decisions})
    except ValueError:
        return True
    return False


def main():
    claim = {"id": "claim:test", "source_id": "source:test", "predicate": "reported_length",
             "value": 100, "scope": "test only", "source_locator": "paragraph 1",
             "reviewer": None, "review_date": None, "review_status": "not_individually_reviewed",
             "review_note": None}
    claim["review_fingerprint"] = review_fingerprint(claim)
    decision = decision_for(claim)
    reviewed = deepcopy(claim)
    apply_claim_reviews([reviewed], {"schema": "osw.ocean-motion-claim-reviews.v1",
                                      "decisions": [decision]})
    assert reviewed["review_status"] == "verified"
    assert review_fingerprint(reviewed) == claim["review_fingerprint"]
    changed = deepcopy(claim)
    changed["value"] = 101
    changed["review_fingerprint"] = review_fingerprint(changed)
    assert fails([changed], [decision])
    assert fails([claim], [decision, decision])
    assert fails([claim], [{**decision, "reviewer": ""}])
    assert fails([claim], [{**decision, "review_date": "20260930"}])
    vocabulary = {**claim, "vocabulary_definition": {"terms": [{"id": "warm", "criterion_summary": "Shelf water exceeds 0.5 degrees Celsius"}]}}
    vocabulary["review_fingerprint"] = review_fingerprint(vocabulary)
    vocabulary_decision = decision_for(vocabulary)
    changed_vocabulary = deepcopy(vocabulary)
    changed_vocabulary["vocabulary_definition"]["terms"][0]["criterion_summary"] = "Surface water exceeds 0.5 degrees Celsius"
    changed_vocabulary["review_fingerprint"] = review_fingerprint(changed_vocabulary)
    assert fails([changed_vocabulary], [vocabulary_decision])
    print("OK: claim review is bound to exact assertion; stale, duplicate, and incomplete decisions fail")


if __name__ == "__main__":
    main()
