import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('readiness', Path(__file__).resolve().parents[1] / 'scopes/luohu/scripts/build_project_readiness.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WindowTests(unittest.TestCase):
    def test_future_event(self):
        self.assertIn('无现有事后', module.window_status('2026-01-09', '2026-01-09', '2024-04-25'))

    def test_annual_interval_not_imputed(self):
        self.assertIn('不能确认', module.window_status('2024-01-01', '2024-12-31', '2024-04-25'))

    def test_covered_not_local_acceptance(self):
        self.assertIn('仍需', module.window_status('2022-05-01', '2022-05-31', '2024-04-25'))

    def test_missing_and_reversed(self):
        self.assertEqual(module.window_status(None, None, '2024-04-25'), '事件日期待核')
        with self.assertRaises(ValueError):
            module.window_status('2024-12-31', '2024-01-01', '2024-04-25')
