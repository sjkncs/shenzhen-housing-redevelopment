import importlib.util
from pathlib import Path
import unittest

import pandas as pd

spec = importlib.util.spec_from_file_location('support', Path(__file__).resolve().parents[1] /
                                             'scopes/luohu/scripts/audit_mutoulong_candidate_support.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SupportTests(unittest.TestCase):
    def setUp(self):
        self.coverage = pd.DataFrame({'community_id': ['a', 'b'], 'transaction_names': ['A', 'B'],
                                      'clean_transaction_n': [3, 1]})
        self.sample = pd.DataFrame({'community': ['a', 'a', 'a'],
                                    'quarter': ['2019Q4', '2020Q1', '2020Q2'],
                                    'transaction_url': ['1', '2', '3']})

    def test_transition_is_separate(self):
        result = module.support_rows(self.sample, self.coverage).set_index('community_id')
        self.assertEqual(result.loc['a', 'transition_transaction_n'], 1)
        self.assertEqual(result.loc['a', 'pre_transaction_n'], 1)
        self.assertEqual(result.loc['a', 'post_transaction_n'], 1)
        self.assertTrue(result.loc['a', 'both_periods_observed'])
        self.assertFalse(result.project_treatment_assigned.any())

    def test_absent_community_is_retained(self):
        result = module.support_rows(self.sample, self.coverage).set_index('community_id')
        self.assertEqual(result.loc['b', 'window_transaction_n'], 0)
        self.assertEqual(result.loc['b', 'pre_missing_quarters_of_12'], 12)
        self.assertEqual(result.loc['b', 'post_missing_quarters_of_15'], 15)

    def test_duplicate_transactions_rejected(self):
        self.sample.loc[1, 'transaction_url'] = '1'
        with self.assertRaises(ValueError):
            module.support_rows(self.sample, self.coverage)


if __name__ == '__main__':
    unittest.main()
