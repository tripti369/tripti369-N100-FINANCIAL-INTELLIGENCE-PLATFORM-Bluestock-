# tripti369-N100-FINANCIAL-INTELLIGENCE-PLATFORM-Bluestock-

# 📈 Nifty100 Financial Intelligence Platform

A Financial Analytics Dashboard built using **Python, Streamlit, SQLite, Pandas, and Plotly** to analyze Nifty100 companies.

The platform consolidates financial datasets into a single analytics dashboard where users can explore company fundamentals, screen stocks, compare peers, analyze sectors, visualize trends, and generate financial insights.

---

## 🚀 Live Demo

🔗 https://n100-financial-intelligence-platform.streamlit.app/

---

# Project Overview

The Nifty100 Financial Intelligence Platform transforms multiple financial datasets into an interactive analytics application.

Instead of manually browsing spreadsheets, users can:

- Explore company profiles
- Screen companies using financial metrics
- Compare peer companies
- Analyze sector-wise performance
- Study historical financial trends
- View capital structure
- Analyze cash flow
- Generate financial reports
- Review valuation indicators
- View NLP-based insights
- Obtain portfolio summaries

---

# Features

## 📊 Dashboard
- Overview statistics
- Total companies
- ROE availability
- ROCE availability
- Book value summary

---

## 🏢 Company Profile

- Company information
- Website links
- Business description
- Financial overview

---

## 🔍 Stock Screener

Filter companies using financial metrics such as:

- ROE
- ROCE
- Book Value

Download screened companies as CSV.

---

## 📊 Peer Comparison

Compare companies within similar sectors.

Provides:

- Peer groups
- Financial comparison
- Relative performance

---

## 📈 Financial Trends

Visualize historical trends using interactive charts.

Includes:

- Sales
- Profit
- Operating Profit
- EPS

---

## 🏭 Sector Analysis

Analyze companies sector-wise.

Displays:

- Sector distribution
- Company counts
- Industry classification

---

## 💰 Capital Structure

Analyze:

- Market Capitalization
- Equity information
- Financial strength

---

## 💸 Cash Flow Intelligence

Review company cash flow information including:

- Operating Cash Flow
- Investing Cash Flow
- Financing Cash Flow

---

## 📑 Company Reports

Access financial reports and company-related information.

---

## 📉 Valuation & Health

Provides valuation indicators including:

- Book Value
- ROE
- ROCE
- Financial health metrics

---

## 🤖 NLP Insights

Summarizes company analysis using available textual datasets.

---

## 📦 Portfolio Summary

Provides an overall financial snapshot across companies.

---

# Project Architecture

```
Excel Datasets
       │
       ▼
 Data Cleaning (Pandas)
       │
       ▼
SQLite Database
       │
       ▼
Data Loader (utils/db.py)
       │
       ▼
Streamlit Dashboard
       │
       ▼
Interactive Analytics
```

---

# Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python |
| Dashboard | Streamlit |
| Database | SQLite |
| Data Analysis | Pandas |
| Charts | Plotly |
| Data Source | Excel Datasets |

---

# Project Structure

```
nifty100-internship/
│
├── app.py
├── nifty100.db
├── utils/
│     └── db.py
│
├── pages/
│     ├── 02_Profile.py
│     ├── 03_Screener.py
│     ├── 04_Peers.py
│     ├── 05_Trends.py
│     ├── 06_Sectors.py
│     ├── 07_Capital.py
│     ├── 08_Reports.py
│     ├── CashFlow.py
│     ├── Valuation.py
│     ├── NLP_Insights.py
│     └── Portfolio.py
│
├── supporting datasets/
│
└── README.md
```

---

# Dataset

The platform integrates financial information including:

- Companies
- Profit & Loss
- Balance Sheet
- Cash Flow
- Financial Ratios
- Market Capitalization
- Stock Prices
- Sector Information
- Peer Groups
- Company Analysis
- Pros & Cons
- Documents

---

# Installation

Clone the repository

```bash
git clone <repository-url>
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

# Future Improvements

- AI-powered financial assistant
- Stock recommendation engine
- Portfolio optimization
- Real-time NSE/BSE integration
- Risk prediction models
- LLM-based report generation
- Financial forecasting

---

# Author

**Tripti Tiwari**

Built as part of a Financial Intelligence Analytics Project using Python and Streamlit.

---

# License

This project is intended for educational and learning purposes.
