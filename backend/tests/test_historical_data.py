from pathlib import Path

import pandas as pd
import pytest

from app.data.ingestion import ingest_company_history
from app.data.normalization import calculate_historical_metrics
from app.data.validation import validate_historical_data
from app.finance.financial_statements import calculate_statement_metrics


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "msft_historical.csv"
)


def test_msft_dataset_loads():
    frame = ingest_company_history(DATA_PATH)

    assert len(frame) == 5
    assert frame["fiscal_year"].tolist() == [
        2021,
        2022,
        2023,
        2024,
        2025,
    ]


def test_historical_metrics_are_calculated():
    frame = ingest_company_history(DATA_PATH)

    latest = frame.iloc[-1]

    assert latest["revenue"] == 281724
    assert latest["gross_profit"] == 195422
    assert latest["ebitda"] == 131604
    assert latest["ebit"] == 116374
    assert latest["net_debt"] == -30444
    assert latest["free_cash_flow"] == 52900


def test_revenue_growth_is_calculated():
    frame = ingest_company_history(DATA_PATH)

    latest_growth = frame.iloc[-1]["revenue_growth"]

    expected = (281724 / 245122) - 1

    assert latest_growth == pytest.approx(expected)


def test_historical_validation_passes():
    frame = ingest_company_history(DATA_PATH)

    issues = validate_historical_data(frame)

    assert issues == []


def test_statement_engine_matches_normalized_metrics():
    frame = ingest_company_history(DATA_PATH)

    calculated = calculate_statement_metrics(frame)

    assert calculated.iloc[-1]["gross_profit"] == 195422
    assert calculated.iloc[-1]["ebitda"] == 131604
    assert calculated.iloc[-1]["ebit"] == 116374
    assert calculated.iloc[-1]["free_cash_flow"] == 52900


def test_invalid_dataset_is_detected():
    invalid = pd.DataFrame(
        {
            "fiscal_year": [2024, 2023],
            "revenue": [100, -50],
            "capital_expenditure": [10, 10],
        }
    )

    issues = validate_historical_data(invalid)

    assert "Fiscal years are not ordered chronologically." in issues
    assert "Negative revenue detected." in issues
