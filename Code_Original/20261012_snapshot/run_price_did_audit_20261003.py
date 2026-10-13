"""Reproducible area-proxy DID audit; project-boundary DID remains separate."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t as student_t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SOURCE = Path('C:/Users/Lenovo/Downloads/二手房成交房源_深圳 来源贝壳.csv')
OUT = Path(__file__).resolve().parents[1] / 'outputs/price_did_audit_20261003'
OUT.mkdir(parents=True, exist_ok=True)

def number(s):
    return pd.to_numeric(s.astype(str).str.replace(',', '', regex=False)
                         .str.extract(r'(-?\d+(?:\.\d+)?)', expand=False), errors='coerce')

def absorb(frame, sample):
    z = frame.astype(float).copy()
    for iteration in range(1000):
        previous = z.to_numpy().copy()
        for key in ['community', 'quarter']:
            z -= z.groupby(sample[key]).transform('mean')
        delta = float(np.max(np.abs(z.to_numpy() - previous)))
        if delta < 1e-10:
            return z, iteration + 1, delta
    raise RuntimeError('Fixed effect absorption did not converge')

def estimate(sample, variables):
    z, iterations, delta = absorb(sample[['ln_price'] + variables], sample)
    assert np.linalg.matrix_rank(z[variables].to_numpy()) == len(variables)
    fit = sm.OLS(z.ln_price, z[variables]).fit(
        cov_type='cluster', cov_kwds={'groups': sample.community, 'use_correction': False})
    n, groups = len(sample), sample.community.nunique()
    # Compute absorbed-FE rank from the community-quarter bipartite components.
    parents = {}
    def root(x):
        parents.setdefault(x, x)
        if parents[x] != x:
            parents[x] = root(parents[x])
        return parents[x]
    for c, q in sample[['community', 'quarter']].drop_duplicates().itertuples(index=False):
        a, b = root('c' + str(c)), root('q' + str(q))
        parents[a] = b
    components = len({root(x) for x in list(parents)})
    fe_rank = groups + sample.quarter.nunique() - components
    rank = fe_rank + len(variables)
    correction = groups / (groups - 1) * (n - 1) / (n - rank)
    covariance = fit.cov_params() * correction
    se = np.sqrt(np.diag(covariance))
    critical = student_t.ppf(.975, groups - 1)
    rows = []
    for i, name in enumerate(variables):
        beta = float(fit.params[name])
        low, high = beta - critical * se[i], beta + critical * se[i]
        rows.append(dict(term=name, beta=beta, se=float(se[i]),
                         p=float(2 * student_t.sf(abs(beta / se[i]), groups - 1)),
                         ci_low=low, ci_high=high, percent=100 * np.expm1(beta),
                         percent_low=100 * np.expm1(low), percent_high=100 * np.expm1(high)))
    info = dict(n=n, communities=groups, treated_communities=int(sample.loc[sample.treated.eq(1), 'community'].nunique()),
                quarters=int(sample.quarter.nunique()), fe_rank=fe_rank, design_rank=rank,
                components=components, cluster_correction=correction, iterations=iterations, delta=delta)
    return pd.DataFrame(rows), covariance, info

raw = pd.read_csv(SOURCE, low_memory=False)
d = pd.DataFrame(dict(date=pd.to_datetime(raw['成交时间'], errors='coerce'),
                     price=number(raw['成交均价 元/平']), total=number(raw['成交价格/万']),
                     area=number(raw['建筑面积']), year_built=number(raw['建成年代']),
                     listing=pd.to_datetime(raw['挂牌时间'], errors='coerce'),
                     community=raw['小区详情url'].str.extract(r'(\d+)/?$', expand=False),
                     name=raw['小区名称'], market=raw['区域商圈'], district=raw['区县'],
                     transaction_url=raw['成交详情页url'], elevator=raw['配备电梯'].map({'有': 1, '无': 0})))
age = d.date.dt.year - d.year_built
mask = (raw['房屋用途'].eq('普通住宅') & raw['交易权属'].eq('商品房') & d.date.notna()
        & d.community.notna() & d.price.gt(0) & d.total.gt(0) & d.area.gt(0)
        & age.between(0, 120) & d.elevator.notna() & ~(d.listing > d.date)
        & ((d.total * 10000 - d.price * d.area).abs() / (d.total * 10000)).le(.02))
d = d[mask & d.district.eq('罗湖区')].copy()
clean_n = len(d)
d['quarter'] = d.date.dt.to_period('Q').astype(str)
d['k'] = (d.date.dt.year - 2020) * 4 + d.date.dt.quarter - 2
d = d[d.date.between('2017-01-01', '2023-12-31')].copy()
duplicates = int(d.transaction_url.notna().sum() - d.transaction_url.dropna().nunique())
if duplicates:
    raise RuntimeError('Duplicate transaction URLs require resolution before estimation')
classification = d.groupby('community').market.nunique()
if (classification > 1).any():
    raise RuntimeError('Community market label changes within sample')
d['treated'] = d.market.eq('翠竹').astype(int)
d['post'] = d.k.ge(0).astype(int)
d['did'] = d.treated * d.post
d['ln_price'] = np.log(d.price)
d['ln_area'] = np.log(d.area)
assert not d.name.astype(str).str.contains('木头龙').any(), 'Project-internal housing requires separate identification'
d.groupby(['quarter', 'treated']).agg(n=('price', 'size'), communities=('community', 'nunique'),
                                     mean_log_price=('ln_price', 'mean'), median_price=('price', 'median')).to_csv(
                                         OUT / 'quarter_support.csv', encoding='utf-8-sig')
d.to_csv(OUT / 'analysis_sample.csv', index=False, encoding='utf-8-sig')
main = d[d.k.ne(-1)].copy()  # 2020Q1 is the transition quarter.
specifications = [('baseline', ['did']), ('housing_adjusted', ['did', 'ln_area', 'elevator'])]
results, model_info = [], {}
for label, columns in specifications:
    table, covariance, info = estimate(main, columns)
    table.insert(0, 'model', label)
    results.append(table)
    model_info[label] = info
pd.concat(results).to_csv(OUT / 'main_did.csv', index=False, encoding='utf-8-sig')

# Reference quarter is 2019Q4, before the formally documented construction month.
unsupported = sorted(set(d.k.unique()) - set(d.loc[d.treated.eq(1), 'k'].unique()))
ks = sorted(int(k) for k in d.loc[d.treated.eq(1), 'k'].unique() if k != -2)
event_names = []
for k in ks:
    name = 'event_' + ('m' + str(-k) if k < 0 else 'p' + str(k))
    d[name] = (d.k.eq(k) & d.treated.eq(1)).astype(int)
    event_names.append(name)
event, covariance, info = estimate(d, event_names + ['ln_area', 'elevator'])
event = event[event.term.isin(event_names)].copy()
event['k'] = ks
event.to_csv(OUT / 'event_study.csv', index=False, encoding='utf-8-sig')
pre_names = [name for k, name in zip(ks, event_names) if k <= -3]
b = event.set_index('term').loc[pre_names, 'beta'].to_numpy()
v = covariance.loc[pre_names, pre_names].to_numpy()
from scipy.stats import f
wald_f = float(b @ np.linalg.solve(v, b) / len(b))
pre_p = float(f.sf(wald_f, len(b), info['communities'] - 1))
plt.rcParams.update({'font.family': ['Microsoft YaHei', 'DejaVu Sans'], 'axes.unicode_minus': False,
                     'font.size': 12, 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.errorbar(event.k, event.percent, yerr=[event.percent - event.percent_low, event.percent_high - event.percent],
            fmt='o', color='#176c9a', ecolor='#81afc7', capsize=3)
ax.scatter([-2], [0], facecolors='white', edgecolors='#176c9a', zorder=5)
ax.axhline(0, color='#626b73', linewidth=.8)
ax.axvline(-.5, color='#b65b38', linestyle='--')
ax.set(xlabel='相对2020年第二季度的季度数（2019Q4为参照）', ylabel='翠竹相对罗湖其他商圈的价格差异（%）',
       title='罗湖片区试点：季度事件研究与95%置信区间')
fig.tight_layout()
fig.savefig(OUT / 'event_study.png', dpi=300)
plt.close(fig)
summary = dict(status='AREA_PROXY_DID_EXECUTED_PROJECT_BOUNDARY_DID_PENDING',
               source=str(SOURCE), source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               luohu_clean_n=clean_n, window=['2017-01-01', '2023-12-31'],
               event_source='https://www.sz.gov.cn/szzt2010/wgkzl/jggk/lsqkgk/content/post_8875889.html',
               event_precision='2020-03; first full post quarter 2020Q2; transition quarter 2020Q1',
               treatment='source market label 翠竹', comparison='all other observed Luohu market labels',
               excluded_transition_main=True, event_reference='2019Q4',
               event_quarters_without_treated_transactions=[int(k) for k in unsupported],
               covariance='community clustered CR1 with absorbed FE rank and t(G-1) intervals',
               model_info=model_info, event_model=info,
               pretrend_joint_test=dict(quarters='2017Q1-2019Q3 relative to 2019Q4', f=wald_f, p=pre_p, restrictions=len(b)),
               inference_scope='one treated market; community clustering does not address a shared treated-market shock',
               unresolved=['verified project-boundary distance', 'other-project exposure in comparisons',
                           'COVID and area-specific concurrent shocks', 'construction anticipation', 'project-level inference'],
               python=sys.version)
(OUT / 'run_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
print(pd.concat(results).to_string(index=False))
