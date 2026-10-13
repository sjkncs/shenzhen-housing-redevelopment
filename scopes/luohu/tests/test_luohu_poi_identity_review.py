import importlib.util
from pathlib import Path
import unittest
import tempfile
import json
import pandas as pd

path = Path(__file__).resolve().parents[1] / 'scripts/review_luohu_poi_ambiguity_20261012.py'
spec = importlib.util.spec_from_file_location('identity_review', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IdentityQualifierTests(unittest.TestCase):
    def test_raw_registry_preserves_multiple_and_missing_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.csv'
            pd.DataFrame({'小区详情url': ['https://x/123/', 'https://x/123/', 'https://x/123/'],
                          '小区经度(百度)': [114.1, 114.2, None],
                          '小区纬度(百度)': [22.5, 22.5, 22.5]}).to_csv(path, index=False)
            registry = module.registry_from_transactions(path, {'123'})
            pairs = json.loads(registry.loc['123', '原始百度标签坐标对集合'])
            self.assertEqual(len(pairs), 3)
            self.assertEqual(pairs[-1], [None, 22.5])

    def test_missing_required_community_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.csv'
            pd.DataFrame({'小区详情url': ['https://x/123/'], '小区经度(百度)': [114.1],
                          '小区纬度(百度)': [22.5]}).to_csv(path, index=False)
            with self.assertRaises(ValueError):
                module.registry_from_transactions(path, {'123', '999'})

    def test_address_qualifier_creates_a_lead(self):
        self.assertEqual(module.qualified_key('置富公寓（文锦北路）'), '置富公寓')

    def test_phase_is_not_dropped(self):
        self.assertNotEqual(module.qualified_key('景福花园(二期)'), '景福花园')

    def test_yard_number_is_not_dropped(self):
        self.assertNotEqual(module.qualified_key('海关宿舍(一院)'), '海关宿舍')

    def test_district_is_not_dropped(self):
        self.assertNotEqual(module.qualified_key('小区(东区)'), '小区')

    def test_building_unit_is_not_dropped(self):
        self.assertNotEqual(module.qualified_key('花园(3栋)'), '花园')

    def test_identical_name_stays_identical(self):
        self.assertEqual(module.qualified_key(' 畔山 花园 '), '畔山花园')


if __name__ == '__main__':
    unittest.main()
