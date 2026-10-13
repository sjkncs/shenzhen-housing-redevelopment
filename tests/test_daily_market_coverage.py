import importlib.util
from pathlib import Path
import unittest
import pandas as pd

spec = importlib.util.spec_from_file_location('daily', Path(__file__).resolve().parents[1] / 'scopes/shenzhen/scripts/audit_daily_market_coverage.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CoverageTests(unittest.TestCase):
    def test_missing_month_not_zero_activity(self):
        data = pd.DataFrame({'日期': pd.to_datetime(['2026-01-31', '2026-03-01']), '成交套数': [2, 3], '成交面积': [100, 150]})
        table = module.monthly_coverage(data)
        feb = table.iloc[1]
        self.assertEqual(feb.observed_days, 0)
        self.assertTrue(pd.isna(feb.reported_transaction_n))
        self.assertFalse(feb.missing_days_filled_with_zero)

    def test_duplicate_day_rejected(self):
        data = pd.DataFrame({'日期': pd.to_datetime(['2026-01-01'] * 2), '成交套数': [1, 1], '成交面积': [50, 50]})
        with self.assertRaises(ValueError):
            module.monthly_coverage(data)
