"""Publish district-level coverage only; never write individual transaction rows."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def clean_mask(raw):
    def number(column):
        return pd.to_numeric(raw[column].astype(str).str.replace(',', '', regex=False)
                             .str.extract(r'(-?\d+(?:\.\d+)?)', expand=False), errors='coerce')
    date = pd.to_datetime(raw['成交时间'], errors='coerce')
    listed = pd.to_datetime(raw['挂牌时间'], errors='coerce')
    price, total, area, built = [number(c) for c in ['成交均价 元/平', '成交价格/万', '建筑面积', '建成年代']]
    community = raw['小区详情url'].str.extract(r'(\d+)/?$', expand=False)
    mask = (raw['房屋用途'].eq('普通住宅') & raw['交易权属'].eq('商品房')
            & date.notna() & community.notna() & price.gt(0) & total.gt(0) & area.gt(0)
            & (date.dt.year - built).between(0, 120) & raw['配备电梯'].isin(['有', '无'])
            & ~(listed > date)
            & ((total * 10000 - price * area).abs() / (total * 10000)).le(.02))
    return mask, date, community


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'summary')
    args = parser.parse_args()
    raw = pd.read_csv(args.input, low_memory=False)
    mask, date, community = clean_mask(raw)
    frame = pd.DataFrame({'district': raw['区县'].fillna('UNKNOWN'), 'date': date, 'community': community})
    table = frame[mask].groupby('district').agg(transaction_n=('date', 'size'),
                                              community_n=('community', 'nunique'),
                                              first_date=('date', 'min'), last_date=('date', 'max')).reset_index()
    for c in ['first_date', 'last_date']:
        table[c] = table[c].dt.strftime('%Y-%m-%d')
    result = {'scope': 'SHENZHEN_SOURCE_COVERAGE_NOT_CITYWIDE_CAUSAL_ESTIMATE',
              'source_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
              'raw_n': len(raw), 'clean_n': int(mask.sum()), 'excluded_n': int((~mask).sum()),
              'first_date': str(date[mask].min().date()), 'last_date': str(date[mask].max().date()),
              'price_type': 'Source-reported transaction prices; platform sample, not official census',
              'raw_data_redistributed': False}
    args.output.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output / 'district_coverage.csv', index=False, encoding='utf-8-sig')
    (args.output / 'coverage.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
