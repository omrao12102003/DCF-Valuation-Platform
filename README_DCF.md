# DCF Valuation Platform

### A Finance-First Equity Valuation & Financial Modelling Engine

**Developed by Om Barot**

A modular Python-based financial modelling platform designed to reproduce the core workflow of fundamental equity research: historical financial analysis, integrated forecasting, three-statement modelling, UFCF, WACC, DCF valuation, sensitivity analysis, reverse DCF, trading comparables, ROIC and Excel reporting.

The project was built with a finance-first approach. The objective is not to create a large software product for its own sake, but to build a transparent, testable and extensible valuation engine where the financial logic remains visible and auditable.

---

## 1. Project Overview

Valuation is rarely a single formula. A reliable DCF begins with historical financial statements, develops explicit operating assumptions, connects the income statement, balance sheet and cash flow statement, converts operating performance into unlevered free cash flow, estimates the cost of capital and finally derives an intrinsic equity value.

This platform follows that complete workflow:

```text
Historical Financial Data
          ↓
Data Ingestion & Normalization
          ↓
Historical Financial Analysis
          ↓
Operating & Financial Forecast
          ↓
Integrated Three-Statement Model
          ↓
Unlevered Free Cash Flow
          ↓
WACC
          ↓
DCF Valuation
          ↓
Sensitivity Analysis
          ↓
Reverse DCF
          ↓
Trading Comparables
          ↓
ROIC Analysis
          ↓
Integrated Valuation
          ↓
Excel Reporting
```

The architecture is deliberately modular so that each stage can be tested independently while still forming one connected valuation pipeline.

---

# 2. Development Roadmap

| Stage | Area | Status |
|---|---|---|
| 1 | Financial Modelling Foundation | Complete |
| 2 | Historical Financial Data Engine | Complete |
| 3 | Forecast Engine & Three-Statement Model | Complete |
| 4 | UFCF, WACC & DCF Valuation | Complete |
| 5 | Sensitivity Analysis & Reverse DCF | Complete |
| 6 | Trading Comparables, ROIC & Integrated Valuation | Complete |
| 7 | Excel Reporting & Final Validation | Complete |

---

# 3. Stage 1 — Financial Modelling Foundation

## Objective

The first stage establishes the financial data structures used throughout the platform.

Instead of keeping financial information as disconnected numbers, the project models the major financial statements as structured objects with validation and derived financial metrics.

## Main Components

- Company model
- Financial assumptions
- Income statement
- Balance sheet
- Cash flow statement
- Financial period
- Company financials
- Validation rules

## Income Statement Logic

The model derives the main profitability layers:

```text
Revenue
    -
Cost of Revenue
    =
Gross Profit

Gross Profit
    -
Operating Expenses
    =
EBITDA

EBITDA
    -
Depreciation & Amortization
    =
EBIT

EBIT
    -
Interest Expense
    =
EBT

EBT
    -
Taxes
    =
Net Income
```

### Core formulas

**Gross Profit**

```text
Gross Profit = Revenue - Cost of Revenue
```

**EBITDA**

```text
EBITDA = Gross Profit - Operating Expenses
```

**EBIT**

```text
EBIT = EBITDA - Depreciation & Amortization
```

**EBT**

```text
EBT = EBIT - Interest Expense
```

**Net Income**

```text
Net Income = EBT - Taxes
```

## Balance Sheet Logic

The balance sheet tracks operating assets, financing liabilities and shareholder equity.

```text
Total Assets
    =
Cash
+ Accounts Receivable
+ Inventory
+ Other Current Assets
+ PP&E
+ Goodwill
+ Intangible Assets
+ Other Non-Current Assets
```

```text
Total Liabilities
    =
Accounts Payable
+ Accrued Liabilities
+ Debt
+ Other Liabilities
```

The model validates:

```text
Balance Check
=
Total Assets
-
Total Liabilities
-
Shareholders' Equity
```

A balanced statement should produce a value close to zero.

