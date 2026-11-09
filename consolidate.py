"""Case 2 - Consolidating and enriching two manager files (synthetic example)."""
import pandas as pd

STANDARD_COLUMNS = ["source", "fund_id", "isin", "quantity", "market_value",
                    "currency", "report_date"]

# Each source has its own column names -> one standard schema
COLUMN_MAPS = {
    "manager_a": {"Fund": "fund_id", "ISIN Code": "isin", "Qty": "quantity",
                  "MV": "market_value", "Ccy": "currency", "Date": "report_date"},
    "manager_b": {"fund_code": "fund_id", "security_isin": "isin", "nominal": "quantity",
                  "market_val": "market_value", "curr": "currency", "nav_date": "report_date"},
}


def read_manager_a(path: str) -> pd.DataFrame:
    # Semicolon-separated, comma as decimal separator, dates as dd/mm/yyyy
    df = pd.read_csv(path, sep=";", decimal=",", dtype={"ISIN Code": str})
    df = df.rename(columns=COLUMN_MAPS["manager_a"])
    df["report_date"] = pd.to_datetime(df["report_date"], format="%d/%m/%Y")
    return df.assign(source="manager_a")


def read_manager_b(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Holdings", dtype={"security_isin": str})
    df = df.rename(columns=COLUMN_MAPS["manager_b"])
    df["report_date"] = pd.to_datetime(df["report_date"])
    return df.assign(source="manager_b")


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    out = df[STANDARD_COLUMNS].copy()
    out["isin"] = out["isin"].astype("string").str.strip().str.upper()
    out["currency"] = out["currency"].astype("string").str.strip().str.upper()
    out["market_value"] = pd.to_numeric(out["market_value"], errors="coerce")
    return out


def enrich(positions: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    # validate="many_to_one" fails loudly if the reference table has duplicate ISINs
    return positions.merge(reference, on="isin", how="left",
                           validate="many_to_one", indicator=True)


def convert_to_eur(df: pd.DataFrame, fx: pd.DataFrame) -> pd.DataFrame:
    """fx has one row per currency and date: rate = units of currency per 1 EUR."""
    out = df.merge(fx, on=["currency", "report_date"], how="left")
    out["market_value_eur"] = out["market_value"] / out["eur_rate"]
    return out


def exception_report(df: pd.DataFrame) -> pd.DataFrame:
    checks = {
        "isin not found in reference data": df["_merge"] == "left_only",
        "missing market value": df["market_value"].isna(),
        "missing FX rate": df["eur_rate"].isna(),
        "invalid ISIN length": df["isin"].str.len() != 12,
        "negative market value": df["market_value"] < 0,
    }
    frames = [df.loc[mask].assign(exception=reason) for reason, mask in checks.items()]
    exc = pd.concat(frames, ignore_index=True)
    return exc[["source", "fund_id", "isin", "market_value", "currency", "exception"]]


def run(path_a, path_b, reference, fx):
    positions = pd.concat([normalise(read_manager_a(path_a)),
                           normalise(read_manager_b(path_b))], ignore_index=True)
    dates = positions["report_date"].unique()
    if len(dates) != 1:
        raise ValueError(f"Files refer to different reporting dates: {dates}")
    enriched = convert_to_eur(enrich(positions, reference), fx)
    exceptions = exception_report(enriched)
    has_problem = (enriched["_merge"] == "left_only") | enriched["market_value_eur"].isna()
    clean = enriched.loc[~has_problem].drop(columns="_merge")
    return clean, exceptions
