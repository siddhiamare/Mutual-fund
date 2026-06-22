"""
BLUESTOCK FINTECH - Mutual Fund Analytics Capstone
DAY 4: Fund Performance Analytics
Run this file after day3_eda_analysis.py
Usage: python day4_performance_analytics.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import sys
import os
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CLEAN  = "data/processed"
CHARTS = "data/charts"
OUT    = "data/processed"
os.makedirs(CHARTS, exist_ok=True)

COLORS = ["#1F4E79","#2E75B6","#2ECC71","#F39C12","#E74C3C"]
RF     = 0.065  # Risk-free rate (RBI repo rate proxy = 6.5%)

print("=" * 60)
print("DAY 4: Fund Performance Analytics")
print("=" * 60)

# ── Load clean data ──────────────────────────────────────────
fm    = pd.read_csv(f"{CLEAN}/01_fund_master_clean.csv")
nav   = pd.read_csv(f"{CLEAN}/02_nav_history_clean.csv", parse_dates=["date"])
perf  = pd.read_csv(f"{CLEAN}/07_scheme_performance_clean.csv")
bench = pd.read_csv(f"{CLEAN}/10_benchmark_clean.csv", parse_dates=["date"])

nav['amfi_code']  = nav['amfi_code'].astype(str)
fm['amfi_code']   = fm['amfi_code'].astype(str)
perf['amfi_code'] = perf['amfi_code'].astype(str)

print("[OK] All files loaded\n")


# ─────────────────────────────────────────────
# STEP 1: Compute Daily Returns
# ─────────────────────────────────────────────
print("--- STEP 1: Computing Daily Returns ---")
nav = nav.sort_values(['amfi_code', 'date'])
nav['daily_return'] = nav.groupby('amfi_code')['nav'].pct_change()
nav = nav.dropna(subset=['daily_return'])

# Save returns
nav.to_csv(f"{OUT}/returns_computed.csv", index=False)
print(f"  [OK] Daily returns computed for {nav['amfi_code'].nunique()} funds")
print(f"  [OK] Saved: returns_computed.csv")


# ─────────────────────────────────────────────
# STEP 2: Compute CAGR (1yr, 3yr, 5yr)
# ─────────────────────────────────────────────
print("\n--- STEP 2: Computing CAGR ---")

def compute_cagr(nav_df, amfi_code, years):
    """Compute CAGR for a given number of years."""
    fund_nav = nav_df[nav_df['amfi_code'] == str(amfi_code)].sort_values('date')
    if len(fund_nav) < 2:
        return np.nan
    end_date   = fund_nav['date'].max()
    start_date = end_date - pd.DateOffset(years=years)
    start_nav  = fund_nav[fund_nav['date'] >= start_date]
    if len(start_nav) == 0:
        return np.nan
    nav_start = start_nav.iloc[0]['nav']
    nav_end   = fund_nav.iloc[-1]['nav']
    n         = years
    cagr      = (nav_end / nav_start) ** (1 / n) - 1
    return round(cagr * 100, 2)

cagr_records = []
for code in nav['amfi_code'].unique():
    name = fm[fm['amfi_code'] == code]['scheme_name'].values
    cagr_records.append({
        'amfi_code':    code,
        'scheme_name':  name[0] if len(name) > 0 else code,
        'cagr_1yr_pct': compute_cagr(nav, code, 1),
        'cagr_3yr_pct': compute_cagr(nav, code, 3),
        'cagr_5yr_pct': compute_cagr(nav, code, 5),
    })

cagr_df = pd.DataFrame(cagr_records)
cagr_df.to_csv(f"{OUT}/cagr_report.csv", index=False)
print(f"  [OK] CAGR computed for {len(cagr_df)} funds")
print(f"  [OK] Saved: cagr_report.csv")
print("\n  Top 5 funds by 3yr CAGR:")
print(cagr_df.nlargest(5, 'cagr_3yr_pct')[['scheme_name','cagr_3yr_pct']].to_string(index=False))


# ─────────────────────────────────────────────
# STEP 3: Compute Sharpe Ratio
# ─────────────────────────────────────────────
print("\n--- STEP 3: Computing Sharpe Ratio ---")

def compute_sharpe(returns, rf=RF):
    """Sharpe = (Annualised Return - Rf) / Annualised Std Dev"""
    if len(returns) < 30:
        return np.nan
    ann_return = (1 + returns.mean()) ** 252 - 1
    ann_std    = returns.std() * np.sqrt(252)
    if ann_std == 0:
        return np.nan
    return round((ann_return - rf) / ann_std, 4)

sharpe_records = []
for code, grp in nav.groupby('amfi_code'):
    name = fm[fm['amfi_code'] == code]['scheme_name'].values
    sharpe_records.append({
        'amfi_code':   code,
        'scheme_name': name[0] if len(name) > 0 else code,
        'sharpe_ratio': compute_sharpe(grp['daily_return']),
    })

sharpe_df = pd.DataFrame(sharpe_records)
sharpe_df.to_csv(f"{OUT}/sharpe_values.csv", index=False)
print(f"  [OK] Saved: sharpe_values.csv")
print("\n  Top 5 funds by Sharpe Ratio:")
print(sharpe_df.nlargest(5, 'sharpe_ratio')[['scheme_name','sharpe_ratio']].to_string(index=False))


# ─────────────────────────────────────────────
# STEP 4: Compute Sortino Ratio
# ─────────────────────────────────────────────
print("\n--- STEP 4: Computing Sortino Ratio ---")

def compute_sortino(returns, rf=RF):
    """Sortino = (Annualised Return - Rf) / Downside Std Dev"""
    if len(returns) < 30:
        return np.nan
    ann_return    = (1 + returns.mean()) ** 252 - 1
    negative_rets = returns[returns < 0]
    if len(negative_rets) == 0:
        return np.nan
    downside_std  = negative_rets.std() * np.sqrt(252)
    if downside_std == 0:
        return np.nan
    return round((ann_return - rf) / downside_std, 4)

sortino_records = []
for code, grp in nav.groupby('amfi_code'):
    name = fm[fm['amfi_code'] == code]['scheme_name'].values
    sortino_records.append({
        'amfi_code':    code,
        'scheme_name':  name[0] if len(name) > 0 else code,
        'sortino_ratio': compute_sortino(grp['daily_return']),
    })

sortino_df = pd.DataFrame(sortino_records)
sortino_df.to_csv(f"{OUT}/sortino_values.csv", index=False)
print(f"  [OK] Saved: sortino_values.csv")
print("\n  Top 5 funds by Sortino Ratio:")
print(sortino_df.nlargest(5, 'sortino_ratio')[['scheme_name','sortino_ratio']].to_string(index=False))


# ─────────────────────────────────────────────
# STEP 5: Compute Alpha & Beta vs Nifty 100
# ─────────────────────────────────────────────
print("\n--- STEP 5: Computing Alpha & Beta vs Nifty 100 ---")

# Get Nifty 100 benchmark returns
nifty100 = bench[bench['index_name'].str.contains('Nifty 100', case=False, na=False)].copy()
if len(nifty100) == 0:
    nifty100 = bench[bench['index_name'].str.contains('Nifty', case=False, na=False)].copy()
nifty100 = nifty100.sort_values('date')
nifty100['bench_return'] = nifty100['close_value'].pct_change()
nifty100 = nifty100.dropna(subset=['bench_return'])

ab_records = []
for code, grp in nav.groupby('amfi_code'):
    merged = pd.merge(
        grp[['date','daily_return']],
        nifty100[['date','bench_return']],
        on='date', how='inner'
    ).dropna()
    name = fm[fm['amfi_code'] == code]['scheme_name'].values
    scheme_name = name[0] if len(name) > 0 else code
    if len(merged) < 30:
        ab_records.append({'amfi_code': code, 'scheme_name': scheme_name,
                           'alpha': np.nan, 'beta': np.nan, 'r_squared': np.nan})
        continue
    slope, intercept, r, p, se = stats.linregress(merged['bench_return'], merged['daily_return'])
    alpha = round(intercept * 252 * 100, 4)  # Annualised alpha in %
    beta  = round(slope, 4)
    ab_records.append({
        'amfi_code':   code,
        'scheme_name': scheme_name,
        'alpha':       alpha,
        'beta':        beta,
        'r_squared':   round(r**2, 4),
    })

ab_df = pd.DataFrame(ab_records)
ab_df.to_csv(f"{OUT}/alpha_beta.csv", index=False)
print(f"  [OK] Saved: alpha_beta.csv")
print("\n  Top 5 funds by Alpha:")
print(ab_df.nlargest(5, 'alpha')[['scheme_name','alpha','beta']].to_string(index=False))


# ─────────────────────────────────────────────
# STEP 6: Compute Maximum Drawdown
# ─────────────────────────────────────────────
print("\n--- STEP 6: Computing Maximum Drawdown ---")

def compute_max_drawdown(nav_series):
    """Max Drawdown = min(NAV / running_max - 1)"""
    running_max = nav_series.cummax()
    drawdown    = (nav_series / running_max - 1)
    return round(drawdown.min() * 100, 4)

dd_records = []
for code, grp in nav.groupby('amfi_code'):
    grp = grp.sort_values('date')
    name = fm[fm['amfi_code'] == code]['scheme_name'].values
    dd_records.append({
        'amfi_code':       code,
        'scheme_name':     name[0] if len(name) > 0 else code,
        'max_drawdown_pct': compute_max_drawdown(grp['nav']),
    })

dd_df = pd.DataFrame(dd_records)
dd_df.to_csv(f"{OUT}/max_drawdown.csv", index=False)
print(f"  [OK] Saved: max_drawdown.csv")
print("\n  Funds with smallest drawdown (most stable):")
print(dd_df.nlargest(5, 'max_drawdown_pct')[['scheme_name','max_drawdown_pct']].to_string(index=False))


# ─────────────────────────────────────────────
# STEP 7: Build Fund Scorecard (0-100)
# ─────────────────────────────────────────────
print("\n--- STEP 7: Building Fund Scorecard ---")

# Merge all metrics
scorecard = cagr_df[['amfi_code','scheme_name','cagr_3yr_pct']].copy()
scorecard = scorecard.merge(sharpe_df[['amfi_code','sharpe_ratio']], on='amfi_code', how='left')
scorecard = scorecard.merge(ab_df[['amfi_code','alpha']], on='amfi_code', how='left')
scorecard = scorecard.merge(dd_df[['amfi_code','max_drawdown_pct']], on='amfi_code', how='left')
scorecard = scorecard.merge(
    fm[['amfi_code','expense_ratio_pct']], on='amfi_code', how='left')

scorecard = scorecard.dropna()

# Rank each metric (higher rank = better)
scorecard['rank_return']   = scorecard['cagr_3yr_pct'].rank(pct=True)
scorecard['rank_sharpe']   = scorecard['sharpe_ratio'].rank(pct=True)
scorecard['rank_alpha']    = scorecard['alpha'].rank(pct=True)
scorecard['rank_expense']  = (1 - scorecard['expense_ratio_pct'].rank(pct=True))  # Lower is better
scorecard['rank_drawdown'] = (1 - scorecard['max_drawdown_pct'].rank(pct=True))   # Less negative is better

# Composite score: weighted sum
scorecard['composite_score'] = (
    scorecard['rank_return']   * 0.30 +
    scorecard['rank_sharpe']   * 0.25 +
    scorecard['rank_alpha']    * 0.20 +
    scorecard['rank_expense']  * 0.15 +
    scorecard['rank_drawdown'] * 0.10
) * 100

scorecard['composite_score'] = scorecard['composite_score'].round(1)
scorecard = scorecard.sort_values('composite_score', ascending=False)
scorecard.to_csv(f"{OUT}/fund_scorecard.csv", index=False)
print(f"  [OK] Saved: fund_scorecard.csv")
print("\n  TOP 10 FUNDS BY COMPOSITE SCORE:")
print(scorecard[['scheme_name','composite_score','cagr_3yr_pct','sharpe_ratio','alpha']].head(10).to_string(index=False))


# ─────────────────────────────────────────────
# STEP 8: Benchmark Comparison Chart
# ─────────────────────────────────────────────
print("\n--- STEP 8: Benchmark Comparison Chart ---")

# Pick top 5 funds by composite score
top5_codes = scorecard.head(5)['amfi_code'].tolist()

# Nifty 50 benchmark
nifty50 = bench[bench['index_name'].str.contains('Nifty 50', case=False, na=False)].copy()
nifty50 = nifty50.sort_values('date')

# Filter last 3 years
cutoff = nav['date'].max() - pd.DateOffset(years=3)
nifty50_3yr = nifty50[nifty50['date'] >= cutoff].copy()
nifty50_3yr['normalised'] = nifty50_3yr['close_value'] / nifty50_3yr['close_value'].iloc[0] * 100

fig, ax = plt.subplots(figsize=(14, 7))

for i, code in enumerate(top5_codes):
    fund_nav = nav[(nav['amfi_code'] == code) & (nav['date'] >= cutoff)].sort_values('date')
    if len(fund_nav) == 0:
        continue
    fund_nav = fund_nav.copy()
    fund_nav['normalised'] = fund_nav['nav'] / fund_nav['nav'].iloc[0] * 100
    name = fm[fm['amfi_code'] == code]['scheme_name'].values
    label = name[0][:35] if len(name) > 0 else code
    ax.plot(fund_nav['date'], fund_nav['normalised'],
            label=label, color=COLORS[i], linewidth=1.8)

# Plot Nifty 50
if len(nifty50_3yr) > 0:
    ax.plot(nifty50_3yr['date'], nifty50_3yr['normalised'],
            label='Nifty 50 (Benchmark)', color='black',
            linewidth=2.5, linestyle='--')

ax.set_title("Top 5 Funds vs Nifty 50 Benchmark (3 Years, Normalised to 100)",
             fontsize=13, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Date")
ax.set_ylabel("Indexed Value (Base = 100)")
ax.legend(fontsize=8, loc='upper left')
ax.axhline(y=100, color='grey', linestyle=':', alpha=0.5)
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart_benchmark_comparison.png", dpi=150)
plt.close()
print(f"  [OK] Saved: chart_benchmark_comparison.png")

# ─────────────────────────────────────────────
# STEP 9: Scorecard Bar Chart
# ─────────────────────────────────────────────
top15 = scorecard.head(15)
top15['short_name'] = top15['scheme_name'].str[:30]
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(top15['short_name'], top15['composite_score'],
               color=COLORS[1], edgecolor='white')
ax.set_title("Top 15 Funds by Composite Score (0-100)",
             fontsize=13, fontweight='bold', color="#1F4E79")
ax.set_xlabel("Composite Score")
ax.axvline(x=50, color='red', linestyle='--', alpha=0.5, label='Score = 50')
for bar, val in zip(bars, top15['composite_score']):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}', va='center', fontsize=8)
plt.tight_layout()
plt.savefig(f"{CHARTS}/chart_fund_scorecard.png", dpi=150)
plt.close()
print(f"  [OK] Saved: chart_fund_scorecard.png")


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("DAY 4 COMPLETE!")
print("  Files saved to data/processed/:")
print("    - returns_computed.csv")
print("    - cagr_report.csv")
print("    - sharpe_values.csv")
print("    - sortino_values.csv")
print("    - alpha_beta.csv")
print("    - max_drawdown.csv")
print("    - fund_scorecard.csv")
print("  Charts saved to data/charts/:")
print("    - chart_benchmark_comparison.png")
print("    - chart_fund_scorecard.png")
print("\nNext step: python day5_advanced_analytics.py")
print("=" * 60)