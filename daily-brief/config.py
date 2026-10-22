"""Everything you are likely to want to change lives in this file.

Add or remove feed URLs, tickers, links, and topics freely. A feed that fails to load is
skipped (and reported in the build log), so a dead link never breaks the page.
"""

# Claude model used for summaries. Override with the MODEL environment variable.
DEFAULT_MODEL = "claude-haiku-5-5"

# How many headlines per section go to the model, and how old they may be.
MAX_ITEMS_PER_SECTION = 14
MAX_AGE_HOURS = 40

# For the AI and DS/ML sections the builder opens this many articles and reads the text,
# so summaries are based on more than the headline. Set to 0 to turn this off.
ARTICLE_TEXT_ITEMS = 6

# ---------------------------------------------------------------- feeds ----
FEEDS = {
    "world": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.theguardian.com/world/rss",
        "https://feeds.npr.org/1004/rss.xml",
        "https://rss.dw.com/rdf/rss-en-all",
    ],
    "thailand": [
        "https://www.bangkokpost.com/rss/data/topstories.xml",
        "https://www.bangkokpost.com/rss/data/business.xml",
        "https://www.thaipbsworld.com/feed/",
        "https://www.khaosodenglish.com/feed/",
        "https://www.thaienquirer.com/feed/",
    ],
    "ai": [
        "https://openai.com/news/rss.xml",
        "https://deepmind.google/blog/rss.xml",
        "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://huggingface.co/blog/feed.xml",
    ],
    # Thailand, English-language sources.
    "thailand": [
        "https://www.bangkokpost.com/rss/data/topstories.xml",
        "https://www.bangkokpost.com/rss/data/thailand.xml",
        "https://www.bangkokpost.com/rss/data/business.xml",
        "https://www.khaosodenglish.com/feed/",
    ],
    "markets": [
        "https://finance.yahoo.com/news/rssindex",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    ],
    # Data science / ML, plus anything else you want summarised.
    "reading": [
        "https://towardsdatascience.com/feed",
        "https://www.kdnuggets.com/feed",
        "https://machinelearningmastery.com/blog/feed/",
        "https://bair.berkeley.edu/blog/feed.xml",
        "https://research.google/blog/rss/",
        "https://huggingface.co/blog/feed.xml",
    ],
}

# -------------------------------------------------------------- markets ----
# Yahoo Finance symbols. ^SET.BK is the Thai SET index.
INDICES = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow": "^DJI",
    "SET (Thailand)": "^SET.BK",
    "Nikkei 225": "^N225",
    "Gold": "GC=F",
    "Oil (WTI)": "CL=F",
    "Bitcoin": "BTC-USD",
}

# Stocks to track for the "biggest moves", trend lines and earnings dates.
WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    "AMD", "NFLX", "JPM", "V", "LLY", "ORCL", "PLTR",
]

SPARK_DAYS = 30            # length of the little trend lines (trading days)
EARNINGS_WINDOW_DAYS = 45  # show earnings reports due within this many days

# One of these is explained in plain language each day (rotates by date).
FINANCE_LESSONS = [
    "How to read an income statement",
    "How to read a balance sheet",
    "How to read a cash flow statement",
    "What is in a 10-K annual report, and which sections matter most",
    "How to read an earnings release and earnings call",
    "P/E ratio and why it can mislead",
    "Free cash flow versus net income",
    "Operating margin versus gross margin",
    "Debt-to-equity and interest coverage",
    "What the footnotes and 'risk factors' sections reveal",
    "Revenue recognition and why it matters",
    "Reading a company's guidance",
    "Index funds versus individual stocks",
    "What moves a stock price on earnings day",
    "Dilution, buybacks and share count",
    "Return on equity and return on invested capital",
]

