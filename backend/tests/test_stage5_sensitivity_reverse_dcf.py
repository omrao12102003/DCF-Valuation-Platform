import numpy as np
import pandas as pd
import pytest

from app.data.ingestion import ingest_ticker
from app.finance.company_forecast import build_company_forecast
from app.finance.reverse_dcf import implied_terminal_growth, reverse_dcf_table
from app.finance.sensitivity import (
    dcf_sensitivity,
    forecast_sensitivity,
    forecast_sensitivity_matrix,
    sensitivity_matrix,
)


@pytest.fixture
def historical():
    return ingest_ticker("MSFT")


@pytest.fixture
def forecast():
    return build_company_forecast("MSFT").forecast

@pytest.fixture
def ufcf(forecast):
    from app.finance.ufcf import calculate_ufcf

    return calculate_ufcf(
        forecast,
        tax_rate=0.21,
        historical=None,
    )


def test_dcf_sensitivity_shape(ufcf):
    result = dcf_sensitivity(
        ufcf,
        net_debt=-30444.0,
        shares_outstanding=7400.0,
        base_wacc=0.09,
        base_terminal_growth=0.03,
    )
    assert len(result) == 25
    assert set(result.columns) == {
        "wacc",
        "terminal_growth_rate",
        "enterprise_value",
        "equity_value",
        "value_per_share",
    }


def test_sensitivity_matrix_shape_and_values(ufcf):
    result = dcf_sensitivity(
        ufcf,
        net_debt=-30444.0,
        shares_outstanding=7400.0,
        base_wacc=0.09,
        base_terminal_growth=0.03,
    )
    matrix = sensitivity_matrix(result)
    assert matrix.shape == (5, 5)
    assert np.isfinite(matrix.to_numpy()).all()


def test_dcf_value_decreases_as_wacc_increases(ufcf):
    result = dcf_sensitivity(
        ufcf,
        net_debt=-30444.0,
        shares_outstanding=7400.0,
        base_wacc=0.09,
        base_terminal_growth=0.03,
    )
    matrix = sensitivity_matrix(result)
    for growth in matrix.columns:
        values = matrix[growth].to_numpy()
        assert np.all(np.diff(values) < 0)


def test_dcf_value_increases_as_terminal_growth_increases(ufcf):
    result = dcf_sensitivity(
        ufcf,
        net_debt=-30444.0,
        shares_outstanding=7400.0,
        base_wacc=0.09,
        base_terminal_growth=0.03,
    )
    matrix = sensitivity_matrix(result)
    for wacc in matrix.index:
        values = matrix.loc[wacc].to_numpy()
        assert np.all(np.diff(values) > 0)


def test_invalid_growth_wacc_combination(ufcf):
    with pytest.raises(ValueError):
        dcf_sensitivity(
            ufcf,
            net_debt=-30444.0,
            shares_outstanding=7400.0,
            base_wacc=0.08,
            base_terminal_growth=0.08,
        )


def test_forecast_sensitivity_shape(forecast):
    result = forecast_sensitivity(
        forecast,
        base_growth=0.08,
        base_margin=0.35,
        wacc=0.09,
        terminal_growth_rate=0.03,
        net_debt=-30444.0,
        shares_outstanding=7400.0,
    )
    assert len(result) == 25
    assert np.isfinite(result["value_per_share"]).all()


def test_forecast_sensitivity_matrix(forecast):
    result = forecast_sensitivity(
        forecast,
        base_growth=0.08,
        base_margin=0.35,
        wacc=0.09,
        terminal_growth_rate=0.03,
        net_debt=-30444.0,
        shares_outstanding=7400.0,
    )
    matrix = forecast_sensitivity_matrix(result)
    assert matrix.shape == (5, 5)


def test_reverse_dcf_recovers_known_growth(ufcf):
    wacc = 0.09
    known_growth = 0.03
    net_debt = -30444.0
    shares = 7400.0

    from app.finance.reverse_dcf import _enterprise_value_for_growth

    enterprise_value = _enterprise_value_for_growth(
        ufcf,
        wacc=wacc,
        terminal_growth_rate=known_growth,
    )
    target_equity = enterprise_value - net_debt
    target_price = target_equity / shares

    result = implied_terminal_growth(
        ufcf,
        target_share_price=target_price,
        shares_outstanding=shares,
        net_debt=net_debt,
        wacc=wacc,
    )

    assert result.implied_terminal_growth == pytest.approx(known_growth, abs=1e-8)


def test_reverse_dcf_table(ufcf):
    from app.finance.reverse_dcf import _enterprise_value_for_growth

    wacc = 0.09
    shares = 7400.0
    net_debt = -30444.0
    enterprise_value = _enterprise_value_for_growth(
        ufcf,
        wacc=wacc,
        terminal_growth_rate=0.03,
    )
    target_price = (enterprise_value - net_debt) / shares

    result = implied_terminal_growth(
        ufcf,
        target_share_price=target_price,
        shares_outstanding=shares,
        net_debt=net_debt,
        wacc=wacc,
        lower_bound=0.0,
        upper_bound=0.08,
    )

    table = reverse_dcf_table(result)
    assert list(table.columns) == ["Metric", "Value"]
    assert "Implied terminal growth" in set(table["Metric"])
    assert result.implied_terminal_growth == pytest.approx(0.03, abs=1e-8)


def test_reverse_dcf_invalid_bounds(ufcf):
    with pytest.raises(ValueError):
        implied_terminal_growth(
            ufcf,
            target_share_price=100.0,
            shares_outstanding=7400.0,
            net_debt=-30444.0,
            wacc=0.09,
            lower_bound=0.09,
            upper_bound=0.10,
        )
