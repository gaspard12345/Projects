import pandas as pd
import pytest
from portfolio_report import (load_portfolio, validate_columns, find_missing_fields,
                              check_market_values, total_value, exposure_by_asset_class,
                              build_summary)


@pytest.fixture
def portfolio():
    return load_portfolio("portfolio.csv")


def test_required_columns_present(portfolio):
    validate_columns(portfolio)  # should not raise


def test_missing_column_raises(portfolio):
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_columns(portfolio.drop(columns=["currency"]))


def test_missing_fields_detected(portfolio):
    assert list(find_missing_fields(portfolio)["position_id"]) == ["P008"]


def test_total_value(portfolio):
    assert total_value(portfolio) == pytest.approx(9_600_000)


def test_weights_sum_to_100(portfolio):
    exp = exposure_by_asset_class(portfolio)
    assert exp["weight_pct"].sum() == pytest.approx(100, abs=0.05)


def test_negative_bond_value_flagged():
    df = pd.DataFrame({"asset_class": ["Corporate Bond", "Derivative"],
                       "market_value_eur": [-100.0, -50.0]})
    flagged = check_market_values(df)
    assert len(flagged) == 1
    assert flagged.iloc[0]["asset_class"] == "Corporate Bond"


def test_mixed_dates_rejected(portfolio):
    bad = portfolio.copy()
    bad.loc[0, "report_date"] = pd.Timestamp("2026-06-30")
    with pytest.raises(ValueError, match="one reporting date"):
        build_summary(bad)
