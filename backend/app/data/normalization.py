from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "fiscal_year",
    "revenue",
    "cost_of_revenue",
    "operating_expenses",
    "depreciation_amortization",
    "interest_expense",
    "taxes",
    "net_income",
    "cash_and_equivalents",
    "accounts_receivable",
    "inventory",
    "property_plant_equipment",
    "accounts_payable",
    "short_term_debt",
    "long_term_debt",
    "total_equity",
    "operating_cash_flow",
    "capital_expenditure",
}


def load_historical_data(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)

    missing = REQUIRED_COLUMNS.difference(frame.columns)

    if missing:
        raise ValueError(
            f"Historical dataset is missing required columns: {sorted(missing)}"
        )

    frame = frame.sort_values("fiscal_year").reset_index(drop=True)

    numeric_columns = [
        column
        for column in frame.columns
        if column != "fiscal_year"
    ]

    frame[numeric_columns] = frame[numeric_columns].apply(
        pd.to_numeric,
        errors="raise",
    )

    return frame


def calculate_historical_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()

    result["revenue_growth"] = result["revenue"].pct_change()

    result["gross_profit"] = (
        result["revenue"] - result["cost_of_revenue"]
    )

    result["gross_margin"] = (
        result["gross_profit"] / result["revenue"]
    )

    result["ebitda"] = (
        result["gross_profit"] - result["operating_expenses"]
    )

    result["ebitda_margin"] = (
        result["ebitda"] / result["revenue"]
    )

    result["ebit"] = (
        result["ebitda"] - result["depreciation_amortization"]
    )

    result["ebit_margin"] = (
        result["ebit"] / result["revenue"]
    )

    result["net_margin"] = (
        result["net_income"] / result["revenue"]
    )

    result["net_debt"] = (
        result["short_term_debt"]
        + result["long_term_debt"]
        - result["cash_and_equivalents"]
    )

    result["free_cash_flow"] = (
        result["operating_cash_flow"]
        - result["capital_expenditure"]
    )

    result["fcf_margin"] = (
        result["free_cash_flow"] / result["revenue"]
    )

    return result
