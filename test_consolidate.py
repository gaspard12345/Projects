import pandas as pd
import pytest
from consolidate import run, enrich

REFERENCE = pd.DataFrame({
    "isin": ["FR0000000001", "US0000000004", "DE0000000002", "GB0000000009", "FR0000000005"],
    "issuer": ["French Republic", "Corp B", "Federal Republic of Germany", "Corp E", "Company C"],
    "asset_class": ["Government Bond", "Corporate Bond", "Government Bond", "Corporate Bond", "Equity"],
    "rating": ["AA-", "BBB", "AAA", None, None],
})
FX = pd.DataFrame({"currency": ["EUR", "USD"],
                   "report_date": pd.to_datetime(["2026-09-30"] * 2),
                   "eur_rate": [1.0, 1.10]})  # illustrative rates; GBP deliberately missing


@pytest.fixture
def result():
    return run("manager_a.csv", "manager_b.xlsx", REFERENCE, FX)


def test_isin_is_cleaned_and_matched(result):
    clean, _ = result
    assert "US0000000004" in set(clean["isin"])


def test_unknown_isin_goes_to_exceptions(result):
    _, exc = result
    assert "XX123" in set(exc.loc[exc["exception"] == "isin not found in reference data", "isin"])


def test_missing_fx_rate_reported(result):
    _, exc = result
    assert "GB0000000009" in set(exc.loc[exc["exception"] == "missing FX rate", "isin"])


def test_usd_converted(result):
    clean, _ = result
    usd = clean.loc[clean["isin"] == "US0000000004", "market_value_eur"].iloc[0]
    assert usd == pytest.approx(600000 / 1.10)


def test_missing_rating_not_invented():
    positions = pd.DataFrame({"isin": ["GB0000000009"]})
    enriched = enrich(positions, REFERENCE)
    assert len(enriched) == 1
    assert pd.isna(enriched.loc[0, "rating"])  # stays empty, never guessed


def test_duplicate_reference_rows_fail_loudly():
    dup_ref = pd.concat([REFERENCE, REFERENCE.iloc[[0]]])
    positions = pd.DataFrame({"isin": ["FR0000000001"]})
    with pytest.raises(pd.errors.MergeError):
        enrich(positions, dup_ref)
