"""Review homonyms and focal addresses without adopting coordinates or spatial treatment."""
import ast
import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup
import pandas as pd
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/supplied_gdata_intake/20261012_luohu_residential_poi'
OUT = ROOT / 'data/supplied_gdata_intake/20261012_luohu_poi_identity_review'
PINNED = ROOT / 'data/supplied_gdata_intake/20261011/building_rar/coordinate_hypotheses'
PROTECTED_QUALIFIERS = re.compile(r'期|院|区|栋|幢|座|楼|单元')


def name_key(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(value)))


def qualified_key(value):
    name = name_key(value)
    match = re.search(r'\(([^()]*)\)$', name)
    if match and not PROTECTED_QUALIFIERS.search(match.group(1)):
        return name[:match.start()]
    return name


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def registry_from_transactions(path, community_ids):
    raw = pd.read_csv(path, usecols=['小区详情url', '小区经度(百度)', '小区纬度(百度)'], low_memory=False)
    raw['community_id'] = raw['小区详情url'].str.extract(r'(\d+)/?$', expand=False)
    raw = raw[raw.community_id.isin(community_ids)]
    rows = []
    for cid, group in raw.groupby('community_id', sort=True):
        pairs = []
        for lon, lat in group[['小区经度(百度)', '小区纬度(百度)']].drop_duplicates().itertuples(index=False, name=None):
            pairs.append([float(lon) if pd.notna(lon) else None, float(lat) if pd.notna(lat) else None])
        rows.append({'贝壳小区URL标识': cid, '原始百度标签坐标对集合': json.dumps(pairs, allow_nan=False)})
    registry = pd.DataFrame(rows, columns=['贝壳小区URL标识', '原始百度标签坐标对集合']).set_index('贝壳小区URL标识')
    if not set(community_ids) <= set(registry.index):
        raise ValueError('Required community missing from transaction source')
    return registry


def download(sid, url, concept):
    folder = OUT / 'official_sources'
    folder.mkdir(exist_ok=True)
    path = folder / (sid + '.html')
    row = {'source_id': sid, 'url': url, 'concept': concept, 'status': 'failed'}
    try:
        if not path.exists():
            temp = path.with_suffix('.download')
            result = subprocess.run(['curl.exe', '--fail', '--location', '--silent', '--show-error', '--max-time', '30',
                                     '--max-filesize', '10000000', '--output', str(temp), url], capture_output=True, timeout=35)
            if result.returncode:
                raise RuntimeError(result.stderr.decode(errors='replace'))
            raw = temp.read_bytes()
            soup = BeautifulSoup(raw, 'html.parser')
            if len(soup.get_text(strip=True)) < 100:
                raise ValueError('Not a usable source page')
            temp.rename(path)
        soup = BeautifulSoup(path.read_bytes(), 'html.parser')
        text = soup.get_text('\n', strip=True)
        (folder / (sid + '.txt')).write_text(text, encoding='utf-8')
        row.update(status='archived', file=str(path), sha256=sha(path), title=soup.title.get_text() if soup.title else '')
    except Exception as exc:
        row['error'] = str(exc)
    return row