# ------------------------------------------------------------ DS/ML ----
# One concept per day (rotates by date), explained with a three-question quiz.
ML_CONCEPTS = [
    "The bias-variance tradeoff",
    "Overfitting and regularisation (L1 versus L2)",
    "Cross-validation and data leakage",
    "Gradient descent and learning rates",
    "Backpropagation in plain English",
    "Precision, recall and the F1 score",
    "ROC curves and AUC",
    "Class imbalance: weighting, resampling and thresholds",
    "Feature scaling, and why tree models do not need it",
    "Random forests versus gradient boosting",
    "Embeddings: how words become vectors",
    "The attention mechanism and transformers",
    "Fine-tuning versus prompting versus RAG",
    "Retrieval-augmented generation and where it goes wrong",
    "A/B testing: p-values, power and sample size",
    "Uplift modelling versus ordinary prediction",
    "Confidence intervals versus credible intervals",
    "Simpson's paradox and confounders",
    "Dropout and early stopping",
    "Batch normalisation",
    "PCA versus t-SNE and UMAP",
    "Clustering: k-means versus DBSCAN",
    "Time-series validation and forecasting pitfalls",
    "Calibration: when predicted probabilities lie",
    "Hyperparameter tuning: grid, random and Bayesian search",
    "Model drift and monitoring in production",
    "SQL window functions for analysts",
    "Causal inference: correlation versus causation",
]

# ----------------------------------------------------------------- jobs ----
# Search shortcuts that open a live search for you. Edit the words in the links to taste.
JOB_SEARCHES = [
    {"label": "ML and AI internships in Bangkok",
     "site": "LinkedIn",
     "url": "https://www.linkedin.com/jobs/search/?keywords=machine%20learning%20intern&location=Bangkok%2C%20Thailand"},
    {"label": "Data science internships in Bangkok",
     "site": "LinkedIn",
     "url": "https://www.linkedin.com/jobs/search/?keywords=data%20science%20intern&location=Bangkok%2C%20Thailand"},
    {"label": "Data scientist jobs in Bangkok",
     "site": "JobsDB",
     "url": "https://th.jobsdb.com/data-scientist-jobs/in-Bangkok"},
    {"label": "AI and LLM engineer jobs in Bangkok",
     "site": "LinkedIn",
     "url": "https://www.linkedin.com/jobs/search/?keywords=LLM%20engineer&location=Bangkok%2C%20Thailand"},
]

# Career pages to check for new openings.
COMPANY_CAREERS = [
    {"name": "Agoda", "url": "https://careersatagoda.com/"},
    {"name": "TikTok", "url": "https://lifeattiktok.com/"},
    {"name": "Grab", "url": "https://www.grab.careers/"},
    {"name": "McKinsey", "url": "https://www.mckinsey.com/careers"},
    {"name": "BCG", "url": "https://careers.bcg.com/"},
]

# Recent remote roles come from Remotive's public listings (free, once a day).
REMOTE_JOB_SEARCHES = ["machine learning", "data scientist"]
REMOTE_JOBS_SHOWN = 10

# One of these becomes the daily learning card with a quiz question (rotates by date).
LEARNING_TOPICS = [
    "Overfitting and underfitting",
    "The bias-variance tradeoff",
    "Train, validation and test sets",
    "Cross-validation",
    "Gradient descent",
    "Learning rate and why it matters",
    "Regularization (L1 and L2)",
    "Precision, recall and F1",
    "ROC curves and AUC",
    "Class imbalance and how to handle it",
    "Feature scaling and normalization",
    "Data leakage",
    "Decision trees and random forests",
    "Gradient boosting (XGBoost, LightGBM)",
    "Backpropagation",
    "Activation functions",
    "Batch normalization and dropout",
    "Embeddings",
    "The attention mechanism",
    "Transformers in plain English",
    "How large language models are trained",
    "Fine-tuning versus prompting versus RAG",
    "Retrieval-augmented generation (RAG)",
    "Hallucinations in LLMs and how to reduce them",
    "A/B testing and statistical significance",
    "P-values and what they do not mean",
    "Confidence intervals",
    "Correlation versus causation",
    "Uplift modelling",
    "Clustering with k-means",
    "Principal component analysis (PCA)",
    "Time-series forecasting basics",
    "SQL window functions",
    "Model monitoring and drift in production",
]

# -------------------------------------------------------------- writing ----
READER_NOTE = (
    "The reader is a computer science student in Bangkok who follows data science, "
    "machine learning and markets. Write clearly and concisely, in plain English."
)
