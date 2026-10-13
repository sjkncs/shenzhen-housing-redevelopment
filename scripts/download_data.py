"""Download released research packages and verify exact bytes without extracting."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def verify(path, asset):
    if path.stat().st_size != asset['bytes']:
        raise ValueError('Size mismatch: ' + path.name)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    if digest.hexdigest() != asset['sha256']:
        raise ValueError('SHA-256 mismatch: ' + path.name)


def verify_luohu(path, expected):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        required = {item['path'] for item in expected} | {'FILE_MANIFEST.json'}
        if len(names) != len(required) or set(names) != required:
            raise ValueError('Unexpected archive members')
        if json.loads(archive.read('FILE_MANIFEST.json')) != expected:
            raise ValueError('Inner manifest differs from repository manifest')
        for item in expected:
            if archive.getinfo(item['path']).file_size != item['bytes']:
                raise ValueError('Inner size mismatch: ' + item['path'])
            digest = hashlib.sha256()
            with archive.open(item['path']) as stream:
                for block in iter(lambda: stream.read(1048576), b''):
                    digest.update(block)
            if digest.hexdigest() != item['sha256']:
                raise ValueError('Inner hash mismatch: ' + item['path'])


def obtain(asset, directory, offline=False):
    name = asset['name']
    if Path(name).name != name or '/' in name or '\\' in name:
        raise ValueError('Invalid asset filename')
    target = directory / name
    if target.exists():
        verify(target, asset)
        return target
    if offline:
        raise FileNotFoundError(target)
    directory.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + '.download')
    # Exclusive creation protects unfinished downloads and existing research files.
    with temporary.open('xb') as stream:
        try:
            request = Request(asset['url'], headers={'User-Agent': 'shenzhen-housing-redevelopment'})
            with urlopen(request, timeout=60) as response:
                written = 0
                while block := response.read(1048576):
                    written += len(block)
                    if written > asset['bytes']:
                        raise ValueError('Response exceeds declared size')
                    stream.write(block)
        except Exception:
            stream.close()
            temporary.unlink()
            raise
    try:
        verify(temporary, asset)
    except Exception:
        temporary.unlink()
        raise
    if target.exists():
        raise FileExistsError('Target appeared while downloading: ' + str(target))
    temporary.rename(target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', choices=['shenzhen', 'luohu', 'all'], default='luohu')
    parser.add_argument('--directory', type=Path, default=ROOT / 'data/raw/downloads')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/DATA_RELEASE_MANIFEST.json').read_text(encoding='utf-8'))
    checked = []
    for asset in manifest['assets']:
        if args.scope != 'all' and asset['scope'] != args.scope:
            continue
        path = obtain(asset, args.directory, args.verify_only)
        if asset['scope'] == 'luohu':
            verify_luohu(path, manifest['luohu_files'])
        checked.append({'name': asset['name'], 'bytes': asset['bytes'], 'sha256': 'PASS'})
    print(json.dumps({'verified': checked, 'extracted': False, 'research_validity_checked': False}))


if __name__ == '__main__':
    main()
