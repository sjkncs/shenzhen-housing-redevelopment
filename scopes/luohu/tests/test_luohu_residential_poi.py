"""Small deterministic tests for candidate filtering; no GIS/data access required."""
import importlib.util
from pathlib import Path
import unittest

module_path = Path(__file__).resolve().parents[1] / 'scripts/build_luohu_residential_poi_20261012.py'
spec = importlib.util.spec_from_file_location('poi_intake', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CandidateClassificationTests(unittest.TestCase):
    def test_gate_in_parentheses_is_not_core(self):
        self.assertEqual(module.classify('海关草埔小区(西门)', '2010302'), 'gate_or_entrance')

    def test_residential_name(self):
        self.assertEqual(module.classify('畔山花园', '2010302'), 'residential_or_building_candidate')

    def test_shop_is_not_residential(self):
        self.assertEqual(module.classify('盛佳美商城', '2010302'), 'explicit_nonresidential_or_mixed')

    def test_other_category_not_adopted_by_name(self):
        self.assertEqual(module.classify('景福花园分店', '2040203'), 'other_category')

    def test_normalization_does_not_drop_location_qualifier(self):
        self.assertEqual(module.key(' 景福花园（ 二期 ） '), '景福花园(二期)')
        self.assertNotEqual(module.key('置富公寓(文锦北路)'), module.key('置富公寓'))

    def test_gate_with_direction_number(self):
        self.assertEqual(module.classify('都市名园-北3门', '2010302'), 'gate_or_entrance')


if __name__ == '__main__':
    unittest.main()
