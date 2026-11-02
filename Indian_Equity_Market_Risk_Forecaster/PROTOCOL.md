# Indian Equity Market Risk Forecaster
## Research Protocol

**Protocol version:** 1.0  
**Status:** Draft — to be reviewed and frozen before modeling  
**Market:** India  
**Exchange:** National Stock Exchange of India (NSE)  
**Primary universe:** NIFTY 50 constituents  
**Initial data source:** yfinance  

---

## 1. Research Purpose

This project investigates whether machine learning models can improve short-horizon equity volatility forecasts relative to established statistical and econometric benchmarks.

The project will evaluate whether forecast improvements translate into more reliable estimates of portfolio risk, including Value at Risk (VaR), Expected Shortfall (ES), and stress losses.

The work will also examine forecast calibration, model stability, explainability, operational monitoring, and the limitations of the data and modeling assumptions.

This is an independent research and engineering project. It is not an investment recommendation, trading signal, or claim of production deployment at a financial institution.

## 2. Research Questions

The primary research question is:

**Can machine learning improve 5-trading-day and 21-trading-day volatility forecasts for liquid Indian equities compared with naive, EWMA, HAR, and GARCH benchmarks?**

Secondary questions:

1. Do machine learning models improve forecast accuracy across calm and stressed market regimes?
2. Are probabilistic volatility forecasts adequately calibrated?
3. Do improved volatility forecasts produce more reliable portfolio risk estimates?
4. How sensitive are portfolio risk estimates to covariance estimation methods?
5. How do the models behave during historical and hypothetical stress scenarios?
6. Are forecast improvements sufficiently robust to justify additional model complexity?
7. Can the forecasting and monitoring workflow be reproduced and operated reliably?

## 3. Market and Investment Universe

### 3.1 Market

- Country: India
- Exchange: NSE
- Primary index: NIFTY 50 price index
- Primary stock universe: NIFTY 50 constituents

### 3.2 Stock selection

The project will investigate historical NIFTY 50 constituent membership.

Preferred approach:
- Use historical constituent membership where reliable data is available.
- Apply membership rules using information available at the relevant historical date.
- Document constituent entry, removal, ticker changes, and delistings.

Fallback approach:
- If reliable historical membership data is unavailable, use a frozen list of NIFTY 50 constituents obtained at the documented universe-selection date.
- Explicitly disclose survivorship bias.
- Do not present results from this fallback universe as an unbiased historical representation of the NIFTY 50.

The final universe-selection date, constituent list, eligibility rules, and data coverage will be recorded after the Phase 1 data audit and before modeling.

### 3.3 Eligibility

A stock must satisfy documented data-coverage and data-quality requirements.

The audit will examine:
- Available historical observations
- Missing trading sessions
- Duplicate dates
- Stale prices
- Zero or abnormal trading volume
- Corporate actions
- Ticker changes and delistings
- Liquidity and trading-history requirements

Eligibility thresholds must be fixed before model evaluation. Any exclusions must be recorded with reasons.

### 3.4 Index distinction

The NIFTY 50 price index and a total-return index are not interchangeable.

The project will identify which index series is used and document whether dividends are included. Equity price-return analysis must not be described as total-return analysis.

## 4. Data Sources and Data Governance

### 4.1 Initial source

Yahoo Finance data will be accessed through yfinance.

Candidate instruments include:

| Data | Candidate Yahoo Finance symbol |
|---|---|
| NIFTY 50 | `^NSEI` |
| India VIX | `^INDIAVIX` |
| USD/INR | `INR=X` or another verified symbol |
| US VIX | `^VIX` |
| Crude oil | `CL=F` or another verified series |
| US Treasury yield | `^TNX` or another verified series |

These are candidates, not confirmed data sources. Availability, coverage, units, and meaning must be validated before use.

### 4.2 Data handling

- Preserve downloaded source data in the raw-data layer.
- Never silently overwrite original raw downloads.
- Record retrieval timestamps, source identifiers, ticker symbols, and download parameters.
- Store cleaned and transformed data separately.
- Use Parquet for analytical datasets.
- Use DuckDB for local analytical queries where appropriate.
- Document any manual corrections and exclusions.

### 4.3 Price adjustments

The download process must explicitly specify the yfinance adjustment behavior.

The project will examine:
- Split-adjusted prices
- Dividend adjustments
- Adjusted versus unadjusted close
- OHLC consistency
- Corporate-action effects

The chosen price series and its interpretation must be documented. The project must not assume that yfinance's default adjustment behavior is constant across package versions.

