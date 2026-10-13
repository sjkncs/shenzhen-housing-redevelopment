import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('download', Path(__file__).resolve().parents[1] / 'scripts/download_data.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DownloadTests(unittest.TestCase):
    def test_valid_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.zip'
            path.write_bytes(b'data')
            item = {'name': path.name, 'bytes': 4, 'sha256': hashlib.sha256(b'data').hexdigest()}
            self.assertEqual(module.obtain(item, path.parent, True), path)

    def test_wrong_hash_is_rejected_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.zip'
            path.write_bytes(b'data')
            with self.assertRaises(ValueError):
                module.obtain({'name': path.name, 'bytes': 4, 'sha256': '0' * 64}, path.parent)
            self.assertEqual(path.read_bytes(), b'data')

    def test_missing_offline_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                module.obtain({'name': 'missing.zip'}, Path(directory), True)

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                module.obtain({'name': '../escape.zip'}, Path(directory), True)

    def test_extra_zip_member_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('FILE_MANIFEST.json', '[]')
                archive.writestr('extra.csv', 'x')
            with self.assertRaises(ValueError):
                module.verify_luohu(path, [])

    def test_inner_data_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.zip'
            expected = [{'path': 'sample.csv', 'bytes': 1, 'sha256': hashlib.sha256(b'x').hexdigest()}]
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('FILE_MANIFEST.json', json.dumps(expected))
                archive.writestr('sample.csv', 'x')
            module.verify_luohu(path, expected)


if __name__ == '__main__':
    unittest.main()
