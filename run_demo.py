"""Demo: runs the whole pipeline on the synthetic data and prints the results."""
import pandas as pd
from portfolio_report import load_portfolio, build_summary, find_missing_fields
from consolidate import run
from isin import is_valid_isin

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

print("=" * 70)
print("CASE 1 - Portfolio report (portfolio.csv)")
print("=" * 70)
portfolio = load_portfolio("portfolio.csv")
summary = build_summary(portfolio)
print(f"Reporting date: {summary['report_date']}")
print(f"Positions: {summary['positions']}")
print(f"Total value: EUR {summary['total_value_eur']:,.0f}")
print(f"Rows with missing fields: {summary['rows_with_missing_fields']}")
print("\nExposure by asset class:")
print(summary["exposures"].to_string(index=False))
print("\nRows to fix before reporting:")
print(find_missing_fields(portfolio)[["position_id", "security_name", "market_value_eur"]].to_string(index=False))

print("\n" + "=" * 70)
print("CASE 2 - Consolidating two managers' files")
print("=" * 70)
reference = pd.DataFrame({
    "isin": ["FR0000000001", "US0000000004", "DE0000000002", "GB0000000009", "FR0000000005"],
    "issuer": ["French Republic", "Corp B", "Federal Republic of Germany", "Corp E", "Company C"],
    "asset_class": ["Government Bond", "Corporate Bond", "Government Bond", "Corporate Bond", "Equity"],
    "rating": ["AA-", "BBB", "AAA", None, None],
})
fx = pd.DataFrame({"currency": ["EUR", "USD"],
                   "report_date": pd.to_datetime(["2026-09-30"] * 2),
                   "eur_rate": [1.0, 1.10]})
clean, exceptions = run("manager_a.csv", "manager_b.xlsx", reference, fx)
print("Clean, enriched positions (in EUR):")
print(clean[["source", "isin", "market_value", "currency", "market_value_eur", "asset_class", "rating"]]
      .round(2).to_string(index=False))
print("\nException report (to check before sending):")
print(exceptions[["source", "isin", "currency", "exception"]].to_string(index=False))

print("\n" + "=" * 70)
print("ISIN check")
print("=" * 70)
for code in ["US0378331005", "US0378331006", "XX123"]:
    print(f"{code:<15} valid: {is_valid_isin(code)}")
