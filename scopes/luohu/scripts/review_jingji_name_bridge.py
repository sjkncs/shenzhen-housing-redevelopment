"""Record the Jingji name/address bridge without assigning dwellings or coordinates."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from bs4 import BeautifulSoup
import fitz
import pandas as pd

CID = '2411048934069'
RAW_HASH = 'b56310294f8b0288eba66c9852353c0339d4e9ba10fc0dadbcfa17ffad63bd22'
ROSTER_HASH = '3f4f2146590f69bdbb92d22742606f0b7a64384ba7d7666c0877a79ec3b2a918'
FULL_URL = 'https://www.szlh.gov.cn/lhjyjdds/gkmlpt/content/11/11008/post_11008298.html'
SHORT_URL = 'https://www.szlh.gov.cn/zwgk/ssjygkzl/content/post_9931859.html'
ROSTER_URL = 'https://www.sz.gov.cn/attachment/0/749/749839/8545776.pdf'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def address_records(path, tokens):
    soup = BeautifulSoup(path.read_bytes(), 'html.parser')
    matches = []
    for element in soup.find_all(['p', 'tr']):
        text = ''.join(element.get_text().split())
        if all(token in text for token in tokens):
            matches.append(text)
    if not matches:
        raise ValueError('No single paragraph/table row contains all address tokens')
    return matches


def source_subset(raw):
    selected = raw.loc[raw['小区详情url'].eq('https://sz.ke.com/xiaoqu/' + CID)].copy()
    if selected.empty or not selected['小区名称'].eq('京基东方华都').all():
        raise ValueError('Unexpected source ID/name mapping')
    if selected['成交详情页url'].isna().any() or selected['成交详情页url'].duplicated().any():
        raise ValueError('Missing or duplicate transaction URLs')
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('transactions', 'roster', 'full', 'short', 'composition', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    if digest(args.transactions) != RAW_HASH or digest(args.roster) != ROSTER_HASH:
        raise ValueError('Pinned source hash mismatch')
    address_records(args.full, ['京基东方华都大厦', '文锦中路2063号', '裙楼'])
    address_records(args.short, ['东方华都', '文锦中路2063号', '东门街道', '地下室'])
    with fitz.open(args.roster) as document:
        entries = [(i + 1, cells) for i, page in enumerate(document)
                   if '东方华都大厦' in page.get_text()
                   for table in page.find_tables().tables for cells in table.extract()
                   if len(cells) == 5 and cells[3] == '东方华都大厦' and cells[1] == '罗湖']
    if len(entries) != 1 or entries[0][1][0] != '291':
        raise ValueError('Official roster entry changed or ambiguous')
    raw = pd.read_csv(args.transactions, dtype=str, usecols=[
        '小区详情url', '小区名称', '成交详情页url', '区县', '区域商圈', '房屋用途',
        '建筑类型', '建成年代', '成交时间'], low_memory=False)
    selected = source_subset(raw)
    dates = pd.to_datetime(selected['成交时间'], errors='raise')
    composition = pd.read_csv(args.composition, dtype={'community': str})
    composition = composition.loc[composition.community.eq(CID)].copy()
    if set(composition.period) != {'pre', 'transition', 'post'} or composition.period.duplicated().any():
        raise ValueError('Composition must contain three unique periods')
    counts = dict(zip(composition.period, composition.transactions.astype(int)))
    if counts != {'pre': 76, 'transition': 7, 'post': 35}:
        raise ValueError('Archived period counts differ from documented review')
    fields = []
    for column in ['区县', '区域商圈', '房屋用途', '建筑类型', '建成年代']:
        for value, count in selected[column].fillna('missing').value_counts().items():
            fields.append({'community_id': CID, 'source_field': column, 'source_value': value,
                           'raw_transaction_n': int(count), 'is_official_identity': False})
    evidence = [
        {'source_id': 'official_roster', 'url': ROSTER_URL, 'sha256': ROSTER_HASH,
         'name': '东方华都大厦', 'address_scope': '名录不含门牌', 'street_reported': '东门',
         'record_locator': 'PDF第7页，序号291', 'supports': '官方住宅参考价格名录名称旁证'},
        {'source_id': 'full_name_address', 'url': FULL_URL, 'sha256': digest(args.full),
         'name': '京基东方华都大厦', 'address_scope': '文锦中路2063号，裙楼三层', 'street_reported': '未明确',
         'record_locator': '2023-11-28设立公告的办学地址段', 'supports': '带京基名称与门牌的机构地址关联'},
        {'source_id': 'short_name_address', 'url': SHORT_URL, 'sha256': digest(args.short),
         'name': '东方华都', 'address_scope': '文锦中路2063号，负一层地下室', 'street_reported': '东门',
         'record_locator': '2022-07-05物业检查页，同一表格行', 'supports': '不带京基名称与门牌的物业机构地址关联'},
    ]
    args.output.mkdir(parents=True)
    for name, rows in [('jingji_name_bridge_evidence.csv', evidence), ('jingji_source_field_counts.csv', fields)]:
        with (args.output / name).open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    composition.to_csv(args.output / 'jingji_existing_period_composition.csv', index=False, encoding='utf-8-sig')
    summary = {'community_id': CID, 'platform_name': '京基东方华都', 'official_roster_name': '东方华都大厦',
               'name_relation_status': 'same_doorplate_corroboration_not_building_identity',
               'raw_record_n': len(selected), 'raw_first_date': dates.min().date().isoformat(),
               'raw_last_date': dates.max().date().isoformat(),
               'existing_clean_window_n': int(composition.transactions.sum()),
               'existing_period_counts': dict(zip(composition.period, composition.transactions.astype(int))),
               'residential_building_identity_verified': False, 'coordinate_verified': False,
               'official_street_conflict_resolved': False, 'project_treatment_assigned': False,
               'exact_name_roster_matches_unchanged': True, 'raw_pages_publicly_republished': False,
               'source_sha256': {k: digest(getattr(args, k)) for k in ['transactions', 'roster', 'full', 'short', 'composition']}}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 京基东方华都名称与住宅记录核查', '',
             '## 本轮证据', '',
             '平台称“京基东方华都”；官方住宅小区参考价表第7页、序号291称“东方华都大厦”，街道记为东门。教育设立公告以“京基东方华都大厦”关联文锦中路2063号裙楼；物业检查页以“东方华都”关联同门牌地下室。', '',
             '**判断：同门牌的名称关联旁证成立，逐套住宅与具体楼栋对应关系仍待核定。** 官方名录没有门牌；本轮没有建立无歧义的官方物业编号链。因此保留上一轮14个完全同名结果，不将名称关联计入第15个精确匹配。', '',
             '## 平台数据与现有窗口', '',
             f"封存原文件按小区ID筛出{len(selected)}条，日期{summary['raw_first_date']}至{summary['raw_last_date']}。全部记录的用途均以平台原字段为准，不升级为官方用途认定。字段频数见CSV。", '',
             f"既有清洗窗口为{summary['existing_clean_window_n']}笔，前段76、过渡季度7、后段35。直接引用既有构成表，未重估因果效应。原149条与窗口118笔的时间范围和筛选条件不同，不能混用。", '',
             '原文件建成年代2005年148条、2006年1条。没有楼栋编号证据，不能据此将交易拆成不同楼栋或分期。', '',
             '## 行政归属与后续', '',
             '平台商圈原字段为螺岭，不能当作街道。名录和物业页记东门；既有2021年卫生检查机构地址记翠竹。保留原文差异，不按多数票或商圈强改行政归属，也不以裙楼经营、泳池或地下室记录认定整栋商业或住宅用途。', '',
             '接下来需取得可对应住宅主体的官方物业/楼栋编号、独立地理位置或宗地资料，再检验与平台小区ID的连接；当前不指定建筑轮廓、不计算项目边界距离、不分配处理组。', '',
             '## 来源与运行', '']
    lines += ['[' + r['source_id'] + '](' + r['url'] + ')：' + r['record_locator'] for r in evidence]
    lines += ['', '[既有2021年地址记录](https://www.szlh.gov.cn/zwfw/yljk/tzgg/content/post_10111558.html)仅用于说明未解决的街道差异。', '',
              '脚本`scopes/luohu/scripts/review_jingji_name_bridge.py`：`--transactions`封存原成交CSV，`--roster`官方参考价原PDF，`--full`教育公告HTML，`--short`物业检查HTML，`--composition`既有时期构成CSV，`--output`新目录。', '',
              '依赖pandas、BeautifulSoup、PyMuPDF。校验原成交及名录哈希；要求门牌和名称出现在同一段或表格行；原网页保留本地，公开证据表只提供来源、定位和哈希。']
    (args.output / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
