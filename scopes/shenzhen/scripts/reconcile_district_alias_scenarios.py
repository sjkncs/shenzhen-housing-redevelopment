"""Compare district alias hypotheses with city totals without choosing a source rule."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

DISTRICTS = {'罗湖', '福田', '南山', '盐田', '宝安', '龙岗', '龙华', '坪山', '光明', '大鹏'}


def compare_group(group, tolerance=.05):
    city = group[group.ZONE.eq('全市')]
    if len(city) != 1:
        raise ValueError('Expected exactly one city total')
    district = group[group.normalized_zone.isin(DISTRICTS)]
    collided = district.duplicated('normalized_zone', keep=False)
    rows = []
    for scenario in ['prefer_short_label', 'prefer_suffix_label', 'sum_both_labels']:
        if scenario == 'sum_both_labels':
            selected = district
        else:
            short = district.ZONE.eq(district.normalized_zone)
            preferred = short if scenario == 'prefer_short_label' else ~short
            selected = district[~collided | preferred]
            if selected.normalized_zone.duplicated().any():
                raise ValueError('Multiple source rows within preferred label')
        count = float(selected.CJ_NUM.sum()) - float(city.CJ_NUM.iloc[0])
        area = float(selected.CJ_AREA.sum()) - float(city.CJ_AREA.iloc[0])
        rows.append({'scenario': scenario, 'reported_district_rows': len(selected),
                     'missing_districts': '|'.join(sorted(DISTRICTS - set(selected.normalized_zone))),
                     'count_difference': count, 'area_difference_m2': area,
                     'matches_city_total': count == 0 and abs(area) <= tolerance,
                     'scenario_accepted': False})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--collisions', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new directory')
    source = pd.read_csv(args.source, dtype={'ID': str})
    collisions = pd.read_csv(args.collisions)
    source['normalized_zone'] = source.ZONE.astype(str).str.replace('区', '', regex=False)
    dates = set(collisions.TJ_DATE)
    usages = set(collisions.HOUSE_USAGE2)
    rows, skipped = [], []
    for (date, use), group in source[source.TJ_DATE.isin(dates) & source.HOUSE_USAGE2.isin(usages)].groupby(['TJ_DATE', 'HOUSE_USAGE2']):
        if not group.normalized_zone.duplicated().any():
            continue
        if group.ZONE.eq('全市').sum() != 1:
            skipped.append({'date': date, 'usage': use, 'reason': 'No unique city total'})
            continue
        for row in compare_group(group):
            rows.append({'date': date, 'usage': use, **row})
    table = pd.DataFrame(rows)
    assert len(table)
    counts = table.groupby('scenario').agg(groups=('date', 'size'),
        matching_groups=('matches_city_total', 'sum'),
        maximum_absolute_count_difference=('count_difference', lambda s: s.abs().max()),
        maximum_absolute_area_difference_m2=('area_difference_m2', lambda s: s.abs().max())).reset_index()
    args.output.mkdir(parents=True)
    table.to_csv(args.output / 'alias_scenario_city_checks.csv', index=False, encoding='utf-8-sig')
    counts.to_csv(args.output / 'alias_scenario_summary.csv', index=False, encoding='utf-8-sig')
    summary = {'compared_date_use_groups': len(table) // 3, 'skipped_groups': skipped,
               'area_tolerance_m2': .05, 'scenario_checks': counts.to_dict('records'),
               'accepted_merge_rule': None, 'existing_monthly_data_modified': False,
               'input_sha256': {k: hashlib.sha256(getattr(args, k).read_bytes()).hexdigest() for k in ['source', 'collisions']}}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
