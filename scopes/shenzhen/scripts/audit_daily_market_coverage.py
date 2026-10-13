"""Audit missing dates and district reconciliation without filling absent rows with zero."""
import argparse
import calendar
import hashlib
import json
from pathlib import Path
import zipfile

import pandas as pd

DISTRICTS = {'罗湖', '福田', '南山', '盐田', '宝安', '龙岗', '龙华', '坪山', '光明', '大鹏'}


def monthly_coverage(frame):
    if frame['日期'].duplicated().any():
        raise ValueError('Duplicate daily observations')
    rows = []
    for month in pd.period_range(frame['日期'].min(), frame['日期'].max(), freq='M'):
        group = frame[frame['日期'].dt.to_period('M').eq(month)]
        days = calendar.monthrange(month.year, month.month)[1]
        n = group['日期'].nunique()
        rows.append({'month': str(month), 'calendar_days': days, 'observed_days': n,
                     'missing_days': days - n, 'calendar_coverage_complete': n == days,
                     'reported_transaction_n': int(group['成交套数'].sum()) if n else None,
                     'reported_area_m2': float(group['成交面积'].sum()) if n else None,
                     'missing_days_filled_with_zero': False})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Select a new output directory')
    with zipfile.ZipFile(args.zip) as archive:
        assert archive.testzip() is None
        names = [n for n in archive.namelist() if n.endswith('.csv')]
        assert len(names) == 1
        raw = pd.read_csv(archive.open(names[0]), encoding='utf-8-sig')
    duplicate_n = int(raw.duplicated(['所属区', '用途', '日期'], keep=False).sum())
    if duplicate_n:
        raise ValueError('Duplicate district-use-date keys: ' + str(duplicate_n))
    raw['日期'] = pd.to_datetime(raw['日期'], errors='raise')
    for c in ['成交套数', '成交面积']:
        raw[c] = pd.to_numeric(raw[c], errors='raise')
        assert raw[c].notna().all() and raw[c].ge(0).all()
    assert (raw['成交套数'] % 1 == 0).all()
    housing = raw[raw['用途'].eq('住宅')]
    luohu = housing[housing['所属区'].eq('罗湖')].copy()
    assert not luohu.empty
    monthly = monthly_coverage(luohu)
    dates = pd.date_range(raw['日期'].min(), raw['日期'].max())
    missing = pd.DataFrame({'date': dates.difference(luohu['日期'])})
    reconciled = []
    for date, group in housing.groupby('日期'):
        city = group[group['所属区'].eq('全市')]
        district = group[group['所属区'].isin(DISTRICTS)]
        if len(city) != 1:
            continue
        missing_districts = sorted(DISTRICTS - set(district['所属区']))
        count_diff = int(district['成交套数'].sum() - city['成交套数'].iloc[0])
        area_diff = float(district['成交面积'].sum() - city['成交面积'].iloc[0])
        reconciled.append({'date': str(date.date()), 'reported_districts': len(district),
                           'missing_districts': '|'.join(missing_districts),
                           'reported_count_minus_city': count_diff, 'reported_area_minus_city_m2': area_diff,
                           'reported_totals_agree': count_diff == 0 and abs(area_diff) <= .05,
                           'all_ten_districts_present': not missing_districts})
    comparison = pd.DataFrame(reconciled)
    args.output.mkdir(parents=True)
    monthly.to_csv(args.output / 'luohu_monthly_reported_coverage.csv', index=False, encoding='utf-8-sig')
    missing.to_csv(args.output / 'luohu_absent_calendar_dates.csv', index=False, encoding='utf-8-sig')
    comparison.to_csv(args.output / 'residential_district_reconciliation.csv', index=False, encoding='utf-8-sig')
    report = {'source_sha256': hashlib.sha256(args.zip.read_bytes()).hexdigest(),
              'raw_rows': len(raw), 'duplicate_key_rows': duplicate_n,
              'raw_first_date': str(raw['日期'].min().date()), 'raw_last_date': str(raw['日期'].max().date()),
              'luohu_observed_days': luohu['日期'].nunique(), 'luohu_absent_days_within_source_range': len(missing),
              'fully_covered_calendar_months': monthly.loc[monthly.calendar_coverage_complete, 'month'].tolist(),
              'city_dates_checked': len(comparison),
              'reported_district_sum_mismatch_days': int((~comparison.reported_totals_agree).sum()),
              'city_dates_with_missing_district_rows': int((~comparison.all_ten_districts_present).sum()),
              'raw_exactly_10000_rows_is_truncation_proof': False,
              'missing_row_is_zero_transaction': False, 'official_market_census_verified': False,
              'usable_for_project_price_did': False}
    (args.output / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
