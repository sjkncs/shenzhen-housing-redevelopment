"""Copy explicitly requested artifacts and seal original code without rewriting sources."""
import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--private-archive', type=Path, required=True)
    args = parser.parse_args()
    records = []

    def copy(source, relative):
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            assert destination.read_bytes() == source.read_bytes(), 'Preserve existing artifact'
        else:
            shutil.copy2(source, destination)
        assert source.read_bytes() == destination.read_bytes()
        if destination.suffix in {'.docx', '.pptx'}:
            with zipfile.ZipFile(destination) as archive:
                assert archive.testzip() is None
        if destination.suffix == '.pdf':
            assert destination.read_bytes().startswith(b'%PDF')
        records.append({'path': relative, 'bytes': destination.stat().st_size,
                        'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})

    original = args.private_archive
    copy(original / 'deliverables/presentation/10.7开题报告.pptx', 'PPT/10.7开题报告.pptx')
    for extension in ['docx', 'pdf']:
        candidates = list((original / 'deliverables/proposal').glob('*开题报告_评委意见修订版.' + extension))
        assert len(candidates) == 1, 'Select the precise source version'
        source = candidates[0]
        copy(source, 'Draft/开题报告_评委意见修订版.' + extension)
    for name in ['run_price_did_audit_20261003.py', 'check_price_did_support_20261003.py',
                 'check_price_did_influence_20261003.py', 'build_luohu_residential_poi_20261012.py',
                 'diagnose_poi_coordinate_frames_20261012.py', 'review_luohu_poi_ambiguity_20261012.py']:
        copy(original / 'scripts' / name, 'Code_Original/20261012_snapshot/' + name)
    (ROOT / 'Logfiles/artifact_manifest.json').write_text(json.dumps({
        'scope': 'Original code and owner-requested academic materials',
        'source_artifacts_rewritten': False, 'files': records}, ensure_ascii=False, indent=2), encoding='utf-8')
    content = (ROOT / 'README_replication.md').read_text(encoding='utf-8')
    page = ('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Research Replication / 研究复现</title><style>'
            'body{max-width:1000px;margin:48px auto;padding:0 24px;background:#f5f8fa;color:#183344;'
            'font-family:Georgia,"Microsoft YaHei",serif;line-height:1.7}'
            'pre{white-space:pre-wrap;background:white;border-top:5px solid #1677a8;padding:32px}'
            'a{color:#1677a8}</style><h1>Research Replication / 研究复现</h1>'
            '<p><a href="README.md">项目首页</a> · <a href="PPT/">PPT</a> · <a href="Draft/">报告</a>'
            ' · <a href="Dataset/">数据</a></p><pre>' + html.escape(content) + '</pre></html>')
    (ROOT / 'README_replication.html').write_text(page, encoding='utf-8')
    print(json.dumps({'copied_files': len(records), 'office_files': 3, 'byte_identity': 'PASS'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
