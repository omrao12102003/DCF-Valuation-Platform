from app.data.company_selector import AVAILABLE_COMPANIES
from app.data.ingestion import ingest_ticker


def test_core_metrics_exist_for_all_companies():
    required = {
        "revenue",
        "gross_profit",
        "ebitda",
        "ebit",
        "free_cash_flow",
        "net_debt",
    }

    for ticker in AVAILABLE_COMPANIES:
        frame = ingest_ticker(ticker)

        assert len(frame) == 5
        assert required.issubset(frame.columns)
        assert not frame[list(required)].isna().any().any()


def test_free_cash_flow_reconciliation():
    for ticker in AVAILABLE_COMPANIES:
        frame = ingest_ticker(ticker)

        expected = (
            frame["operating_cash_flow"]
            - frame["capital_expenditure"]
        )

        assert frame["free_cash_flow"].equals(expected)


def test_historical_period_integrity():
    for ticker in AVAILABLE_COMPANIES:
        frame = ingest_ticker(ticker)

        assert frame["fiscal_year"].nunique() == 5
        assert frame["fiscal_year"].is_monotonic_increasing
        assert (frame["revenue"] > 0).all()
