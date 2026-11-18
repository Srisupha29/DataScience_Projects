window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "ml-logreg", area: "ml", title: "Logistic regression and the decision boundary", mins: 30, level: 2, light: false,
    res: { label: "scikit-learn: logistic regression", url: "https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression", src: "free" },
    aloud: "Explain how logistic regression turns a linear score into a probability, and where the decision boundary comes from.",
    interviewQ: "Why is logistic regression called a linear model even though its output is a probability between 0 and 1?",
    quiz: [
      { q: "What does logistic regression compute before you apply a threshold?",
        options: ["A probability between 0 and 1, by passing a linear score through the sigmoid", "A class label directly", "A distance to the nearest neighbour", "An unbounded number used as the prediction"],
        answer: 0, why: "The linear score w·x + b goes through the sigmoid to give P(y = 1 | x). The threshold is applied afterwards." },
      { q: "Which loss is used to fit logistic regression?",
        options: ["Mean squared error", "Hinge loss", "Log loss (cross-entropy)", "Absolute error"],
        answer: 2, why: "Log loss is the negative log-likelihood of the labels under the model, and it is convex for logistic regression." },
      { q: "Why is logistic regression called a linear model?",
        options: ["Its learning curve is a straight line", "It can only use two features", "Its probabilities increase linearly with every feature", "The log-odds are a linear function of the features, so the decision boundary is a hyperplane"],
        answer: 3, why: "The boundary is where w·x + b = 0, which is a straight line or plane in feature space." }
    ]
  },
  {
    id: "ml-trees", area: "ml", title: "Decision trees: how a split is chosen", mins: 30, level: 2, light: false,
    res: { label: "scikit-learn: decision trees", url: "https://scikit-learn.org/stable/modules/tree.html", src: "free" },
    aloud: "Explain how a tree decides which feature and threshold to split on, using Gini impurity or entropy.",
    interviewQ: "Why does a fully grown decision tree overfit, and what are three ways to control it?",
    quiz: [
      { q: "A node contains 50% class A and 50% class B. What is its Gini impurity?",
        options: ["0", "0.25", "0.5", "1"],
        answer: 2, why: "Gini = 1 − Σp² = 1 − (0.25 + 0.25) = 0.5, the maximum for two classes. A pure node has Gini 0." },
      { q: "How does a tree choose the best split?",
        options: ["The split with the largest weighted reduction in impurity across the child nodes", "The split closest to the median", "The first feature in the dataset", "The split that puts the most rows on the left"],
        answer: 0, why: "It tries candidate features and thresholds and keeps the one whose children are purest overall." },
      { q: "Which setting reduces overfitting in a tree?",
        options: ["Removing the depth limit", "Requiring more samples in each leaf (a higher min_samples_leaf)", "Training on fewer rows", "Dropping the validation set"],
        answer: 1, why: "Bigger leaves and shallower depth stop the tree from memorizing individual rows. Pruning does the same job." }
    ]
  },
  {
    id: "ml-knn", area: "ml", title: "k-nearest neighbours", mins: 25, level: 2, light: true,
    res: { label: "scikit-learn: nearest neighbours", url: "https://scikit-learn.org/stable/modules/neighbors.html", src: "free" },
    aloud: "Explain how kNN predicts, why it has almost no training step, and what k controls.",
    interviewQ: "Your kNN gets slower as the data grows and its accuracy drops with 200 features. Why?",
    quiz: [
      { q: "What does a very small k (such as 1) tend to do?",
        options: ["Underfit with a smooth boundary", "Overfit with a jagged boundary that follows noise", "Always predict the majority class", "Ignore the nearest point"],
        answer: 1, why: "With k = 1 a single noisy neighbour decides the prediction. Larger k smooths the boundary." },
      { q: "Why should you scale features before kNN?",
        options: ["kNN needs normally distributed features", "Scaling chooses k for you", "Scaling speeds up training", "kNN uses distances, so a feature with a large range would dominate"],
        answer: 3, why: "Income in dollars would swamp age in years unless both are put on comparable scales." },
      { q: "What is the 'curse of dimensionality' for kNN?",
        options: ["Training takes too long", "In many dimensions, distances between points become similar, so 'nearest' stops being meaningful", "There are too few classes", "Labels get noisier"],
        answer: 1, why: "With many features, the nearest and farthest points end up at similar distances, which weakens the method." }
    ]
  },
  {
    id: "ml-nb", area: "ml", title: "Naive Bayes classifier", mins: 25, level: 2, light: true,
    res: { label: "scikit-learn: naive Bayes", url: "https://scikit-learn.org/stable/modules/naive_bayes.html", src: "free" },
    aloud: "Explain what 'naive' assumes, and why the method still works well for text such as spam.",
    interviewQ: "Naive Bayes gives a word that never appeared in spam a spam probability of zero. What breaks, and how do you fix it?",
    quiz: [
      { q: "What is the 'naive' assumption in naive Bayes?",
        options: ["Features are conditionally independent given the class", "All classes are equally likely", "Features are normally distributed", "The labels contain no noise"],
        answer: 0, why: "It lets the model multiply per-feature probabilities instead of modelling every combination of features." },
      { q: "A word never appeared in the spam training emails, so its estimated spam probability is 0. What is the usual fix?",
        options: ["Delete the word and retrain", "Raise the decision threshold", "Laplace (additive) smoothing, which adds a small count to every word", "Use the median probability"],
        answer: 2, why: "Without smoothing, one zero makes the whole product zero, no matter how spammy the rest of the email looks." },
      { q: "Why is naive Bayes a strong baseline for text despite its unrealistic assumption?",
        options: ["It models word order", "It is fast, needs little data, and the ranking of class probabilities is often right even when the probabilities themselves are off", "It cannot overfit", "It is the only model that handles text"],
        answer: 1, why: "For classification you only need the right class to win, not perfectly calibrated probabilities." }
    ]
  },
  {
    id: "ml-svm", area: "ml", title: "Support vector machines and margins", mins: 35, level: 3, light: false,
    res: { label: "scikit-learn: support vector machines", url: "https://scikit-learn.org/stable/modules/svm.html", src: "free" },
    aloud: "Explain the margin, the support vectors, and what the C parameter trades off.",
    interviewQ: "When would you pick an SVM with an RBF kernel over logistic regression, and what would worry you about it?",
    quiz: [
      { q: "What does a standard SVM try to maximize?",
        options: ["The number of support vectors", "The training accuracy only", "The distance to the origin", "The margin between the boundary and the closest points of each class"],
        answer: 3, why: "A wider margin tends to generalize better." },
      { q: "Which training points determine the SVM decision boundary?",
        options: ["All points equally", "Only the support vectors, the points on or inside the margin", "Only points far from the boundary", "The class centroids"],
        answer: 1, why: "Points well outside the margin can be removed without changing the boundary." },
      { q: "In a soft-margin SVM, what does a large C do?",
        options: ["Allows many margin violations and gives a wider margin", "Penalizes violations heavily, giving a narrower margin and more risk of overfitting", "Switches the kernel off", "Sets the number of classes"],
        answer: 1, why: "C is the price of a violation. A large C means 'do not misclassify training points', which can overfit noise." }
    ]
  },
  {
    id: "ml-pca", area: "ml", title: "PCA: what it does and when to use it", mins: 30, level: 2, light: false,
    res: { label: "scikit-learn: PCA", url: "https://scikit-learn.org/stable/modules/decomposition.html#pca", src: "free" },
    aloud: "Explain PCA as finding the directions where the data varies most, and say what 'explained variance' tells you.",
    interviewQ: "You have 300 correlated features. When would you use PCA before a model, and what do you lose?",
    quiz: [
      { q: "What are the principal components?",
        options: ["The original features ranked by importance", "Clusters in the data", "Orthogonal directions, ordered by how much variance they capture", "The features most correlated with the target"],
        answer: 2, why: "The first component is the direction of greatest variance, the second is the greatest remaining variance at right angles to it, and so on." },
      { q: "Why standardize features before PCA?",
        options: ["PCA needs the labels", "Features with large scales would dominate the variance and therefore the components", "It makes components non-orthogonal", "It chooses the number of components"],
        answer: 1, why: "PCA is driven by variance, and variance depends on units." },
      { q: "What is a main drawback of using PCA components as model inputs?",
        options: ["They are always worse than raw features", "They have more dimensions than the data", "They are mixtures of features, so harder to interpret, and PCA ignores the target", "They cannot be computed for numeric data"],
        answer: 2, why: "PCA is unsupervised. The high-variance directions are not necessarily the predictive ones." }
    ]
  },
  {
    id: "ml-optimizers", area: "ml", title: "Gradient descent, SGD and Adam", mins: 35, level: 3, light: false,
    res: { label: "CS231n notes: learning and optimization", url: "https://cs231n.github.io/neural-networks-3/", src: "free" },
    aloud: "Explain gradient descent as walking downhill, then say what changes with mini-batches, momentum and Adam.",
    interviewQ: "Your training loss bounces up and down and never settles. What do you check first?",
    quiz: [
      { q: "What does the learning rate control?",
        options: ["The number of epochs", "The number of layers", "The size of each parameter update step", "The batch size"],
        answer: 2, why: "Too large and training bounces or diverges. Too small and it crawls." },
      { q: "Compared with full-batch gradient descent, what is mini-batch SGD?",
        options: ["More accurate gradients but slower per step", "Noisier gradient estimates, but each step is much cheaper, so it often improves sooner", "Guaranteed to find the global minimum", "Only usable for small models"],
        answer: 1, why: "A random mini-batch gives an approximate gradient at a fraction of the cost." },
      { q: "What does momentum add to gradient descent?",
        options: ["A running average of past gradients, so updates keep moving in consistent directions and oscillations are dampened", "A bigger learning rate", "Random labels", "A smaller batch"],
        answer: 0, why: "Think of a ball rolling downhill: it builds up speed along consistent slopes and smooths out zig-zags." }
    ]
  },
  {
    id: "ml-nn-basics", area: "ml", title: "Neural network basics: layers and activations", mins: 35, level: 2, light: false,
    res: { label: "3Blue1Brown: neural networks", url: "https://www.3blue1brown.com/topics/neural-networks", src: "free" },
    aloud: "Explain what a hidden layer does, and why a network needs a non-linear activation function.",
    interviewQ: "What happens if you stack ten linear layers with no activation functions?",
    quiz: [
      { q: "Why do neural networks need non-linear activation functions?",
        options: ["To make training faster", "To keep all weights positive", "To reduce the number of parameters", "Without them, stacked layers collapse into one linear transformation"],
        answer: 3, why: "A product of matrices is still a matrix, so ten linear layers can only do what one can." },
      { q: "Which activation is the usual default for hidden layers today?",
        options: ["A step function", "ReLU or a close variant", "The identity function", "Square root"],
        answer: 1, why: "ReLU is cheap and, unlike sigmoid and tanh, does not squash gradients for positive inputs." },
      { q: "A model predicts one of 5 mutually exclusive classes. What belongs on the output layer?",
        options: ["ReLU with mean squared error", "Sigmoid with hinge loss", "Softmax with cross-entropy loss", "No activation and no loss"],
        answer: 2, why: "Softmax turns the 5 scores into probabilities that sum to 1." }
    ]
  },
  {
    id: "ml-imbalance", area: "ml", title: "Handling class imbalance", mins: 30, level: 2, light: false,
    res: { label: "imbalanced-learn user guide", url: "https://imbalanced-learn.org/stable/user_guide.html", src: "free" },
    aloud: "Name three ways to handle a 1% positive class, and say what could go wrong with each.",
    interviewQ: "You oversample the minority class before splitting into train and test. What is wrong with that?",
    quiz: [
      { q: "What goes wrong if you oversample before splitting into train and test?",
        options: ["Nothing, it is the recommended order", "The test set becomes smaller", "Copies of the same minority rows can land in both sets, leaking information and inflating the scores", "Recall drops to zero"],
        answer: 2, why: "Resample only inside the training data (or inside each cross-validation fold)." },
      { q: "What does class_weight='balanced' do in many scikit-learn models?",
        options: ["Drops majority rows", "Weights the loss so mistakes on rare classes cost more", "Switches the metric to accuracy", "Duplicates minority rows on disk"],
        answer: 1, why: "It rebalances the importance of each class without changing the data." },
      { q: "Besides resampling, what can improve results on imbalanced data?",
        options: ["Using accuracy as the main metric", "Removing all minority examples", "Raising k in k-means", "Tuning the decision threshold on predicted probabilities for the metric you care about"],
        answer: 3, why: "The default 0.5 threshold is rarely right when one class is rare." }
    ]
  },
  {
    id: "ml-tuning", area: "ml", title: "Hyperparameter tuning: grid, random, Bayesian", mins: 30, level: 2, light: false,
    res: { label: "DataCamp: Hyperparameter Tuning in Python", url: "https://www.datacamp.com/courses/hyperparameter-tuning-in-python", src: "datacamp" },
    aloud: "Explain the difference between a parameter and a hyperparameter, and why random search often beats grid search.",
    interviewQ: "How do you tune a model without leaking information from your test set?",
    quiz: [
      { q: "Which of these is a hyperparameter?",
        options: ["The coefficients of a linear regression", "The maximum depth you set for a tree before training", "The weights of a neural network", "The predicted value in a leaf"],
        answer: 1, why: "Hyperparameters are settings you choose. Parameters are what training learns." },
      { q: "Why can random search beat grid search for the same budget?",
        options: ["It is guaranteed to find the optimum", "It needs no validation", "It tests each combination twice", "It tries more distinct values of the few hyperparameters that really matter"],
        answer: 3, why: "A grid repeats the same few values of an important parameter, while random draws give a new value every time." },
      { q: "When should the final test set be used?",
        options: ["Once, at the end, after tuning with cross-validation on the training data", "During every tuning step", "To choose the hyperparameters", "To train the final model with extra weight"],
        answer: 0, why: "If you tune on the test set, it stops being an honest estimate of new data." }
    ]
  },
  {
    id: "ml-deep-gradient-boosting", area: "ml", deep: true, title: "Deep dive: gradient boosting from scratch", mins: 75, level: 3, light: false,
    res: { label: "XGBoost docs: introduction to boosted trees", url: "https://xgboost.readthedocs.io/en/stable/tutorials/model.html", src: "free" },
    aloud: "Walk through boosting round by round for squared error: what each new tree is fit to, why a small learning rate helps, and what XGBoost adds (second-order gradients and tree regularization).",
    interviewQ: "Show why, for squared error, the negative gradient is just the residual. Then say what changes when the loss is log loss.",
    quiz: [
      { q: "For squared error loss L = ½(y − F)², what is the negative gradient with respect to the prediction F?",
        options: ["F − y", "(y − F)²", "y × F", "y − F, the residual"],
        answer: 3, why: "dL/dF = −(y − F), so the negative gradient is y − F. Each new tree is fit to these residuals." },
      { q: "In gradient boosting with learning rate η, how is the model updated after fitting a tree h to the residuals?",
        options: ["F_new = h", "F_new = η × F_old", "F_new = F_old + η × h", "F_new = F_old − h²"],
        answer: 2, why: "Each tree adds a shrunken correction to the running prediction." },
      { q: "Why use a small learning rate together with more trees?",
        options: ["It makes each tree larger", "Each tree contributes less, which usually generalizes better but needs more trees", "It removes the need for early stopping", "It makes boosting run in parallel"],
        answer: 1, why: "Shrinkage makes the ensemble improve in small careful steps and reduces overfitting." },
      { q: "What does XGBoost use beyond the plain gradient?",
        options: ["Both the first and second derivatives (gradient and Hessian) of the loss, plus an explicit penalty on tree complexity", "Only the sign of the gradient", "A random forest at every step", "No loss function"],
        answer: 0, why: "The second-order information gives better step sizes for the leaf values, and the penalty discourages large trees." },
      { q: "Why is boosting built sequentially, unlike a random forest?",
        options: ["It is not, both are fully parallel", "Trees are trained on separate data folds", "Each tree depends on the errors of the ensemble so far, so trees cannot be trained independently", "It needs a GPU"],
        answer: 2, why: "Within one tree the split search can be parallelized, but tree t cannot start before tree t − 1 is done." }
    ]
  },
  {
    id: "ml-deep-kernel-trick", area: "ml", deep: true, title: "Deep dive: the kernel trick and the SVM dual", mins: 70, level: 3, light: false,
    res: { label: "Wikipedia: kernel method (kernel trick)", url: "https://en.wikipedia.org/wiki/Kernel_method", src: "free" },
    aloud: "Explain how a kernel computes similarity in a high-dimensional space without ever building that space, and why the SVM dual form only needs dot products.",
    interviewQ: "Why does the RBF kernel correspond to infinitely many features, and what does gamma control?",
    quiz: [
      { q: "What is the kernel trick?",
        options: ["Replacing the labels with probabilities", "Computing inner products in a high-dimensional feature space directly with a kernel function, without building the features", "Removing the support vectors", "Standardizing the kernel"],
        answer: 1, why: "It gives the benefit of a rich feature map at the cost of one function evaluation per pair of points." },
      { q: "In the SVM dual formulation, the training data enters the optimization only through:",
        options: ["Feature means", "The labels alone", "The number of classes", "Dot products between pairs of training points, which a kernel can replace"],
        answer: 3, why: "That is exactly why swapping in a kernel works without touching the rest of the algorithm." },
      { q: "In the RBF kernel exp(−γ‖x − x'‖²), what does a very large γ do?",
        options: ["Points influence far-away regions, giving a smooth boundary", "Each point's influence becomes very local, giving a wiggly boundary that can overfit", "It turns the kernel linear", "It makes the margin infinite"],
        answer: 1, why: "A large γ means similarity drops off quickly with distance." },
      { q: "Which training points have non-zero dual coefficients in an SVM?",
        options: ["All points", "Only misclassified points", "Only the majority class", "Only the support vectors"],
        answer: 3, why: "Points strictly outside the margin get a coefficient of zero." },
      { q: "What property must a kernel (Gram) matrix have?",
        options: ["It must be diagonal", "It must have all positive entries", "It must be symmetric and positive semi-definite", "Its determinant must be 1"],
        answer: 2, why: "This is Mercer's condition. It guarantees the kernel corresponds to an inner product in some feature space." }
    ]
  },
  {
    id: "ml-deep-training-nn", area: "ml", deep: true, title: "Deep dive: training neural networks that actually train", mins: 80, level: 3, light: false,
    res: { label: "CS231n notes: setting up the data, initialization and regularization", url: "https://cs231n.github.io/neural-networks-2/", src: "free" },
    aloud: "Explain vanishing and exploding gradients, how initialization, normalization and residual connections help, and give a checklist for debugging a model that does not learn.",
    interviewQ: "Your network's loss does not go down. Walk me through your debugging order.",
    quiz: [
      { q: "Why is initializing all weights in a hidden layer to the same value (such as zero) a problem?",
        options: ["It makes training too fast", "It causes overflow", "All neurons in the layer compute the same thing and get the same gradients, so they never become different", "It stops you using ReLU"],
        answer: 2, why: "This is the symmetry problem. Random initialization breaks it." },
      { q: "A new model will not train. What is a good first sanity check?",
        options: ["Add more layers", "Try to overfit a tiny batch of 10 to 20 examples. If it cannot, there is a bug", "Switch to a bigger dataset", "Remove the validation set"],
        answer: 1, why: "Any working network should be able to memorize a handful of examples." },
      { q: "What does batch normalization do?",
        options: ["Normalizes labels", "Removes outliers from the dataset", "Normalizes each layer's inputs using batch statistics, then rescales with learned parameters, which stabilizes and speeds up training", "Replaces the optimizer"],
        answer: 2, why: "It keeps activations in a well-behaved range, which allows larger learning rates." },
      { q: "What happens to dropout at inference time?",
        options: ["It is turned off and all units are used (with scaling handled so activations match training)", "It is still applied randomly", "It is applied twice", "It doubles the learning rate"],
        answer: 0, why: "Dropout is a training-time regularizer. Predictions should be deterministic." },
      { q: "The loss becomes NaN after a few steps. What are likely causes?",
        options: ["The model is too small", "Too few epochs", "A small batch size alone", "A learning rate that is too high, or numerical problems such as log(0), causing values to explode"],
        answer: 3, why: "Check the learning rate first, then look for log of zero, division by zero or unscaled inputs." }
    ]
  }
]);
