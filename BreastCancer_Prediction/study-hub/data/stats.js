window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "stats-ci", area: "stats", title: "Confidence intervals in plain language", mins: 25, level: 2, light: false,
    res: { label: "StatQuest: confidence intervals", url: "https://www.youtube.com/results?search_query=statquest+confidence+intervals", src: "free" },
    aloud: "Explain what a 95% confidence interval means to a friend who has never studied statistics, without saying the true value is 95% likely to be inside it.",
    interviewQ: "Your A/B test shows a lift of 2% with a 95% confidence interval of -0.5% to 4.5%. What do you tell the product manager?",
    quiz: [
      { q: "A 95% confidence interval for average order value is $18 to $22. Which statement is correct?",
        options: ["There is a 95% probability the true mean lies between $18 and $22", "If we repeated the sampling many times, about 95% of intervals built this way would contain the true mean", "95% of individual orders fall between $18 and $22", "The sample mean has a 95% chance of falling between $18 and $22"],
        answer: 1, why: "The 95% describes the method: across many repeated samples, about 95% of the intervals it produces cover the true value. It is not a probability statement about this one interval, and it says nothing about individual orders." },
      { q: "Everything else equal, what happens to a confidence interval when the sample size grows?",
        options: ["It gets wider", "It gets narrower", "It stays the same", "It becomes biased"],
        answer: 1, why: "The standard error shrinks roughly with the square root of n, so the interval narrows." },
      { q: "Which change makes a confidence interval wider?",
        options: ["Raising the confidence level from 95% to 99%", "Doubling the sample size", "Collecting less noisy data", "Using a more precise measuring tool"],
        answer: 0, why: "To be more confident that the interval catches the true value, the method has to cover a wider range." }
    ]
  },
  {
    id: "stats-pvalue", area: "stats", title: "P-values: what they are and are not", mins: 30, level: 2, light: false,
    res: { label: "Wikipedia: p-value (read the definition and misuses)", url: "https://en.wikipedia.org/wiki/P-value", src: "free" },
    aloud: "Define a p-value in one sentence, then name two things people wrongly say it means.",
    interviewQ: "A test returns p = 0.03. Walk me through exactly what you can and cannot conclude.",
    quiz: [
      { q: "What is a p-value?",
        options: ["The probability that the null hypothesis is true", "The probability of seeing data at least this extreme if the null hypothesis were true", "The probability the result will replicate", "The size of the effect"],
        answer: 1, why: "It is calculated assuming the null is true. It does not give the probability that the null (or the alternative) is true." },
      { q: "A test gives p = 0.03 and your significance level is 0.05. What is the correct conclusion?",
        options: ["The effect is large", "The null hypothesis has a 3% chance of being true", "We reject the null at the 5% level", "The result will replicate 97% of the time"],
        answer: 2, why: "Significance only says the data would be unusual under the null. It says nothing about how large or important the effect is." },
      { q: "With millions of users, an A/B test finds p = 0.001 for a 0.1% increase in conversion. What is the sensible reading?",
        options: ["It is statistically significant but may be too small to matter, so check the effect size and interval", "It must be launched because p is very small", "The test is invalid because the lift is small", "The p-value means there is a 99.9% chance the lift is real"],
        answer: 0, why: "Large samples make tiny effects significant. Decide using effect size, confidence interval and business cost." }
    ]
  },
  {
    id: "stats-power", area: "stats", title: "Statistical power and sample size", mins: 35, level: 3, light: false,
    res: { label: "DataCamp: Hypothesis Testing in Python", url: "https://www.datacamp.com/courses/hypothesis-testing-in-python", src: "datacamp" },
    aloud: "Explain power and Type II error using an A/B test where the new design really is better but your test says nothing happened.",
    interviewQ: "How would you decide how many users you need for an A/B test, and what inputs do you need from the business?",
    quiz: [
      { q: "Statistical power is the probability of:",
        options: ["Rejecting a true null hypothesis", "Correctly rejecting the null when a real effect exists", "Accepting the null when it is true", "Getting a p-value below 0.5"],
        answer: 1, why: "Power equals 1 minus the Type II error rate: the chance of detecting an effect that is really there." },
      { q: "Holding other things fixed, which change increases power?",
        options: ["A smaller sample", "A larger sample", "A smaller true effect", "A stricter significance level, such as 0.001 instead of 0.05"],
        answer: 1, why: "More data reduces noise. Smaller effects and stricter alpha both lower power." },
      { q: "An A/B test has a real lift, but the result is not significant. What kind of error is this?",
        options: ["Type I error", "Type II error", "Sampling bias", "Simpson's paradox"],
        answer: 1, why: "Failing to reject a false null is a Type II error, which is what low power produces." }
    ]
  },
  {
    id: "stats-clt", area: "stats", title: "The central limit theorem", mins: 25, level: 2, light: true,
    res: { label: "Wikipedia: central limit theorem", url: "https://en.wikipedia.org/wiki/Central_limit_theorem", src: "free" },
    aloud: "Explain the central limit theorem to someone who only knows what an average is, and say why it matters for A/B tests.",
    interviewQ: "Your data is heavily skewed. Why can you still use a t-test or z-test on the mean with a large sample?",
    quiz: [
      { q: "What does the central limit theorem say?",
        options: ["All data becomes normally distributed with enough samples", "The distribution of the sample mean approaches normal as n grows, whatever the population shape (with finite variance)", "The median always equals the mean", "Large samples have no variance"],
        answer: 1, why: "It is about the sampling distribution of the mean, not the raw data." },
      { q: "A population has standard deviation 10. What is the standard error of the mean for n = 25?",
        options: ["10", "2", "0.4", "5"],
        answer: 1, why: "Standard error = sigma divided by the square root of n = 10 / 5 = 2." },
      { q: "Which situation can break the central limit theorem?",
        options: ["A skewed population with n = 200", "Independent draws from a population with finite variance", "Data from a Cauchy distribution, which has no finite variance", "Binary 0/1 data"],
        answer: 2, why: "The theorem needs a finite variance. Extremely heavy-tailed data can violate that." }
    ]
  },
  {
    id: "stats-bayes", area: "stats", title: "Bayes' theorem and base rates", mins: 30, level: 2, light: false,
    res: { label: "Wikipedia: Bayes' theorem (medical test example)", url: "https://en.wikipedia.org/wiki/Bayes%27_theorem", src: "free" },
    aloud: "Use a rare disease and an accurate test to explain why a positive result can still mean you probably do not have the disease.",
    interviewQ: "A fraud model catches 90% of fraud and wrongly flags 5% of good transactions. Fraud is 0.5% of transactions. If a transaction is flagged, roughly how likely is fraud?",
    quiz: [
      { q: "A disease affects 1% of people. A test detects 90% of cases and gives a false positive for 9% of healthy people. Roughly what is the chance someone who tests positive has the disease?",
        options: ["90%", "50%", "About 9%", "1%"],
        answer: 2, why: "Per 10,000 people: 90 true positives and about 891 false positives. 90 / (90 + 891) is about 9%." },
      { q: "In Bayes' theorem, what does the prior represent?",
        options: ["Your belief about the hypothesis before seeing the new data", "The probability of the data", "The false positive rate", "The final answer after updating"],
        answer: 0, why: "The prior is the starting belief, which the likelihood of the new data then updates into the posterior." },
      { q: "Why do base rates matter when judging an accurate test?",
        options: ["They do not matter if sensitivity is high", "When the condition is rare, even a small false positive rate produces many more false positives than true positives", "They only matter for continuous data", "They change the test's sensitivity"],
        answer: 1, why: "A rare condition means most people tested are healthy, so even a low false positive rate adds up." }
    ]
  },
  {
    id: "stats-multiple", area: "stats", title: "Multiple testing and p-hacking", mins: 25, level: 2, light: false,
    res: { label: "Wikipedia: multiple comparisons problem", url: "https://en.wikipedia.org/wiki/Multiple_comparisons_problem", src: "free" },
    aloud: "Explain why testing 20 metrics and reporting the one that came out significant is misleading, and name one fix.",
    interviewQ: "Your A/B test tracked 15 metrics and only one is significant at 0.05. How do you respond?",
    quiz: [
      { q: "You test 20 independent hypotheses at alpha = 0.05 and every null is actually true. About how many false positives do you expect?",
        options: ["0", "1", "5", "20"],
        answer: 1, why: "20 tests times a 5% false positive rate gives about 1 expected false positive." },
      { q: "With the Bonferroni correction, what per-test threshold do you use for 10 tests and an overall alpha of 0.05?",
        options: ["0.5", "0.05", "0.005", "0.0005"],
        answer: 2, why: "Bonferroni divides alpha by the number of tests: 0.05 / 10 = 0.005." },
      { q: "Which of these is p-hacking?",
        options: ["Writing down the one primary metric before the test starts", "Trying many metrics and segments and reporting only those with p < 0.05", "Using a larger sample", "Reporting confidence intervals"],
        answer: 1, why: "Searching until something looks significant, then reporting only that, inflates the false positive rate." }
    ]
  },
  {
    id: "stats-regression", area: "stats", title: "Linear regression assumptions and diagnostics", mins: 35, level: 3, light: false,
    res: { label: "StatQuest: linear regression", url: "https://www.youtube.com/results?search_query=statquest+linear+regression", src: "free" },
    aloud: "List the main assumptions of linear regression and say which plot you would use to check each one.",
    interviewQ: "Two of your predictors are correlated at 0.98. What happens to the model and what would you do?",
    quiz: [
      { q: "Which of these is NOT an assumption of ordinary least squares regression?",
        options: ["The relationship between the predictors and the mean of y is linear", "The errors have constant variance", "The errors are independent", "The predictors must be normally distributed"],
        answer: 3, why: "OLS makes no assumption that the predictors are normal. The assumptions are about the errors and the form of the relationship." },
      { q: "Residuals fan out as the fitted values increase. What is this called?",
        options: ["Multicollinearity", "Heteroscedasticity", "Autocorrelation", "Overfitting"],
        answer: 1, why: "Non-constant error variance is heteroscedasticity. A residuals-versus-fitted plot shows it." },
      { q: "Two predictors are correlated at 0.98. What is the main effect on a linear regression?",
        options: ["Coefficient estimates become unstable with large standard errors", "The model cannot be fitted at all", "Predictions on the training data become much worse", "The residuals become non-normal"],
        answer: 0, why: "Multicollinearity makes individual coefficients hard to separate, even though overall predictions can stay fine." }
    ]
  }
]);
