from pathlib import Path

import pandas as pd

from app.data.company_selector import get_company_file
from app.data.normalization import (
    calculate_historical_metrics,
    load_historical_data,
)


def ingest_company_history(path: str | Path) -> pd.DataFrame:
    historical_data = load_historical_data(path)
    return calculate_historical_metrics(historical_data)


def ingest_ticker(
    ticker: str,
    data_directory: str | Path | None = None,
) -> pd.DataFrame:
    return ingest_company_history(
        get_company_file(ticker, data_directory)
    )