## Cash Flow Logic

The foundation also establishes operating cash flow, capital expenditure and free cash flow relationships.

```text
Free Cash Flow
=
Operating Cash Flow
-
Capital Expenditure
```

## Technology Used

- Python
- Pydantic
- Dataclasses
- Pytest

## Why This Stage Matters

Every later valuation calculation depends on consistent financial definitions. Stage 1 therefore acts as the modelling foundation rather than simply being a data container.

---

# 4. Stage 2 — Historical Financial Data Engine

## Objective

Stage 2 introduces a standardized historical financial-data pipeline.

The goal is to take company financial data, normalize it into a common schema and calculate historical performance metrics consistently across companies.

## Companies Included for Development

```text
AAPL   Apple
MSFT   Microsoft
GOOGL  Alphabet
AMZN   Amazon
NVDA   NVIDIA
META   Meta
```

Historical periods currently cover:

```text
2021
2022
2023
2024
2025
```

## Data Pipeline

```text
CSV Dataset
    ↓
Company Selection
    ↓
Data Loading
    ↓
Schema Validation
    ↓
Normalization
    ↓
Historical Metrics
```

## Historical Metrics

The engine calculates:

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
- FCF margin

### Revenue Growth

```text
Revenue Growth
=
(Current Revenue / Previous Revenue) - 1
```

### Gross Margin

```text
Gross Margin
=
Gross Profit / Revenue
```

### EBITDA Margin

```text
EBITDA Margin
=
EBITDA / Revenue
```

### EBIT Margin

```text
EBIT Margin
=
EBIT / Revenue
```

### Net Margin

```text
Net Margin
=
Net Income / Revenue
```

### Net Debt

```text
Net Debt
=
Total Debt - Cash & Equivalents
```

### FCF Margin

```text
FCF Margin
=
Free Cash Flow / Revenue
```

## Technology Used

- Python
- Pandas
- NumPy
- Pytest
- CSV-based financial data

## Engineering Logic

A common schema is used across companies so that the same financial calculations can be applied to every dataset.

This makes the valuation engine reusable rather than hard-coded around one company.

## Data Note

The included company datasets are development/synthetic datasets used to test the architecture and financial calculations. They are not intended to represent live market data or verified current financial statements.

---

# 5. Stage 3 — Forecast Engine & Three-Statement Model

## Objective

Stage 3 converts historical financial information into an integrated five-year forecast.

This is one of the most important parts of the platform because a DCF should be driven by explicit operating and financial assumptions rather than by directly projecting a valuation number.

## Forecast Horizon

Default forecast horizon:

```text
5 Years
```

## Forecast Assumptions

The forecast engine supports assumptions including:

- Revenue growth
- Gross margin
- Operating expenses as a percentage of revenue
- Depreciation as a percentage of revenue
- Interest/debt assumptions
- Tax rate
- Days Sales Outstanding
- Days Inventory Outstanding
- Days Payables Outstanding
- Capital expenditure as a percentage of revenue
- Working-capital ratios
- Debt repayment
- Minimum cash

## Revenue Forecast

```text
Revenue(t)
=
Revenue(t-1) × (1 + Growth Rate)
```

## Gross Profit

```text
Gross Profit
=
Revenue × Gross Margin
```

## Cost of Revenue

```text
Cost of Revenue
=
Revenue - Gross Profit
```

## Operating Expenses

```text
Operating Expenses
=
Revenue × Operating Expense Ratio
```

## EBITDA

```text
EBITDA
=
Gross Profit - Operating Expenses
```

## Depreciation

```text
D&A
=
Revenue × D&A / Revenue
```

## EBIT

```text
EBIT
=
EBITDA - D&A
```

## Interest Expense

Interest expense is linked to the debt structure rather than being treated as an isolated historical number.

## Taxes

```text
Taxes
=
EBT × Tax Rate
```

## Net Income

```text
Net Income
=
EBT - Taxes
```

---

## Three-Statement Integration

The forecast model connects all three financial statements.

