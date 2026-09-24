from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WACCInputs:
    risk_free_rate: float
    equity_risk_premium: float
    beta: float
    pre_tax_cost_of_debt: float
    tax_rate: float
    market_value_equity: float
    market_value_debt: float

    def validate(self) -> None:
        for name, value in {
            "risk_free_rate": self.risk_free_rate,
            "equity_risk_premium": self.equity_risk_premium,
            "pre_tax_cost_of_debt": self.pre_tax_cost_of_debt,
            "tax_rate": self.tax_rate,
        }.items():
            if not 0 <= value < 1:
                raise ValueError(
                    f"{name} must be between 0 and 1."
                )

        if self.beta < 0:
            raise ValueError("beta cannot be negative.")

        if self.market_value_equity < 0:
            raise ValueError(
                "market_value_equity cannot be negative."
            )

        if self.market_value_debt < 0:
            raise ValueError(
                "market_value_debt cannot be negative."
            )

        if (
            self.market_value_equity
            + self.market_value_debt
            <= 0
        ):
            raise ValueError(
                "Total capital must be greater than zero."
            )


@dataclass(frozen=True)
class WACCResult:
    cost_of_equity: float
    after_tax_cost_of_debt: float
    equity_weight: float
    debt_weight: float
    wacc: float


def calculate_cost_of_equity(
    risk_free_rate: float,
    equity_risk_premium: float,
    beta: float,
) -> float:
    if beta < 0:
        raise ValueError("beta cannot be negative.")

    return (
        risk_free_rate
        + beta * equity_risk_premium
    )


def calculate_wacc(inputs: WACCInputs) -> WACCResult:
    inputs.validate()

    total_capital = (
        inputs.market_value_equity
        + inputs.market_value_debt
    )

    equity_weight = (
        inputs.market_value_equity
        / total_capital
    )

    debt_weight = (
        inputs.market_value_debt
        / total_capital
    )

    cost_of_equity = calculate_cost_of_equity(
        inputs.risk_free_rate,
        inputs.equity_risk_premium,
        inputs.beta,
    )

    after_tax_cost_of_debt = (
        inputs.pre_tax_cost_of_debt
        * (1.0 - inputs.tax_rate)
    )

    wacc = (
        equity_weight * cost_of_equity
        + debt_weight * after_tax_cost_of_debt
    )

    return WACCResult(
        cost_of_equity=cost_of_equity,
        after_tax_cost_of_debt=after_tax_cost_of_debt,
        equity_weight=equity_weight,
        debt_weight=debt_weight,
        wacc=wacc,
    )
