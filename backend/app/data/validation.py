from __future__ import annotations

import pandas as pd


def validate_historical_data(frame: pd.DataFrame) -> list[str]:
    """
    Return accounting/data-quality issues found in the historical dataset.
    """

    issues: list[str] = []

    if frame.empty:
        issues.append("Historical dataset is empty.")
        return issues

    if frame["fiscal_year"].duplicated().any():
        issues.append("Duplicate fiscal years detected.")

    if not frame["fiscal_year"].is_monotonic_increasing:
        issues.append("Fiscal years are not ordered chronologically.")

    monetary_columns = [
        column
        for column in frame.columns
        if column not in {"fiscal_year", "revenue_growth"}
    ]

    for column in monetary_columns:
        if frame[column].isna().any():
            issues.append(f"Missing values detected in {column}.")

    if (frame["revenue"] < 0).any():
        issues.append("Negative revenue detected.")

    if (frame["capital_expenditure"] < 0).any():
        issues.append("Capital expenditure cannot be negative.")

    return issues
