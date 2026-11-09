import pytest
from tpt_mapping import issuer_code_type, pick_issuer_identifier


def test_priority_prefers_lei():
    assert pick_issuer_identifier(lei="TESTLEI0000000000001", internal="X1")[0] == "LEI"


def test_internal_id_is_code_9_in_v8():
    assert issuer_code_type("INTERNAL", "V8") == "9"


def test_missing_identifier_cannot_be_written_as_9_in_v8():
    kind, _ = pick_issuer_identifier()
    with pytest.raises(ValueError):
        issuer_code_type(kind, "V8")      # V8: identifiers are mandatory, 9 no longer means "none"


def test_v7_none_still_code_9():
    assert issuer_code_type("NONE", "V7") == "9"
