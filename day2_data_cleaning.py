"""
BLUESTOCK FINTECH - Mutual Fund Analytics Capstone
DAY 2: Data Cleaning + SQLite Database
Run this file after day1_data_ingestion_fixed.py
Usage: python day2_data_cleaning.py
"""

import pandas as pd
import numpy as np
import os
import sys
import sqlite3
from sqlalchemy import create_engine

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─────────────────────────────────────────────
# PATHS - adjust if needed
# ─────────────────────────────────────────────
RAW   = "data/raw"
CLEAN = "data/processed"
DB    = "data/db/bluestock_mf.db"

os.makedirs(CLEAN, exist_ok=True)
os.makedirs("data/db", exist_ok=True)

print("=" * 60)
print("DAY 2: Data Cleaning + SQLite Database")
print("=" * 60)


# ─────────────────────────────────────────────
# LOAD RAW FILES
# ─────────────────────────────────────────────
fund_master        = pd.read_csv(f"{RAW}/01_fund_master.csv")
nav_history        = pd.read_csv(f"{RAW}/02_nav_history.csv", parse_dates=["date"])
aum_by_fund_house  = pd.read_csv(f"{RAW}/03_aum_by_fund_house.csv", parse_dates=["date"])
monthly_sip        = pd.read_csv(f"{RAW}/04_monthly_sip_inflows.csv")
category_inflows   = pd.read_csv(f"{RAW}/05_category_inflows.csv")
folio_count        = pd.read_csv(f"{RAW}/06_industry_folio_count.csv")
scheme_perf        = pd.read_csv(f"{RAW}/07_scheme_performance.csv")
transactions       = pd.read_csv(f"{RAW}/08_investor_transactions.csv", parse_dates=["transaction_date"])
portfolio          = pd.read_csv(f"{RAW}/09_portfolio_holdings.csv")
benchmark          = pd.read_csv(f"{RAW}/10_benchmark_indices.csv", parse_dates=["date"])

print("\n[OK] All raw files loaded\n")


