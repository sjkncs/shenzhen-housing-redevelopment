"""Render unverified point/footprint hypotheses for manual review, not attribution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--transactions', type=Path, required=True)
    parser.add_argument('--footprints', type=Path, required=True)
    parser.add_argument('--leads', type=Path, required=True)
    parser.add_argument('--support', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Select a new atlas output directory')
    root = Path(__file__).resolve().parents[1]
    implementation = root / 'data/supplied_gdata_intake/20261011/building_rar/coordinate_hypotheses/implementation.py'
    assert hashlib.sha256(implementation.read_bytes()).hexdigest() == '9fa83f46294f9e5616942d8cfec74825f2ecf4b6716418bc7d0208f46c6aa84f'
    spec = importlib.util.spec_from_file_location('pinned_math', implementation)
    math = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(math)
    assert hashlib.sha256(args.transactions.read_bytes()).hexdigest() == 'b56310294f8b0288eba66c9852353c0339d4e9ba10fc0dadbcfa17ffad63bd22'
    raw = pd.read_csv(args.transactions, usecols=['小区详情url', '小区经度(百度)', '小区纬度(百度)'], low_memory=False)
    raw['cid'] = raw['小区详情url'].str.extract(r'(\d+)/?$', expand=False)
    footprints = gpd.read_file(args.footprints).to_crs(4547)
    assert footprints.candidate_id.is_unique and footprints.geometry.is_valid.all()
    support = pd.read_csv(args.support, dtype={'community_id': str})
    leads = pd.read_csv(args.leads, dtype={'community_id': str}).sort_values('window_transaction_n', ascending=False)
    transform = Transformer.from_crs(4326, 4547, always_xy=True)
    args.output.mkdir(parents=True)
    index = []
    for lead in leads.itertuples():
        values = raw.loc[raw.cid.eq(lead.community_id), ['小区经度(百度)', '小区纬度(百度)']].drop_duplicates()
        for pair_index, (lon, lat) in enumerate(values.itertuples(index=False, name=None)):
            if pd.isna(lon) or pd.isna(lat):
                continue
            gc_lat, gc_lon = math.gcj2wgs_exact(lat, lon)
            bd_lat, bd_lon = math.gcj2wgs_exact(*math.bd2gcj(lat, lon))
            fig, axes = plt.subplots(1, 3, figsize=(15, 6.5))
            for ax, (label, x, y) in zip(axes, [('raw_as_wgs84', lon, lat), ('raw_as_gcj02', gc_lon, gc_lat), ('raw_as_bd09', bd_lon, bd_lat)]):
                point = Point(*transform.transform(x, y))
                nearby = footprints.iloc[footprints.sindex.query(point.buffer(90), predicate='intersects')].copy()
                if len(nearby):
                    nearby.plot(ax=ax, facecolor='#edf1f3', edgecolor='#77838a', linewidth=.7)
                    distance = nearby.geometry.distance(point)
                    candidates = nearby[distance.le(50)].copy()
                    if len(candidates):
                        candidates.plot(ax=ax, facecolor='#d8eaf4', edgecolor='#176c9a', linewidth=.9)
                    for building in candidates.itertuples():
                        location = building.geometry.representative_point()
                        ax.annotate(str(building.source_row_ordinal), (location.x, location.y),
                                    fontsize=6, ha='center', color='#25343a')
                else:
                    candidates = nearby
                expected = support[(support.community_id.eq(lead.community_id)) &
                                   support.coordinate_pair_index.eq(pair_index) & support.hypothesis.eq(label)]
                assert len(expected) == 1 and int(expected.nearby_50m_n.iloc[0]) == len(candidates)
                assert int(expected.covering_footprints_n.iloc[0]) == int(candidates.geometry.covers(point).sum())
                ax.add_patch(plt.Circle((point.x, point.y), 50, fill=False, color='#ad7630', linestyle='--', linewidth=.8))
                ax.scatter([point.x], [point.y], marker='+', s=100, color='#b1373e', zorder=5)
                ax.set(xlim=(point.x - 90, point.x + 90), ylim=(point.y - 90, point.y + 90), aspect='equal',
                       title=label + '\n50m candidates: ' + str(len(candidates)))
                ax.ticklabel_format(style='plain', useOffset=False)
                ax.tick_params(labelsize=7, axis='x', labelrotation=25)
                ax.set_xlabel('Declared-frame easting (diagnostic only)', fontsize=8)
            fig.suptitle('Community ' + lead.community_id + ' | transactions: ' + str(lead.window_transaction_n)
                         + '\nUNVERIFIED coordinate hypotheses / no building selected', fontsize=12)
            fig.text(.5, .035, 'Each panel has its own hypothesis center, not the same geographic position.\n'
                     'Labels = source-row ordinals; blue = within 50m. No imagery or project redline.',
                     ha='center', fontsize=9)
            fig.subplots_adjust(left=.065, right=.99, bottom=.24, top=.77, wspace=.28)
            filename = 'review_' + lead.community_id + '_' + str(pair_index) + '.png'
            fig.savefig(args.output / filename, dpi=150)
            plt.close(fig)
            index.append({'community_id': lead.community_id, 'name': lead.transaction_names,
                          'coordinate_pair_index': pair_index, 'window_transactions': lead.window_transaction_n,
                          'image': filename, 'sha256': hashlib.sha256((args.output / filename).read_bytes()).hexdigest(),
                          'identity_accepted': False})
    pd.DataFrame(index).to_csv(args.output / 'review_atlas_index.csv', index=False, encoding='utf-8-sig')
    lines = ['# 住宅定位人工审查图册', '',
             '三种假设各以自己的候选点居中，范围均为180×180声明投影单位。不同面板不是同一地理位置，不能凭面板形状作直接重叠比较。', '',
             '红十字为假设点，虚线为50米诊断半径，蓝色为全部半径内建筑，标注数字为原建筑行序号（对应LUOHU_SRC_编号），不是楼栋名称。', '',
             '建筑源仅按声明WGS84解释；没有卫星影像、官方地址落点或木头龙红线。不能凭蓝色轮廓、落点或最近距离接受真实住宅身份。', '',
             '按窗口成交数排序，优先审查数据影响较大的候选。索引和每张图哈希见review_atlas_index.csv。面板候选数量已逐个与此前60条诊断记录核对一致。', '']
    for item in index:
        lines += ['## ' + item['name'] + '（' + str(item['window_transactions']) + '笔）', '',
                  '![' + item['name'] + '](' + item['image'] + ')', '']
    (args.output / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'rendered_images': len(index), 'panel_counts_match_previous_audit': True, 'selected_buildings': 0}))


if __name__ == '__main__':
    main()
