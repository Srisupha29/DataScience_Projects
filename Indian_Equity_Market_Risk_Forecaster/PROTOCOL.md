# Research Protocol: Indian Large-Cap Volatility and Risk Predictor

## 1. Research Question

Can statistical and machine-learning models improve forecasts of short-term volatility for Indian large-cap equities compared with established volatility forecasting baselines?

The project forecasts 5-trading-day and 21-trading-day forward volatility. It evaluates forecast accuracy and the usefulness of forecasts for portfolio risk measurement.

This is an independent research and engineering project, not an investment advice or automated trading system.

## 2. Universe and Data

### 2.1 Equity Universe

- **Equity universe:** NIFTY 50 constituents, fixed using one documented start-date constituent list.
- **Stock data:** Daily OHLCV prices from Yahoo Finance using `.NS` tickers.
- **Market and macro data:** NIFTY index, India VIX, USD/INR, Brent crude and US Treasury yields.
- **Data limitation:** Yahoo Finance is an unofficial data source. The fixed constituent universe introduces survivorship bias; this limitation will be disclosed.

### 2.2 Data Management

- Preserve downloaded raw data unchanged.
- Record all cleaning decisions and corrections.
- Maintain reproducible processing from raw data to cleaned datasets.
- Align global market variables to information actually available at the Indian market close.
- Apply appropriate lags to prevent look-ahead bias.
- Maintain source-date metadata for lagged macroeconomic observations.
- Do not use future observations to fill historical missing values.

### 2.3 Data Quality and Corporate Actions

Data processing must address:

- Missing trading days and duplicate dates.
- Zero, negative or invalid prices.
- Missing or zero trading volume.
- Suspicious price movements and potential corporate actions.
- Splits, dividends, demergers and ticker changes.
- Stale prices and unusual observations.

All corrections and exclusions must be documented. Raw source data must remain unchanged.

**Documented TMPV handling:** The 14 October 2025 demerger-related price discontinuity is not corrected by the adjusted-close series. The affected daily return is marked unavailable, and forward target windows containing that return are also unavailable. No unsupported adjustment factor is applied.

Other unresolved anomalies are retained in the corporate-action review documentation and must be treated transparently.

## 3. Forecast Targets

### 3.1 Daily Returns

Use daily close-to-close log returns:

\[
r_t = \ln(P_t/P_{t-1})
\]

where \(P_t\) is the adjusted closing price.

### 3.2 Forward Volatility

Define forward realized-volatility proxies for horizon \(h\):

\[
RV_{t,h} =
\sqrt{\frac{252}{h}\sum_{j=1}^{h}r_{t+j}^{2}}
\]

where:

\[
h \in \{5,21\}
\]

The target windows use returns from \(t+1\) through \(t+h\), excluding the prediction-date return.

These are annualized close-to-close volatility proxies, not true intraday realized volatility.

### 3.3 Target Dataset

For each stock, retain:

- `Daily_Return`
- `RV_5D`
- `RV_21D`

Target datasets are stored separately from model features.

Observations without sufficient future returns are unavailable:

- The final 5 observations have unavailable 5-day targets.
- The final 21 observations have unavailable 21-day targets.

The documented TMPV corporate-action exclusion also makes affected forward target windows unavailable.

Target values are stored as decimal volatility, not percentages.

## 4. Features and Leakage Prevention

### 4.1 Stock-Level Features

The stock-level feature dataset contains 12 features.

**Lagged daily returns:**

- `Return_Lag_1`
- `Return_Lag_2`
- `Return_Lag_5`
- `Return_Lag_10`
- `Return_Lag_21`

**Historical volatility:**

- `Hist_Vol_5D`
- `Hist_Vol_21D`
- `Hist_Vol_63D`

Historical volatility is calculated using rolling standard deviation of previous daily returns, annualized by \(\sqrt{252}\). The rolling calculations exclude the current day's return.

**Volume-based features:**

- `Volume_Change_1D`
- `Volume_MA_Ratio_5D`
- `Volume_MA_Ratio_21D`

Volume moving-average benchmarks use previous trading sessions. Current-session volume is available at the forecast origin, which is the Indian market close.

**Price-range feature:**

- `Daily_Range`

Calculated as:

\[
Daily\_Range_t =
\frac{High_t-Low_t}{Close_{t-1}}
\]

Current-session high and low are available at the forecast origin.

### 4.2 Market and Macroeconomic Features

The shared market/macro feature dataset contains seven features:

| Feature | Source | Calculation or purpose |
|---|---|---|
| `NIFTY_Return` | NIFTY 50 | Daily log return |
| `NIFTY_Hist_Vol_21D` | NIFTY 50 | 21-session annualized historical volatility |
| `INDIA_VIX_Level` | India VIX | Current implied-volatility level |
| `INDIA_VIX_Change` | India VIX | Daily percentage change |
| `USD_INR_Return` | USD/INR | Daily log return |
| `BRENT_CRUDE_Return` | Brent crude | Daily log return |
| `US_10Y_YIELD_Change` | US 10Y yield | Daily absolute change in yield |

The market/macro features are stored separately and joined to individual stock features by date.