```text
             Income Statement
                    │
                    │ Net Income
                    ↓
             Cash Flow Statement
                    │
                    │ Cash Flow
                    ↓
              Balance Sheet
                    │
             ┌──────┴──────┐
             ↓             ↓
            Cash          Equity
```

## Working Capital

Operating working capital is calculated from operating current assets and liabilities.

```text
NWC
=
Accounts Receivable
+ Inventory
+ Other Current Assets
- Accounts Payable
- Accrued Liabilities
```

## Working Capital Drivers

### Accounts Receivable

```text
AR
≈
Revenue × DSO / 365
```

### Inventory

```text
Inventory
≈
Cost of Revenue × DIO / 365
```

### Accounts Payable

```text
AP
≈
Cost of Revenue × DPO / 365
```

## PP&E Roll-Forward

```text
Ending PP&E
=
Beginning PP&E
+ Capital Expenditure
- Depreciation
```

## Equity Roll-Forward

The model connects earnings to equity through the forecast period.

## Balance Sheet Validation

```text
Balance Check
=
Total Assets
-
Total Liabilities
-
Shareholders' Equity
```

The integrated forecast is expected to remain internally consistent.

## Technology Used

- Python
- Pandas
- NumPy
- Dataclasses
- Pytest

---

# 6. Stage 4 — UFCF, WACC & DCF Valuation

## Objective

Stage 4 converts the forecast into intrinsic enterprise and equity value.

This is the core valuation stage.

---

## 6.1 Unlevered Free Cash Flow

The platform calculates UFCF independently from financing structure.

### NOPAT

```text
NOPAT
=
EBIT × (1 - Tax Rate)
```

### Change in Working Capital

```text
Change in NWC
=
NWC(t) - NWC(t-1)
```

### UFCF

```text
UFCF
=
NOPAT
+ D&A
- Capital Expenditure
- Change in NWC
```

This measures the cash flow available to all capital providers before financing effects.

---

# 6.2 WACC

Weighted Average Cost of Capital is used as the discount rate.

## Cost of Equity

The platform uses the CAPM framework:

```text
Cost of Equity
=
Risk-Free Rate
+
Beta × Equity Risk Premium
```

## After-Tax Cost of Debt

```text
After-Tax Cost of Debt
=
Pre-Tax Cost of Debt × (1 - Tax Rate)
```

## Capital Weights

```text
Equity Weight
=
Equity Value / (Equity Value + Debt)
```

```text
Debt Weight
=
Debt / (Equity Value + Debt)
```

## WACC

```text
WACC
=
Equity Weight × Cost of Equity
+
Debt Weight × After-Tax Cost of Debt
```

---

# 6.3 DCF Valuation

Each forecast UFCF is discounted back to present value.

## Present Value of UFCF

```text
PV(UFCF)
=
UFCF / (1 + WACC)^t
```

where `t` is the forecast year.

---

## Terminal Value

The platform uses the Gordon Growth Method.

```text
Terminal Value
=
UFCF(n) × (1 + g)
/
(WACC - g)
```

where:

- `g` = terminal growth rate
- `n` = final forecast year

## Present Value of Terminal Value

```text
PV(Terminal Value)
=
Terminal Value / (1 + WACC)^n
```

## Enterprise Value

```text
Enterprise Value
=
PV of Explicit Forecast
+
PV of Terminal Value
```

## Equity Value

```text
Equity Value
=
Enterprise Value
-
Net Debt
```

Because:

```text
Net Debt = Debt - Cash
```

## Intrinsic Value Per Share

```text
Intrinsic Value Per Share
=
Equity Value / Shares Outstanding
```

## Technology Used

- Python
- NumPy
- Pandas
- SciPy
- Dataclasses
- Pytest

---

# 7. Stage 5 — Sensitivity Analysis & Reverse DCF

## Objective

A DCF is highly dependent on assumptions. Stage 5 evaluates how valuation changes when key assumptions change.

---

