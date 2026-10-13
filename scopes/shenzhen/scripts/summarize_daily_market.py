"""Summarize administrative daily resale totals; not a community price panel."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.glob('*.csv')):
        raise FileExistsError('Use a new output directory')
    with zipfile.ZipFile(args.zip) as archive:
        assert archive.testzip() is None
        names = [name for name in archive.namelist() if name.lower().endswith('.csv')]
        assert len(names) == 1
        raw = pd.read_csv(archive.open(names[0]), encoding='utf-8-sig')
    required = {'所属区', '用途', '日期', '成交套数', '成交面积'}
    assert required <= set(raw.columns)
    raw['日期'] = pd.to_datetime(raw['日期'], errors='raise')
    raw['成交套数'] = pd.to_numeric(raw['成交套数'], errors='raise')
    raw['成交面积'] = pd.to_numeric(raw['成交面积'], errors='raise')
    assert raw['成交套数'].ge(0).all() and raw['成交面积'].ge(0).all()
    luohu = raw[(raw['所属区'].eq('罗湖')) & (raw['用途'].eq('住宅'))].copy()
    assert not luohu.empty
    luohu = luohu[['日期', '成交套数', '成交面积']].sort_values('日期')
    args.output.mkdir(parents=True, exist_ok=True)
    luohu.to_csv(args.output / 'luohu_daily_residential_market.csv', index=False, encoding='utf-8-sig')
    all_summary = raw.groupby(['所属区', '用途'], dropna=False).agg(
        first_date=('日期', 'min'), last_date=('日期', 'max'), rows=('日期', 'size'),
        transaction_n=('成交套数', 'sum'), area_m2=('成交面积', 'sum')).reset_index()
    all_summary.to_csv(args.output / 'district_use_coverage.csv', index=False, encoding='utf-8-sig')
    summary = {'scope': 'DAILY_ADMINISTRATIVE_MARKET_TOTALS_NOT_COMMUNITY_PANEL',
               'source_sha256': hashlib.sha256(args.zip.read_bytes()).hexdigest(),
               'csv_rows': len(raw), 'luohu_residential_rows': len(luohu),
               'first_date': str(raw['日期'].min().date()), 'last_date': str(raw['日期'].max().date()),
               'luohu_residential_first_date': str(luohu['日期'].min().date()),
               'luohu_residential_last_date': str(luohu['日期'].max().date()),
               'has_community_id': False, 'has_price': False, 'has_coordinates': False,
               'usable_for_project_did': False}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
