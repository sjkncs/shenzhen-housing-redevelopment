import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('roster_audit', Path(__file__).resolve().parents[1] / 'scopes/luohu/scripts/audit_official_residential_names.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OfficialNameTests(unittest.TestCase):
    def row(self, name, district='罗湖'):
        return dict(official_name=name, district=district, street='测试', official_serial='1', pdf_page=1)

    def test_exact_name_only_and_no_identity_upgrade(self):
        rows = module.match_names([dict(community_id='1', name='测试花园'), dict(community_id='2', name='测试花园一期')], [self.row('测试花园')])
        self.assertTrue(rows[0]['official_roster_name_corroborated'])
        self.assertFalse(rows[1]['official_roster_name_corroborated'])
        self.assertFalse(rows[0]['residential_building_identity_verified'])

    def test_wrong_district_not_matched(self):
        rows = module.match_names([dict(community_id='1', name='测试花园')], [self.row('测试花园', '南山')])
        self.assertFalse(rows[0]['official_roster_name_corroborated'])

    def test_duplicate_official_name_rejected(self):
        with self.assertRaises(ValueError):
            module.match_names([dict(community_id='1', name='测试花园')], [self.row('测试花园'), self.row('测试花园')])


if __name__ == '__main__':
    unittest.main()