### 4.4 Data-quality checks

Automated checks will cover:
- Duplicate observations
- Missing values
- Invalid or non-positive prices
- Abnormal returns
- Zero-volume observations
- Stale prices
- Missing trading sessions
- Unexpected date ranges
- Time-zone and date alignment
- Inconsistent OHLC values
- Incorrect ticker or instrument mappings

### 4.5 Data limitations

yfinance is an unofficial source and may have incomplete or revised historical data. Its use does not imply an official NSE data license.

Data limitations, availability gaps, corporate-action handling, and any licensing or redistribution restrictions must be documented.

## 5. Trading Calendar and Information Timing

The project will use the Indian exchange trading calendar for Indian equity observations.

Calendar handling must distinguish:
- Trading sessions
- Exchange holidays
- Missing observations
- Non-trading days
- Global-market sessions

Global variables must be aligned to the information actually available at the Indian market forecast cutoff.

In particular:
- US market closing values must not be treated as known at an earlier Indian market close.
- Global features must be lagged according to their actual publication or observation times.
- USD/INR and commodity series must be aligned using documented timestamps.
- Every feature must have an explicit information cutoff.

A feature-leakage audit must verify that no feature uses information published after the forecast timestamp.

## 6. Forecast Targets

### 6.1 Horizons

The forecasting horizons are:
- 5 Indian trading days
- 21 Indian trading days

### 6.2 Primary volatility target

The primary target will be forward close-to-close realized volatility calculated from daily adjusted-price log returns.

Let:

r(t) = ln(P(t) / P(t-1))

For horizon h:

RV(t,h) = sqrt((252/h) * sum(r(t+j)^2)), for j = 1,...,h

where:
- P(t) is the selected adjusted closing price.
- h is 5 or 21 trading days.
- 252 is the annualization convention.

This is a daily-return-based volatility proxy. It is not intraday realized volatility.

The implementation must ensure that the target uses only returns occurring after the forecast timestamp.

### 6.3 Target integrity

- Target windows must not extend into the feature observation period.
- Training labels must not overlap validation or test information in a way that creates leakage.
- An embargo of at least the forecast horizon will be applied where necessary.
- Five-day and 21-day targets will be evaluated separately.
- Target construction will be tested with synthetic examples and explicit date checks.

## 7. Features

Candidate features include:

### 7.1 Stock-level features
- Lagged returns
- Lagged volatility
- Rolling volatility
- Drawdowns
- High-low range measures
- Volume changes
- Rolling volume z-scores
- Price gaps where available

### 7.2 Market-level features
- NIFTY 50 returns and volatility
- India VIX changes and levels, if validated
- Market drawdowns
- Sector or market breadth features where reliable data is available

### 7.3 Global and macro features
- US VIX
- USD/INR changes
- Crude oil changes
- US Treasury yield changes

All external features must be lagged to the Indian market information cutoff.

### 7.4 Calendar and event features
- Day-of-week indicators
- Month and quarter indicators
- Documented market-event indicators where reliable data exists

Features must be defined before the locked test is evaluated. Feature selection must use training data only.

## 8. Data Splitting and Validation

### 8.1 Chronological design

Random train-test splitting is prohibited for the primary forecasting evaluation.

The project will use:
- Development data for feature and model development
- Expanding walk-forward validation for model selection
- A final chronological locked test period
- A forward-testing period after model freeze

The exact calendar cutoffs will be determined after the Phase 1 coverage audit using a documented chronological split rule. The cutoffs must be recorded before model training and locked before final evaluation.

### 8.2 Walk-forward validation

- Training windows expand chronologically.
- Validation observations occur strictly after their training observations.
- An embargo of at least the forecast horizon is applied where needed.
- Hyperparameter tuning occurs only within training/validation data.
- The same fold definitions are used for comparable models.

### 8.3 Locked test

The locked test period must not be used for:
- Feature selection
- Hyperparameter tuning
- Model selection
- Threshold selection
- Repeated experimentation

It will be evaluated after the model and protocol are frozen.

Any change that uses locked-test results to modify the model invalidates the original locked-test claim. A new evaluation period or explicitly labeled exploratory analysis would then be required.

## 9. Benchmark Models

The following benchmarks will be implemented:

1. Naive forecast
2. Exponentially Weighted Moving Average (EWMA)
3. Heterogeneous Autoregressive (HAR) volatility model
4. GARCH(1,1)

Each benchmark must use information available at the forecast timestamp.

