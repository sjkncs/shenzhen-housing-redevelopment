"""Audit address leads and quarterly support; never assign project treatment."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

ROADS = ('华丽路', '爱国路', '文锦中路')


def support_rows(sample, coverage):
    sample = sample.copy()
    if sample.transaction_url.dropna().duplicated().any():
        raise ValueError('Duplicate transaction URLs')
    if not sample.quarter.str.fullmatch(r'20\d{2}Q[1-4]').all():
        raise ValueError('Invalid quarter')
    if not sample.quarter.between('2017Q1', '2023Q4').all():
        raise ValueError('Unexpected analysis window')
    if not set(sample.community) <= set(coverage.community_id):
        raise ValueError('Community missing from audited coverage')
    rows = []
    for record in coverage.itertuples():
        group = sample[sample.community.eq(record.community_id)]
        pre = group[group.quarter.le('2019Q4')]
        post = group[group.quarter.ge('2020Q2')]
        rows.append({'community_id': record.community_id, 'transaction_names': record.transaction_names,
                     'clean_transaction_n_all_dates': record.clean_transaction_n,
                     'window_transaction_n': len(group), 'pre_transaction_n': len(pre),
                     'transition_transaction_n': int(group.quarter.eq('2020Q1').sum()),
                     'post_transaction_n': len(post), 'pre_observed_quarters': pre.quarter.nunique(),
                     'post_observed_quarters': post.quarter.nunique(),
                     'pre_missing_quarters_of_12': 12 - pre.quarter.nunique(),
                     'post_missing_quarters_of_15': 15 - post.quarter.nunique(),
                     'both_periods_observed': bool(len(pre) and len(post)),
                     'identity_verified': False, 'coordinate_verified': False,
                     'project_treatment_assigned': False})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', type=Path, required=True)
    parser.add_argument('--coverage', type=Path, required=True)
    parser.add_argument('--matches', type=Path, required=True)
    parser.add_argument('--supplement', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve existing audit; use a new output directory')
    sample = pd.read_csv(args.sample, dtype={'community': str})
    coverage = pd.read_csv(args.coverage, dtype={'community_id': str})
    matched = pd.read_csv(args.matches, dtype={'community_id': str, 'POIID': str})
    supplemental = pd.read_csv(args.supplement, dtype={'community_id': str, 'candidate_POIID': str})
    assert len(sample) == 11231 and len(coverage) == 621
    assert coverage.community_id.is_unique and coverage.clean_transaction_n.sum() == 16199
    table = support_rows(sample, coverage)
    leads = []
    for source, frame, address_col, poi_col in [('exact_name', matched, 'poi_address', 'POIID'),
                                               ('qualified_name', supplemental, 'candidate_address', 'candidate_POIID')]:
        for record in frame.to_dict('records'):
            address = str(record.get(address_col, ''))
            hits = [road for road in ROADS if road in address]
            if hits:
                leads.append({'community_id': record['community_id'], 'POIID': record[poi_col],
                              'road_tokens': '|'.join(hits), 'link_rule': source,
                              'address_is_neighbourhood_assignment': False})
    lead = pd.DataFrame(leads, columns=['community_id', 'POIID', 'road_tokens', 'link_rule',
                                      'address_is_neighbourhood_assignment']).drop_duplicates()
    lead_support = lead.merge(table, on='community_id', validate='many_to_one')
    args.output.mkdir(parents=True)
    table.to_csv(args.output / 'all_621_community_support.csv', index=False, encoding='utf-8-sig')
    lead_support.to_csv(args.output / 'road_address_leads_support.csv', index=False, encoding='utf-8-sig')
    selected = sample[sample.community.isin(lead.community_id)]
    selected.groupby('quarter').agg(transactions=('price', 'size'), communities=('community', 'nunique')).to_csv(
        args.output / 'road_leads_quarter_support.csv', encoding='utf-8-sig')
    unique_support = table[table.community_id.isin(lead.community_id)]
    report = {'scope': 'ADDRESS_LEADS_AND_OBSERVATION_SUPPORT_NOT_PROJECT_SAMPLE',
              'roads': list(ROADS), 'analysis_window': ['2017Q1', '2023Q4'],
              'pre_period': ['2017Q1', '2019Q4'], 'transition': '2020Q1', 'post_period': ['2020Q2', '2023Q4'],
              'coverage_community_n': len(table), 'window_transaction_n': len(sample),
              'road_lead_link_n': len(lead), 'road_lead_community_n': len(unique_support),
              'road_lead_window_transaction_n': len(selected),
              'road_leads_both_periods_n': int(unique_support.both_periods_observed.sum()),
              'road_leads_no_window_transactions_n': int(unique_support.window_transaction_n.eq(0).sum()),
              'project_treatment_assigned': False, 'boundary_distances_computed': False,
              'source_sha256': {k: hashlib.sha256(getattr(args, k).read_bytes()).hexdigest()
                                for k in ['sample', 'coverage', 'matches', 'supplement']}}
    (args.output / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