def main():
    global BASE, OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=BASE)
    parser.add_argument('--output', type=Path, default=OUT)
    parser.add_argument('--transactions', type=Path)
    parser.add_argument('--skip-official-fetch', action='store_true')
    args = parser.parse_args()
    BASE, OUT = args.base, args.output
    if OUT.exists():
        raise FileExistsError('Preserve existing review; select a new --output directory')
    OUT.mkdir(parents=True, exist_ok=True)
    files = [BASE / n for n in ['罗湖住宅及出入口候选.csv', '成交小区_POI同名候选连接.csv',
                                'BD09_GCJ02假设下超过100米_待核小区.csv', '621小区匹配覆盖.csv']]
    input_hashes = {str(p): sha(p) for p in files}
    poi = pd.read_csv(files[0], dtype=str, keep_default_na=False)
    links = pd.read_csv(files[1], dtype={'community_id': str, 'POIID': str})
    outliers = pd.read_csv(files[2], dtype={'community_id': str, 'POIID': str})
    coverage = pd.read_csv(files[3], dtype={'community_id': str})
    assert len(outliers) == 18 and len(coverage) == 621
    core = poi[~poi.candidate_role.isin(['gate_or_entrance', 'explicit_nonresidential_or_mixed'])].copy()
    by_key = {}
    for _, row in core.iterrows():
        by_key.setdefault(qualified_key(row.Name_CHN), []).append(row)
    input_registry = ROOT / 'data/acquisition/community_matching/20260926T081831338704Z/深圳小区身份与原始坐标.csv'
    if args.transactions is not None or not input_registry.exists():
        source = args.transactions or Path(os.environ.get('SHENZHEN_TRANSACTION_CSV', 'data/raw/shenzhen_transactions.csv'))
        expected = json.loads((ROOT / 'outputs/price_did_audit_20261003/run_summary.json').read_text(encoding='utf-8'))['source_sha256']
        if sha(source) != expected:
            raise ValueError('Transaction source differs from frozen research input')
        registry = registry_from_transactions(source, set(outliers.community_id))
        registry_origin = {'method': 'rebuilt_from_public_transaction_source', 'sha256': expected,
                           'needed_community_n': len(registry), 'coordinate_system_accepted': False}
    else:
        registry = pd.read_csv(input_registry, dtype=str, keep_default_na=False).set_index('贝壳小区URL标识')
        registry_origin = {'method': 'legacy_registry', 'sha256': sha(input_registry)}
    provenance = json.loads((PINNED / '核验摘要.json').read_text(encoding='utf-8'))
    assert sha(PINNED / 'implementation.py') == next(x['sha256'] for x in provenance['source_files'] if x['file'] == 'implementation.py')
    tree = ast.parse((PINNED / 'implementation.py').read_text(encoding='utf-8'))
    assert all(isinstance(n, (ast.Import, ast.Assign, ast.FunctionDef)) for n in tree.body)
    env = {}
    exec(compile(tree, 'pinned_diagnostic_only', 'exec'), env)
    def gcj_wgs(lon, lat):
        a, b = env['gcj2wgs_exact'](float(lat), float(lon))
        return b, a
    geod = Geod(ellps='WGS84')
    def candidate_distance(cid, row):
        pairs = json.loads(registry.loc[cid, '原始百度标签坐标对集合'])
        if len(pairs) != 1 or any(v is None for v in pairs[0]):
            return None
        lon, lat = map(float, pairs[0])
        a, b = env['gcj2wgs_exact'](*env['bd2gcj'](lat, lon))
        right = gcj_wgs(row.declared_wgs84_lon, row.declared_wgs84_lat)
        return abs(geod.inv(b, a, *right)[2])
    reviews, summaries = [], []
    for _, record in outliers.iterrows():
        name = record.transaction_names
        candidates = list(by_key.get(qualified_key(name), []))
        # Include related names for review, not for automatic identity resolution.
        for _, row in core.iterrows():
            if name_key(name) in name_key(row.Name_CHN) and row.POIID not in {x.POIID for x in candidates}:
                candidates.append(row)
        for row in candidates:
            reviews.append({'community_id': record.community_id, 'transaction_name': name,
                            'previous_exact_POIID': record.POIID, 'candidate_POIID': row.POIID,
                            'candidate_name': row.Name_CHN, 'candidate_address': row.address_text,
                            'match_rule': 'exact' if name_key(name) == name_key(row.Name_CHN) else
                                          ('address_parenthesis_candidate' if qualified_key(name) == qualified_key(row.Name_CHN) else 'related_name_review_only'),
                            'diagnostic_pair_distance_m_BD09_GCJ02': candidate_distance(record.community_id, row),
                            'candidate_BELID': row.BELID, 'identity_verified': False,
                            'nearest_candidate_selected': False, 'coordinate_replaced': False})
        risk = 'needs_position_or_extent_check'
        if len(candidates) > 1:
            risk = 'homonym_or_name_variant_ambiguity'
        summaries.append({'community_id': record.community_id, 'transaction_name': name,
                          'previous_diagnostic_distance_m': record.diagnostic_point_pair_distance_m,
                          'related_core_candidates_n': len(candidates), 'review_reason': risk,
                          'review_status': 'unresolved', 'accepted_POIID': ''})
    pd.DataFrame(reviews).to_csv(OUT / '18小区_全部相关POI候选.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(summaries).to_csv(OUT / '18小区_问题分流.csv', index=False, encoding='utf-8-sig')
    # Conservative address qualifier matching creates leads for previously unmatched communities.
    extended = []
    for _, c in coverage[coverage.poi_candidate_n == 0].iterrows():
        names = c.transaction_names.split(';')
        seen = {}
        for name in names:
            for row in by_key.get(qualified_key(name), []):
                if name_key(row.Name_CHN) != name_key(name):
                    seen[row.POIID] = row
        for row in seen.values():
            extended.append({'community_id': c.community_id, 'transaction_names': c.transaction_names,
                             'clean_transaction_n': int(c.clean_transaction_n), 'candidate_POIID': row.POIID,
                             'candidate_name': row.Name_CHN, 'candidate_address': row.address_text,
                             'candidate_n': len(seen), 'match_rule': 'only_optional_nonphase_parentheses_ignored',
                             'identity_verified': False, 'coordinate_accepted': False})
    extended_df = pd.DataFrame(extended, columns=['community_id', 'transaction_names', 'clean_transaction_n',
                               'candidate_POIID', 'candidate_name', 'candidate_address', 'candidate_n', 'match_rule',
                               'identity_verified', 'coordinate_accepted'])
    extended_df.to_csv(OUT / '未匹配小区_地址限定名补充候选.csv', index=False, encoding='utf-8-sig')
    # Focal parent/child links are source attributes, not proof of all gates being usable.
    focal = poi[poi.Name_CHN.str.contains('畔山花园|景福|鹿丹|中海天钻|都市名园|海关草埔|置富|绿茵庭苑', regex=True)].copy()
    focal['gate_public_access_verified'] = False
    focal.to_csv(OUT / '重点项目住宅_主体与出入口关联.csv', index=False, encoding='utf-8-sig')
    sources = [{'status': 'not_fetched', 'reason': 'explicit --skip-official-fetch'}] if args.skip_official_fetch else [download('cuido_renewal_2021', 'https://www.szlh.gov.cn/lhczjdbsc/gkmlpt/content/8/8739/post_8739732.html',
                        '翠都花园翠竹路地址及裙楼商业物业更新；不能推定整个住宅已拆')]
    source_text = OUT / 'official_sources/cuido_renewal_2021.txt'
    if sources[0]['status'] == 'archived':
        text = ''.join(source_text.read_text(encoding='utf-8').split())
        assert '翠都花园' in text and '人民医院周边片区城市更新' in text and '翠竹路' in text
    (OUT / '官方地址与同期更新来源.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding='utf-8')
    ambiguous_exact = pd.DataFrame(summaries).query('related_core_candidates_n > 1')
    summary = {'source_candidate_n': len(poi), 'previous_exact_matches_n': len(links), 'outliers_n': len(outliers),
               'outliers_with_multiple_related_candidates_n': len(ambiguous_exact),
               'additional_unmatched_community_leads_n': int(extended_df.community_id.nunique()),
               'additional_qualified_name_links_n': len(extended_df), 'focal_poi_n': len(focal),
               'official_sources_archived_n': sum(r['status'] == 'archived' for r in sources),
               'recorded_housing_identity_accepted_n': 0, 'production_coordinate_changed': False,
               'project_distance_computed': False, 'price_models_run': False,
               'coordinate_hypothesis_note': 'BD09 transaction / GCJ02 POI; diagnostic only',
               'input_hashes': input_hashes}
    summary['coordinate_registry_origin'] = registry_origin
    assert all(sha(Path(path)) == checksum for path, checksum in input_hashes.items())
    (OUT / '核验摘要.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    lines = ['# 罗湖住宅POI身份与异常排查', '',
             '同名唯一指严格名称下只有一个候选，并不保证房屋身份唯一。省略地址、分期或院区可能隐藏其他候选。本轮列出18组偏差超过100米的相关主体候选，保持原匹配，未按最近点替换。',
             f'其中{len(ambiguous_exact)}个小区有多个相关名称候选。两份源点按BD09/GCJ02解释后的距离仅作排查，不作为住宅到项目距离，也不证明最近点是真实身份。',
             f'对原303个未匹配小区，仅忽略可选且不含分期、院区、栋座等身份要素的末尾括号，补出{extended_df.community_id.nunique()}个小区的{len(extended_df)}条候选。所有新线索仍未验收。',
             '重点项目主体、门点和BELID原关系另表保存。门点可能是停车或内部通道，未取得公众准入依据前不能直接算步行服务可达性。',
             ('官方来源已取回，本地原文核查仅用于解释同期更新线索，不认证住宅身份。' if sources[0]['status'] == 'archived' else '本轮未取回官方来源；历史通告线索需另行核验，未将其算作本轮已归档证据。'),
             '原始ZIP、CSV和上轮POI图层保持不变，未新增交易或运行价格模型。后续逐候选核对地址、院区、用途与独立位置，不把近距离筛选当身份确认。']
    (OUT / '本轮结论与待核事项.md').write_text('\n\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
