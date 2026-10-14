import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('queue_builder', ROOT / 'scopes/luohu/scripts/build_residential_review_queue.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReviewQueueTests(unittest.TestCase):
    def inputs(self):
        out = ROOT / 'scopes/luohu/outputs'
        return {k: module.read_rows(out / path) for k, path in {
            'leads': 'mutoulong_address_support_20261013/road_address_leads_support.csv',
            'baseline': 'mutoulong_baseline_review_20261013/baseline_evidence.csv',
            'support': 'footprint_hypothesis_review_20261014/coordinate_hypothesis_footprint_support.csv',
            'addresses': 'official_address_review_20261013/official_address_evidence.csv',
            'atlas': 'footprint_review_atlas_final_20261014/review_atlas_index.csv'}.items()}

    def test_all_candidates_remain_pending(self):
        rows = module.build_queue(**self.inputs())
        self.assertEqual(len(rows), 20)
        self.assertEqual(sum(int(r['window_transaction_n']) for r in rows), 366)
        self.assertTrue(all(r['review_status'] == 'pending' and not r['accepted_building_id'] for r in rows))
        self.assertTrue(all(not r['residential_identity_verified'] and not r['coordinate_verified'] for r in rows))
        self.assertEqual(sum(r['official_address_corroborated'].lower() == 'true' for r in rows), 3)

    def test_missing_hypothesis_rejected(self):
        inputs = self.inputs()
        inputs['support'].pop()
        with self.assertRaises(ValueError):
            module.build_queue(**inputs)

    def test_duplicate_baseline_rejected(self):
        inputs = self.inputs()
        inputs['baseline'].append(inputs['baseline'][0])
        with self.assertRaises(ValueError):
            module.build_queue(**inputs)

    def test_accepted_footprint_rejected(self):
        inputs = self.inputs()
        inputs['support'][0]['building_selected'] = 'True'
        with self.assertRaises(ValueError):
            module.build_queue(**inputs)


if __name__ == '__main__':
    unittest.main()
