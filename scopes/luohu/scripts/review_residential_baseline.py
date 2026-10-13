"""Record source-reported baseline evidence without accepting residence identity."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def classify(first_date, years):
    years = sorted(set(years))
    if pd.notna(first_date) and pd.Timestamp(first_date) < pd.Timestamp('2020-01-01'):
        return 'platform_transaction_observed_before_2020'
    if years and min(years) >= 2020:
        return 'post2020_construction_reported_requires_review'
    if years and min(years) < 2020:
        return 'pre2020_construction_reported_without_pre2020_transaction'
    return 'insufficient_source_evidence'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', type=Path, required=True)
    parser.add_argument('--coverage', type=Path, required=True)
    parser.add_argument('--leads', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    sample = pd.read_csv(args.sample, dtype={'community': str})
    coverage = pd.read_csv(args.coverage, dtype={'community_id': str})
    leads = pd.read_csv(args.leads, dtype={'community_id': str})
    assert coverage.community_id.is_unique and leads.community_id.is_unique
    rows = []
    for lead in leads.to_dict('records'):
        covered = coverage[coverage.community_id.eq(lead['community_id'])]
        assert len(covered) == 1
        record = covered.iloc[0]
        years = sorted(sample.loc[sample.community.eq(lead['community_id']), 'year_built'].dropna().astype(int).unique().tolist())
        rows.append({'community_id': lead['community_id'], 'transaction_names': lead['transaction_names'],
                     'first_source_transaction_date': record.first_date,
                     'last_source_transaction_date': record.last_date,
                     'reported_construction_years': '|'.join(map(str, years)),
                     'reported_years_conflict': len(years) > 1,
                     'baseline_evidence': classify(record.first_date, years),
                     'window_transaction_n': lead['window_transaction_n'],
                     'both_periods_observed': lead['both_periods_observed'],
                     'official_residential_identity_verified': False,
                     'boundary_distance_verified': False, 'treatment_assigned': False})
    table = pd.DataFrame(rows)
    args.output.mkdir(parents=True)
    table.to_csv(args.output / 'baseline_evidence.csv', index=False, encoding='utf-8-sig')
    summary = {'candidate_n': len(table), 'reference_cutoff': '2020-01-01',
               'reference_is_not_earliest_anticipation_date': True,
               'baseline_evidence_counts': table.baseline_evidence.value_counts().to_dict(),
               'conflicting_reported_years_n': int(table.reported_years_conflict.sum()),
               'identity_accepted_n': 0, 'treatment_assigned_n': 0,
               'inputs_sha256': {key: hashlib.sha256(getattr(args, key).read_bytes()).hexdigest()
                                 for key in ['sample', 'coverage', 'leads']}}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(table[['transaction_names', 'reported_construction_years', 'baseline_evidence']].to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
