from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.finance.ufcf import (
    calculate_terminal_value,
    calculate_ufcf,
)


@dataclass(frozen=True)
class DCFInputs:
    wacc: float
    terminal_growth_rate: float
    net_debt: float
    shares_outstanding: float

    def validate(self) -> None:
        if self.wacc <= 0:
            raise ValueError("wacc must be positive.")

        if self.terminal_growth_rate < 0:
            raise ValueError(
                "terminal_growth_rate cannot be negative."
            )

        if self.wacc <= self.terminal_growth_rate:
            raise ValueError(
                "wacc must be greater than terminal growth rate."
            )

        if self.shares_outstanding <= 0:
            raise ValueError(
                "shares_outstanding must be greater than zero."
            )


@dataclass(frozen=True)
class DCFResult:
    enterprise_value: float
    net_debt: float
    equity_value: float
    shares_outstanding: float
    value_per_share: float
    pv_explicit_forecast: float
    terminal_value: float
    pv_terminal_value: float
    terminal_value_pct_of_ev: float


def calculate_dcf(
    ufcf_forecast: pd.DataFrame,
    inputs: DCFInputs,
) -> DCFResult:
    inputs.validate()

    if "ufcf" not in ufcf_forecast.columns:
        raise ValueError(
            "Forecast must contain a 'ufcf' column."
        )

    if ufcf_forecast.empty:
        raise ValueError("UFCF forecast cannot be empty.")

    ufcf = (
        ufcf_forecast["ufcf"]
        .astype(float)
        .tolist()
    )

    discount_factors = [
        1.0 / ((1.0 + inputs.wacc) ** period)
        for period in range(1, len(ufcf) + 1)
    ]

    pv_explicit = sum(
        cash_flow * discount_factor
        for cash_flow, discount_factor
        in zip(ufcf, discount_factors)
    )

    terminal_value = calculate_terminal_value(
        final_ufcf=ufcf[-1],
        wacc=inputs.wacc,
        terminal_growth_rate=inputs.terminal_growth_rate,
    )

    pv_terminal = (
        terminal_value
        * discount_factors[-1]
    )

    enterprise_value = (
        pv_explicit + pv_terminal
    )

    equity_value = (
        enterprise_value - inputs.net_debt
    )

    value_per_share = (
        equity_value
        / inputs.shares_outstanding
    )

    terminal_share = (
        pv_terminal / enterprise_value
        if enterprise_value != 0
        else 0.0
    )

    return DCFResult(
        enterprise_value=enterprise_value,
        net_debt=inputs.net_debt,
        equity_value=equity_value,
        shares_outstanding=inputs.shares_outstanding,
        value_per_share=value_per_share,
        pv_explicit_forecast=pv_explicit,
        terminal_value=terminal_value,
        pv_terminal_value=pv_terminal,
        terminal_value_pct_of_ev=terminal_share,
    )


def build_dcf(
    forecast: pd.DataFrame,
    tax_rate: float,
    wacc: float,
    terminal_growth_rate: float,
    net_debt: float,
    shares_outstanding: float,
    historical: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, DCFResult]:
    ufcf = calculate_ufcf(
        forecast=forecast,
        tax_rate=tax_rate,
        historical=historical,
    )

    result = calculate_dcf(
        ufcf_forecast=ufcf,
        inputs=DCFInputs(
            wacc=wacc,
            terminal_growth_rate=terminal_growth_rate,
            net_debt=net_debt,
            shares_outstanding=shares_outstanding,
        ),
    )

    return ufcf, result
