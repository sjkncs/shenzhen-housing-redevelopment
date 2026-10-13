import csv
import json
import math
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1] / 'scopes/luohu/project_registry/mutoulong/image_comparison_2019'


class ImageComparisonTests(unittest.TestCase):
    def test_fit_and_check_points_are_separate(self):
        with (BASE / 'image_points.csv').open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        fit = {r['point_id'] for r in rows if r['role'] == 'fit'}
        check = {r['point_id'] for r in rows if r['role'] == 'check'}
        self.assertEqual(len(fit), 6)
        self.assertEqual(len(check), 6)
        self.assertFalse(fit & check)

    def test_reported_error_matches_saved_points(self):
        report = json.loads((BASE / 'comparison.json').read_text(encoding='utf-8'))
        with (BASE / 'pixel_correspondence_checks.csv').open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.DictReader(stream))
        for role, field in [('fit', 'fit_rmse_display_pixels'), ('check', 'held_out_rmse_display_pixels')]:
            errors = [float(r['error_display_pixels']) for r in rows if r['role'] == role]
            self.assertAlmostEqual(math.sqrt(sum(e * e for e in errors) / len(errors)), report[field], places=10)
        self.assertFalse(report['geographic_accuracy_verified'])
        self.assertFalse(report['crs_confirmed'])
        self.assertFalse(report['housing_distances_computed'])


if __name__ == '__main__':
    unittest.main()
