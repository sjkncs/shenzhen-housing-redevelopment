"""Select source footprints against a supplied district boundary; no CRS acceptance."""
import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


def fingerprints(shapefile):
    result = {}
    for extension in ['.shp', '.shx', '.dbf', '.prj']:
        path = shapefile.with_suffix(extension)
        if not path.is_file():
            raise FileNotFoundError(path)
        result[extension] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--buildings', type=Path, required=True)
    parser.add_argument('--districts', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve earlier extraction; select a new output')
    inputs = {key: fingerprints(getattr(args, key)) for key in ['buildings', 'districts']}
    buildings = gpd.read_file(args.buildings)
    districts = gpd.read_file(args.districts)
    if buildings.crs is None or districts.crs is None:
        raise ValueError('Declared CRS missing; do not guess')
    boundary = districts[districts.sname.eq('罗湖区')]
    if len(boundary) != 1 or not boundary.geometry.is_valid.all():
        raise ValueError('Expected one valid Luohu boundary')
    boundary = boundary.to_crs(buildings.crs)
    polygon = boundary.geometry.iloc[0]
    valid = buildings.geometry.notna() & ~buildings.geometry.is_empty & buildings.geometry.is_valid
    # Invalid geometries remain in the source. Never repair or silently intersect them.
    eligible = buildings.loc[valid].copy()
    candidates = eligible[eligible.geometry.intersects(polygon)].copy()
    candidates['source_row_ordinal'] = candidates.index.astype(int)
    candidates['candidate_id'] = ['LUOHU_SRC_' + str(i) for i in candidates.source_row_ordinal]
    candidates['boundary_relation'] = candidates.geometry.map(lambda geom: 'fully_within' if polygon.covers(geom) else 'crosses_or_touches')
    candidates['position_verified'] = False
    candidates['residential_use_verified'] = False
    candidates['survey_date_verified'] = False
    candidates['project_exposure_assigned'] = False
    invalid = buildings.loc[~valid]
    bounds = polygon.bounds
    invalid_bbox = invalid.cx[bounds[0]:bounds[2], bounds[1]:bounds[3]]
    args.output.mkdir(parents=True)
    candidates.to_file(args.output / 'luohu_building_candidates.gpkg', layer='declared_crs_candidates', driver='GPKG')
    attrs = candidates.drop(columns='geometry')
    attrs.to_csv(args.output / 'building_candidate_attributes.csv', index=False, encoding='utf-8-sig')
    pd.to_numeric(candidates.Floor, errors='coerce').value_counts(dropna=False).rename_axis('source_reported_floor').reset_index(name='candidate_n').to_csv(
        args.output / 'reported_floor_counts.csv', index=False, encoding='utf-8-sig')
    report = {'scope': 'SUPPLIED_BOUNDARY_DECLARED_CRS_BUILDING_CANDIDATES_NOT_VERIFIED_RESIDENTIAL_DATASET',
              'building_source_n': len(buildings), 'source_invalid_or_empty_n': int((~valid).sum()),
              'invalid_source_bbox_candidates_n': len(invalid_bbox),
              'candidate_n': len(candidates), 'fully_within_n': int(candidates.boundary_relation.eq('fully_within').sum()),
              'crosses_or_touches_n': int(candidates.boundary_relation.eq('crosses_or_touches').sum()),
              'building_declared_crs': str(buildings.crs), 'boundary_declared_crs': str(districts.crs),
              'source_id_unique_within_candidates': bool(candidates.Id.is_unique),
              'input_component_sha256': inputs, 'accepted_coordinate_frame': False,
              'collection_date_verified': False, 'historical_baseline_verified': False,
              'residential_building_n_verified': None, 'transaction_join_performed': False}
    (args.output / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for key in inputs:
        assert fingerprints(getattr(args, key)) == inputs[key]
    reread = gpd.read_file(args.output / 'luohu_building_candidates.gpkg')
    assert len(reread) == len(candidates) and reread.candidate_id.is_unique and reread.geometry.is_valid.all()
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
