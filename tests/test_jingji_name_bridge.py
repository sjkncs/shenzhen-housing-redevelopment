import importlib.util
from pathlib import Path
import tempfile
import unittest
import pandas as pd

spec = importlib.util.spec_from_file_location('name_bridge', Path(__file__).resolve().parents[1] / 'scopes/luohu/scripts/review_jingji_name_bridge.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NameBridgeTests(unittest.TestCase):
    def test_tokens_from_separate_records_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'page.html'
            path.write_text('<p>name</p><p>address</p>', encoding='utf-8')
            with self.assertRaises(ValueError):
                module.address_records(path, ['name', 'address'])

    def test_single_record_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'page.html'
            path.write_text('<table><tr><td>name</td><td>address</td></tr></table>', encoding='utf-8')
            self.assertEqual(len(module.address_records(path, ['name', 'address'])), 1)

    def test_id_not_substring_name_selection(self):
        raw = pd.DataFrame({'小区详情url': ['https://sz.ke.com/xiaoqu/' + module.CID, 'another'],
                            '小区名称': ['京基东方华都', '京基东方华都'], '成交详情页url': ['a', 'b']})
        self.assertEqual(len(module.source_subset(raw)), 1)


if __name__ == '__main__':
    unittest.main()
