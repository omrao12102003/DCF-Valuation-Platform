from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ComparableCompany:
    ticker: str
    revenue: float
    ebitda: float
    ebit: float
    net_income: float
    cash: float
    debt: float
    market_cap: float
    shares_outstanding: float

    @property
    def enterprise_value(self) -> float:
        return self.market_cap + self.debt - self.cash

    @property
    def ev_revenue(self) -> float:
        return self.enterprise_value / self.revenue

    @property
    def ev_ebitda(self) -> float:
        return self.enterprise_value / self.ebitda

    @property
    def ev_ebit(self) -> float:
        return self.enterprise_value / self.ebit

    @property
    def pe(self) -> float:
        return self.market_cap / self.net_income


def comparable_metrics(companies: list[ComparableCompany]) -> pd.DataFrame:
    rows = []

    for company in companies:
        rows.append(
            {
                "ticker": company.ticker,
                "revenue": company.revenue,
                "ebitda": company.ebitda,
                "ebit": company.ebit,
                "net_income": company.net_income,
                "cash": company.cash,
                "debt": company.debt,
                "market_cap": company.market_cap,
                "enterprise_value": company.enterprise_value,
                "ev_revenue": company.ev_revenue,
                "ev_ebitda": company.ev_ebitda,
                "ev_ebit": company.ev_ebit,
                "pe": company.pe,
                "shares_outstanding": company.shares_outstanding,
            }
        )

    return pd.DataFrame(rows)


def peer_multiples(
    peers: pd.DataFrame,
    *,
    exclude_ticker: str | None = None,
) -> pd.Series:
    data = peers.copy()

    if exclude_ticker is not None:
        data = data[data["ticker"] != exclude_ticker]

    if data.empty:
        raise ValueError("At least one peer is required.")

    columns = ["ev_revenue", "ev_ebitda", "ev_ebit", "pe"]

    return data[columns].median()


def implied_enterprise_value(
    target: ComparableCompany,
    peer_multiples: pd.Series,
) -> pd.DataFrame:
    rows = [
        {
            "method": "EV / Revenue",
            "multiple": float(peer_multiples["ev_revenue"]),
            "metric": target.revenue,
            "implied_enterprise_value": float(
                peer_multiples["ev_revenue"] * target.revenue
            ),
        },
        {
            "method": "EV / EBITDA",
            "multiple": float(peer_multiples["ev_ebitda"]),
            "metric": target.ebitda,
            "implied_enterprise_value": float(
                peer_multiples["ev_ebitda"] * target.ebitda
            ),
        },
        {
            "method": "EV / EBIT",
            "multiple": float(peer_multiples["ev_ebit"]),
            "metric": target.ebit,
            "implied_enterprise_value": float(
                peer_multiples["ev_ebit"] * target.ebit
            ),
        },
    ]

    result = pd.DataFrame(rows)
    result["implied_equity_value"] = (
        result["implied_enterprise_value"]
        - target.debt
        + target.cash
    )
    result["implied_value_per_share"] = (
        result["implied_equity_value"] / target.shares_outstanding
    )
    return result


def comparable_valuation_table(
    target: ComparableCompany,
    peers: list[ComparableCompany],
) -> pd.DataFrame:
    metrics = comparable_metrics(peers + [target])
    multiples = peer_multiples(metrics, exclude_ticker=target.ticker)
    implied = implied_enterprise_value(target, multiples)

    return implied.assign(target=target.ticker)