# ─────────────────────────────────────────────
# CLEAN 1: fund_master
# ─────────────────────────────────────────────
print("--- Cleaning 01_fund_master ---")
fm = fund_master.copy()
fm['launch_date'] = pd.to_datetime(fm['launch_date'])
fm['amfi_code'] = fm['amfi_code'].astype(str)
fm = fm.drop_duplicates(subset='amfi_code')
print(f"  Rows: {len(fm)} | Missing: {fm.isnull().sum().sum()}")
fm.to_csv(f"{CLEAN}/01_fund_master_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 2: nav_history
# ─────────────────────────────────────────────
print("\n--- Cleaning 02_nav_history ---")
nav = nav_history.copy()
nav['amfi_code'] = nav['amfi_code'].astype(str)
nav = nav.sort_values(['amfi_code', 'date'])
nav = nav.drop_duplicates(subset=['amfi_code', 'date'])

# Remove rows where NAV is zero or negative
before = len(nav)
nav = nav[nav['nav'] > 0]
print(f"  Removed {before - len(nav)} rows with NAV <= 0")

# Forward-fill missing NAV values per fund (for weekends/holidays)
nav = nav.set_index('date').groupby('amfi_code')['nav'].apply(
    lambda x: x.resample('D').last().ffill()
).reset_index()
nav.columns = ['amfi_code', 'date', 'nav']

# Compute daily return %
nav = nav.sort_values(['amfi_code', 'date'])
nav['daily_return_pct'] = nav.groupby('amfi_code')['nav'].pct_change() * 100
nav['daily_return_pct'] = nav['daily_return_pct'].round(4)

print(f"  Rows after cleaning: {len(nav):,}")
print(f"  Missing values: {nav.isnull().sum().sum()}")
nav.to_csv(f"{CLEAN}/02_nav_history_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 3: aum_by_fund_house
# ─────────────────────────────────────────────
print("\n--- Cleaning 03_aum_by_fund_house ---")
aum = aum_by_fund_house.copy()
aum = aum.drop_duplicates()
aum = aum.dropna(subset=['aum_crore'])
print(f"  Rows: {len(aum)} | Missing: {aum.isnull().sum().sum()}")
aum.to_csv(f"{CLEAN}/03_aum_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 4: monthly_sip_inflows
# ─────────────────────────────────────────────
print("\n--- Cleaning 04_monthly_sip_inflows ---")
sip = monthly_sip.copy()
# yoy_growth_pct is empty for first year - fill with 0
sip['yoy_growth_pct'] = pd.to_numeric(sip['yoy_growth_pct'], errors='coerce').fillna(0)
sip = sip.drop_duplicates(subset='month')
print(f"  Rows: {len(sip)} | Missing: {sip.isnull().sum().sum()}")
sip.to_csv(f"{CLEAN}/04_sip_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 5: category_inflows
# ─────────────────────────────────────────────
print("\n--- Cleaning 05_category_inflows ---")
cat = category_inflows.copy()
cat = cat.drop_duplicates()
cat['net_inflow_crore'] = pd.to_numeric(cat['net_inflow_crore'], errors='coerce')
print(f"  Rows: {len(cat)} | Missing: {cat.isnull().sum().sum()}")
cat.to_csv(f"{CLEAN}/05_category_inflows_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 6: folio_count
# ─────────────────────────────────────────────
print("\n--- Cleaning 06_industry_folio_count ---")
folio = folio_count.copy()
folio = folio.drop_duplicates(subset='month')
print(f"  Rows: {len(folio)} | Missing: {folio.isnull().sum().sum()}")
folio.to_csv(f"{CLEAN}/06_folio_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 7: scheme_performance
# ─────────────────────────────────────────────
print("\n--- Cleaning 07_scheme_performance ---")
perf = scheme_perf.copy()
perf['amfi_code'] = perf['amfi_code'].astype(str)

# Validate numeric columns
numeric_cols = ['return_1yr_pct','return_3yr_pct','return_5yr_pct',
                'sharpe_ratio','alpha','beta','max_drawdown_pct','expense_ratio_pct']
for col in numeric_cols:
    perf[col] = pd.to_numeric(perf[col], errors='coerce')

# Flag unusual Sharpe ratios
unusual = perf[perf['sharpe_ratio'] < 0]
if len(unusual) > 0:
    print(f"  [WARN] {len(unusual)} funds with negative Sharpe ratio")

# Validate expense ratio range (should be 0.1% to 2.5%)
out_of_range = perf[(perf['expense_ratio_pct'] < 0.1) | (perf['expense_ratio_pct'] > 2.5)]
if len(out_of_range) > 0:
    print(f"  [WARN] {len(out_of_range)} funds with unusual expense ratio")

print(f"  Rows: {len(perf)} | Missing: {perf.isnull().sum().sum()}")
perf.to_csv(f"{CLEAN}/07_scheme_performance_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 8: investor_transactions
# ─────────────────────────────────────────────
print("\n--- Cleaning 08_investor_transactions ---")
tx = transactions.copy()
tx['amfi_code'] = tx['amfi_code'].astype(str)

# Standardise transaction_type capitalization
tx['transaction_type'] = tx['transaction_type'].str.strip().str.title()
valid_types = ['Sip', 'Lumpsum', 'Redemption']
invalid = tx[~tx['transaction_type'].isin(valid_types)]
if len(invalid) > 0:
    print(f"  [WARN] {len(invalid)} rows with unexpected transaction_type")

# Remove rows with amount <= 0
before = len(tx)
tx = tx[tx['amount_inr'] > 0]
print(f"  Removed {before - len(tx)} rows with amount <= 0")

# KYC status check
print(f"  KYC status breakdown:\n{tx['kyc_status'].value_counts().to_string()}")

print(f"  Rows: {len(tx):,} | Missing: {tx.isnull().sum().sum()}")
tx.to_csv(f"{CLEAN}/08_transactions_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 9: portfolio_holdings
# ─────────────────────────────────────────────
print("\n--- Cleaning 09_portfolio_holdings ---")
port = portfolio.copy()
port['amfi_code'] = port['amfi_code'].astype(str)
port = port.drop_duplicates()
port = port[port['weight_pct'] > 0]
print(f"  Rows: {len(port)} | Missing: {port.isnull().sum().sum()}")
port.to_csv(f"{CLEAN}/09_portfolio_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# CLEAN 10: benchmark_indices
# ─────────────────────────────────────────────
print("\n--- Cleaning 10_benchmark_indices ---")
bench = benchmark.copy()
bench = bench.sort_values(['index_name', 'date'])
bench = bench.drop_duplicates(subset=['index_name', 'date'])
bench = bench[bench['close_value'] > 0]
print(f"  Rows: {len(bench):,} | Missing: {bench.isnull().sum().sum()}")
bench.to_csv(f"{CLEAN}/10_benchmark_clean.csv", index=False)
print("  [OK] Saved")


# ─────────────────────────────────────────────
# LOAD INTO SQLITE DATABASE
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("Loading data into SQLite database...")
print("=" * 60)

engine = create_engine(f"sqlite:///{DB}")

tables = {
    "dim_fund":           fm,
    "fact_nav":           nav,
    "fact_aum":           aum,
    "fact_sip_industry":  sip,
    "fact_category_inflows": cat,
    "fact_folio_count":   folio,
    "fact_performance":   perf,
    "fact_transactions":  tx,
    "fact_portfolio":     port,
    "fact_benchmark":     bench,
}

for table_name, df in tables.items():
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"  [OK] {table_name}: {len(df):,} rows loaded")

print("\n[OK] Database created: data/db/bluestock_mf.db")


# ─────────────────────────────────────────────
# RUN 10 SQL QUERIES
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("RUNNING 10 SQL QUERIES")
print("=" * 60)

conn = sqlite3.connect(DB)

queries = {
    "1. Top 5 funds by AUM": """
        SELECT scheme_name, fund_house, aum_crore
        FROM fact_performance
        ORDER BY aum_crore DESC LIMIT 5
    """,
    "2. Average NAV per fund (last 30 days)": """
        SELECT amfi_code, ROUND(AVG(nav),2) as avg_nav
        FROM fact_nav
        WHERE date >= date('now', '-30 days')
        GROUP BY amfi_code
        ORDER BY avg_nav DESC LIMIT 5
    """,
    "3. SIP inflow by year": """
        SELECT substr(month,1,4) as year, ROUND(SUM(sip_inflow_crore),0) as total_sip
        FROM fact_sip_industry
        GROUP BY year ORDER BY year
    """,
    "4. Transactions by state (top 5)": """
        SELECT state, COUNT(*) as num_transactions, ROUND(SUM(amount_inr)/1e7,2) as total_cr
        FROM fact_transactions
        GROUP BY state ORDER BY num_transactions DESC LIMIT 5
    """,
    "5. Funds with expense ratio < 1%": """
        SELECT scheme_name, fund_house, expense_ratio_pct
        FROM dim_fund WHERE expense_ratio_pct < 1.0
        ORDER BY expense_ratio_pct LIMIT 5
    """,
    "6. Top 5 funds by Sharpe ratio": """
        SELECT scheme_name, sharpe_ratio, return_3yr_pct
        FROM fact_performance
        ORDER BY sharpe_ratio DESC LIMIT 5
    """,
    "7. Transaction type breakdown": """
        SELECT transaction_type, COUNT(*) as count,
               ROUND(SUM(amount_inr)/1e7,2) as total_crore
        FROM fact_transactions GROUP BY transaction_type
    """,
    "8. Benchmark index date range": """
        SELECT index_name, MIN(date) as from_date, MAX(date) as to_date, COUNT(*) as days
        FROM fact_benchmark GROUP BY index_name
    """,
    "9. Funds with highest Alpha": """
        SELECT scheme_name, alpha, return_3yr_pct, benchmark_3yr_pct
        FROM fact_performance ORDER BY alpha DESC LIMIT 5
    """,
    "10. SIP transactions by age group": """
        SELECT age_group, COUNT(*) as count, ROUND(AVG(amount_inr),0) as avg_amount
        FROM fact_transactions WHERE transaction_type = 'Sip'
        GROUP BY age_group ORDER BY age_group
    """,
}

for title, sql in queries.items():
    print(f"\n--- {title} ---")
    result = pd.read_sql_query(sql, conn)
    print(result.to_string(index=False))

conn.close()

print("\n" + "=" * 60)

