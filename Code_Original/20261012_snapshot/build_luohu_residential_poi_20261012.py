"""Extract administrative Luohu POIs and trace candidate matches, never infer identity."""
import ast
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / 'data/supplied_gdata_intake/20261011'
OUT = ROOT / 'data/supplied_gdata_intake/20261012_luohu_residential_poi'
ZIP = Path('C:/Users/Lenovo/OneDrive/ドキュメント/xwechat_files/wxid_aftj4nq0x7ye12_8bc3/msg/file/2026-10/POI (1).zip')
RAW = Path('C:/Users/Lenovo/Downloads/二手房成交房源_深圳 来源贝壳.csv')
GATE = re.compile(r'(?:[-－·（(].*?(?:门|入口|出口)|(?:正门|东门|西门|南门|北门|出入口|入口|出口))[)）]?$')
RESIDENTIAL = re.compile(r'住宅|小区|花园|公寓|宿舍|家属|新村|大院|名苑|雅居|名园|村|苑|阁|庭|园|楼|栋|座|大厦|广场')
NONRES = re.compile(r'商城|商业城|商场|购物|酒店|宾馆|旅馆|工业|产业园|写字楼|办公|物流|厂房|工厂')


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(part)
    return value.hexdigest()


def key(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(value or '')))


def classify(name, category):
    if category != '2010302':
        return 'other_category'
    if GATE.search(name):
        return 'gate_or_entrance'
    if NONRES.search(name):
        return 'explicit_nonresidential_or_mixed'
    if RESIDENTIAL.search(name):
        return 'residential_or_building_candidate'
    return 'unclassified_area_candidate'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def load_communities():
    prior = json.loads((ROOT / 'outputs/price_did_audit_20261003/run_summary.json').read_text(encoding='utf-8'))
    assert digest(RAW) == prior['source_sha256'], 'Transaction source changed; do not reuse frozen counts'
    raw = pd.read_csv(RAW, low_memory=False)
    def number(column):
        return pd.to_numeric(raw[column].astype(str).str.replace(',', '', regex=False).str.extract(r'(-?\d+(?:\.\d+)?)', expand=False), errors='coerce')
    date = pd.to_datetime(raw['成交时间'], errors='coerce')
    listed = pd.to_datetime(raw['挂牌时间'], errors='coerce')
    price, total, area, built = (number(c) for c in ['成交均价 元/平', '成交价格/万', '建筑面积', '建成年代'])
    community = raw['小区详情url'].str.extract(r'(\d+)/?$', expand=False)
    elevator = raw['配备电梯'].map({'有': 1, '无': 0})
    mask = (raw['房屋用途'].eq('普通住宅') & raw['交易权属'].eq('商品房') & raw['区县'].eq('罗湖区')
            & date.notna() & community.notna() & price.gt(0) & total.gt(0) & area.gt(0)
            & (date.dt.year - built).between(0, 120) & elevator.notna() & ~(listed > date)
            & ((total * 10000 - price * area).abs() / (total * 10000)).le(.02))
    clean = raw.loc[mask, ['小区名称', '小区经度(百度)', '小区纬度(百度)']].copy()
    clean['community_id'] = community[mask]
    clean['date'] = date[mask]
    assert len(clean) == prior['luohu_clean_n']
    rows = []
    for cid, group in clean.groupby('community_id', sort=True):
        coords = group[['小区经度(百度)', '小区纬度(百度)']].drop_duplicates()
        coords = [[float(a), float(b)] if pd.notna(a) and pd.notna(b) else [None, None] for a, b in coords.itertuples(index=False, name=None)]
        rows.append({'community_id': cid, 'names': sorted(group['小区名称'].dropna().unique()),
                     'transaction_n': len(group), 'first_date': str(group.date.min().date()),
                     'last_date': str(group.date.max().date()), 'raw_coordinate_pairs': coords})
    assert len(rows) == 621
    return rows, len(clean)


