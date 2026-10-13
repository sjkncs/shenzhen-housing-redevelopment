import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('baseline', Path(__file__).resolve().parents[1] /
                                             'scopes/luohu/scripts/review_residential_baseline.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BaselineTests(unittest.TestCase):
    def test_prior_transaction_does_not_accept_identity(self):
        self.assertEqual(module.classify('2019-12-31', [2000]), 'platform_transaction_observed_before_2020')

    def test_old_year_not_prior_transaction(self):
        self.assertEqual(module.classify('2021-02-01', [1990]),
                         'pre2020_construction_reported_without_pre2020_transaction')

    def test_new_year_requires_review(self):
        self.assertEqual(module.classify('2021-02-01', [2020, 2021]),
                         'post2020_construction_reported_requires_review')

    def test_no_year_not_guessed(self):
        self.assertEqual(module.classify('2021-02-01', []), 'insufficient_source_evidence')


if __name__ == '__main__':
    unittest.main()
