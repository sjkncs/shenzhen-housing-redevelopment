"""Audit exact Luohu names against a pinned official housing-reference PDF."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import fitz

ROSTER_URL = 'https://www.sz.gov.cn/attachment/0/749/749839/8545776.pdf'
ROSTER_HASH = '3f4f2146590f69bdbb92d22742606f0b7a64384ba7d7666c0877a79ec3b2a918'
ADDRESS_SOURCES = {
    'huandao': ('环岛丽园', '华丽路1099号', '丽来阁',
                'https://www.szlh.gov.cn/attachment/1/1306/1306081/10645642.pdf'),
    'yangguang': ('阳光绿地家园', '爱国路3003号', '1座2A',
                 'https://www.szlh.gov.cn/lhqwsjkj/attachment/1/1620/1620939/12354733.pdf'),
}


def compact(value):
    return ''.join((value or '').split())


def extract_roster(pdf):
    rows = []
    with fitz.open(pdf) as document:
        for number, page in enumerate(document, 1):
            for table in page.find_tables().tables:
                for cells in table.extract():
                    if len(cells) != 5 or not compact(cells[0]).isdigit():
                        continue
                    serial, district, street, name, price = map(compact, cells)
                    if not price.isdigit() or not district or not name:
                        raise ValueError('Malformed official table row: ' + str(cells))
                    rows.append({'official_serial': serial, 'district': district,
                                 'street': street, 'official_name': name,
                                 'reference_price_not_transaction': int(price), 'pdf_page': number})
    serials = [int(r['official_serial']) for r in rows]
    if not serials or serials != list(range(1, max(serials) + 1)):
        raise ValueError('Official roster is incomplete or duplicated')
    return rows


def match_names(queue, roster):
    result = []
    seen = set()
    for candidate in queue:
        cid = candidate['community_id']
        if cid in seen:
            raise ValueError('Duplicate candidate community')
        seen.add(cid)
        matches = [r for r in roster if r['district'] == '罗湖' and r['official_name'] == compact(candidate['name'])]
        if len(matches) > 1:
            raise ValueError('Ambiguous exact official name: ' + candidate['name'])
        official = matches[0] if matches else {}
        result.append({'community_id': cid, 'platform_name': candidate['name'],
                       'match_rule': 'exact_name_and_luohu' if matches else 'no_exact_match',
                       'official_roster_name_corroborated': bool(matches),
                       'official_name': official.get('official_name', ''),
                       'official_serial': official.get('official_serial', ''),
                       'official_street': official.get('street', ''),
                       'pdf_page': official.get('pdf_page', ''),
                       'source_url': ROSTER_URL, 'source_sha256': ROSTER_HASH,
                       'residential_building_identity_verified': False,
                       'coordinate_verified': False, 'project_treatment_assigned': False})
    return result


def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('roster', 'queue', 'huandao', 'yangguang', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    if hashlib.sha256(args.roster.read_bytes()).hexdigest() != ROSTER_HASH:
        raise ValueError('Official roster hash differs from archived source')
    with args.queue.open(encoding='utf-8-sig', newline='') as stream:
        queue = list(csv.DictReader(stream))
    roster = extract_roster(args.roster)
    matched = match_names(queue, roster)
    addresses = []
    for key, (name, address, label, url) in ADDRESS_SOURCES.items():
        path = getattr(args, key)
        with fitz.open(path) as document:
            # Require one address cell, so unrelated records cannot satisfy separate tokens.
            pages = [i + 1 for i, page in enumerate(document)
                     if any(all(token in compact(cell) for token in (name, address, label))
                            for table in page.find_tables().tables
                            for cells in table.extract() for cell in cells)]
        if not pages:
            raise ValueError('Expected address evidence absent: ' + key)
        cid = [r['community_id'] for r in queue if r['name'] == name]
        if len(cid) != 1:
            raise ValueError('Address cannot be linked to one candidate')
        addresses.append({'community_id': cid[0], 'candidate_name': name,
                          'address_to_check': address, 'building_label_lead': label,
                          'pdf_pages': '|'.join(map(str, pages)), 'source_url': url,
                          'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                          'source_bytes': path.stat().st_size, 'checked_on': '2026-10-14',
                          'evidence_scope': '公共场所检查机构地址，不认证住宅楼栋、竣工或历史用途',
                          'official_address_corroborated': True,
                          'residential_building_identity_verified': False,
                          'coordinate_verified': False, 'project_treatment_assigned': False})
    args.output.mkdir(parents=True)
    write_csv(args.output / 'official_roster_name_matches.csv', matched)
    write_csv(args.output / 'supplemental_address_evidence.csv', addresses)
    summary = {'checked_on': '2026-10-14', 'candidate_n': len(matched),
               'official_roster_row_n': len(roster),
               'luohu_roster_row_n': sum(r['district'] == '罗湖' for r in roster),
               'exact_name_matches_n': sum(r['official_roster_name_corroborated'] for r in matched),
               'unmatched_platform_names': [r['platform_name'] for r in matched if not r['official_roster_name_corroborated']],
               'supplemental_address_n': len(addresses), 'residential_building_verified_n': 0,
               'reference_prices_used_as_transactions': False,
               'roster_source_sha256': ROSTER_HASH,
               'queue_source_sha256': hashlib.sha256(args.queue.read_bytes()).hexdigest(),
               'raw_documents_publicly_republished': False,
               'roster_publication_date': 'not independently verified in this audit'}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 官方住宅小区名称与新增地址证据核查', '',
             '本轮使用政府门户《深圳市住宅小区二手住房成交参考价格表》原PDF核对20个候选。逐页结构化表格提取，并验证序号连续、不重复；仅接受罗湖行政区及完整名称完全一致，不猜测别名。', '',
             f"官方表共{len(roster)}条；20个候选中{summary['exact_name_matches_n']}个名称完全一致。未匹配不代表住宅不存在或属于非住宅，只表示当前表及规则未提供旁证。", '',
             '这是一份参考价格名录，不是逐套成交数据或当前价格。名录列名旁证、具体住宅楼栋身份、历史存在、坐标验证与项目归属必须分别处理；本轮不修改原核查清单的待确认状态。', '',
             '|平台名称|官方名录旁证|PDF页/序号|', '|---|---|---|']
    for r in matched:
        lines.append(f"|{r['platform_name']}|{r['official_name'] or '未找到完全同名条目'}|{str(r['pdf_page']) + '/' + str(r['official_serial']) if r['pdf_page'] else '—'}|")
    lines += ['', '## 新增门牌与楼栋线索', '',
              '环岛丽园：华丽路1099号、丽来阁；阳光绿地家园：爱国路3003号、1座2A。来源均为公共场所检查附件中的机构地址，不能自动确认整栋住宅用途。', '',
              '京基东方华都：已有官方旁证主要为裙楼机构地址；本轮没有按去掉“京基”等方式强配名录，也没有据此排除其住宅记录。', '',
              '## 来源和复现', '', '[官方参考价格表](' + ROSTER_URL + ')', '']
    lines += ['[' + r['candidate_name'] + '地址附件](' + r['source_url'] + ')：PDF第' + r['pdf_pages'] + '页；SHA-256见CSV。' for r in addresses]
    lines += ['', '脚本：`scopes/luohu/scripts/audit_official_residential_names.py`。参数`--roster`原名录PDF、`--queue`20小区清单、`--huandao`和`--yangguang`两份原地址PDF、`--output`新目录；依赖PyMuPDF。', '',
              '原PDF保留在本地，公开摘要保留下载地址和文件哈希。表的发布日未在本轮独立核实，不根据搜索摘要或附件编号填写。']
    (args.output / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
