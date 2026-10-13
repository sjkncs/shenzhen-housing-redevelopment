import importlib.util
from pathlib import Path
import unittest
import pandas as pd

spec = importlib.util.spec_from_file_location('composition', Path(__file__).resolve().parents[1] / 'scopes/luohu/scripts/audit_candidate_composition.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PeriodTests(unittest.TestCase):
    def test_transition_not_in_pre_or_post(self):
        periods = module.assign_period(pd.Series(['2019Q4', '2020Q1', '2020Q2']))
        self.assertEqual(periods.tolist(), ['pre', 'transition', 'post'])


if __name__ == '__main__':
    unittest.main()