## 7.1 DCF Sensitivity Analysis

The primary sensitivity matrix varies:

```text
WACC × Terminal Growth
```

For every combination, the DCF is recalculated.

Conceptually:

```text
                 Terminal Growth
              ↓    ↓    ↓    ↓    ↓

WACC →        DCF valuation per share
```

This helps identify how dependent the valuation is on the discount rate and terminal growth assumption.

---

## 7.2 Forecast Sensitivity

The platform also evaluates:

```text
Revenue Growth × EBIT Margin
```

This tests how operating performance assumptions affect valuation.

For example:

```text
Higher Revenue Growth
        +
Higher EBIT Margin
        ↓
Higher Forecast Cash Flow
        ↓
Higher DCF Value
```

The calculation is performed through the actual valuation engine rather than applying a simple percentage adjustment to the final price.

---

# 7.3 Reverse DCF

Normal DCF:

```text
Operating Assumptions
        ↓
Cash Flows
        ↓
DCF
        ↓
Value Per Share
```

Reverse DCF works in the opposite direction:

```text
Target Share Price
        ↓
Required Enterprise Value
        ↓
Required Terminal Value
        ↓
Implied Terminal Growth
```

The platform solves for the terminal growth rate that makes the DCF equal to a specified target price.

## Numerical Logic

A bisection-style numerical search is used.

Conceptually:

```text
Lower Growth
      ↓
Calculate DCF
      ↓
Compare with Target
      ↓
Adjust Growth Range
      ↓
Repeat
      ↓
Implied Terminal Growth
```

The model enforces the fundamental DCF constraint:

```text
Terminal Growth < WACC
```

## Technology Used

- Python
- NumPy
- Pandas
- Numerical solving logic
- Pytest

---

# 8. Stage 6 — Trading Comparables, ROIC & Integrated Valuation

## Objective

Stage 6 adds market-based valuation and return-on-capital analysis to complement the intrinsic DCF model.

---

# 8.1 Trading Comparables

The platform supports:

```text
EV / Revenue
EV / EBITDA
EV / EBIT
P / E
```

## Enterprise Value

```text
Enterprise Value
=
Market Capitalization
+
Debt
-
Cash
```

## EV / Revenue

```text
EV / Revenue
=
Enterprise Value / Revenue
```

## EV / EBITDA

```text
EV / EBITDA
=
Enterprise Value / EBITDA
```

## EV / EBIT

```text
EV / EBIT
=
Enterprise Value / EBIT
```

## P / E

```text
P / E
=
Market Capitalization / Net Income
```

Peer multiples are aggregated using median statistics to reduce the impact of extreme individual observations.

## Implied Valuation

For an EV-based multiple:

```text
Implied Enterprise Value
=
Target Financial Metric × Peer Multiple
```

Then:

```text
Implied Equity Value
=
Implied Enterprise Value
-
Debt
+
Cash
```

For P/E:

```text
Implied Equity Value
=
Target Net Income × Peer P/E
```

---

# 8.2 ROIC

Return on Invested Capital evaluates how effectively the business generates operating returns from invested capital.

## NOPAT

```text
NOPAT
=
EBIT × (1 - Tax Rate)
```

## Invested Capital

```text
Invested Capital
=
Equity
+
Debt
-
Cash
```

## ROIC

```text
ROIC
=
NOPAT / Invested Capital
```

## Value Creation Spread

When WACC is available:

```text
Value Creation Spread
=
ROIC - WACC
```

This allows the model to compare operating returns with the estimated cost of capital.

---

# 8.3 Integrated Valuation

The platform brings together multiple valuation perspectives:

```text
                  DCF
                   │
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
   Intrinsic   Market-Based  Returns
   Valuation   Comparables   Analysis
        │          │          │
        └──────────┼──────────┘
                   ↓
          Integrated Analysis
```

The purpose is not to force different valuation methods into one arbitrary number, but to allow the analyst to examine the company from several financial perspectives.

## Technology Used

