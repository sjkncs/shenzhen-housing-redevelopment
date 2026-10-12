"""Influence and differential linear-trend sensitivity of the area-proxy DID."""
from pathlib import Path
import ast
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t as student_t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/price_did_audit_20261003'
tree = ast.parse((ROOT / 'scripts/run_price_did_audit_20261003.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                             and n.name in ['absorb', 'estimate']], type_ignores=[]), '<estimators>', 'exec'))
d = pd.read_csv(OUT / 'analysis_sample.csv', dtype={'community': str})
d = d[d.k.ne(-1)].copy()
d['treated_linear_time'] = d.treated * d.k
rows=[]
for label, variables in [('baseline', ['did','ln_area','elevator']),
                          ('treated_linear_trend', ['did','ln_area','elevator','treated_linear_time'])]:
    result, _, info = estimate(d, variables)
    result['model'] = label
    rows.append(result)
pd.concat(rows).to_csv(OUT/'linear_trend_sensitivity.csv',index=False,encoding='utf-8-sig')
influence=[]
ids = sorted(d.loc[d.treated.eq(1),'community'].unique())
for cid in ids:
    s=d[d.community.ne(cid)].copy()
    result, _, info=estimate(s,['did','ln_area','elevator'])
    row=result[result.term.eq('did')].iloc[0].to_dict()
    row.update(omitted_community=cid, omitted_name=str(d.loc[d.community.eq(cid),'name'].iloc[0]),
               omitted_transactions=int(d.community.eq(cid).sum()), n=len(s))
    influence.append(row)
i=pd.DataFrame(influence)
i.to_csv(OUT/'leave_one_treated_community_out.csv',index=False,encoding='utf-8-sig')
plt.rcParams.update({'font.family':['Microsoft YaHei','DejaVu Sans'],'axes.unicode_minus':False})
fig, ax=plt.subplots(figsize=(9,4.5))
order=i.sort_values('percent').reset_index(drop=True)
ax.plot(np.arange(1,len(order)+1),order.percent,'o',color='#176c9a',markersize=4)
ax.axhline(17.416684,color='#b65b38',linestyle='--',label='原试点估计')
ax.set(xlabel='逐一剔除翠竹小区的估计（按结果排序）',ylabel='相对价格变化（%）',title='单个处理小区影响检验')
ax.legend(frameon=False)
fig.tight_layout();fig.savefig(OUT/'community_influence.png',dpi=300);plt.close(fig)
summary=dict(runs=len(i),minimum_percent=float(i.percent.min()),maximum_percent=float(i.percent.max()),
             trend_results=pd.concat(rows).to_dict('records'),
             interpretation='Linear-trend model extrapolates a single differential trend across the full window; sensitivity only.',
             unchanged='area proxy definition and source sample; project-boundary assignment remains pending')
(OUT/'influence_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(i)==42 and np.isfinite(i.beta).all()
print(json.dumps(summary,ensure_ascii=False,indent=2))
