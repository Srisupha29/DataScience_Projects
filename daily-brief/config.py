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

# The learning card, the book of the day and the Spanish reading are prepared for today AND
# the next few days, and the page shows the one that matches the date on your device. That
# way they still change every day even if GitHub skips a scheduled run. Costs a few cents more.
LOOKAHEAD_DAYS = 3

# ---------------------------------------------------------------- books ----
# Non-fiction only. Each entry: (category, title, author, one-line description).
# One book is featured per day (the categories take turns), and Claude writes a
# short summary of it. Add your own books to this list.
BOOKS = [
    # Business
    ("Business", "Good to Great", "Jim Collins", "Research on what lets a few companies sustain outstanding results while similar ones stall."),
    ("Business", "The Lean Startup", "Eric Ries", "Build, measure and learn in small experiments instead of betting on big guesses."),
    ("Business", "Zero to One", "Peter Thiel with Blake Masters", "How to build something new rather than copy what already works."),
    ("Business", "The Hard Thing About Hard Things", "Ben Horowitz", "Candid lessons on running a company when there are no easy answers."),
    ("Business", "Crossing the Chasm", "Geoffrey A. Moore", "How technology products move from early adopters to the mainstream market."),
    ("Business", "The Innovator's Dilemma", "Clayton M. Christensen", "Why well-run companies get overtaken by cheaper, simpler challengers."),
    ("Business", "Blue Ocean Strategy", "W. Chan Kim and Renée Mauborgne", "Finding new markets with little competition instead of fighting over existing ones."),
    ("Business", "High Output Management", "Andrew S. Grove", "Managing a team like a production system, from Intel's former CEO."),
    ("Business", "Measure What Matters", "John Doerr", "How goals and key results (OKRs) keep teams focused."),
    ("Business", "Never Split the Difference", "Chris Voss with Tahl Raz", "Negotiation tactics from a former FBI hostage negotiator."),
    ("Business", "Principles: Life and Work", "Ray Dalio", "A hedge-fund founder's rules for decisions, work and radical transparency."),
    # Stocks and investing
    ("Stocks & investing", "The Intelligent Investor", "Benjamin Graham", "The classic case for value investing and a margin of safety."),
    ("Stocks & investing", "A Random Walk Down Wall Street", "Burton G. Malkiel", "Why beating the market is hard, and why index funds make sense."),
    ("Stocks & investing", "The Little Book of Common Sense Investing", "John C. Bogle", "The case for low-cost index funds, from Vanguard's founder."),
    ("Stocks & investing", "One Up on Wall Street", "Peter Lynch", "Using what you know as an everyday observer to find good stocks."),
    ("Stocks & investing", "The Psychology of Money", "Morgan Housel", "Short essays on why behaviour matters more than intelligence with money."),
    ("Stocks & investing", "Common Stocks and Uncommon Profits", "Philip A. Fisher", "A qualitative checklist for finding outstanding growth companies."),
    ("Stocks & investing", "The Little Book That Beats the Market", "Joel Greenblatt", "A simple, rule-based approach to value investing."),
    ("Stocks & investing", "Financial Intelligence", "Karen Berman and Joe Knight", "How to read financial statements without an accounting degree."),
    ("Stocks & investing", "The Most Important Thing", "Howard Marks", "Risk, market cycles and second-level thinking."),
    ("Stocks & investing", "The Little Book of Valuation", "Aswath Damodaran", "How to put a value on a company, step by step."),
    ("Stocks & investing", "Against the Gods", "Peter L. Bernstein", "The history of how people learned to measure and manage risk."),
    ("Stocks & investing", "The Big Short", "Michael Lewis", "The story of the few who bet against the 2008 housing bubble."),
    # Self-help
    ("Self-help", "Atomic Habits", "James Clear", "Small changes that compound into big results, and how to make habits stick."),
    ("Self-help", "Deep Work", "Cal Newport", "Why focused, distraction-free work is rare and valuable, and how to protect it."),
    ("Self-help", "The 7 Habits of Highly Effective People", "Stephen R. Covey", "A principle-based approach to personal effectiveness."),
    ("Self-help", "How to Win Friends and Influence People", "Dale Carnegie", "Timeless advice on getting along with people."),
    ("Self-help", "Essentialism", "Greg McKeown", "Doing fewer things, but the right ones."),
    ("Self-help", "The Power of Habit", "Charles Duhigg", "The science of how habits form and how to change them."),
    ("Self-help", "Grit", "Angela Duckworth", "Why passion and perseverance can matter as much as talent."),
    ("Self-help", "So Good They Can't Ignore You", "Cal Newport", "Why building rare skills beats 'following your passion' for a career."),
    ("Self-help", "Make It Stick", "Peter C. Brown, Henry L. Roediger III and Mark A. McDaniel", "What learning science says about studying and remembering."),
    ("Self-help", "Ultralearning", "Scott H. Young", "Strategies for learning hard skills quickly and independently."),
    ("Self-help", "Getting Things Done", "David Allen", "A system for capturing tasks and clearing your mind."),
    ("Self-help", "Range", "David Epstein", "Why generalists and broad experience can beat early specialisation."),
    # Economics
    ("Economics", "Freakonomics", "Steven D. Levitt and Stephen J. Dubner", "Applying economic thinking to surprising everyday questions."),
    ("Economics", "Basic Economics", "Thomas Sowell", "Economics explained in plain language, from prices to trade."),
    ("Economics", "Nudge", "Richard H. Thaler and Cass R. Sunstein", "How small changes in how choices are presented steer behaviour."),
    ("Economics", "Misbehaving", "Richard H. Thaler", "How the field of behavioural economics came to be."),
    ("Economics", "The Worldly Philosophers", "Robert L. Heilbroner", "The lives and ideas of the great economic thinkers."),
    ("Economics", "Poor Economics", "Abhijit V. Banerjee and Esther Duflo", "An evidence-based look at how poor households actually make decisions."),
    ("Economics", "Why Nations Fail", "Daron Acemoglu and James A. Robinson", "How institutions shape which countries become rich or poor."),
    ("Economics", "The Undercover Economist", "Tim Harford", "Everyday economics, from coffee prices to traffic."),
    ("Economics", "Economics in One Lesson", "Henry Hazlitt", "A short, free-market case for looking past the immediate effects of policy."),
    ("Economics", "Factfulness", "Hans Rosling with Ola Rosling and Anna Rosling Rönnlund", "Habits of thinking that distort how we see the world, and the data that corrects them."),
    ("Economics", "The Signal and the Noise", "Nate Silver", "Why most predictions fail and how to forecast better."),
    # Psychology
    ("Psychology", "Thinking, Fast and Slow", "Daniel Kahneman", "Two modes of thinking and the biases they produce."),
    ("Psychology", "Influence", "Robert B. Cialdini", "Six principles of persuasion and why they work."),
    ("Psychology", "Predictably Irrational", "Dan Ariely", "Experiments showing how our decisions are systematically biased."),
    ("Psychology", "Quiet", "Susan Cain", "The strengths of introverts in a world that rewards extroversion."),
    ("Psychology", "Emotional Intelligence", "Daniel Goleman", "Why self-awareness and empathy matter as much as IQ."),
    ("Psychology", "Flow", "Mihaly Csikszentmihalyi", "The state of deep absorption and what makes work and play fulfilling."),
    ("Psychology", "The Happiness Hypothesis", "Jonathan Haidt", "Ancient wisdom tested against modern psychology."),
    ("Psychology", "Drive", "Daniel H. Pink", "What really motivates people: autonomy, mastery and purpose."),
    ("Psychology", "Thinking in Bets", "Annie Duke", "Making decisions under uncertainty, from a former professional poker player."),
    ("Psychology", "Mindset", "Carol S. Dweck", "How believing abilities can grow shapes learning and success."),
    ("Psychology", "Man's Search for Meaning", "Viktor E. Frankl", "A psychiatrist's account of surviving the Nazi camps and finding purpose."),
    ("Psychology", "Outliers", "Malcolm Gladwell", "What lies behind unusually successful people."),
]