Macroeconomic source-date metadata is retained for auditing and is not used as a model predictor.

Global market variables are already aligned according to the Stage 1 information-availability policy. They must not be shifted a second time.

### 4.3 Forecast Origin and Information Availability

The forecast origin is the close of the Indian trading session on date \(t\).

Features may use information available by that close:

- Historical stock returns and volatility.
- Current-session volume and price range.
- Current-session NIFTY return and India VIX.
- Lag-aligned global market and macroeconomic observations.

The target begins on the next trading session.

### 4.4 Leakage Prevention

- No future prices, returns or macroeconomic observations may enter features.
- Target windows must begin after the prediction date.
- Rolling features must use only information available at the forecast origin.
- Target columns must never be included among model predictors.
- Feature and target dates must be aligned.
- All dates must remain chronological.
- Learned preprocessing transformations must be fitted using training data only.
- Missing values must not be filled using future observations or statistics calculated from validation or locked-test data.

Structural feature and target alignment checks must pass before model training.

## 5. Models

### 5.1 Statistical Baselines

The following established volatility forecasting approaches will be implemented:

1. **Naive / Last-observation baseline:** Uses the most recently available volatility estimate as the forecast.
2. **EWMA:** Exponentially weighted moving-average volatility forecast.
3. **HAR:** Heterogeneous Autoregressive model using daily, weekly and monthly volatility components.
4. **GARCH(1,1):** Generalized Autoregressive Conditional Heteroskedasticity model with one ARCH and one GARCH term.

Each baseline must be evaluated for both forecast horizons.

The exact implementation, estimation windows, parameter choices and forecast conversion methods must be documented.

### 5.2 Machine-Learning Models

- Ridge Regression.
- LightGBM.

Machine-learning models will use the engineered stock-level and market/macro features.

Tune models using training folds only. Compare ML models with the statistical baselines on the validation period.

Freeze the selected model and all associated decisions before evaluating the locked test period.

No machine-learning model should be introduced before baseline results have been established.

## 6. Validation Strategy

### 6.1 Chronological Data Coverage

The final usable target coverage across the 50 stocks is:

| Target | First valid date | Last valid date | Observations per stock |
|---|---|---|---:|
| 5-day volatility | 2010-01-04 | 2026-10-30 | 4,154 |
| 21-day volatility | 2010-01-04 | 2026-10-07 | 4,138 |

For comparable evaluation across horizons, the common final date is fixed at **2026-10-07**.

The common reference date index contains 4,117 observations.

### 6.2 Chronological Train, Validation and Locked-Test Splits

The following boundaries are fixed before model training.

| Period | 5-Day Forecast | 21-Day Forecast |
|---|---|---|
| Training | 2010-01-04 to 2021-09-28 | 2010-01-04 to 2021-09-03 |
| Train-validation gap | 2021-09-29 to 2021-10-05 | 2021-09-06 to 2021-10-05 |
| Validation | 2021-10-06 to 2024-03-28 | 2021-10-06 to 2024-03-04 |
| Validation-test gap | 2024-04-01 to 2024-04-05 | 2024-03-05 to 2024-04-05 |
| Locked test | 2024-04-08 to 2026-10-07 | 2024-04-08 to 2026-10-07 |

The gaps contain exactly the relevant forecast horizon in trading observations.

The locked-test period is identical for both forecast horizons.

### 6.3 Walk-Forward Validation

Use five expanding-window walk-forward folds for each forecast horizon.

Each fold:

- Trains on all eligible historical observations available before its validation period.
- Uses an expanding training window.
- Excludes observations immediately before validation whose forward target windows would overlap the validation period.
- Maintains a gap equal to the forecast horizon.
- Predicts the next chronological validation block.

The five validation blocks are consecutive, non-overlapping and cover the entire validation period.

#### 5-Day Walk-Forward Folds

| Fold | Train Start | Train End | Gap Start | Gap End | Validation Start | Validation End | Train Obs. | Gap Obs. | Validation Obs. |
|---:|---|---|---|---|---|---|---:|---:|---:|
| 1 | 2010-01-04 | 2021-09-28 | 2021-09-29 | 2021-10-05 | 2021-10-06 | 2022-04-04 | 2,876 | 5 | 123 |
| 2 | 2010-01-04 | 2022-03-28 | 2022-03-29 | 2022-04-04 | 2022-04-05 | 2022-09-30 | 2,999 | 5 | 123 |
| 3 | 2010-01-04 | 2022-09-23 | 2022-09-26 | 2022-09-30 | 2022-10-03 | 2023-03-29 | 3,122 | 5 | 123 |
| 4 | 2010-01-04 | 2023-03-22 | 2023-03-23 | 2023-03-29 | 2023-03-31 | 2023-09-27 | 3,245 | 5 | 122 |
| 5 | 2010-01-04 | 2023-09-20 | 2023-09-21 | 2023-09-27 | 2023-09-28 | 2024-03-28 | 3,367 | 5 | 122 |

Total validation observations: 613.

#### 21-Day Walk-Forward Folds

