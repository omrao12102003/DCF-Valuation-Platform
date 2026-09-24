from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.data.ingestion import ingest_ticker
from app.finance.forecast import ForecastAssumptions
from app.finance.three_statement import (
    ThreeStatementModel,
    build_three_statement_model,
)


def build_company_forecast(
    ticker: str,
    data_directory: str | Path | None = None,
    assumptions: ForecastAssumptions | None = None,
) -> ThreeStatementModel:
    historical = ingest_ticker(
        ticker=ticker,
        data_directory=data_directory,
    )

    return build_three_statement_model(
        historical=historical,
        assumptions=assumptions,
    )


def forecast_summary(
    ticker: str,
    data_directory: str | Path | None = None,
    assumptions: ForecastAssumptions | None = None,
) -> pd.DataFrame:
    model = build_company_forecast(
        ticker=ticker,
        data_directory=data_directory,
        assumptions=assumptions,
    )

    forecast = model.forecast

    return forecast[
        [
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
        ]
    ].copy()
