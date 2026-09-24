from pathlib import Path

AVAILABLE_COMPANIES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "META": "Meta",
}


def available_companies() -> dict[str, str]:
    return AVAILABLE_COMPANIES.copy()


def get_company_file(
    ticker: str,
    data_directory: str | Path | None = None,
) -> Path:
    ticker = ticker.strip().upper()

    if ticker not in AVAILABLE_COMPANIES:
        available = ", ".join(AVAILABLE_COMPANIES)
        raise ValueError(
            f"Unknown company '{ticker}'. Available companies: {available}"
        )

    if data_directory is None:
        data_directory = Path(__file__).resolve().parents[3] / "data" / "raw"

    path = Path(data_directory) / f"{ticker}_historical.csv"

    if not path.is_file():
        raise FileNotFoundError(f"Historical dataset not found: {path}")

    return path
