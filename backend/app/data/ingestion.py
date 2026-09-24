from pathlib import Path

import pandas as pd

from app.data.normalization import (
    calculate_historical_metrics,
    load_historical_data,
)


def ingest_company_history(path: str | Path) -> pd.DataFrame:
    """
    Load and normalize a company's historical financial statements.
    """

    historical = load_historical_data(path)

    return calculate_historical_metrics(historical)
