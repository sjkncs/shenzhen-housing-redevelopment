"""Pre-specified support and placebo diagnostics for the area-proxy pilot."""
from pathlib import Path
import ast
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/price_did_audit_20261003'
# Reuse only reviewed estimator definitions, without executing the analysis module.
tree = ast.parse((ROOT / 'scripts/run_price_did_audit_20261003.py').read_text(encoding='utf-8'))
definitions = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                              and n.name in ['absorb', 'estimate']], type_ignores=[])
exec(compile(definitions, '<reviewed estimators>', 'exec'))
d = pd.read_csv(OUT / 'analysis_sample.csv', dtype={'community': str})
d['date'] = pd.to_datetime(d.date)
support = d[d.k.ne(-1)].groupby(['community', 'treated', 'post']).agg(
    transactions=('price', 'size'), quarters=('quarter', 'nunique')).reset_index()
wide = support.pivot(index=['community', 'treated'], columns='post', values='quarters').fillna(0)
wide.columns = ['pre_quarters', 'post_quarters']
wide.to_csv(OUT / 'community_pre_post_support.csv', encoding='utf-8-sig')
both = wide.index[(wide.pre_quarters >= 1) & (wide.post_quarters >= 1)].get_level_values('community')
four = wide.index[(wide.pre_quarters >= 4) & (wide.post_quarters >= 4)].get_level_values('community')
samples = [
    ('original_2017_2023', d[d.k.ne(-1)].copy()),
    ('same_communities_pre_post', d[d.k.ne(-1) & d.community.isin(both)].copy()),
    ('at_least_four_quarters_each_side', d[d.k.ne(-1) & d.community.isin(four)].copy()),
    ('short_window_2018_2021', d[d.k.ne(-1) & d.date.between('2018-01-01', '2021-12-31')].copy()),
    ('placebo_2019Q1_using_2017_2019', d[d.date.between('2017-01-01', '2019-12-31')].copy()),
]
rows, info = [], {}
for label, s in samples:
    if label.startswith('placebo'):
        s['post'] = s.date.ge('2019-01-01').astype(int)
        s['did'] = s.treated * s.post
    table, _, model = estimate(s, ['did', 'ln_area', 'elevator'])
    row = table[table.term.eq('did')].iloc[0].to_dict()
    row.update(model=label, n=len(s), communities=s.community.nunique(),
               treated_communities=s.loc[s.treated.eq(1), 'community'].nunique(),
               treated_pre=int(((s.treated == 1) & (s.post == 0)).sum()),
               treated_post=int(((s.treated == 1) & (s.post == 1)).sum()))
    rows.append(row)
    info[label] = model
results = pd.DataFrame(rows)
results.to_csv(OUT / 'did_support_sensitivity.csv', index=False, encoding='utf-8-sig')
stats = dict(samples=info, retained_both_sides=len(both), retained_four_quarters_each=len(four),
             placebo='2019Q1 chosen before outcomes; all observations precede documented 2020 construction',
             scope='area proxy sensitivity; no selection of specification by sign or significance')
(OUT / 'support_diagnostics.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
assert np.isfinite(results[['beta', 'se']].to_numpy()).all()
print(results.to_string(index=False))
