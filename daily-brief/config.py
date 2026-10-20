"""Everything you are likely to want to change lives in this file.

Add or remove feed URLs, tickers, and topics freely. A feed that fails to load is
skipped (and reported in the build log), so a dead link never breaks the page.
"""

# Claude model used for summaries. Override with the MODEL environment variable.
DEFAULT_MODEL = "claude-haiku-5-5"

# How many headlines per section go to the model, and how old they may be.
MAX_ITEMS_PER_SECTION = 14
MAX_AGE_HOURS = 40

# ---------------------------------------------------------------- feeds ----
FEEDS = {
    "world": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.theguardian.com/world/rss",
        "https://feeds.npr.org/1004/rss.xml",
        "https://rss.dw.com/rdf/rss-en-all",
    ],
    "ai": [
        "https://openai.com/news/rss.xml",
        "https://deepmind.google/blog/rss.xml",
        "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://huggingface.co/blog/feed.xml",
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

# Stocks to track for the "biggest moves" and "stocks to watch" lists.
WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    "AMD", "NFLX", "JPM", "V", "LLY", "ORCL", "PLTR",
]

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

# -------------------------------------------------------------- writing ----
READER_NOTE = (
    "The reader is a computer science student in Bangkok who follows data science, "
    "machine learning and markets. Write clearly and concisely, in plain English."
)
