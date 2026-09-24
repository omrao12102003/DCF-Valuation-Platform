from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class ForecastAssumptions:
    forecast_years: int = 5

    revenue_growth: float = 0.08
    gross_margin: float | None = None
    operating_expense_pct_revenue: float | None = None
    depreciation_pct_revenue: float = 0.035
    interest_pct_debt: float = 0.045
    tax_rate: float = 0.21

    dso: float = 45.0
    dio: float = 35.0
    dpo: float = 40.0

    capex_pct_revenue: float = 0.06
    other_current_assets_pct_revenue: float = 0.025
    other_current_liabilities_pct_revenue: float = 0.04

    debt_repayment_pct: float = 0.0
    minimum_cash: float = 0.0

    @classmethod
    def from_historical(cls, historical: pd.DataFrame) -> "ForecastAssumptions":
        if historical.empty:
            raise ValueError("Historical financial data cannot be empty.")

        latest = historical.iloc[-1]

        revenue = float(latest["revenue"])
        if revenue <= 0:
            raise ValueError("Latest revenue must be positive.")

        gross_margin = (
            float(latest["gross_profit"]) / revenue
            if "gross_profit" in latest
            else None
        )

        operating_expenses = float(latest["operating_expenses"])
        opex_pct = operating_expenses / revenue

        return cls(
            revenue_growth=(
                float(latest["revenue_growth"])
                if "revenue_growth" in latest
                and pd.notna(latest["revenue_growth"])
                else 0.08
            ),
            gross_margin=gross_margin,
            operating_expense_pct_revenue=opex_pct,
        )

    def validate(self) -> None:
        if self.forecast_years < 1:
            raise ValueError("forecast_years must be at least 1.")

        bounded_rates = {
            "tax_rate": self.tax_rate,
            "revenue_growth": self.revenue_growth,
            "depreciation_pct_revenue": self.depreciation_pct_revenue,
            "interest_pct_debt": self.interest_pct_debt,
            "capex_pct_revenue": self.capex_pct_revenue,
            "other_current_assets_pct_revenue": self.other_current_assets_pct_revenue,
            "other_current_liabilities_pct_revenue": self.other_current_liabilities_pct_revenue,
            "debt_repayment_pct": self.debt_repayment_pct,
        }

        for name, value in bounded_rates.items():
            if value < -1:
                raise ValueError(f"{name} is unrealistically below -100%.")

        if self.tax_rate >= 1:
            raise ValueError("tax_rate must be below 100%.")

        for name in ("dso", "dio", "dpo"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} cannot be negative.")

        if self.gross_margin is not None and not 0 < self.gross_margin <= 1:
            raise ValueError("gross_margin must be between 0 and 1.")

        if (
            self.operating_expense_pct_revenue is not None
            and self.operating_expense_pct_revenue < 0
        ):
            raise ValueError("operating_expense_pct_revenue cannot be negative.")


