import math

import pandas as pd
import pytest

from app.data.ingestion import ingest_ticker
from app.finance.forecast import (
    ForecastAssumptions,
    build_forecast_model,
    forecast_income_statement,
)
from app.finance.three_statement import build_three_statement_model


COMPANIES = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]


@pytest.fixture
def historical():
    return ingest_ticker("MSFT")


def test_default_assumptions_are_valid(historical):
    assumptions = ForecastAssumptions.from_historical(historical)
    assumptions.validate()


def test_forecast_produces_five_years(historical):
    model = build_forecast_model(historical)

    assert len(model["income_statement"]) == 5
    assert len(model["balance_sheet"]) == 5
    assert len(model["cash_flow"]) == 5


def test_forecast_years_follow_historical_period(historical):
    model = build_forecast_model(historical)

    expected = [2026, 2027, 2028, 2029, 2030]

    assert model["income_statement"]["fiscal_year"].tolist() == expected
    assert model["balance_sheet"]["fiscal_year"].tolist() == expected
    assert model["cash_flow"]["fiscal_year"].tolist() == expected


def test_revenue_growth_is_applied(historical):
    assumptions = ForecastAssumptions(revenue_growth=0.10)

    result = forecast_income_statement(
        historical,
        assumptions,
    )

    first_revenue = float(historical.iloc[-1]["revenue"]) * 1.10

    assert math.isclose(
        float(result.iloc[0]["revenue"]),
        first_revenue,
        rel_tol=1e-9,
    )


def test_income_statement_math(historical):
    model = build_forecast_model(historical)
    income = model["income_statement"]

    assert (
        income["gross_profit"].round(8)
        == (
            income["revenue"] - income["cost_of_revenue"]
        ).round(8)
    ).all()

    assert (
        income["ebitda"].round(8)
        == (
            income["gross_profit"] - income["operating_expenses"]
        ).round(8)
    ).all()

    assert (
        income["ebit"].round(8)
        == (
            income["ebitda"] - income["depreciation_amortization"]
        ).round(8)
    ).all()

    assert (
        income["ebt"].round(8)
        == (
            income["ebit"] - income["interest_expense"]
        ).round(8)
    ).all()


def test_balance_sheet_balances(historical):
    model = build_forecast_model(historical)

    balance_sheet = model["balance_sheet"]

    assert balance_sheet["balance_check"].abs().max() < 1e-6


def test_cash_flow_math(historical):
    model = build_forecast_model(historical)
    cash_flow = model["cash_flow"]

    assert (
        cash_flow["free_cash_flow"].round(8)
        == (
            cash_flow["operating_cash_flow"]
            + cash_flow["investing_cash_flow"]
        ).round(8)
    ).all()


def test_three_statements_have_same_periods(historical):
    model = build_three_statement_model(historical)

    assert (
        model.forecast_income_statement["fiscal_year"].tolist()
        == model.forecast_balance_sheet["fiscal_year"].tolist()
        == model.forecast_cash_flow["fiscal_year"].tolist()
    )


def test_three_statement_validation_passes(historical):
    model = build_three_statement_model(historical)
    model.validate()


def test_integrated_forecast_contains_core_financial_metrics(historical):
    model = build_three_statement_model(historical)

    forecast = model.forecast

    required = {
        "fiscal_year",
        "revenue",
        "ebitda",
        "ebit",
        "net_income",
        "free_cash_flow",
        "total_assets",
        "total_liabilities",
        "shareholders_equity",
        "balance_check",
    }

    assert required.issubset(forecast.columns)


@pytest.mark.parametrize("ticker", COMPANIES)
def test_all_companies_forecast_successfully(ticker):
    historical = ingest_ticker(ticker)

    model = build_three_statement_model(historical)

    assert len(model.forecast_income_statement) == 5
    assert len(model.forecast_balance_sheet) == 5
    assert len(model.forecast_cash_flow) == 5

    assert (
        model.forecast_balance_sheet["balance_check"].abs().max()
        < 1e-6
    )

    assert (model.forecast_income_statement["revenue"] > 0).all()
    assert (model.forecast_income_statement["ebitda"].notna()).all()
    assert (model.forecast_cash_flow["free_cash_flow"].notna()).all()


def test_custom_forecast_horizon(historical):
    assumptions = ForecastAssumptions(
        forecast_years=10,
        revenue_growth=0.06,
    )

    model = build_three_statement_model(
        historical,
        assumptions,
    )

    assert len(model.forecast_income_statement) == 10
    assert len(model.forecast_balance_sheet) == 10
    assert len(model.forecast_cash_flow) == 10


def test_custom_assumptions_change_forecast(historical):
    base = build_three_statement_model(
        historical,
        ForecastAssumptions(revenue_growth=0.05),
    )

    high_growth = build_three_statement_model(
        historical,
        ForecastAssumptions(revenue_growth=0.15),
    )

    base_revenue = float(
        base.forecast_income_statement.iloc[-1]["revenue"]
    )

    high_revenue = float(
        high_growth.forecast_income_statement.iloc[-1]["revenue"]
    )

    assert high_revenue > base_revenue


def test_invalid_assumptions_are_rejected():
    with pytest.raises(ValueError):
        ForecastAssumptions(tax_rate=1.2).validate()

    with pytest.raises(ValueError):
        ForecastAssumptions(dso=-1).validate()

    with pytest.raises(ValueError):
        ForecastAssumptions(forecast_years=0).validate()
