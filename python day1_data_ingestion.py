"""
BLUESTOCK FINTECH — Mutual Fund Analytics Capstone
DAY 1: Data Ingestion Script
Run this file to load and inspect all 10 datasets.
Usage: python day1_data_ingestion.py
"""

import pandas as pd
import os
import sys

# Fix for Windows terminal encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─────────────────────────────────────────────
# STEP 1: Set the path to your CSV files folder
# ─────────────────────────────────────────────
# Change this to wherever you saved the 10 CSV files
DATA_FOLDER = "data/raw"

# ─────────────────────────────────────────────
# STEP 2: Load all 10 CSV files
# ─────────────────────────────────────────────

print("=" * 60)
print("BLUESTOCK FINTECH — Loading All Datasets")
print("=" * 60)

# Load each file into a pandas DataFrame
fund_master         = pd.read_csv(os.path.join(DATA_FOLDER, "01_fund_master.csv"))
nav_history         = pd.read_csv(os.path.join(DATA_FOLDER, "02_nav_history.csv"), parse_dates=["date"])
aum_by_fund_house   = pd.read_csv(os.path.join(DATA_FOLDER, "03_aum_by_fund_house.csv"), parse_dates=["date"])
monthly_sip         = pd.read_csv(os.path.join(DATA_FOLDER, "04_monthly_sip_inflows.csv"))
category_inflows    = pd.read_csv(os.path.join(DATA_FOLDER, "05_category_inflows.csv"))
folio_count         = pd.read_csv(os.path.join(DATA_FOLDER, "06_industry_folio_count.csv"))
scheme_performance  = pd.read_csv(os.path.join(DATA_FOLDER, "07_scheme_performance.csv"))
transactions        = pd.read_csv(os.path.join(DATA_FOLDER, "08_investor_transactions.csv"), parse_dates=["transaction_date"])
portfolio_holdings  = pd.read_csv(os.path.join(DATA_FOLDER, "09_portfolio_holdings.csv"))
benchmark_indices   = pd.read_csv(os.path.join(DATA_FOLDER, "10_benchmark_indices.csv"), parse_dates=["date"])

print("\n[OK] All 10 files loaded successfully!\n")

# ─────────────────────────────────────────────
# STEP 3: Print a summary of each dataset
# ─────────────────────────────────────────────

datasets = {
    "01 Fund Master":           fund_master,
    "02 NAV History":           nav_history,
    "03 AUM by Fund House":     aum_by_fund_house,
    "04 Monthly SIP Inflows":   monthly_sip,
    "05 Category Inflows":      category_inflows,
    "06 Industry Folio Count":  folio_count,
    "07 Scheme Performance":    scheme_performance,
    "08 Investor Transactions": transactions,
    "09 Portfolio Holdings":    portfolio_holdings,
    "10 Benchmark Indices":     benchmark_indices,
}

for name, df in datasets.items():
    print(f"─── {name} ───")
    print(f"  Rows: {df.shape[0]:,}   Columns: {df.shape[1]}")
    print(f"  Columns: {list(df.columns)}")
    missing = df.isnull().sum().sum()
    print(f"  Missing values: {missing}")
    print()

# ─────────────────────────────────────────────
# STEP 4: Quick validation checks
# ─────────────────────────────────────────────

print("=" * 60)
print("VALIDATION CHECKS")
print("=" * 60)

# Check 1: How many unique funds are there?
print(f"\n[OK] Unique funds in fund_master: {fund_master['amfi_code'].nunique()}")
print(f"[OK] Unique funds in nav_history: {nav_history['amfi_code'].nunique()}")

# Check 2: Date range of NAV data
print(f"\n[OK] NAV History date range: {nav_history['date'].min().date()} → {nav_history['date'].max().date()}")

# Check 3: Fund houses
print(f"\n[OK] Fund houses ({fund_master['fund_house'].nunique()} total):")
for fh in sorted(fund_master['fund_house'].unique()):
    print(f"   - {fh}")

# Check 4: Transaction types
print(f"\n[OK] Transaction types:")
print(transactions['transaction_type'].value_counts().to_string())

# Check 5: Categories
print(f"\n[OK] Fund categories:")
print(fund_master['category'].value_counts().to_string())

# Check 6: Benchmark indices available
print(f"\n[OK] Benchmark indices:")
print(benchmark_indices['index_name'].value_counts().to_string())

# Check 7: Are all AMFI codes in fund_master present in nav_history?
master_codes = set(fund_master['amfi_code'])
nav_codes = set(nav_history['amfi_code'])
missing_in_nav = master_codes - nav_codes
if missing_in_nav:
    print(f"\n[WARN]  AMFI codes in fund_master but NOT in nav_history: {missing_in_nav}")
else:
    print(f"\n[OK] All AMFI codes in fund_master exist in nav_history")

print("\n" + "=" * 60)
print("DAY 1 COMPLETE [OK]")
print("Next step: Run day2_data_cleaning.py")
print("=" * 60)