import pandas as pd
import pytest

from app.finance.dcf import (
    DCFInputs,
    calculate_dcf,
)
from app.finance.ufcf import (
    calculate_terminal_value,
    calculate_ufcf,
)
from app.finance.wacc import (
    WACCInputs,
    calculate_cost_of_equity,
    calculate_wacc,
)
from app.finance.three_statement import (
    build_three_statement_model,
)
from app.finance.valuation import build_valuation


def test_cost_of_equity():
    assert calculate_cost_of_equity(
        0.04,
        0.05,
        1.2,
    ) == pytest.approx(0.10)


def test_wacc_components():
    result = calculate_wacc(
        WACCInputs(
            risk_free_rate=0.04,
            equity_risk_premium=0.05,
            beta=1.2,
            pre_tax_cost_of_debt=0.05,
            tax_rate=0.25,
            market_value_equity=800.0,
            market_value_debt=200.0,
        )
    )

    assert result.cost_of_equity == pytest.approx(0.10)
    assert result.after_tax_cost_of_debt == pytest.approx(0.0375)
    assert result.equity_weight == pytest.approx(0.80)
    assert result.debt_weight == pytest.approx(0.20)
    assert result.wacc == pytest.approx(0.0875)


def test_ufcf_uses_historical_opening_nwc():
    historical = pd.DataFrame(
        {
            "accounts_receivable": [100.0],
            "inventory": [50.0],
            "other_current_assets": [20.0],
            "accounts_payable": [60.0],
            "accrued_liabilities": [30.0],
        }
    )

    forecast = pd.DataFrame(
        {
            "fiscal_year": [2026],
            "revenue": [1000.0],
            "ebit": [200.0],
            "depreciation_amortization": [50.0],
            "capital_expenditure": [60.0],
            "accounts_receivable": [110.0],
            "inventory": [55.0],
            "other_current_assets": [22.0],
            "accounts_payable": [65.0],
            "accrued_liabilities": [33.0],
        }
    )

    result = calculate_ufcf(
        forecast,
        tax_rate=0.25,
        historical=historical,
    )

    opening_nwc = 100 + 50 + 20 - 60 - 30
    forecast_nwc = 110 + 55 + 22 - 65 - 33

    assert result.loc[0, "change_in_nwc"] == pytest.approx(
        forecast_nwc - opening_nwc
    )

    expected = (
        200 * 0.75
        + 50
        - 60
        - (forecast_nwc - opening_nwc)
    )

    assert result.loc[0, "ufcf"] == pytest.approx(expected)


def test_terminal_value():
    expected = (
        150.0 * 1.03
        / (0.10 - 0.03)
    )

    assert calculate_terminal_value(
        150.0,
        0.10,
        0.03,
    ) == pytest.approx(expected)


def test_terminal_value_rejects_wacc_not_above_growth():
    with pytest.raises(ValueError):
        calculate_terminal_value(
            150.0,
            0.05,
            0.05,
        )


def test_dcf_bridge():
    forecast = pd.DataFrame(
        {
            "ufcf": [
                100.0,
                110.0,
                120.0,
            ]
        }
    )

    result = calculate_dcf(
        forecast,
        DCFInputs(
            wacc=0.10,
            terminal_growth_rate=0.03,
            net_debt=100.0,
            shares_outstanding=50.0,
        ),
    )

    pv_explicit = (
        100 / 1.10
        + 110 / 1.10**2
        + 120 / 1.10**3
    )

    terminal = (
        120 * 1.03
        / (0.10 - 0.03)
    )

    pv_terminal = terminal / 1.10**3
    enterprise_value = (
        pv_explicit + pv_terminal
    )
    equity_value = enterprise_value - 100

    assert result.pv_explicit_forecast == pytest.approx(
        pv_explicit
    )
    assert result.terminal_value == pytest.approx(
        terminal
    )
    assert result.pv_terminal_value == pytest.approx(
        pv_terminal
    )
    assert result.enterprise_value == pytest.approx(
        enterprise_value
    )
    assert result.equity_value == pytest.approx(
        equity_value
    )
    assert result.value_per_share == pytest.approx(
        equity_value / 50
    )


def test_dcf_rejects_invalid_wacc_growth():
    with pytest.raises(ValueError):
        calculate_dcf(
            pd.DataFrame({"ufcf": [100.0]}),
            DCFInputs(
                wacc=0.05,
                terminal_growth_rate=0.05,
                net_debt=0.0,
                shares_outstanding=10.0,
            ),
        )


def test_full_valuation_pipeline():
    from app.data.ingestion import ingest_ticker
    historical = ingest_ticker("MSFT")
    model = build_three_statement_model(historical)

    result = build_valuation(
        ticker="MSFT",
        forecast=model.forecast,
        historical=historical,
        wacc_inputs=WACCInputs(
            risk_free_rate=0.04,
            equity_risk_premium=0.05,
            beta=1.10,
            pre_tax_cost_of_debt=0.05,
            tax_rate=0.21,
            market_value_equity=2_800_000.0,
            market_value_debt=64_000.0,
        ),
        terminal_growth_rate=0.03,
        shares_outstanding=7_400.0,
    )

    assert len(result.ufcf) == 5
    assert result.dcf.enterprise_value > 0
    assert result.dcf.equity_value > 0
    assert result.dcf.value_per_share > 0
    assert 0 < result.wacc.wacc < 1
    assert result.dcf.terminal_value_pct_of_ev > 0
