from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


PeriodType = Literal["FY", "Q1", "Q2", "Q3", "Q4", "TTM"]


class IncomeStatement(BaseModel):
    """
    Normalized income statement.

    Monetary values are stored internally in millions of the reporting
    currency. Expenses are represented as positive values and are subtracted
    when calculating profitability.
    """

    revenue: float = Field(ge=0)
    cost_of_revenue: float = Field(ge=0)
    operating_expenses: float = Field(ge=0)
    depreciation_amortization: float = Field(ge=0)
    interest_expense: float = Field(ge=0)
    taxes: float = Field(ge=0)
    net_income: float

    @property
    def gross_profit(self) -> float:
        return self.revenue - self.cost_of_revenue

    @property
    def ebitda(self) -> float:
        return self.gross_profit - self.operating_expenses

    @property
    def ebit(self) -> float:
        return self.ebitda - self.depreciation_amortization

    @property
    def ebt(self) -> float:
        return self.ebit - self.interest_expense


class BalanceSheet(BaseModel):
    """
    Normalized balance sheet.

    Monetary values are stored in millions of the reporting currency.
    """

    cash_and_equivalents: float = Field(ge=0)
    accounts_receivable: float = Field(ge=0)
    inventory: float = Field(ge=0)
    other_current_assets: float = Field(ge=0)

    property_plant_equipment: float = Field(ge=0)
    goodwill: float = Field(ge=0)
    intangible_assets: float = Field(ge=0)
    other_non_current_assets: float = Field(ge=0)

    accounts_payable: float = Field(ge=0)
    accrued_liabilities: float = Field(ge=0)
    short_term_debt: float = Field(ge=0)
    long_term_debt: float = Field(ge=0)
    other_non_current_liabilities: float = Field(ge=0)

    total_equity: float

    @property
    def total_assets(self) -> float:
        return (
            self.cash_and_equivalents
            + self.accounts_receivable
            + self.inventory
            + self.other_current_assets
            + self.property_plant_equipment
            + self.goodwill
            + self.intangible_assets
            + self.other_non_current_assets
        )

    @property
    def total_liabilities(self) -> float:
        return (
            self.accounts_payable
            + self.accrued_liabilities
            + self.short_term_debt
            + self.long_term_debt
            + self.other_non_current_liabilities
        )

    @property
    def balance_check(self) -> float:
        return self.total_assets - (
            self.total_liabilities + self.total_equity
        )

    @property
    def net_debt(self) -> float:
        return (
            self.short_term_debt
            + self.long_term_debt
            - self.cash_and_equivalents
        )


class CashFlowStatement(BaseModel):
    """
    Normalized cash flow statement.

    Monetary values are stored in millions of the reporting currency.
    """

    net_income: float
    depreciation_amortization: float = Field(ge=0)
    change_in_working_capital: float
    capital_expenditure: float = Field(ge=0)

    other_operating_cash_flow: float = 0.0
    investing_cash_flow: float = 0.0
    financing_cash_flow: float = 0.0

    dividends_paid: float = Field(default=0.0, ge=0)
    debt_issued: float = Field(default=0.0, ge=0)
    debt_repaid: float = Field(default=0.0, ge=0)
    shares_issued: float = Field(default=0.0, ge=0)
    shares_repurched: float = Field(default=0.0, ge=0)

    @property
    def operating_cash_flow(self) -> float:
        return (
            self.net_income
            + self.depreciation_amortization
            - self.change_in_working_capital
            + self.other_operating_cash_flow
        )

    @property
    def free_cash_flow(self) -> float:
        return self.operating_cash_flow - self.capital_expenditure

    @property
    def net_financing_cash_flow(self) -> float:
        return (
            self.debt_issued
            - self.debt_repaid
            + self.shares_issued
            - self.shares_repurched
            - self.dividends_paid
        )


class FinancialPeriod(BaseModel):
    """
    A complete financial reporting period.

    This object is the basic unit passed through the financial modelling
    engine. Historical and forecast periods use the same structure so that
    actual results can flow directly into the forecast model.
    """

    fiscal_year: int = Field(ge=1900, le=2100)
    period_type: PeriodType = "FY"
    period_end: date

    currency: str = Field(min_length=3, max_length=3)
    is_forecast: bool = False

    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow_statement: CashFlowStatement

    source: str | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        value = value.upper()

        if not value.isalpha():
            raise ValueError("Currency must contain alphabetic ISO-style code")

        return value


class CompanyFinancials(BaseModel):
    """
    Complete historical and forecast financial dataset for a company.
    """

    company_id: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    reporting_currency: str = Field(min_length=3, max_length=3)

    periods: list[FinancialPeriod] = Field(min_length=1)

    @field_validator("reporting_currency")
    @classmethod
    def validate_reporting_currency(cls, value: str) -> str:
        return value.upper()

    def historical_periods(self) -> list[FinancialPeriod]:
        return [period for period in self.periods if not period.is_forecast]

    def forecast_periods(self) -> list[FinancialPeriod]:
        return [period for period in self.periods if period.is_forecast]

    def latest_historical_period(self) -> FinancialPeriod:
        historical = self.historical_periods()

        if not historical:
            raise ValueError("No historical financial period is available")

        return max(historical, key=lambda period: period.period_end)
