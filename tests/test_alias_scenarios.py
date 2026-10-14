import importlib.util
from pathlib import Path
import unittest
import pandas as pd

spec = importlib.util.spec_from_file_location('alias', Path(__file__).resolve().parents[1] / 'scopes/shenzhen/scripts/reconcile_district_alias_scenarios.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AliasTests(unittest.TestCase):
    def test_additive_records_can_match_without_acceptance(self):
        data = pd.DataFrame({'ZONE': ['全市', '罗湖', '罗湖区', '福田'],
                             'normalized_zone': ['全市', '罗湖', '罗湖', '福田'],
                             'CJ_NUM': [6, 2, 1, 3], 'CJ_AREA': [600, 200, 100, 300]})
        rows = module.compare_group(data)
        self.assertFalse(rows[0]['matches_city_total'])
        self.assertFalse(rows[1]['matches_city_total'])
        self.assertTrue(rows[2]['matches_city_total'])
        self.assertTrue(all(not r['scenario_accepted'] for r in rows))

    def test_city_missing_is_rejected(self):
        data = pd.DataFrame({'ZONE': ['罗湖'], 'normalized_zone': ['罗湖'], 'CJ_NUM': [2], 'CJ_AREA': [200]})
        with self.assertRaises(ValueError):
            module.compare_group(data)
