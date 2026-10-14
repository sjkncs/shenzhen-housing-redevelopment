import importlib.util
from pathlib import Path
import unittest

import pandas as pd

spec = importlib.util.spec_from_file_location('monthly', Path(__file__).resolve().parents[1] / 'scopes/shenzhen/scripts/compare_luohu_monthly_aliases.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MonthlyTests(unittest.TestCase):
    def test_empty_month_not_zero(self):
        clean = pd.DataFrame({'ID': ['a', 'b'], 'TJ_DATE': ['2022-01-01', '2022-03-01'], 'CJ_NUM': [2, 3], 'CJ_AREA': [100, 150]})
        extra = pd.DataFrame(columns=clean.columns)
        result = module.compare_months(clean, extra)
        self.assertTrue(pd.isna(result.iloc[1].additive_reported_count))
        self.assertFalse(result.missing_days_filled_with_zero.any())

    def test_same_day_rows_count_as_one_observed_day(self):
        clean = pd.DataFrame({'ID': ['a'], 'TJ_DATE': ['2022-01-01'], 'CJ_NUM': [2], 'CJ_AREA': [100]})
        extra = pd.DataFrame({'ID': ['b', 'c'], 'TJ_DATE': ['2022-01-02'] * 2, 'CJ_NUM': [1, 3], 'CJ_AREA': [50, 150]})
        row = module.compare_months(clean, extra).iloc[0]
        self.assertEqual(row.additive_observed_days, 2)
        self.assertEqual(row.additional_reported_count, 4)
        self.assertFalse(row.additive_rule_source_confirmed)

    def test_duplicate_source_rejected(self):
        clean = pd.DataFrame({'ID': ['a'], 'TJ_DATE': ['2022-01-01'], 'CJ_NUM': [2], 'CJ_AREA': [100]})
        with self.assertRaises(ValueError):
            module.compare_months(clean, clean)