def main():
    OUT.mkdir(exist_ok=True)
    existing_summary = OUT / '核验摘要.json'
    if existing_summary.exists():
        from datetime import datetime
        backup = OUT / ('上轮核验摘要_' + datetime.now().strftime('%H%M%S') + '.json')
        backup.write_bytes(existing_summary.read_bytes())
    source_dir = INTAKE / 'poi_luohu/source_components'
    shp = next(source_dir.glob('*.shp'))
    with zipfile.ZipFile(ZIP) as archive:
        expected = {Path(item.filename).suffix.lower(): item.file_size for item in archive.infolist() if not item.filename.endswith('.xml')}
        for suffix in ('.dbf', '.shp', '.shx', '.prj'):
            assert shp.with_suffix(suffix).stat().st_size == expected[suffix]
    info = pyogrio.read_info(shp)
    assert info['crs'] == 'EPSG:3857' and info['features'] == 788695
    print('Reading FULL city source with Code=440303, no bounding box', flush=True)
    poi = pyogrio.read_dataframe(shp, where="Code = '440303'", use_arrow=True)
    assert len(poi) and poi.crs.to_epsg() == 3857
    assert set(poi.Code) == {'440303'}
    fields = ['POIID', 'Code', 'Type', 'SORTCODE', 'Name_CHN', 'ADDRESS1', 'ADDRESS2', 'ADDRESS3', 'ADDRESS4', 'ADDRESS5', 'ADDRESS6', 'ADDRESS7', 'ADDRESS8', 'BELID', 'BELType', 'OPENFLAG']
    poi = poi[fields + ['geometry']].copy()
    assert poi.geometry.notna().all() and poi.geometry.is_valid.all() and not poi.geometry.is_empty.any()
    missing_district = int(poi.ADDRESS3.isna().sum())
    conflicts = poi.ADDRESS3.notna() & ~poi.ADDRESS3.eq('罗湖区')
    assert not conflicts.any(), 'District Code and ADDRESS3 conflict'
    assert not poi.POIID.duplicated().any(), 'Duplicate source ID needs explicit resolution'
    poi['candidate_role'] = [classify(str(name or ''), str(code)) for name, code in zip(poi.Name_CHN.fillna(''), poi.Type)]
    poi['source_fid_metadata'] = 'POIID retained as string; source IDs not transaction community IDs'
    poi['capture_date_verified'] = False
    poi['position_verified'] = False
    poi['map_frame_verified'] = False
    poi['map_frame_warning'] = 'EPSG projection declaration does not establish underlying map coordinate convention'
    address_fields = [f'ADDRESS{i}' for i in range(1, 9)]
    poi['address_text'] = poi[address_fields].fillna('').astype(str).agg(' '.join, axis=1).str.strip()
    lonlat = poi.to_crs(4326)
    poi['declared_wgs84_lon'] = lonlat.geometry.x
    poi['declared_wgs84_lat'] = lonlat.geometry.y
    candidates = poi[poi.Type.eq('2010302')].copy()
    parents = poi.set_index('POIID')
    candidates['parent_name'] = candidates.BELID.map(parents.Name_CHN).fillna('')
    candidates['parent_found_same_district'] = candidates.BELID.isin(parents.index)
    candidates['parent_link_is_identity_verified'] = False

    communities, transaction_n = load_communities()
    by_name = {}
    for _, row in candidates.iterrows():
        by_name.setdefault(key(row.Name_CHN), []).append(row)
    upstream = INTAKE / 'building_rar/coordinate_hypotheses'
    upstream_audit = json.loads((upstream / '核验摘要.json').read_text(encoding='utf-8'))
    pinned = next(r['sha256'] for r in upstream_audit['source_files'] if r['file'] == 'implementation.py')
    assert digest(upstream / 'implementation.py') == pinned
    source = (upstream / 'implementation.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    assert all(isinstance(node, (ast.Import, ast.Assign, ast.FunctionDef)) for node in tree.body)
    env = {}
    exec(compile(tree, 'sha_pinned_coordinate_diagnostic', 'exec'), env)
    project = Transformer.from_crs(4326, 3857, always_xy=True)
    matches, coverage = [], []
    for community in communities:
        seen = {}
        for name in community['names']:
            for row in by_name.get(key(name), []):
                seen[row.POIID] = row
        coverage.append({'community_id': community['community_id'], 'transaction_names': ';'.join(community['names']),
                         'clean_transaction_n': community['transaction_n'], 'first_date': community['first_date'],
                         'last_date': community['last_date'], 'poi_candidate_n': len(seen),
                         'poi_match_status': 'no_exact_name_candidate' if not seen else ('single_name_candidate' if len(seen) == 1 else 'multiple_name_candidates'),
                         'identity_verified': False, 'coordinate_verified': False})
        for poi_id, row in seen.items():
            record = {'community_id': community['community_id'], 'transaction_names': ';'.join(community['names']),
                      'clean_transaction_n': community['transaction_n'], 'POIID': poi_id, 'poi_name': row.Name_CHN,
                      'poi_type': row.Type, 'candidate_role': row.candidate_role, 'candidate_n_for_community': len(seen),
                      'poi_address': row.address_text, 'poi_declared_lon': row.declared_wgs84_lon,
                      'poi_declared_lat': row.declared_wgs84_lat, 'raw_coordinate_n': len(community['raw_coordinate_pairs']),
                      'raw_as_wgs84_diagnostic_distance_m': None, 'raw_as_gcj02_diagnostic_distance_m': None,
                      'raw_as_bd09_diagnostic_distance_m': None, 'position_accepted': False, 'independent_validation': False}
            pairs = community['raw_coordinate_pairs']
            if len(pairs) == 1 and None not in pairs[0]:
                lon, lat = pairs[0]
                gc_lat, gc_lon = env['gcj2wgs_exact'](lat, lon)
                bd_lat, bd_lon = env['gcj2wgs_exact'](*env['bd2gcj'](lat, lon))
                from shapely.geometry import Point
                for hypothesis, a, b in [('wgs84', lon, lat), ('gcj02', gc_lon, gc_lat), ('bd09', bd_lon, bd_lat)]:
                    candidate = gpd.GeoSeries([Point(*project.transform(a, b))], crs=3857).to_crs(4547).iloc[0]
                    reference = gpd.GeoSeries([row.geometry], crs=3857).to_crs(4547).iloc[0]
                    record[f'raw_as_{hypothesis}_diagnostic_distance_m'] = candidate.distance(reference)
            matches.append(record)
    coverage_df, matches_df = pd.DataFrame(coverage), pd.DataFrame(matches)
    assert matches
    diagnostic = matches_df[(matches_df.candidate_n_for_community == 1) & (matches_df.raw_coordinate_n == 1)].copy()
    distance_fields = [f'raw_as_{h}_diagnostic_distance_m' for h in ['wgs84', 'gcj02', 'bd09']]
    diagnostic = diagnostic.dropna(subset=distance_fields)
    metrics = {}
    for field in distance_fields:
        distances = diagnostic[field]
        metrics[field] = {'n': len(distances), 'median_m': float(distances.median()),
                          'p90_m': float(distances.quantile(.9)), 'within_100m_n': int(distances.le(100).sum()),
                          'within_300m_n': int(distances.le(300).sum())}
    projected = poi.to_crs(4547)
    gpkg = OUT / '罗湖区POI与住宅定位候选_EPSG4547.gpkg'
    projected.to_file(gpkg, layer='luohu_all_poi_code440303', driver='GPKG')
    candidates.to_crs(4547).to_file(gpkg, layer='housing_and_entrance_candidates', driver='GPKG')
    candidates.drop(columns=['geometry']).to_csv(OUT / '罗湖住宅及出入口候选.csv', index=False, encoding='utf-8-sig')
    candidates[candidates.candidate_role.isin(['residential_or_building_candidate', 'unclassified_area_candidate'])].drop(columns='geometry').to_csv(
        OUT / '罗湖住宅主体及楼区待核表.csv', index=False, encoding='utf-8-sig')
    matches_df.to_csv(OUT / '成交小区_POI同名候选连接.csv', index=False, encoding='utf-8-sig')
    coverage_df.to_csv(OUT / '621小区匹配覆盖.csv', index=False, encoding='utf-8-sig')
    type_examples = [{'type_code': code, 'count': len(part), 'example_names': part.Name_CHN.fillna('').head(12).tolist(),
                      'official_type_dictionary_verified': False} for code, part in poi.groupby('Type')]
    write_json(OUT / '类别代码与名称样例.json', type_examples)
    lookup_terms = ['畔山花园', '景福', '莲塘花园', '海关草埔', '置富', '绿茵庭苑', '鹿丹', '都市名园', '中海天钻']
    focal = candidates[candidates.Name_CHN.fillna('').str.contains('|'.join(map(re.escape, lookup_terms)), regex=True)].copy()
    focal.drop(columns='geometry').to_csv(OUT / '重点项目住宅名称线索.csv', index=False, encoding='utf-8-sig')
    write_json(OUT / '核验摘要.json', {
        'source_zip': str(ZIP), 'source_zip_sha256': digest(ZIP), 'source_shapefile': str(shp),
        'source_rows': int(info['features']), 'source_crs_declaration': info['crs'],
        'dbf_last_update': info.get('layer_metadata', {}).get('DBF_DATE_LAST_UPDATE'),
        'dbf_date_is_capture_date_verified': False, 'administrative_filter': "Code='440303', no bbox",
        'luohu_poi_n': len(poi), 'missing_address3_n': missing_district, 'district_address_conflicts_n': int(conflicts.sum()),
        'candidate_poi_n': len(candidates), 'candidate_role_counts': candidates.candidate_role.value_counts().to_dict(),
        'clean_transaction_n': transaction_n, 'clean_community_n': len(coverage_df),
        'communities_with_exact_name_candidate_n': int(coverage_df.poi_candidate_n.gt(0).sum()),
        'single_candidate_communities_n': int(coverage_df.poi_candidate_n.eq(1).sum()),
        'multi_candidate_communities_n': int(coverage_df.poi_candidate_n.gt(1).sum()),
        'candidate_links_n': len(matches_df), 'diagnostic_distances': metrics,
        'coordinate_dependency_warning': 'POI and source CSV may share provider; agreement is not independent validation',
        'source_coordinate_system_verified': False, 'new_transactions': 0, 'production_coordinates_overwritten': False,
        'project_distance_computed': False, 'project_did_run': False,
        'outputs': {str(path.name): digest(path) for path in OUT.glob('*.csv')},
    })
    readback = pyogrio.read_info(gpkg, layer='luohu_all_poi_code440303')
    assert readback['features'] == len(poi) and readback['crs'] == 'EPSG:4547'
    assert pyogrio.read_info(gpkg, layer='housing_and_entrance_candidates')['features'] == len(candidates)
    report = f'''# 罗湖住宅定位候选资料

全市原始POI按Code＝440303筛出{len(poi)}条罗湖记录，不使用上一轮宽窗口作为行政区总量。地址区县非空部分全部与罗湖一致。EPSG:3857是源文件声明，本轮按该声明生成EPSG:4547参照，并不证明地理位置精度或供应商坐标口径已验收。

类别2010302共有{len(candidates)}条候选，混有住宅、宿舍、商业楼和出入口。名称启发式只用作人工分流，不是官方类别解释或住宅身份确认。独立列出明确商业、门点和其他候选，不将它们加总为小区数。

现行清理成交16199笔、621小区保持原口径。同名POI候选连接覆盖{int(coverage_df.poi_candidate_n.gt(0).sum())}个小区，唯一候选{int(coverage_df.poi_candidate_n.eq(1).sum())}个，多候选{int(coverage_df.poi_candidate_n.gt(1).sum())}个；另有无同名候选住宅，未采用最近点或模糊名称强行连接。候选连接不是成交身份验收。

单候选点的WGS84、GCJ02和BD09解释距离另行诊断。这些距离指向POI点而非旧改红线，同供应商依赖和范围差异可能造成表面吻合，不能视为独立坐标认证。保留原始点，不统一纠偏，不产生项目暴露、住宅距离档或新DID。

进一步的双端诊断见“成交与POI_双端坐标口径诊断.csv”。EPSG投影声明与底层地图经纬度口径必须分开核验；若POI底层含GCJ偏移，直接按声明反投影得到的度并非已验收WGS84。新GeoPackage只按原声明投影，明确标注map_frame_verified为False，不应与测绘成果直接叠加计算正式距离。

DBF记录的2020-09-08仅为表文件更新元信息，采集时间和设施开放时间未知。不可据此证明2020年前已存在某设施，尤其不能识别2025年景福回迁后的服务。

上一轮443920条是含其他区的宽窗口记录，旧文件“罗湖窗口POI_WGS84.gpkg”实际为EPSG:3857，已另附错误标识说明，本次交付只引用新的正确命名文件。
'''
    (OUT / '资料口径与使用说明.md').write_text(report, encoding='utf-8')
    print(json.dumps({'luohu_poi_n': len(poi), 'candidate_n': len(candidates),
                      'matched_communities': int(coverage_df.poi_candidate_n.gt(0).sum()),
                      'single_candidates': int(coverage_df.poi_candidate_n.eq(1).sum()), 'diagnostic_metrics': metrics}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
