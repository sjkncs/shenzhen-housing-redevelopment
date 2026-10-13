import importlib.util
from pathlib import Path
import unittest
import pandas as pd

spec = importlib.util.spec_from_file_location('collisions', Path(__file__).resolve().parents[1] / 'scopes/shenzhen/scripts/classify_district_collisions.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CollisionTests(unittest.TestCase):
    def test_equal_values_do_not_imply_accepted_version(self):
        group = pd.DataFrame({'CJ_NUM': [2, 2], 'CJ_AREA': [100., 100.]})
        self.assertEqual(module.classify_group(group), '套数面积数值相同但来源记录不同')

    def test_area_conflict(self):
        group = pd.DataFrame({'CJ_NUM': [2, 2], 'CJ_AREA': [100., 101.]})
        self.assertEqual(module.classify_group(group), '套数相同面积不同')

    def test_both_conflict(self):
        group = pd.DataFrame({'CJ_NUM': [2, 3], 'CJ_AREA': [100., 101.]})
        self.assertEqual(module.classify_group(group), '套数和面积均不同')
