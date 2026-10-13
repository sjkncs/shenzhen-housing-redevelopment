"""Classify normalized district collisions without selecting or merging versions."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def classify_group(group):
    if len(group) < 2:
        raise ValueError('Expected multiple source records')
    count_same = group.CJ_NUM.nunique(dropna=False) == 1
    area_same = group.CJ_AREA.nunique(dropna=False) == 1
    if count_same and area_same:
        return '套数面积数值相同但来源记录不同'
    if count_same:
        return '套数相同面积不同'
    if area_same:
        return '面积相同套数不同'
    return '套数和面积均不同'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new audit directory')
    data = pd.read_csv(args.input, dtype={'ID': str})
    assert data.ID.is_unique
    assert data[['CJ_NUM', 'CJ_AREA', 'TJ_DATE', 'ZONE_NORMALIZED', 'HOUSE_USAGE2']].notna().all().all()
    rows = []
    for (zone, use, date), group in data.groupby(['ZONE_NORMALIZED', 'HOUSE_USAGE2', 'TJ_DATE']):
        category = classify_group(group)
        rows.append({'district': zone, 'usage': use, 'date': date, 'source_rows': len(group),
                     'original_zone_labels': '|'.join(sorted(group.ZONE.unique())),
                     'source_ids': '|'.join(group.ID), 'classification': category,
                     'count_min': group.CJ_NUM.min(), 'count_max': group.CJ_NUM.max(),
                     'area_min': group.CJ_AREA.min(), 'area_max': group.CJ_AREA.max(),
                     'source_version_selected': False, 'added_to_monthly_summary': False})
    result = pd.DataFrame(rows)
    args.output.mkdir(parents=True)
    result.to_csv(args.output / 'collision_group_classification.csv', index=False, encoding='utf-8-sig')
    result.groupby(['district', 'classification']).agg(groups=('date', 'size'),
        first_date=('date', 'min'), last_date=('date', 'max')).reset_index().to_csv(
            args.output / 'collision_district_summary.csv', index=False, encoding='utf-8-sig')
    summary = {'source_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
               'source_rows': len(data), 'collision_groups': len(result),
               'first_date': result.date.min(), 'last_date': result.date.max(),
               'classification_counts': result.classification.value_counts().to_dict(),
               'date_counts': result.date.value_counts().to_dict(),
               'source_version_selected': False, 'existing_monthly_results_changed': False}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