# ------------------------------------------------------------- Spanish ----
# Level of the daily reading, on the CEFR scale: A1, A2, B1, B2, C1.
# Change this as you improve.
SPANISH_LEVEL = "B1"

# Themes rotate by date.
SPANISH_THEMES = [
    "A morning in a café in Madrid",
    "Ordering food and talking with a waiter in Mexico City",
    "A student's first day at a university in Colombia",
    "How a small business in Buenos Aires uses social media",
    "A short news-style piece about artificial intelligence changing jobs",
    "Planning a weekend trip to Barcelona",
    "A conversation between two friends about saving money",
    "The history of a famous Latin American dish",
    "Remote work and life as a digital nomad in Latin America",
    "A day in the life of a data scientist in Santiago",
    "Festivals and traditions in Spain",
    "A short biography of a famous Spanish-speaking scientist",
    "Health and daily routines: sleep, exercise and food",
    "Technology and smartphones in everyday life",
    "The stock market explained simply for a beginner",
    "A job interview in Spanish",
    "Weather and the seasons in Chile and Argentina",
    "Music and dance in the Caribbean",
    "Taking public transport and asking for directions in Lima",
    "Learning a language: tips from a teacher",
    "A true-to-life travel anecdote about a funny misunderstanding",
    "Renewable energy in Spain",
    "A visit to the doctor or the pharmacy",
    "Football culture in Spanish-speaking countries",
    "Bangkok through the eyes of a Spanish-speaking visitor",
]

# -------------------------------------------------------------- writing ----
READER_NOTE = (
    "The reader is a computer science student in Bangkok who follows data science, "
    "machine learning and markets. Write clearly and concisely, in plain English."
)