def _require_columns(frame: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required historical columns: {missing}")


def _latest_value(frame: pd.DataFrame, column: str, default: float = 0.0) -> float:
    if column not in frame.columns:
        return default
    value = frame.iloc[-1][column]
    if pd.isna(value):
        return default
    return float(value)


def forecast_income_statement(
    historical: pd.DataFrame,
    assumptions: ForecastAssumptions,
) -> pd.DataFrame:
    _require_columns(
        historical,
        [
            "fiscal_year",
            "revenue",
            "cost_of_revenue",
            "operating_expenses",
            "depreciation_amortization",
            "interest_expense",
            "taxes",
        ],
    )

    assumptions.validate()

    latest = historical.iloc[-1]

    revenue = float(latest["revenue"])

    gross_margin = assumptions.gross_margin
    if gross_margin is None:
        gross_margin = (
            float(latest["gross_profit"]) / revenue
            if "gross_profit" in latest
            else (revenue - float(latest["cost_of_revenue"])) / revenue
        )

    opex_ratio = assumptions.operating_expense_pct_revenue
    if opex_ratio is None:
        opex_ratio = float(latest["operating_expenses"]) / revenue

    debt = (
        _latest_value(historical, "short_term_debt", 0.0)
        + _latest_value(historical, "long_term_debt", 0.0)
    )

    rows: list[dict] = []

    for year_index in range(1, assumptions.forecast_years + 1):
        fiscal_year = int(latest["fiscal_year"]) + year_index

        revenue *= 1.0 + assumptions.revenue_growth
        gross_profit = revenue * gross_margin
        cost_of_revenue = revenue - gross_profit

        operating_expenses = revenue * opex_ratio
        depreciation = revenue * assumptions.depreciation_pct_revenue

        ebitda = gross_profit - operating_expenses
        ebit = ebitda - depreciation

        interest_expense = max(debt, 0.0) * assumptions.interest_pct_debt
        ebt = ebit - interest_expense

        taxes = max(ebt, 0.0) * assumptions.tax_rate
        net_income = ebt - taxes

        rows.append(
            {
                "fiscal_year": fiscal_year,
                "revenue": revenue,
                "cost_of_revenue": cost_of_revenue,
                "gross_profit": gross_profit,
                "operating_expenses": operating_expenses,
                "depreciation_amortization": depreciation,
                "ebitda": ebitda,
                "ebit": ebit,
                "interest_expense": interest_expense,
                "ebt": ebt,
                "taxes": taxes,
                "net_income": net_income,
                "revenue_growth": assumptions.revenue_growth,
                "gross_margin": gross_profit / revenue,
                "ebitda_margin": ebitda / revenue,
                "ebit_margin": ebit / revenue,
                "net_margin": net_income / revenue,
            }
        )

    return pd.DataFrame(rows)


def _working_capital_from_revenue(
    revenue: float,
    cost_of_revenue: float,
    assumptions: ForecastAssumptions,
) -> tuple[float, float, float, float, float, float]:
    accounts_receivable = revenue * assumptions.dso / 365.0
    inventory = cost_of_revenue * assumptions.dio / 365.0
    accounts_payable = cost_of_revenue * assumptions.dpo / 365.0

    other_current_assets = (
        revenue * assumptions.other_current_assets_pct_revenue
    )
    other_current_liabilities = (
        revenue * assumptions.other_current_liabilities_pct_revenue
    )

    net_working_capital = (
        accounts_receivable
        + inventory
        + other_current_assets
        - accounts_payable
        - other_current_liabilities
    )

    return (
        accounts_receivable,
        inventory,
        accounts_payable,
        other_current_assets,
        other_current_liabilities,
        net_working_capital,
    )


def forecast_balance_sheet(
    historical: pd.DataFrame,
    income_statement: pd.DataFrame,
    assumptions: ForecastAssumptions,
) -> pd.DataFrame:
    _require_columns(
        historical,
        [
            "fiscal_year",
            "cash_and_equivalents",
            "accounts_receivable",
            "inventory",
            "other_current_assets",
            "property_plant_equipment",
            "accounts_payable",
            "accrued_liabilities",
            "short_term_debt",
            "long_term_debt",
            "total_equity",
        ],
    )

    latest = historical.iloc[-1]

    cash = float(latest["cash_and_equivalents"])
    ppe = float(latest["property_plant_equipment"])
    debt = (
        float(latest["short_term_debt"])
        + float(latest["long_term_debt"])
    )
    equity = float(latest["total_equity"])

    rows: list[dict] = []

    for _, forecast in income_statement.iterrows():
        revenue = float(forecast["revenue"])
        cost_of_revenue = float(forecast["cost_of_revenue"])
        depreciation = float(forecast["depreciation_amortization"])
        net_income = float(forecast["net_income"])

        (
            accounts_receivable,
            inventory,
            accounts_payable,
            other_current_assets,
            other_current_liabilities,
            _,
        ) = _working_capital_from_revenue(
            revenue,
            cost_of_revenue,
            assumptions,
        )

        capex = revenue * assumptions.capex_pct_revenue

        ppe = max(0.0, ppe + capex - depreciation)

        debt_repayment = max(0.0, debt * assumptions.debt_repayment_pct)
        debt = max(0.0, debt - debt_repayment)

        equity += net_income

        current_assets_before_cash = (
            accounts_receivable
            + inventory
            + other_current_assets
        )

        current_liabilities = (
            accounts_payable
            + other_current_liabilities
        )

        non_cash_assets = current_assets_before_cash + ppe

        liabilities_before_equity = current_liabilities + debt

        required_cash = max(
            assumptions.minimum_cash,
            liabilities_before_equity + equity - non_cash_assets,
        )

        cash = max(assumptions.minimum_cash, required_cash)

        total_assets = non_cash_assets + cash
        total_liabilities = liabilities_before_equity

        balance_check = total_assets - total_liabilities - equity

        rows.append(
            {
                "fiscal_year": int(forecast["fiscal_year"]),
                "cash_and_equivalents": cash,
                "accounts_receivable": accounts_receivable,
                "inventory": inventory,
                "other_current_assets": other_current_assets,
                "property_plant_equipment": ppe,
                "total_current_assets": (
                    cash
                    + accounts_receivable
                    + inventory
                    + other_current_assets
                ),
                "total_assets": total_assets,
                "accounts_payable": accounts_payable,
                "other_current_liabilities": other_current_liabilities,
                "total_current_liabilities": current_liabilities,
                "total_debt": debt,
                "total_liabilities": total_liabilities,
                "total_equity": equity,
                "balance_check": balance_check,
                "capital_expenditure": capex,
                "debt_repayment": debt_repayment,
            }
        )

    return pd.DataFrame(rows)


def forecast_cash_flow(
    historical: pd.DataFrame,
    income_statement: pd.DataFrame,
    balance_sheet: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(
        historical,
        [
            "fiscal_year",
            "operating_cash_flow",
            "capital_expenditure",
        ],
    )

    previous_bs = historical.iloc[-1]
    previous_nwc = (
        _latest_value(historical, "accounts_receivable")
        + _latest_value(historical, "inventory")
        + _latest_value(historical, "other_current_assets")
        - _latest_value(historical, "accounts_payable")
        - _latest_value(historical, "accrued_liabilities")
    )

    rows: list[dict] = []

    for _, income in income_statement.iterrows():
        year = int(income["fiscal_year"])
        bs = balance_sheet[balance_sheet["fiscal_year"] == year].iloc[0]

        current_nwc = (
            float(bs["accounts_receivable"])
            + float(bs["inventory"])
            + float(bs["other_current_assets"])
            - float(bs["accounts_payable"])
            - float(bs["other_current_liabilities"])
        )

        change_nwc = current_nwc - previous_nwc

        depreciation = float(income["depreciation_amortization"])
        capex = float(bs["capital_expenditure"])
        debt_repayment = float(bs["debt_repayment"])

        operating_cash_flow = (
            float(income["net_income"])
            + depreciation
            - change_nwc
        )

        investing_cash_flow = -capex
        financing_cash_flow = -debt_repayment

        free_cash_flow = operating_cash_flow + investing_cash_flow

        rows.append(
            {
                "fiscal_year": year,
                "net_income": float(income["net_income"]),
                "depreciation_amortization": depreciation,
                "change_in_working_capital": change_nwc,
                "operating_cash_flow": operating_cash_flow,
                "capital_expenditure": capex,
                "investing_cash_flow": investing_cash_flow,
                "debt_repayment": debt_repayment,
                "financing_cash_flow": financing_cash_flow,
                "free_cash_flow": free_cash_flow,
            }
        )

        previous_nwc = current_nwc

    return pd.DataFrame(rows)


def build_forecast_model(
    historical: pd.DataFrame,
    assumptions: ForecastAssumptions | None = None,
) -> dict[str, pd.DataFrame]:
    if historical.empty:
        raise ValueError("Historical financial data cannot be empty.")

    historical = historical.sort_values("fiscal_year").reset_index(drop=True)

    if assumptions is None:
        assumptions = ForecastAssumptions.from_historical(historical)

    assumptions.validate()

    income_statement = forecast_income_statement(
        historical,
        assumptions,
    )

    balance_sheet = forecast_balance_sheet(
        historical,
        income_statement,
        assumptions,
    )

    cash_flow = forecast_cash_flow(
        historical,
        income_statement,
        balance_sheet,
    )

    return {
        "income_statement": income_statement,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow,
    }
