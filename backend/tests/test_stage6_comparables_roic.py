import numpy as np
import pytest

from app.data.ingestion import ingest_ticker
from app.finance.comparables import (
    ComparableCompany,
    comparable_metrics,
    comparable_valuation_table,
    peer_multiples,
)
from app.finance.integrated_valuation import (
    build_integrated_valuation,
    integrated_valuation_table,
)
from app.finance.roic import calculate_roic, roic_summary, roic_table


def company(ticker: str, scale: float) -> ComparableCompany:
    return ComparableCompany(
        ticker=ticker,
        revenue=100_000.0 * scale,
        ebitda=45_000.0 * scale,
        ebit=38_000.0 * scale,
        net_income=30_000.0 * scale,
        cash=10_000.0 * scale,
        debt=20_000.0 * scale,
        market_cap=600_000.0 * scale,
        shares_outstanding=10_000.0 * scale,
    )


@pytest.fixture
def historical():
    return ingest_ticker("MSFT")


def test_comparable_company_multiples():
    c = company("TEST", 1.0)

    assert c.enterprise_value == pytest.approx(610_000.0)
    assert c.ev_revenue == pytest.approx(6.1)
    assert c.ev_ebitda == pytest.approx(610_000.0 / 45_000.0)
    assert c.ev_ebit == pytest.approx(610_000.0 / 38_000.0)
    assert c.pe == pytest.approx(20.0)


def test_comparable_metrics():
    result = comparable_metrics(
        [company("A", 1.0), company("B", 1.2)]
    )

    assert len(result) == 2
    assert result["enterprise_value"].notna().all()
    assert result["ev_ebitda"].notna().all()


def test_peer_median_multiples():
    peers = comparable_metrics(
        [company("A", 1.0), company("B", 1.2), company("C", 0.8)]
    )

    multiples = peer_multiples(peers)

    assert set(multiples.index) == {
        "ev_revenue",
        "ev_ebitda",
        "ev_ebit",
        "pe",
    }
    assert np.isfinite(multiples.to_numpy()).all()


def test_peer_exclusion():
    peers = comparable_metrics(
        [company("A", 1.0), company("B", 1.2), company("C", 0.8)]
    )

    multiples = peer_multiples(peers, exclude_ticker="B")

    assert len(multiples) == 4
    assert np.isfinite(multiples.to_numpy()).all()


def test_comparable_valuation():
    target = company("TARGET", 1.0)
    peers = [company("A", 1.1), company("B", 0.9), company("C", 1.2)]

    result = comparable_valuation_table(target, peers)

    assert len(result) == 3
    assert {
        "implied_enterprise_value",
        "implied_equity_value",
        "implied_value_per_share",
    }.issubset(result.columns)
    assert result["implied_value_per_share"].notna().all()


def test_roic_calculation(historical):
    result = calculate_roic(
        historical,
        tax_rate=0.21,
        wacc=0.09,
    )

    assert len(result) == 5
    assert result["nopat"].notna().all()
    assert result["invested_capital"].gt(0).all()
    assert result["roic"].notna().all()
    assert result["value_creation_spread"].notna().all()


def test_roic_formula(historical):
    result = roic_summary(
        historical,
        tax_rate=0.21,
        wacc=0.09,
    )

    expected_nopat = result.ebit * (1.0 - 0.21)
    expected_roic = expected_nopat / result.invested_capital

    assert result.nopat == pytest.approx(expected_nopat)
    assert result.roic == pytest.approx(expected_roic)
    assert result.value_creation_spread == pytest.approx(
        result.roic - 0.09
    )


def test_roic_table(historical):
    result = roic_summary(
        historical,
        tax_rate=0.21,
        wacc=0.09,
    )

    table = roic_table(result)

    assert list(table.columns) == ["Metric", "Value"]
    assert "ROIC" in set(table["Metric"])
    assert "ROIC - WACC" in set(table["Metric"])


def test_integrated_valuation(historical):
    target = company("MSFT", 1.0)
    peers = [
        company("AAPL", 1.1),
        company("GOOGL", 0.95),
        company("AMZN", 1.05),
    ]

    result = build_integrated_valuation(
        ticker="MSFT",
        dcf_value_per_share=125.0,
        target=target,
        peers=peers,
        historical=historical,
        tax_rate=0.21,
        wacc=0.09,
    )

    table = integrated_valuation_table(result)

    assert len(table) == 2
    assert list(table.columns) == [
        "Method",
        "Value Per Share",
    ]
    assert result.roic.roic > 0
    assert np.isfinite(result.comparable_value_per_share)


def test_all_six_historical_roic():
    for ticker in ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]:
        historical = ingest_ticker(ticker)

        result = roic_summary(
            historical,
            tax_rate=0.21,
            wacc=0.09,
        )

        assert result.invested_capital > 0
        assert np.isfinite(result.roic)
        assert np.isfinite(result.nopat)
