

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CLEAN   = "data/processed"
CHARTS  = "data/charts"
os.makedirs(CHARTS, exist_ok=True)

sns.set_theme(style="whitegrid")
COLORS = ["#1F4E79","#2E75B6","#2ECC71","#F39C12","#E74C3C","#8E44AD","#1ABC9C","#E67E22"]

print("=" * 60)
print("DAY 3: Exploratory Data Analysis")
print("=" * 60)

# ── Load clean data ──────────────────────────────────────────
fm   = pd.read_csv(f"{CLEAN}/01_fund_master_clean.csv")
nav  = pd.read_csv(f"{CLEAN}/02_nav_history_clean.csv", parse_dates=["date"])
aum  = pd.read_csv(f"{CLEAN}/03_aum_clean.csv", parse_dates=["date"])
sip  = pd.read_csv(f"{CLEAN}/04_sip_clean.csv")
cat  = pd.read_csv(f"{CLEAN}/05_category_inflows_clean.csv")
folio= pd.read_csv(f"{CLEAN}/06_folio_clean.csv")
perf = pd.read_csv(f"{CLEAN}/07_scheme_performance_clean.csv")
tx   = pd.read_csv(f"{CLEAN}/08_transactions_clean.csv", parse_dates=["transaction_date"])
port = pd.read_csv(f"{CLEAN}/09_portfolio_clean.csv")
bench= pd.read_csv(f"{CLEAN}/10_benchmark_clean.csv", parse_dates=["date"])

print("[OK] All clean files loaded\n")

# ── CHART 1: NAV Trend for 5 Large Cap funds ─────────────────
print("Generating Chart 1: NAV Trend Lines...")
large_cap_codes = fm[fm['category'] == 'Large Cap']['amfi_code'].astype(str).tolist()[:5]
fig, ax = plt.subplots(figsize=(14, 6))
for i, code in enumerate(large_cap_codes):
    df_fund = nav[nav['amfi_code'] == int(code)] if nav['amfi_code'].dtype != object else nav[nav['amfi_code'] == code]
    name = fm[fm['amfi_code'].astype(str) == str(code)]['scheme_name'].values
    label = name[0][:30] if len(name) > 0 else code
    ax.plot(df_fund['date'], df_fund['nav'], label=label, color=COLORS[i], linewidth=1.5)
