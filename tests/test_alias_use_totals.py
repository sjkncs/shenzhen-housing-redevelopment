import importlib.util
from pathlib import Path
import unittest

import pandas as pd

spec = importlib.util.spec_from_file_location('use_totals', Path(__file__).resolve().parents[1] / 'scopes/shenzhen/scripts/audit_alias_use_totals.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class UseTotalTests(unittest.TestCase):
    def test_multiple_categories_match(self):
        group = pd.DataFrame({'HOUSE_USAGE2': ['全部', '住宅', '办公'], 'CJ_NUM': [3, 2, 1], 'CJ_AREA': [150, 100, 50]})
        self.assertTrue(module.reconcile(group)['matches'])

    def test_missing_total_is_not_zero(self):
        group = pd.DataFrame({'HOUSE_USAGE2': ['住宅'], 'CJ_NUM': [2], 'CJ_AREA': [100]})
        result = module.reconcile(group)
        self.assertFalse(result['checkable'])
        self.assertIsNone(result['count_difference'])

    def test_duplicate_category_rejected(self):
        group = pd.DataFrame({'HOUSE_USAGE2': ['全部', '住宅', '住宅'], 'CJ_NUM': [3, 2, 1], 'CJ_AREA': [150, 100, 50]})
        with self.assertRaises(ValueError):
            module.reconcile(group)
