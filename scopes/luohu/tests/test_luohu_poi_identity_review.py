import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'scripts/review_luohu_poi_ambiguity_20261012.py'
spec = importlib.util.spec_from_file_location('identity_review', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IdentityQualifierTests(unittest.TestCase):
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