The assumptions, estimation windows, refitting frequency, and forecast construction must be documented.

## 10. Machine Learning Models

The planned challenger models are:

- Ridge Regression
- Random Forest
- LightGBM
- XGBoost

The project may evaluate:
- Per-stock models
- Pooled models across stocks

Pooled-model complexity may be reduced if compute or time becomes a constraint.

Hyperparameter optimization may use Optuna, but only inside development training folds.

Experiment configurations, parameters, metrics, and artifacts should be recorded using MLflow.

No model may be selected using locked-test performance.

## 11. Forecast Evaluation

### 11.1 Primary metrics

- RMSE on log volatility
- QLIKE
- MAE where informative

The precise treatment of zero or near-zero volatility values must be documented.

### 11.2 Evaluation dimensions

Results will be reported:
- Separately for 5-day and 21-day horizons
- Across individual stocks where sample sizes permit
- Across the pooled universe
- Across calm and stressed regimes

Regime definitions must be determined without using future information and documented before final evaluation.

### 11.3 Statistical comparison

Forecast comparisons will include the Diebold-Mariano (DM) test where appropriate.

Because multi-day forecast errors may overlap, the variance estimator must account for serial dependence and overlapping horizons.

Statistical significance must not be confused with economic significance.

## 12. Probabilistic Forecasts and Calibration

The project will evaluate:
- Quantile forecasts
- Conformal calibration
- Pinball loss
- Empirical interval coverage
- Forecast calibration across market regimes

Where appropriate, standardized forecast residuals will be used to construct VaR and ES estimates.

Calibration must be evaluated out of sample. Calibration procedures must not use locked-test outcomes to adjust the model.

## 13. Portfolio Construction and Risk

### 13.1 Portfolio examples

The planned portfolios are:
- Equal-weight portfolio
- Inverse-volatility portfolio
- Sector-tilted portfolio

Portfolio weights must be calculated using information available at the portfolio formation date.

### 13.2 Covariance estimation

The project will compare:
- Sample covariance
- Ledoit-Wolf shrinkage covariance
- EWMA covariance
- Hybrid approaches combining forecast volatility and shrunk correlation estimates

Evaluation will include:
- Out-of-sample predicted versus realized portfolio variance
- Realized volatility of minimum-variance portfolios
- Covariance condition numbers
- Eigenvalue checks
- Positive-semidefinite validation

### 13.3 Portfolio risk measures

The project will calculate:
- Parametric VaR using normal assumptions
- Parametric VaR using Student-t assumptions
- Historical Simulation VaR
- Filtered Historical Simulation VaR
- Expected Shortfall
- Marginal VaR
- Component VaR
- Variance contribution
- Diversification ratio
- Effective number of bets

Component contributions must reconcile to total portfolio risk within documented numerical tolerance.

### 13.4 Backtesting

Portfolio risk estimates will be evaluated out of sample.

The project will use:
- Kupiec unconditional coverage test
- Christoffersen independence and conditional coverage tests
- Basel traffic-light interpretation where applicable

Limitations due to sample size, overlapping horizons, and test assumptions must be stated.

## 14. Stress Testing

### 14.1 Historical stress periods

The project will examine:
- March 2020 market stress
- A documented interest-rate repricing period

Historical scenario dates and data availability must be recorded.

### 14.2 Hypothetical scenarios

The planned scenarios include:
- Sharp NIFTY 50 market decline
- Material increase in volatility
- USD/INR depreciation shock
- Crude oil price shock
- Correlations moving toward one

Scenario magnitudes and implementation assumptions must be specified and frozen before final stress evaluation.

### 14.3 Reverse stress testing

The project will identify combinations of market and risk-factor shocks that produce a predefined material portfolio loss.

Scenario results must include:
- Portfolio loss
- VaR and ES comparison
- Main risk contributors
- Forecast lag or overshoot
- Recovery behavior
- Key assumptions and limitations

Stress tests are hypothetical or historical analytical exercises, not predictions.

## 15. Economic Value Analysis

A volatility-targeting strategy will be compared with:
- Buy-and-hold
- Equal-weight portfolio

The evaluation will include:
- Transaction costs
- Sharpe ratio
- Sortino ratio
- Maximum drawdown
- Turnover
- Realized versus target volatility
- Bootstrap confidence intervals where appropriate

Transaction costs must be explicit assumptions rather than claims about actual investor costs. The base assumption and sensitivity analysis must be documented before the final comparison.

No locked-test tuning is permitted.

## 16. Explainability and Robustness

