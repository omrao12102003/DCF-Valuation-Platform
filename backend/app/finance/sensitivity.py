from __future__ import annotations

import numpy as np
import pandas as pd

from app.finance.dcf import DCFInputs, calculate_dcf
from app.finance.ufcf import calculate_terminal_value


def dcf_sensitivity(
    ufcf: pd.DataFrame,
    *,
    net_debt: float,
    shares_outstanding: float,
    base_wacc: float,
    base_terminal_growth: float,
    wacc_range: tuple[float, ...] | None = None,
    terminal_growth_range: tuple[float, ...] | None = None,
    tax_rate: float = 0.21,
) -> pd.DataFrame:
    if wacc_range is None:
        wacc_range = tuple(
            round(base_wacc + x, 6)
            for x in (-0.02, -0.01, 0.0, 0.01, 0.02)
        )

    if terminal_growth_range is None:
        terminal_growth_range = tuple(
            round(base_terminal_growth + x, 6)
            for x in (-0.01, -0.005, 0.0, 0.005, 0.01)
        )

    if not ufcf.index.equals(pd.RangeIndex(len(ufcf))):
        ufcf = ufcf.reset_index(drop=True)

    final_ufcf = float(ufcf["ufcf"].iloc[-1])
    rows: list[dict[str, float]] = []

    for wacc in wacc_range:
        if wacc <= 0:
            raise ValueError("WACC must be positive.")

        for growth in terminal_growth_range:
            if growth >= wacc:
                raise ValueError(
                    f"Terminal growth ({growth:.4%}) must be below WACC ({wacc:.4%})."
                )

            periods = np.arange(1, len(ufcf) + 1, dtype=float)
            discount_factors = 1.0 / ((1.0 + wacc) ** periods)
            pv_explicit = float(
                (ufcf["ufcf"].astype(float).to_numpy() * discount_factors).sum()
            )

            terminal_value = calculate_terminal_value(
                final_ufcf,
                wacc=wacc,
                terminal_growth_rate=growth,
            )
            pv_terminal = terminal_value / ((1.0 + wacc) ** len(ufcf))
            enterprise_value = pv_explicit + pv_terminal
            equity_value = enterprise_value - net_debt
            value_per_share = equity_value / shares_outstanding

            rows.append(
                {
                    "wacc": wacc,
                    "terminal_growth_rate": growth,
                    "enterprise_value": enterprise_value,
                    "equity_value": equity_value,
                    "value_per_share": value_per_share,
                }
            )

    return pd.DataFrame(rows)


def sensitivity_matrix(
    sensitivity: pd.DataFrame,
    *,
    value_column: str = "value_per_share",
) -> pd.DataFrame:
    matrix = sensitivity.pivot(
        index="wacc",
        columns="terminal_growth_rate",
        values=value_column,
    )
    return matrix.sort_index().sort_index(axis=1)


def forecast_sensitivity(
    base_forecast: pd.DataFrame,
    *,
    base_growth: float,
    base_margin: float,
    wacc: float,
    terminal_growth_rate: float,
    net_debt: float,
    shares_outstanding: float,
    growth_range: tuple[float, ...] | None = None,
    margin_range: tuple[float, ...] | None = None,
) -> pd.DataFrame:
    if growth_range is None:
        growth_range = tuple(round(base_growth + x, 6) for x in (-0.02, -0.01, 0.0, 0.01, 0.02))

    if margin_range is None:
        margin_range = tuple(round(base_margin + x, 6) for x in (-0.02, -0.01, 0.0, 0.01, 0.02))

    rows: list[dict[str, float]] = []

    for growth in growth_range:
        for margin in margin_range:
            forecast = base_forecast.copy()
            revenue = float(forecast["revenue"].iloc[0])
            revenues = []
            for _ in range(len(forecast)):
                revenue *= 1.0 + growth
                revenues.append(revenue)

            forecast["revenue"] = revenues
            forecast["ebit"] = forecast["revenue"] * margin

            if "depreciation_amortization" in forecast.columns:
                da = forecast["depreciation_amortization"].astype(float)
            else:
                da = forecast["revenue"] * 0.05

            if "capital_expenditure" in forecast.columns:
                capex = forecast["capital_expenditure"].astype(float)
            else:
                capex = forecast["revenue"] * 0.05

            forecast["ufcf"] = (
                forecast["ebit"] * (1.0 - 0.21)
                + da
                - capex
            )

            final_ufcf = float(forecast["ufcf"].iloc[-1])
            periods = np.arange(1, len(forecast) + 1, dtype=float)
            pv_explicit = float(
                (
                    forecast["ufcf"].astype(float).to_numpy()
                    / ((1.0 + wacc) ** periods)
                ).sum()
            )
            terminal = calculate_terminal_value(
                final_ufcf,
                wacc=wacc,
                terminal_growth_rate=terminal_growth_rate,
            )
            pv_terminal = terminal / ((1.0 + wacc) ** len(forecast))
            enterprise_value = pv_explicit + pv_terminal
            equity_value = enterprise_value - net_debt

            rows.append(
                {
                    "revenue_growth": growth,
                    "ebit_margin": margin,
                    "enterprise_value": enterprise_value,
                    "equity_value": equity_value,
                    "value_per_share": equity_value / shares_outstanding,
                }
            )

    return pd.DataFrame(rows)


def forecast_sensitivity_matrix(
    sensitivity: pd.DataFrame,
    *,
    value_column: str = "value_per_share",
) -> pd.DataFrame:
    return sensitivity.pivot(
        index="revenue_growth",
        columns="ebit_margin",
        values=value_column,
    ).sort_index().sort_index(axis=1)