- Python
- Pandas
- NumPy
- Dataclasses
- Pytest

---

# 9. Stage 7 — Excel Reporting & Final Validation

## Objective

Stage 7 converts the Python valuation engine into a structured analyst-style Excel output and performs final system validation.

## Excel Technology

The workbook is generated using:

```text
Python
+
OpenPyXL
```

## Intended Report Structure

The generated workbook is designed to contain dedicated sheets for major parts of the valuation process, including:

```text
Historical
Forecast
Income Statement
Balance Sheet
Cash Flow
UFCF
WACC
DCF
DCF Sensitivity
Forecast Sensitivity
Reverse DCF
Comparables
ROIC
Valuation
Integrated Analysis
```

## Reporting Principle

The Excel workbook is not intended to replace the Python engine.

Instead:

```text
Python Financial Engine
        ↓
Validated Calculations
        ↓
Structured Excel Report
```

This keeps the calculation logic centralized while providing a familiar format for financial analysis.

## Final Validation

Stage 7 validates:

- Python compilation
- Automated test suite
- Financial calculations
- Multi-company processing
- Workbook generation
- Workbook readability
- Required report outputs
- Git working-tree integrity

## Output

```text
data/processed/DCF_Valuation_Platform_Final.xlsx
```

## Technology Used

- Python
- OpenPyXL
- Pandas
- Pytest

---

# 10. Technology Stack

## Core Programming

- Python 3
- Object-oriented and modular Python design
- Dataclasses
- Type hints

## Financial & Data Analysis

- NumPy
- Pandas
- SciPy
- statsmodels

## Data Validation

- Pydantic
- Custom financial validation logic

## Reporting

- OpenPyXL
- Excel workbook generation

## Testing

- Pytest
- Unit testing
- Integration testing
- Multi-company smoke testing
- Financial integrity validation

## Development Environment

- macOS
- VS Code
- Ghostty Terminal
- Git
- GitHub

---

# 11. Project Architecture

```text
DCF-Valuation-Platform/
│
├── README.md
├── requirements.txt
├── pytest.ini
├── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   │
│   │   ├── data/
│   │   │   ├── ingestion.py
│   │   │   ├── normalization.py
│   │   │   ├── validation.py
│   │   │   └── company_selector.py
│   │   │
│   │   ├── finance/
│   │   │   ├── capex.py
│   │   │   ├── comparables.py
│   │   │   ├── company_forecast.py
│   │   │   ├── dcf.py
│   │   │   ├── debt.py
│   │   │   ├── equity.py
│   │   │   ├── excel_export.py
│   │   │   ├── fcf.py
│   │   │   ├── financial_statements.py
│   │   │   ├── forecast.py
│   │   │   ├── integrated_valuation.py
│   │   │   ├── reverse_dcf.py
│   │   │   ├── roic.py
│   │   │   ├── sensitivity.py
│   │   │   ├── three_statement.py
│   │   │   ├── ufcf.py
│   │   │   ├── valuation.py
│   │   │   ├── wacc.py
│   │   │   └── working_capital.py
│   │   │
│   │   └── models/
│   │       ├── assumptions.py
│   │       ├── company.py
│   │       ├── financials.py
│   │       └── valuation.py
│   │
│   ├── scripts/
│   │   └── build_final_workbook.py
│   │
│   └── tests/
│
├── data/
│   ├── raw/
│   └── processed/
│
└── docs/
```

---

# 12. Testing Philosophy

The project is designed around the principle that financial models should be testable, not just executable.

Testing covers:

- Input validation
- Financial statement calculations
- Historical metrics
- Forecast calculations
- Three-statement integration
- Balance-sheet integrity
- UFCF
- WACC
- DCF
- Sensitivity analysis
- Reverse DCF
- Comparable-company calculations
- ROIC
- Integrated valuation
- Excel export
- Multi-company processing

Typical validation commands:

```bash
pytest -q
```

```bash
python -m compileall -q backend/app backend/tests
```

