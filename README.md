# Bluestock Mutual Fund Capstone Project

## Project Overview

The Bluestock Mutual Fund Capstone Project focuses on building an end-to-end data analytics solution for mutual fund performance analysis. The project involves data extraction, transformation, and loading (ETL), exploratory data analysis (EDA), performance evaluation, and dashboard development to provide actionable insights for investors and financial analysts.

The solution automates data processing workflows and presents key findings through interactive visualizations, enabling efficient decision-making based on mutual fund performance metrics.

---

## Problem Statement

Investors often face challenges in analyzing large volumes of mutual fund data and comparing funds across different categories. Manual analysis is time-consuming and inefficient. This project addresses these challenges by developing an automated analytics pipeline and dashboard for mutual fund performance evaluation and insight generation.

---

## Project Objectives

* Collect and integrate mutual fund datasets.
* Design and implement an ETL pipeline.
* Perform data cleaning and preprocessing.
* Conduct exploratory data analysis (EDA).
* Evaluate fund performance using financial metrics.
* Develop an interactive dashboard.
* Generate business insights and recommendations.
* Build a scalable analytics framework.

---

## Technology Stack

### Programming Languages

* Python

### Libraries

* Pandas
* NumPy
* Matplotlib
* Seaborn
* Scikit-learn

### Visualization Tools

* Power BI / Tableau

### Version Control

* Git
* GitHub

---

## Project Architecture

Raw Data

↓
Extraction

↓
Transformation

↓
Validation

↓
Processed Data

↓
Dashboard & Reporting

---

## Dataset Description

### Mutual Fund NAV Data

Contains historical Net Asset Value (NAV) information for mutual funds.

### Fund Information Dataset

Contains metadata including:

* Fund Name
* Category
* Asset Management Company (AMC)
* Risk Classification

### Performance Dataset

Contains:

* Annual Returns
* CAGR
* Risk Metrics
* Benchmark Performance

---

## Project Structure

```text
Bluestock-MF-Capstone/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── run_pipeline.py
│
├── notebooks/
│
├── dashboard/
│
├── reports/
│
├── presentation/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/Bluestock-MF-Capstone.git
```

### Move to Project Directory

```bash
cd Bluestock-MF-Capstone
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the ETL Pipeline

Execute the master ETL script:

```bash
python scripts/run_pipeline.py
```

This script performs:

1. Data Extraction
2. Data Cleaning
3. Data Transformation
4. Data Loading

---

## Dashboard

### Power BI

Open:

```text
dashboard/Bluestock_MF_Dashboard.pbix
```

### Tableau

Open:

```text
dashboard/Bluestock_MF_Dashboard.twbx
```

### Published Dashboard (Optional)

Dashboard URL:

[Paste Dashboard Link Here]

---

## Key Findings

* Equity funds demonstrated the highest long-term returns.
* Debt funds exhibited lower volatility.
* Hybrid funds provided balanced risk-return characteristics.
* Risk-adjusted metrics offered better performance evaluation than raw returns alone.

---

## Deliverables

* Final Report (PDF)
* Power BI / Tableau Dashboard
* ETL Pipeline
* Source Code
* Presentation
* GitHub Repository

---

## Future Enhancements

* Automated scheduling using Airflow
* Real-time data ingestion
* Predictive analytics
* Portfolio recommendation system
* Cloud deployment

---

## Author

[siddhi A]

Bluestock Mutual Fund Capstone Project

Version 1.0