The project will use:
- SHAP where computationally appropriate
- Permutation importance
- Feature stability analysis
- Error analysis by market regime
- Error analysis by liquidity and sector where data permits
- Horizon-specific error analysis
- Sensitivity analysis

The report must identify where models fail, not only where they perform well.

Explainability results will be treated as model diagnostics, not proof of causal relationships.

## 17. Independent Model Validation

A separate validation report will be written from an independent-review perspective.

It will cover:
1. Purpose and scope
2. Data review
3. Conceptual soundness
4. Benchmark and challenger comparison
5. Forecast outcomes
6. Backtesting and statistical tests
7. Regime analysis
8. Sensitivity analysis
9. Stress testing
10. Assumptions and limitations
11. Findings and severity
12. Overall fitness-for-purpose conclusion

The validation report must distinguish implementation correctness, statistical performance, and suitability for a stated use.

## 18. Monitoring and Governance

The project will define monitoring triggers for:
- VaR backtesting exceptions
- Rolling forecast error relative to benchmarks
- Feature distribution drift
- Forecast calibration drift
- Missing or stale input data
- API and pipeline failures

Retraining and escalation rules must be documented.

The project will maintain:
- Model card
- Model inventory
- Model version log
- Experiment records
- Reproducibility instructions
- Known limitations and outstanding findings

## 19. Engineering and Deployment

The planned engineering components are:
- Python modular source code
- Automated tests using pytest
- FastAPI forecasting endpoints
- Docker packaging
- GitHub Actions workflow
- Scheduled daily forecast generation after the Indian market close
- Append-only forecast log
- Later joining of forecasts with realized outcomes
- Data-quality and drift checks

Tests must cover:
- Target and feature leakage
- Data schema
- Forecast output schema
- Covariance positive-semidefiniteness
- Risk contribution reconciliation
- API behavior
- Pipeline reproducibility

Deployment is a research demonstration and does not imply production-grade financial infrastructure.

## 20. Reproducibility and Experiment Integrity

The following rules are mandatory:

1. The research protocol must be committed before modeling code is written.
2. Raw data must be preserved separately from processed data.
3. Data retrieval timestamps and source identifiers must be recorded.
4. Random seeds must be fixed and documented where relevant.
5. Data splits and fold assignments must be reproducible.
6. Model configurations and results must be recorded.
7. Locked-test results must not guide model development.
8. Protocol amendments must be versioned, dated, and justified.
9. Negative or inconclusive findings must be reported.
10. All reported metrics must be reproducible from documented code and data.

## 21. Known Limitations

Expected limitations include:
- Unofficial historical data source
- Potential survivorship bias
- Historical constituent data availability
- Corporate-action and ticker-mapping issues
- Missing, stale, or revised market observations
- Non-synchronous global and Indian market observations
- Daily data rather than intraday data
- Volatility proxy rather than true intraday realized volatility
- Limited computational resources
- Simplified transaction-cost assumptions
- Historical relationships that may not persist

These limitations must be revisited as evidence becomes available.

## 22. Scope Control

If time or compute becomes constrained, reduce work in this order:

1. Pooled-model variants in Phase 4
2. Depth of explainability analysis in Phase 9
3. Economic-value analysis in Phase 8
4. Additional covariance estimators in Phase 6

Preserve the core work on:
- Benchmark and ML forecasting
- Out-of-sample evaluation
- Probabilistic forecasts and calibration
- Portfolio risk
- Independent validation
- Engineering and monitoring

Extensions such as pretrained time-series models, PyTorch sequence models, LLM-based news scoring, and fundamentals prediction are out of scope until the core project is complete.

## 23. Final Deliverables

The completed project should include:
- Reproducible data pipeline
- Validated forecasting targets and features
- Benchmark and ML model comparisons
- Probabilistic forecast evaluation
- Portfolio risk analysis
- VaR and ES backtesting
- Stress-testing analysis
- Explainability and robustness analysis
- Independent model validation report
- Model card and monitoring framework
- FastAPI and Docker demonstration
- Automated tests and CI
- Interactive dashboard
- Technical README
- Two-page executive research memo
- Summary of weekly market-literacy notes

## 24. Protocol Amendments

Every amendment must record:
- Amendment date
- Previous rule
- New rule
- Reason for change
- Whether any model results had already been observed
- Whether the locked test was affected

Changes made after observing results must be identified as exploratory and must not be presented as pre-registered decisions.

---

**Protocol status:** Draft.  
**Next action:** Review and freeze this protocol before writing modeling code.
