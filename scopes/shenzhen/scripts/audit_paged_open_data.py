"""Verify paged Shenzhen open-data snapshot and write normalized market aggregates."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(p.name != 'README.md' for p in args.output.iterdir()):
        raise FileExistsError('Use a new output directory')
    manifest = json.loads(args.audit.read_text(encoding='utf-8'))
    frames = []
    page_checks = []
    for item in manifest['pages']:
        path = args.pages / ('page_%03d.json' % item['page'])
        raw = path.read_bytes()
        actual = hashlib.sha256(raw).hexdigest().upper()
        assert actual == item['sha256'] and len(json.loads(raw)['data']) == item['rows']
        frames.append(pd.DataFrame(json.loads(raw)['data']))
        page_checks.append({'page': item['page'], 'rows': item['rows'], 'sha256': actual, 'verified': True})
    frame = pd.concat(frames, ignore_index=True)
    assert len(frame) == manifest['reported_total'] == manifest['downloaded_rows']
    required = {'ID', 'TJ_DATE', 'CJ_NUM', 'CJ_AREA', 'HOUSE_USAGE2', 'ZONE'}
    assert required <= set(frame.columns)
    assert frame.ID.astype(str).is_unique
    frame['TJ_DATE'] = pd.to_datetime(frame.TJ_DATE, errors='raise')
    frame['CJ_NUM'] = pd.to_numeric(frame.CJ_NUM, errors='raise')
    frame['CJ_AREA'] = pd.to_numeric(frame.CJ_AREA, errors='raise')
    assert frame.CJ_NUM.ge(0).all() and frame.CJ_AREA.ge(0).all()
    frame['ZONE_NORMALIZED'] = frame.ZONE.astype(str).str.replace('区', '', regex=False)
    collisions = frame[frame.duplicated(['ZONE_NORMALIZED', 'HOUSE_USAGE2', 'TJ_DATE'], keep=False)].copy()
    # Name normalization can collapse separately published rows. Preserve both versions;
    # do not aggregate colliding keys or choose one silently.
    eligible = frame.drop(index=collisions.index)
    housing = eligible[eligible.HOUSE_USAGE2.eq('住宅')]
    luohu = housing[housing.ZONE_NORMALIZED.eq('罗湖')]
    monthly = housing.assign(month=housing.TJ_DATE.dt.to_period('M').astype(str)).groupby(['ZONE_NORMALIZED', 'month']).agg(
        reported_rows=('ID', 'size'), transaction_n=('CJ_NUM', 'sum'), area_m2=('CJ_AREA', 'sum')).reset_index()
    args.output.mkdir(parents=True, exist_ok=True)
    luohu.to_csv(args.output / 'luohu_daily_residential_open_data.csv', index=False, encoding='utf-8-sig')
    collisions.to_csv(args.output / 'normalized_name_collision_rows.csv', index=False, encoding='utf-8-sig')
    monthly.to_csv(args.output / 'district_monthly_residential_open_data.csv', index=False, encoding='utf-8-sig')
    summary = {'scope': 'PAGED_SHENZHEN_OPEN_DATA_ADMINISTRATIVE_TOTALS_NOT_COMMUNITY_PRICES',
               'endpoint': manifest['endpoint'], 'page_n': len(page_checks), 'row_n': len(frame),
               'first_date': str(frame.TJ_DATE.min().date()), 'last_date': str(frame.TJ_DATE.max().date()),
               'luohu_housing_rows': len(luohu), 'luohu_first_date': str(luohu.TJ_DATE.min().date()),
               'luohu_last_date': str(luohu.TJ_DATE.max().date()), 'pages': page_checks,
               'normalized_collision_rows': len(collisions), 'collision_rows_excluded_from_summaries': True,
               'has_community_id': False, 'has_price': False, 'has_coordinates': False,
               'usable_for_project_price_did': False}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
