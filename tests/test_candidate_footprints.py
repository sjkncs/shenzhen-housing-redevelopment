import importlib.util
from pathlib import Path
import unittest

import geopandas as gpd
from shapely.geometry import Point, box

spec = importlib.util.spec_from_file_location('footprints', Path(__file__).resolve().parents[1] / 'scopes/luohu/scripts/diagnose_candidate_footprints.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FootprintTests(unittest.TestCase):
    def test_all_covering_polygons_retained(self):
        data = gpd.GeoDataFrame({'geometry': [box(-1, -1, 1, 1), box(-2, -2, 2, 2)]}, crs=4547)
        result = module.nearby(data, Point(0, 0))
        self.assertEqual(len(result), 2)
        self.assertTrue(result.covers_point.all())

    def test_buffer_bbox_not_enough(self):
        data = gpd.GeoDataFrame({'geometry': [box(40, 40, 41, 41), box(20, 0, 21, 1)]}, crs=4547)
        self.assertEqual(len(module.nearby(data, Point(0, 0), 50)), 1)
