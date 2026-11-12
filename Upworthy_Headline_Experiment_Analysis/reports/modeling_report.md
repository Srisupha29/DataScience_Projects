## Machine Learning and NLP Modeling Report

**Project phase:** Phase 2.4 — ML Modeling  
**Status:** Modeling complete for the agreed scope  
**Primary tools:** Python, pandas, scikit-learn, sentence-transformers, XGBoost  
**Evaluation:** Five-fold experiment-grouped cross-validation

---

## 1. Objective

The objective was to evaluate whether headline text representations and linguistic features could predict which headline performed better relative to other headline variants within the same experiment.

The task was framed as within-experiment headline ranking rather than general CTR prediction. This accounts for differences between experiments in audiences, topics, exposure levels, and underlying CTRs.

The project evaluated engineered linguistic features, TF-IDF representations, conventional classifiers, pairwise models, and pretrained sentence embeddings.

## 2. Dataset and Eligibility

The source dataset contained **22,666 package-level rows across 4,873 experiments**.

The analysis applied structural eligibility rules requiring at least two distinct normalized headlines and one shared, non-missing image ID per experiment. A further comparability audit excluded **165 experiments** with repeated stimulus identities that had changing impression or click counts.

The resulting modeling dataset contained:

- **9,778 headline-variant rows**
- **2,136 eligible experiments**
- Headline text for NLP feature construction
- Six engineered binary headline features

These rules operationalize a headline-only comparison using recorded headline and image identifiers. They do not prove that every other experimental condition remained constant.

### Final pairwise evaluation subset

The final pairwise evaluation included **2,130 experiments**. Six eligible experiments had no comparable pairs after applying the minimum relative-CTR difference threshold of `0.0005`.

A total of **17,270 comparable headline pairs** contributed to the final evaluation.

## 3. Target Construction

For each headline, the target was based on its CTR relative to the pooled CTR of the other retained variants in the same experiment.

\[
\text{CTR}_i = \frac{\text{clicks}_i}{\text{impressions}_i}
\]

\[
\text{Relative CTR}_i =
\text{CTR}_i - \text{CTR}_{\text{other variants}}
\]

The binary target was defined as:

- `1`: The headline's relative CTR was positive.
- `0`: The headline's relative CTR was zero or negative.

The target distribution was:

| Target | Rows |
|---|---:|
| 0 | 5,120 |
| 1 | 4,658 |
| **Total** | **9,778** |

Clicks, impressions, CTR values, target values, and other outcome-derived fields were not intended to be predictive inputs.

The pairwise task compared two headlines within the same experiment and assessed whether the model ranked the headline with the larger observed relative CTR higher. Pairs with an absolute relative-CTR difference below `0.0005` were excluded from pairwise training/evaluation as specified by the relevant workflow. This threshold is a modeling choice, not a statistical-significance threshold, and it changes the population of pairs being evaluated.

## 4. Feature Engineering and NLP

### 4.1 Engineered headline features

The project created six binary linguistic features:

1. Question mark
2. Exclamation mark
3. Number
4. You-family / second-person pronoun
5. First-person pronoun
6. Third-person pronoun

These features capture selected surface-level headline characteristics. Earlier feature exploration also considered numeric characteristics such as character count, word count, average word length, punctuation counts, and uppercase ratio; the final feature configuration should be described according to the specific model pipeline being discussed.

### 4.2 TF-IDF

The initial validated TF-IDF representation used a vocabulary of up to **5,000 terms**. Combined with the six binary features, the validated feature matrix contained **9,778 rows and 5,006 columns**.

TF-IDF provides a sparse lexical representation, while the engineered features represent selected headline structures. Some earlier pairwise-model experiments used a different TF-IDF configuration; the 5,006-column figure refers to the validated initial feature matrix and should not be taken as the configuration for every later candidate.

### 4.3 Sentence embeddings

Two pretrained Sentence Transformer models were evaluated:

- `sentence-transformers/all-MiniLM-L6-v2` — 384-dimensional embeddings
- `sentence-transformers/all-mpnet-base-v2` — 768-dimensional embeddings

The embedding workflow centered headline embeddings relative to the experiment mean and applied dimensionality reduction within training folds. MPNet was retained because its pairwise accuracy exceeded MiniLM by more than the project's 0.5-percentage-point stopping threshold.

The transformer models were used as pretrained feature extractors; they were not fine-tuned on this dataset.

## 5. Validation Strategy and Leakage Controls

The modeling workflow used five-fold `StratifiedGroupKFold` cross-validation with shuffling and random seed `42`.

Experiment IDs were used as groups so variants from the same experiment would not appear in both training and validation folds. This is important because the target is defined relative to other variants within an experiment.

The pairwise workflow constructed comparisons between variants from the same training experiment. Training-fold preprocessing and dimensionality reduction were fitted within the training folds. The intended leakage controls excluded target and outcome-derived fields from predictive inputs.

The final candidate was selected after comparing multiple models on the same cross-validation folds. The resulting estimate may therefore be optimistic due to model-selection bias. There was no independent final test set.

