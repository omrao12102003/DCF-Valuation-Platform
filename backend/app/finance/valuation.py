from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.finance.dcf import DCFResult, build_dcf
from app.finance.wacc import WACCInputs, WACCResult, calculate_wacc


@dataclass(frozen=True)
class ValuationResult:
    ticker: str
    tax_rate: float
    terminal_growth_rate: float
    wacc: WACCResult
    dcf: DCFResult
    ufcf: pd.DataFrame

    def summary(self) -> dict[str, float | str]:
        return {
            "ticker": self.ticker,
            "tax_rate": self.tax_rate,
            "wacc": self.wacc.wacc,
            "cost_of_equity": self.wacc.cost_of_equity,
            "after_tax_cost_of_debt": (
                self.wacc.after_tax_cost_of_debt
            ),
            "terminal_growth_rate": (
                self.terminal_growth_rate
            ),
            "enterprise_value": self.dcf.enterprise_value,
            "net_debt": self.dcf.net_debt,
            "equity_value": self.dcf.equity_value,
            "shares_outstanding": (
                self.dcf.shares_outstanding
            ),
            "value_per_share": self.dcf.value_per_share,
            "pv_explicit_forecast": (
                self.dcf.pv_explicit_forecast
            ),
            "terminal_value": self.dcf.terminal_value,
            "pv_terminal_value": (
                self.dcf.pv_terminal_value
            ),
            "terminal_value_pct_of_ev": (
                self.dcf.terminal_value_pct_of_ev
            ),
        }


def build_valuation(
    ticker: str,
    forecast: pd.DataFrame,
    historical: pd.DataFrame,
    wacc_inputs: WACCInputs,
    terminal_growth_rate: float,
    shares_outstanding: float,
) -> ValuationResult:
    wacc_result = calculate_wacc(wacc_inputs)

    ufcf, dcf_result = build_dcf(
        forecast=forecast,
        tax_rate=wacc_inputs.tax_rate,
        wacc=wacc_result.wacc,
        terminal_growth_rate=terminal_growth_rate,
        net_debt=(
            float(historical.iloc[-1]["net_debt"])
            if "net_debt" in historical.columns
            else (
                float(
                    historical.iloc[-1]["short_term_debt"]
                )
                + float(
                    historical.iloc[-1]["long_term_debt"]
                )
                - float(
                    historical.iloc[-1][
                        "cash_and_equivalents"
                    ]
                )
            )
        ),
        shares_outstanding=shares_outstanding,
        historical=historical,
    )

    return ValuationResult(
        ticker=ticker,
        tax_rate=wacc_inputs.tax_rate,
        terminal_growth_rate=terminal_growth_rate,
        wacc=wacc_result,
        dcf=dcf_result,
        ufcf=ufcf,
    )


def valuation_table(result: ValuationResult) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Metric": [
                "Risk-free rate",
                "Equity risk premium",
                "Beta",
                "Pre-tax cost of debt",
                "Tax rate",
                "Cost of equity",
                "After-tax cost of debt",
                "Equity weight",
                "Debt weight",
                "WACC",
                "Terminal growth rate",
                "PV of explicit forecast",
                "PV of terminal value",
                "Terminal value % of EV",
                "Enterprise value",
                "Net debt",
                "Equity value",
                "Shares outstanding",
                "DCF value per share",
            ],
            "Value": [
                result.wacc.cost_of_equity
                - result.wacc.wacc
                + result.wacc.cost_of_equity,
                result.wacc.cost_of_equity
                - (
                    result.wacc.cost_of_equity
                    - result.wacc.cost_of_debt
                    if hasattr(result.wacc, "cost_of_debt")
                    else 0
                ),
                None,
                None,
                result.tax_rate,
                result.wacc.cost_of_equity,
                result.wacc.after_tax_cost_of_debt,
                result.wacc.equity_weight,
                result.wacc.debt_weight,
                result.wacc.wacc,
                result.terminal_growth_rate,
                result.dcf.pv_explicit_forecast,
                result.dcf.pv_terminal_value,
                result.dcf.terminal_value_pct_of_ev,
                result.dcf.enterprise_value,
                result.dcf.net_debt,
                result.dcf.equity_value,
                result.dcf.shares_outstanding,
                result.dcf.value_per_share,
            ],
        }
    )
