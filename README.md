# 📊 Data Science Portfolio
 
Welcome to my Data Science portfolio!
This repository showcases my projects in **data analysis, business intelligence, experiment analysis, and machine learning**, highlighting my journey toward becoming a data-focused problem solver.
 
---
 
## About Me
 
* 🎓 Computer Science student at Mahidol University International College (MUIC), specializing in Data Science and Machine Learning
* 📊 Data Analytics & BI Intern at CJ Logistics Thailand, building Power BI dashboards and automated reporting across 5+ warehouses
* 🧪 Interested in experiment analysis, business intelligence, and machine learning
* 📈 Building projects to strengthen real-world problem-solving skills
---
 
## 🧠 Skills & Tools
 
* **Languages:** Python, SQL
* **Data & Libraries:** Pandas, NumPy, Scikit-learn, XGBoost, PyTorch, SHAP, sentence-transformers
* **BI & Visualization:** Tableau, Power BI (DAX), Excel, Matplotlib, Seaborn, Plotly
* **Statistics:** A/B test analysis, hypothesis testing (Benjamini-Hochberg), bootstrap confidence intervals
* **Tools:** Jupyter Notebook, Git/GitHub, GitHub Actions, Streamlit, Claude API
---
 
## 📂 Projects
 
### 🥇 1. Customer & Product Insights Dashboard (E-commerce)
 
**Overview:**
Interactive Tableau dashboards that analyze customer purchasing behavior, loyalty patterns, discount usage, and subscription adoption, supported by SQL pipelines that prepare the data. The project focuses on customer segmentation and identifying trends that help businesses improve retention and engagement.
 
**What I did:**
 
* Built **SQL pipelines** to extract, clean, and aggregate **100K+ customer records** into analysis-ready datasets
* Performed **Exploratory Data Analysis (EDA)** on customer transaction data
* Segmented customers into **New, Returning, and Loyal** groups based on purchase history
* Analyzed **subscription adoption** among repeat buyers
* Investigated the impact of **discount usage** on customer behavior
* Designed and published **3 interactive Tableau dashboards tracking 8+ KPIs** for customer loyalty and spending, turning findings into actionable insights for business stakeholders
**Tools:** `SQL` `Tableau`
 
**Key Skills:**
`Business Intelligence` `Dashboard Design` `KPI Tracking` `Customer Analytics` `EDA`
 
---
 
### 🥈 2. Automated Daily Intelligence Dashboard
 
**Overview:**
An automated daily briefing site that turns 20+ RSS feeds and live market data into structured summaries, rebuilt and published every morning without manual work.
 
**What I did:**
 
* Ingested **20+ RSS feeds** and live market data (**yfinance**) and used the **Claude API** to produce structured JSON summaries across **7 sections**
* Scheduled a **GitHub Actions** job that rebuilds and publishes the site to **GitHub Pages** each morning in about **2.5 minutes**
* Engineered for reliability: validates model output, retries with a larger token budget when a reply is cut off, checks the API before each build, and falls back to raw headlines when a summary fails
* Across **28 workflow runs, 21 succeeded**; traced and fixed all **7 failures** (Pages configuration, workflow location, folder-path errors)
* Prepared **3 days of content ahead** and added a second daily backup run so the page stays current when a scheduled run is skipped or fails
**Tools:** `Python` `Claude API` `GitHub Actions` `feedparser` `yfinance`
 
**Key Skills:**
`Automation` `Reliable Reporting` `API Integration` `Error Handling` `CI/CD`
 
---
 
### 🥉 3. Upworthy Headline Experiment Analysis
 
**Overview:**
An analysis of 22.7K Upworthy A/B test records (81M impressions) to understand what makes a headline win, and a ranking model that predicts winning headlines without leaking information across experiments.
 
**What I did:**
 
* Found that **question marks and exclamation marks** in headlines were associated with **lower click-through rates**, testing six headline features within experiments (**5,280 tests**, Benjamini-Hochberg correction, bootstrap confidence intervals)
* Reframed the task as **pairwise ranking** and added MPNet sentence embeddings, lifting mean pairwise accuracy from **57.8% to 61.5%** (+3.7 pp, paired-bootstrap 95% CI +2.7 to +4.7)
* Prevented leakage with **experiment-grouped 5-fold cross-validation** across 2,136 experiments and 17,270 comparison pairs
* Audited data integrity and excluded **165 experiments** with ambiguous repeated records
**Tools:** `Python` `scikit-learn` `XGBoost` `sentence-transformers` `SQL`
 
**Key Skills:**
`A/B Testing` `Experiment Analysis` `Hypothesis Testing` `NLP` `Leakage-Safe Validation`
 
---
 
### 4. Breast Cancer Prediction App
 
🔗 **Live App:** [https://breast-cancer-prediction29.streamlit.app](https://breast-cancer-prediction29.streamlit.app)
 
**Overview:**
A machine learning web app that predicts whether a tumor is **benign or malignant** using medical diagnostic features.
 
**What I did:**
 
* Performed **Exploratory Data Analysis (EDA)** and narrowed 30 features to 12 through correlation analysis
* Removed outliers with **Local Outlier Factor (LOF)**
* Built a **Random Forest Classifier** reaching **96% accuracy, 93% recall on malignant cases, and 0.995 ROC-AUC** on a held-out test set (baseline: 63% accuracy, 0% recall)
* Set the decision threshold at 0.30 to favor recall, using **SHAP** to explain predictions
* Deployed the model as a **Streamlit** app that returns malignancy probability and a low/moderate/high risk tier
**Key Skills:**
`Machine Learning` `EDA` `Model Deployment` `Explainability` `Data Cleaning`
 
---
 
## 📈 Goals
 
* Keep building **end-to-end data projects** that turn data into business decisions
* Strengthen skills in **experimentation, analytics, and machine learning**
* Master **model deployment and real-world applications**
---
 
## ⭐ Let’s Connect
 
If you find my work interesting, feel free to connect or follow my journey!

