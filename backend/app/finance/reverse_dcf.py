from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.finance.ufcf import calculate_terminal_value


@dataclass(frozen=True)
class ReverseDCFResult:
    target_share_price: float
    shares_outstanding: float
    target_equity_value: float
    target_enterprise_value: float
    net_debt: float
    implied_terminal_growth: float
    wacc: float
    final_ufcf: float
    forecast_years: int


def _enterprise_value_for_growth(
    ufcf: pd.DataFrame,
    *,
    wacc: float,
    terminal_growth_rate: float,
) -> float:
    if terminal_growth_rate >= wacc:
        raise ValueError("Terminal growth must be below WACC.")

    periods = np.arange(1, len(ufcf) + 1, dtype=float)
    values = ufcf["ufcf"].astype(float).to_numpy()
    pv_explicit = float((values / ((1.0 + wacc) ** periods)).sum())

    terminal_value = calculate_terminal_value(
        float(values[-1]),
        wacc=wacc,
        terminal_growth_rate=terminal_growth_rate,
    )
    pv_terminal = terminal_value / ((1.0 + wacc) ** len(ufcf))
    return pv_explicit + pv_terminal


def implied_terminal_growth(
    ufcf: pd.DataFrame,
    *,
    target_share_price: float,
    shares_outstanding: float,
    net_debt: float,
    wacc: float,
    lower_bound: float = 0.0,
    upper_bound: float | None = None,
    tolerance: float = 1e-10,
    max_iterations: int = 200,
) -> ReverseDCFResult:
    if upper_bound is None:
        upper_bound = wacc - 0.0001

    if not lower_bound < upper_bound < wacc:
        raise ValueError("Growth bounds must satisfy lower < upper < WACC.")

    target_equity_value = target_share_price * shares_outstanding
    target_enterprise_value = target_equity_value + net_debt

    low = lower_bound
    high = upper_bound

    low_value = _enterprise_value_for_growth(
        ufcf, wacc=wacc, terminal_growth_rate=low
    )
    high_value = _enterprise_value_for_growth(
        ufcf, wacc=wacc, terminal_growth_rate=high
    )

    if not (low_value <= target_enterprise_value <= high_value):
        raise ValueError(
            "Target valuation is outside the supplied terminal-growth bounds."
        )

    for _ in range(max_iterations):
        mid = (low + high) / 2.0
        mid_value = _enterprise_value_for_growth(
            ufcf, wacc=wacc, terminal_growth_rate=mid
        )

        if abs(mid_value - target_enterprise_value) <= tolerance:
            low = high = mid
            break

        if mid_value < target_enterprise_value:
            low = mid
        else:
            high = mid

    growth = (low + high) / 2.0

    return ReverseDCFResult(
        target_share_price=target_share_price,
        shares_outstanding=shares_outstanding,
        target_equity_value=target_equity_value,
        target_enterprise_value=target_enterprise_value,
        net_debt=net_debt,
        implied_terminal_growth=growth,
        wacc=wacc,
        final_ufcf=float(ufcf["ufcf"].iloc[-1]),
        forecast_years=len(ufcf),
    )


def reverse_dcf_table(result: ReverseDCFResult) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Metric": [
                "Target share price",
                "Shares outstanding",
                "Target equity value",
                "Net debt",
                "Target enterprise value",
                "WACC",
                "Implied terminal growth",
                "Final forecast UFCF",
                "Forecast years",
            ],
            "Value": [
                result.target_share_price,
                result.shares_outstanding,
                result.target_equity_value,
                result.net_debt,
                result.target_enterprise_value,
                result.wacc,
                result.implied_terminal_growth,
                result.final_ufcf,
                result.forecast_years,
            ],
        }
    )
