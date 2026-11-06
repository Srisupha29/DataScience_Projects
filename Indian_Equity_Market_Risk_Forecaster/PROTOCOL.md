# Research Protocol: Indian Large-Cap Volatility and Risk Predictor

## 1. Research question

Can statistical and machine-learning models improve forecasts of short-term volatility for Indian large-cap equities compared with established volatility forecasting baselines?

The project forecasts 5-trading-day and 21-trading-day forward volatility. It evaluates forecast accuracy and the usefulness of forecasts for portfolio risk measurement.

## 2. Universe and data

- **Equity universe:** NIFTY 50 constituents, fixed using one documented start-date constituent list.
- **Stock data:** Daily OHLCV prices from Yahoo Finance (`.NS` tickers).
- **Market and macro data:** NIFTY index, India VIX, USD/INR, Brent crude and US Treasury yields.
- **Data limitation:** Yahoo Finance is an unofficial data source. The fixed constituent universe introduces survivorship bias; this limitation will be disclosed.
- Preserve downloaded raw data unchanged. Record all cleaning decisions and corrections.
- Align global market variables to information actually available at the Indian market close. Apply appropriate lags to prevent look-ahead bias.

## 3. Forecast targets

Use daily close-to-close log returns:

\[
r_t = \ln(P_t/P_{t-1})
\]

Define forward realized-volatility proxies for horizon \(h\):

\[
RV_{t,h} =
\sqrt{\frac{252}{h}\sum_{j=1}^{h}r_{t+j}^{2}}
\]

where \(h \in \{5,21\}\).

These are close-to-close volatility proxies, not true intraday realized volatility.

## 4. Features and validation

Features will use only information available at the forecast origin:

- Lagged returns and volatility
- Trading volume and price range
- Market-level indicators
- Lagged macroeconomic variables

Test all features for look-ahead leakage.

Use chronological training, validation and locked-test periods. Final date boundaries will be determined from available data coverage and fixed before model training. Use walk-forward validation with a gap equal to the forecast horizon.

## 5. Models

**Baselines**
- Last observed volatility
- Exponentially weighted moving average (EWMA)
- Heterogeneous autoregressive (HAR) model
- GARCH(1,1)

**Machine learning**
- Ridge Regression
- LightGBM

Tune models using training folds only. Compare ML models with the baselines on the validation period. Freeze the selected model before evaluating the locked test period.

## 6. Evaluation

Primary metrics:
- RMSE on log-volatility
- QLIKE loss

Report validation and locked-test performance. Conduct one Diebold–Mariano test comparing the selected model against the best baseline. Also report performance during calm and stressed market periods.

The locked test period must be evaluated exactly once.

## 7. Portfolio risk analysis

- Convert volatility forecasts into loss quantiles (VaR).
- Evaluate VaR breach rates and Kupiec tests.
- Compare against GARCH and historical simulation.
- Construct a fixed-rule equal-weight portfolio.
- Compare sample covariance with Ledoit–Wolf covariance.
- Calculate portfolio VaR and individual stock risk contributions. Verify that contributions sum to total portfolio risk.
- Replay two or three historical stress periods and document forecast behavior.

## 8. Reproducibility and reporting

- Raw data must remain unchanged.
- Data cleaning must be reproducible through one command.
- Automated data and model tests must pass.
- Provide a simple command or API returning a forecast for a ticker.
- Document methodology, results, unsuccessful approaches and limitations.
- Report actual measured results; do not claim ML superiority if baselines perform better.

**Research safeguards:** Commit this protocol before modeling. Fix the universe and chronological split before model training. Never use locked-test results to tune or select models.