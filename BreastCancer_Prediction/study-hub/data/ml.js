window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "ml-bias-variance", area: "ml", title: "The bias-variance trade-off", mins: 30, level: 2, light: false,
    res: { label: "StatQuest: bias and variance", url: "https://www.youtube.com/results?search_query=statquest+bias+and+variance", src: "free" },
    aloud: "Explain overfitting and underfitting using training error and validation error, and name two ways to fix each.",
    interviewQ: "Your model has 98% training accuracy and 75% validation accuracy. What do you check and change first?",
    quiz: [
      { q: "A model has very low training error but high validation error. What is the likely problem?",
        options: ["High bias (underfitting)", "High variance (overfitting)", "Too much regularization", "The learning rate is zero"],
        answer: 1, why: "A large gap between training and validation performance is the classic sign of overfitting, which is high variance." },
      { q: "Which change would most likely reduce overfitting?",
        options: ["Adding many more features with no controls", "Increasing regularization strength", "Training on fewer examples", "Making the model more complex"],
        answer: 1, why: "Regularization limits model complexity. More data would also help, while fewer examples or more complexity make overfitting worse." },
      { q: "A model scores poorly on both the training and validation sets. What does this suggest?",
        options: ["High variance", "High bias (underfitting)", "Data leakage", "A perfect fit"],
        answer: 1, why: "If it cannot even fit the training data, the model is too simple or the features are not informative." }
    ]
  },
  {
    id: "ml-cv", area: "ml", title: "Cross-validation and data leakage", mins: 35, level: 3, light: false,
    res: { label: "scikit-learn: cross-validation guide", url: "https://scikit-learn.org/stable/modules/cross_validation.html", src: "free" },
    aloud: "Explain k-fold cross-validation and give one concrete example of data leakage.",
    interviewQ: "Your model scored 0.97 AUC in testing and 0.70 in production. List the possible causes, starting with leakage.",
    quiz: [
      { q: "Why use k-fold cross-validation instead of a single train/test split?",
        options: ["It trains faster", "It gives a more reliable estimate of how the model generalizes", "It removes the need for a test set", "It prevents overfitting by itself"],
        answer: 1, why: "Averaging over several splits reduces the dependence on one lucky or unlucky split." },
      { q: "Which is an example of data leakage?",
        options: ["Fitting a scaler on the whole dataset before splitting into train and test", "Fitting a scaler on the training set only", "Using a pipeline for preprocessing", "Holding out a final test set"],
        answer: 0, why: "Statistics from the test data leak into training. Fit preprocessing inside each training fold only." },
      { q: "You are predicting next month's sales from historical monthly data. Which validation is appropriate?",
        options: ["Shuffled k-fold", "Time-ordered splits where training data always comes before validation data", "Leave one random row out", "Train and test on the same period"],
        answer: 1, why: "With time-dependent data, shuffling lets the model train on the future to predict the past." }
    ]
  },
  {
    id: "ml-metrics", area: "ml", title: "Precision, recall and picking the right metric", mins: 30, level: 2, light: false,
    res: { label: "scikit-learn: classification metrics", url: "https://scikit-learn.org/stable/modules/model_evaluation.html", src: "free" },
    aloud: "Define precision and recall with a spam filter, and say when you would care more about each.",
    interviewQ: "Only 0.5% of transactions are fraud. Why is accuracy a poor metric, and what would you report instead?",
    quiz: [
      { q: "Only 0.1% of transactions are fraud. A model that predicts 'not fraud' for everything has 99.9% accuracy. What does this show?",
        options: ["The model is excellent", "Accuracy is misleading on imbalanced data", "Fraud is easy to detect", "The test set is too small"],
        answer: 1, why: "A trivial model can score high accuracy without catching any positives. Use precision, recall or PR-AUC." },
      { q: "A classifier has 40 true positives, 10 false positives and 20 false negatives. What is its precision?",
        options: ["0.8", "0.67", "0.4", "0.5"],
        answer: 0, why: "Precision = TP / (TP + FP) = 40 / 50 = 0.8. Recall would be 40 / 60, about 0.67." },
      { q: "For a screening test where missing a real case is very costly, which metric should you prioritize?",
        options: ["Precision", "Recall", "Accuracy", "Specificity"],
        answer: 1, why: "Recall measures the share of real cases you catch. Accepting more false alarms is the usual trade-off." }
    ]
  },
  {
    id: "ml-forest-boosting", area: "ml", title: "Random forests vs gradient boosting", mins: 40, level: 3, light: false,
    res: { label: "DataCamp: Ensemble Methods in Python", url: "https://www.datacamp.com/courses/ensemble-methods-in-python", src: "datacamp" },
    aloud: "Explain how a random forest and gradient boosting each combine trees, and why they behave differently.",
    interviewQ: "When would you choose gradient boosting over a random forest, and what do you tune first?",
    quiz: [
      { q: "How does a random forest reduce variance?",
        options: ["It averages many decorrelated trees trained on bootstrap samples", "It fits each tree to the previous tree's errors", "It uses a single very deep tree", "It removes all features except one"],
        answer: 0, why: "Bagging plus random feature selection makes trees differ, and averaging them smooths out individual errors." },
      { q: "How does gradient boosting build its model?",
        options: ["Trees are trained independently and averaged", "Trees are added one at a time, each correcting the errors of the ensemble so far", "It trains one neural network", "It clusters the data first"],
        answer: 1, why: "Each new tree fits the residual errors (the gradient of the loss) of the current ensemble." },
      { q: "If you keep adding trees without tuning, which model is more likely to start overfitting?",
        options: ["Random forest", "Gradient boosting", "Neither can overfit", "Both overfit equally"],
        answer: 1, why: "Adding more trees to a random forest generally plateaus. Boosting keeps fitting residuals, so it needs early stopping and a small learning rate." }
    ]
  },
  {
    id: "ml-regularization", area: "ml", title: "L1 vs L2 regularization", mins: 30, level: 2, light: false,
    res: { label: "scikit-learn: linear models (Ridge and Lasso)", url: "https://scikit-learn.org/stable/modules/linear_model.html", src: "free" },
    aloud: "Explain what L1 and L2 penalties add to the loss and what each does to the coefficients.",
    interviewQ: "You have 500 features and 2,000 rows. Would you use Lasso or Ridge, and why?",
    quiz: [
      { q: "Which regularization can shrink some coefficients exactly to zero?",
        options: ["L1 (Lasso)", "L2 (Ridge)", "Neither", "Both always do"],
        answer: 0, why: "The L1 penalty produces sparse solutions, so it doubles as feature selection." },
      { q: "What does the L2 penalty add to the loss?",
        options: ["The sum of absolute coefficients", "The sum of squared coefficients", "The number of non-zero coefficients", "The largest coefficient"],
        answer: 1, why: "L2 penalizes squared size, which shrinks coefficients smoothly but rarely to exactly zero." },
      { q: "You increase the regularization strength. What generally happens?",
        options: ["Bias goes up and variance goes down", "Bias goes down and variance goes up", "Both go up", "Neither changes"],
        answer: 0, why: "A stronger penalty restricts the model, trading a bit of fit for stability." }
    ]
  },
  {
    id: "ml-clustering", area: "ml", title: "K-means and choosing k", mins: 30, level: 2, light: false,
    res: { label: "scikit-learn: clustering guide", url: "https://scikit-learn.org/stable/modules/clustering.html", src: "free" },
    aloud: "Describe the k-means steps in order and give two ways to pick k.",
    interviewQ: "You clustered customers with k-means and one feature is income in dollars. What goes wrong and how do you fix it?",
    quiz: [
      { q: "What does k-means minimize?",
        options: ["The distance between clusters", "The within-cluster sum of squared distances to the centroids", "The number of clusters", "The variance between clusters"],
        answer: 1, why: "Inertia is the total squared distance from each point to its cluster centroid." },
      { q: "Why should you scale features before k-means?",
        options: ["It speeds up plotting", "K-means uses distances, so a feature with a large range dominates", "K-means requires normally distributed data", "Scaling picks the best k"],
        answer: 1, why: "Without scaling, a feature measured in thousands drowns out features measured in single digits." },
      { q: "A silhouette score close to 1 means:",
        options: ["Points sit well inside their cluster and far from other clusters", "Clusters overlap heavily", "The model has too many clusters", "The data is random"],
        answer: 0, why: "Scores near 1 mean good separation. Scores near 0 mean overlapping clusters, and negative scores suggest misassigned points." }
    ]
  },
  {
    id: "ml-encoding", area: "ml", title: "Encoding categorical features", mins: 25, level: 2, light: true,
    res: { label: "scikit-learn: preprocessing and encoding", url: "https://scikit-learn.org/stable/modules/preprocessing.html", src: "free" },
    aloud: "Explain one-hot encoding versus label encoding and when each is a bad idea.",
    interviewQ: "A column has 50,000 distinct categories, such as zip codes or product IDs. How do you encode it?",
    quiz: [
      { q: "Why is one-hot encoding usually preferred to label encoding for an unordered category in a linear model?",
        options: ["It uses less memory", "Label encoding implies an order and distances that do not exist", "One-hot columns are always more accurate", "Label encoding cannot be reversed"],
        answer: 1, why: "Encoding 'red', 'green', 'blue' as 1, 2, 3 tells a linear model that blue is three times red." },
      { q: "What is the main risk of target encoding?",
        options: ["It cannot handle new categories", "Target leakage if the encoding is computed using the same rows it predicts", "It always makes features sparse", "It requires scaling"],
        answer: 1, why: "The encoded value contains information about the label, so compute it only inside training folds (with smoothing)." },
      { q: "A category has 50,000 distinct values. What problem does one-hot encoding cause?",
        options: ["It creates a huge, sparse feature space", "It loses information", "It removes the category", "It makes values negative"],
        answer: 0, why: "You get 50,000 mostly-zero columns. Alternatives include target encoding, hashing, or grouping rare values." }
    ]
  }
]);
