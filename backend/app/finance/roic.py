from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ROICResult:
    ebit: float
    tax_rate: float
    nopat: float
    invested_capital: float
    roic: float
    wacc: float | None
    value_creation_spread: float | None


def calculate_roic(
    financials: pd.DataFrame,
    *,
    tax_rate: float,
    wacc: float | None = None,
) -> pd.DataFrame:
    required = {
        "fiscal_year",
        "ebit",
        "cash_and_equivalents",
        "short_term_debt",
        "long_term_debt",
        "total_equity",
    }

    missing = required.difference(financials.columns)
    if missing:
        raise ValueError(f"Missing ROIC fields: {sorted(missing)}")

    result = financials.copy()

    result["nopat"] = result["ebit"] * (1.0 - tax_rate)
    result["debt"] = (
        result["short_term_debt"].astype(float)
        + result["long_term_debt"].astype(float)
    )
    result["invested_capital"] = (
        result["total_equity"].astype(float)
        + result["debt"]
        - result["cash_and_equivalents"].astype(float)
    )

    if (result["invested_capital"] <= 0).any():
        raise ValueError("Invested capital must be positive.")

    result["roic"] = result["nopat"] / result["invested_capital"]

    if wacc is not None:
        result["wacc"] = float(wacc)
        result["value_creation_spread"] = result["roic"] - float(wacc)

    return result


def roic_summary(
    financials: pd.DataFrame,
    *,
    tax_rate: float,
    wacc: float | None = None,
) -> ROICResult:
    calculated = calculate_roic(
        financials,
        tax_rate=tax_rate,
        wacc=wacc,
    )

    row = calculated.iloc[-1]

    return ROICResult(
        ebit=float(row["ebit"]),
        tax_rate=tax_rate,
        nopat=float(row["nopat"]),
        invested_capital=float(row["invested_capital"]),
        roic=float(row["roic"]),
        wacc=wacc,
        value_creation_spread=(
            float(row["value_creation_spread"])
            if wacc is not None
            else None
        ),
    )


def roic_table(result: ROICResult) -> pd.DataFrame:
    metrics = [
        ("EBIT", result.ebit),
        ("Tax rate", result.tax_rate),
        ("NOPAT", result.nopat),
        ("Invested capital", result.invested_capital),
        ("ROIC", result.roic),
    ]

    if result.wacc is not None:
        metrics.append(("WACC", result.wacc))

    if result.value_creation_spread is not None:
        metrics.append(
            ("ROIC - WACC", result.value_creation_spread)
        )

    return pd.DataFrame(metrics, columns=["Metric", "Value"])
