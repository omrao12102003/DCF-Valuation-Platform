from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


OPERATING_CURRENT_ASSETS = (
    "accounts_receivable",
    "inventory",
    "other_current_assets",
)

OPERATING_CURRENT_LIABILITIES = (
    "accounts_payable",
    "accrued_liabilities",
    "other_current_liabilities",
)


def _working_capital(df: pd.DataFrame) -> pd.Series:
    assets = [
        column
        for column in OPERATING_CURRENT_ASSETS
        if column in df.columns
    ]
    liabilities = [
        column
        for column in OPERATING_CURRENT_LIABILITIES
        if column in df.columns
    ]

    if not assets or not liabilities:
        raise ValueError(
            "Forecast must contain operating working-capital fields."
        )

    return df[assets].sum(axis=1) - df[liabilities].sum(axis=1)


def calculate_ufcf(
    forecast: pd.DataFrame,
    tax_rate: float,
    historical: pd.DataFrame | None = None,
) -> pd.DataFrame:
    required = {
        "fiscal_year",
        "revenue",
        "ebit",
        "depreciation_amortization",
        "capital_expenditure",
    }

    missing = required - set(forecast.columns)
    if missing:
        raise ValueError(
            f"Forecast missing required UFCF columns: {sorted(missing)}"
        )

    if not 0 <= tax_rate < 1:
        raise ValueError("tax_rate must be between 0 and 1.")

    result = forecast.copy()

    if result.empty:
        raise ValueError("Forecast cannot be empty.")

    if historical is not None:
        historical_required = {
            "accounts_receivable",
            "inventory",
            "other_current_assets",
            "accounts_payable",
            "accrued_liabilities",
        }

        historical_missing = (
            historical_required - set(historical.columns)
        )

        if historical_missing:
            raise ValueError(
                "Historical data missing working-capital fields: "
                f"{sorted(historical_missing)}"
            )

        opening_nwc = float(
            _working_capital(historical.tail(1)).iloc[0]
        )
    else:
        opening_nwc = None

    forecast_nwc = _working_capital(result)

    previous_nwc = (
        opening_nwc
        if opening_nwc is not None
        else float(forecast_nwc.iloc[0])
    )

    changes = []

    for value in forecast_nwc:
        current_nwc = float(value)
        changes.append(current_nwc - previous_nwc)
        previous_nwc = current_nwc

    result["working_capital"] = forecast_nwc
    result["change_in_nwc"] = changes

    result["nopat"] = (
        result["ebit"].astype(float)
        * (1.0 - tax_rate)
    )

    result["ufcf"] = (
        result["nopat"]
        + result["depreciation_amortization"].astype(float)
        - result["capital_expenditure"].astype(float)
        - result["change_in_nwc"]
    )

    result["ufcf_margin"] = (
        result["ufcf"] / result["revenue"].astype(float)
    )

    return result


def calculate_terminal_value(
    final_ufcf: float,
    wacc: float,
    terminal_growth_rate: float,
) -> float:
    if wacc <= 0:
        raise ValueError("WACC must be positive.")

    if terminal_growth_rate < 0:
        raise ValueError(
            "Terminal growth rate cannot be negative."
        )

    if wacc <= terminal_growth_rate:
        raise ValueError(
            "WACC must be greater than terminal growth rate."
        )

    return (
        final_ufcf * (1.0 + terminal_growth_rate)
        / (wacc - terminal_growth_rate)
    )


@dataclass(frozen=True)
class UFCFValidation:
    periods: int
    total_ufcf: float
    minimum_ufcf: float
    maximum_ufcf: float


def validate_ufcf(result: pd.DataFrame) -> UFCFValidation:
    required = {
        "fiscal_year",
        "nopat",
        "depreciation_amortization",
        "capital_expenditure",
        "change_in_nwc",
        "ufcf",
        "ufcf_margin",
    }

    missing = required - set(result.columns)
    if missing:
        raise ValueError(
            f"UFCF result missing fields: {sorted(missing)}"
        )

    if result["ufcf"].isna().any():
        raise ValueError("UFCF contains missing values.")

    return UFCFValidation(
        periods=len(result),
        total_ufcf=float(result["ufcf"].sum()),
        minimum_ufcf=float(result["ufcf"].min()),
        maximum_ufcf=float(result["ufcf"].max()),
    )
