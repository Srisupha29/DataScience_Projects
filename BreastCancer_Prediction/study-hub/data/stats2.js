window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "stats-distributions", area: "stats", title: "Normal, binomial and Poisson: when to use which", mins: 30, level: 2, light: false,
    res: { label: "Seeing Theory: probability distributions", url: "https://seeing-theory.brown.edu/probability-distributions/index.html", src: "free" },
    aloud: "For each case, name the distribution and say why: purchases out of 100 visitors, support tickets per hour, adult heights.",
    interviewQ: "Conversions out of 10,000 visitors at a 2% rate: which distribution models the count, and what are its mean and standard deviation?",
    quiz: [
      { q: "Out of 100 visitors, each independently clicks with probability 0.1. How is the number of clicks distributed?",
        options: ["Normal", "Binomial", "Poisson", "Uniform"],
        answer: 1, why: "A fixed number of independent yes/no trials with the same probability is binomial." },
      { q: "Support tickets arrive at a roughly constant average rate. Which distribution models the count per hour?",
        options: ["Bernoulli", "Binomial", "Poisson", "Uniform"],
        answer: 2, why: "Poisson models counts of events in a fixed interval when events occur independently at a steady rate." },
      { q: "A binomial count with n = 10,000 and p = 0.02. What are its mean and standard deviation?",
        options: ["200 and 14", "200 and 196", "200 and 200", "20 and 4.4"],
        answer: 0, why: "Mean = np = 200. SD = √(np(1 − p)) = √196 = 14." }
    ]
  },
  {
    id: "stats-conditional", area: "stats", title: "Conditional probability and independence", mins: 25, level: 2, light: true,
    res: { label: "Seeing Theory: basic probability", url: "https://seeing-theory.brown.edu/basic-probability/index.html", src: "free" },
    aloud: "Explain P(A|B), say what it means for two events to be independent, and say why P(A|B) is usually not the same as P(B|A).",
    interviewQ: "60% of mobile users convert and 30% of all users are on mobile. What is the probability a random user is a mobile user who converts?",
    quiz: [
      { q: "P(A) = 0.4 and P(B) = 0.5, and A and B are independent. What is P(A and B)?",
        options: ["0.9", "0.2", "0.1", "0.45"],
        answer: 1, why: "For independent events, P(A and B) = P(A) × P(B) = 0.4 × 0.5." },
      { q: "P(A and B) = 0.12 and P(B) = 0.4. What is P(A | B)?",
        options: ["0.048", "0.12", "0.3", "0.5"],
        answer: 2, why: "P(A | B) = P(A and B) / P(B) = 0.12 / 0.4 = 0.3." },
      { q: "If P(A | B) = P(A), the events A and B are:",
        options: ["Mutually exclusive", "Independent", "Complementary", "Always both true"],
        answer: 1, why: "Knowing B happened does not change the probability of A, which is the definition of independence." }
    ]
  },
  {
    id: "stats-moments", area: "stats", title: "Expectation, variance and covariance", mins: 30, level: 2, light: false,
    res: { label: "Wikipedia: covariance", url: "https://en.wikipedia.org/wiki/Covariance", src: "free" },
    aloud: "Explain expectation and variance in plain words, then say how covariance and correlation differ.",
    interviewQ: "Why do people report correlation instead of covariance when comparing relationships?",
    quiz: [
      { q: "Which formula defines Var(X)?",
        options: ["E[X]²", "E[(X − E[X])²]", "E[X] − E[X²]", "E[|X|]"],
        answer: 1, why: "Variance is the expected squared distance from the mean." },
      { q: "X has variance 4. What is Var(3X)?",
        options: ["12", "9", "7", "36"],
        answer: 3, why: "Var(aX) = a² Var(X) = 9 × 4 = 36." },
      { q: "Why is correlation often preferred to covariance?",
        options: ["It is always larger", "It measures causation", "It is unit-free and bounded between −1 and 1, so it can be compared across variables", "It captures every non-linear relationship"],
        answer: 2, why: "Covariance changes with units. Correlation rescales it. Neither proves causation, and correlation only measures linear association." }
    ]
  },
  {
    id: "stats-which-test", area: "stats", title: "Choosing the right test: t-test, chi-square, ANOVA", mins: 35, level: 2, light: false,
    res: { label: "SciPy statistics tutorial", url: "https://docs.scipy.org/doc/scipy/tutorial/stats.html", src: "free" },
    aloud: "Pick a test for each: average order value of two groups, conversion across three landing pages, and whether device type and plan are related.",
    interviewQ: "You want to compare average session time across four app versions. Which test do you use, and what do you do after a significant result?",
    quiz: [
      { q: "You compare average session time between two independent groups of users. Which test fits?",
        options: ["Chi-square test", "Two-sample t-test", "Paired t-test", "Correlation test"],
        answer: 1, why: "Two independent groups and a numeric outcome point to a two-sample t-test." },
      { q: "You compare mean values across three or more groups. Which test fits?",
        options: ["Several t-tests with no correction", "Chi-square", "ANOVA (followed by corrected comparisons if it is significant)", "Bayes' theorem"],
        answer: 2, why: "Many separate t-tests inflate the false positive rate. ANOVA tests all groups at once." },
      { q: "The same users are measured before and after a change. Which test fits?",
        options: ["Two-sample t-test", "Chi-square", "Paired t-test", "ANOVA with three groups"],
        answer: 2, why: "The measurements are linked by user, so you test the differences within each user." }
    ]
  },
  {
    id: "stats-chisq", area: "stats", title: "Chi-square test for categorical data", mins: 25, level: 2, light: true,
    res: { label: "Wikipedia: chi-squared test", url: "https://en.wikipedia.org/wiki/Chi-squared_test", src: "free" },
    aloud: "Explain observed versus expected counts, and what a large chi-square value means.",
    interviewQ: "Conversion is compared across three landing pages. Which test do you use, and what does a significant result tell you, and not tell you?",
    quiz: [
      { q: "What does a chi-square test of independence compare?",
        options: ["The means of two groups", "Observed counts with the counts expected if the variables were independent", "Two variances", "Two medians"],
        answer: 1, why: "A large gap between observed and expected counts is evidence of a relationship." },
      { q: "In a 2×2 table, a cell has row total 40 and column total 50, with a grand total of 100. What is its expected count under independence?",
        options: ["20", "40", "25", "0.5"],
        answer: 0, why: "Expected = (row total × column total) / grand total = 40 × 50 / 100 = 20." },
      { q: "Which situation is a problem for the chi-square test?",
        options: ["A very large sample", "Very small expected counts, such as under 5 in many cells", "More than two categories", "Binary data"],
        answer: 1, why: "The chi-square approximation becomes unreliable. Fisher's exact test is an alternative for small tables." }
    ]
  },
  {
    id: "stats-mle-idea", area: "stats", title: "Maximum likelihood estimation: the idea", mins: 30, level: 2, light: false,
    res: { label: "Seeing Theory: frequentist inference", url: "https://seeing-theory.brown.edu/frequentist-inference/index.html", src: "free" },
    aloud: "Explain likelihood as 'how well a parameter value explains the data' using coin flips.",
    interviewQ: "You see 7 heads in 10 flips. What is the maximum likelihood estimate of p, and why?",
    quiz: [
      { q: "You see 7 heads in 10 flips. What is the maximum likelihood estimate of p?",
        options: ["0.5", "0.7", "0.3", "0.07"],
        answer: 1, why: "The likelihood p⁷(1 − p)³ peaks at p = 7/10." },
      { q: "The likelihood function is viewed as a function of:",
        options: ["The data, with the parameters fixed", "Both, held fixed", "The sample size only", "The parameters, with the observed data held fixed"],
        answer: 3, why: "Probability fixes the parameters and asks about data. Likelihood fixes the data and asks about parameters." },
      { q: "With more and more data, a maximum likelihood estimate generally:",
        options: ["Gets less accurate", "Becomes more precise and, under standard conditions, converges to the true value", "Always equals the prior", "Stays the same"],
        answer: 1, why: "This property is called consistency." }
    ]
  },
  {
    id: "stats-bootstrap", area: "stats", title: "Bootstrap and permutation tests", mins: 30, level: 2, light: false,
    res: { label: "DataCamp: Statistical Thinking in Python (Part 2)", url: "https://www.datacamp.com/courses/statistical-thinking-in-python-part-2", src: "datacamp" },
    aloud: "Explain how resampling with replacement gives a confidence interval without formulas, and how shuffling labels gives a p-value.",
    interviewQ: "When would you prefer a bootstrap confidence interval over a formula-based one?",
    quiz: [
      { q: "What is a bootstrap sample?",
        options: ["A smaller sample drawn without replacement", "A sample drawn with replacement from your data, of the same size", "A brand new experiment", "The test set"],
        answer: 1, why: "Resampling your own data many times mimics drawing new samples from the population." },
      { q: "How do you get a 95% bootstrap confidence interval for a median?",
        options: ["Compute the median of the original data only", "Use the standard error formula for the mean", "Resample many times, compute the median each time, and take the 2.5th and 97.5th percentiles", "It cannot be done"],
        answer: 2, why: "The bootstrap works for statistics like the median where there is no simple formula." },
      { q: "In a permutation test for a difference in means between groups A and B, what do you do?",
        options: ["Shuffle the group labels many times and see how often a difference as large as the observed one appears by chance", "Remove the outliers", "Resample only group A", "Compare the variances"],
        answer: 0, why: "If the groups did not matter, shuffling the labels should give differences as large as the real one fairly often." }
    ]
  },
  {
    id: "stats-confounding", area: "stats", title: "Confounding and Simpson's paradox", mins: 30, level: 3, light: false,
    res: { label: "Wikipedia: Simpson's paradox", url: "https://en.wikipedia.org/wiki/Simpson%27s_paradox", src: "free" },
    aloud: "Give an example where a trend in the combined data reverses once you split by a group, and explain why it happens.",
    interviewQ: "Users who use feature X retain better. Can you conclude that X causes better retention?",
    quiz: [
      { q: "What is Simpson's paradox?",
        options: ["A trend that appears in each group reverses or disappears when the groups are combined (or vice versa)", "A rule that p-values are always wrong", "Two tests giving the same p-value", "Bias from tiny samples"],
        answer: 0, why: "It happens when group sizes differ and the grouping variable affects the outcome." },
      { q: "What is a confounder?",
        options: ["A noisy measurement", "A variable with no variance", "The outcome itself", "A variable that influences both the treatment and the outcome, creating a misleading association"],
        answer: 3, why: "Highly engaged users both adopt a feature more and retain more, so the feature looks like the cause." },
      { q: "When you can choose who gets the treatment, what best removes confounding?",
        options: ["A larger sample alone", "Randomization", "A smaller p-value threshold", "Dropping outliers"],
        answer: 1, why: "Random assignment makes the groups comparable on everything, including things you did not measure." }
    ]
  },
  {
    id: "stats-peeking", area: "stats", title: "Peeking, stopping rules and sequential testing", mins: 30, level: 3, light: false,
    res: { label: "Evan Miller: how not to run an A/B test", url: "https://www.evanmiller.org/how-not-to-run-an-ab-test.html", src: "free" },
    aloud: "Explain why checking a test every day and stopping when p < 0.05 inflates false positives.",
    interviewQ: "A product manager wants to stop an A/B test on day 4 because p = 0.03. What do you say?",
    quiz: [
      { q: "You check a fixed-horizon test every day and stop the first time p < 0.05. What happens to the overall false positive rate?",
        options: ["It stays at 5%", "It goes well above 5%", "It goes below 5%", "It is not affected"],
        answer: 1, why: "Each look is another chance for random noise to cross the threshold." },
      { q: "Which approach fixes the peeking problem?",
        options: ["Look more often", "Lower alpha after seeing the data", "Fix the sample size in advance and analyze once, or use a sequential method designed for repeated looks", "Drop the control group"],
        answer: 2, why: "Sequential methods adjust the thresholds so the overall error rate stays under control." },
      { q: "Why does repeated looking inflate errors?",
        options: ["P-values grow with time", "The data changes meaning", "Samples become biased", "Every look is another opportunity for chance to produce a 'significant' result"],
        answer: 3, why: "It is the same logic as testing many metrics: more chances means more false alarms." }
    ]
  },
  {
    id: "stats-deep-bayesian-ab", area: "stats", deep: true, title: "Deep dive: Bayesian A/B testing with Beta-Binomial", mins: 75, level: 3, light: false,
    res: { label: "Think Bayes (free book)", url: "https://allendowney.github.io/ThinkBayes2/", src: "free" },
    aloud: "Walk through a Beta prior, update it with conversions and non-conversions, compute the probability that B beats A, and say how that differs from a p-value.",
    interviewQ: "Your prior is Beta(1, 1). After 20 conversions out of 100 visitors, what is the posterior, and what is its mean?",
    quiz: [
      { q: "What does a Beta(1, 1) prior say about a conversion rate?",
        options: ["It is strongly centered on 0.5", "All values between 0 and 1 are equally likely (uniform)", "It is exactly 0", "It follows a normal distribution"],
        answer: 1, why: "Beta(1, 1) is flat, so the data does most of the work." },
      { q: "A Beta(1, 1) prior meets data with 20 conversions and 80 non-conversions. What is the posterior?",
        options: ["Beta(20, 80)", "Beta(21, 81)", "Beta(1, 1)", "Beta(100, 20)"],
        answer: 1, why: "Add the conversions to the first parameter and the non-conversions to the second: Beta(1 + 20, 1 + 80)." },
      { q: "What is the mean of a Beta(21, 81) posterior?",
        options: ["0.200", "0.210", "0.250", "0.206"],
        answer: 3, why: "The mean of Beta(a, b) is a / (a + b) = 21 / 102 ≈ 0.206." },
      { q: "The posteriors give P(B > A) = 0.96. What does this mean?",
        options: ["The p-value is 0.04", "There is a 4% chance the test is invalid", "B is 96% better than A", "Given the model and prior, there is about a 96% probability that B's true rate is higher than A's"],
        answer: 3, why: "It is a direct probability statement about the parameters, which a p-value cannot give." },
      { q: "What is the effect of a strong prior when you have little data?",
        options: ["No effect", "The posterior stays close to the prior until enough data arrives to move it", "The posterior ignores the prior", "The posterior becomes uniform"],
        answer: 1, why: "A strong prior is like having already seen many observations." }
    ]
  },
  {
    id: "stats-deep-ab-end-to-end", area: "stats", deep: true, title: "Deep dive: A/B testing end to end", mins: 90, level: 3, light: false,
    res: { label: "Evan Miller: sample size calculator for A/B tests", url: "https://www.evanmiller.org/ab-testing/sample-size.html", src: "free" },
    aloud: "Walk through an A/B test from start to decision: hypothesis, primary and guardrail metrics, sample size, randomization checks, analysis and the final call.",
    interviewQ: "You planned a 50/50 split but the test shows 51.5% / 48.5%. What do you do?",
    quiz: [
      { q: "What is a sample ratio mismatch (SRM)?",
        options: ["The control group has a higher metric", "The observed split between groups differs from the planned split by more than chance explains, which signals a problem with assignment or logging", "The sample is too large", "Two metrics are correlated"],
        answer: 1, why: "Do not trust the results until you know why the split is off." },
      { q: "How does the sample size you need change if you want to detect a smaller lift?",
        options: ["You need fewer users", "It does not change", "You need many more users, since it grows roughly with 1 / effect²", "You need a smaller alpha only"],
        answer: 2, why: "Halving the effect you want to detect roughly quadruples the required sample." },
      { q: "How does CUPED reduce variance?",
        options: ["By dropping users", "By adjusting the metric using a pre-experiment covariate that is correlated with it", "By raising alpha", "By running the test longer"],
        answer: 1, why: "Removing the part of the metric that is predictable from pre-experiment behaviour leaves less noise." },
      { q: "What is a guardrail metric?",
        options: ["The primary goal metric", "A synonym for p-value", "A metric used for randomization", "A metric you watch to make sure you are not causing harm (for example latency or refunds) while improving the primary metric"],
        answer: 3, why: "A win on the primary metric does not count if a guardrail gets worse." },
      { q: "What should the randomization unit usually match?",
        options: ["The analysis unit, to avoid dependence (for example randomize by user if you analyze per user)", "Always page views", "Always sessions", "Whatever is cheapest"],
        answer: 0, why: "Randomizing by page view but analyzing by user mixes both variants inside each user and breaks independence." }
    ]
  },
  {
    id: "stats-deep-ols-math", area: "stats", deep: true, title: "Deep dive: linear regression from the math", mins: 80, level: 3, light: false,
    res: { label: "Wikipedia: ordinary least squares", url: "https://en.wikipedia.org/wiki/Ordinary_least_squares", src: "free" },
    aloud: "Derive the normal equations from minimizing squared error, and say when XᵀX cannot be inverted.",
    interviewQ: "What does the Gauss–Markov theorem say, and which assumptions does it need?",
    quiz: [
      { q: "Which is the normal equation solution for ordinary least squares?",
        options: ["β = (XᵀX)⁻¹ Xᵀ y", "β = X⁻¹ y always", "β = Xᵀ y", "β = (XXᵀ)⁻¹ y"],
        answer: 0, why: "Setting the gradient of the squared error to zero gives XᵀXβ = Xᵀy." },
      { q: "When is XᵀX not invertible?",
        options: ["When n is large", "When the target is binary", "When features are standardized", "When features are perfectly collinear, or there are more features than samples"],
        answer: 3, why: "Then there are infinitely many coefficient vectors that fit equally well." },
      { q: "Under the classical assumptions (linearity, zero-mean uncorrelated errors with constant variance, no perfect collinearity), the Gauss–Markov theorem says OLS is:",
        options: ["The best of all possible estimators", "The best linear unbiased estimator (BLUE)", "Biased but efficient", "Valid only with normal errors"],
        answer: 1, why: "Normality is not needed for this result. It is needed for exact small-sample t and F tests." },
      { q: "What does R² measure?",
        options: ["The correlation between residuals and X", "The p-value of the model", "The proportion of the variance in y explained by the model", "The slope"],
        answer: 2, why: "R² = 1 − (residual sum of squares) / (total sum of squares)." },
      { q: "Adding more predictors to an OLS model (with an intercept) never decreases which of these?",
        options: ["Adjusted R²", "Test error", "Standard errors", "R² on the training data"],
        answer: 3, why: "Training R² can only stay the same or rise, which is why adjusted R² and held-out data exist." }
    ]
  }
]);
