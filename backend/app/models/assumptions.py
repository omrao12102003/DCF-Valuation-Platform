from pydantic import BaseModel, Field


class FinancialAssumptions(BaseModel):
    """
    Explicit forecasting assumptions.

    Assumptions are kept separate from reported financial data so that
    historical results are never silently mixed with forecasts.
    """

    revenue_growth: float
    gross_margin: float = Field(ge=0, le=1)
    operating_expense_percent_revenue: float = Field(ge=0, le=1)

    tax_rate: float = Field(ge=0, le=1)

    dso: float = Field(ge=0)
    dio: float = Field(ge=0)
    dpo: float = Field(ge=0)

    capex_percent_revenue: float = Field(ge=0, le=1)
    depreciation_percent_revenue: float = Field(ge=0, le=1)

    terminal_growth_rate: float
    risk_free_rate: float = Field(ge=0, le=1)
    equity_risk_premium: float = Field(ge=0, le=1)
    beta: float = Field(gt=0)
    pre_tax_cost_of_debt: float = Field(ge=0, le=1)
