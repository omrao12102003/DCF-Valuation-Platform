from datetime import date

import pytest

from app.models.financials import (
    BalanceSheet,
    CashFlowStatement,
    CompanyFinancials,
    FinancialPeriod,
    IncomeStatement,
)


def build_period(is_forecast: bool = False) -> FinancialPeriod:
    income_statement = IncomeStatement(
        revenue=1000,
        cost_of_revenue=400,
        operating_expenses=250,
        depreciation_amortization=50,
        interest_expense=20,
        taxes=56,
        net_income=224,
    )

    balance_sheet = BalanceSheet(
        cash_and_equivalents=200,
        accounts_receivable=150,
        inventory=100,
        other_current_assets=50,
        property_plant_equipment=500,
        goodwill=100,
        intangible_assets=50,
        other_non_current_assets=50,
        accounts_payable=100,
        accrued_liabilities=50,
        short_term_debt=100,
        long_term_debt=300,
        other_non_current_liabilities=100,
        total_equity=450,
    )

    cash_flow_statement = CashFlowStatement(
        net_income=224,
        depreciation_amortization=50,
        change_in_working_capital=20,
        capital_expenditure=100,
    )

    return FinancialPeriod(
        fiscal_year=2025,
        period_type="FY",
        period_end=date(2025, 12, 31),
        currency="USD",
        is_forecast=is_forecast,
        income_statement=income_statement,
        balance_sheet=balance_sheet,
        cash_flow_statement=cash_flow_statement,
        source="test",
    )


def test_income_statement_profitability_metrics():
    period = build_period()

    assert period.income_statement.gross_profit == 600
    assert period.income_statement.ebitda == 350
    assert period.income_statement.ebit == 300
    assert period.income_statement.ebt == 280


def test_balance_sheet_equation():
    period = build_period()

    assert period.balance_sheet.total_assets == 1200
    assert period.balance_sheet.total_liabilities == 650
    assert period.balance_sheet.balance_check == 100


def test_cash_flow_free_cash_flow():
    period = build_period()

    assert period.cash_flow_statement.operating_cash_flow == 254
    assert period.cash_flow_statement.free_cash_flow == 154


def test_historical_and_forecast_periods_are_separated():
    historical = build_period(False)
    forecast = build_period(True)

    financials = CompanyFinancials(
        company_id="MSFT",
        company_name="Microsoft Corporation",
        reporting_currency="USD",
        periods=[historical, forecast],
    )

    assert len(financials.historical_periods()) == 1
    assert len(financials.forecast_periods()) == 1
    assert financials.latest_historical_period().is_forecast is False


def test_currency_is_normalized():
    period = build_period()

    period = period.model_copy(update={"currency": "gbp"})

    assert period.currency == "GBP"


def test_invalid_revenue_is_rejected():
    with pytest.raises(ValueError):
        IncomeStatement(
            revenue=-100,
            cost_of_revenue=400,
            operating_expenses=250,
            depreciation_amortization=50,
            interest_expense=20,
            taxes=56,
            net_income=224,
        )
