# 🚦 Toll AI Insights

An AI-powered analytics dashboard for toll transaction data built using **Streamlit**, **Pandas**, and **Plotly**.

The application transforms raw toll transaction reports into interactive dashboards, helping toll operators and management teams quickly understand traffic patterns, lane performance, vehicle distribution, payment trends, and operational insights.

---

## Features

- 📊 Executive Dashboard
- 🚗 Vehicle Class Analysis
- 🚦 Lane Performance Analysis
- ⏰ Hourly Traffic Trends
- 💳 Payment Mode Analysis
- ⚠️ Exempt Vehicle Detection
- 📈 Daily Report Comparison
- 🤖 AI-generated Operational Insights
- 📋 Raw Data Explorer

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly Express
- OpenPyXL

---

## Project Structure

```
Toll-AI-Insights/
│
├── app.py              # Dashboard (Version 1)
├── app2.py             # Dashboard with comparison & AI insights
├── parser.py
├── parser2.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository

```bash
https://github.com/rajchouhan19/Toll-Data-Insights
```

Move into the project

```bash
cd Toll-AI-Insights
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app2.py
```

---

## Dataset

The application is designed to work with Toll Transaction Detail Reports exported from Toll Management Systems.

Typical fields include:

- Transaction Number
- Date & Time
- Lane
- Vehicle Class
- Payment Mode
- Journey Type
- Vehicle Number
- Revenue
- Exempt Information

*Sample datasets are not included due to confidentiality.*

---

## Future Scope

- AI-powered natural language summaries
- Toll operational recommendations
- Traffic forecasting
- Revenue prediction
- Location-aware insights using LLMs
- Intelligent anomaly detection
- Multi-day trend analysis
- SaaS deployment for toll operators

---

## Disclaimer

This project is a prototype developed for demonstrating AI-driven toll analytics and operational intelligence. Confidential operational datasets are not included in this repository.
