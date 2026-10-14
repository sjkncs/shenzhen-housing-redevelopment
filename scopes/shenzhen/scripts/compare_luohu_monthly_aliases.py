"""Compare reported Luohu monthly totals with and without alias-collision rows."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def compare_months(clean, collisions):
    columns = ['ID', 'TJ_DATE', 'CJ_NUM', 'CJ_AREA']
    clean, collisions = clean[columns].copy(), collisions[columns].copy()
    if not clean.ID.is_unique or not collisions.ID.is_unique or set(clean.ID) & set(collisions.ID):
        raise ValueError('Overlapping or duplicate source IDs')
    all_rows = pd.concat([clean, collisions], ignore_index=True)
    if all_rows.empty:
        raise ValueError('No observations')
    for frame in [clean, all_rows]:
        frame['TJ_DATE'] = pd.to_datetime(frame.TJ_DATE, errors='raise')
        for c in ['CJ_NUM', 'CJ_AREA']:
            frame[c] = pd.to_numeric(frame[c], errors='raise')
            if frame[c].isna().any() or frame[c].lt(0).any():
                raise ValueError('Invalid source total')
    rows = []
    for month in pd.period_range(all_rows.TJ_DATE.min(), all_rows.TJ_DATE.max(), freq='M'):
        isolated = clean[clean.TJ_DATE.dt.to_period('M').eq(month)]
        summed = all_rows[all_rows.TJ_DATE.dt.to_period('M').eq(month)]
        count_base = float(isolated.CJ_NUM.sum()) if len(isolated) else None
        area_base = float(isolated.CJ_AREA.sum()) if len(isolated) else None
        count_all = float(summed.CJ_NUM.sum()) if len(summed) else None
        area_all = float(summed.CJ_AREA.sum()) if len(summed) else None
        rows.append({'month': str(month), 'calendar_days': month.days_in_month,
                     'isolated_observed_days': isolated.TJ_DATE.nunique(),
                     'additive_observed_days': summed.TJ_DATE.nunique(),
                     'isolated_reported_count': count_base, 'additive_reported_count': count_all,
                     'isolated_reported_area_m2': area_base, 'additive_reported_area_m2': area_all,
                     'additional_reported_count': count_all - count_base if count_base is not None and count_all is not None else None,
                     'additional_reported_area_m2': area_all - area_base if area_base is not None and area_all is not None else None,
                     'count_change_percent_vs_isolated': 100 * (count_all - count_base) / count_base if count_base and count_all is not None else None,
                     'additive_rule_source_confirmed': False, 'missing_days_filled_with_zero': False})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean', type=Path, required=True)
    parser.add_argument('--collisions', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    clean = pd.read_csv(args.clean, dtype={'ID': str})
    collisions = pd.read_csv(args.collisions, dtype={'ID': str})
    assert clean.ZONE_NORMALIZED.eq('罗湖').all() and clean.HOUSE_USAGE2.eq('住宅').all()
    collisions = collisions[collisions.ZONE_NORMALIZED.eq('罗湖') & collisions.HOUSE_USAGE2.eq('住宅')]
    result = compare_months(clean, collisions)
    affected = result[result.additional_reported_count.fillna(0).ne(0) | result.additional_reported_area_m2.fillna(0).ne(0)]
    args.output.mkdir(parents=True)
    result.to_csv(args.output / 'luohu_monthly_alias_sensitivity.csv', index=False, encoding='utf-8-sig')
    affected.to_csv(args.output / 'affected_months.csv', index=False, encoding='utf-8-sig')
    summary = {'scope': 'MONTHLY_REPORTED_VOLUME_ALIAS_SENSITIVITY_NOT_PRICE_EFFECT',
               'isolated_source_rows': len(clean), 'collision_source_rows': len(collisions),
               'affected_months': affected.month.tolist(),
               'additional_reported_count': int(collisions.CJ_NUM.sum()),
               'additional_reported_area_m2': float(collisions.CJ_AREA.sum()),
               'existing_monthly_results_modified': False, 'official_merge_rule_accepted': False,
               'inputs_sha256': {k: hashlib.sha256(getattr(args, k).read_bytes()).hexdigest() for k in ['clean', 'collisions']}}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))
    print(affected.to_string(index=False))


if __name__ == '__main__':
    main()
