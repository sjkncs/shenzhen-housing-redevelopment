"""Verify public scope, local links, aggregate results, and omitted private artifacts."""
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode('utf-8').split('\0')
files = list(filter(None, files))
catalog_path = ROOT / 'Code_Revision/code_catalog.json'
if catalog_path.exists():
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))['files']
    python_paths = {name for name in files if name.endswith('.py')}
    assert {row['path'] for row in catalog} == python_paths, 'Python code classification incomplete'
    assert len({row['path'] for row in catalog}) == len(catalog), 'Duplicate code entries'
    assert all(row['purpose_zh'] and row['inputs_zh'] and row['outputs_zh'] and row['run_status_zh'] for row in catalog)
secrets = re.compile(rb'(?:ghp_|gho_|github_pat_|sk-proj-)[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
artifacts = json.loads((ROOT / 'Logfiles/artifact_manifest.json').read_text(encoding='utf-8')) if (ROOT / 'Logfiles/artifact_manifest.json').exists() else {'files': []}
sealed = {r['path']: r for r in artifacts['files']}
office_allowed = {'Draft/开题报告_评委意见修订版.docx', 'Draft/开题报告_评委意见修订版.pdf', 'PPT/10.7开题报告.pptx',
                  'Draft/深圳市老旧住宅区拆除重建项目对周边住宅价格的动态影响.docx'}
for name in files:
    path = ROOT / name
    assert path.suffix.lower() not in {'.doc', '.docx', '.pptx', '.pdf', '.zip', '.rar', '.gpkg', '.exe', '.dll'} or name in office_allowed, name
    assert path.name not in {'analysis_sample.csv', 'community_pre_post_support.csv'}, name
    assert not secrets.search(path.read_bytes()), 'Potential credential: ' + name
    if name in sealed:
        assert path.stat().st_size == sealed[name]['bytes']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sealed[name]['sha256']
    if path.suffix in {'.docx', '.pptx'}:
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            for item in archive.namelist():
                if item.endswith('.xml'):
                    assert not secrets.search(archive.read(item)), 'Potential credential in Office XML'
    if path.suffix in {'.md', '.py', '.json', '.csv'}:
        text = path.read_text(encoding='utf-8-sig')
        if name != 'scripts/validate_public_repository.py' and not name.startswith('Code_Original/'):
            assert not re.search(r'(?<![\d.])20\d{8}(?!\d)|[A-Z]:[/\\]Users[/\\]|wxid_', text), 'Personal identifier: ' + name
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if not re.match(r'https?://|#', link):
                    assert (path.parent / link.split('#')[0]).exists(), 'Broken local link: ' + link
summary = json.loads((ROOT / 'scopes/shenzhen/summary/coverage.json').read_text())
table = pd.read_csv(ROOT / 'scopes/shenzhen/summary/district_coverage.csv')
assert len(table) == 10 and table.transaction_n.sum() == summary['clean_n'] == 132774
assert summary['raw_n'] == summary['clean_n'] + summary['excluded_n']
luohu = table[table.district.eq('罗湖区')].iloc[0]
assert luohu.transaction_n == 16199 and luohu.community_n == 621
audit = json.loads((ROOT / 'scopes/luohu/outputs/price_did_audit_20261003/run_summary.json').read_text())
assert audit['luohu_clean_n'] == luohu.transaction_n
assert audit['status'] == 'AREA_PROXY_DID_EXECUTED_PROJECT_BOUNDARY_DID_PENDING'
assert audit['pretrend_joint_test']['p'] < .05
math = ROOT / 'scopes/luohu/data/supplied_gdata_intake/20261011/building_rar/coordinate_hypotheses/implementation.py'
assert hashlib.sha256(math.read_bytes()).hexdigest() == '9fa83f46294f9e5616942d8cfec74825f2ecf4b6716418bc7d0208f46c6aa84f'
print(json.dumps({'public_files': len(files), 'citywide_clean_n': summary['clean_n'],
                  'luohu_clean_n': int(luohu.transaction_n), 'status': 'PASS'}))
