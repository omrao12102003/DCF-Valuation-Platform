from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.finance.forecast import (
    ForecastAssumptions,
    build_forecast_model,
)


@dataclass
class ThreeStatementModel:
    historical: pd.DataFrame
    forecast_income_statement: pd.DataFrame
    forecast_balance_sheet: pd.DataFrame
    forecast_cash_flow: pd.DataFrame

    @property
    def forecast(self) -> pd.DataFrame:
        income = self.forecast_income_statement.copy()
        balance = self.forecast_balance_sheet.copy()
        cash_flow = self.forecast_cash_flow.copy()

        result = income.merge(
            balance,
            on="fiscal_year",
            how="inner",
            suffixes=("", "_bs"),
        )

        result = result.merge(
            cash_flow,
            on="fiscal_year",
            how="inner",
            suffixes=("", "_cf"),
        )

        if "total_equity" in result.columns:
            result["shareholders_equity"] = result["total_equity"]

        asset_columns = [c for c in ["cash_and_equivalents", "accounts_receivable", "inventory", "other_current_assets", "property_plant_equipment", "goodwill", "intangible_assets", "other_non_current_assets"] if c in result.columns]
        liability_columns = [c for c in ["accounts_payable", "accrued_liabilities", "short_term_debt", "long_term_debt", "other_current_liabilities", "other_non_current_liabilities"] if c in result.columns]

        result["total_assets"] = result[asset_columns].sum(axis=1)
        result["total_liabilities"] = result[liability_columns].sum(axis=1)
        result["balance_check"] = result["total_assets"] - result["total_liabilities"] - result["shareholders_equity"]

        return result

    def validate(self, tolerance: float = 1e-6) -> None:
        if self.forecast_income_statement.empty:
            raise ValueError("Forecast income statement is empty.")

        if self.forecast_balance_sheet.empty:
            raise ValueError("Forecast balance sheet is empty.")

        if self.forecast_cash_flow.empty:
            raise ValueError("Forecast cash flow is empty.")

        years = set(self.forecast_income_statement["fiscal_year"])
        bs_years = set(self.forecast_balance_sheet["fiscal_year"])
        cf_years = set(self.forecast_cash_flow["fiscal_year"])

        if years != bs_years or years != cf_years:
            raise ValueError("Forecast periods are inconsistent across statements.")

        max_balance_error = self.forecast_balance_sheet[
            "balance_check"
        ].abs().max()

        if max_balance_error > tolerance:
            raise ValueError(
                f"Balance sheet does not balance. "
                f"Maximum error={max_balance_error}"
            )

        if (self.forecast_income_statement["revenue"] <= 0).any():
            raise ValueError("Forecast revenue must remain positive.")

        if (
            self.forecast_income_statement["gross_profit"]
            > self.forecast_income_statement["revenue"]
        ).any():
            raise ValueError("Gross profit cannot exceed revenue.")

        if (
            self.forecast_cash_flow["capital_expenditure"] < 0
        ).any():
            raise ValueError("Capital expenditure must be non-negative.")

    def historical_plus_forecast(self) -> pd.DataFrame:
        historical_columns = [
            "fiscal_year",
            "revenue",
            "cost_of_revenue",
            "operating_expenses",
            "depreciation_amortization",
            "interest_expense",
            "taxes",
            "net_income",
            "operating_cash_flow",
            "capital_expenditure",
        ]

        available = [
            column
            for column in historical_columns
            if column in self.historical.columns
        ]

        historical = self.historical[available].copy()
        historical["period_type"] = "historical"

        forecast = self.forecast.copy()
        forecast["period_type"] = "forecast"

        common = list(set(historical.columns).intersection(forecast.columns))

        return pd.concat(
            [
                historical[common],
                forecast[common],
            ],
            ignore_index=True,
        ).sort_values("fiscal_year").reset_index(drop=True)


def build_three_statement_model(
    historical: pd.DataFrame,
    assumptions: ForecastAssumptions | None = None,
) -> ThreeStatementModel:
    model = build_forecast_model(
        historical=historical,
        assumptions=assumptions,
    )

    result = ThreeStatementModel(
        historical=historical.copy(),
        forecast_income_statement=model["income_statement"],
        forecast_balance_sheet=model["balance_sheet"],
        forecast_cash_flow=model["cash_flow"],
    )

    result.validate()

    return result
