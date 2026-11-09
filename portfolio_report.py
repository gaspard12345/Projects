"""Case 1 - Portfolio reporting (synthetic, educational example)."""
import pandas as pd

REQUIRED_COLUMNS = ["position_id", "isin", "security_name", "asset_class",
                    "currency", "market_value_eur", "report_date"]


def load_portfolio(path: str) -> pd.DataFrame:
    """Load the holdings file and parse dates."""
    df = pd.read_csv(path, dtype={"position_id": str, "isin": str})
    df["report_date"] = pd.to_datetime(df["report_date"], format="%Y-%m-%d")
    return df


def validate_columns(df: pd.DataFrame, required=REQUIRED_COLUMNS) -> None:
    """Stop early if the file does not have the expected structure."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def find_missing_fields(df: pd.DataFrame, required=REQUIRED_COLUMNS) -> pd.DataFrame:
    """Return the rows where at least one required field is empty."""
    mask = df[required].isna().any(axis=1)
    return df.loc[mask]


def check_market_values(df: pd.DataFrame) -> pd.DataFrame:
    """Flag missing or non-numeric values and negative values outside derivatives."""
    mv = pd.to_numeric(df["market_value_eur"], errors="coerce")
    issues = df.assign(issue="")
    issues.loc[mv.isna(), "issue"] = "missing or non-numeric market value"
    negative = (mv < 0) & (df["asset_class"] != "Derivative")
    issues.loc[negative, "issue"] = "negative market value on a non-derivative"
    return issues.loc[issues["issue"] != ""]


def check_single_report_date(df: pd.DataFrame) -> None:
    dates = df["report_date"].dropna().unique()
    if len(dates) != 1:
        raise ValueError(f"Expected one reporting date, found {len(dates)}: {dates}")


def total_value(df: pd.DataFrame) -> float:
    return float(pd.to_numeric(df["market_value_eur"], errors="coerce").sum())


def exposure_by_asset_class(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.assign(market_value_eur=pd.to_numeric(df["market_value_eur"], errors="coerce"))
    out = (clean.groupby("asset_class", as_index=False)["market_value_eur"].sum()
                .sort_values("market_value_eur", ascending=False))
    out["weight_pct"] = (out["market_value_eur"] / out["market_value_eur"].sum() * 100).round(2)
    return out.reset_index(drop=True)


def build_summary(df: pd.DataFrame) -> dict:
    validate_columns(df)
    check_single_report_date(df)
    return {
        "report_date": str(df["report_date"].iloc[0].date()),
        "positions": len(df),
        "total_value_eur": round(total_value(df), 2),
        "rows_with_missing_fields": len(find_missing_fields(df)),
        "market_value_issues": len(check_market_values(df)),
        "exposures": exposure_by_asset_class(df),
    }
