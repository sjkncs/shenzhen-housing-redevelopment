"""Describe candidate transaction composition without attributing price changes."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def assign_period(quarters):
    result = pd.Series('transition', index=quarters.index)
    result.loc[quarters.le('2019Q4')] = 'pre'
    result.loc[quarters.ge('2020Q2')] = 'post'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', type=Path, required=True)
    parser.add_argument('--transactions', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve earlier output; select a new directory')
    sample = pd.read_csv(args.sample, dtype={'community': str})
    baseline = pd.read_csv(args.baseline, dtype={'community_id': str})
    raw = pd.read_csv(args.transactions, usecols=['成交详情页url', '所在楼层'], low_memory=False)
    expected_sha = 'b56310294f8b0288eba66c9852353c0339d4e9ba10fc0dadbcfa17ffad63bd22'
    assert hashlib.sha256(args.transactions.read_bytes()).hexdigest() == expected_sha
    selected = sample[sample.community.isin(baseline.community_id)].copy()
    assert len(selected) == 366 and selected.transaction_url.notna().all()
    if selected.transaction_url.duplicated().any():
        raise ValueError('Duplicate sample transactions')
    raw = raw[raw['成交详情页url'].isin(selected.transaction_url)].copy()
    if raw['成交详情页url'].duplicated().any():
        raise ValueError('Ambiguous raw transaction lookup')
    selected = selected.merge(raw, left_on='transaction_url', right_on='成交详情页url', how='left', validate='one_to_one', indicator=True)
    assert selected['_merge'].eq('both').all()
    selected['period'] = assign_period(selected.quarter)
    selected['floor_band'] = selected['所在楼层'].fillna('missing').str.extract(r'(高楼层|中楼层|低楼层|地下室|底层|顶层)', expand=False).fillna('unknown_or_missing')
    period = selected.groupby(['community', 'name', 'period']).agg(
        transactions=('price', 'size'), quarters=('quarter', 'nunique'),
        median_area=('area', 'median'), mean_area=('area', 'mean'),
        elevator_share=('elevator', 'mean'), median_reported_year=('year_built', 'median'),
        median_source_price=('price', 'median')).reset_index()
    years = selected.groupby(['community', 'name', 'period', 'year_built']).size().rename('transactions').reset_index()
    years['within_period_share'] = years.transactions / years.groupby(['community', 'period']).transactions.transform('sum')
    floors = selected.groupby(['community', 'name', 'period', 'floor_band']).size().rename('transactions').reset_index()
    floors['within_period_share'] = floors.transactions / floors.groupby(['community', 'period']).transactions.transform('sum')
    contrasts = []
    for cid, group in selected.groupby('community'):
        pre, post = group[group.period.eq('pre')], group[group.period.eq('post')]
        if pre.empty or post.empty:
            continue
        pre_share = pre.year_built.value_counts(normalize=True)
        post_share = post.year_built.value_counts(normalize=True)
        union = pre_share.index.union(post_share.index)
        tv = (pre_share.reindex(union, fill_value=0) - post_share.reindex(union, fill_value=0)).abs().sum() / 2
        contrasts.append({'community_id': cid, 'name': group.name.iloc[0], 'pre_n': len(pre), 'post_n': len(post),
                          'median_area_pre': pre.area.median(), 'median_area_post': post.area.median(),
                          'median_area_difference_m2': post.area.median() - pre.area.median(),
                          'elevator_share_difference': post.elevator.mean() - pre.elevator.mean(),
                          'reported_year_share_total_variation': float(tv),
                          'difference_is_causal_effect': False})
    contrast = pd.DataFrame(contrasts)
    args.output.mkdir(parents=True)
    for name, frame in [('period_composition.csv', period), ('reported_year_composition.csv', years),
                        ('floor_band_composition.csv', floors), ('pre_post_composition.csv', contrast)]:
        frame.to_csv(args.output / name, index=False, encoding='utf-8-sig')
    summary = {'scope': 'SOURCE_REPORTED_TRANSACTION_COMPOSITION_NOT_CAUSAL_EFFECT',
               'candidate_n': selected.community.nunique(), 'transactions_n': len(selected),
               'conflicting_reported_years_n': int(baseline.reported_years_conflict.sum()),
               'both_periods_candidates_n': len(contrast),
               'period_counts': selected.period.value_counts().to_dict(),
               'floor_band_unknown_n': int(selected.floor_band.eq('unknown_or_missing').sum()),
               'identity_confirmed': False, 'building_phase_assigned': False,
               'source_sha256': {key: hashlib.sha256(getattr(args, key).read_bytes()).hexdigest()
                                 for key in ['sample', 'transactions', 'baseline']}}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))
    print(contrast.sort_values('reported_year_share_total_variation', ascending=False).to_string(index=False))


if __name__ == '__main__':
    main()
