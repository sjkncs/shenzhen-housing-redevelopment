"""List all nearby footprints under coordinate hypotheses; never select a building."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point


def nearby(footprints, point, radius=50):
    candidates = footprints.iloc[footprints.sindex.query(point.buffer(radius), predicate='intersects')].copy()
    candidates['hypothesis_distance_m'] = candidates.geometry.distance(point)
    candidates = candidates[candidates.hypothesis_distance_m.le(radius)]
    candidates['covers_point'] = candidates.geometry.covers(point)
    return candidates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--transactions', type=Path, required=True)
    parser.add_argument('--footprints', type=Path, required=True)
    parser.add_argument('--leads', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    root = Path(__file__).resolve().parents[1]
    implementation = root / 'data/supplied_gdata_intake/20261011/building_rar/coordinate_hypotheses/implementation.py'
    assert hashlib.sha256(implementation.read_bytes()).hexdigest() == '9fa83f46294f9e5616942d8cfec74825f2ecf4b6716418bc7d0208f46c6aa84f'
    spec = importlib.util.spec_from_file_location('pinned_math', implementation)
    math = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(math)
    source_sha = hashlib.sha256(args.transactions.read_bytes()).hexdigest()
    assert source_sha == 'b56310294f8b0288eba66c9852353c0339d4e9ba10fc0dadbcfa17ffad63bd22'
    raw = pd.read_csv(args.transactions, usecols=['小区详情url', '小区经度(百度)', '小区纬度(百度)'], low_memory=False)
    raw['cid'] = raw['小区详情url'].str.extract(r'(\d+)/?$', expand=False)
    leads = pd.read_csv(args.leads, dtype={'community_id': str})
    assert leads.community_id.is_unique
    buildings = gpd.read_file(args.footprints)
    assert buildings.crs.to_epsg() == 4326 and buildings.candidate_id.is_unique
    assert buildings.geometry.is_valid.all()
    projected = buildings.to_crs(4547)
    transform = Transformer.from_crs(4326, 4547, always_xy=True)
    pairs, rows = [], []
    for lead in leads.itertuples():
        coordinates = raw.loc[raw.cid.eq(lead.community_id), ['小区经度(百度)', '小区纬度(百度)']].drop_duplicates()
        for index, (lon, lat) in enumerate(coordinates.itertuples(index=False, name=None)):
            if pd.isna(lon) or pd.isna(lat):
                rows.append({'community_id': lead.community_id, 'name': lead.transaction_names,
                             'coordinate_pair_index': index, 'hypothesis': 'missing_coordinates',
                             'raw_coordinate_pair_n': len(coordinates), 'nearby_50m_n': None,
                             'covering_footprints_n': None, 'building_selected': False})
                continue
            gc_lat, gc_lon = math.gcj2wgs_exact(lat, lon)
            bd_lat, bd_lon = math.gcj2wgs_exact(*math.bd2gcj(lat, lon))
            for hypothesis, x, y in [('raw_as_wgs84', lon, lat), ('raw_as_gcj02', gc_lon, gc_lat),
                                     ('raw_as_bd09', bd_lon, bd_lat)]:
                point = Point(*transform.transform(x, y))
                candidates = nearby(projected, point)
                rows.append({'community_id': lead.community_id, 'name': lead.transaction_names,
                             'coordinate_pair_index': index, 'hypothesis': hypothesis,
                             'raw_coordinate_pair_n': len(coordinates), 'nearby_50m_n': len(candidates),
                             'covering_footprints_n': int(candidates.covers_point.sum()), 'building_selected': False})
                for candidate in candidates.itertuples():
                    pairs.append({'community_id': lead.community_id, 'coordinate_pair_index': index,
                                  'hypothesis': hypothesis, 'footprint_candidate_id': candidate.candidate_id,
                                  'source_reported_floor': candidate.Floor,
                                  'hypothesis_distance_m': candidate.hypothesis_distance_m,
                                  'covers_point': candidate.covers_point, 'identity_verified': False})
    table = pd.DataFrame(rows)
    args.output.mkdir(parents=True)
    table.to_csv(args.output / 'coordinate_hypothesis_footprint_support.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(pairs, columns=['community_id', 'coordinate_pair_index', 'hypothesis', 'footprint_candidate_id',
                                'source_reported_floor', 'hypothesis_distance_m', 'covers_point', 'identity_verified']).to_csv(
        args.output / 'all_50m_footprint_candidates.csv', index=False, encoding='utf-8-sig')
    summary = {'scope': 'HYPOTHETICAL_POINT_FOOTPRINT_RELATION_NOT_BUILDING_IDENTITY',
               'community_n': len(leads), 'diagnostic_rows': len(rows), 'candidate_pair_rows': len(pairs),
               'hypothesis_stats': table.groupby('hypothesis').agg(
                   diagnostic_points=('community_id', 'size'),
                   points_with_covering_polygon=('covering_footprints_n', lambda s: int(s.gt(0).sum())),
                   points_with_50m_candidates=('nearby_50m_n', lambda s: int(s.gt(0).sum()))).reset_index().to_dict('records'),
               'building_source_assumed_wgs84_for_diagnostic_only': True,
               'accepted_coordinate_frame': False, 'accepted_building_identity_n': 0,
               'project_distance_computed': False,
               'input_sha256': {key: hashlib.sha256(getattr(args, key).read_bytes()).hexdigest()
                                for key in ['transactions', 'footprints', 'leads']}}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