ax.set_title("NAV Trend - Top 5 Large Cap Funds (2022-2026)", fontsize=14, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Date"); ax.set_ylabel("NAV (Rs.)")
ax.legend(fontsize=8, loc='upper left')
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart01_nav_trend.png", dpi=150)
plt.close()
print("  [OK] chart01_nav_trend.png")

# ── CHART 2: AUM by Fund House (Grouped Bar) ─────────────────
print("Generating Chart 2: AUM Growth by AMC...")
aum['year'] = aum['date'].dt.year
aum_pivot = aum.groupby(['fund_house','year'])['aum_crore'].sum().reset_index()
top_houses = aum_pivot.groupby('fund_house')['aum_crore'].sum().nlargest(6).index
aum_top = aum_pivot[aum_pivot['fund_house'].isin(top_houses)]
aum_wide = aum_top.pivot(index='fund_house', columns='year', values='aum_crore').fillna(0)
fig, ax = plt.subplots(figsize=(14, 6))
aum_wide.plot(kind='bar', ax=ax, colormap='Blues', edgecolor='white')
ax.set_title("AUM by Fund House per Year (Top 6 AMCs)", fontsize=14, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Fund House"); ax.set_ylabel("AUM (Rs. Crore)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e5:.1f}L'))
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart02_aum_growth.png", dpi=150)
plt.close()
print("  [OK] chart02_aum_growth.png")

# ── CHART 3: SIP Inflow Time Series ──────────────────────────
print("Generating Chart 3: SIP Inflow Trend...")
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(sip['month'], sip['sip_inflow_crore'], color="#1F4E79", linewidth=2, marker='o', markersize=3)
ax.fill_between(range(len(sip)), sip['sip_inflow_crore'], alpha=0.15, color="#2E75B6")
# Mark Dec 2025 milestone
if '2025-12' in sip['month'].values:
    idx = sip[sip['month'] == '2025-12'].index[0]
    ax.axvline(x=sip['month'].tolist().index('2025-12'), color='red', linestyle='--', alpha=0.7)
    ax.annotate('Rs.31,002 Cr\n(Dec 2025 ATH)', xy=(sip['month'].tolist().index('2025-12'), 31002),
                xytext=(sip['month'].tolist().index('2025-12')-4, 28000),
                arrowprops=dict(arrowstyle='->', color='red'), fontsize=9, color='red')
ax.set_title("Monthly SIP Inflows Jan 2022 - Dec 2025", fontsize=14, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Month"); ax.set_ylabel("SIP Inflow (Rs. Crore)")
tick_positions = list(range(0, len(sip), 6))
ax.set_xticks(tick_positions)
ax.set_xticklabels([sip['month'].iloc[i] for i in tick_positions], rotation=45)
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart03_sip_inflow.png", dpi=150)
plt.close()
print("  [OK] chart03_sip_inflow.png")

# ── CHART 4: Category Inflow Heatmap ─────────────────────────
print("Generating Chart 4: Category Inflow Heatmap...")
try:
    cat_pivot = cat.pivot_table(index='category', columns='month', values='net_inflow_crore', aggfunc='sum')
    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(cat_pivot, cmap='RdYlGn', center=0, ax=ax, linewidths=0.3,
                fmt='.0f', annot=False, cbar_kws={'label': 'Net Inflow (Crore)'})
    ax.set_title("Category-wise Net Inflows Heatmap", fontsize=14, fontweight='bold', color="#1F4E79")
    plt.xticks(rotation=45, ha='right', fontsize=7)
    plt.tight_layout()
    plt.savefig(f"{CHARTS}/chart04_category_heatmap.png", dpi=150)
    plt.close()
    print("  [OK] chart04_category_heatmap.png")
except Exception as e:
    print(f"  [WARN] Chart 4 skipped: {e}")

# ── CHART 5: Investor Age Distribution ───────────────────────
print("Generating Chart 5: Investor Demographics...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
age_counts = tx['age_group'].value_counts().sort_index()
ax1.pie(age_counts, labels=age_counts.index, autopct='%1.1f%%',
        colors=COLORS[:len(age_counts)], startangle=90)
ax1.set_title("Investors by Age Group", fontweight='bold', color="#1F4E79")
age_sip = tx[tx['transaction_type']=='Sip'].groupby('age_group')['amount_inr'].mean() / 1000
age_sip.plot(kind='bar', ax=ax2, color=COLORS[1], edgecolor='white')
ax2.set_title("Avg SIP Amount by Age Group (Rs. 000s)", fontweight='bold', color="#1F4E79")
ax2.set_xlabel("Age Group"); ax2.set_ylabel("Avg Amount (Rs. 000s)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart05_demographics.png", dpi=150)
plt.close()
print("  [OK] chart05_demographics.png")

# ── CHART 6: SIP Amount by State ─────────────────────────────
print("Generating Chart 6: Geographic Distribution...")
state_data = tx.groupby('state')['amount_inr'].sum().sort_values() / 1e7
fig, ax = plt.subplots(figsize=(10, 8))
bars = ax.barh(state_data.index, state_data.values, color=COLORS[1], edgecolor='white')
ax.set_title("Total SIP Amount by State (Rs. Crore)", fontsize=14, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Total Amount (Rs. Crore)")
for bar, val in zip(bars, state_data.values):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            f'{val:.0f}', va='center', fontsize=8)
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart06_geographic.png", dpi=150)
plt.close()
print("  [OK] chart06_geographic.png")

# ── CHART 7: Folio Count Growth ───────────────────────────────
print("Generating Chart 7: Folio Count Growth...")
folio_col = [c for c in folio.columns if 'total' in c.lower() or 'folio' in c.lower()][0]
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(folio['month'], folio[folio_col], color=COLORS[2], linewidth=2.5, marker='o', markersize=4)
ax.fill_between(range(len(folio)), folio[folio_col], alpha=0.2, color=COLORS[2])
ax.set_title("Industry Folio Count Growth (Crore)", fontsize=14, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Month"); ax.set_ylabel("Total Folios (Crore)")
tick_positions = list(range(0, len(folio), 3))
ax.set_xticks(tick_positions)
ax.set_xticklabels([folio['month'].iloc[i] for i in tick_positions], rotation=45, fontsize=8)
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart07_folio_growth.png", dpi=150)
plt.close()
print("  [OK] chart07_folio_growth.png")

# ── CHART 8: Correlation Matrix of NAV Returns ───────────────
print("Generating Chart 8: Correlation Matrix...")
top10_codes = perf.nlargest(10, 'aum_crore')['amfi_code'].astype(str).tolist()
nav['amfi_code'] = nav['amfi_code'].astype(str)
nav_pivot = nav[nav['amfi_code'].isin(top10_codes)].pivot_table(
    index='date', columns='amfi_code', values='daily_return_pct')
nav_pivot = nav_pivot.dropna(thresh=5)
corr = nav_pivot.corr()
labels = []
for code in corr.columns:
    name = fm[fm['amfi_code'].astype(str) == str(code)]['scheme_name'].values
    labels.append(name[0][:20] if len(name) > 0 else code)
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            xticklabels=labels, yticklabels=labels, ax=ax, linewidths=0.5)
ax.set_title("NAV Return Correlation Matrix (Top 10 Funds by AUM)", fontsize=13, fontweight='bold', color="#1F4E79")
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart08_correlation.png", dpi=150)
plt.close()
print("  [OK] chart08_correlation.png")

# ── CHART 9: Sector Allocation Donut ─────────────────────────
print("Generating Chart 9: Sector Allocation...")
sector_col = [c for c in port.columns if 'sector' in c.lower()][0]
weight_col  = [c for c in port.columns if 'weight' in c.lower()][0]
sector_wt = port.groupby(sector_col)[weight_col].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(sector_wt, labels=sector_wt.index,
    autopct='%1.1f%%', colors=COLORS * 2, startangle=90,
    wedgeprops=dict(width=0.6))
ax.set_title("Sector Allocation Across All Equity Funds", fontsize=14, fontweight='bold', color="#1F4E79")
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart09_sector_allocation.png", dpi=150)
plt.close()
print("  [OK] chart09_sector_allocation.png")

# ── CHART 10: Top 10 & Bottom 10 Funds by 3yr Return ─────────
print("Generating Chart 10: Top & Bottom Funds...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
top10 = perf.nlargest(10, 'return_3yr_pct')[['scheme_name','return_3yr_pct']]
top10['scheme_name'] = top10['scheme_name'].str[:30]
ax1.barh(top10['scheme_name'], top10['return_3yr_pct'], color=COLORS[2])
ax1.set_title("Top 10 Funds - 3yr CAGR %", fontweight='bold', color="#1F4E79")
ax1.set_xlabel("3yr CAGR %")
bot10 = perf.nsmallest(10, 'return_3yr_pct')[['scheme_name','return_3yr_pct']]
bot10['scheme_name'] = bot10['scheme_name'].str[:30]
ax2.barh(bot10['scheme_name'], bot10['return_3yr_pct'], color=COLORS[4])
ax2.set_title("Bottom 10 Funds - 3yr CAGR %", fontweight='bold', color="#1F4E79")
ax2.set_xlabel("3yr CAGR %")
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart10_top_bottom_funds.png", dpi=150)
plt.close()
print("  [OK] chart10_top_bottom_funds.png")

# ── CHART 11: Transaction Type Breakdown ─────────────────────
print("Generating Chart 11: Transaction Types...")
tx_type = tx.groupby('transaction_type')['amount_inr'].sum() / 1e7
fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(tx_type.index, tx_type.values, color=[COLORS[2], COLORS[3], COLORS[4]], edgecolor='white', width=0.5)
ax.set_title("Transaction Volume by Type (Rs. Crore)", fontsize=14, fontweight='bold', color="#1F4E79")
ax.set_ylabel("Total Amount (Rs. Crore)")
for bar, val in zip(bars, tx_type.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f'Rs.{val:.0f} Cr', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart11_transaction_types.png", dpi=150)
plt.close()
print("  [OK] chart11_transaction_types.png")

# ── CHART 12: Sharpe Ratio Distribution ──────────────────────
print("Generating Chart 12: Sharpe Ratio Distribution...")
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(perf['sharpe_ratio'].dropna(), bins=15, kde=True, color=COLORS[1], ax=ax)
ax.axvline(x=1.0, color='red', linestyle='--', label='Sharpe = 1.0 (Good)')
ax.axvline(x=perf['sharpe_ratio'].mean(), color='green', linestyle='--',
           label=f"Mean = {perf['sharpe_ratio'].mean():.2f}")
ax.set_title("Distribution of Sharpe Ratios Across All Funds", fontsize=14, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Sharpe Ratio"); ax.set_ylabel("Count")
ax.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart12_sharpe_distribution.png", dpi=150)
plt.close()
print("  [OK] chart12_sharpe_distribution.png")

# ── CHART 13: Benchmark Index Performance ────────────────────
print("Generating Chart 13: Benchmark Indices...")
fig, ax = plt.subplots(figsize=(14, 6))
for i, idx_name in enumerate(bench['index_name'].unique()[:5]):
    df_idx = bench[bench['index_name'] == idx_name].sort_values('date')
    # Normalise to 100 at start
    df_idx = df_idx.copy()
    df_idx['normalised'] = df_idx['close_value'] / df_idx['close_value'].iloc[0] * 100
    ax.plot(df_idx['date'], df_idx['normalised'], label=idx_name, linewidth=1.8, color=COLORS[i])
ax.set_title("Benchmark Index Performance (Normalised to 100)", fontsize=14, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Date"); ax.set_ylabel("Indexed Value (Base=100)")
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart13_benchmark_indices.png", dpi=150)
plt.close()
print("  [OK] chart13_benchmark_indices.png")

# ── CHART 14: T30 vs B30 City Tier Pie ───────────────────────
print("Generating Chart 14: T30 vs B30...")
tier = tx.groupby('city_tier')['amount_inr'].sum() / 1e7
fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(tier, labels=tier.index, autopct='%1.1f%%',
       colors=[COLORS[0], COLORS[2]], startangle=90,
       wedgeprops=dict(edgecolor='white', linewidth=2))
ax.set_title("SIP Investment: T30 vs B30 Cities", fontsize=14, fontweight='bold', color="#1F4E79")
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart14_t30_b30.png", dpi=150)
plt.close()
print("  [OK] chart14_t30_b30.png")

# ── CHART 15: Expense Ratio vs Return Scatter ─────────────────
print("Generating Chart 15: Expense Ratio vs Return...")
fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(perf['expense_ratio_pct'], perf['return_3yr_pct'],
                     c=perf['sharpe_ratio'], cmap='RdYlGn', s=80, alpha=0.8, edgecolors='grey')
plt.colorbar(scatter, ax=ax, label='Sharpe Ratio')
ax.set_title("Expense Ratio vs 3yr Return (colour = Sharpe)", fontsize=13, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Expense Ratio (%)"); ax.set_ylabel("3yr CAGR (%)")
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart15_expense_vs_return.png", dpi=150)
plt.close()
print("  [OK] chart15_expense_vs_return.png")

# ── SUMMARY ──────────────────────────────────────────────────
print("\n" + "=" * 60)
print("DAY 3 COMPLETE!")
print(f"  15 charts saved to: data/charts/")
print("\nKEY INSIGHTS:")
print(f"  1. Largest fund by AUM: {perf.nlargest(1,'aum_crore')['scheme_name'].values[0][:40]}")
print(f"  2. Best 3yr return:     {perf.nlargest(1,'return_3yr_pct')['scheme_name'].values[0][:40]} ({perf['return_3yr_pct'].max():.1f}%)")
print(f"  3. Best Sharpe ratio:   {perf.nlargest(1,'sharpe_ratio')['scheme_name'].values[0][:40]} ({perf['sharpe_ratio'].max():.2f})")
print(f"  4. Total SIP inflow (latest month): Rs.{sip['sip_inflow_crore'].iloc[-1]:,.0f} Cr")
print(f"  5. Most popular age group: {tx['age_group'].value_counts().index[0]}")
