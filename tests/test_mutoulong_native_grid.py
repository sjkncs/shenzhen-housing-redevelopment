"""Check transcribed source-grid integrity without assuming a CRS."""
import csv
import hashlib
import json
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1] / 'scopes/luohu/project_registry/mutoulong/native_grid_2019'


class SourceGridTests(unittest.TestCase):
    def test_points_and_hash(self):
        audit = json.loads((BASE / 'audit.json').read_text(encoding='utf-8'))
        path = BASE / 'coordinates.csv'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), audit['coordinate_table_sha256'])
        with path.open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual([r['point_id'] for r in rows], ['J' + str(i) for i in range(1, 46)])
        self.assertEqual(len({(r['raw_x'], r['raw_y']) for r in rows}), 45)

    def test_independent_shoelace_area(self):
        audit = json.loads((BASE / 'audit.json').read_text(encoding='utf-8'))
        with (BASE / 'coordinates.csv').open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        for ring in audit['ring_checks']:
            points = [(float(r['raw_x']), float(r['raw_y'])) for r in rows if r['ring_id'] == ring['ring_id']]
            self.assertEqual(len(points), ring['point_count'])
            x0, y0 = points[0]
            shifted = [(x - x0, y - y0) for x, y in points]
            area = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(shifted, shifted[1:] + shifted[:1]))) / 2
            self.assertAlmostEqual(area, ring['source_grid_area_units_squared'], places=6)

    def test_no_accepted_geographic_claim(self):
        audit = json.loads((BASE / 'audit.json').read_text(encoding='utf-8'))
        for field in ['crs_confirmed', 'units_confirmed', 'georeferenced', 'housing_distances_computed',
                      'whole_demolition_boundary_equivalence_verified', 'independent_transcription_check']:
            self.assertFalse(audit[field])


if __name__ == '__main__':
    unittest.main()
