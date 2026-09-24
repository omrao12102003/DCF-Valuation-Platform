# Historical Financial Model

## Development company

Microsoft Corporation (MSFT) is used as the initial development company.

The model is designed so the underlying calculations can later be applied to
other companies.

## Historical period

The development dataset contains five annual periods:

- 2021
- 2022
- 2023
- 2024
- 2025

Monetary values are represented in millions of USD.

## Historical analysis

The model calculates:

- Revenue growth
- Gross profit
- Gross margin
- EBITDA
- EBITDA margin
- EBIT
- EBIT margin
- Net margin
- Net debt
- Free cash flow
- Free cash flow margin

## Design principle

Reported financial data is kept separate from calculated metrics.

This allows the valuation engine to distinguish between:

1. Financial information obtained from a source
2. Normalized financial information
3. Metrics calculated by the model
4. Forecast assumptions

## Next step

The historical model becomes the starting point for the forecast engine.

The latest historical period will become the base year for the forecast.