```bash
git diff --check
```

---

# 13. Financial Modelling Principles

## Transparency

Financial formulas are implemented explicitly so that assumptions and calculations can be inspected.

## Modularity

Each major financial function is isolated into its own module.

## Reproducibility

The same inputs and assumptions should produce the same outputs.

## Validation

The model continuously checks financial relationships rather than assuming that calculations are correct.

## Chronological Integrity

Historical periods and forecast periods are kept conceptually separate to reduce the risk of look-ahead bias.

## Finance Before Interface

The core objective is the financial engine. User-interface complexity is intentionally kept secondary to financial correctness and model transparency.

---

# 14. Data & Valuation Disclaimer

The current repository includes development/synthetic financial datasets for architecture and testing purposes.

The outputs should therefore not be interpreted as:

- Live market valuations
- Verified current company financial statements
- Investment advice
- Analyst recommendations
- Price targets based on current market data

For production research, the historical datasets, market capitalization, debt, cash, beta, risk-free rate, equity risk premium and other assumptions should be replaced with current, verified sources.

The platform is an educational and technical financial-modelling project.

---

# 15. Developer

## Om Barot

**B.Tech — Computer Science & Engineering**  
**VIT Vellore**  
**Graduated: 2026**

**MSc International Accounting & Finance**  
**Bayes Business School, City St George's, University of London**  
**2026–27**  
**Currently studying**

### Academic Background

The project combines two areas of study:

```text
Computer Science
        +
Accounting & Finance
        ↓
Financial Technology / Quantitative Finance
```

The Computer Science background provides the programming, data structures, modelling and software engineering foundation, while the MSc in International Accounting & Finance provides a stronger foundation in financial reporting, valuation, accounting and finance.

This project was developed to bring both areas together in a practical financial-modelling environment.

---

# 16. Why This Project Was Built

The purpose of the project was to move beyond isolated finance formulas and build a complete valuation workflow from raw financial data to a final investment-analysis report.

Instead of implementing only a DCF calculator, the platform connects:

```text
Accounting Data
      ↓
Financial Analysis
      ↓
Forecasting
      ↓
Three-Statement Modelling
      ↓
Cash Flow Analysis
      ↓
Cost of Capital
      ↓
Intrinsic Valuation
      ↓
Market Valuation
      ↓
Return Analysis
      ↓
Sensitivity & Scenario Analysis
      ↓
Reporting
```

The result is a reusable foundation for further development in:

- Equity Research
- Financial Modelling
- Valuation
- Quantitative Finance
- Investment Analysis
- Financial Data Science
- FinTech

---

# 17. Future Development

Possible future extensions include:

- Live SEC/company filing ingestion
- Current market-price integration
- Automated financial statement extraction
- Historical market-data integration
- More advanced peer-selection algorithms
- Scenario management
- Monte Carlo valuation
- Probability-weighted valuation
- Automated investment research
- LLM-assisted financial-document analysis
- RAG-based financial research
- Portfolio-level valuation
- Backtesting and factor analysis

These are intentionally separated from the current core model so that the existing financial engine remains understandable and testable.

---

# 18. Final Summary

The DCF Valuation Platform is a complete finance-first modelling pipeline covering seven development stages:

```text
1. Financial Modelling Foundation
            ↓
2. Historical Financial Data Engine
            ↓
3. Forecast + Three-Statement Model
            ↓
4. UFCF + WACC + DCF
            ↓
5. Sensitivity + Reverse DCF
            ↓
6. Comparables + ROIC + Integrated Valuation
            ↓
7. Excel Reporting + Final Validation
```

The project brings together software engineering and financial analysis into one reproducible valuation framework.

**Developed by Om Barot**  
**B.Tech CSE, VIT Vellore — 2026**  
**MSc International Accounting & Finance, Bayes Business School — 2026–27**

---

## Project Status

**Core seven-stage DCF valuation platform: Complete**

**Focus: Financial modelling, valuation, analysis and reproducible reporting.**
