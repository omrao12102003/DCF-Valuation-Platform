from pydantic import BaseModel, Field


class Company(BaseModel):
    """
    Basic company identity used by the financial modelling engine.
    """

    ticker: str = Field(min_length=1)
    name: str = Field(min_length=1)
    country: str = Field(min_length=1)
    reporting_currency: str = Field(min_length=3, max_length=3)

    shares_outstanding_millions: float | None = Field(default=None, gt=0)

    @property
    def ticker_normalized(self) -> str:
        return self.ticker.upper()
