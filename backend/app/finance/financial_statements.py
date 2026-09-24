from __future__ import annotations

import pandas as pd


def calculate_statement_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate core historical financial statement metrics.

    The input contains normalized reported financial data.
    The output adds profitability, leverage and cash-flow metrics.
    """

    result = frame.copy()

    result["gross_profit"] = (
        result["revenue"] - result["cost_of_revenue"]
    )

    result["ebitda"] = (
        result["gross_profit"] - result["operating_expenses"]
    )

    result["ebit"] = (
        result["ebitda"] - result["depreciation_amortization"]
    )

    result["ebt"] = (
        result["ebit"] - result["interest_expense"]
    )

    result["calculated_tax_rate"] = (
        result["taxes"] / result["ebt"].replace(0, pd.NA)
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

    return result