| Fold | Train Start | Train End | Gap Start | Gap End | Validation Start | Validation End | Train Obs. | Gap Obs. | Validation Obs. |
|---:|---|---|---|---|---|---|---:|---:|---:|
| 1 | 2010-01-04 | 2021-09-03 | 2021-09-06 | 2021-10-05 | 2021-10-06 | 2022-03-30 | 2,860 | 21 | 120 |
| 2 | 2010-01-04 | 2022-02-25 | 2022-02-28 | 2022-03-30 | 2022-03-31 | 2022-09-22 | 2,980 | 21 | 120 |
| 3 | 2010-01-04 | 2022-08-23 | 2022-08-24 | 2022-09-22 | 2022-09-23 | 2023-03-15 | 3,100 | 21 | 119 |
| 4 | 2010-01-04 | 2023-02-13 | 2023-02-14 | 2023-03-15 | 2023-03-16 | 2023-09-07 | 3,219 | 21 | 119 |
| 5 | 2010-01-04 | 2023-08-08 | 2023-08-09 | 2023-09-07 | 2023-09-08 | 2024-03-04 | 3,338 | 21 | 119 |

Total validation observations: 597.

### 6.4 Validation Rules

- Preserve chronological ordering throughout model development.
- Do not use random train-test splitting.
- Maintain horizon-specific gaps to prevent overlapping target windows across partition boundaries.
- Use validation results for baseline comparison and model selection.
- Fit preprocessing transformations using training data only.
- Do not use locked-test results for feature selection, parameter tuning or model selection.

### 6.5 Locked-Test Policy

The locked-test period must remain untouched during model development.

After model selection and all development decisions are frozen:

1. Fit the final selected model using eligible training and validation observations.
2. Exclude the horizon-specific gap immediately before the locked-test period.
3. Generate predictions for the locked-test period.
4. Evaluate the final model once on the locked-test period.
5. Report the results without further tuning or model selection.

The locked test must not be evaluated repeatedly to guide development decisions.

## 7. Evaluation

### 7.1 Primary Metrics

Evaluate both forecast horizons using:

- RMSE on log-volatility.
- QLIKE loss.

For log-volatility RMSE, compare:

\[
\ln(\widehat{RV}_{t,h})
\quad \text{against} \quad
\ln(RV_{t,h})
\]

For QLIKE, use a clearly documented implementation consistent across all models and horizons.

### 7.2 Model Comparison

Report:

- Walk-forward validation performance.
- Locked-test performance.
- Baseline leaderboard.
- Model performance separately for 5-day and 21-day forecasts.
- Calm versus stressed market performance.

Do not claim machine-learning superiority unless actual measured results support it.

### 7.3 Statistical Comparison

Conduct one Diebold-Mariano test comparing the selected model against the best baseline.

- Define the loss differential explicitly.
- Account for serial dependence in forecast errors, particularly because forward target windows overlap.
- Document the test specification and interpretation.
- Do not use the locked test to choose which model to compare.

## 8. Portfolio Risk Analysis

### 8.1 Value at Risk

Convert volatility forecasts into loss quantiles (VaR).

Evaluate:

- VaR breach rates.
- Kupiec unconditional coverage tests.
- Forecast performance relative to GARCH and historical simulation.

Document the assumptions used to convert volatility forecasts into loss distributions and quantiles.

### 8.2 Portfolio Construction

Construct a fixed-rule equal-weight portfolio.

Compare:

- Sample covariance.
- Ledoit-Wolf covariance estimation.

Calculate portfolio VaR and individual stock risk contributions.

Verify that individual risk contributions sum to total portfolio risk, subject to the documented risk-contribution methodology.

### 8.3 Historical Stress Analysis

Replay two or three historical stress periods.

Evaluate:

- Forecast behavior before, during and after each stress period.
- Whether forecasts under-react, over-react or lag market conditions.
- Portfolio risk and individual stock contributions.
- Differences between volatility forecasts and realized outcomes.

Document the scenarios, dates, assumptions and results.

## 9. Reproducibility and Reporting

- Raw data must remain unchanged.
- Data cleaning must be reproducible through one command.
- Automated data and model tests must pass.
- Feature and target generation must be reproducible.
- Record random seeds and model configurations where applicable.
- Preserve experiment results and model artifacts.
- Provide a simple command or API returning a forecast for a ticker.
- Document methodology, results, unsuccessful approaches and limitations.
- Report actual measured results; do not claim ML superiority if baselines perform better.

## 10. Research Safeguards

The following rules are mandatory:

1. Commit this protocol before modeling.
2. Fix the constituent universe and chronological split before model training.
3. Preserve raw data and document all cleaning decisions.
4. Do not introduce future information into features or preprocessing.
5. Tune models using training folds only.
6. Use validation results for model selection.
7. Never use locked-test results to tune or select models.
8. Evaluate the locked test exactly once after all development decisions are frozen.
9. Document any protocol amendments with the reason, date and impact.
10. Report unsuccessful experiments and limitations transparently.

**Research principle:** The objective is to determine whether the models provide measurable forecasting and risk-management value, not to demonstrate that machine learning must outperform statistical baselines.