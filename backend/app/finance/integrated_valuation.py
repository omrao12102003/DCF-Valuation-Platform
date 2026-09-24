from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.finance.comparables import ComparableCompany, comparable_valuation_table
from app.finance.roic import ROICResult, roic_summary


@dataclass(frozen=True)
class IntegratedValuation:
    ticker: str
    dcf_value_per_share: float
    comparable_value_per_share: float
    roic: ROICResult
    valuation_summary: pd.DataFrame


def build_integrated_valuation(
    *,
    ticker: str,
    dcf_value_per_share: float,
    target: ComparableCompany,
    peers: list[ComparableCompany],
    historical: pd.DataFrame,
    tax_rate: float,
    wacc: float,
) -> IntegratedValuation:
    comparable = comparable_valuation_table(target, peers)

    comparable_value = float(
        comparable["implied_value_per_share"].median()
    )

    roic = roic_summary(
        historical,
        tax_rate=tax_rate,
        wacc=wacc,
    )

    summary = pd.DataFrame(
        {
            "Method": [
                "DCF",
                "Trading Comparables",
            ],
            "Value Per Share": [
                dcf_value_per_share,
                comparable_value,
            ],
        }
    )

    return IntegratedValuation(
        ticker=ticker,
        dcf_value_per_share=dcf_value_per_share,
        comparable_value_per_share=comparable_value,
        roic=roic,
        valuation_summary=summary,
    )


def integrated_valuation_table(
    result: IntegratedValuation,
) -> pd.DataFrame:
    return result.valuation_summary.copy()
