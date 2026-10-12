"""Joint coordinate hypotheses for transaction and POI points, without accepting either."""
import ast
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/supplied_gdata_intake/20261012_luohu_residential_poi'
RAW = Path(os.environ.get('SHENZHEN_TRANSACTION_CSV', 'data/raw/shenzhen_transactions.csv'))
PINNED = ROOT / 'data/supplied_gdata_intake/20261011/building_rar/coordinate_hypotheses'


def main():
    audit = json.loads((PINNED / '核验摘要.json').read_text(encoding='utf-8'))
    source = (PINNED / 'implementation.py').read_bytes()
    expected = next(r['sha256'] for r in audit['source_files'] if r['file'] == 'implementation.py')
    assert hashlib.sha256(source).hexdigest() == expected
    tree = ast.parse(source.decode('utf-8'))
    assert all(isinstance(n, (ast.Import, ast.Assign, ast.FunctionDef)) for n in tree.body)
    functions = {}
    exec(compile(tree, 'pinned_math_conversion', 'exec'), functions)
    def variants(lon, lat):
        gc_lat, gc_lon = functions['gcj2wgs_exact'](lat, lon)
        bd_lat, bd_lon = functions['gcj2wgs_exact'](*functions['bd2gcj'](lat, lon))
        return {'wgs84': (lon, lat), 'gcj02': (gc_lon, gc_lat), 'bd09': (bd_lon, bd_lat)}
    matches = pd.read_csv(OUT / '成交小区_POI同名候选连接.csv', dtype={'community_id': str, 'POIID': str})
    matches = matches[(matches.candidate_n_for_community == 1) & (matches.raw_coordinate_n == 1)].copy()
    raw = pd.read_csv(RAW, usecols=['小区详情url', '小区经度(百度)', '小区纬度(百度)'], low_memory=False)
    raw['cid'] = raw['小区详情url'].str.extract(r'(\d+)/?$', expand=False)
    unique = raw[['cid', '小区经度(百度)', '小区纬度(百度)']].drop_duplicates()
    duplicate_ids = set(unique.loc[unique.cid.duplicated(keep=False), 'cid'])
    unique = unique[~unique.cid.isin(duplicate_ids)].set_index('cid')
    geod = Geod(ellps='WGS84')
    rows = []
    for _, m in matches.iterrows():
        if m.community_id not in unique.index:
            continue
        r = unique.loc[m.community_id]
        if pd.isna(r['小区经度(百度)']) or pd.isna(r['小区纬度(百度)']):
            continue
        transaction = variants(float(r['小区经度(百度)']), float(r['小区纬度(百度)']))
        poi = variants(float(m.poi_declared_lon), float(m.poi_declared_lat))
        for a, left in transaction.items():
            for b, right in poi.items():
                distance = abs(geod.inv(*left, *right)[2])
                rows.append({'community_id': m.community_id, 'transaction_names': m.transaction_names,
                             'POIID': m.POIID, 'poi_name': m.poi_name,
                             'transaction_coordinate_hypothesis': a, 'poi_underlying_degree_hypothesis': b,
                             'diagnostic_point_pair_distance_m': distance,
                             'independently_verified': False, 'accepted_housing_position': False})
    table = pd.DataFrame(rows)
    assert len(table) and len(table) % 9 == 0
    table.to_csv(OUT / '成交与POI_双端坐标口径诊断.csv', index=False, encoding='utf-8-sig')
    preferred_hypothesis = table[(table.transaction_coordinate_hypothesis == 'bd09') & (table.poi_underlying_degree_hypothesis == 'gcj02')]
    preferred_hypothesis[preferred_hypothesis.diagnostic_point_pair_distance_m > 100].sort_values(
        'diagnostic_point_pair_distance_m', ascending=False).to_csv(
        OUT / 'BD09_GCJ02假设下超过100米_待核小区.csv', index=False, encoding='utf-8-sig')
    statistics = []
    for (a, b), group in table.groupby(['transaction_coordinate_hypothesis', 'poi_underlying_degree_hypothesis']):
        distances = group.diagnostic_point_pair_distance_m
        statistics.append({'transaction_hypothesis': a, 'poi_hypothesis': b, 'matched_community_n': len(group),
                           'median_m': float(distances.median()), 'p90_m': float(distances.quantile(.9)),
                           'within_100m_n': int(distances.le(100).sum()), 'within_300m_n': int(distances.le(300).sum())})
    (OUT / '双端坐标诊断摘要.json').write_text(json.dumps({
        'upstream_commit': audit['commit'], 'source_implementation_sha256': expected,
        'matched_community_n': int(len(table) / 9), 'candidate_combinations': statistics,
        'interpretation': 'Hypothesis selection by agreement, not independent surveying accuracy or confirmation of provider CRS',
        'uniform_correction_accepted': False, 'source_or_production_modified': False,
        'jingfu_independent_crs_boundary_converted': False,
        'preferred_hypothesis_is_not_acceptance': 'transaction BD09 and POI GCJ02; diagnostics only',
    }, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    lines = ['# 双端坐标解释诊断', '',
             'POI声明EPSG:3857，但该声明不能独自证明供应商底层经纬度未含地图偏移。首先按声明投影反算度，再分别按WGS84、GCJ02、BD09解释；成交原点同样形成三个候选。共九种组合，以同名唯一候选小区作点对一致性诊断。',
             '不能把两个来源有共同供应商时的吻合当独立验证，不能以最小距离反推全表真值。POI点与成交小区点也未必表示同一房角、入口或中心。',
             '未修改任何原坐标或生产样本，未转换深圳独立坐标征收图。建议优先向提供者确认双方地图口径；再用独立地址、测绘或可靠设施坐标验证。诊断改善不解锁正式项目距离。']
    (OUT / '双端坐标解释说明.md').write_text('\n\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(sorted(statistics, key=lambda r: r['median_m']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
