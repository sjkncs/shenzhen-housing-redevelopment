"""Check all-use totals within each original district label, without merging labels."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def reconcile(group, tolerance=.05):
    total = group[group.HOUSE_USAGE2.eq('全部')]
    detail = group[~group.HOUSE_USAGE2.eq('全部')]
    if len(total) != 1 or detail.empty:
        return {'checkable': False, 'matches': False, 'count_difference': None, 'area_difference_m2': None}
    if group.HOUSE_USAGE2.duplicated().any():
        raise ValueError('Duplicate use category within original label and date')
    count = float(detail.CJ_NUM.sum() - total.CJ_NUM.iloc[0])
    area = float(detail.CJ_AREA.sum() - total.CJ_AREA.iloc[0])
    return {'checkable': True, 'matches': count == 0 and abs(area) <= tolerance,
            'count_difference': count, 'area_difference_m2': area}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    source = pd.read_csv(args.source, dtype={'ID': str})
    assert source.ID.is_unique
    for field in ['CJ_NUM', 'CJ_AREA']:
        source[field] = pd.to_numeric(source[field], errors='raise')
        assert source[field].notna().all() and source[field].ge(0).all()
    suffix = source[source.ZONE.str.endswith('区')]
    assert not suffix.empty
    keys = {(name[:-1], date) for name, date in zip(suffix.ZONE, suffix.TJ_DATE)}
    rows = []
    for (label, date), group in source.groupby(['ZONE', 'TJ_DATE']):
        name = label[:-1] if label.endswith('区') else label
        if (name, date) not in keys:
            continue
        rows.append({'source_zone_label': label, 'date': date,
                     'label_type': 'suffix' if label.endswith('区') else 'short',
                     'source_rows': len(group), 'detail_categories': '|'.join(sorted(set(group.HOUSE_USAGE2) - {'全部'})),
                     **reconcile(group), 'source_definition_confirmed': False})
    table = pd.DataFrame(rows)
    counts = table.groupby('label_type').agg(groups=('date', 'size'), checkable_groups=('checkable', 'sum'),
                                           matching_groups=('matches', 'sum')).reset_index()
    args.output.mkdir(parents=True)
    table.to_csv(args.output / 'original_label_use_reconciliation.csv', index=False, encoding='utf-8-sig')
    counts.to_csv(args.output / 'label_type_check_summary.csv', index=False, encoding='utf-8-sig')
    summary = {'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
               'suffix_source_rows': len(suffix), 'suffix_districts_n': suffix.ZONE.nunique(),
               'suffix_first_date': suffix.TJ_DATE.min(), 'suffix_last_date': suffix.TJ_DATE.max(),
               'category_checks': counts.to_dict('records'), 'area_tolerance_m2': .05,
               'merge_rule_accepted': False, 'source_definition_confirmed': False,
               'existing_monthly_tables_modified': False}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
