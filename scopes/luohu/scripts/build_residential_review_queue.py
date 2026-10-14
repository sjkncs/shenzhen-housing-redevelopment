"""Join archived evidence into a pending manual review queue; never accept buildings."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def read_rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def unique(rows):
    result = {}
    for row in rows:
        key = row['community_id']
        if key in result:
            raise ValueError('Duplicate community: ' + key)
        result[key] = row
    return result


def build_queue(leads, baseline, support, addresses, atlas):
    base, official, images = unique(baseline), unique(addresses), unique(atlas)
    lead_map = unique(leads)
    if set(base) != set(lead_map) or set(images) != set(lead_map):
        raise ValueError('Baseline and atlas must cover exactly the lead communities')
    if not set(official).issubset(lead_map):
        raise ValueError('Official evidence contains an unknown community')
    hypotheses = ('raw_as_wgs84', 'raw_as_gcj02', 'raw_as_bd09')
    grouped = {}
    for row in support:
        key = (row['community_id'], row['hypothesis'])
        if key in grouped or row['coordinate_pair_index'] != '0':
            raise ValueError('This queue requires one coordinate pair per community')
        if row['building_selected'].lower() != 'false':
            raise ValueError('Accepted building must not enter a pending queue')
        grouped[key] = row
    if set(grouped) != {(cid, h) for cid in lead_map for h in hypotheses}:
        raise ValueError('Missing or extra coordinate hypothesis')
    rows = []
    for cid, lead in lead_map.items():
        b, a, im = base[cid], official.get(cid, {}), images[cid]
        if im['identity_accepted'].lower() != 'false':
            raise ValueError('Atlas identity is already accepted')
        if int(im['window_transactions']) != int(lead['window_transaction_n']):
            raise ValueError('Atlas transaction count differs from leads')
        checks = ['确认住宅主体与门牌及楼栋对应', '确认数据坐标口径并独立核对位置', '核对木头龙红线后计算距离']
        if b['reported_years_conflict'].lower() == 'true':
            checks.insert(0, '核对平台建成年代冲突，不凭名称拆分楼栋')
        if b['baseline_evidence'] != 'platform_transaction_observed_before_2020':
            checks.insert(0, '补充事件前已存在的住宅证据')
        if lead['both_periods_observed'].lower() != 'true':
            checks.append('补查前后成交支持，缺记录不作零成交')
        row = {'community_id': cid, 'name': im['name'],
               'window_transaction_n': lead['window_transaction_n'],
               'pre_transaction_n': lead['pre_transaction_n'],
               'post_transaction_n': lead['post_transaction_n'],
               'reported_construction_years': b['reported_construction_years'],
               'reported_years_conflict': b['reported_years_conflict'],
               'baseline_evidence': b['baseline_evidence'],
               'official_address_corroborated': a.get('official_address_corroborated', 'False'),
               'official_address': a.get('address_to_check', ''),
               'official_source_url': a.get('source_url', ''),
               'atlas_image': '../footprint_review_atlas_final_20261014/' + im['image'],
               'atlas_sha256': im['sha256']}
        for h in hypotheses:
            s = grouped[cid, h]
            row[h + '_nearby_50m_n'] = s['nearby_50m_n']
            row[h + '_covering_n'] = s['covering_footprints_n']
        row.update(review_status='pending', accepted_building_id='',
                   residential_identity_verified=False, coordinate_verified=False,
                   project_treatment_assigned=False, next_checks_zh='；'.join(checks))
        rows.append(row)
    rows.sort(key=lambda r: (-int(r['window_transaction_n']), r['community_id']))
    for rank, row in enumerate(rows, 1):
        row['review_order'] = rank
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('leads', 'baseline', 'support', 'addresses', 'atlas', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    inputs = {name: getattr(args, name) for name in ('leads', 'baseline', 'support', 'addresses', 'atlas')}
    rows = build_queue(**{k: read_rows(p) for k, p in inputs.items()})
    for im in read_rows(args.atlas):
        digest = hashlib.sha256((args.atlas.parent / im['image']).read_bytes()).hexdigest()
        if digest != im['sha256']:
            raise ValueError('Atlas image hash mismatch: ' + im['image'])
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / 'residential_review_queue.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {'community_n': len(rows), 'window_transactions': sum(int(r['window_transaction_n']) for r in rows),
               'official_address_corroborated_n': sum(r['official_address_corroborated'].lower() == 'true' for r in rows),
               'reported_year_conflict_n': sum(r['reported_years_conflict'].lower() == 'true' for r in rows),
               'accepted_building_n': 0, 'coordinate_verified_n': 0, 'project_treatment_assigned_n': 0,
               'source_sha256': {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in inputs.items()}}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 罗湖住宅线索逐小区核查清单', '',
             '本表连接已有地址、基期证据和三坐标假设图册，没有新增独立地理验证。', '',
             '查看顺序按2017—2023年成交笔数降序排列，仅用于分配人工核查工作；不是样本纳入标准。全部小区保留，所有住宅身份、坐标及项目处理状态仍待确认。', '',
             '官方地址旁证可能指向裙楼或公共服务机构，不能直接确认住宅楼栋。三种坐标假设一视同仁，附近或覆盖点的轮廓均不自动接受。', '',
             '|顺序|小区|成交笔数|官方地址旁证|下一步核查|', '|---|---|---:|---|---|']
    for r in rows:
        evidence = '[原页](' + r['official_source_url'] + ')' if r['official_source_url'] else '尚缺'
        lines.append(f"|{r['review_order']}|[{r['name']}]({r['atlas_image']})|{r['window_transaction_n']}|{evidence}|{r['next_checks_zh']}|")
    lines += ['', '## 复现', '',
              '脚本：`scopes/luohu/scripts/build_residential_review_queue.py`。必须显式提供五份输入和一个尚不存在的输出目录；摘要记录输入SHA-256，运行时核对全部图像哈希。', '',
              '输入参数：`--leads`道路线索成交支持，`--baseline`基期及年代证据，`--support`三坐标假设计数，`--addresses`官方地址旁证，`--atlas`图册索引，`--output`新目录。', '',
              '输出CSV每行一个小区。`review_status=pending`，`accepted_building_id`留空；未取得新证据前不可填写为已确认。零覆盖仅指当前坐标假设与供应轮廓，不表示住宅不存在。']
    (args.output / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
