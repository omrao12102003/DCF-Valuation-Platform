import pytest

from app.data.company_selector import (
    AVAILABLE_COMPANIES,
    available_companies,
    get_company_file,
)
from app.data.ingestion import ingest_ticker
from app.data.validation import validate_historical_data


def test_company_universe():
    companies = available_companies()

    assert len(companies) == 6
    assert set(companies) == {
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "META",
    }


def test_company_files_exist():
    for ticker in AVAILABLE_COMPANIES:
        assert get_company_file(ticker).is_file()


@pytest.mark.parametrize("ticker", list(AVAILABLE_COMPANIES))
def test_company_can_be_ingested(ticker):
    frame = ingest_ticker(ticker)

    assert len(frame) == 5
    assert frame["fiscal_year"].is_monotonic_increasing
    assert (frame["revenue"] > 0).all()
    assert frame["ebitda"].notna().all()
    assert frame["ebit"].notna().all()
    assert frame["free_cash_flow"].notna().all()


@pytest.mark.parametrize("ticker", list(AVAILABLE_COMPANIES))
def test_company_passes_validation(ticker):
    frame = ingest_ticker(ticker)

    assert validate_historical_data(frame) == []


def test_ticker_selection_is_case_insensitive():
    assert (
        ingest_ticker("MSFT")["revenue"].tolist()
        == ingest_ticker("msft")["revenue"].tolist()
    )


def test_unknown_ticker_is_rejected():
    with pytest.raises(ValueError, match="Unknown company"):
        get_company_file("TSLA")


def test_all_companies_use_same_schema():
    schemas = {
        tuple(ingest_ticker(ticker).columns)
        for ticker in AVAILABLE_COMPANIES
    }

    assert len(schemas) == 1
