# Financial Model Architecture

## Purpose

The DCF Valuation Platform is primarily a financial modelling and valuation
engine. Python is used to implement the financial logic, but the central
objective is accounting analysis, forecasting and valuation.

The model separates four concepts:

1. Reported financial data
2. Normalized financial data
3. Forecast assumptions
4. Valuation calculations

This separation prevents assumptions from being confused with historical
results.

## Internal financial unit

Monetary values are represented internally in millions of the reporting
currency.

For example:

- USD 281 billion revenue is represented as 281,000 million USD.
- Currency remains explicitly attached to the financial period.

The data acquisition and normalization layers are responsible for converting
external data into this internal representation.

## Financial period

Each financial period contains:

- fiscal year
- reporting period
- period-end date
- currency
- historical/forecast status
- income statement
- balance sheet
- cash flow statement
- data source

Historical and forecast periods intentionally use the same structural model.
This allows actual financial results to flow into the forecast engine without
creating a separate incompatible data structure.

## Income statement

The model derives:

Revenue
→ Gross Profit
→ EBITDA
→ EBIT
→ EBT
→ Net Income

The reported inputs and derived profitability metrics remain conceptually
separate.

## Balance sheet

The model stores the major operating, investing and financing balances and
derives:

- Total Assets
- Total Liabilities
- Balance Sheet Check
- Net Debt

The accounting identity is:

Assets = Liabilities + Equity

## Cash flow statement

The cash flow structure supports:

- Net Income
- Depreciation and Amortization
- Working Capital
- Capital Expenditure
- Operating Cash Flow
- Free Cash Flow
- Debt financing
- Equity financing
- Dividends

## Forecast assumptions

Forecast assumptions are deliberately separated from financial statements.

Examples include:

- Revenue growth
- Gross margin
- Operating expense percentage
- Tax rate
- DSO
- DIO
- DPO
- CapEx percentage
- Depreciation percentage
- Terminal growth
- Risk-free rate
- Equity risk premium
- Beta
- Cost of debt

These assumptions will later drive the forecast and valuation engines.

## Future financial flow

The completed platform will follow:

Historical Data
→ Normalization
→ Historical Analysis
→ Forecast Assumptions
→ Revenue Model
→ Operating Model
→ Working Capital
→ PP&E
→ Debt
→ Equity
→ Three-Statement Model
→ UFCF
→ WACC
→ DCF
→ Reverse DCF
→ Scenarios
→ Sensitivity
→ Comparables
→ ROIC
→ Valuation Reconciliation

The financial engine is the primary product. Any API or interface added later
will expose this model rather than becoming the centre of the project.
