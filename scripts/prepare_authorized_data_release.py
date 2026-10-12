"""Prepare an explicitly authorized data snapshot without altering source files."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--private-tree', type=Path, required=True)
    parser.add_argument('--transaction-zip', type=Path, required=True)
    parser.add_argument('--poi-zip', type=Path, required=True)
    parser.add_argument('--building-rar', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / 'luohu-derived-data.zip'
    paths = []
    for folder in ['20261012_luohu_residential_poi', '20261012_luohu_poi_identity_review']:
        for path in sorted((args.private_tree / 'data/supplied_gdata_intake' / folder).glob('*')):
            if path.is_file() and path.suffix in {'.csv', '.gpkg'}:
                paths.append((path, 'poi/' + folder + '/' + path.name))
    for name in ['analysis_sample.csv', 'community_pre_post_support.csv']:
        paths.append((args.private_tree / 'outputs/price_did_audit_20261003' / name, 'transactions/' + name))
    file_manifest = [{'path': relative, 'bytes': path.stat().st_size, 'sha256': sha(path)} for path, relative in paths]
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path, relative in paths:
            archive.write(path, relative)
        archive.writestr('FILE_MANIFEST.json', json.dumps(file_manifest, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for item in file_manifest:
            assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']
    rows = []
    for path, name, scope in [(args.transaction_zip, 'shenzhen-transactions-source.zip', 'shenzhen'),
                              (args.poi_zip, 'shenzhen-poi-source.zip', 'shenzhen'),
                              (args.building_rar, 'shenzhen-buildings-source.rar', 'shenzhen'),
                              (target, target.name, 'luohu')]:
        rows.append({'name': name, 'scope': scope, 'bytes': path.stat().st_size, 'sha256': sha(path),
                     'url': 'https://github.com/sjkncs/shenzhen-housing-redevelopment/releases/download/data-snapshot-20261012/' + name})
    root = Path(__file__).resolve().parents[1]
    (root / 'docs/DATA_RELEASE_MANIFEST.json').write_text(json.dumps({
        'authorization': 'Repository owner explicitly authorized public sharing on 2026-10-12',
        'third_party_license': 'No new license or independent rights verification claimed',
        'tag': 'data-snapshot-20261012', 'assets': rows,
        'luohu_files': file_manifest}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'assets': rows, 'luohu_files': len(paths), 'crc_and_hash_checks': 'PASS'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