## 6. Baseline Model Comparison

Initial five-fold grouped cross-validation results were:

| Model | ROC-AUC | Mean experiment-level pairwise accuracy |
|---|---:|---:|
| Logistic regression | 0.5694 | 56.21% |
| Gradient boosting | 0.5393 | 54.58% |
| Tuned gradient boosting | 0.5443 | 54.96% |
| XGBoost classifier | 0.5620 | 55.54% |

In the later evaluation used for the final paired comparison, the original weighted pairwise logistic baseline achieved **57.8330%** mean experiment-level pairwise accuracy and ROC-AUC of **0.5755**.

The initial pointwise-model results and later pairwise-baseline results come from different modeling/evaluation stages. The matched comparison in the next section is the relevant comparison for the selected candidate.

## 7. Final Model: MPNet-Enhanced Pairwise Logistic Regression

The selected candidate was a pairwise logistic regression model incorporating `sentence-transformers/all-mpnet-base-v2` embeddings alongside the headline feature representations. Embeddings were centered relative to the experiment mean, and dimensionality reduction was performed within each training fold.

The final comparison evaluated the baseline and MPNet candidate on the same experiment-level evaluation subset using the same pairwise-accuracy definition.

| Metric | Original pairwise logistic baseline | MPNet-enhanced pairwise logistic |
|---|---:|---:|
| Mean experiment-level pairwise accuracy | 57.8330% | 61.5292% |
| Evaluation experiments | 2,130 | 2,130 |
| Comparable pairs | 17,270 | 17,270 |

The observed improvement was **3.6963 percentage points**, approximately **3.70 percentage points**.

This result measures how often the model correctly ranks comparable headline pairs under the defined evaluation procedure. It does **not** mean CTR increased by 3.70%, and it does not establish a real-world improvement in click-through rate.

## 8. Paired Bootstrap Comparison

A paired bootstrap resampled experiment IDs **10,000 times** using random seed `20261023`. Baseline and MPNet predictions were compared on the same resampled experiments.

| Statistic | Result |
|---|---:|
| Baseline mean experiment-level pairwise accuracy | 57.8330% |
| MPNet mean experiment-level pairwise accuracy | 61.5292% |
| Observed improvement | +3.6963 percentage points |
| 95% bootstrap confidence interval | +2.6666 to +4.7310 percentage points |
| Bootstrap resamples | 10,000 |
| Random seed | `20261023` |

The confidence interval excludes zero, supporting an improvement under this experiment-level bootstrap procedure.

The script also reported an approximate bootstrap tail estimate rounded to `0.0000`. This is not an exact p-value and should not be reported as a probability of exactly zero.

The interval quantifies sampling uncertainty conditional on the available predictions. It does not correct for model-selection bias or establish expected performance on future experiments.

## 9. Interpretation

In the current evaluation, pairwise ranking with pretrained MPNet sentence embeddings performed better than the original pairwise logistic baseline for ranking comparable headline pairs within experiments.

The project demonstrates the application of:

- Linguistic feature engineering
- Sparse lexical text representations with TF-IDF
- Pretrained semantic sentence embeddings
- Pairwise logistic modeling
- Experiment-grouped cross-validation
- Experiment-level paired bootstrap comparison

The result is evidence of predictive ranking performance on this dataset and evaluation setup. It is not evidence that a headline feature or model recommendation causes higher CTR, nor that the same performance will generalize to other publishers, topics, or future experiments.

## 10. Limitations

1. **Model-selection bias:** Multiple candidates were compared on the same cross-validation folds used to report performance, so the selected model's estimate may be optimistic.
2. **No independent final test set:** The reported result is not an independent holdout estimate.
3. **Noisy observed outcomes:** Relative CTR is estimated from finite impressions and clicks; observed rankings may not reflect underlying expected performance.
4. **Thresholded pair evaluation:** Excluding pairs with relative-CTR differences below `0.0005` means the reported accuracy applies to the remaining comparable pairs, not every possible pair.
5. **Eligibility limitations:** Recorded headline and image identifiers cannot guarantee that every other package characteristic remained constant.
6. **Generalization:** The evaluation does not establish performance on future experiments, other publishers, or different editorial settings.
7. **No causal claim:** Predicting observed headline rankings does not establish that the model will cause an increase in CTR.
8. **Pretrained embeddings:** The transformer models were used as pretrained feature extractors rather than fine-tuned.
9. **Interpretability:** The final ranking result does not by itself identify which words or linguistic features drive performance.

## 11. Final Conclusion

Phase 2.4 modeling is complete for the agreed scope. The selected MPNet-enhanced pairwise logistic model achieved **61.53% mean experiment-level pairwise accuracy**, compared with **57.83%** for the original pairwise baseline—an observed improvement of **3.70 percentage points**.

The paired experiment-level bootstrap confidence interval was **+2.67 to +4.73 percentage points** across 10,000 resamples.

Because the model was selected using the same cross-validation folds, this should be presented as a promising cross-validated estimate rather than an unbiased estimate of future performance. Independent validation would be required to establish generalization more conclusively.